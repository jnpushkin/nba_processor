"""
Helper utilities for NBA data processing.
"""

import re
from typing import Any, Optional, Union

from .constants import TEAM_ALIASES, NBA_TEAMS


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            # Handle strings like "12.0"
            return int(float(value.strip()))
        except (ValueError, AttributeError):
            return default
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return default
    return default


def normalize_name(name: str) -> str:
    """Normalize a player name for consistent matching."""
    if not name:
        return ""
    # Remove suffixes like Jr., Sr., III, etc.
    name = re.sub(r'\s+(Jr\.?|Sr\.?|III|II|IV)$', '', name, flags=re.IGNORECASE)
    # Remove periods
    name = name.replace('.', '')
    # Normalize whitespace
    name = ' '.join(name.split())
    return name.strip().lower()


def get_team_code(team_name: str) -> str:
    """Get team abbreviation code."""
    canonical = TEAM_ALIASES.get(team_name, team_name)
    if canonical in NBA_TEAMS:
        return NBA_TEAMS[canonical]['code']
    # Fallback: first 3 letters uppercased
    return team_name[:3].upper()


def parse_minutes(mp: Union[str, int, float]) -> float:
    """Parse minutes played from various formats.

    Args:
        mp: Minutes in format "MM:SS", decimal, or integer

    Returns:
        Minutes as float
    """
    if isinstance(mp, (int, float)):
        return float(mp)

    if isinstance(mp, str):
        if ':' in mp:
            parts = mp.split(':')
            try:
                minutes = int(parts[0])
                seconds = int(parts[1]) if len(parts) > 1 else 0
                return minutes + seconds / 60.0
            except ValueError:
                return 0.0
        try:
            return float(mp)
        except ValueError:
            return 0.0

    return 0.0


def calculate_game_score(stats: dict) -> float:
    """Calculate John Hollinger's Game Score.

    Game Score = PTS + 0.4*FGM - 0.7*FGA - 0.4*(FTA-FTM) + 0.7*ORB + 0.3*DRB
                 + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV

    Args:
        stats: Dictionary with player stats

    Returns:
        Game score value
    """
    pts = safe_int(stats.get('pts', 0))
    fg = safe_int(stats.get('fg', 0))
    fga = safe_int(stats.get('fga', 0))
    ft = safe_int(stats.get('ft', 0))
    fta = safe_int(stats.get('fta', 0))
    orb = safe_int(stats.get('orb', 0))
    drb = safe_int(stats.get('drb', 0))
    stl = safe_int(stats.get('stl', 0))
    ast = safe_int(stats.get('ast', 0))
    blk = safe_int(stats.get('blk', 0))
    pf = safe_int(stats.get('pf', 0))
    tov = safe_int(stats.get('tov', 0))

    game_score = (
        pts
        + 0.4 * fg
        - 0.7 * fga
        - 0.4 * (fta - ft)
        + 0.7 * orb
        + 0.3 * drb
        + stl
        + 0.7 * ast
        + 0.7 * blk
        - 0.4 * pf
        - tov
    )

    return round(game_score, 1)


def is_triple_double(stats: dict, threshold: int = 10) -> bool:
    """Check if stats constitute a triple-double.

    Args:
        stats: Dictionary with player stats
        threshold: Minimum value for each category (default 10)

    Returns:
        True if triple-double achieved
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    counts = sum(1 for cat in categories if safe_int(stats.get(cat, 0)) >= threshold)
    return counts >= 3


def is_double_double(stats: dict, threshold: int = 10) -> bool:
    """Check if stats constitute a double-double.

    Args:
        stats: Dictionary with player stats
        threshold: Minimum value for each category (default 10)

    Returns:
        True if double-double achieved
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    counts = sum(1 for cat in categories if safe_int(stats.get(cat, 0)) >= threshold)
    return counts >= 2


def calculate_true_shooting(pts: int, fga: int, fta: int) -> Optional[float]:
    """Calculate true shooting percentage.

    TS% = PTS / (2 * (FGA + 0.44 * FTA))

    Args:
        pts: Points scored
        fga: Field goal attempts
        fta: Free throw attempts

    Returns:
        True shooting percentage or None if not calculable
    """
    denominator = 2 * (fga + 0.44 * fta)
    if denominator == 0:
        return None
    return round(pts / denominator, 3)


