#!/usr/bin/env python3
"""
Unified Multi-Country Legal Scraper - FAST MODE
Supports 10 concurrent workers for faster scraping
"""

import click
import yaml
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.unified_database import UnifiedDatabase
from src.scrapers.bangladesh_scraper import BangladeshLawsScraper


def load_config(country: str, fast_mode: bool = False) -> dict:
    """Load configuration for a country"""
    if fast_mode:
        config_file = Path(f"config/{country}_fast.yaml")
        if not config_file.exists():
            config_file = Path(f"config/{country}.yaml")
    else:
        config_file = Path(f"config/{country}.yaml")

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def scrape_document_worker(scraper, url):
    """Worker function to scrape a single document"""
    try:
        doc_data = scraper.parse_document(url)
        if doc_data:
            scraper.save_document(doc_data)

            # Download PDF if available
            if doc_data.get('pdf_url') and scraper.download_pdfs:
                pdf_path = scraper.download_pdf(
                    doc_data['pdf_url'],
                    doc_data.get('id', 0)
                )
                if pdf_path and doc_data.get('id'):
                    scraper.db.update_pdf_path(doc_data['id'], pdf_path)

            return {'success': True, 'url': url, 'title': doc_data.get('title', 'Unknown')}
        else:
            return {'success': False, 'url': url, 'error': 'Failed to parse'}

    except Exception as e:
        return {'success': False, 'url': url, 'error': str(e)}


@click.group()
@click.version_option(version="1.0.0-fast")
def cli():
    """
    Unified Multi-Country Legal Document Scraper - FAST MODE

    Uses 10 concurrent workers for faster scraping!
    """
    pass


@cli.command()
@click.option('--country', type=click.Choice(['bangladesh', 'india']),
              default='bangladesh', help='Country to scrape')
@click.option('--workers', type=int, default=10, help='Number of concurrent workers')
@click.option('--resume', is_flag=True, help='Resume from previous session')
@click.option('--limit', type=int, help='Limit number of documents to scrape')
def scrape(country, workers, resume, limit):
    """Scrape legal documents with concurrent workers"""

    click.echo("=" * 70)
    click.echo(f"Unified Legal Scraper - FAST MODE ({workers} workers)")
    click.echo("=" * 70)

    if country == 'bangladesh':
        click.echo(f"\n🇧🇩 Scraping Bangladesh Laws with {workers} concurrent workers...")

        # Load fast config
        config = load_config('bangladesh', fast_mode=True)
        config['concurrent_workers'] = workers

        db = UnifiedDatabase()
        scraper = BangladeshLawsScraper(config, db)

        # Get document list
        click.echo("📋 Getting document list...")
        urls = scraper.get_document_list()

        # Filter already scraped if resuming
        if resume:
            scraped_urls = db.get_scraped_urls(country)
            urls = [url for url in urls if url not in scraped_urls]
            click.echo(f"📝 Resuming: {len(urls)} documents remaining")

        # Apply limit if specified
        if limit:
            urls = urls[:limit]

        click.echo(f"🎯 Scraping {len(urls)} documents with {workers} workers...")

        # Statistics
        stats = {'successful': 0, 'failed': 0, 'pdfs': 0}

        # Scrape with concurrent workers
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(scrape_document_worker, scraper, url): url
                for url in urls
            }

            # Process results with progress bar
            with tqdm(total=len(urls), desc="Scraping", unit="doc") as pbar:
                for future in as_completed(future_to_url):
                    result = future.result()

                    if result['success']:
                        stats['successful'] += 1
                        pbar.set_postfix({
                            'success': stats['successful'],
                            'failed': stats['failed']
                        })
                    else:
                        stats['failed'] += 1

                    pbar.update(1)

        # Final stats
        click.echo("\n" + "=" * 70)
        click.echo("✅ SCRAPING COMPLETE")
        click.echo("=" * 70)
        click.echo(f"📊 Results:")
        click.echo(f"  • Successful: {stats['successful']:,}")
        click.echo(f"  • Failed: {stats['failed']:,}")
        click.echo(f"  • Success Rate: {stats['successful']/len(urls)*100:.1f}%")

        db.close()

    else:
        click.echo(f"\n🇮🇳 India scraper not yet implemented for fast mode")
        click.echo("Use: python bulk_download.py")


@cli.command()
@click.option('--country', help='Show stats for specific country')
def stats(country):
    """Show scraping statistics"""
    db = UnifiedDatabase()

    click.echo("=" * 70)
    click.echo("📊 Scraping Statistics")
    click.echo("=" * 70)

    if country:
        stats = db.get_country_stats(country)
        click.echo(f"\n🌍 {country.upper()}:")
        click.echo(f"  • Total documents: {stats.get('total_docs', 0):,}")
        click.echo(f"  • PDFs downloaded: {stats.get('pdfs_downloaded', 0):,}")
    else:
        overall = db.get_stats()
        click.echo(f"\n🌍 Overall:")
        click.echo(f"  • Total documents: {overall.get('total_documents', 0):,}")
        click.echo(f"  • Countries: {overall.get('total_countries', 0)}")
        click.echo(f"  • PDFs: {overall.get('pdfs_downloaded', 0):,}")

        # Per country
        for c in db.get_all_countries():
            c_stats = db.get_country_stats(c)
            click.echo(f"\n  {c.upper()}: {c_stats.get('total_docs', 0):,} documents")

    db.close()


@cli.command()
def benchmark():
    """Run a benchmark with different worker counts"""

    click.echo("🏃 Running benchmark...")
    click.echo("Testing different worker counts: 1, 5, 10, 20")

    import time
    from src.unified_database import UnifiedDatabase

    config = load_config('bangladesh', fast_mode=True)
    db = UnifiedDatabase()

    # Get small sample of URLs
    scraper = BangladeshLawsScraper(config, db)
    all_urls = scraper.get_document_list()
    sample_urls = all_urls[:20]  # Test with 20 documents

    results = {}

    for worker_count in [1, 5, 10, 20]:
        click.echo(f"\n⏱️  Testing with {worker_count} workers...")

        start_time = time.time()
        successful = 0

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(scrape_document_worker, scraper, url)
                      for url in sample_urls]

            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    successful += 1

        elapsed = time.time() - start_time
        rate = len(sample_urls) / elapsed

        results[worker_count] = {
            'time': elapsed,
            'rate': rate,
            'successful': successful
        }

        click.echo(f"   ✓ Time: {elapsed:.1f}s | Rate: {rate:.1f} docs/sec")

    # Show summary
    click.echo("\n" + "=" * 70)
    click.echo("📊 Benchmark Results")
    click.echo("=" * 70)
    for workers, data in results.items():
        click.echo(f"{workers:2d} workers: {data['time']:6.1f}s  |  {data['rate']:5.1f} docs/sec")

    db.close()


if __name__ == '__main__':
    cli()
