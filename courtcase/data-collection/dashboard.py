#!/usr/bin/env python3
"""
Real-time Scraping Monitor Dashboard
Flask-based web dashboard to monitor scraping progress
"""

from flask import Flask, render_template, jsonify
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
DATABASE_PATH = os.getenv('DATABASE_URL', 'sqlite:///data/indiankanoon.db').replace('sqlite:///', '')
PROXY_LIST_FILE = 'config/proxy_list.json'
PROXY_TEST_REPORT = 'config/proxy_test_report.json'


def get_db_stats():
    """Get statistics from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Total cases
        cursor.execute("SELECT COUNT(*) FROM legal_cases")
        total_cases = cursor.fetchone()[0]

        # PDFs downloaded
        cursor.execute("SELECT COUNT(*) FROM legal_cases WHERE pdf_downloaded = 1")
        pdfs_downloaded = cursor.fetchone()[0]

        # Cases added today
        cursor.execute("""
            SELECT COUNT(*) FROM legal_cases
            WHERE created_at >= date('now')
        """)
        added_today = cursor.fetchone()[0]

        # Recent cases
        cursor.execute("""
            SELECT id, title, court, created_at
            FROM legal_cases
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_cases = cursor.fetchall()

        conn.close()

        return {
            'total_cases': total_cases,
            'pdfs_downloaded': pdfs_downloaded,
            'added_today': added_today,
            'recent_cases': [
                {
                    'id': row[0],
                    'title': row[1],
                    'court': row[2],
                    'created_at': row[3]
                }
                for row in recent_cases
            ]
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_cases': 0,
            'pdfs_downloaded': 0,
            'added_today': 0,
            'recent_cases': []
        }


def get_proxy_stats():
    """Get proxy statistics"""
    try:
        # Load proxy list
        if Path(PROXY_LIST_FILE).exists():
            with open(PROXY_LIST_FILE, 'r') as f:
                proxy_data = json.load(f)
                total_proxies = proxy_data.get('total_proxies', 0)
                providers = proxy_data.get('providers', {})
        else:
            total_proxies = 0
            providers = {}

        # Load test report
        working_proxies = 0
        failed_proxies = 0
        avg_response_time = 0

        if Path(PROXY_TEST_REPORT).exists():
            with open(PROXY_TEST_REPORT, 'r') as f:
                test_data = json.load(f)
                summary = test_data.get('summary', {})
                working_proxies = summary.get('working', 0)
                failed_proxies = summary.get('failed', 0)
                avg_response_time = summary.get('avg_response_time', 0)

        return {
            'total_proxies': total_proxies,
            'working_proxies': working_proxies,
            'failed_proxies': failed_proxies,
            'avg_response_time': avg_response_time,
            'providers': providers
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_proxies': 0,
            'working_proxies': 0,
            'failed_proxies': 0,
            'avg_response_time': 0,
            'providers': {}
        }


def calculate_progress(total_cases: int, target: int = 1400000):
    """Calculate scraping progress"""
    percentage = (total_cases / target) * 100 if target > 0 else 0

    # Estimate completion
    # Assume average rate based on recent progress
    # This is a simplified estimation
    if total_cases > 0:
        # Rough estimate: if we have X cases now, and we started recently
        days_elapsed = 1  # TODO: Calculate from first case date
        rate_per_day = total_cases / days_elapsed if days_elapsed > 0 else 0
        remaining = target - total_cases
        days_remaining = remaining / rate_per_day if rate_per_day > 0 else 0
        completion_date = datetime.now() + timedelta(days=days_remaining)
    else:
        rate_per_day = 0
        days_remaining = 0
        completion_date = None

    return {
        'current': total_cases,
        'target': target,
        'percentage': round(percentage, 2),
        'rate_per_day': int(rate_per_day),
        'days_remaining': round(days_remaining, 1),
        'completion_date': completion_date.strftime('%Y-%m-%d') if completion_date else 'N/A'
    }


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    db_stats = get_db_stats()
    proxy_stats = get_proxy_stats()
    progress = calculate_progress(db_stats.get('total_cases', 0))

    return jsonify({
        'database': db_stats,
        'proxies': proxy_stats,
        'progress': progress,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/logs')
def api_logs():
    """API endpoint for recent logs"""
    log_file = Path('logs/scraper.log')

    if not log_file.exists():
        return jsonify({'logs': []})

    # Read last 50 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
        recent_logs = lines[-50:] if len(lines) > 50 else lines

    return jsonify({'logs': recent_logs})


if __name__ == '__main__':
    # Create template directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            Scraping Monitor Dashboard Starting...            ║
    ║              Indian Kanoon Scraper Project                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    print("\n🌐 Dashboard URL: http://127.0.0.1:5000")
    print("📊 Monitoring database, proxies, and scraping progress...")
    print("🔄 Auto-refreshes every 10 seconds\n")

    app.run(debug=True, host='127.0.0.1', port=5000)
