"""NBA Processor data scrapers."""

from .boxscore_scraper import BoxscoreScraper, download_boxscores
from .br_extras_scraper import BRExtrasScraper

__all__ = ['BoxscoreScraper', 'download_boxscores', 'BRExtrasScraper']
