"""
Pytest configuration and shared fixtures for NBA Processor tests.
"""
import pytest
import sys
from pathlib import Path

# Add grandparent directory to path so 'from nba_processor.' finds the root package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def sample_game_data():
    """Provide a minimal valid game data structure for testing."""
    return {
        "game_id": "202401150LAL",
        "basic_info": {
            "away_team": "Boston Celtics",
            "home_team": "Los Angeles Lakers",
            "away_team_code": "BOS",
            "home_team_code": "LAL",
            "away_score": 118,
            "home_score": 112,
            "date": "January 15, 2024",
            "date_yyyymmdd": "20240115",
            "venue": "Crypto.com Arena",
            "attendance": "18997"
        },
        "box_score": {
            "away": {"players": [
                {
                    "name": "Jayson Tatum",
                    "player_id": "tatumja01",
                    "starter": True,
                    "mp": "38:12",
                    "pts": 32,
                    "trb": 10,
                    "ast": 5,
                    "stl": 2,
                    "blk": 1,
                    "fg": 11,
                    "fga": 22,
                    "fg3": 4,
                    "fg3a": 10,
                    "ft": 6,
                    "fta": 7,
                    "orb": 2,
                    "drb": 8,
                    "tov": 3,
                    "pf": 2,
                    "plus_minus": 8
                },
                {
                    "name": "Jaylen Brown",
                    "player_id": "brownja02",
                    "starter": True,
                    "mp": "36:45",
                    "pts": 28,
                    "trb": 6,
                    "ast": 4,
                    "stl": 1,
                    "blk": 0,
                    "fg": 10,
                    "fga": 20,
                    "fg3": 3,
                    "fg3a": 8,
                    "ft": 5,
                    "fta": 6,
                    "orb": 1,
                    "drb": 5,
                    "tov": 2,
                    "pf": 3,
                    "plus_minus": 6
                }
            ]},
            "home": {"players": [
                {
                    "name": "LeBron James",
                    "player_id": "jamesle01",
                    "starter": True,
                    "mp": "40:00",
                    "pts": 35,
                    "trb": 12,
                    "ast": 11,
                    "stl": 2,
                    "blk": 1,
                    "fg": 13,
                    "fga": 24,
                    "fg3": 3,
                    "fg3a": 7,
                    "ft": 6,
                    "fta": 8,
                    "orb": 3,
                    "drb": 9,
                    "tov": 4,
                    "pf": 2,
                    "plus_minus": -3
                },
                {
                    "name": "Anthony Davis",
                    "player_id": "davisan01",
                    "starter": True,
                    "mp": "38:30",
                    "pts": 25,
                    "trb": 14,
                    "ast": 3,
                    "stl": 1,
                    "blk": 4,
                    "fg": 10,
                    "fga": 18,
                    "fg3": 0,
                    "fg3a": 2,
                    "ft": 5,
                    "fta": 7,
                    "orb": 4,
                    "drb": 10,
                    "tov": 2,
                    "pf": 3,
                    "plus_minus": -5
                }
            ]}
        },
        "players": {
            "away": [
                {
                    "name": "Jayson Tatum",
                    "player_id": "tatumja01",
                    "starter": True,
                    "mp": "38:12",
                    "pts": 32,
                    "trb": 10,
                    "ast": 5,
                    "stl": 2,
                    "blk": 1,
                    "fg": 11,
                    "fga": 22,
                    "fg3": 4,
                    "fg3a": 10,
                    "ft": 6,
                    "fta": 7,
                    "orb": 2,
                    "drb": 8,
                    "tov": 3,
                    "pf": 2,
                    "plus_minus": 8
                },
                {
                    "name": "Jaylen Brown",
                    "player_id": "brownja02",
                    "starter": True,
                    "mp": "36:45",
                    "pts": 28,
                    "trb": 6,
                    "ast": 4,
                    "stl": 1,
                    "blk": 0,
                    "fg": 10,
                    "fga": 20,
                    "fg3": 3,
                    "fg3a": 8,
                    "ft": 5,
                    "fta": 6,
                    "orb": 1,
                    "drb": 5,
                    "tov": 2,
                    "pf": 3,
                    "plus_minus": 6
                }
            ],
            "home": [
                {
                    "name": "LeBron James",
                    "player_id": "jamesle01",
                    "starter": True,
                    "mp": "40:00",
                    "pts": 35,
                    "trb": 12,
                    "ast": 11,
                    "stl": 2,
                    "blk": 1,
                    "fg": 13,
                    "fga": 24,
                    "fg3": 3,
                    "fg3a": 7,
                    "ft": 6,
                    "fta": 8,
                    "orb": 3,
                    "drb": 9,
                    "tov": 4,
                    "pf": 2,
                    "plus_minus": -3
                },
                {
                    "name": "Anthony Davis",
                    "player_id": "davisan01",
                    "starter": True,
                    "mp": "38:30",
                    "pts": 25,
                    "trb": 14,
                    "ast": 3,
                    "stl": 1,
                    "blk": 4,
                    "fg": 10,
                    "fga": 18,
                    "fg3": 0,
                    "fg3a": 2,
                    "ft": 5,
                    "fta": 7,
                    "orb": 4,
                    "drb": 10,
                    "tov": 2,
                    "pf": 3,
                    "plus_minus": -5
                }
            ]
        },
        "linescore": {
            "away": {"quarters": ["28", "32", "30", "28"], "total": 118},
            "home": {"quarters": ["30", "25", "32", "25"], "total": 112}
        }
    }


@pytest.fixture
def multiple_games_data(sample_game_data):
    """Provide multiple game data entries for aggregation tests."""
    import copy

    game1 = copy.deepcopy(sample_game_data)

    game2 = copy.deepcopy(sample_game_data)
    game2["game_id"] = "202401170BOS"
    game2["basic_info"]["date_yyyymmdd"] = "20240117"
    game2["basic_info"]["away_team"] = "Los Angeles Lakers"
    game2["basic_info"]["home_team"] = "Boston Celtics"
    game2["basic_info"]["away_score"] = 105
    game2["basic_info"]["home_score"] = 120

    game3 = copy.deepcopy(sample_game_data)
    game3["game_id"] = "202401200NYK"
    game3["basic_info"]["date_yyyymmdd"] = "20240120"
    game3["basic_info"]["home_team"] = "New York Knicks"
    game3["basic_info"]["away_score"] = 110
    game3["basic_info"]["home_score"] = 108

    return [game1, game2, game3]


@pytest.fixture
def triple_double_stats():
    """Provide stats that constitute a triple-double."""
    return {
        "pts": 25,
        "trb": 12,
        "ast": 10,
        "stl": 3,
        "blk": 2
    }


@pytest.fixture
def double_double_stats():
    """Provide stats that constitute a double-double."""
    return {
        "pts": 20,
        "trb": 12,
        "ast": 5,
        "stl": 2,
        "blk": 1
    }


@pytest.fixture
def high_scoring_stats():
    """Provide stats for a high-scoring game."""
    return {
        "pts": 50,
        "trb": 8,
        "ast": 6,
        "stl": 1,
        "blk": 0,
        "fg": 18,
        "fga": 32,
        "fg3": 5,
        "fg3a": 12,
        "ft": 9,
        "fta": 10
    }


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide a temporary cache directory for testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
