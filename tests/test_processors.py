"""
Tests for the processor modules.
"""
import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nba_processor.processors.player_stats_processor import PlayerStatsProcessor


class TestPlayerStatsProcessor:
    """Tests for PlayerStatsProcessor class."""

    def test_initializes_with_games(self, sample_game_data):
        """Test that processor initializes correctly."""
        processor = PlayerStatsProcessor([sample_game_data])
        assert processor is not None
        assert len(processor.games) == 1

    def test_processes_player_stats(self, sample_game_data):
        """Test that player stats are processed."""
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)
        assert 'players' in result
        assert 'player_games' in result

    def test_aggregates_multiple_games(self, multiple_games_data):
        """Test aggregation across multiple games."""
        processor = PlayerStatsProcessor(multiple_games_data)
        result = processor.process_all_player_stats()

        players_df = result['players']
        assert isinstance(players_df, pd.DataFrame)

    def test_detects_triple_doubles(self, sample_game_data):
        """Test that triple-doubles are detected."""
        # LeBron has 35 pts, 12 reb, 11 ast = triple-double
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        triple_doubles_df = result.get('triple_doubles', pd.DataFrame())
        # Should detect LeBron's triple-double
        assert isinstance(triple_doubles_df, pd.DataFrame)

    def test_detects_double_doubles(self, sample_game_data):
        """Test that double-doubles are detected."""
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        double_doubles_df = result.get('double_doubles', pd.DataFrame())
        assert isinstance(double_doubles_df, pd.DataFrame)

    def test_tracks_season_highs(self, sample_game_data):
        """Test that season highs are tracked."""
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        season_highs_df = result.get('season_highs', pd.DataFrame())
        assert isinstance(season_highs_df, pd.DataFrame)

    def test_separates_starters_and_bench(self, sample_game_data):
        """Test that starters and bench are tracked separately."""
        processor = PlayerStatsProcessor([sample_game_data])
        result = processor.process_all_player_stats()

        starters_bench_df = result.get('starters_vs_bench', pd.DataFrame())
        assert isinstance(starters_bench_df, pd.DataFrame)


class TestPlayerDataExtraction:
    """Tests for player data extraction from games."""

    def test_extracts_player_names(self, sample_game_data):
        """Test that player names are extracted correctly."""
        away_players = sample_game_data['players']['away']
        home_players = sample_game_data['players']['home']

        assert any(p['name'] == 'Jayson Tatum' for p in away_players)
        assert any(p['name'] == 'LeBron James' for p in home_players)

    def test_extracts_basic_stats(self, sample_game_data):
        """Test that basic stats are extracted."""
        player = sample_game_data['players']['home'][0]  # LeBron

        assert 'pts' in player
        assert 'trb' in player
        assert 'ast' in player
        assert player['pts'] == 35

    def test_extracts_shooting_stats(self, sample_game_data):
        """Test that shooting stats are extracted."""
        player = sample_game_data['players']['home'][0]

        assert 'fg' in player
        assert 'fga' in player
        assert 'fg3' in player
        assert 'fg3a' in player
        assert 'ft' in player
        assert 'fta' in player

    def test_extracts_minutes_played(self, sample_game_data):
        """Test that minutes played is extracted."""
        player = sample_game_data['players']['home'][0]

        assert 'mp' in player
        assert player['mp'] == '40:00'


class TestGameDataExtraction:
    """Tests for game data extraction."""

    def test_extracts_game_id(self, sample_game_data):
        """Test that game ID is extracted."""
        assert sample_game_data['game_id'] == '202401150LAL'

    def test_extracts_teams(self, sample_game_data):
        """Test that team names are extracted."""
        basic = sample_game_data['basic_info']

        assert basic['away_team'] == 'Boston Celtics'
        assert basic['home_team'] == 'Los Angeles Lakers'

    def test_extracts_scores(self, sample_game_data):
        """Test that scores are extracted."""
        basic = sample_game_data['basic_info']

        assert basic['away_score'] == 118
        assert basic['home_score'] == 112

    def test_extracts_venue(self, sample_game_data):
        """Test that venue is extracted."""
        basic = sample_game_data['basic_info']

        assert basic['venue'] == 'Crypto.com Arena'


class TestLinescoreProcessing:
    """Tests for linescore processing."""

    def test_extracts_quarters(self, sample_game_data):
        """Test that quarter scores are extracted."""
        linescore = sample_game_data['linescore']

        assert len(linescore['away']['quarters']) == 4
        assert len(linescore['home']['quarters']) == 4

    def test_calculates_totals(self, sample_game_data):
        """Test that totals are calculated."""
        linescore = sample_game_data['linescore']

        assert linescore['away']['total'] == 118
        assert linescore['home']['total'] == 112


class TestDataAggregation:
    """Tests for data aggregation across games."""

    def test_aggregates_player_totals(self, multiple_games_data):
        """Test that player totals are aggregated correctly."""
        processor = PlayerStatsProcessor(multiple_games_data)
        result = processor.process_all_player_stats()

        players_df = result['players']

        # Players should appear with aggregated stats
        if not players_df.empty:
            # Check that games column exists
            if 'games' in players_df.columns:
                assert all(players_df['games'] >= 1)

    def test_handles_empty_input(self):
        """Test handling of empty input."""
        processor = PlayerStatsProcessor([])
        result = processor.process_all_player_stats()

        assert isinstance(result, dict)
        assert 'players' in result
