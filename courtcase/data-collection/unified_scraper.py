#!/usr/bin/env python3
"""
Unified Multi-Country Legal Scraper
Command-line tool for scraping legal documents from multiple countries
"""

import click
import yaml
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.unified_database import UnifiedDatabase
from src.scrapers.bangladesh_scraper import BangladeshLawsScraper


def load_config(country: str) -> dict:
    """Load configuration for a country"""
    config_file = Path(f"config/{country}.yaml")

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Unified Multi-Country Legal Document Scraper

    Supports scraping legal documents from:
    - Bangladesh (bdlaws.minlaw.gov.bd)
    - India (indiankanoon.org) - Coming soon
    - More countries can be added easily!
    """
    pass


@cli.command()
@click.option('--country', type=click.Choice(['bangladesh', 'india', 'all']),
              default='bangladesh', help='Country to scrape')
@click.option('--resume', is_flag=True, help='Resume from previous session')
@click.option('--limit', type=int, help='Limit number of documents to scrape')
def scrape(country, resume, limit):
    """Scrape legal documents from specified country"""

    click.echo("=" * 70)
    click.echo("Unified Multi-Country Legal Scraper")
    click.echo("=" * 70)

    db = UnifiedDatabase()

    if country == 'bangladesh' or country == 'all':
        click.echo(f"\n🇧🇩 Scraping Bangladesh Laws...")
        config = load_config('bangladesh')

        scraper = BangladeshLawsScraper(config, db)
        scraper.scrape_all(resume=resume)

    if country == 'india' or country == 'all':
        click.echo(f"\n🇮🇳 Scraping Indian Kanoon...")
        click.echo("⚠️  India scraper coming soon! Use existing bulk_download.py for now.")

    click.echo("\n✅ Scraping complete!")
    click.echo(f"📊 View statistics: python unified_scraper.py stats")

    db.close()


@cli.command()
@click.option('--country', help='Show stats for specific country only')
@click.option('--detailed', is_flag=True, help='Show detailed statistics')
def stats(country, detailed):
    """Show scraping statistics"""

    db = UnifiedDatabase()

    click.echo("=" * 70)
    click.echo("📊 Legal Documents Statistics")
    click.echo("=" * 70)

    if country:
        # Stats for specific country
        stats = db.get_country_stats(country)
        click.echo(f"\n🌍 {country.upper()} Statistics:")
        click.echo(f"  • Total documents: {stats.get('total_docs', 0):,}")
        click.echo(f"  • PDFs downloaded: {stats.get('pdfs_downloaded', 0):,}")
        click.echo(f"  • Document types: {stats.get('doc_types', 0)}")
        click.echo(f"  • Years covered: {stats.get('years_covered', 0)}")
        click.echo(f"  • Earliest year: {stats.get('earliest_year', 'N/A')}")
        click.echo(f"  • Latest year: {stats.get('latest_year', 'N/A')}")
        click.echo(f"  • Last scraped: {stats.get('last_scraped', 'N/A')}")

    else:
        # Overall stats
        overall = db.get_stats()
        click.echo(f"\n🌍 Overall Statistics:")
        click.echo(f"  • Total documents: {overall.get('total_documents', 0):,}")
        click.echo(f"  • Countries: {overall.get('total_countries', 0)}")
        click.echo(f"  • PDFs downloaded: {overall.get('pdfs_downloaded', 0):,}")
        click.echo(f"  • HTML scraped: {overall.get('html_scraped', 0):,}")
        click.echo(f"  • Active documents: {overall.get('active_documents', 0):,}")

        # Per-country breakdown
        countries = db.get_all_countries()
        if countries:
            click.echo(f"\n📋 By Country:")
            for c in countries:
                c_stats = db.get_country_stats(c)
                click.echo(f"  • {c.upper()}: {c_stats.get('total_docs', 0):,} documents")

    if detailed:
        click.echo(f"\n📄 Recent Documents:")
        docs = db.get_documents(country=country, limit=10)
        for doc in docs:
            click.echo(f"  • [{doc['country']}] {doc['title'][:60]}...")

    db.close()


@cli.command()
@click.argument('query')
@click.option('--country', help='Search within specific country only')
def search(query, country):
    """Search for documents by keyword"""

    db = UnifiedDatabase()

    click.echo(f"🔍 Searching for: '{query}'")
    if country:
        click.echo(f"   in {country}")

    results = db.search_documents(query, country=country)

    if results:
        click.echo(f"\nFound {len(results)} results:\n")
        for i, doc in enumerate(results[:20], 1):  # Show first 20
            click.echo(f"{i}. [{doc['country']}] {doc['title']}")
            if doc.get('year'):
                click.echo(f"   Year: {doc['year']}")
            click.echo(f"   URL: {doc['source_url']}\n")

        if len(results) > 20:
            click.echo(f"... and {len(results) - 20} more results")
    else:
        click.echo("No results found")

    db.close()


@cli.command()
def test():
    """Test scraper configuration and connectivity"""

    click.echo("🧪 Testing scraper configuration...\n")

    # Test database
    click.echo("1. Testing database connection...")
    try:
        db = UnifiedDatabase()
        stats = db.get_stats()
        click.echo(f"   ✓ Database OK ({stats.get('total_documents', 0)} documents)")
        db.close()
    except Exception as e:
        click.echo(f"   ✗ Database error: {e}")
        return

    # Test Bangladesh config
    click.echo("\n2. Testing Bangladesh configuration...")
    try:
        config = load_config('bangladesh')
        click.echo(f"   ✓ Config loaded: {config['name']}")
        click.echo(f"   ✓ Base URL: {config['base_url']}")
    except Exception as e:
        click.echo(f"   ✗ Config error: {e}")

    # Test connectivity
    click.echo("\n3. Testing website connectivity...")
    try:
        import requests
        response = requests.get("http://bdlaws.minlaw.gov.bd", timeout=10)
        if response.status_code == 200:
            click.echo(f"   ✓ Bangladesh Laws website is accessible")
        else:
            click.echo(f"   ⚠ Bangladesh Laws returned status {response.status_code}")
    except Exception as e:
        click.echo(f"   ✗ Connection error: {e}")

    click.echo("\n✅ Test complete!")


@cli.command()
def info():
    """Show system information"""

    click.echo("=" * 70)
    click.echo("Unified Multi-Country Legal Scraper - System Information")
    click.echo("=" * 70)

    # Database info
    db = UnifiedDatabase()
    overall = db.get_stats()

    click.echo(f"\n📊 Database:")
    click.echo(f"  • Path: {db.db_path}")
    click.echo(f"  • Documents: {overall.get('total_documents', 0):,}")
    click.echo(f"  • Countries: {overall.get('total_countries', 0)}")

    # Available countries
    click.echo(f"\n🌍 Available Countries:")
    config_dir = Path("config")
    if config_dir.exists():
        for config_file in config_dir.glob("*.yaml"):
            country = config_file.stem
            try:
                cfg = load_config(country)
                click.echo(f"  • {country.upper()}: {cfg.get('name', 'Unknown')}")
                click.echo(f"    URL: {cfg.get('base_url', 'N/A')}")
            except:
                pass

    # Directories
    click.echo(f"\n📁 Output Directories:")
    for country in db.get_all_countries():
        click.echo(f"  • {country}:")
        click.echo(f"    - PDFs: data/pdfs/{country}/")
        click.echo(f"    - HTML: data/html/{country}/")

    db.close()


if __name__ == '__main__':
    cli()
