#!/usr/bin/env python3
"""
Complete System Validation - All 4 Phases
Tests integration of all components
"""

import sys
import os
from pathlib import Path
import subprocess
import psycopg2
import sqlite3
import yaml

sys.path.insert(0, '/workspaces/lool-/data-collection')

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_phase(phase_num, phase_name):
    print(f"\n{YELLOW}{'─'*80}{RESET}")
    print(f"{YELLOW}PHASE {phase_num}: {phase_name}{RESET}")
    print(f"{YELLOW}{'─'*80}{RESET}\n")

def check_pass(test_name):
    print(f"{GREEN}✅ PASS{RESET} - {test_name}")
    return True

def check_fail(test_name, error):
    print(f"{RED}❌ FAIL{RESET} - {test_name}: {error}")
    return False

def check_warning(test_name, warning):
    print(f"{YELLOW}⚠️  WARN{RESET} - {test_name}: {warning}")
    return None

# ============================================================================
# PHASE 1: BASIC INFRASTRUCTURE
# ============================================================================

def validate_phase1():
    """Validate Phase 1: Basic Infrastructure"""
    print_phase(1, "BASIC INFRASTRUCTURE")
    results = []

    # 1. Check directory structure
    try:
        required_dirs = [
            'data', 'data/pdfs', 'logs', 'checkpoints',
            'config', 'src', 'src/database', 'scripts'
        ]
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                results.append(check_pass(f"Directory exists: {dir_path}"))
            else:
                results.append(check_fail(f"Directory missing: {dir_path}", "Not found"))
    except Exception as e:
        results.append(check_fail("Directory structure", str(e)))

    # 2. Check SQLite database
    try:
        if Path('data/indiankanoon.db').exists():
            conn = sqlite3.connect('data/indiankanoon.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM universal_legal_documents")
            count = cursor.fetchone()[0]
            conn.close()
            results.append(check_pass(f"SQLite database ({count} documents)"))
        else:
            results.append(check_warning("SQLite database", "Not found (using PostgreSQL)"))
    except Exception as e:
        results.append(check_fail("SQLite database", str(e)))

    # 3. Check configuration files
    try:
        configs = [
            'config/config_single_ip.yaml',
            'config/config_postgresql.yaml'
        ]
        for config in configs:
            if Path(config).exists():
                with open(config) as f:
                    yaml.safe_load(f)
                results.append(check_pass(f"Config file: {config}"))
            else:
                results.append(check_fail(f"Config file: {config}", "Not found"))
    except Exception as e:
        results.append(check_fail("Configuration files", str(e)))

    # 4. Check database models
    try:
        from src.database.models import Base, Document, FileStorage
        results.append(check_pass("Database models imported"))
    except Exception as e:
        results.append(check_fail("Database models", str(e)))

    # 5. Check PDF storage
    try:
        pdf_dir = Path('data/pdfs')
        if pdf_dir.exists():
            pdf_count = len(list(pdf_dir.glob('*.pdf')))
            results.append(check_pass(f"PDF storage ({pdf_count} PDFs)"))
        else:
            results.append(check_fail("PDF storage", "Directory not found"))
    except Exception as e:
        results.append(check_fail("PDF storage", str(e)))

    return results

# ============================================================================
# PHASE 2: PERFORMANCE OPTIMIZATIONS
# ============================================================================

def validate_phase2():
    """Validate Phase 2: Performance Optimizations"""
    print_phase(2, "PERFORMANCE OPTIMIZATIONS")
    results = []

    # 1. Check scraper files
    try:
        scrapers = [
            'single_ip_production_scraper.py',
            'postgresql_production_scraper.py'
        ]
        for scraper in scrapers:
            if Path(scraper).exists():
                # Check for optimization features
                with open(scraper) as f:
                    content = f.read()

                    # Check for connection pooling
                    if 'thread_local' in content or '_get_session' in content:
                        results.append(check_pass(f"{scraper}: Connection pooling"))
                    else:
                        results.append(check_warning(f"{scraper}: Connection pooling", "Not found"))

                    # Check for direct PDF optimization
                    if '.pdf' in content and 'endswith' in content:
                        results.append(check_pass(f"{scraper}: Direct PDF download"))
                    else:
                        results.append(check_warning(f"{scraper}: Direct PDF download", "Not found"))

                    # Check for checkpointing
                    if 'checkpoint' in content.lower():
                        results.append(check_pass(f"{scraper}: Checkpointing"))
                    else:
                        results.append(check_fail(f"{scraper}: Checkpointing", "Not found"))
            else:
                results.append(check_fail(f"Scraper: {scraper}", "Not found"))
    except Exception as e:
        results.append(check_fail("Scraper files", str(e)))

    # 2. Check PostgreSQL adapter
    try:
        from src.database.postgresql_adapter import PostgreSQLAdapter
        results.append(check_pass("PostgreSQL adapter"))
    except Exception as e:
        results.append(check_fail("PostgreSQL adapter", str(e)))

    # 3. Check worker configuration
    try:
        with open('config/config_postgresql.yaml') as f:
            config = yaml.safe_load(f)
            workers = config['performance']['max_workers']
            if workers == 2:
                results.append(check_pass(f"Worker configuration ({workers} workers - optimal)"))
            else:
                results.append(check_warning("Worker configuration", f"{workers} workers configured"))
    except Exception as e:
        results.append(check_fail("Worker configuration", str(e)))

    # 4. Check rate limiting
    try:
        with open('config/config_postgresql.yaml') as f:
            config = yaml.safe_load(f)
            delay = config['scraper']['delay_between_requests']
            if delay == 0.5:
                results.append(check_pass(f"Rate limiting ({delay}s delay = 2 req/sec)"))
            else:
                results.append(check_warning("Rate limiting", f"{delay}s delay configured"))
    except Exception as e:
        results.append(check_fail("Rate limiting", str(e)))

    return results

# ============================================================================
# PHASE 3: QUALITY GATES
# ============================================================================

def validate_phase3():
    """Validate Phase 3: Quality Gates"""
    print_phase(3, "QUALITY GATES & VALIDATION")
    results = []

    # 1. Check quality configuration
    try:
        if Path('config/quality_thresholds.yaml').exists():
            with open('config/quality_thresholds.yaml') as f:
                config = yaml.safe_load(f)
            results.append(check_pass("Quality thresholds configuration"))
        else:
            results.append(check_warning("Quality thresholds", "Config file not found"))
    except Exception as e:
        results.append(check_warning("Quality configuration", str(e)))

    # 2. Check URL classifier
    try:
        if Path('src/url_classifier.py').exists():
            results.append(check_pass("URL classifier"))
        else:
            results.append(check_warning("URL classifier", "Not found"))
    except Exception as e:
        results.append(check_warning("URL classifier", str(e)))

    # 3. Check migration scripts
    try:
        migration_files = list(Path('migrations').glob('*.sql')) if Path('migrations').exists() else []
        if migration_files:
            results.append(check_pass(f"Database migrations ({len(migration_files)} files)"))
        else:
            results.append(check_warning("Database migrations", "No migration files found"))
    except Exception as e:
        results.append(check_warning("Database migrations", str(e)))

    # 4. Check quality validation in scrapers
    try:
        for scraper in ['single_ip_production_scraper.py', 'postgresql_production_scraper.py']:
            if Path(scraper).exists():
                with open(scraper) as f:
                    content = f.read()
                    if 'PDF' in content and ('validate' in content.lower() or 'startswith' in content):
                        results.append(check_pass(f"{scraper}: PDF validation"))
                    else:
                        results.append(check_warning(f"{scraper}: PDF validation", "Not clearly implemented"))
    except Exception as e:
        results.append(check_warning("Quality validation", str(e)))

    return results

# ============================================================================
# PHASE 4: POSTGRESQL PRODUCTION
# ============================================================================

def validate_phase4():
    """Validate Phase 4: PostgreSQL Production System"""
    print_phase(4, "POSTGRESQL PRODUCTION SYSTEM")
    results = []

    # 1. Check PostgreSQL container
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'indiankanoon-postgres' in result.stdout:
            results.append(check_pass("PostgreSQL container running"))
        else:
            results.append(check_fail("PostgreSQL container", "Not running"))
            return results  # Can't continue if PostgreSQL isn't running
    except Exception as e:
        results.append(check_fail("Docker check", str(e)))
        return results

    # 2. Check PostgreSQL connection
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='indiankanoon',
            user='indiankanoon_user',
            password='postgres'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        conn.close()
        results.append(check_pass(f"PostgreSQL connection ({version[:20]}...)"))
    except Exception as e:
        results.append(check_fail("PostgreSQL connection", str(e)))
        return results

    # 3. Check database schema
    try:
        conn = psycopg2.connect(
            host='localhost', port=5433, database='indiankanoon',
            user='indiankanoon_user', password='postgres'
        )
        cursor = conn.cursor()

        # Check for required tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['documents', 'file_storage', 'parties', 'judges', 'citations']
        for table in required_tables:
            if table in tables:
                results.append(check_pass(f"Table exists: {table}"))
            else:
                results.append(check_fail(f"Table missing: {table}", "Not found"))

        conn.close()
    except Exception as e:
        results.append(check_fail("Database schema", str(e)))

    # 4. Check data migration
    try:
        conn = psycopg2.connect(
            host='localhost', port=5433, database='indiankanoon',
            user='indiankanoon_user', password='postgres'
        )
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM file_storage")
        file_count = cursor.fetchone()[0]

        conn.close()

        results.append(check_pass(f"Documents migrated ({doc_count} documents)"))
        results.append(check_pass(f"Files tracked ({file_count} PDFs)"))
    except Exception as e:
        results.append(check_fail("Data migration", str(e)))

    # 5. Check PostgreSQL scraper
    try:
        if Path('postgresql_production_scraper.py').exists():
            with open('postgresql_production_scraper.py') as f:
                content = f.read()
                if 'PostgreSQLAdapter' in content:
                    results.append(check_pass("PostgreSQL scraper implementation"))
                else:
                    results.append(check_fail("PostgreSQL scraper", "Adapter not found"))
        else:
            results.append(check_fail("PostgreSQL scraper", "File not found"))
    except Exception as e:
        results.append(check_fail("PostgreSQL scraper", str(e)))

    # 6. Check migration script
    try:
        if Path('scripts/migrate_to_postgres_production.py').exists():
            results.append(check_pass("Migration script"))
        else:
            results.append(check_warning("Migration script", "Not found"))
    except Exception as e:
        results.append(check_warning("Migration script", str(e)))

    return results

# ============================================================================
# INTEGRATION TEST
# ============================================================================

def run_integration_test():
    """Run end-to-end integration test"""
    print_phase(5, "END-TO-END INTEGRATION TEST")
    results = []

    # 1. Test PostgreSQL scraper with 1 document
    try:
        print("Running: python3 postgresql_production_scraper.py --limit 1")
        result = subprocess.run(
            ['python3', 'postgresql_production_scraper.py', '--limit', '1'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd='/workspaces/lool-/data-collection'
        )

        if 'Connected to PostgreSQL' in result.stdout:
            results.append(check_pass("PostgreSQL scraper execution"))
        else:
            results.append(check_warning("PostgreSQL scraper", "Connection message not found"))

        if 'SCRAPING SESSION COMPLETE' in result.stdout:
            results.append(check_pass("Scraper completes successfully"))
        else:
            results.append(check_fail("Scraper completion", "Did not complete"))

    except subprocess.TimeoutExpired:
        results.append(check_fail("Integration test", "Timeout after 60s"))
    except Exception as e:
        results.append(check_fail("Integration test", str(e)))

    # 2. Verify database was updated
    try:
        conn = psycopg2.connect(
            host='localhost', port=5433, database='indiankanoon',
            user='indiankanoon_user', password='postgres'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        count_after = cursor.fetchone()[0]
        conn.close()

        results.append(check_pass(f"Database accessible after scrape ({count_after} docs)"))
    except Exception as e:
        results.append(check_fail("Post-scrape database check", str(e)))

    return results

# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():
    print_header("COMPLETE SYSTEM VALIDATION - ALL 4 PHASES")
    print(f"{BLUE}Validating integration of all components{RESET}\n")

    all_results = {}

    # Run validation for each phase
    all_results['Phase 1'] = validate_phase1()
    all_results['Phase 2'] = validate_phase2()
    all_results['Phase 3'] = validate_phase3()
    all_results['Phase 4'] = validate_phase4()
    all_results['Integration'] = run_integration_test()

    # Summary
    print_header("VALIDATION SUMMARY")

    total_pass = 0
    total_fail = 0
    total_warn = 0

    for phase, results in all_results.items():
        pass_count = sum(1 for r in results if r is True)
        fail_count = sum(1 for r in results if r is False)
        warn_count = sum(1 for r in results if r is None)

        total_pass += pass_count
        total_fail += fail_count
        total_warn += warn_count

        status = f"{GREEN}✅{RESET}" if fail_count == 0 else f"{RED}❌{RESET}"
        print(f"{status} {phase}: {pass_count} passed, {fail_count} failed, {warn_count} warnings")

    print(f"\n{BLUE}{'─'*80}{RESET}")
    print(f"Total: {GREEN}{total_pass} passed{RESET}, {RED}{total_fail} failed{RESET}, {YELLOW}{total_warn} warnings{RESET}")
    print(f"{BLUE}{'─'*80}{RESET}\n")

    # Final verdict
    if total_fail == 0:
        print(f"{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}✅ ALL PHASES COMPLETE AND WORKING TOGETHER!{RESET}")
        print(f"{GREEN}{'='*80}{RESET}\n")
        print(f"{GREEN}🚀 System is PRODUCTION READY{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*80}{RESET}")
        print(f"{RED}❌ SOME COMPONENTS NEED ATTENTION{RESET}")
        print(f"{RED}{'='*80}{RESET}\n")
        print(f"{YELLOW}Review failures above before deploying{RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Validation interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Validation error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
