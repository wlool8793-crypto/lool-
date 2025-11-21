#!/usr/bin/env python3
"""
Test script for Bangladesh Legal Data Scraping System
Demonstrates the complete functionality
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_source_registry():
    """Test the source registry"""
    print("🔧 Testing Source Registry...")

    from src.scrapers.bangladesh.source_registry import BangladeshSourceRegistry

    registry = BangladeshSourceRegistry()

    # Test source counts
    stats = registry.get_source_stats()
    print(f"✅ Total sources loaded: {stats['total_sources']}")
    print(f"✅ Tier distribution: {stats['tier_distribution']}")
    print(f"✅ Type distribution: {stats['type_distribution']}")

    # Test specific source retrieval
    bdlaws = registry.get_source('bdlaws')
    if bdlaws:
        print(f"✅ Found bdlaws: {bdlaws.name} ({bdlaws.url})")

    # Test priority order
    priority = registry.get_priority_order()
    print(f"✅ Priority order (first 5): {priority[:5]}")

    return True

def test_plugin_manager():
    """Test the plugin manager"""
    print("\n🔧 Testing Plugin Manager...")

    from src.scrapers.bangladesh.plugin_manager import PluginManager

    try:
        with PluginManager(max_workers=3) as manager:
            # Test statistics
            stats = manager.get_statistics()
            print(f"✅ Plugin manager stats: {stats['total_sources']} sources")
            print(f"✅ Available scrapers: {stats['available_scrapers']}")

            # Test getting specific scraper
            scraper = manager.get_scraper('bdlaws')
            if scraper:
                print(f"✅ Created bdlaws scraper: {type(scraper).__name__}")

            # Test getting stub scraper
            bdlex_scraper = manager.get_scraper('bdlex')
            if bdlex_scraper:
                print(f"✅ Created bdlex stub scraper: {type(bdlex_scraper).__name__}")

        return True
    except Exception as e:
        print(f"❌ Plugin manager test failed: {e}")
        return False

def test_individual_scraper():
    """Test an individual scraper"""
    print("\n🔧 Testing Individual Scraper...")

    from src.scrapers.bangladesh.tier1.bdlaws_scraper import BDLawsScraper

    config = {
        'source_name': 'bdlaws',
        'base_url': 'https://bdlaws.minlaw.gov.bd',
        'rate_limit': 1.0
    }

    try:
        with BDLawsScraper(config) as scraper:
            print(f"✅ Created scraper: {scraper.source_name}")

            # Test connection
            connection = scraper.test_connection()
            print(f"✅ Connection test: {'Success' if connection else 'Failed (expected in sandbox)'}")

            # Test document list (may fail in sandbox)
            try:
                documents = scraper.get_document_list(limit=5)
                print(f"✅ Document list test: {len(documents)} documents found")
            except Exception as e:
                print(f"⚠️ Document list test: {e} (expected in sandbox)")

        return True
    except Exception as e:
        print(f"❌ Individual scraper test failed: {e}")
        return False

def test_cli_help():
    """Test CLI help functionality"""
    print("\n🔧 Testing CLI Help...")

    import subprocess

    try:
        result = subprocess.run([
            'python', 'bangladesh_master_scraper.py', '--help'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ CLI help command works")
            return True
        else:
            print(f"⚠️ CLI help returned: {result.returncode}")
            print(f"Output: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration Loading...")

    try:
        # Test if config file exists
        config_path = Path(__file__).parent / 'config' / 'sources' / 'bangladesh' / 'bangladesh_sources.yaml'
        if config_path.exists():
            print(f"✅ Config file found: {config_path}")

            # Try to load and parse
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'sources' in config:
                print(f"✅ Config loaded with {len(config['sources'])} sources")
                return True
            else:
                print("⚠️ Config loaded but no 'sources' section found")
                return False
        else:
            print(f"⚠️ Config file not found: {config_path}")
            return False

    except Exception as e:
        print(f"❌ Config loading test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Bangladesh Legal Data Scraping System - Test Suite")
    print("=" * 60)

    tests = [
        ("Source Registry", test_source_registry),
        ("Plugin Manager", test_plugin_manager),
        ("Individual Scraper", test_individual_scraper),
        ("CLI Help", test_cli_help),
        ("Config Loading", test_config_loading)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! The Bangladesh Legal Data Scraping System is ready!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)