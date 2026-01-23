"""
Website generator for interactive NBA stats HTML output with travel tracking.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Set
import pandas as pd

from ..utils.log import info
from ..utils.constants import (
    EXCEL_COLORS, NBA_ARENAS, NBA_TEAMS, TEAM_CODES,
    NBA_DIVISIONS, NBA_CONFERENCES, DIVISION_TO_CONFERENCE,
    TEAM_CODE_TO_DIVISION, TEAM_CODE_ALIASES
)


def _generate_js_constants() -> str:
    """Generate JavaScript constants from Python constants."""
    # Team codes mapping (full name -> code)
    team_codes_js = {name: info['code'] for name, info in NBA_TEAMS.items()}

    # Team short names (full name -> mascot)
    team_short_names = {}
    for name in NBA_TEAMS.keys():
        # Extract mascot (last word(s) after city)
        parts = name.split()
        # Handle special cases
        if 'Trail Blazers' in name:
            team_short_names[name] = 'Trail Blazers'
        elif '76ers' in name:
            team_short_names[name] = '76ers'
        else:
            team_short_names[name] = parts[-1]

    # Milestone categories for filtering
    milestone_categories = {
        'multi': ['quadruple_doubles', 'triple_doubles', 'double_doubles', 'near_triple_doubles',
                  'near_double_doubles', 'five_by_fives', 'all_around_games'],
        'scoring': ['seventy_point_games', 'sixty_point_games', 'fifty_point_games',
                    'forty_five_point_games', 'forty_point_games', 'thirty_five_point_games',
                    'thirty_point_games', 'twenty_five_point_games', 'twenty_point_games'],
        'rebounding': ['twenty_five_rebound_games', 'twenty_rebound_games', 'eighteen_rebound_games',
                       'fifteen_rebound_games', 'twelve_rebound_games', 'ten_rebound_games'],
        'assists': ['twenty_assist_games', 'fifteen_assist_games', 'twelve_assist_games', 'ten_assist_games'],
        'steals': ['ten_steal_games', 'seven_steal_games', 'five_steal_games', 'four_steal_games'],
        'blocks': ['ten_block_games', 'seven_block_games', 'five_block_games', 'four_block_games'],
        'threes': ['ten_three_games', 'eight_three_games', 'seven_three_games',
                   'six_three_games', 'five_three_games', 'perfect_from_three'],
        'efficiency': ['hot_shooting_games', 'perfect_ft_games', 'perfect_fg_games',
                       'efficient_scoring_games', 'high_game_score'],
        'combined': ['thirty_ten_games', 'twenty_five_ten_games', 'twenty_ten_games',
                     'twenty_ten_five_games', 'twenty_twenty_games', 'points_assists_double_double'],
        'defensive': ['defensive_monster_games', 'zero_turnover_games'],
        'plusminus': ['plus_25_games', 'plus_20_games', 'minus_25_games']
    }

    import json
    return f'''
// Auto-generated constants from Python
const TEAM_SHORT_NAMES = {json.dumps(team_short_names)};
const TEAM_CODES = {json.dumps(team_codes_js)};
const MILESTONE_CATEGORIES = {json.dumps(milestone_categories)};

function getShortName(fullName) {{
    return TEAM_SHORT_NAMES[fullName] || fullName;
}}

function getTeamCode(fullName) {{
    if (fullName && fullName.includes(', ')) {{
        return fullName.split(', ').map(t => TEAM_CODES[t.trim()] || t.trim().slice(0,3).toUpperCase()).join(', ');
    }}
    return TEAM_CODES[fullName] || fullName;
}}
'''


def generate_website_from_data(processed_data: Dict[str, pd.DataFrame], output_path: str) -> None:
    """
    Generate interactive HTML website from processed data.
    """
    info(f"Generating website: {output_path}")

    # Serialize DataFrames to JSON
    data = {}
    for key, df in processed_data.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            if key == 'player_games' and 'date' in df.columns:
                df = df.sort_values('date', ascending=False)
            data[key] = df.to_dict(orient='records')

    # Include milestones and descriptions (already dicts, not DataFrames)
    if 'milestones' in processed_data and isinstance(processed_data['milestones'], dict):
        data['milestones'] = processed_data['milestones']
    if 'milestone_descriptions' in processed_data and isinstance(processed_data['milestone_descriptions'], dict):
        data['milestone_descriptions'] = processed_data['milestone_descriptions']

    # Build games summary (one row per game, not per player)
    games_df = processed_data.get('player_games', pd.DataFrame())
    data['games'] = _build_games_summary(games_df)

    # Calculate venue/travel stats
    venue_stats = _calculate_venue_stats(games_df)
    data['venues'] = venue_stats['venues']

    # Calculate team checklist (teams/divisions/conferences seen)
    team_checklist = _calculate_team_checklist(games_df)
    data['teamChecklist'] = team_checklist

    # Calculate summary stats
    players_df = processed_data.get('players', pd.DataFrame())

    # Count milestones from the milestones dict
    milestones = data.get('milestones', {})
    total_milestones = sum(len(v) for v in milestones.values() if isinstance(v, list))

    summary = {
        'totalPlayers': len(players_df) if not players_df.empty else 0,
        'totalGames': len(data['games']),
        'totalPoints': int(players_df['Total PTS'].sum()) if not players_df.empty and 'Total PTS' in players_df.columns else 0,
        'tripleDoubles': len(milestones.get('triple_doubles', [])),
        'doubleDoubles': len(milestones.get('double_doubles', [])),
        'totalMilestones': total_milestones,
        'arenasVisited': venue_stats['arenas_visited'],
        'totalArenas': 30,
        'statesVisited': venue_stats['states_visited'],
        'citiesVisited': venue_stats['cities_visited'],
        'teamsSeen': team_checklist['summary']['teamsSeen'],
        'totalTeams': 30,
    }
    data['summary'] = summary

    json_data = json.dumps(data, default=str)

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    html = _generate_html(json_data, summary)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    info(f"Website saved: {output_path}")


def _build_games_summary(games_df: pd.DataFrame) -> List[Dict]:
    """Build one row per game with aggregated info."""
    if games_df.empty:
        return []

    games = []
    if 'game_id' not in games_df.columns:
        return []

    for game_id, group in games_df.groupby('game_id'):
        first = group.iloc[0]
        games.append({
            'game_id': game_id,
            'date': first.get('date', ''),
            'date_yyyymmdd': first.get('date_yyyymmdd', ''),
            'team': first.get('team', ''),
            'opponent': first.get('opponent', ''),
            'result': first.get('result', ''),
            'score': first.get('score', ''),
            'game_type': first.get('game_type', 'regular'),
            'players': len(group),
        })

    # Sort by date descending (use date_yyyymmdd for proper sorting)
    games.sort(key=lambda x: x.get('date_yyyymmdd', ''), reverse=True)
    return games


def _normalize_team_code(code: str) -> str:
    """Normalize team code using aliases."""
    if not code:
        return ''
    code = code.upper().strip()
    return TEAM_CODE_ALIASES.get(code, code)


def _get_team_code_from_name(name: str) -> str:
    """Get team code from team name."""
    if not name:
        return ''
    for team_name, info in NBA_TEAMS.items():
        if name == team_name or team_name in name or name in team_name:
            return info['code']
    return ''


def _calculate_team_checklist(games_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate team/division/conference progress checklist."""
    if games_df.empty:
        return {
            'teams': [],
            'divisions': {},
            'conferences': {},
            'summary': {'teamsSeen': 0, 'totalTeams': 30}
        }

    # Get unique games
    if 'game_id' in games_df.columns:
        unique_games = games_df.drop_duplicates(subset=['game_id'])
    else:
        unique_games = games_df

    # Track teams seen and visit counts
    teams_seen: Set[str] = set()
    team_visit_counts: Dict[str, int] = {}

    for _, game in unique_games.iterrows():
        game_id = str(game.get('game_id', ''))
        team = str(game.get('team', ''))
        opponent = str(game.get('opponent', ''))

        # Extract home team code from game_id (format: YYYYMMDD0XXX)
        home_code = None
        if len(game_id) >= 12 and game_id[8] == '0':
            home_code = _normalize_team_code(game_id[9:12])

        # Get team codes from names
        team_code = _get_team_code_from_name(team)
        opp_code = _get_team_code_from_name(opponent)

        # Add home team from game_id
        if home_code and home_code in TEAM_CODES:
            teams_seen.add(home_code)
            team_visit_counts[home_code] = team_visit_counts.get(home_code, 0) + 1

        # Add team (might be same as home, might be away)
        if team_code and team_code in TEAM_CODES:
            teams_seen.add(team_code)
            if team_code != home_code:  # Avoid double counting
                team_visit_counts[team_code] = team_visit_counts.get(team_code, 0) + 1

        # Add opponent
        if opp_code and opp_code in TEAM_CODES:
            teams_seen.add(opp_code)
            if opp_code != home_code and opp_code != team_code:
                team_visit_counts[opp_code] = team_visit_counts.get(opp_code, 0) + 1

    # Build team data for each team
    teams_data = []
    for team_name, info in NBA_TEAMS.items():
        code = info['code']
        division = info['division']
        conference = info['conference']

        teams_data.append({
            'code': code,
            'name': team_name,
            'division': division,
            'conference': conference,
            'seen': code in teams_seen,
            'visitCount': team_visit_counts.get(code, 0),
        })

    # Build division summaries
    divisions = {}
    for div_name, team_codes in NBA_DIVISIONS.items():
        div_teams = [t for t in teams_data if t['code'] in team_codes]
        teams_seen_count = sum(1 for t in div_teams if t['seen'])
        divisions[div_name] = {
            'name': div_name,
            'conference': DIVISION_TO_CONFERENCE[div_name],
            'teams': div_teams,
            'teamsSeen': teams_seen_count,
            'totalTeams': len(team_codes),
            'complete': teams_seen_count == len(team_codes),
        }

    # Build conference summaries
    conferences = {}
    for conf_name, div_names in NBA_CONFERENCES.items():
        conf_teams = [t for t in teams_data if t['conference'] == conf_name]
        teams_seen_count = sum(1 for t in conf_teams if t['seen'])
        conferences[conf_name] = {
            'name': conf_name,
            'divisions': div_names,
            'teamsSeen': teams_seen_count,
            'totalTeams': 15,
            'complete': teams_seen_count == 15,
        }

    return {
        'teams': teams_data,
        'divisions': divisions,
        'conferences': conferences,
        'summary': {
            'teamsSeen': len(teams_seen),
            'totalTeams': 30,
        }
    }


