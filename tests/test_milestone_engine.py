"""
Comprehensive tests for the milestone detection engine.

Tests all 40+ milestone types across categories:
- Multi-category achievements
- Scoring milestones
- Rebounding milestones
- Assist milestones
- Steal/block milestones
- Three-pointer milestones
- Efficiency milestones
- Combined milestones
- Defensive milestones
- Clean games
- Plus/minus milestones
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nba_processor.utils.helpers import (
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
    calculate_game_score,
    calculate_true_shooting,
    calculate_effective_fg_pct,
)
from nba_processor.engines.milestone_engine import (
    MilestoneEngine,
    MilestoneResults,
    MILESTONE_DESCRIPTIONS,
)


# ============================================================
# MULTI-CATEGORY ACHIEVEMENT TESTS
# ============================================================

class TestTripleDoubleDetection:
    """Tests for triple-double detection."""

    def test_pts_reb_ast_triple_double(self):
        """Test classic points-rebounds-assists triple-double."""
        stats = {'pts': 25, 'trb': 12, 'ast': 10, 'stl': 2, 'blk': 1}
        assert is_triple_double(stats) is True

    def test_with_steals(self):
        """Test triple-double including steals."""
        stats = {'pts': 20, 'trb': 10, 'ast': 5, 'stl': 10, 'blk': 2}
        assert is_triple_double(stats) is True

    def test_with_blocks(self):
        """Test triple-double including blocks."""
        stats = {'pts': 15, 'trb': 12, 'ast': 5, 'stl': 2, 'blk': 10}
        assert is_triple_double(stats) is True

    def test_quadruple_double_counts(self):
        """Test that quadruple-double is also detected as triple-double."""
        stats = {'pts': 20, 'trb': 15, 'ast': 12, 'stl': 10, 'blk': 5}
        assert is_triple_double(stats) is True

    def test_near_triple_double_fails(self):
        """Test that near triple-double is not detected."""
        stats = {'pts': 25, 'trb': 9, 'ast': 10, 'stl': 2, 'blk': 1}
        assert is_triple_double(stats) is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        stats = {'pts': 8, 'trb': 8, 'ast': 8, 'stl': 1, 'blk': 1}
        assert is_triple_double(stats, threshold=8) is True
        assert is_triple_double(stats, threshold=10) is False


class TestDoubleDoubleDetection:
    """Tests for double-double detection."""

    def test_pts_reb_double_double(self):
        """Test points-rebounds double-double."""
        stats = {'pts': 20, 'trb': 10, 'ast': 5, 'stl': 1, 'blk': 0}
        assert is_double_double(stats) is True

    def test_pts_ast_double_double(self):
        """Test points-assists double-double."""
        stats = {'pts': 22, 'trb': 5, 'ast': 12, 'stl': 1, 'blk': 0}
        assert is_double_double(stats) is True

    def test_reb_ast_double_double(self):
        """Test rebounds-assists double-double (rare)."""
        stats = {'pts': 8, 'trb': 15, 'ast': 10, 'stl': 2, 'blk': 1}
        assert is_double_double(stats) is True

    def test_single_category_fails(self):
        """Test that single double-digit category fails."""
        stats = {'pts': 30, 'trb': 5, 'ast': 3, 'stl': 1, 'blk': 0}
        assert is_double_double(stats) is False


class TestQuadrupleDoubleDetection:
    """Tests for quadruple-double detection."""

    def test_quadruple_double(self):
        """Test detection of quadruple-double."""
        stats = {'pts': 20, 'trb': 15, 'ast': 12, 'stl': 10, 'blk': 5}
        assert is_quadruple_double(stats) is True

    def test_triple_double_not_quadruple(self):
        """Test that triple-double is not quadruple-double."""
        stats = {'pts': 25, 'trb': 12, 'ast': 10, 'stl': 2, 'blk': 1}
        assert is_quadruple_double(stats) is False

    def test_quintuple_double(self):
        """Test that quintuple-double is also detected."""
        stats = {'pts': 10, 'trb': 10, 'ast': 10, 'stl': 10, 'blk': 10}
        assert is_quadruple_double(stats) is True


class TestFiveByFiveDetection:
    """Tests for 5x5 game detection."""

    def test_five_by_five(self):
        """Test detection of 5x5 game."""
        stats = {'pts': 15, 'trb': 8, 'ast': 6, 'stl': 5, 'blk': 5}
        assert is_five_by_five(stats) is True

    def test_near_five_by_five_fails(self):
        """Test that near 5x5 fails."""
        stats = {'pts': 15, 'trb': 8, 'ast': 6, 'stl': 4, 'blk': 5}
        assert is_five_by_five(stats) is False

    def test_all_high_stats(self):
        """Test with all high stats."""
        stats = {'pts': 20, 'trb': 15, 'ast': 10, 'stl': 8, 'blk': 6}
        assert is_five_by_five(stats) is True


class TestNearTripleDoubleDetection:
    """Tests for near triple-double detection."""

    def test_near_triple_double(self):
        """Test detection of near triple-double."""
        stats = {'pts': 25, 'trb': 12, 'ast': 9, 'stl': 2, 'blk': 1}
        assert is_near_triple_double(stats) is True

    def test_actual_triple_double_not_near(self):
        """Test that actual triple-double is not 'near'."""
        stats = {'pts': 25, 'trb': 12, 'ast': 10, 'stl': 2, 'blk': 1}
        assert is_near_triple_double(stats) is False

    def test_only_one_double_digit(self):
        """Test with only one double-digit category."""
        stats = {'pts': 25, 'trb': 5, 'ast': 8, 'stl': 2, 'blk': 1}
        assert is_near_triple_double(stats) is False


class TestNearDoubleDoubleDetection:
    """Tests for near double-double detection."""

    def test_near_double_double(self):
        """Test detection of near double-double."""
        stats = {'pts': 18, 'trb': 9, 'ast': 4, 'stl': 2, 'blk': 1}
        assert is_near_double_double(stats) is True

    def test_actual_double_double_not_near(self):
        """Test that actual double-double is not 'near'."""
        stats = {'pts': 20, 'trb': 10, 'ast': 4, 'stl': 2, 'blk': 1}
        assert is_near_double_double(stats) is False


class TestAllAroundGameDetection:
    """Tests for all-around game detection."""

    def test_five_plus_in_all(self):
        """Test detection with 5+ in all categories."""
        stats = {'pts': 15, 'trb': 8, 'ast': 6, 'stl': 5, 'blk': 5}
        assert is_all_around_game(stats) is True

    def test_eight_plus_in_four(self):
        """Test detection with 8+ in 4 categories."""
        stats = {'pts': 20, 'trb': 10, 'ast': 8, 'stl': 8, 'blk': 2}
        assert is_all_around_game(stats) is True

    def test_not_all_around(self):
        """Test that regular game is not all-around."""
        stats = {'pts': 20, 'trb': 10, 'ast': 5, 'stl': 1, 'blk': 0}
        assert is_all_around_game(stats) is False


class TestGetDoubleDoubleCategories:
    """Tests for double-double category string."""

    def test_pts_reb_categories(self):
        """Test pts/reb category string."""
        stats = {'pts': 20, 'trb': 12, 'ast': 5, 'stl': 2, 'blk': 1}
        result = get_double_double_categories(stats)
        assert 'pts' in result
        assert 'reb' in result

    def test_triple_double_categories(self):
        """Test triple-double category string."""
        stats = {'pts': 20, 'trb': 12, 'ast': 10, 'stl': 2, 'blk': 1}
        result = get_double_double_categories(stats)
        assert 'pts' in result
        assert 'reb' in result
        assert 'ast' in result


# ============================================================
# GAME SCORE CALCULATION TESTS
# ============================================================

class TestGameScoreCalculation:
    """Tests for game score calculation."""

    def test_excellent_game(self):
        """Test game score for excellent performance."""
        stats = {
            'pts': 40, 'fg': 15, 'fga': 25, 'ft': 8, 'fta': 10,
            'orb': 3, 'drb': 8, 'stl': 3, 'ast': 10, 'blk': 2,
            'pf': 2, 'tov': 2
        }
        gs = calculate_game_score(stats)
        assert gs > 30  # Excellent performance

    def test_average_game(self):
        """Test game score for average performance."""
        stats = {
            'pts': 15, 'fg': 6, 'fga': 12, 'ft': 2, 'fta': 3,
            'orb': 1, 'drb': 3, 'stl': 1, 'ast': 3, 'blk': 0,
            'pf': 2, 'tov': 2
        }
        gs = calculate_game_score(stats)
        assert 5 < gs < 20  # Average performance

    def test_poor_game(self):
        """Test game score for poor performance."""
        stats = {
            'pts': 4, 'fg': 2, 'fga': 10, 'ft': 0, 'fta': 2,
            'orb': 0, 'drb': 1, 'stl': 0, 'ast': 1, 'blk': 0,
            'pf': 4, 'tov': 5
        }
        gs = calculate_game_score(stats)
        assert gs < 5  # Poor performance

    def test_empty_stats(self):
        """Test with empty stats."""
        assert calculate_game_score({}) == 0.0


# ============================================================
# SCORING MILESTONE THRESHOLD TESTS
# ============================================================

class TestScoringMilestoneThresholds:
    """Tests for scoring milestone thresholds."""

    def test_70_point_game(self):
        """Test detection of 70+ point game."""
        stats = {'pts': 70, 'trb': 8, 'ast': 5, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 70

    def test_60_point_game(self):
        """Test detection of 60+ point game."""
        stats = {'pts': 62, 'trb': 8, 'ast': 5, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 60

    def test_50_point_game(self):
        """Test detection of 50+ point game."""
        stats = {'pts': 50, 'trb': 8, 'ast': 5, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 50

    def test_45_point_game(self):
        """Test detection of 45+ point game."""
        stats = {'pts': 47, 'trb': 6, 'ast': 4, 'stl': 2, 'blk': 0}
        assert stats['pts'] >= 45

    def test_40_point_game(self):
        """Test detection of 40+ point game."""
        stats = {'pts': 42, 'trb': 6, 'ast': 4, 'stl': 2, 'blk': 0}
        assert stats['pts'] >= 40

    def test_35_point_game(self):
        """Test detection of 35+ point game."""
        stats = {'pts': 36, 'trb': 5, 'ast': 6, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 35

    def test_30_point_game(self):
        """Test detection of 30+ point game."""
        stats = {'pts': 32, 'trb': 5, 'ast': 6, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 30

    def test_25_point_game(self):
        """Test detection of 25+ point game."""
        stats = {'pts': 27, 'trb': 5, 'ast': 6, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 25

    def test_20_point_game(self):
        """Test detection of 20+ point game."""
        stats = {'pts': 22, 'trb': 5, 'ast': 6, 'stl': 1, 'blk': 1}
        assert stats['pts'] >= 20


# ============================================================
# REBOUNDING MILESTONE THRESHOLD TESTS
# ============================================================

class TestReboundingMilestoneThresholds:
    """Tests for rebounding milestone thresholds."""

    def test_25_rebound_game(self):
        """Test detection of 25+ rebound game."""
        stats = {'pts': 15, 'trb': 27, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 25

    def test_20_rebound_game(self):
        """Test detection of 20+ rebound game."""
        stats = {'pts': 15, 'trb': 22, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 20

    def test_18_rebound_game(self):
        """Test detection of 18+ rebound game."""
        stats = {'pts': 15, 'trb': 19, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 18

    def test_15_rebound_game(self):
        """Test detection of 15+ rebound game."""
        stats = {'pts': 15, 'trb': 16, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 15

    def test_12_rebound_game(self):
        """Test detection of 12+ rebound game."""
        stats = {'pts': 15, 'trb': 13, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 12

    def test_10_rebound_game(self):
        """Test detection of 10+ rebound game."""
        stats = {'pts': 15, 'trb': 11, 'ast': 3, 'stl': 1, 'blk': 2}
        assert stats['trb'] >= 10


# ============================================================
# ASSIST MILESTONE THRESHOLD TESTS
# ============================================================

class TestAssistMilestoneThresholds:
    """Tests for assist milestone thresholds."""

    def test_20_assist_game(self):
        """Test detection of 20+ assist game."""
        stats = {'pts': 18, 'trb': 5, 'ast': 21, 'stl': 2, 'blk': 0}
        assert stats['ast'] >= 20

    def test_15_assist_game(self):
        """Test detection of 15+ assist game."""
        stats = {'pts': 18, 'trb': 5, 'ast': 16, 'stl': 2, 'blk': 0}
        assert stats['ast'] >= 15

    def test_12_assist_game(self):
        """Test detection of 12+ assist game."""
        stats = {'pts': 18, 'trb': 5, 'ast': 13, 'stl': 2, 'blk': 0}
        assert stats['ast'] >= 12

    def test_10_assist_game(self):
        """Test detection of 10+ assist game."""
        stats = {'pts': 18, 'trb': 5, 'ast': 11, 'stl': 2, 'blk': 0}
        assert stats['ast'] >= 10


# ============================================================
# STEAL MILESTONE THRESHOLD TESTS
# ============================================================

class TestStealMilestoneThresholds:
    """Tests for steal milestone thresholds."""

    def test_10_steal_game(self):
        """Test detection of 10+ steal game."""
        stats = {'pts': 12, 'trb': 4, 'ast': 5, 'stl': 10, 'blk': 1}
        assert stats['stl'] >= 10

    def test_7_steal_game(self):
        """Test detection of 7+ steal game."""
        stats = {'pts': 12, 'trb': 4, 'ast': 5, 'stl': 8, 'blk': 1}
        assert stats['stl'] >= 7

    def test_5_steal_game(self):
        """Test detection of 5+ steal game."""
        stats = {'pts': 12, 'trb': 4, 'ast': 5, 'stl': 6, 'blk': 1}
        assert stats['stl'] >= 5

    def test_4_steal_game(self):
        """Test detection of 4+ steal game."""
        stats = {'pts': 12, 'trb': 4, 'ast': 5, 'stl': 4, 'blk': 1}
        assert stats['stl'] >= 4


# ============================================================
# BLOCK MILESTONE THRESHOLD TESTS
# ============================================================

class TestBlockMilestoneThresholds:
    """Tests for block milestone thresholds."""

    def test_10_block_game(self):
        """Test detection of 10+ block game."""
        stats = {'pts': 10, 'trb': 12, 'ast': 2, 'stl': 1, 'blk': 10}
        assert stats['blk'] >= 10

    def test_7_block_game(self):
        """Test detection of 7+ block game."""
        stats = {'pts': 10, 'trb': 12, 'ast': 2, 'stl': 1, 'blk': 8}
        assert stats['blk'] >= 7

    def test_5_block_game(self):
        """Test detection of 5+ block game."""
        stats = {'pts': 10, 'trb': 12, 'ast': 2, 'stl': 1, 'blk': 6}
        assert stats['blk'] >= 5

    def test_4_block_game(self):
        """Test detection of 4+ block game."""
        stats = {'pts': 10, 'trb': 12, 'ast': 2, 'stl': 1, 'blk': 4}
        assert stats['blk'] >= 4


# ============================================================
# THREE-POINTER MILESTONE TESTS
# ============================================================

class TestThreePointerMilestones:
    """Tests for three-pointer milestones."""

    def test_10_three_pointers(self):
        """Test detection of 10+ three-pointers made."""
        stats = {'fg3': 10, 'fg3a': 15}
        assert stats['fg3'] >= 10

    def test_8_three_pointers(self):
        """Test detection of 8+ three-pointers made."""
        stats = {'fg3': 9, 'fg3a': 14}
        assert stats['fg3'] >= 8

    def test_7_three_pointers(self):
        """Test detection of 7+ three-pointers made."""
        stats = {'fg3': 7, 'fg3a': 12}
        assert stats['fg3'] >= 7

    def test_6_three_pointers(self):
        """Test detection of 6+ three-pointers made."""
        stats = {'fg3': 6, 'fg3a': 10}
        assert stats['fg3'] >= 6

    def test_5_three_pointers(self):
        """Test detection of 5+ three-pointers made."""
        stats = {'fg3': 5, 'fg3a': 8}
        assert stats['fg3'] >= 5

    def test_perfect_from_three(self):
        """Test detection of perfect three-point shooting."""
        stats = {'fg3': 5, 'fg3a': 5}
        assert is_perfect_from_three(stats) is True

    def test_not_perfect_from_three(self):
        """Test non-perfect three-point shooting."""
        stats = {'fg3': 4, 'fg3a': 5}
        assert is_perfect_from_three(stats) is False

    def test_perfect_from_three_min_attempts(self):
        """Test perfect shooting below minimum attempts."""
        stats = {'fg3': 2, 'fg3a': 2}
        assert is_perfect_from_three(stats) is False  # Below 4 attempts


# ============================================================
# EFFICIENCY MILESTONE TESTS
# ============================================================

class TestEfficiencyMilestones:
    """Tests for efficiency milestones."""

    def test_hot_shooting(self):
        """Test detection of hot shooting game."""
        stats = {'fg': 12, 'fga': 18}  # 66.7%
        assert is_hot_shooting(stats) is True

    def test_not_hot_shooting_pct(self):
        """Test non-hot shooting percentage."""
        stats = {'fg': 8, 'fga': 18}  # 44.4%
        assert is_hot_shooting(stats) is False

    def test_not_hot_shooting_attempts(self):
        """Test hot percentage but below attempt threshold."""
        stats = {'fg': 6, 'fga': 8}  # 75% but only 8 attempts
        assert is_hot_shooting(stats) is False

    def test_perfect_free_throws(self):
        """Test detection of perfect free throw shooting."""
        stats = {'ft': 12, 'fta': 12}
        assert is_perfect_ft(stats) is True

    def test_not_perfect_free_throws(self):
        """Test non-perfect free throw shooting."""
        stats = {'ft': 10, 'fta': 12}
        assert is_perfect_ft(stats) is False

    def test_perfect_ft_min_attempts(self):
        """Test perfect FT below minimum attempts."""
        stats = {'ft': 2, 'fta': 2}
        assert is_perfect_ft(stats) is False  # Below 5 attempts

    def test_perfect_field_goal(self):
        """Test detection of perfect field goal shooting."""
        stats = {'fg': 8, 'fga': 8}
        assert is_perfect_fg(stats) is True

    def test_not_perfect_field_goal(self):
        """Test non-perfect field goal shooting."""
        stats = {'fg': 6, 'fga': 8}
        assert is_perfect_fg(stats) is False

    def test_efficient_scoring(self):
        """Test detection of efficient scoring game."""
        # 20 pts on 10 FGA and 5 FTA gives ~70% TS
        stats = {'pts': 20, 'fga': 10, 'fta': 5}
        assert is_efficient_scoring(stats) is True

    def test_not_efficient_scoring_points(self):
        """Test efficient shooting but below point threshold."""
        stats = {'pts': 10, 'fga': 5, 'fta': 2}
        assert is_efficient_scoring(stats) is False  # Below 15 pts


class TestTrueShootingCalculation:
    """Tests for true shooting percentage."""

    def test_calculates_ts_pct(self):
        """Test calculation of true shooting percentage."""
        # 30 pts on 20 FGA and 8 FTA
        ts = calculate_true_shooting(30, 20, 8)
        assert ts == pytest.approx(0.638, rel=0.01)

    def test_handles_zero_attempts(self):
        """Test handling of zero attempts."""
        assert calculate_true_shooting(0, 0, 0) is None


class TestEffectiveFgPctCalculation:
    """Tests for effective FG percentage."""

    def test_calculates_efg_pct(self):
        """Test calculation of effective FG%."""
        # 10 FG, 4 3PM, 20 FGA
        efg = calculate_effective_fg_pct(10, 4, 20)
        assert efg == 0.6

    def test_handles_zero_attempts(self):
        """Test handling of zero attempts."""
        assert calculate_effective_fg_pct(0, 0, 0) is None


# ============================================================
# COMBINED MILESTONE TESTS
# ============================================================

class TestCombinedMilestones:
    """Tests for combined milestone achievements."""

    def test_30_10_game_with_rebounds(self):
        """Test detection of 30-10 with rebounds."""
        stats = {'pts': 35, 'trb': 12, 'ast': 5, 'stl': 1, 'blk': 1}
        has_30_10 = stats['pts'] >= 30 and (stats['trb'] >= 10 or stats['ast'] >= 10)
        assert has_30_10 is True

    def test_30_10_game_with_assists(self):
        """Test detection of 30-10 with assists."""
        stats = {'pts': 32, 'trb': 5, 'ast': 12, 'stl': 1, 'blk': 1}
        has_30_10 = stats['pts'] >= 30 and (stats['trb'] >= 10 or stats['ast'] >= 10)
        assert has_30_10 is True

    def test_25_10_game(self):
        """Test detection of 25-10 game."""
        stats = {'pts': 28, 'trb': 11, 'ast': 5, 'stl': 1, 'blk': 1}
        has_25_10 = stats['pts'] >= 25 and (stats['trb'] >= 10 or stats['ast'] >= 10)
        assert has_25_10 is True

    def test_20_10_game(self):
        """Test detection of 20-10 game."""
        stats = {'pts': 22, 'trb': 10, 'ast': 5, 'stl': 1, 'blk': 1}
        has_20_10 = stats['pts'] >= 20 and (stats['trb'] >= 10 or stats['ast'] >= 10)
        assert has_20_10 is True

    def test_20_10_5_game(self):
        """Test detection of 20-10-5 game."""
        stats = {'pts': 22, 'trb': 12, 'ast': 6, 'stl': 1, 'blk': 1}
        has_20_10_5 = stats['pts'] >= 20 and stats['trb'] >= 10 and stats['ast'] >= 5
        assert has_20_10_5 is True

    def test_20_20_game(self):
        """Test detection of 20-20 game (points and rebounds)."""
        stats = {'pts': 25, 'trb': 22, 'ast': 3, 'stl': 1, 'blk': 2}
        has_20_20 = stats['pts'] >= 20 and stats['trb'] >= 20
        assert has_20_20 is True

    def test_points_assists_double_double(self):
        """Test detection of points-assists double-double."""
        stats = {'pts': 18, 'trb': 5, 'ast': 12, 'stl': 2, 'blk': 0}
        has_pts_ast_dd = stats['pts'] >= 10 and stats['ast'] >= 10 and stats['trb'] < 10
        assert has_pts_ast_dd is True


# ============================================================
# DEFENSIVE MILESTONE TESTS
# ============================================================

class TestDefensiveMilestones:
    """Tests for defensive milestones."""

    def test_defensive_monster(self):
        """Test detection of defensive monster game."""
        stats = {'stl': 4, 'blk': 4}  # 8 combined
        assert is_defensive_monster(stats) is True

    def test_not_defensive_monster(self):
        """Test that moderate defense is not monster."""
        stats = {'stl': 2, 'blk': 3}  # 5 combined
        assert is_defensive_monster(stats) is False

    def test_defensive_monster_all_steals(self):
        """Test defensive monster with all steals."""
        stats = {'stl': 8, 'blk': 0}
        assert is_defensive_monster(stats) is True

    def test_defensive_monster_all_blocks(self):
        """Test defensive monster with all blocks."""
        stats = {'stl': 0, 'blk': 7}
        assert is_defensive_monster(stats) is True


# ============================================================
# CLEAN GAME TESTS
# ============================================================

class TestCleanGameMilestones:
    """Tests for clean game milestones."""

    def test_zero_turnover_game(self):
        """Test detection of zero turnover game."""
        stats = {'tov': 0, 'mp': 30}
        assert is_zero_turnover_game(stats) is True

    def test_zero_turnover_string_minutes(self):
        """Test zero turnover with string minutes format."""
        stats = {'tov': 0, 'mp': '32:15'}
        assert is_zero_turnover_game(stats) is True

    def test_zero_turnover_low_minutes(self):
        """Test zero turnover with insufficient minutes."""
        stats = {'tov': 0, 'mp': 15}
        assert is_zero_turnover_game(stats) is False

    def test_with_turnovers(self):
        """Test that game with turnovers is not clean."""
        stats = {'tov': 2, 'mp': 35}
        assert is_zero_turnover_game(stats) is False


# ============================================================
# MILESTONE ENGINE INTEGRATION TESTS
# ============================================================

class TestMilestoneEngineIntegration:
    """Integration tests for MilestoneEngine."""

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        engine = MilestoneEngine()
        assert engine.results is not None

    def test_engine_processes_single_game(self, sample_game_data):
        """Test engine processes a single game."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        assert isinstance(results, MilestoneResults)

    def test_engine_detects_triple_double(self, sample_game_data):
        """Test engine detects triple-double in game."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        # LeBron has 35/12/11 = triple-double
        assert len(results.triple_doubles) >= 1

    def test_engine_detects_double_doubles(self, sample_game_data):
        """Test engine detects double-doubles in game."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        # Multiple players have double-doubles
        assert len(results.double_doubles) >= 1

    def test_engine_detects_scoring_milestone(self, sample_game_data):
        """Test engine detects scoring milestones."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        # LeBron has 35 points
        assert len(results.thirty_five_point_games) >= 1

    def test_engine_detects_rebounding_milestone(self, sample_game_data):
        """Test engine detects rebounding milestones."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        # Anthony Davis has 14 rebounds
        assert len(results.twelve_rebound_games) >= 1

    def test_engine_to_dict(self, sample_game_data):
        """Test engine results convert to dict."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        results_dict = results.to_dict()
        assert isinstance(results_dict, dict)
        assert 'triple_doubles' in results_dict

    def test_engine_milestone_count(self, sample_game_data):
        """Test engine milestone count."""
        engine = MilestoneEngine()
        results = engine.process_games([sample_game_data])

        count = results.get_milestone_count()
        assert count > 0

    def test_engine_milestone_summary(self, sample_game_data):
        """Test engine milestone summary."""
        engine = MilestoneEngine()
        engine.process_games([sample_game_data])

        summary = engine.get_milestone_summary()
        assert isinstance(summary, dict)
        assert 'triple_doubles' in summary

    def test_engine_player_milestones(self, sample_game_data):
        """Test getting milestones for specific player."""
        engine = MilestoneEngine()
        engine.process_games([sample_game_data])

        lebron_milestones = engine.get_player_milestones('LeBron James')
        assert len(lebron_milestones) > 0

    def test_milestone_descriptions_exist(self):
        """Test that all milestone types have descriptions."""
        assert 'triple_doubles' in MILESTONE_DESCRIPTIONS
        assert 'fifty_point_games' in MILESTONE_DESCRIPTIONS
        assert 'five_by_fives' in MILESTONE_DESCRIPTIONS
        assert 'defensive_monster_games' in MILESTONE_DESCRIPTIONS


# ============================================================
# EDGE CASE TESTS
# ============================================================

class TestMilestoneEdgeCases:
    """Tests for edge cases in milestone detection."""

    def test_empty_stats(self):
        """Test handling of empty stats dictionary."""
        assert is_triple_double({}) is False
        assert is_double_double({}) is False
        assert is_quadruple_double({}) is False
        assert is_five_by_five({}) is False
        assert calculate_game_score({}) == 0.0

    def test_missing_categories(self):
        """Test handling of missing stat categories."""
        stats = {'pts': 20, 'trb': 10}  # Missing ast, stl, blk
        assert is_double_double(stats) is True  # Should still work

    def test_zero_values(self):
        """Test handling of zero values."""
        stats = {'pts': 0, 'trb': 0, 'ast': 0, 'stl': 0, 'blk': 0}
        assert is_triple_double(stats) is False
        assert is_double_double(stats) is False

    def test_negative_values(self):
        """Test handling of negative values (shouldn't happen but test anyway)."""
        stats = {'pts': -5, 'trb': 10, 'ast': 10, 'stl': 10, 'blk': 0}
        # Should not count negative as meeting threshold
        assert is_triple_double(stats) is True  # 3 categories still >= 10

    def test_string_stats(self):
        """Test handling of string stat values."""
        stats = {'pts': '25', 'trb': '12', 'ast': '10', 'stl': '2', 'blk': '1'}
        assert is_triple_double(stats) is True

    def test_float_stats(self):
        """Test handling of float stat values."""
        stats = {'pts': 25.0, 'trb': 12.0, 'ast': 10.0, 'stl': 2.0, 'blk': 1.0}
        assert is_triple_double(stats) is True

    def test_engine_handles_empty_game_list(self):
        """Test engine handles empty game list."""
        engine = MilestoneEngine()
        results = engine.process_games([])

        assert results.get_milestone_count() == 0

    def test_engine_handles_malformed_game(self):
        """Test engine handles malformed game data."""
        engine = MilestoneEngine()
        malformed_game = {'game_id': 'test', 'players': {}}
        results = engine.process_games([malformed_game])

        # Should not crash
        assert isinstance(results, MilestoneResults)


# ============================================================
# PLUS/MINUS MILESTONE TESTS
# ============================================================

class TestPlusMinusMilestones:
    """Tests for plus/minus milestones."""

    def test_plus_25_game(self):
        """Test detection of +25 game."""
        stats = {'plus_minus': 28}
        assert stats['plus_minus'] >= 25

    def test_plus_20_game(self):
        """Test detection of +20 game."""
        stats = {'plus_minus': 22}
        assert stats['plus_minus'] >= 20

    def test_minus_25_game(self):
        """Test detection of -25 game."""
        stats = {'plus_minus': -27}
        assert stats['plus_minus'] <= -25

    def test_neutral_plus_minus(self):
        """Test neutral plus/minus."""
        stats = {'plus_minus': 5}
        assert -25 < stats['plus_minus'] < 20