def calculate_effective_fg_pct(fg: int, fg3: int, fga: int) -> Optional[float]:
    """Calculate effective field goal percentage.

    eFG% = (FG + 0.5 * 3PM) / FGA

    Args:
        fg: Field goals made
        fg3: Three-pointers made
        fga: Field goal attempts

    Returns:
        Effective FG% or None if not calculable
    """
    if fga == 0:
        return None
    return round((fg + 0.5 * fg3) / fga, 3)


def is_quadruple_double(stats: dict, threshold: int = 10) -> bool:
    """Check if stats constitute a quadruple-double.

    Args:
        stats: Dictionary with player stats
        threshold: Minimum value for each category (default 10)

    Returns:
        True if quadruple-double achieved (4+ categories with 10+)
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    counts = sum(1 for cat in categories if safe_int(stats.get(cat, 0)) >= threshold)
    return counts >= 4


def is_five_by_five(stats: dict, threshold: int = 5) -> bool:
    """Check if stats constitute a 5x5 game.

    Args:
        stats: Dictionary with player stats
        threshold: Minimum value for each category (default 5)

    Returns:
        True if 5x5 achieved (5+ in all 5 categories)
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    return all(safe_int(stats.get(cat, 0)) >= threshold for cat in categories)


def is_near_triple_double(stats: dict, threshold: int = 10, near_threshold: int = 8) -> bool:
    """Check if stats constitute a near triple-double.

    Args:
        stats: Dictionary with player stats
        threshold: Threshold for full categories (default 10)
        near_threshold: Threshold for near category (default 8)

    Returns:
        True if near triple-double (2 categories at 10+, 1 at 8-9)
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    at_threshold = sum(1 for cat in categories if safe_int(stats.get(cat, 0)) >= threshold)
    near = sum(1 for cat in categories
               if near_threshold <= safe_int(stats.get(cat, 0)) < threshold)

    # Already a triple-double, not "near"
    if at_threshold >= 3:
        return False
    return at_threshold == 2 and near >= 1


def is_near_double_double(stats: dict, threshold: int = 10, near_threshold: int = 8) -> bool:
    """Check if stats constitute a near double-double.

    Args:
        stats: Dictionary with player stats
        threshold: Threshold for full category (default 10)
        near_threshold: Threshold for near category (default 8)

    Returns:
        True if near double-double (1 category at 10+, 1 at 8-9)
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    at_threshold = sum(1 for cat in categories if safe_int(stats.get(cat, 0)) >= threshold)
    near = sum(1 for cat in categories
               if near_threshold <= safe_int(stats.get(cat, 0)) < threshold)

    # Already a double-double, not "near"
    if at_threshold >= 2:
        return False
    return at_threshold == 1 and near >= 1


def is_all_around_game(stats: dict) -> bool:
    """Check if stats constitute an all-around game.

    All-around game: 5+ in all 5 categories OR 8+ in 4 categories.

    Args:
        stats: Dictionary with player stats

    Returns:
        True if all-around game achieved
    """
    categories = ['pts', 'trb', 'ast', 'stl', 'blk']
    values = [safe_int(stats.get(cat, 0)) for cat in categories]

    # 5+ in all 5 categories
    if all(v >= 5 for v in values):
        return True

    # 8+ in 4 categories
    at_eight = sum(1 for v in values if v >= 8)
    return at_eight >= 4


def is_hot_shooting(stats: dict, fg_pct_threshold: float = 0.6,
                    min_attempts: int = 10) -> bool:
    """Check if stats constitute a hot shooting game.

    Args:
        stats: Dictionary with player stats
        fg_pct_threshold: Minimum FG% (default 60%)
        min_attempts: Minimum FGA required (default 10)

    Returns:
        True if hot shooting game achieved
    """
    fg = safe_int(stats.get('fg', 0))
    fga = safe_int(stats.get('fga', 0))

    if fga < min_attempts:
        return False

    fg_pct = fg / fga if fga > 0 else 0
    return fg_pct >= fg_pct_threshold


def is_perfect_from_three(stats: dict, min_attempts: int = 4) -> bool:
    """Check if player shot 100% from three with minimum attempts.

    Args:
        stats: Dictionary with player stats
        min_attempts: Minimum 3PA required (default 4)

    Returns:
        True if perfect from three
    """
    fg3 = safe_int(stats.get('fg3', 0))
    fg3a = safe_int(stats.get('fg3a', 0))

    return fg3a >= min_attempts and fg3 == fg3a


