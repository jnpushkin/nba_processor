"""Tests for Basketball Reference extras scraper (PBP, shot chart, plus-minus)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from nba_processor.scrapers.br_extras_scraper import (
    parse_br_pbp,
    parse_br_shot_chart,
    parse_br_plus_minus,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def pbp_html():
    return (FIXTURES_DIR / "br_pbp_sample.html").read_text()


@pytest.fixture
def shot_chart_html():
    return (FIXTURES_DIR / "br_shot_chart_sample.html").read_text()


@pytest.fixture
def plus_minus_html():
    return (FIXTURES_DIR / "br_plus_minus_sample.html").read_text()


# --- PBP tests ---

class TestParseBrPbp:
    def test_returns_plays(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        assert result is not None
        assert 'plays' in result
        assert result['play_count'] == len(result['plays'])

    def test_play_count(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        # 1 jump ball + 5 plays + 1 end q1 + 1 start q2 + 1 play = 9
        assert result['play_count'] == 9

    def test_quarter_tracking(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        plays = result['plays']
        # First plays are Q1
        assert plays[0]['quarter'] == 1
        # Last play is Q2
        assert plays[-1]['quarter'] == 2

    def test_neutral_event(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        jump_ball = result['plays'][0]
        assert jump_ball['team_side'] is None
        assert 'Jump ball' in jump_ball['action']
        assert jump_ball['time'] == '12:00.0'

    def test_away_play(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        # J. Strawther misses 3-pt (away)
        miss = result['plays'][1]
        assert miss['team_side'] == 'away'
        assert miss['player'] == 'J. Strawther'
        assert 'misses 3-pt' in miss['action']

    def test_home_play(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        # Defensive rebound by D. Melton (home)
        reb = result['plays'][2]
        assert reb['team_side'] == 'home'
        assert reb['player'] == 'D. Melton'

    def test_scoring_play(self, pbp_html):
        result = parse_br_pbp(pbp_html)
        # M. Moody makes 2-pt layup, score 0-2
        make = result['plays'][3]
        assert make['team_side'] == 'home'
        assert make['away_score'] == 0
        assert make['home_score'] == 2
        assert make['score'] == '0-2'

    def test_returns_none_for_empty(self):
        assert parse_br_pbp('<html><body></body></html>') is None


# --- Shot chart tests ---

class TestParseBrShotChart:
    def test_returns_shots(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        assert result is not None
        assert 'shots' in result
        assert result['shot_count'] == len(result['shots'])

    def test_shot_count(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        # 3 DEN shots + 2 GSW shots
        assert result['shot_count'] == 5

    def test_made_shot(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        jokic_make = result['shots'][0]
        assert jokic_make['player'] == 'Nikola Jokic'
        assert jokic_make['team'] == 'DEN'
        assert jokic_make['made'] is True
        assert jokic_make['x'] == 233
        assert jokic_make['y'] == 58
        assert jokic_make['quarter'] == 1

    def test_missed_shot(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        murray_miss = result['shots'][1]
        assert murray_miss['player'] == 'Jamal Murray'
        assert murray_miss['made'] is False
        assert murray_miss['quarter'] == 1

    def test_team_assignment(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        teams = [s['team'] for s in result['shots']]
        assert teams.count('DEN') == 3
        assert teams.count('GSW') == 2

    def test_description_from_tip(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        assert 'made 2-pointer from 3 ft' in result['shots'][0]['description']

    def test_player_id(self, shot_chart_html):
        result = parse_br_shot_chart(shot_chart_html)
        assert result['shots'][0]['player_id'] == 'jokicni01'

    def test_returns_none_for_empty(self):
        assert parse_br_shot_chart('<html><body></body></html>') is None


# --- Plus-minus tests ---

class TestParseBrPlusMinus:
    def test_returns_teams(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        assert result is not None
        assert 'away' in result
        assert 'home' in result

    def test_away_players(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        assert len(result['away']) == 2
        assert result['away'][0]['player'] == 'Nikola Jokic'
        assert result['away'][1]['player'] == 'Jamal Murray'

    def test_home_players(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        assert len(result['home']) == 2
        assert result['home'][0]['player'] == 'Stephen Curry'
        assert result['home'][1]['player'] == 'Moses Moody'

    def test_on_off_net_values(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        jokic = result['away'][0]
        assert jokic['on'] == 12.0
        assert jokic['off'] == -3.0
        assert jokic['net'] == 15.0

    def test_negative_values(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        murray = result['away'][1]
        assert murray['on'] == -2.0
        assert murray['off'] == 5.0
        assert murray['net'] == -7.0

    def test_zero_value(self, plus_minus_html):
        result = parse_br_plus_minus(plus_minus_html)
        moody = result['home'][1]
        assert moody['off'] == 0.0

    def test_returns_none_for_empty(self):
        assert parse_br_plus_minus('<html><body></body></html>') is None
