# Contributing & Data Maintenance Guide

This document explains how to update the NBA Processor when team or arena information changes.

## Reference Data Locations

| Data Type | File Location |
|-----------|---------------|
| Team codes & names | `nba_processor/utils/constants.py` → `NBA_TEAMS` |
| Team aliases | `nba_processor/utils/constants.py` → `TEAM_ALIASES` |
| Arena data | `nba_processor/utils/constants.py` → `NBA_ARENAS` |
| Stat columns | `nba_processor/utils/constants.py` → `BASIC_STATS`, `ADVANCED_STATS` |
| Date formats | `nba_processor/utils/constants.py` → `DATE_FORMATS` |

## Common Update Scenarios

### 1. Team Relocates

**Example:** If a team moves to a new city

**Step 1:** Update team info in `constants.py`:

```python
NBA_TEAMS = {
    # Update team entry with new name
    'New City Team Name': {
        'code': 'NTC',  # Update code if needed
        'conference': 'East/West',
        'division': 'Division Name'
    },
    ...
}
```

**Step 2:** Add aliases for old team name:

```python
TEAM_ALIASES = {
    'Old City Team Name': 'New City Team Name',
    'Old Nickname': 'New City Team Name',
    ...
}
```

**Step 3:** Update arena information.

### 2. New Arena Opens

Edit `constants.py` → `NBA_ARENAS`:

```python
NBA_ARENAS = {
    'Team Name': {
        'name': 'New Arena Name',
        'city': 'City',
        'state': 'ST',
        'lat': 00.0000,
        'lng': -00.0000,
        'capacity': 20000,
        'opened': 2025
    },
    ...
}
```

### 3. Division Realignment

If the NBA realigns divisions:

```python
NBA_TEAMS = {
    'Team Name': {
        'code': 'TM',
        'conference': 'East/West',
        'division': 'New Division Name'  # Update division
    },
    ...
}
```

### 4. Adding New Stat Columns

To track additional statistics:

**Step 1:** Add to `BASIC_STATS` or `ADVANCED_STATS`:

```python
BASIC_STATS = [
    ...existing stats...,
    'new_stat',  # Add new stat abbreviation
]
```

**Step 2:** Update parsers to extract the new stat from box scores.

**Step 3:** Update processors to aggregate the new stat.

## Team Code Reference

### Eastern Conference

| Team | Code | Division |
|------|------|----------|
| Atlanta Hawks | ATL | Southeast |
| Boston Celtics | BOS | Atlantic |
| Brooklyn Nets | BKN | Atlantic |
| Charlotte Hornets | CHA | Southeast |
| Chicago Bulls | CHI | Central |
| Cleveland Cavaliers | CLE | Central |
| Detroit Pistons | DET | Central |
| Indiana Pacers | IND | Central |
| Miami Heat | MIA | Southeast |
| Milwaukee Bucks | MIL | Central |
| New York Knicks | NYK | Atlantic |
| Orlando Magic | ORL | Southeast |
| Philadelphia 76ers | PHI | Atlantic |
| Toronto Raptors | TOR | Atlantic |
| Washington Wizards | WAS | Southeast |

### Western Conference

| Team | Code | Division |
|------|------|----------|
| Dallas Mavericks | DAL | Southwest |
| Denver Nuggets | DEN | Northwest |
| Golden State Warriors | GSW | Pacific |
| Houston Rockets | HOU | Southwest |
| Los Angeles Clippers | LAC | Pacific |
| Los Angeles Lakers | LAL | Pacific |
| Memphis Grizzlies | MEM | Southwest |
| Minnesota Timberwolves | MIN | Northwest |
| New Orleans Pelicans | NOP | Southwest |
| Oklahoma City Thunder | OKC | Northwest |
| Phoenix Suns | PHX | Pacific |
| Portland Trail Blazers | POR | Northwest |
| Sacramento Kings | SAC | Pacific |
| San Antonio Spurs | SAS | Southwest |
| Utah Jazz | UTA | Northwest |

## Milestone Detection

The processor detects various statistical achievements. To add new milestones:

### Current Milestones

- **Triple-doubles:** 10+ in 3 of 5 categories (PTS, REB, AST, STL, BLK)
- **Double-doubles:** 10+ in 2 of 5 categories

### Adding New Milestone Types

Edit `nba_processor/utils/helpers.py`:

```python
def is_new_milestone(stats: dict, threshold: int = X) -> bool:
    """Check for new milestone type."""
    # Add detection logic
    return condition
```

Then update the processor to track the new milestone.

## Advanced Stats Calculations

### Game Score (John Hollinger)

```
GmSc = PTS + 0.4*FG - 0.7*FGA - 0.4*(FTA-FT) + 0.7*ORB + 0.3*DRB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV
```

### True Shooting %

```
TS% = PTS / (2 * (FGA + 0.44 * FTA))
```

### Effective Field Goal %

```
eFG% = (FG + 0.5 * 3PM) / FGA
```

## Cache Management

**Clear all cache:**
```bash
rm -rf cache/*.json
```

**Force re-parse specific game:**
```bash
rm cache/game_id.json
python3 -m nba_processor path/to/game.html
```

## After Making Changes

1. **Clear cache** to regenerate data:
   ```bash
   rm -rf cache/*.json
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Regenerate outputs**:
   ```bash
   python3 -m nba_processor --from-cache-only
   ```

4. **Verify changes** in the generated Excel and HTML files.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_helpers.py -v

# Run with coverage
pytest tests/ --cov=nba_processor
```

## Type Checking

```bash
# Run mypy
mypy nba_processor/

# Run on specific module
mypy nba_processor/utils/helpers.py
```

## Historical Team Names

| Former Name | Current Name | Changed |
|-------------|--------------|---------|
| Seattle SuperSonics | Oklahoma City Thunder | 2008 |
| New Jersey Nets | Brooklyn Nets | 2012 |
| Charlotte Bobcats | Charlotte Hornets | 2014 |
| New Orleans Hornets | New Orleans Pelicans | 2013 |

Keep historical names in `TEAM_ALIASES` for parsing old box scores.

## Box Score Sources

The processor parses HTML box scores from:
- **Basketball Reference:** Primary source for NBA games

Ensure parsers in `nba_processor/parsers/` can handle format changes from these sources.