def is_perfect_ft(stats: dict, min_attempts: int = 5) -> bool:
    """Check if player shot 100% from FT line with minimum attempts.

    Args:
        stats: Dictionary with player stats
        min_attempts: Minimum FTA required (default 5)

    Returns:
        True if perfect from free throw line
    """
    ft = safe_int(stats.get('ft', 0))
    fta = safe_int(stats.get('fta', 0))

    return fta >= min_attempts and ft == fta


def is_perfect_fg(stats: dict, min_attempts: int = 5) -> bool:
    """Check if player shot 100% from field with minimum attempts.

    Args:
        stats: Dictionary with player stats
        min_attempts: Minimum FGA required (default 5)

    Returns:
        True if perfect from field
    """
    fg = safe_int(stats.get('fg', 0))
    fga = safe_int(stats.get('fga', 0))

    return fga >= min_attempts and fg == fga


def is_efficient_scoring(stats: dict, ts_threshold: float = 0.65,
                         min_points: int = 15) -> bool:
    """Check if player had an efficient scoring game.

    Args:
        stats: Dictionary with player stats
        ts_threshold: Minimum TS% (default 65%)
        min_points: Minimum points required (default 15)

    Returns:
        True if efficient scoring game achieved
    """
    pts = safe_int(stats.get('pts', 0))
    fga = safe_int(stats.get('fga', 0))
    fta = safe_int(stats.get('fta', 0))

    if pts < min_points:
        return False

    ts = calculate_true_shooting(pts, fga, fta)
    return ts is not None and ts >= ts_threshold


def is_defensive_monster(stats: dict, combined_threshold: int = 7) -> bool:
    """Check if player had a defensive monster game.

    Args:
        stats: Dictionary with player stats
        combined_threshold: Combined steals + blocks threshold (default 7)

    Returns:
        True if defensive monster game achieved
    """
    stl = safe_int(stats.get('stl', 0))
    blk = safe_int(stats.get('blk', 0))

    return (stl + blk) >= combined_threshold


def is_zero_turnover_game(stats: dict, min_minutes: float = 20.0) -> bool:
    """Check if player had zero turnovers with significant minutes.

    Args:
        stats: Dictionary with player stats
        min_minutes: Minimum minutes played (default 20)

    Returns:
        True if zero turnover game achieved
    """
    tov = safe_int(stats.get('tov', 0))
    mp = stats.get('mp', 0)

    # Parse minutes if string
    if isinstance(mp, str):
        mp = parse_minutes(mp)

    return tov == 0 and mp >= min_minutes


def get_double_double_categories(stats: dict, threshold: int = 10) -> str:
    """Get string describing which categories hit double-digit.

    Args:
        stats: Dictionary with player stats
        threshold: Threshold for category (default 10)

    Returns:
        String like "pts/reb" or "pts/ast/reb"
    """
    category_names = {
        'pts': 'pts',
        'trb': 'reb',
        'ast': 'ast',
        'stl': 'stl',
        'blk': 'blk'
    }

    categories = [cat for cat in ['pts', 'trb', 'ast', 'stl', 'blk']
                  if safe_int(stats.get(cat, 0)) >= threshold]

    return '/'.join(category_names.get(c, c) for c in categories)


def calculate_assist_to_turnover_ratio(stats: dict) -> Optional[float]:
    """Calculate assist to turnover ratio.

    Args:
        stats: Dictionary with player stats

    Returns:
        AST/TOV ratio or None if no turnovers
    """
    ast = safe_int(stats.get('ast', 0))
    tov = safe_int(stats.get('tov', 0))

    if tov == 0:
        return None if ast == 0 else float('inf')
    return round(ast / tov, 2)


def calculate_rebound_rate(stats: dict, team_reb: int, opp_reb: int) -> Optional[float]:
    """Calculate approximate rebound rate.

    Args:
        stats: Dictionary with player stats
        team_reb: Team total rebounds
        opp_reb: Opponent total rebounds

    Returns:
        Rebound rate percentage or None
    """
    trb = safe_int(stats.get('trb', 0))
    total_reb = team_reb + opp_reb

    if total_reb == 0:
        return None
    return round((trb / total_reb) * 100, 1)
