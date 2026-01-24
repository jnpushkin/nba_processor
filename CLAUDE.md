# Claude Code Instructions

## Python
Always use `python3` instead of `python` for all commands.

## Project Structure
- Root directory IS the `nba_processor` package (no nested `nba_processor/nba_processor/`)
- `engines/` - Milestone detection engine (55+ milestone types)
- `parsers/` - Basketball Reference HTML parsing
- `processors/` - Stats aggregation
- `website/` - HTML website generation
- `tests/` - Pytest test suite (189 tests)
- `cache/` - Cached parsed game data

## Running the Processor
```bash
cd /Users/jeremypushkin
python3 -m nba_processor [input_path]            # Process games
python3 -m nba_processor --website-only          # Skip Excel
python3 -m nba_processor --from-cache-only       # Use cached data
```

## Running Tests
```bash
cd /Users/jeremypushkin/nba_processor
python3 -m pytest tests/              # All tests
python3 -m pytest tests/ -v           # Verbose
python3 -m pytest tests/ -k milestone # Filter by name
```

## Deployment
Website deploys to Surge (configured in main.py)

## Key Files
- `engines/milestone_engine.py` - Milestone detection (55+ types)
- `parsers/html_parser.py` - HTML parsing, outputs `box_score` structure
- `processors/player_stats_processor.py` - Stats aggregation
- `tests/conftest.py` - Test fixtures

## Architecture Notes
- Milestone engine uses tiered elif pattern (only highest tier reported per category)
- HTML parser outputs `box_score.away.players[]` and `box_score.home.players[]`
- Test fixtures include BOTH `box_score` and `players` keys for compatibility
- Tests use `sys.path.insert(0, parent.parent.parent)` to find the package

## Do NOT
- Create nested `nba_processor/nba_processor/` directory structure
- Use `python` command (always `python3`)
- Modify test fixtures without including both `box_score` and `players` formats
