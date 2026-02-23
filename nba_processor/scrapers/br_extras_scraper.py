"""
Basketball Reference extras scraper: PBP, shot chart, and plus-minus pages.
"""

import json
import os
import re
import time
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

import cloudscraper
from bs4 import BeautifulSoup, Comment, NavigableString

from ..utils.constants import BASE_DIR
from ..utils.log import info, warn, error, debug, success


# Rate limiting
MIN_DELAY = 3.0
MAX_DELAY = 5.0

# URLs
PBP_URL = "https://www.basketball-reference.com/boxscores/pbp/{game_id}.html"
SHOT_CHART_URL = "https://www.basketball-reference.com/boxscores/shot-chart/{game_id}.html"
PLUS_MINUS_URL = "https://www.basketball-reference.com/boxscores/plus-minus/{game_id}.html"

# Cache directories (parsed JSON)
CACHE_DIR = BASE_DIR / "cache"
PBP_CACHE_DIR = CACHE_DIR / "br_pbp"
SHOT_CHART_CACHE_DIR = CACHE_DIR / "br_shot_chart"
PLUS_MINUS_CACHE_DIR = CACHE_DIR / "br_plus_minus"

# Raw HTML directories
HTML_DIR = BASE_DIR / "html_games"
PBP_HTML_DIR = HTML_DIR / "br_pbp"
SHOT_CHART_HTML_DIR = HTML_DIR / "br_shot_chart"
PLUS_MINUS_HTML_DIR = HTML_DIR / "br_plus_minus"


def _extract_from_comments(soup: BeautifulSoup) -> BeautifulSoup:
    """Extract HTML tables/divs hidden in comments (BR lazy loading pattern)."""
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if '<div' in comment or '<table' in comment:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            for tag in comment_soup.children:
                if hasattr(tag, 'name') and tag.name:
                    soup.append(tag.__copy__() if hasattr(tag, '__copy__') else tag)
    return soup


def parse_br_pbp(html: str) -> Optional[Dict[str, Any]]:
    """
    Parse Basketball Reference play-by-play HTML.

    Returns dict with 'plays' list and 'play_count'.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Find PBP table (may be in comments)
    table = soup.find('table', id='pbp')
    if not table:
        soup = _extract_from_comments(soup)
        table = soup.find('table', id='pbp')
    if not table:
        return None

    plays = []
    current_quarter = 0

    for row in table.find_all('tr'):
        # Check for quarter header
        if 'thead' in row.get('class', []):
            row_id = row.get('id', '')
            if row_id.startswith('q'):
                try:
                    current_quarter = int(row_id[1:])
                except ValueError:
                    pass
            continue

        cells = row.find_all('td')
        if not cells:
            continue

        time_val = cells[0].get_text(strip=True)

        # colspan=5 means neutral event (jump ball, quarter start/end)
        if len(cells) == 2 and cells[1].get('colspan'):
            action_text = ' '.join(cells[1].get_text(' ', strip=True).split())
            plays.append({
                'quarter': current_quarter,
                'time': time_val,
                'team_side': None,
                'player': None,
                'action': action_text,
                'score': None,
                'away_score': None,
                'home_score': None,
            })
            continue

        if len(cells) < 6:
            continue

        # Columns: 0=time, 1=away_action, 2=away_delta, 3=score, 4=home_delta, 5=home_action
        away_text = ' '.join(cells[1].get_text(' ', strip=True).split())
        home_text = ' '.join(cells[5].get_text(' ', strip=True).split())
        score_text = cells[3].get_text(strip=True)

        # Determine which side has the action
        if away_text and away_text != '\xa0':
            team_side = 'away'
            action = away_text
            # Extract player from first link
            link = cells[1].find('a')
            player = link.get_text(strip=True) if link else None
        elif home_text and home_text != '\xa0':
            team_side = 'home'
            action = home_text
            link = cells[5].find('a')
            player = link.get_text(strip=True) if link else None
        else:
            continue

        # Parse score
        away_score = None
        home_score = None
        if score_text and '-' in score_text:
            parts = score_text.split('-')
            try:
                away_score = int(parts[0])
                home_score = int(parts[1])
            except (ValueError, IndexError):
                pass

        plays.append({
            'quarter': current_quarter,
            'time': time_val,
            'team_side': team_side,
            'player': player,
            'action': action,
            'score': score_text if score_text else None,
            'away_score': away_score,
            'home_score': home_score,
        })

    if not plays:
        return None

    return {
        'plays': plays,
        'play_count': len(plays),
    }


def parse_br_shot_chart(html: str) -> Optional[Dict[str, Any]]:
    """
    Parse Basketball Reference shot chart HTML.

    Returns dict with 'shots' list and 'shot_count'.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Shot chart is NOT in comments typically, but check anyway
    shot_areas = soup.find_all('div', class_='shot-area')
    if not shot_areas:
        soup = _extract_from_comments(soup)
        shot_areas = soup.find_all('div', class_='shot-area')
    if not shot_areas:
        return None

    shots = []

    for area in shot_areas:
        # Get team from parent wrapper id (e.g., "shots-GSW" -> "GSW")
        area_id = area.get('id', '')
        team = area_id.replace('shots-', '') if area_id.startswith('shots-') else ''

        # Build player name lookup from the select dropdown
        player_names = {}
        if team:
            select = soup.find('select', id=f'player-{team}')
            if select:
                for option in select.find_all('option'):
                    val = option.get('value', '')
                    if val:
                        # Use direct text node only (html.parser nests unclosed options)
                        name = next((t.strip() for t in option.children
                                     if isinstance(t, NavigableString) and t.strip()), '')
                        if name:
                            player_names[val] = name

        for div in area.find_all('div', class_='tooltip'):
            classes = div.get('class', [])
            style = div.get('style', '')
            tip = div.get('tip', '')

            # Extract coordinates
            x_match = re.search(r'left:\s*(-?\d+)px', style)
            y_match = re.search(r'top:\s*(-?\d+)px', style)
            x = int(x_match.group(1)) if x_match else 0
            y = int(y_match.group(1)) if y_match else 0

            # Made or missed
            made = 'make' in classes

            # Quarter from class like "q-1"
            quarter = 0
            for cls in classes:
                if cls.startswith('q-'):
                    try:
                        quarter = int(cls[2:])
                    except ValueError:
                        pass

            # Player ID from class like "p-curryst01"
            player_id = ''
            for cls in classes:
                if cls.startswith('p-'):
                    player_id = cls[2:]

            # Get player display name
            player = player_names.get(player_id, player_id)

            # Parse description from tip
            description = ''
            if tip:
                # Second line of tip is the shot description
                lines = tip.split('<br>')
                if len(lines) >= 2:
                    description = lines[1].strip()

            shots.append({
                'player': player,
                'player_id': player_id,
                'team': team,
                'x': x,
                'y': y,
                'made': made,
                'quarter': quarter,
                'description': description,
            })

    if not shots:
        return None

    return {
        'shots': shots,
        'shot_count': len(shots),
    }


