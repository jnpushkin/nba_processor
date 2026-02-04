"""
Comprehensive milestone detection engine for NBA games.

Detects 40+ milestone types across scoring, rebounding, assists,
defense, shooting efficiency, and multi-category achievements.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..utils.helpers import (
    safe_int,
    safe_float,
    parse_minutes,
    calculate_game_score,
    calculate_true_shooting,
    calculate_effective_fg_pct,
    is_triple_double,
    is_double_double,
    is_quadruple_double,
    is_five_by_five,
    is_near_triple_double,
    is_near_double_double,
    is_all_around_game,
    is_hot_shooting,
    is_perfect_from_three,
    is_perfect_ft,
    is_perfect_fg,
    is_efficient_scoring,
    is_defensive_monster,
    is_zero_turnover_game,
    get_double_double_categories,
)


@dataclass
class MilestoneEntry:
    """Represents a single milestone achievement."""
    milestone_type: str
    player: str
    player_id: str
    team: str
    opponent: str
    game_id: str
    date: str
    side: str  # 'home' or 'away'
    stats: Dict[str, Any]
    detail: str = ""
    date_yyyymmdd: str = ""

    def __post_init__(self):
        # Extract YYYYMMDD from game_id if not provided (game_id format: YYYYMMDD + team)
        if not self.date_yyyymmdd and self.game_id and len(self.game_id) >= 8:
            self.date_yyyymmdd = self.game_id[:8]


@dataclass
class MilestoneResults:
    """Container for all milestone detection results."""
    # Multi-category achievements
    quadruple_doubles: List[MilestoneEntry] = field(default_factory=list)
    triple_doubles: List[MilestoneEntry] = field(default_factory=list)
    double_doubles: List[MilestoneEntry] = field(default_factory=list)
    near_triple_doubles: List[MilestoneEntry] = field(default_factory=list)
    near_double_doubles: List[MilestoneEntry] = field(default_factory=list)
    five_by_fives: List[MilestoneEntry] = field(default_factory=list)
    all_around_games: List[MilestoneEntry] = field(default_factory=list)

    # Scoring milestones
    seventy_point_games: List[MilestoneEntry] = field(default_factory=list)
    sixty_point_games: List[MilestoneEntry] = field(default_factory=list)
    fifty_point_games: List[MilestoneEntry] = field(default_factory=list)
    forty_five_point_games: List[MilestoneEntry] = field(default_factory=list)
    forty_point_games: List[MilestoneEntry] = field(default_factory=list)
    thirty_five_point_games: List[MilestoneEntry] = field(default_factory=list)
    thirty_point_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_five_point_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_point_games: List[MilestoneEntry] = field(default_factory=list)

    # Rebounding milestones
    twenty_five_rebound_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_rebound_games: List[MilestoneEntry] = field(default_factory=list)
    eighteen_rebound_games: List[MilestoneEntry] = field(default_factory=list)
    fifteen_rebound_games: List[MilestoneEntry] = field(default_factory=list)
    twelve_rebound_games: List[MilestoneEntry] = field(default_factory=list)
    ten_rebound_games: List[MilestoneEntry] = field(default_factory=list)

    # Assist milestones
    twenty_assist_games: List[MilestoneEntry] = field(default_factory=list)
    fifteen_assist_games: List[MilestoneEntry] = field(default_factory=list)
    twelve_assist_games: List[MilestoneEntry] = field(default_factory=list)
    ten_assist_games: List[MilestoneEntry] = field(default_factory=list)

    # Steal milestones
    ten_steal_games: List[MilestoneEntry] = field(default_factory=list)
    seven_steal_games: List[MilestoneEntry] = field(default_factory=list)
    five_steal_games: List[MilestoneEntry] = field(default_factory=list)
    four_steal_games: List[MilestoneEntry] = field(default_factory=list)

    # Block milestones
    ten_block_games: List[MilestoneEntry] = field(default_factory=list)
    seven_block_games: List[MilestoneEntry] = field(default_factory=list)
    five_block_games: List[MilestoneEntry] = field(default_factory=list)
    four_block_games: List[MilestoneEntry] = field(default_factory=list)

    # Three-pointer milestones
    ten_three_games: List[MilestoneEntry] = field(default_factory=list)
    eight_three_games: List[MilestoneEntry] = field(default_factory=list)
    seven_three_games: List[MilestoneEntry] = field(default_factory=list)
    six_three_games: List[MilestoneEntry] = field(default_factory=list)
    five_three_games: List[MilestoneEntry] = field(default_factory=list)
    perfect_from_three: List[MilestoneEntry] = field(default_factory=list)

    # Efficiency milestones
    hot_shooting_games: List[MilestoneEntry] = field(default_factory=list)
    perfect_ft_games: List[MilestoneEntry] = field(default_factory=list)
    perfect_fg_games: List[MilestoneEntry] = field(default_factory=list)
    efficient_scoring_games: List[MilestoneEntry] = field(default_factory=list)
    high_game_score: List[MilestoneEntry] = field(default_factory=list)

    # Combined milestones
    thirty_ten_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_five_ten_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_ten_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_ten_five_games: List[MilestoneEntry] = field(default_factory=list)
    twenty_twenty_games: List[MilestoneEntry] = field(default_factory=list)
    points_assists_double_double: List[MilestoneEntry] = field(default_factory=list)

    # Defensive milestones
    defensive_monster_games: List[MilestoneEntry] = field(default_factory=list)

    # Clean games
    zero_turnover_games: List[MilestoneEntry] = field(default_factory=list)

    # Plus/Minus milestones
    plus_25_games: List[MilestoneEntry] = field(default_factory=list)
    plus_20_games: List[MilestoneEntry] = field(default_factory=list)
    minus_25_games: List[MilestoneEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[Dict]]:
        """Convert results to dictionary format."""
        result = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name != 'to_dict':
                value = getattr(self, attr_name)
                if isinstance(value, list):
                    result[attr_name] = [
                        {
                            'milestone_type': e.milestone_type,
                            'player': e.player,
                            'player_id': e.player_id,
                            'team': e.team,
                            'opponent': e.opponent,
                            'game_id': e.game_id,
                            'date': e.date,
                            'date_yyyymmdd': e.date_yyyymmdd,
                            'side': e.side,
                            'stats': e.stats,
                            'detail': e.detail,
                        }
                        for e in value
                    ]
        return result

    def get_milestone_count(self) -> int:
        """Get total number of milestones detected."""
        count = 0
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name not in ('to_dict', 'get_milestone_count'):
                value = getattr(self, attr_name)
                if isinstance(value, list):
                    count += len(value)
        return count


class MilestoneEngine:
    """
    Engine for detecting player milestones in NBA games.

    Detects 40+ milestone types organized into categories:
    - Multi-category achievements (triple-doubles, 5x5, etc.)
    - Scoring milestones (20-70 point games)
    - Rebounding milestones (10-25 rebound games)
    - Assist milestones (10-20 assist games)
    - Steal milestones (4-10 steal games)
    - Block milestones (4-10 block games)
    - Three-pointer milestones (5-10 threes, perfect shooting)
    - Efficiency milestones (hot shooting, perfect FT/FG)
    - Combined milestones (30-10, 20-20, etc.)
    - Defensive milestones (defensive monster games)
    - Clean games (zero turnovers)
    - Plus/minus milestones (+/- 20+)
    """

    def __init__(self):
        """Initialize the milestone engine."""
        self.results = MilestoneResults()

    def process_games(self, games: List[Dict]) -> MilestoneResults:
        """Process multiple games and detect all milestones.

        Args:
            games: List of game data dictionaries

        Returns:
            MilestoneResults containing all detected milestones
        """
        self.results = MilestoneResults()

        for game in games:
            self._process_game(game)

        return self.results

    def _process_game(self, game: Dict) -> None:
        """Process a single game for milestones.

        Args:
            game: Game data dictionary
        """
        game_id = game.get('game_id', '')
        basic_info = game.get('basic_info', {})
        date = basic_info.get('date', basic_info.get('date_yyyymmdd', ''))
        home_team = basic_info.get('home_team', '')
        away_team = basic_info.get('away_team', '')

        # Get players from box_score structure (supports both 'basic' and 'players' keys)
        box_score = game.get('box_score', {})

        def get_players_for_side(side: str) -> List[Dict]:
            side_data = box_score.get(side, {})
            players = side_data.get('players', [])
            if not players:
                players = side_data.get('basic', [])
            return players

        # Process away team players
        for player in get_players_for_side('away'):
            self._check_player_milestones(
                player=player,
                team=away_team,
                opponent=home_team,
                game_id=game_id,
                date=date,
                side='away'
            )

        # Process home team players
        for player in get_players_for_side('home'):
            self._check_player_milestones(
                player=player,
                team=home_team,
                opponent=away_team,
                game_id=game_id,
                date=date,
                side='home'
            )

    def _check_player_milestones(
        self,
        player: Dict,
        team: str,
        opponent: str,
        game_id: str,
        date: str,
        side: str
    ) -> None:
        """Check all milestone types for a player.

        Args:
            player: Player stats dictionary
            team: Player's team name
            opponent: Opponent team name
            game_id: Game identifier
            date: Game date
            side: 'home' or 'away'
        """
        name = player.get('name', '')
        player_id = player.get('player_id', '')

        # Extract stats
        pts = safe_int(player.get('pts', 0))
        trb = safe_int(player.get('trb', 0))
        ast = safe_int(player.get('ast', 0))
        stl = safe_int(player.get('stl', 0))
        blk = safe_int(player.get('blk', 0))
        fg3 = safe_int(player.get('fg3', 0))
        fg3a = safe_int(player.get('fg3a', 0))
        fg = safe_int(player.get('fg', 0))
        fga = safe_int(player.get('fga', 0))
        ft = safe_int(player.get('ft', 0))
        fta = safe_int(player.get('fta', 0))
        tov = safe_int(player.get('tov', 0))
        plus_minus = safe_int(player.get('plus_minus', 0))

        mp = player.get('mp', 0)
        if isinstance(mp, str):
            mp = parse_minutes(mp)

        stats = {
            'pts': pts, 'trb': trb, 'ast': ast, 'stl': stl, 'blk': blk,
            'fg3': fg3, 'fg3a': fg3a, 'fg': fg, 'fga': fga,
            'ft': ft, 'fta': fta, 'tov': tov, 'plus_minus': plus_minus,
            'mp': mp
        }

        base_entry = {
            'player': name,
            'player_id': player_id,
            'team': team,
            'opponent': opponent,
            'game_id': game_id,
            'date': date,
            'side': side,
            'stats': stats,
        }

        # === MULTI-CATEGORY ACHIEVEMENTS ===
        if is_quadruple_double(stats):
            categories = get_double_double_categories(stats)
            self.results.quadruple_doubles.append(MilestoneEntry(
                milestone_type='quadruple_double',
                detail=f'Quadruple-double ({categories})',
                **base_entry
            ))

        if is_triple_double(stats):
            categories = get_double_double_categories(stats)
            self.results.triple_doubles.append(MilestoneEntry(
                milestone_type='triple_double',
                detail=f'Triple-double ({categories})',
                **base_entry
            ))

        if is_double_double(stats):
            categories = get_double_double_categories(stats)
            self.results.double_doubles.append(MilestoneEntry(
                milestone_type='double_double',
                detail=f'Double-double ({categories})',
                **base_entry
            ))

        if is_near_triple_double(stats):
            self.results.near_triple_doubles.append(MilestoneEntry(
                milestone_type='near_triple_double',
                detail=f'Near triple-double ({pts}/{trb}/{ast})',
                **base_entry
            ))

        if is_near_double_double(stats):
            self.results.near_double_doubles.append(MilestoneEntry(
                milestone_type='near_double_double',
                detail=f'Near double-double',
                **base_entry
            ))

        if is_five_by_five(stats):
            self.results.five_by_fives.append(MilestoneEntry(
                milestone_type='five_by_five',
                detail=f'5x5 ({pts}/{trb}/{ast}/{stl}/{blk})',
                **base_entry
            ))

        if is_all_around_game(stats):
            self.results.all_around_games.append(MilestoneEntry(
                milestone_type='all_around_game',
                detail=f'All-around ({pts}/{trb}/{ast}/{stl}/{blk})',
                **base_entry
            ))

        # === SCORING MILESTONES ===
        if pts >= 70:
            self.results.seventy_point_games.append(MilestoneEntry(
                milestone_type='seventy_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 60:
            self.results.sixty_point_games.append(MilestoneEntry(
                milestone_type='sixty_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 50:
            self.results.fifty_point_games.append(MilestoneEntry(
                milestone_type='fifty_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 45:
            self.results.forty_five_point_games.append(MilestoneEntry(
                milestone_type='forty_five_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 40:
            self.results.forty_point_games.append(MilestoneEntry(
                milestone_type='forty_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 35:
            self.results.thirty_five_point_games.append(MilestoneEntry(
                milestone_type='thirty_five_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 30:
            self.results.thirty_point_games.append(MilestoneEntry(
                milestone_type='thirty_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 25:
            self.results.twenty_five_point_games.append(MilestoneEntry(
                milestone_type='twenty_five_point_game',
                detail=f'{pts} points',
                **base_entry
            ))
        elif pts >= 20:
            self.results.twenty_point_games.append(MilestoneEntry(
                milestone_type='twenty_point_game',
                detail=f'{pts} points',
                **base_entry
            ))

        # === REBOUNDING MILESTONES ===
        if trb >= 25:
            self.results.twenty_five_rebound_games.append(MilestoneEntry(
                milestone_type='twenty_five_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))
        elif trb >= 20:
            self.results.twenty_rebound_games.append(MilestoneEntry(
                milestone_type='twenty_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))
        elif trb >= 18:
            self.results.eighteen_rebound_games.append(MilestoneEntry(
                milestone_type='eighteen_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))
        elif trb >= 15:
            self.results.fifteen_rebound_games.append(MilestoneEntry(
                milestone_type='fifteen_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))
        elif trb >= 12:
            self.results.twelve_rebound_games.append(MilestoneEntry(
                milestone_type='twelve_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))
        elif trb >= 10:
            self.results.ten_rebound_games.append(MilestoneEntry(
                milestone_type='ten_rebound_game',
                detail=f'{trb} rebounds',
                **base_entry
            ))

        # === ASSIST MILESTONES ===
        if ast >= 20:
            self.results.twenty_assist_games.append(MilestoneEntry(
                milestone_type='twenty_assist_game',
                detail=f'{ast} assists',
                **base_entry
            ))
        elif ast >= 15:
            self.results.fifteen_assist_games.append(MilestoneEntry(
                milestone_type='fifteen_assist_game',
                detail=f'{ast} assists',
                **base_entry
            ))
        elif ast >= 12:
            self.results.twelve_assist_games.append(MilestoneEntry(
                milestone_type='twelve_assist_game',
                detail=f'{ast} assists',
                **base_entry
            ))
        elif ast >= 10:
            self.results.ten_assist_games.append(MilestoneEntry(
                milestone_type='ten_assist_game',
                detail=f'{ast} assists',
                **base_entry
            ))

        # === STEAL MILESTONES ===
        if stl >= 10:
            self.results.ten_steal_games.append(MilestoneEntry(
                milestone_type='ten_steal_game',
                detail=f'{stl} steals',
                **base_entry
            ))
        elif stl >= 7:
            self.results.seven_steal_games.append(MilestoneEntry(
                milestone_type='seven_steal_game',
                detail=f'{stl} steals',
                **base_entry
            ))
        elif stl >= 5:
            self.results.five_steal_games.append(MilestoneEntry(
                milestone_type='five_steal_game',
                detail=f'{stl} steals',
                **base_entry
            ))
        elif stl >= 4:
            self.results.four_steal_games.append(MilestoneEntry(
                milestone_type='four_steal_game',
                detail=f'{stl} steals',
                **base_entry
            ))

        # === BLOCK MILESTONES ===
        if blk >= 10:
            self.results.ten_block_games.append(MilestoneEntry(
                milestone_type='ten_block_game',
                detail=f'{blk} blocks',
                **base_entry
            ))
        elif blk >= 7:
            self.results.seven_block_games.append(MilestoneEntry(
                milestone_type='seven_block_game',
                detail=f'{blk} blocks',
                **base_entry
            ))
        elif blk >= 5:
            self.results.five_block_games.append(MilestoneEntry(
                milestone_type='five_block_game',
                detail=f'{blk} blocks',
                **base_entry
            ))
        elif blk >= 4:
            self.results.four_block_games.append(MilestoneEntry(
                milestone_type='four_block_game',
                detail=f'{blk} blocks',
                **base_entry
            ))

        # === THREE-POINTER MILESTONES ===
        if fg3 >= 10:
            self.results.ten_three_games.append(MilestoneEntry(
                milestone_type='ten_three_game',
                detail=f'{fg3} three-pointers',
                **base_entry
            ))
        elif fg3 >= 8:
            self.results.eight_three_games.append(MilestoneEntry(
                milestone_type='eight_three_game',
                detail=f'{fg3} three-pointers',
                **base_entry
            ))
        elif fg3 >= 7:
            self.results.seven_three_games.append(MilestoneEntry(
                milestone_type='seven_three_game',
                detail=f'{fg3} three-pointers',
                **base_entry
            ))
        elif fg3 >= 6:
            self.results.six_three_games.append(MilestoneEntry(
                milestone_type='six_three_game',
                detail=f'{fg3} three-pointers',
                **base_entry
            ))
        elif fg3 >= 5:
            self.results.five_three_games.append(MilestoneEntry(
                milestone_type='five_three_game',
                detail=f'{fg3} three-pointers',
                **base_entry
            ))

        if is_perfect_from_three(stats):
            self.results.perfect_from_three.append(MilestoneEntry(
                milestone_type='perfect_from_three',
                detail=f'{fg3}/{fg3a} from three (100%)',
                **base_entry
            ))

        # === EFFICIENCY MILESTONES ===
        if is_hot_shooting(stats):
            fg_pct = round((fg / fga) * 100, 1) if fga > 0 else 0
            self.results.hot_shooting_games.append(MilestoneEntry(
                milestone_type='hot_shooting_game',
                detail=f'{fg}/{fga} FG ({fg_pct}%)',
                **base_entry
            ))

        if is_perfect_ft(stats):
            self.results.perfect_ft_games.append(MilestoneEntry(
                milestone_type='perfect_ft_game',
                detail=f'{ft}/{fta} FT (100%)',
                **base_entry
            ))

        if is_perfect_fg(stats):
            self.results.perfect_fg_games.append(MilestoneEntry(
                milestone_type='perfect_fg_game',
                detail=f'{fg}/{fga} FG (100%)',
                **base_entry
            ))

        if is_efficient_scoring(stats):
            ts = calculate_true_shooting(pts, fga, fta)
            ts_pct = round(ts * 100, 1) if ts else 0
            self.results.efficient_scoring_games.append(MilestoneEntry(
                milestone_type='efficient_scoring_game',
                detail=f'{pts} points on {ts_pct}% TS',
                **base_entry
            ))

        game_score = calculate_game_score(stats)
        if game_score >= 35:
            self.results.high_game_score.append(MilestoneEntry(
                milestone_type='high_game_score',
                detail=f'Game Score: {game_score}',
                **base_entry
            ))

        # === COMBINED MILESTONES ===
        if pts >= 30 and (trb >= 10 or ast >= 10):
            self.results.thirty_ten_games.append(MilestoneEntry(
                milestone_type='thirty_ten_game',
                detail=f'{pts} pts, {trb} reb, {ast} ast',
                **base_entry
            ))
        elif pts >= 25 and (trb >= 10 or ast >= 10):
            self.results.twenty_five_ten_games.append(MilestoneEntry(
                milestone_type='twenty_five_ten_game',
                detail=f'{pts} pts, {trb} reb, {ast} ast',
                **base_entry
            ))
        elif pts >= 20 and (trb >= 10 or ast >= 10):
            self.results.twenty_ten_games.append(MilestoneEntry(
                milestone_type='twenty_ten_game',
                detail=f'{pts} pts, {trb} reb, {ast} ast',
                **base_entry
            ))

        if pts >= 20 and trb >= 10 and ast >= 5:
            self.results.twenty_ten_five_games.append(MilestoneEntry(
                milestone_type='twenty_ten_five_game',
                detail=f'{pts} pts, {trb} reb, {ast} ast',
                **base_entry
            ))

        if pts >= 20 and trb >= 20:
            self.results.twenty_twenty_games.append(MilestoneEntry(
                milestone_type='twenty_twenty_game',
                detail=f'{pts} points, {trb} rebounds',
                **base_entry
            ))

        if pts >= 10 and ast >= 10 and trb < 10:
            self.results.points_assists_double_double.append(MilestoneEntry(
                milestone_type='points_assists_double_double',
                detail=f'{pts} pts, {ast} ast',
                **base_entry
            ))

        # === DEFENSIVE MILESTONES ===
        if is_defensive_monster(stats):
            self.results.defensive_monster_games.append(MilestoneEntry(
                milestone_type='defensive_monster_game',
                detail=f'{stl} steals, {blk} blocks',
                **base_entry
            ))

        # === CLEAN GAMES ===
        if is_zero_turnover_game(stats):
            self.results.zero_turnover_games.append(MilestoneEntry(
                milestone_type='zero_turnover_game',
                detail=f'0 turnovers in {mp:.0f} minutes',
                **base_entry
            ))

        # === PLUS/MINUS MILESTONES ===
        if plus_minus >= 25:
            self.results.plus_25_games.append(MilestoneEntry(
                milestone_type='plus_25_game',
                detail=f'+{plus_minus}',
                **base_entry
            ))
        elif plus_minus >= 20:
            self.results.plus_20_games.append(MilestoneEntry(
                milestone_type='plus_20_game',
                detail=f'+{plus_minus}',
                **base_entry
            ))

        if plus_minus <= -25:
            self.results.minus_25_games.append(MilestoneEntry(
                milestone_type='minus_25_game',
                detail=f'{plus_minus}',
                **base_entry
            ))

    def get_milestone_summary(self) -> Dict[str, int]:
        """Get count of each milestone type.

        Returns:
            Dictionary mapping milestone type to count
        """
        summary = {}
        for attr_name in dir(self.results):
            if not attr_name.startswith('_') and attr_name not in ('to_dict', 'get_milestone_count'):
                value = getattr(self.results, attr_name)
                if isinstance(value, list):
                    summary[attr_name] = len(value)
        return summary

    def get_player_milestones(self, player_name: str) -> List[MilestoneEntry]:
        """Get all milestones for a specific player.

        Args:
            player_name: Player name to search for

        Returns:
            List of milestone entries for the player
        """
        player_milestones = []
        player_lower = player_name.lower()

        for attr_name in dir(self.results):
            if not attr_name.startswith('_') and attr_name not in ('to_dict', 'get_milestone_count'):
                value = getattr(self.results, attr_name)
                if isinstance(value, list):
                    for entry in value:
                        if entry.player.lower() == player_lower:
                            player_milestones.append(entry)

        return player_milestones


# Milestone type descriptions for display
MILESTONE_DESCRIPTIONS = {
    # Multi-category
    'quadruple_doubles': 'Quadruple-Double (10+ in 4 categories)',
    'triple_doubles': 'Triple-Double (10+ in 3 categories)',
    'double_doubles': 'Double-Double (10+ in 2 categories)',
    'near_triple_doubles': 'Near Triple-Double (2 at 10+, 1 at 8-9)',
    'near_double_doubles': 'Near Double-Double (1 at 10+, 1 at 8-9)',
    'five_by_fives': '5x5 Game (5+ in all 5 categories)',
    'all_around_games': 'All-Around Game (5+ in 5 or 8+ in 4 categories)',

    # Scoring
    'seventy_point_games': '70+ Point Games',
    'sixty_point_games': '60+ Point Games',
    'fifty_point_games': '50+ Point Games',
    'forty_five_point_games': '45+ Point Games',
    'forty_point_games': '40+ Point Games',
    'thirty_five_point_games': '35+ Point Games',
    'thirty_point_games': '30+ Point Games',
    'twenty_five_point_games': '25+ Point Games',
    'twenty_point_games': '20+ Point Games',

    # Rebounding
    'twenty_five_rebound_games': '25+ Rebound Games',
    'twenty_rebound_games': '20+ Rebound Games',
    'eighteen_rebound_games': '18+ Rebound Games',
    'fifteen_rebound_games': '15+ Rebound Games',
    'twelve_rebound_games': '12+ Rebound Games',
    'ten_rebound_games': '10+ Rebound Games',

    # Assists
    'twenty_assist_games': '20+ Assist Games',
    'fifteen_assist_games': '15+ Assist Games',
    'twelve_assist_games': '12+ Assist Games',
    'ten_assist_games': '10+ Assist Games',

    # Steals
    'ten_steal_games': '10+ Steal Games',
    'seven_steal_games': '7+ Steal Games',
    'five_steal_games': '5+ Steal Games',
    'four_steal_games': '4+ Steal Games',

    # Blocks
    'ten_block_games': '10+ Block Games',
    'seven_block_games': '7+ Block Games',
    'five_block_games': '5+ Block Games',
    'four_block_games': '4+ Block Games',

    # Three-pointers
    'ten_three_games': '10+ Three-Pointer Games',
    'eight_three_games': '8+ Three-Pointer Games',
    'seven_three_games': '7+ Three-Pointer Games',
    'six_three_games': '6+ Three-Pointer Games',
    'five_three_games': '5+ Three-Pointer Games',
    'perfect_from_three': 'Perfect from Three (4+ attempts)',

    # Efficiency
    'hot_shooting_games': 'Hot Shooting (60%+ FG, 10+ attempts)',
    'perfect_ft_games': 'Perfect Free Throws (5+ attempts)',
    'perfect_fg_games': 'Perfect from Field (5+ attempts)',
    'efficient_scoring_games': 'Efficient Scoring (65%+ TS, 15+ pts)',
    'high_game_score': 'High Game Score (35+)',

    # Combined
    'thirty_ten_games': '30-10 Games (30+ pts, 10+ reb/ast)',
    'twenty_five_ten_games': '25-10 Games (25+ pts, 10+ reb/ast)',
    'twenty_ten_games': '20-10 Games (20+ pts, 10+ reb/ast)',
    'twenty_ten_five_games': '20-10-5 Games',
    'twenty_twenty_games': '20-20 Games (20+ pts, 20+ reb)',
    'points_assists_double_double': 'Points-Assists Double-Double',

    # Defensive
    'defensive_monster_games': 'Defensive Monster (7+ stl+blk)',

    # Clean
    'zero_turnover_games': 'Zero Turnover Games (20+ min)',

    # Plus/Minus
    'plus_25_games': '+25 Plus/Minus Games',
    'plus_20_games': '+20 Plus/Minus Games',
    'minus_25_games': '-25 Plus/Minus Games',
}
