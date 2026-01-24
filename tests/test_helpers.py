"""
Tests for the helpers module.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nba_processor.utils.helpers import (
    safe_int,
    safe_float,
    normalize_name,
    get_team_code,
    parse_minutes,
    calculate_game_score,
    is_triple_double,
    is_double_double,
    calculate_true_shooting,
    calculate_effective_fg_pct,
)


class TestSafeInt:
    """Tests for safe_int function."""

    def test_returns_int_value(self):
        """Test that integer values are returned correctly."""
        assert safe_int(42) == 42

    def test_converts_string_to_int(self):
        """Test that string values are converted to int."""
        assert safe_int('42') == 42
        assert safe_int('42.0') == 42

    def test_converts_float_to_int(self):
        """Test that float values are converted to int."""
        assert safe_int(42.7) == 42

    def test_returns_default_for_none(self):
        """Test that default is returned for None."""
        assert safe_int(None) == 0
        assert safe_int(None, 99) == 99

    def test_returns_default_for_invalid_string(self):
        """Test that default is returned for non-numeric strings."""
        assert safe_int('not a number') == 0


class TestSafeFloat:
    """Tests for safe_float function."""

    def test_returns_float_value(self):
        """Test that float values are returned correctly."""
        assert safe_float(3.14) == 3.14

    def test_converts_string_to_float(self):
        """Test that string values are converted to float."""
        assert safe_float('3.14') == 3.14

    def test_converts_int_to_float(self):
        """Test that int values are converted to float."""
        assert safe_float(42) == 42.0

    def test_returns_default_for_none(self):
        """Test that default is returned for None."""
        assert safe_float(None) == 0.0
        assert safe_float(None, 1.5) == 1.5


class TestNormalizeName:
    """Tests for normalize_name function."""

    def test_lowercases_name(self):
        """Test that names are lowercased."""
        assert normalize_name('LEBRON JAMES') == 'lebron james'

    def test_removes_suffixes(self):
        """Test that suffixes like Jr., Sr. are removed."""
        assert normalize_name('Gary Payton Jr.') == 'gary payton'
        assert normalize_name('Tim Hardaway Jr') == 'tim hardaway'
        assert normalize_name('Marcus Morris Sr.') == 'marcus morris'

    def test_removes_periods(self):
        """Test that periods are removed."""
        assert normalize_name('P.J. Tucker') == 'pj tucker'

    def test_removes_extra_whitespace(self):
        """Test that extra whitespace is removed."""
        assert normalize_name('  LeBron   James  ') == 'lebron james'

    def test_handles_empty_string(self):
        """Test that empty strings are handled."""
        assert normalize_name('') == ''

    def test_handles_none(self):
        """Test that None input returns empty string."""
        assert normalize_name(None) == ''


class TestGetTeamCode:
    """Tests for get_team_code function."""

    def test_returns_code_for_full_name(self):
        """Test that code is returned for full team name."""
        assert get_team_code('Boston Celtics') == 'BOS'
        assert get_team_code('Los Angeles Lakers') == 'LAL'

    def test_returns_code_for_alias(self):
        """Test that code is returned for team alias."""
        assert get_team_code('Celtics') == 'BOS'
        assert get_team_code('Lakers') == 'LAL'

    def test_fallback_for_unknown_team(self):
        """Test fallback behavior for unknown teams."""
        result = get_team_code('Unknown Team')
        assert result == 'UNK'  # First 3 letters


class TestParseMinutes:
    """Tests for parse_minutes function."""

    def test_parses_colon_format(self):
        """Test parsing of MM:SS format."""
        assert parse_minutes('38:12') == pytest.approx(38.2, rel=0.01)
        assert parse_minutes('40:00') == 40.0
        assert parse_minutes('12:30') == 12.5

    def test_handles_integer(self):
        """Test handling of integer input."""
        assert parse_minutes(38) == 38.0

    def test_handles_float(self):
        """Test handling of float input."""
        assert parse_minutes(38.5) == 38.5

    def test_handles_string_number(self):
        """Test handling of string number."""
        assert parse_minutes('38') == 38.0

    def test_handles_invalid_input(self):
        """Test handling of invalid input."""
        assert parse_minutes('invalid') == 0.0
        assert parse_minutes('') == 0.0


class TestCalculateGameScore:
    """Tests for calculate_game_score function."""

    def test_calculates_positive_game_score(self):
        """Test calculation of positive game score."""
        stats = {
            'pts': 25, 'fg': 9, 'fga': 18, 'ft': 4, 'fta': 5,
            'orb': 2, 'drb': 6, 'stl': 2, 'ast': 5, 'blk': 1,
            'pf': 2, 'tov': 3
        }
        gs = calculate_game_score(stats)
        assert gs > 0

    def test_calculates_negative_game_score(self):
        """Test calculation with poor performance."""
        stats = {
            'pts': 2, 'fg': 1, 'fga': 12, 'ft': 0, 'fta': 2,
            'orb': 0, 'drb': 1, 'stl': 0, 'ast': 0, 'blk': 0,
            'pf': 5, 'tov': 6
        }
        gs = calculate_game_score(stats)
        assert gs < 0

    def test_handles_empty_stats(self):
        """Test handling of empty stats dictionary."""
        gs = calculate_game_score({})
        assert gs == 0.0


class TestIsTripleDouble:
    """Tests for is_triple_double function."""

    def test_detects_triple_double(self, triple_double_stats):
        """Test detection of triple-double."""
        assert is_triple_double(triple_double_stats) is True

    def test_rejects_double_double(self, double_double_stats):
        """Test that double-double is not detected as triple-double."""
        assert is_triple_double(double_double_stats) is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        stats = {'pts': 8, 'trb': 8, 'ast': 8, 'stl': 8, 'blk': 8}
        assert is_triple_double(stats, threshold=8) is True
        assert is_triple_double(stats, threshold=10) is False

    def test_handles_empty_stats(self):
        """Test handling of empty stats."""
        assert is_triple_double({}) is False


class TestIsDoubleDouble:
    """Tests for is_double_double function."""

    def test_detects_double_double(self, double_double_stats):
        """Test detection of double-double."""
        assert is_double_double(double_double_stats) is True

    def test_rejects_single_double_digit(self):
        """Test that single double-digit category is rejected."""
        stats = {'pts': 15, 'trb': 5, 'ast': 3, 'stl': 1, 'blk': 0}
        assert is_double_double(stats) is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        stats = {'pts': 8, 'trb': 8, 'ast': 3, 'stl': 1, 'blk': 0}
        assert is_double_double(stats, threshold=8) is True


class TestCalculateTrueShooting:
    """Tests for calculate_true_shooting function."""

    def test_calculates_ts_pct(self):
        """Test calculation of true shooting percentage."""
        # 30 pts on 20 FGA and 8 FTA
        # TS% = 30 / (2 * (20 + 0.44 * 8)) = 30 / 47.04 = 0.638
        ts = calculate_true_shooting(30, 20, 8)
        assert ts == pytest.approx(0.638, rel=0.01)

    def test_handles_zero_attempts(self):
        """Test handling of zero attempts."""
        assert calculate_true_shooting(0, 0, 0) is None


class TestCalculateEffectiveFgPct:
    """Tests for calculate_effective_fg_pct function."""

    def test_calculates_efg_pct(self):
        """Test calculation of effective FG%."""
        # 10 FG, 4 3PM, 20 FGA
        # eFG% = (10 + 0.5 * 4) / 20 = 12 / 20 = 0.6
        efg = calculate_effective_fg_pct(10, 4, 20)
        assert efg == 0.6

    def test_handles_zero_attempts(self):
        """Test handling of zero attempts."""
        assert calculate_effective_fg_pct(0, 0, 0) is None
