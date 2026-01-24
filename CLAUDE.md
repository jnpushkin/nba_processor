# Claude Code Instructions

## Python
Always use `python3` instead of `python` for all commands.

## Project Structure
- Root directory IS the `nba_processor` package (no nested `nba_processor/nba_processor/`)
- `engines/` - Milestone detection engine (55+ milestone types)
- `parsers/` - Basketball Reference HTML parsing
- `processors/` - Stats aggregation
- `scrapers/` - Web scrapers for Basketball Reference
- `website/` - HTML website generation
- `tests/` - Pytest test suite (189 tests)
- `cache/` - Cached parsed game data and career firsts

## Running the Processor
```bash
cd /Users/jeremypushkin
python3 -m nba_processor [input_path]            # Process games (auto-deploys)
python3 -m nba_processor --website-only          # Skip Excel
python3 -m nba_processor --from-cache-only       # Use cached data
python3 -m nba_processor --scrape-firsts         # Also scrape career firsts for players with new games
python3 -m nba_processor --no-deploy             # Skip Surge deployment
```

## Scraping Career Firsts
```bash
python3 -m nba_processor.scrapers.career_firsts_scraper              # All players
python3 -m nba_processor.scrapers.career_firsts_scraper --player curryst01  # Single player
python3 -m nba_processor.scrapers.career_firsts_scraper --check-witnessed   # Show witnessed
```

**Important:** Basketball Reference rate limits aggressively. Use 3.1+ second delays between requests. On 429 errors, wait 15 minutes before retrying.

## Running Tests
```bash
cd /Users/jeremypushkin/nba_processor
python3 -m pytest tests/              # All tests
python3 -m pytest tests/ -v           # Verbose
python3 -m pytest tests/ -k milestone # Filter by name
```

## Deployment
Website auto-deploys to Surge after generation (use `--no-deploy` to skip). Domain: nba-processor.surge.sh

## Key Files
- `engines/milestone_engine.py` - Milestone detection (55+ types)
- `parsers/html_parser.py` - HTML parsing, outputs `box_score` structure
- `processors/player_stats_processor.py` - Stats aggregation
- `scrapers/career_firsts_scraper.py` - Career milestone scraper
- `tests/conftest.py` - Test fixtures

## Architecture Notes
- Milestone engine uses tiered elif pattern (only highest tier reported per category)
- HTML parser outputs `box_score.away.players[]` and `box_score.home.players[]`
- Test fixtures include BOTH `box_score` and `players` keys for compatibility
- Tests use `sys.path.insert(0, parent.parent.parent)` to find the package
- Career milestones track points/rebounds/assists/etc at 1000, 2000, 3000... intervals
- Sports-Reference sites (Basketball-Reference, Baseball-Reference) hide tables in HTML comments for lazy loading - must extract and parse them with BeautifulSoup Comment class
- Basketball-Reference game log uses `data-stat='date'` (not 'date_game'), `data-stat='opp_name_abbr'` (not 'opp_id'), and `data-stat='year_id'` for season
- NBA game log URLs use ending year: 2009-10 season → `/gamelog/2010`

## Error Handling
When encountering repeated errors or discovering project-specific quirks:
- Update this CLAUDE.md file with the finding
- Add to "Do NOT" section if it's a common mistake
- Add to "Architecture Notes" if it's a structural insight

## Do NOT
- Create nested `nba_processor/nba_processor/` directory structure
- Use `python` command (always `python3`)
- Modify test fixtures without including both `box_score` and `players` formats
- Scrape Basketball Reference faster than 3.1s between requests
