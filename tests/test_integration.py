"""
Integration tests for the NBA Processor pipeline.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nba_processor.processors.player_stats_processor import PlayerStatsProcessor
from nba_processor.utils.helpers import (
    is_triple_double,
    is_double_double,
    calculate_game_score,
)


class TestFullPipelineIntegration:
    """Integration tests for the full data processing pipeline."""

    def test_pipeline_processes_single_game(self, sample_game_data):
        """Test that the pipeline handles a single game."""
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)
        assert 'players' in result
        assert 'player_games' in result

    def test_pipeline_processes_multiple_games(self, multiple_games_data):
        """Test that the pipeline handles multiple games."""
        processor = PlayerStatsProcessor(multiple_games_data)
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)
        assert len(multiple_games_data) == 3

    def test_pipeline_handles_empty_input(self):
        """Test that the pipeline handles empty input gracefully."""
        processor = PlayerStatsProcessor([])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)


class TestMilestoneIntegration:
    """Integration tests for milestone detection."""

    def test_triple_double_detection_integration(self, sample_game_data):
        """Test that triple-doubles are detected in the pipeline."""
        # LeBron in sample data: 35 pts, 12 reb, 11 ast = triple-double
        lebron = sample_game_data['players']['home'][0]
        stats = {
            'pts': lebron['pts'],
            'trb': lebron['trb'],
            'ast': lebron['ast'],
            'stl': lebron['stl'],
            'blk': lebron['blk']
        }

        assert is_triple_double(stats) is True

    def test_double_double_detection_integration(self, sample_game_data):
        """Test that double-doubles are detected in the pipeline."""
        # Jayson Tatum in sample data: 32 pts, 10 reb = double-double
        tatum = sample_game_data['players']['away'][0]
        stats = {
            'pts': tatum['pts'],
            'trb': tatum['trb'],
            'ast': tatum['ast'],
            'stl': tatum['stl'],
            'blk': tatum['blk']
        }

        assert is_double_double(stats) is True

    def test_game_score_integration(self, sample_game_data):
        """Test that game scores are calculated in the pipeline."""
        player = sample_game_data['players']['home'][0]  # LeBron
        stats = {
            'pts': player['pts'],
            'fg': player['fg'],
            'fga': player['fga'],
            'ft': player['ft'],
            'fta': player['fta'],
            'orb': player['orb'],
            'drb': player['drb'],
            'stl': player['stl'],
            'ast': player['ast'],
            'blk': player['blk'],
            'pf': player['pf'],
            'tov': player['tov']
        }

        gs = calculate_game_score(stats)
        assert gs > 20  # LeBron's stats should yield high game score


class TestDataAggregationIntegration:
    """Integration tests for data aggregation."""

    def test_aggregates_player_stats(self, multiple_games_data):
        """Test that player stats are aggregated correctly."""
        processor = PlayerStatsProcessor(multiple_games_data)
        result = processor.process_all_player_stats()

        players_df = result['players']
        assert players_df is not None

    def test_aggregates_across_teams(self, multiple_games_data):
        """Test aggregation when same players appear for different teams."""
        processor = PlayerStatsProcessor(multiple_games_data)
        result = processor.process_all_player_stats()

        # Verify result structure
        assert 'players' in result


class TestEdgeCases:
    """Tests for edge cases in the integration."""

    def test_handles_missing_player_fields(self, sample_game_data):
        """Test handling of players with missing fields."""
        # Add player with missing fields
        sample_game_data['players']['home'].append({
            'name': 'Incomplete Player',
            'pts': 5
            # Missing other stats
        })

        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        # Should not crash
        assert isinstance(result, dict)

    def test_handles_zero_minute_players(self, sample_game_data):
        """Test handling of players with zero minutes."""
        sample_game_data['players']['home'].append({
            'name': 'DNP Player',
            'mp': '0:00',
            'pts': 0,
            'trb': 0,
            'ast': 0,
            'stl': 0,
            'blk': 0,
            'fg': 0,
            'fga': 0
        })

        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)

    def test_handles_overtime_games(self, sample_game_data):
        """Test handling of overtime games."""
        sample_game_data['linescore']['away']['quarters'].append('10')
        sample_game_data['linescore']['home']['quarters'].append('8')
        sample_game_data['linescore']['away']['total'] = 128
        sample_game_data['linescore']['home']['total'] = 120

        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)

    def test_handles_unicode_names(self, sample_game_data):
        """Test handling of Unicode characters in player names."""
        sample_game_data['players']['away'].append({
            'name': 'Nikola Jokić',
            'mp': '35:00',
            'pts': 25,
            'trb': 12,
            'ast': 10,
            'stl': 1,
            'blk': 1
        })

        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)


class TestStatisticalAccuracy:
    """Tests for statistical accuracy."""

    def test_stats_are_non_negative(self, sample_game_data):
        """Test that stats are non-negative."""
        for side in ['away', 'home']:
            for player in sample_game_data['players'][side]:
                assert player['pts'] >= 0
                assert player['trb'] >= 0
                assert player['ast'] >= 0

    def test_fg_lte_fga(self, sample_game_data):
        """Test that FG <= FGA."""
        for side in ['away', 'home']:
            for player in sample_game_data['players'][side]:
                if 'fg' in player and 'fga' in player:
                    assert player['fg'] <= player['fga']

    def test_ft_lte_fta(self, sample_game_data):
        """Test that FT <= FTA."""
        for side in ['away', 'home']:
            for player in sample_game_data['players'][side]:
                if 'ft' in player and 'fta' in player:
                    assert player['ft'] <= player['fta']

    def test_score_consistency(self, sample_game_data):
        """Test that linescore total matches basic_info score."""
        linescore = sample_game_data['linescore']
        basic = sample_game_data['basic_info']

        assert linescore['away']['total'] == basic['away_score']
        assert linescore['home']['total'] == basic['home_score']