def _calculate_venue_stats(games_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate venue and travel statistics from games."""
    if games_df.empty:
        return {'venues': [], 'arenas_visited': 0, 'states_visited': 0, 'cities_visited': 0}

    if 'game_id' in games_df.columns:
        unique_games = games_df.drop_duplicates(subset=['game_id'])
    else:
        unique_games = games_df

    visited_codes: Set[str] = set()
    visited_cities: Set[str] = set()
    visited_states: Set[str] = set()
    venue_games: Dict[str, List] = {}

    for _, game in unique_games.iterrows():
        game_id = str(game.get('game_id', ''))
        date_str = str(game.get('date', ''))

        home_code = None
        if len(game_id) >= 12 and game_id[8] == '0':
            home_code = game_id[9:12].upper()

        if not home_code:
            continue

        actual_arena_code = home_code
        year = None
        if date_str and len(date_str) >= 4:
            try:
                year = int(date_str.split(',')[-1].strip()) if ',' in date_str else int(date_str[:4])
            except:
                pass

        if home_code == 'LAC' and year and year < 2024:
            actual_arena_code = 'LAL'

        if actual_arena_code in NBA_ARENAS:
            arena = NBA_ARENAS[actual_arena_code]
            visited_codes.add(actual_arena_code)
            visited_cities.add(arena['city'])
            visited_states.add(arena['state'])

            if actual_arena_code not in venue_games:
                venue_games[actual_arena_code] = []
            venue_games[actual_arena_code].append({'date': date_str, 'game_id': game_id})

    venues = []
    for code, arena in NBA_ARENAS.items():
        games = venue_games.get(code, [])
        venues.append({
            'code': code,
            'name': arena['name'],
            'team': arena['team'],
            'city': arena['city'],
            'state': arena['state'],
            'lat': arena['lat'],
            'lng': arena['lng'],
            'visited': code in visited_codes,
            'games': len(games),
            'first_visit': min(g['date'] for g in games) if games else None,
            'last_visit': max(g['date'] for g in games) if games else None,
        })

    return {
        'venues': venues,
        'arenas_visited': len(visited_codes),
        'states_visited': len(visited_states),
        'cities_visited': len(visited_cities),
    }


def _generate_html(json_data: str, summary: Dict[str, Any]) -> str:
    generated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBA Stats Tracker</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
{_get_css()}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-controls">
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark mode">&#127769;</button>
        </div>
        <h1>NBA Stats Tracker</h1>
        <p class="header-subtitle">Game-by-game statistics & arena tracking</p>
        <div class="dashboard-grid">
            <div class="progress-ring-container">
                <svg class="progress-ring" viewBox="0 0 100 100">
                    <circle class="progress-ring-bg" cx="50" cy="50" r="42"/>
                    <circle class="progress-ring-fill" cx="50" cy="50" r="42"
                        style="--progress: {(summary.get('teamsSeen', 0) / 30) * 100}"/>
                </svg>
                <div class="progress-ring-text">
                    <div class="progress-ring-value">{summary.get('teamsSeen', 0)}<span class="progress-ring-total">/30</span></div>
                    <div class="progress-ring-label">Teams</div>
                </div>
            </div>
            <div class="progress-ring-container">
                <svg class="progress-ring" viewBox="0 0 100 100">
                    <circle class="progress-ring-bg" cx="50" cy="50" r="42"/>
                    <circle class="progress-ring-fill arenas" cx="50" cy="50" r="42"
                        style="--progress: {(summary.get('arenasVisited', 0) / 30) * 100}"/>
                </svg>
                <div class="progress-ring-text">
                    <div class="progress-ring-value">{summary.get('arenasVisited', 0)}<span class="progress-ring-total">/30</span></div>
                    <div class="progress-ring-label">Arenas</div>
                </div>
            </div>
            <div class="progress-ring-container">
                <svg class="progress-ring" viewBox="0 0 100 100">
                    <circle class="progress-ring-bg" cx="50" cy="50" r="42"/>
                    <circle class="progress-ring-fill milestones" cx="50" cy="50" r="42"
                        style="--progress: {min((summary.get('totalMilestones', 0) / 100) * 100, 100)}"/>
                </svg>
                <div class="progress-ring-text">
                    <div class="progress-ring-value">{summary.get('totalMilestones', 0)}</div>
                    <div class="progress-ring-label">Milestones</div>
                </div>
            </div>
            <div class="stats-column">
                <div class="mini-stat">
                    <span class="mini-stat-value">{summary.get('totalGames', 0)}</span>
                    <span class="mini-stat-label">Games</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-value">{summary.get('totalPlayers', 0)}</span>
                    <span class="mini-stat-label">Players</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-value">{summary.get('statesVisited', 0)}</span>
                    <span class="mini-stat-label">States</span>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
        <nav class="tabs">
            <button class="tab active" onclick="showSection('games')" data-section="games">Games</button>
            <button class="tab" onclick="showSection('players')" data-section="players">Players</button>
            <button class="tab" onclick="showSection('teams')" data-section="teams">Teams</button>
            <button class="tab" onclick="showSection('venues')" data-section="venues">Arenas</button>
            <button class="tab" onclick="showSection('map')" data-section="map">Map</button>
            <button class="tab" onclick="showSection('achievements')" data-section="achievements">Achievements</button>
        </nav>

        <!-- Games Section -->
        <div id="games" class="section active">
            <h2>Games Attended</h2>
            <div class="games-grid" id="games-grid"></div>
        </div>

        <!-- Players Section -->
        <div id="players" class="section">
            <h2>Player Statistics
                <div class="section-actions">
                    <button class="btn btn-secondary" onclick="downloadCSV('players')">Download CSV</button>
                </div>
            </h2>
            <div class="filters">
                <div class="filter-group">
                    <label>Search</label>
                    <input type="text" id="players-search" placeholder="Search..." onkeyup="filterPlayersTable()">
                </div>
                <div class="filter-group">
                    <label>Team</label>
                    <select id="players-team" onchange="filterPlayersTable()"><option value="">All Teams</option></select>
                </div>
                <div class="filter-group">
                    <label>Min Games</label>
                    <input type="number" id="players-min-games" min="1" placeholder="1" onchange="filterPlayersTable()">
                </div>
                <button class="clear-filters" onclick="clearPlayersFilters()">Clear</button>
            </div>
            <div class="table-container">
                <table id="players-table"><thead></thead><tbody></tbody></table>
            </div>
        </div>

        <!-- Teams Section -->
        <div id="teams" class="section">
            <h2>Team Checklist</h2>
            <div class="team-progress">
                <div class="progress-bar"><div class="progress-fill" id="team-progress-fill"></div></div>
                <div class="progress-text" id="team-progress-text">0/30 Teams Seen</div>
            </div>
            <div class="checklist-tabs">
                <button class="checklist-tab active" onclick="showChecklistView('all')" data-view="all">All Teams</button>
                <button class="checklist-tab" onclick="showChecklistView('east')" data-view="east">Eastern</button>
                <button class="checklist-tab" onclick="showChecklistView('west')" data-view="west">Western</button>
                <button class="checklist-tab" onclick="showChecklistView('divisions')" data-view="divisions">By Division</button>
            </div>
            <div id="team-checklist-container" class="team-checklist-container"></div>
        </div>

        <!-- Venues Section -->
        <div id="venues" class="section">
            <h2>Arena Checklist</h2>
            <div class="arena-progress">
                <div class="progress-bar"><div class="progress-fill" id="arena-progress-fill"></div></div>
                <div class="progress-text" id="arena-progress-text">0/30 Arenas Visited</div>
            </div>
            <div class="filters">
                <div class="filter-group">
                    <label>Show</label>
                    <select id="venues-filter" onchange="filterVenuesTable()">
                        <option value="all">All Arenas</option>
                        <option value="visited">Visited Only</option>
                        <option value="unvisited">Not Visited</option>
                    </select>
                </div>
            </div>
            <div class="table-container">
                <table id="venues-table">
                    <thead><tr><th>Team</th><th>Arena</th><th>City</th><th>State</th><th>Games</th><th>First Visit</th><th>Status</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <!-- Map Section -->
        <div id="map" class="section">
            <h2>Arena Map</h2>
            <div class="map-legend">
                <span class="legend-item"><span class="legend-dot visited"></span> Visited</span>
                <span class="legend-item"><span class="legend-dot not-visited"></span> Not Visited</span>
            </div>
            <div id="arena-map"></div>
        </div>

        <!-- Achievements Section -->
        <div id="achievements" class="section">
            <h2>Milestones & Achievements ({summary.get('totalMilestones', 0)} total)</h2>
            <div class="milestone-filters">
                <div class="filter-group">
                    <label>Category</label>
                    <select id="milestone-category" onchange="filterMilestones()">
                        <option value="all">All Categories</option>
                        <option value="multi">Multi-Category</option>
                        <option value="scoring">Scoring</option>
                        <option value="rebounding">Rebounding</option>
                        <option value="assists">Assists</option>
                        <option value="steals">Steals</option>
                        <option value="blocks">Blocks</option>
                        <option value="threes">Three-Pointers</option>
                        <option value="efficiency">Efficiency</option>
                        <option value="combined">Combined</option>
                        <option value="defensive">Defensive</option>
                        <option value="plusminus">Plus/Minus</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Search Player</label>
                    <input type="text" id="milestone-search" placeholder="Search..." onkeyup="filterMilestones()">
                </div>
            </div>
            <div id="milestones-container" class="milestones-container"></div>
        </div>
    </div>

    <!-- Box Score Modal -->
    <div class="modal" id="boxscore-modal" onclick="if(event.target === this) closeModal('boxscore-modal')">
        <div class="modal-content modal-large">
            <button class="modal-close" onclick="closeModal('boxscore-modal')">&times;</button>
            <div id="boxscore-detail"></div>
        </div>
    </div>

    <!-- Player Modal -->
    <div class="modal" id="player-modal" onclick="if(event.target === this) closeModal('player-modal')">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal('player-modal')">&times;</button>
            <div id="player-detail"></div>
        </div>
    </div>

    <div id="toast" class="toast"></div>

    <footer><p>Generated: {generated_time}</p></footer>

    <script>
const DATA = {json_data};
{_get_javascript()}
    </script>
</body>
</html>'''


def _get_css() -> str:
    return '''
:root {
    --bg-primary: #f5f5f5;
    --bg-secondary: #ffffff;
    --bg-header: linear-gradient(135deg, #1D428A 0%, #C8102E 100%);
    --text-primary: #333333;
    --text-secondary: #666666;
    --text-muted: #999999;
    --border-color: #e0e0e0;
    --accent-color: #1D428A;
    --hover-color: #f8f9fa;
    --shadow: 0 4px 6px rgba(0,0,0,0.1);
    --success: #27ae60;
}

[data-theme="dark"] {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-header: linear-gradient(135deg, #0f3460, #1a1a2e);
    --text-primary: #eaeaea;
    --text-secondary: #b0b0b0;
    --text-muted: #777777;
    --border-color: #2a2a4a;
    --accent-color: #4a9eff;
    --hover-color: #1e2a4a;
    --shadow: 0 4px 6px rgba(0,0,0,0.3);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}

.header {
    background: var(--bg-header);
    color: white;
    padding: 2rem;
    text-align: center;
    position: relative;
}
.header h1 { font-size: 2rem; margin-bottom: 0.25rem; }
.header-subtitle { font-size: 0.9rem; opacity: 0.8; margin-bottom: 1.5rem; }
.header-controls { position: absolute; top: 1rem; right: 1rem; }
.theme-toggle {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    width: 40px; height: 40px;
    cursor: pointer;
    font-size: 1.1rem;
    color: white;
}

/* Dashboard Grid */
.dashboard-grid {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
    padding: 0.5rem;
}
.progress-ring-container {
    position: relative;
    width: 110px;
    height: 110px;
}
.progress-ring {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
}
.progress-ring-bg {
    fill: none;
    stroke: rgba(255,255,255,0.2);
    stroke-width: 8;
}
.progress-ring-fill {
    fill: none;
    stroke: #4ade80;
    stroke-width: 8;
    stroke-linecap: round;
    stroke-dasharray: 264;
    stroke-dashoffset: calc(264 - (264 * var(--progress) / 100));
    transition: stroke-dashoffset 1s ease-out;
}
.progress-ring-fill.arenas { stroke: #60a5fa; }
.progress-ring-fill.milestones { stroke: #fbbf24; }
.progress-ring-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}
.progress-ring-value {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.2;
}
.progress-ring-total {
    font-size: 0.9rem;
    opacity: 0.7;
}
.progress-ring-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    opacity: 0.8;
    letter-spacing: 0.5px;
}
.stats-column {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.mini-stat {
    background: rgba(255,255,255,0.1);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 120px;
}
.mini-stat-value {
    font-size: 1.25rem;
    font-weight: 700;
}
.mini-stat-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    opacity: 0.8;
}

@media (max-width: 600px) {
    .dashboard-grid { gap: 1rem; }
    .progress-ring-container { width: 90px; height: 90px; }
    .progress-ring-value { font-size: 1.2rem; }
    .stats-column { flex-direction: row; flex-wrap: wrap; justify-content: center; }
}

.container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }

.tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; justify-content: center; }
.tab {
    padding: 0.6rem 1.2rem;
    background: var(--bg-secondary);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    color: var(--text-primary);
    box-shadow: var(--shadow);
}
.tab:hover { background: var(--hover-color); }
.tab.active { background: var(--accent-color); color: white; }

.section {
    display: none;
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
}
.section.active { display: block; }
.section h2 {
    margin-bottom: 1rem;
    color: var(--accent-color);
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Games Grid */
.games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1rem;
}
.game-card {
    background: var(--bg-primary);
    border-radius: 10px;
    padding: 1.25rem;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    border-left: 4px solid var(--accent-color);
}
.game-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
.game-card-date { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.game-card-teams { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; }
.game-card-result { font-size: 0.9rem; color: var(--text-secondary); }
.game-card-result .win { color: var(--success); font-weight: 600; }
.game-card-result .loss { color: #e74c3c; font-weight: 600; }

/* Filters */
.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    align-items: flex-end;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 8px;
}
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; }
.filter-group label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; }
.filter-group input, .filter-group select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    min-width: 120px;
}
.clear-filters {
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
    color: var(--text-secondary);
}
.btn { padding: 0.5rem 1rem; background: var(--accent-color); color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--border-color); }
.section-actions { display: flex; gap: 0.5rem; }

/* Tables */
.table-container { overflow-x: auto; max-height: 600px; overflow-y: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 0.6rem; text-align: left; border-bottom: 1px solid var(--border-color); }
th {
    background: var(--bg-primary);
    font-weight: 600;
    position: sticky;
    top: 0;
    cursor: pointer;
    white-space: nowrap;
    z-index: 10;
}
th[title] {
    text-decoration: underline dotted;
    text-underline-offset: 3px;
    text-decoration-color: var(--text-muted);
}
th:hover { background: var(--hover-color); }
th.sort-active { background: var(--hover-color); color: var(--accent-color); }
tr:hover { background: var(--hover-color); }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.player-link { color: var(--accent-color); cursor: pointer; text-decoration: underline; }

/* Arena Progress */
.arena-progress, .team-progress { margin-bottom: 1.5rem; text-align: center; }
.progress-bar { background: var(--bg-primary); border-radius: 10px; height: 20px; overflow: hidden; margin-bottom: 0.5rem; }
.progress-fill { background: linear-gradient(90deg, #27ae60, #2ecc71); height: 100%; border-radius: 10px; transition: width 0.3s; }
.progress-text { font-size: 1rem; font-weight: 600; }
.status-visited { color: var(--success); font-weight: 600; }
.status-not-visited { color: var(--text-muted); }

/* Team Checklist */
.checklist-tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; justify-content: center; }
.checklist-tab {
    padding: 0.5rem 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    color: var(--text-primary);
}
.checklist-tab:hover { background: var(--hover-color); }
.checklist-tab.active { background: var(--accent-color); color: white; border-color: var(--accent-color); }

.team-checklist-container { display: grid; gap: 1.5rem; }
.division-card {
    background: var(--bg-primary);
    border-radius: 10px;
    padding: 1.25rem;
    border-left: 4px solid var(--accent-color);
}
.division-card.complete { border-left-color: var(--success); }
.division-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}
.division-header h4 { margin: 0; color: var(--accent-color); }
.division-header .badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-complete { background: var(--success); color: white; }
.badge-progress { background: var(--bg-secondary); color: var(--text-secondary); }
.team-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem; }
.team-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: 6px;
    font-size: 0.9rem;
}
.team-item.seen { background: rgba(39, 174, 96, 0.1); }
.team-item .check { color: var(--success); font-weight: bold; }
.team-item .not-seen { color: var(--text-muted); }
.team-item .visit-count { margin-left: auto; color: var(--text-muted); font-size: 0.8rem; }
.conference-summary {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.conference-box {
    background: var(--bg-primary);
    padding: 1rem 1.5rem;
    border-radius: 10px;
    text-align: center;
    min-width: 150px;
}
.conference-box h5 { margin: 0 0 0.5rem 0; color: var(--accent-color); }
.conference-box .count { font-size: 1.5rem; font-weight: 700; }
.conference-box.complete .count { color: var(--success); }

/* Map */
#arena-map { height: 500px; border-radius: 8px; border: 1px solid var(--border-color); }
.map-legend { display: flex; gap: 1.5rem; margin-bottom: 1rem; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; }
.legend-dot { width: 16px; height: 16px; border-radius: 50%; }
.legend-dot.visited { background: #27ae60; }
.legend-dot.not-visited { background: #95a5a6; }

/* Milestones */
.milestone-filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 8px;
    flex-wrap: wrap;
    align-items: flex-end;
}
.milestones-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; }
.milestone-card {
    background: var(--bg-primary);
    border-radius: 10px;
    padding: 1rem;
    border-left: 4px solid var(--accent-color);
}
.milestone-card h4 {
    font-size: 1rem;
    margin-bottom: 0.75rem;
    color: var(--accent-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.milestone-card h4 .count {
    background: var(--accent-color);
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
}
.milestone-card .empty { color: var(--text-muted); font-style: italic; padding: 0.5rem 0; }
.sub-section h3 { font-size: 1.1rem; margin-bottom: 0.75rem; color: var(--accent-color); }

/* Modals */
.modal {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.6);
    z-index: 1000;
    justify-content: center;
    align-items: center;
}
.modal.active { display: flex; }
.modal-content {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    max-width: 700px;
    max-height: 85vh;
    overflow-y: auto;
    width: 95%;
    position: relative;
}
.modal-content.modal-large { max-width: 1000px; }
.modal-close {
    position: absolute;
    top: 1rem; right: 1rem;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-secondary);
}

/* Player Stats & Chart */
.player-stat-box {
    background: var(--bg-primary);
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
}
.player-stat-box .number { font-size: 1.4rem; font-weight: 700; color: var(--accent-color); }
.player-stat-box .label { font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); }

.chart-section {
    background: var(--bg-primary);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.chart-header h4 { margin: 0; font-size: 1rem; }
.chart-toggles { display: flex; gap: 0.5rem; }
.chart-toggle {
    padding: 0.35rem 0.75rem;
    border: 1px solid var(--border-color);
    background: var(--bg-secondary);
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
    color: var(--text-primary);
    transition: all 0.2s;
}
.chart-toggle:hover { background: var(--hover-color); }
.chart-toggle.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}
.chart-container {
    height: 200px;
    position: relative;
}

/* Box Score */
.boxscore-header { text-align: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--border-color); }
.boxscore-header h2 { font-size: 1.4rem; margin-bottom: 0.25rem; }
.boxscore-header .date { color: var(--text-secondary); }
.boxscore-header .result { font-size: 1.2rem; font-weight: 600; margin-top: 0.5rem; }
.boxscore-section { margin-bottom: 1.5rem; }
.boxscore-section h4 { margin-bottom: 0.5rem; color: var(--accent-color); }

/* Team-separated box scores */
.boxscore-team { margin-bottom: 1.5rem; }
.boxscore-team-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: var(--accent-color);
    color: white;
    border-radius: 8px 8px 0 0;
    margin: 0;
}
.boxscore-team-header .team-total {
    font-size: 0.9rem;
    opacity: 0.9;
}
.boxscore-table { border-radius: 0 0 8px 8px; overflow: hidden; }
.roster-divider {
    background: var(--bg-primary) !important;
}
.roster-divider td {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0.4rem 0.6rem !important;
    letter-spacing: 0.5px;
}

.toast {
    position: fixed;
    bottom: 2rem; right: 2rem;
    background: var(--text-primary);
    color: var(--bg-secondary);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s;
    z-index: 2000;
}
.toast.show { transform: translateY(0); opacity: 1; }

footer { text-align: center; padding: 1.5rem; color: var(--text-muted); font-size: 0.8rem; }

@media (max-width: 768px) {
    .header { padding: 1.5rem 1rem; }
    .header h1 { font-size: 1.5rem; }
    .stats-overview { gap: 0.5rem; }
    .stat-box { padding: 0.5rem 0.75rem; min-width: 70px; }
    .stat-box .number { font-size: 1.25rem; }
    .container { padding: 1rem; }
    .games-grid { grid-template-columns: 1fr; }
    .achievements-grid { grid-template-columns: 1fr; }
    #arena-map { height: 350px; }
}
    '''


def _get_javascript() -> str:
    return _generate_js_constants() + '''
let arenaMap = null;
let filteredPlayers = [];
let playerSortCol = null;
let playerSortAsc = false;

// Theme
function toggleTheme() {
    const html = document.documentElement;
    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    if (arenaMap) setTimeout(() => arenaMap.invalidateSize(), 100);
}
(function() {
    const saved = localStorage.getItem('theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
    else if (window.matchMedia('(prefers-color-scheme: dark)').matches)
        document.documentElement.setAttribute('data-theme', 'dark');
})();

// Sections
function showSection(id) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelector(`[data-section="${id}"]`).classList.add('active');
    document.getElementById(id).classList.add('active');
    if (id === 'map' && !arenaMap) initMap();
}

// Modals
function openModal(id) { document.getElementById(id).classList.add('active'); document.body.style.overflow = 'hidden'; }
function closeModal(id) { document.getElementById(id).classList.remove('active'); document.body.style.overflow = ''; }
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

// Games Grid
function renderGamesGrid() {
    const games = DATA.games || [];
    const grid = document.getElementById('games-grid');

    if (!games.length) {
        grid.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No games found</p>';
        return;
    }

    grid.innerHTML = games.map((g, i) => {
        const resultClass = g.result && g.result.toLowerCase().startsWith('w') ? 'win' : 'loss';
        const gameType = g.game_type && g.game_type !== 'regular' ? `<span style="font-size:0.75rem;opacity:0.7;margin-left:0.5rem;">(${g.game_type})</span>` : '';
        return `
        <div class="game-card" onclick="showBoxScore('${g.game_id}')">
            <div class="game-card-date">${g.date}</div>
            <div class="game-card-teams">${g.team} vs ${g.opponent}${gameType}</div>
            <div class="game-card-result"><span class="${resultClass}">${g.result || ''}</span> ${g.score || ''}</div>
        </div>`;
    }).join('');
}

// Format minutes (handles both decimal and MM:SS formats)
function formatMinutes(mp) {
    if (mp == null || mp === '' || mp === '-') return '-';
    if (typeof mp === 'string' && mp.includes(':')) return mp;
    const num = parseFloat(mp);
    if (isNaN(num)) return '-';
    const mins = Math.floor(num);
    const secs = Math.round((num - mins) * 60);
    return secs > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${mins}:00`;
}

// Box Score Modal
function showBoxScore(gameId) {
    const playerGames = (DATA.player_games || []).filter(p => p.game_id === gameId);
    const gameInfo = (DATA.games || []).find(g => g.game_id === gameId);

    if (!playerGames.length) { showToast('No box score data'); return; }

    const detail = document.getElementById('boxscore-detail');
    const resultClass = gameInfo?.result?.toLowerCase().startsWith('w') ? 'win' : 'loss';
    const gameType = gameInfo?.game_type && gameInfo.game_type !== 'regular' ? ` (${gameInfo.game_type})` : '';

    // Group players by team
    const teams = {};
    playerGames.forEach(p => {
        const team = p.team || 'Unknown';
        if (!teams[team]) teams[team] = { starters: [], bench: [] };
        if (p.starter) {
            teams[team].starters.push(p);
        } else {
            teams[team].bench.push(p);
        }
    });

    // Sort each group by minutes played (descending)
    Object.values(teams).forEach(t => {
        t.starters.sort((a, b) => (b.mp || 0) - (a.mp || 0));
        t.bench.sort((a, b) => (b.mp || 0) - (a.mp || 0));
    });

    let html = `
    <div class="boxscore-header">
        <h2>${gameInfo?.team || ''} vs ${gameInfo?.opponent || ''}${gameType}</h2>
        <div class="date">${gameInfo?.date || ''}</div>
        <div class="result"><span class="${resultClass}">${gameInfo?.result || ''}</span> ${gameInfo?.score || ''}</div>
    </div>`;

    // Render each team's box score
    Object.entries(teams).forEach(([teamName, roster]) => {
        const teamCode = getTeamCode(teamName);
        const teamPts = [...roster.starters, ...roster.bench].reduce((sum, p) => sum + (p.pts || 0), 0);

        html += `
        <div class="boxscore-team">
            <h4 class="boxscore-team-header">${teamName} <span class="team-total">${teamPts} PTS</span></h4>
            <div class="table-container">
                <table class="boxscore-table">
                    <thead><tr>
                        <th>Player</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th>
                        <th>STL</th><th>BLK</th><th>TO</th><th>FG</th><th>3P</th><th>FT</th><th>+/-</th>
                    </tr></thead>
                    <tbody>`;

        // Starters
        if (roster.starters.length > 0) {
            html += `<tr class="roster-divider"><td colspan="12">Starters</td></tr>`;
            roster.starters.forEach(p => {
                html += renderBoxScoreRow(p);
            });
        }

        // Bench
        if (roster.bench.length > 0) {
            html += `<tr class="roster-divider"><td colspan="12">Bench</td></tr>`;
            roster.bench.forEach(p => {
                html += renderBoxScoreRow(p);
            });
        }

        html += '</tbody></table></div></div>';
    });

    detail.innerHTML = html;
    openModal('boxscore-modal');
}

function renderBoxScoreRow(p) {
    return `<tr>
        <td><span class="player-link" onclick="event.stopPropagation();showPlayerDetail('${(p.player||'').replace(/'/g, "\\'")}')">${p.player}</span></td>
        <td class="num">${formatMinutes(p.mp)}</td>
        <td class="num">${p.pts || 0}</td>
        <td class="num">${p.trb || 0}</td>
        <td class="num">${p.ast || 0}</td>
        <td class="num">${p.stl || 0}</td>
        <td class="num">${p.blk || 0}</td>
        <td class="num">${p.tov || 0}</td>
        <td class="num">${p.fg || 0}-${p.fga || 0}</td>
        <td class="num">${p.fg3 || 0}-${p.fg3a || 0}</td>
        <td class="num">${p.ft || 0}-${p.fta || 0}</td>
        <td class="num">${p.plus_minus || 0}</td>
    </tr>`;
}

// Players Table
const playerCols = [
    'Player', 'Team', 'Games', 'MPG', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TOPG',
    'FG%', '3P%', 'FT%', 'TS%', 'eFG%', 'Total PTS', 'Total REB', 'Total AST', 'Total +/-'
];

// Tooltips for stat abbreviations
const statTooltips = {
    'MPG': 'Minutes Per Game',
    'PPG': 'Points Per Game',
    'RPG': 'Rebounds Per Game',
    'APG': 'Assists Per Game',
    'SPG': 'Steals Per Game',
    'BPG': 'Blocks Per Game',
    'TOPG': 'Turnovers Per Game',
    'FG%': 'Field Goal Percentage',
    '3P%': 'Three-Point Percentage',
    'FT%': 'Free Throw Percentage',
    'TS%': 'True Shooting Percentage',
    'eFG%': 'Effective Field Goal Percentage',
    'Total PTS': 'Total Points Scored',
    'Total REB': 'Total Rebounds',
    'Total AST': 'Total Assists',
    'Total +/-': 'Cumulative Plus/Minus'
};

// Columns that should show 1 decimal (per-game stats)
const perGameCols = ['MPG', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TOPG'];
// Columns that should show 3 decimals (percentages)
const pctCols = ['FG%', '3P%', 'FT%', 'TS%', 'eFG%'];

function formatStatValue(val, col) {
    if (val == null || val === '') return '';
    if (typeof val !== 'number') return val;
    if (pctCols.includes(col)) return val.toFixed(3);
    if (perGameCols.includes(col)) return val.toFixed(1);
    return Number.isInteger(val) ? val : val.toFixed(1);
}

function renderPlayersTable() {
    const table = document.getElementById('players-table');
    const data = filteredPlayers;

    if (!data || !data.length) {
        table.innerHTML = '<tr><td colspan="20" style="text-align:center;padding:2rem;">No players</td></tr>';
        return;
    }

    let html = '<thead><tr>' + playerCols.map(c => {
        const tooltip = statTooltips[c] ? ` title="${statTooltips[c]}"` : '';
        const sortIndicator = playerSortCol === c ? (playerSortAsc ? ' \\u25B2' : ' \\u25BC') : '';
        const activeClass = playerSortCol === c ? ' class="sort-active"' : '';
        return `<th onclick="sortPlayersTable('${c}')"${tooltip}${activeClass}>${c}${sortIndicator}</th>`;
    }).join('') + '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        playerCols.forEach(col => {
            let v = row[col];
            if (v == null) v = '';
            if (typeof v === 'number') {
                v = formatStatValue(v, col);
                html += `<td class="num">${v}</td>`;
            } else if (col === 'Player') {
                html += `<td><span class="player-link" onclick="showPlayerDetail('${(v||'').replace(/'/g, \"\\\\'\")}')">${v}</span></td>`;
            } else if (col === 'Team') {
                html += `<td>${getTeamCode(v)}</td>`;
            } else {
                html += `<td>${v}</td>`;
            }
        });
        html += '</tr>';
    });
    table.innerHTML = html + '</tbody>';
}

function sortPlayersTable(col) {
    // Toggle direction if same column, otherwise default to descending for numbers, ascending for text
    if (playerSortCol === col) {
        playerSortAsc = !playerSortAsc;
    } else {
        playerSortCol = col;
        // Default: numbers sort descending (highest first), text sorts ascending (A-Z)
        const isNumericCol = filteredPlayers.length > 0 && typeof filteredPlayers[0][col] === 'number';
        playerSortAsc = !isNumericCol;
    }

    filteredPlayers.sort((a, b) => {
        let av = a[col], bv = b[col];
        if (av == null) av = '';
        if (bv == null) bv = '';

        let result;
        if (typeof av === 'number' && typeof bv === 'number') {
            result = av - bv;
        } else {
            result = String(av).localeCompare(String(bv));
        }

        return playerSortAsc ? result : -result;
    });
    renderPlayersTable();
}

function filterPlayersTable() {
    const search = document.getElementById('players-search').value.toLowerCase();
    const team = document.getElementById('players-team').value;
    const minG = parseInt(document.getElementById('players-min-games').value) || 0;

    filteredPlayers = (DATA.players || []).filter(p => {
        if (search && !Object.values(p).some(v => String(v).toLowerCase().includes(search))) return false;
        if (team && !String(p.Team || '').includes(team)) return false;
        if (minG && (p.Games || 0) < minG) return false;
        return true;
    });
    renderPlayersTable();
}

function clearPlayersFilters() {
    document.getElementById('players-search').value = '';
    document.getElementById('players-team').value = '';
    document.getElementById('players-min-games').value = '';
    playerSortCol = null;
    playerSortAsc = false;
    filterPlayersTable();
}

function populateTeamDropdown() {
    const teams = new Set();
    (DATA.players || []).forEach(p => { if (p.Team) p.Team.split(', ').forEach(t => teams.add(t)); });
    const sel = document.getElementById('players-team');
    Array.from(teams).sort().forEach(t => {
        const o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o);
    });
}

// Player Detail with Chart
let playerChart = null;

function showPlayerDetail(name) {
    const games = (DATA.player_games || []).filter(g => g.player === name).sort((a,b) => (b.date_yyyymmdd||'').localeCompare(a.date_yyyymmdd||''));
    const stats = (DATA.players || []).find(p => p.Player === name);

    if (!stats && !games.length) { showToast('Player not found'); return; }

    let html = `<h2>${name}</h2>`;
    if (stats) {
        html += `<p style="color:var(--text-secondary);margin-bottom:1rem;">${stats.Team || ''} | ${stats.Games || 0} games</p>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.75rem;margin-bottom:1.5rem;">
            <div class="player-stat-box"><div class="number">${(stats.PPG||0).toFixed(1)}</div><div class="label">PPG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.RPG||0).toFixed(1)}</div><div class="label">RPG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.APG||0).toFixed(1)}</div><div class="label">APG</div></div>
            <div class="player-stat-box"><div class="number">${(stats.MPG||0).toFixed(1)}</div><div class="label">MPG</div></div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-bottom:1.5rem;">
            <div style="text-align:center;"><strong>${((stats['FG%']||0)*100).toFixed(1)}%</strong><br><small>FG%</small></div>
            <div style="text-align:center;"><strong>${((stats['3P%']||0)*100).toFixed(1)}%</strong><br><small>3P%</small></div>
            <div style="text-align:center;"><strong>${((stats['FT%']||0)*100).toFixed(1)}%</strong><br><small>FT%</small></div>
        </div>`;
    }

    // Add chart section if multiple games
    if (games.length > 1) {
        html += `
        <div class="chart-section">
            <div class="chart-header">
                <h4>Performance Trend</h4>
                <div class="chart-toggles">
                    <button class="chart-toggle active" data-stat="pts">PTS</button>
                    <button class="chart-toggle" data-stat="trb">REB</button>
                    <button class="chart-toggle" data-stat="ast">AST</button>
                    <button class="chart-toggle" data-stat="game_score">GmSc</button>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="player-chart"></canvas>
            </div>
        </div>`;
    }

    if (games.length) {
        html += '<h4 style="margin-top:1.5rem;margin-bottom:0.5rem;">Game Log</h4><div class="table-container" style="max-height:250px;"><table><thead><tr><th>Date</th><th>Opp</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th><th>STL</th><th>BLK</th><th>FG</th><th>+/-</th></tr></thead><tbody>';
        games.forEach(g => html += `<tr><td>${g.date||''}</td><td>${g.opponent||''}</td><td>${formatMinutes(g.mp)}</td><td>${g.pts||0}</td><td>${g.trb||0}</td><td>${g.ast||0}</td><td>${g.stl||0}</td><td>${g.blk||0}</td><td>${g.fg||0}-${g.fga||0}</td><td>${g.plus_minus||0}</td></tr>`);
        html += '</tbody></table></div>';
    }

    document.getElementById('player-detail').innerHTML = html;
    openModal('player-modal');

    // Initialize chart after DOM update
    if (games.length > 1) {
        setTimeout(() => initPlayerChart(games, 'pts'), 100);

        // Add toggle listeners
        document.querySelectorAll('.chart-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-toggle').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                initPlayerChart(games, e.target.dataset.stat);
            });
        });
    }
}

function initPlayerChart(games, stat) {
    const ctx = document.getElementById('player-chart');
    if (!ctx) return;

    if (playerChart) {
        playerChart.destroy();
    }

    // Reverse for chart (oldest to newest, left to right)
    const chartGames = [...games].reverse();

    const labels = chartGames.map(g => {
        const d = g.date || '';
        // Shorten date for display
        const parts = d.split(' ');
        return parts.length >= 2 ? `${parts[0].slice(0,3)} ${parts[1]}` : d;
    });

    const data = chartGames.map(g => g[stat] || 0);
    const avg = data.reduce((a,b) => a+b, 0) / data.length;

    const statLabels = { pts: 'Points', trb: 'Rebounds', ast: 'Assists', game_score: 'Game Score' };
    const statColors = { pts: '#4ade80', trb: '#60a5fa', ast: '#f472b6', game_score: '#fbbf24' };

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
    const textColor = isDark ? '#b0b0b0' : '#666666';

    playerChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: statLabels[stat] || stat,
                data: data,
                borderColor: statColors[stat] || '#4ade80',
                backgroundColor: (statColors[stat] || '#4ade80') + '20',
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => chartGames[items[0].dataIndex]?.date || '',
                        afterLabel: (item) => `vs ${chartGames[item.dataIndex]?.opponent || ''}`
                    }
                },
                annotation: {
                    annotations: {
                        avgLine: {
                            type: 'line',
                            yMin: avg,
                            yMax: avg,
                            borderColor: 'rgba(255,255,255,0.5)',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                display: true,
                                content: `Avg: ${avg.toFixed(1)}`,
                                position: 'end'
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, maxRotation: 45 }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

// Venues
function renderVenuesTable() {
    const venues = DATA.venues || [];
    const visited = venues.filter(v => v.visited).length;
    document.getElementById('arena-progress-fill').style.width = `${(visited/30)*100}%`;
    document.getElementById('arena-progress-text').textContent = `${visited}/30 Arenas Visited`;
    filterVenuesTable();
}

function filterVenuesTable() {
    const filter = document.getElementById('venues-filter').value;
    let venues = DATA.venues || [];
    if (filter === 'visited') venues = venues.filter(v => v.visited);
    else if (filter === 'unvisited') venues = venues.filter(v => !v.visited);

    const tbody = document.querySelector('#venues-table tbody');
    tbody.innerHTML = venues.map(v => `
        <tr>
            <td>${v.team}</td>
            <td>${v.name}</td>
            <td>${v.city}</td>
            <td>${v.state}</td>
            <td class="num">${v.games}</td>
            <td>${v.first_visit || '-'}</td>
            <td class="${v.visited ? 'status-visited' : 'status-not-visited'}">${v.visited ? '✓ Visited' : 'Not Yet'}</td>
        </tr>
    `).join('');
}

// Map
function initMap() {
    arenaMap = L.map('arena-map').setView([39.8, -98.5], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(arenaMap);
    (DATA.venues || []).forEach(v => {
        const color = v.visited ? '#27ae60' : '#95a5a6';
        L.circleMarker([v.lat, v.lng], { radius: 10, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.9 })
            .addTo(arenaMap)
            .bindPopup(`<strong>${v.team}</strong><br>${v.name}<br>${v.city}, ${v.state}<br><em>${v.visited ? v.games + ' games' : 'Not visited'}</em>`);
    });
}

// Constants are auto-generated at the start of this script

// Team Checklist
let currentChecklistView = 'all';

function renderTeamChecklist() {
    const checklist = DATA.teamChecklist || {};
    const teams = checklist.teams || [];
    const divisions = checklist.divisions || {};
    const conferences = checklist.conferences || {};
    const summary = checklist.summary || { teamsSeen: 0, totalTeams: 30 };

    // Update progress bar
    document.getElementById('team-progress-fill').style.width = `${(summary.teamsSeen/30)*100}%`;
    document.getElementById('team-progress-text').textContent = `${summary.teamsSeen}/30 Teams Seen`;

    showChecklistView(currentChecklistView);
}

function showChecklistView(view) {
    currentChecklistView = view;
    const container = document.getElementById('team-checklist-container');
    const checklist = DATA.teamChecklist || {};
    const teams = checklist.teams || [];
    const divisions = checklist.divisions || {};
    const conferences = checklist.conferences || {};

    // Update tab styling
    document.querySelectorAll('.checklist-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-view="${view}"]`)?.classList.add('active');

    let html = '';

    if (view === 'all') {
        // Show all teams in a single grid
        const seen = teams.filter(t => t.seen).length;
        html = `
            <div class="division-card ${seen === 30 ? 'complete' : ''}">
                <div class="division-header">
                    <h4>All NBA Teams</h4>
                    <span class="badge ${seen === 30 ? 'badge-complete' : 'badge-progress'}">${seen}/30</span>
                </div>
                <div class="team-grid">
                    ${teams.sort((a,b) => a.name.localeCompare(b.name)).map(t => `
                        <div class="team-item ${t.seen ? 'seen' : ''}">
                            <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                            <span>${getShortName(t.name)}</span>
                            ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>`;
    } else if (view === 'east' || view === 'west') {
        const conf = view === 'east' ? 'East' : 'West';
        const confData = conferences[conf] || { teamsSeen: 0, totalTeams: 15, divisions: [] };
        const divNames = view === 'east' ? ['Atlantic', 'Central', 'Southeast'] : ['Northwest', 'Pacific', 'Southwest'];

        html = `
            <div class="conference-summary">
                <div class="conference-box ${confData.teamsSeen === 15 ? 'complete' : ''}">
                    <h5>${conf}ern Conference</h5>
                    <div class="count">${confData.teamsSeen}/15</div>
                </div>
            </div>`;

        divNames.forEach(divName => {
            const div = divisions[divName] || { teams: [], teamsSeen: 0, totalTeams: 5 };
            html += `
                <div class="division-card ${div.complete ? 'complete' : ''}">
                    <div class="division-header">
                        <h4>${divName} Division</h4>
                        <span class="badge ${div.complete ? 'badge-complete' : 'badge-progress'}">${div.teamsSeen}/${div.totalTeams}</span>
                    </div>
                    <div class="team-grid">
                        ${(div.teams || []).map(t => `
                            <div class="team-item ${t.seen ? 'seen' : ''}">
                                <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                                <span>${getShortName(t.name)}</span>
                                ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        });
    } else if (view === 'divisions') {
        // Show conference summaries first
        html = `<div class="conference-summary">`;
        ['East', 'West'].forEach(conf => {
            const confData = conferences[conf] || { teamsSeen: 0, totalTeams: 15 };
            html += `
                <div class="conference-box ${confData.teamsSeen === 15 ? 'complete' : ''}">
                    <h5>${conf}ern</h5>
                    <div class="count">${confData.teamsSeen}/15</div>
                </div>`;
        });
        html += '</div>';

        // Show all divisions
        const divOrder = ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest'];
        divOrder.forEach(divName => {
            const div = divisions[divName] || { teams: [], teamsSeen: 0, totalTeams: 5, conference: '' };
            html += `
                <div class="division-card ${div.complete ? 'complete' : ''}">
                    <div class="division-header">
                        <h4>${divName} <small style="font-weight:normal;color:var(--text-muted);">(${div.conference || ''})</small></h4>
                        <span class="badge ${div.complete ? 'badge-complete' : 'badge-progress'}">${div.teamsSeen}/${div.totalTeams}</span>
                    </div>
                    <div class="team-grid">
                        ${(div.teams || []).map(t => `
                            <div class="team-item ${t.seen ? 'seen' : ''}">
                                <span class="${t.seen ? 'check' : 'not-seen'}">${t.seen ? '✓' : '○'}</span>
                                <span>${getShortName(t.name)}</span>
                                ${t.visitCount > 0 ? `<span class="visit-count">${t.visitCount}x</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>`;
        });
    }

    container.innerHTML = html;
}

// MILESTONE_CATEGORIES is auto-generated from Python constants

// Master order for displaying all milestones (grouped by category)
const MILESTONE_ORDER = [
    // Multi-stat achievements
    'quadruple_doubles', 'triple_doubles', 'near_triple_doubles', 'double_doubles', 'near_double_doubles',
    'five_by_fives', 'all_around_games',
    // Scoring (high to low)
    'seventy_point_games', 'sixty_point_games', 'fifty_point_games', 'forty_five_point_games',
    'forty_point_games', 'thirty_five_point_games', 'thirty_point_games', 'twenty_five_point_games', 'twenty_point_games',
    // Combined stats
    'twenty_twenty_games', 'thirty_ten_games', 'twenty_five_ten_games', 'twenty_ten_five_games',
    'twenty_ten_games', 'points_assists_double_double',
    // Rebounding (high to low)
    'twenty_five_rebound_games', 'twenty_rebound_games', 'eighteen_rebound_games',
    'fifteen_rebound_games', 'twelve_rebound_games', 'ten_rebound_games',
    // Assists (high to low)
    'twenty_assist_games', 'fifteen_assist_games', 'twelve_assist_games', 'ten_assist_games',
    // Three-pointers
    'ten_three_games', 'eight_three_games', 'seven_three_games', 'six_three_games', 'five_three_games', 'perfect_from_three',
    // Steals (high to low)
    'ten_steal_games', 'seven_steal_games', 'five_steal_games', 'four_steal_games',
    // Blocks (high to low)
    'ten_block_games', 'seven_block_games', 'five_block_games', 'four_block_games',
    // Efficiency
    'high_game_score', 'efficient_scoring_games', 'hot_shooting_games', 'perfect_fg_games', 'perfect_ft_games',
    // Defensive
    'defensive_monster_games', 'zero_turnover_games',
    // Plus/Minus
    'plus_25_games', 'plus_20_games', 'minus_25_games'
];

function renderMilestones() {
    filterMilestones();
}

function filterMilestones() {
    const category = document.getElementById('milestone-category').value;
    const search = document.getElementById('milestone-search').value.toLowerCase();
    const container = document.getElementById('milestones-container');
    const milestones = DATA.milestones || {};
    const descriptions = DATA.milestone_descriptions || {};

    let keysToShow = [];
    if (category === 'all') {
        // Use master order for "all" view to group related stats together
        keysToShow = MILESTONE_ORDER.filter(k => milestones[k] && milestones[k].length > 0);
        // Also include any milestones not in the master order
        Object.keys(milestones).forEach(k => {
            if (!keysToShow.includes(k) && milestones[k] && milestones[k].length > 0) {
                keysToShow.push(k);
            }
        });
    } else {
        keysToShow = (MILESTONE_CATEGORIES[category] || []).filter(k => milestones[k] && milestones[k].length > 0);
    }

    let html = '';
    keysToShow.forEach(key => {
        let data = milestones[key] || [];

        // Sort by date descending (most recent first)
        data = [...data].sort((a, b) => (b.date_yyyymmdd || '').localeCompare(a.date_yyyymmdd || ''));

        // Filter by search
        if (search) {
            data = data.filter(m => m.player?.toLowerCase().includes(search) || m.team?.toLowerCase().includes(search));
        }

        if (data.length === 0 && search) return;

        const title = descriptions[key] || key.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
        html += `<div class="milestone-card">
            <h4>${title} <span class="count">${data.length}</span></h4>`;

        if (data.length === 0) {
            html += '<p class="empty">None recorded</p>';
        } else {
            html += '<div class="table-container" style="max-height:300px;"><table><thead><tr><th>Date</th><th>Player</th><th>Team</th><th>vs</th><th>Detail</th></tr></thead><tbody>';
            data.slice(0, 50).forEach(m => {
                html += `<tr>
                    <td>${m.date || ''}</td>
                    <td><span class="player-link" onclick="showPlayerDetail('${(m.player||'').replace(/'/g, \"\\\\'\")}')">${m.player || ''}</span></td>
                    <td>${m.team || ''}</td>
                    <td>${m.opponent || ''}</td>
                    <td>${m.detail || ''}</td>
                </tr>`;
            });
            if (data.length > 50) html += `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">...and ${data.length - 50} more</td></tr>`;
            html += '</tbody></table></div>';
        }
        html += '</div>';
    });

    if (!html) {
        html = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No milestones found</p>';
    }

    container.innerHTML = html;
}

// CSV Download
function downloadCSV(type) {
    const data = type === 'players' ? filteredPlayers : null;
    if (!data || !data.length) { showToast('No data'); return; }
    const headers = playerCols;
    const csv = [headers.join(','), ...data.map(r => headers.map(h => {
        let v = r[h]; if (v == null) v = '';
        if (typeof v === 'string' && (v.includes(',') || v.includes('"'))) v = '"' + v.replace(/"/g, '""') + '"';
        return v;
    }).join(','))].join('\\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = 'nba_players.csv'; a.click();
    showToast('Download started');
}

// Init
document.addEventListener('DOMContentLoaded', function() {
    renderGamesGrid();
    populateTeamDropdown();
    filteredPlayers = DATA.players ? [...DATA.players] : [];
    renderPlayersTable();
    renderTeamChecklist();
    renderVenuesTable();
    renderMilestones();
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.querySelectorAll('.modal.active').forEach(m => closeModal(m.id));
});
    '''