def parse_br_plus_minus(html: str) -> Optional[Dict[str, Any]]:
    """
    Parse Basketball Reference plus-minus HTML.

    Returns dict with 'away' and 'home' player lists.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Plus-minus may be in comments
    pm_div = soup.find('div', class_='plusminus')
    if not pm_div:
        soup = _extract_from_comments(soup)
        pm_div = soup.find('div', class_='plusminus')
    if not pm_div:
        return None

    # Find team sections (away first, home second)
    # Each team is in a div under the width-constrained container
    container = pm_div.find('div', style=lambda s: s and 'width:' in s)
    if not container:
        return None

    team_sections = []
    for child in container.children:
        if hasattr(child, 'name') and child.name and hasattr(child, 'find') and child.find('h3'):
            team_sections.append(child)

    if len(team_sections) < 2:
        return None

    def _parse_team_section(section):
        players = []
        player_divs = section.find_all('div', class_='player')
        for pdiv in player_divs:
            span = pdiv.find('span')
            if not span:
                continue
            name = span.get_text(strip=True)

            # Parse On/Off/Net from text like "(On: +10 · Off: -4 · Net: +14)"
            text = pdiv.get_text(strip=True)
            on_val = off_val = net_val = 0.0

            on_match = re.search(r'On:\s*([+-]?\d+)', text)
            off_match = re.search(r'Off:\s*([+-]?\d+)', text)
            net_match = re.search(r'Net:\s*([+-]?\d+)', text)

            if on_match:
                on_val = float(on_match.group(1))
            if off_match:
                off_val = float(off_match.group(1))
            if net_match:
                net_val = float(net_match.group(1))

            players.append({
                'player': name,
                'on': on_val,
                'off': off_val,
                'net': net_val,
            })

        return players

    away = _parse_team_section(team_sections[0])
    home = _parse_team_section(team_sections[1])

    if not away and not home:
        return None

    return {
        'away': away,
        'home': home,
    }


class BRExtrasScraper:
    """Scraper for Basketball Reference PBP, shot chart, and plus-minus pages."""

    def __init__(self):
        for d in (PBP_CACHE_DIR, SHOT_CHART_CACHE_DIR, PLUS_MINUS_CACHE_DIR,
                  PBP_HTML_DIR, SHOT_CHART_HTML_DIR, PLUS_MINUS_HTML_DIR):
            d.mkdir(parents=True, exist_ok=True)

        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True,
            }
        )
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < MIN_DELAY:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            sleep_time = delay - elapsed
            if sleep_time > 0:
                debug(f"  Rate limiting: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _fetch_url(self, url: str) -> Optional[str]:
        self._rate_limit()
        self.request_count += 1
        try:
            response = self.scraper.get(url, timeout=30)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                return response.text
            elif response.status_code == 404:
                debug(f"  Not found: {url}")
                return None
            elif response.status_code == 429:
                warn("Rate limited! Waiting 60 seconds...")
                time.sleep(60)
                return self._fetch_url(url)
            else:
                warn(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            error(f"Error fetching {url}: {e}")
            return None

    def _load_cache(self, cache_dir: Path, game_id: str) -> Optional[Dict]:
        cache_path = cache_dir / f"{game_id}.json"
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def _save_cache(self, cache_dir: Path, game_id: str, data: Dict) -> None:
        cache_path = cache_dir / f"{game_id}.json"
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            warn(f"Failed to cache {cache_path}: {e}")

    def _friendly_filename(self, game_id: str) -> str:
        """Convert game_id to friendly filename like DEN@GSW_20260222."""
        cache_path = CACHE_DIR / f"{game_id}.json"
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                bi = data.get('basic_info', {})
                away = bi.get('away_team_code', '')
                home = bi.get('home_team_code', '')
                date = bi.get('date_yyyymmdd', '')
                if away and home and date:
                    return f"{away}@{home}_{date}"
            except (json.JSONDecodeError, IOError):
                pass
        return game_id

    def _save_html(self, html_dir: Path, game_id: str, html: str) -> None:
        filename = self._friendly_filename(game_id)
        html_path = html_dir / f"{filename}.html"
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except IOError as e:
            warn(f"Failed to save HTML {html_path}: {e}")

    def _load_html(self, html_dir: Path, game_id: str) -> Optional[str]:
        # Try friendly name first, then fall back to game_id
        for filename in (self._friendly_filename(game_id), game_id):
            html_path = html_dir / f"{filename}.html"
            if html_path.exists():
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except IOError:
                    pass
        return None

    def _get_html(self, url: str, html_dir: Path, game_id: str) -> Optional[str]:
        """Fetch HTML from network or load from saved file."""
        saved = self._load_html(html_dir, game_id)
        if saved:
            return saved
        html = self._fetch_url(url)
        if html:
            self._save_html(html_dir, game_id, html)
        return html

    def scrape_pbp(self, game_id: str, use_cache: bool = True) -> Optional[Dict]:
        if use_cache:
            cached = self._load_cache(PBP_CACHE_DIR, game_id)
            if cached:
                return cached

        html = self._get_html(PBP_URL.format(game_id=game_id), PBP_HTML_DIR, game_id)
        if not html:
            return None

        result = parse_br_pbp(html)
        if result:
            result['game_id'] = game_id
            self._save_cache(PBP_CACHE_DIR, game_id, result)
        return result

    def scrape_shot_chart(self, game_id: str, use_cache: bool = True) -> Optional[Dict]:
        if use_cache:
            cached = self._load_cache(SHOT_CHART_CACHE_DIR, game_id)
            if cached:
                return cached

        html = self._get_html(SHOT_CHART_URL.format(game_id=game_id), SHOT_CHART_HTML_DIR, game_id)
        if not html:
            return None

        result = parse_br_shot_chart(html)
        if result:
            result['game_id'] = game_id
            self._save_cache(SHOT_CHART_CACHE_DIR, game_id, result)
        return result

    def scrape_plus_minus(self, game_id: str, use_cache: bool = True) -> Optional[Dict]:
        if use_cache:
            cached = self._load_cache(PLUS_MINUS_CACHE_DIR, game_id)
            if cached:
                return cached

        html = self._get_html(PLUS_MINUS_URL.format(game_id=game_id), PLUS_MINUS_HTML_DIR, game_id)
        if not html:
            return None

        result = parse_br_plus_minus(html)
        if result:
            result['game_id'] = game_id
            self._save_cache(PLUS_MINUS_CACHE_DIR, game_id, result)
        return result

    def scrape_all(self, game_id: str, use_cache: bool = True) -> Dict[str, Optional[Dict]]:
        return {
            'pbp': self.scrape_pbp(game_id, use_cache),
            'shot_chart': self.scrape_shot_chart(game_id, use_cache),
            'plus_minus': self.scrape_plus_minus(game_id, use_cache),
        }
