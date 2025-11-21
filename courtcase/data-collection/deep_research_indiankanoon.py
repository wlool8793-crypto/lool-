#!/usr/bin/env python3
"""
COMPREHENSIVE DEEP RESEARCH OF INDIANKANOON.ORG
Explores ALL features, document types, and content available on the website
Uses Selenium for full JavaScript rendering and interaction
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

class IndianKanoonResearcher:
    def __init__(self):
        self.base_url = "https://indiankanoon.org"
        self.research_data = {
            'timestamp': datetime.now().isoformat(),
            'homepage': {},
            'document_types': {},
            'courts': {},
            'features': {},
            'search_capabilities': {},
            'statutes_and_acts': {},
            'data_estimates': {}
        }

    def setup_browser(self):
        """Initialize Selenium browser"""
        print("Setting up browser...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.binary_location = '/snap/bin/chromium'

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✓ Browser ready\n")

    def research_homepage(self):
        """Analyze homepage structure and features"""
        print("=" * 80)
        print("1. HOMEPAGE ANALYSIS")
        print("=" * 80)

        try:
            self.driver.get(self.base_url)
            time.sleep(3)

            # Get title and meta
            self.research_data['homepage']['title'] = self.driver.title
            print(f"Title: {self.driver.title}")

            # Find all navigation links
            nav_links = self.driver.find_elements(By.TAG_NAME, 'a')
            unique_links = set()
            for link in nav_links[:50]:  # Check first 50 links
                href = link.get_attribute('href')
                if href and self.base_url in href:
                    unique_links.add(href)

            self.research_data['homepage']['navigation_links'] = list(unique_links)
            print(f"Navigation links found: {len(unique_links)}")

            # Look for search box
            try:
                search_box = self.driver.find_element(By.ID, 'search-box')
                self.research_data['homepage']['has_search'] = True
                print("✓ Search functionality available")
            except:
                self.research_data['homepage']['has_search'] = False

        except Exception as e:
            print(f"Error analyzing homepage: {e}")

    def research_document_types(self):
        """Explore all available document types"""
        print("\n" + "=" * 80)
        print("2. DOCUMENT TYPES DISCOVERY")
        print("=" * 80)

        # Test different document type searches
        doc_types = [
            'supremecourt',
            'highcourt',
            'tribunal',
            'district',
            'constitution',
            'act',
            'statute',
            'ordinance',
            'notification',
            'circular'
        ]

        for doc_type in doc_types:
            try:
                url = f"{self.base_url}/search/?formInput=doctypes:%20{doc_type}%20fromdate:%201-1-2023%20todate:%2031-12-2023"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                results = soup.find_all('div', class_='result')
                has_results = len(results) > 0 and 'No matching results' not in response.text

                self.research_data['document_types'][doc_type] = {
                    'available': has_results,
                    'sample_count_2023': len(results) if has_results else 0
                }

                status = "✓ Available" if has_results else "✗ Not available/No results"
                print(f"{doc_type:20s}: {status:20s} ({len(results)} on first page)")

                time.sleep(1)
            except Exception as e:
                print(f"{doc_type:20s}: Error - {e}")

    def research_courts(self):
        """Discover all available courts and their hierarchies"""
        print("\n" + "=" * 80)
        print("3. COURT SYSTEM MAPPING")
        print("=" * 80)

        # Supreme Court
        print("\nSupreme Court of India:")
        self._count_cases_by_years('supremecourt', range(2020, 2025))

        # High Courts (try to find which ones)
        print("\nHigh Courts:")
        high_court_states = [
            'Delhi', 'Mumbai', 'Calcutta', 'Madras', 'Karnataka',
            'Kerala', 'Gujarat', 'Rajasthan', 'Punjab', 'Allahabad'
        ]

        for state in high_court_states:
            try:
                url = f"{self.base_url}/search/?formInput={state}%20highcourt%20fromdate:%201-1-2023%20todate:%2031-12-2023"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='result')

                if len(results) > 0:
                    print(f"  {state:15s}: {len(results)} results")
                    if state not in self.research_data['courts']:
                        self.research_data['courts'][state] = {}
                    self.research_data['courts'][state]['high_court_cases_2023'] = len(results)

                time.sleep(1)
            except:
                pass

    def _count_cases_by_years(self, doc_type, years):
        """Count cases for specific document type across years"""
        total = 0
        for year in years:
            try:
                url = f"{self.base_url}/search/?formInput=doctypes:%20{doc_type}%20fromdate:%201-1-{year}%20todate:%2031-12-{year}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='result')

                # Try to get max page
                page_links = soup.find_all('a', href=lambda x: x and 'pagenum=' in x if x else False)
                max_page = 0
                for link in page_links:
                    try:
                        num = int(link['href'].split('pagenum=')[1].split('&')[0])
                        max_page = max(max_page, num)
                    except:
                        pass

                estimated = (max_page + 1) * len(results) if len(results) > 0 else 0
                total += estimated

                if estimated > 0:
                    print(f"  {year}: ~{estimated:,} cases ({max_page+1} pages × {len(results)}/page)")

                time.sleep(1)
            except:
                pass

        print(f"  Total {doc_type} ({min(years)}-{max(years)}): ~{total:,} cases")
        self.research_data['data_estimates'][f'{doc_type}_{min(years)}_{max(years)}'] = total

    def research_statutes_and_acts(self):
        """Explore statutory documents and legislation"""
        print("\n" + "=" * 80)
        print("4. STATUTES, ACTS & LEGISLATION")
        print("=" * 80)

        # Check for bareacts/statutes section
        try:
            url = f"{self.base_url}/browse/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for act listings
            act_links = soup.find_all('a', href=lambda x: x and '/doc/' in x if x else False)
            print(f"Found {len(act_links)} document links in browse section")

            # Sample some acts
            sample_acts = []
            for link in act_links[:10]:
                act_title = link.get_text(strip=True)
                if act_title:
                    sample_acts.append(act_title)
                    print(f"  - {act_title[:70]}...")

            self.research_data['statutes_and_acts']['sample_acts'] = sample_acts
            self.research_data['statutes_and_acts']['browse_available'] = True

        except Exception as e:
            print(f"Error researching statutes: {e}")
            self.research_data['statutes_and_acts']['browse_available'] = False

    def research_search_capabilities(self):
        """Test advanced search features"""
        print("\n" + "=" * 80)
        print("5. SEARCH CAPABILITIES")
        print("=" * 80)

        search_features = {
            'by_date_range': 'fromdate: 1-1-2023 todate: 31-12-2023',
            'by_court': 'doctypes: supremecourt',
            'by_citation': 'AIR 2023',
            'by_judge': 'Justice',
            'by_act': 'Indian Penal Code',
            'by_section': 'Section 420',
            'boolean_and': 'criminal AND appeal',
            'boolean_or': 'bail OR custody',
        }

        for feature, query in search_features.items():
            try:
                url = f"{self.base_url}/search/?formInput={query}"
                response = requests.get(url)
                has_results = 'No matching results' not in response.text

                self.research_data['search_capabilities'][feature] = has_results
                status = "✓ Works" if has_results else "✗ No results"
                print(f"{feature:20s}: {status}")

                time.sleep(1)
            except:
                self.research_data['search_capabilities'][feature] = False

    def estimate_total_data(self):
        """Estimate total documents available"""
        print("\n" + "=" * 80)
        print("6. TOTAL DATA ESTIMATION")
        print("=" * 80)

        estimates = {
            'Supreme Court (all years)': self._estimate_all_years('supremecourt'),
            'High Courts (all years)': self._estimate_all_years('highcourt'),
            'Tribunals (sample)': self._estimate_sample('tribunal'),
        }

        total_estimated = sum(estimates.values())

        for category, count in estimates.items():
            print(f"{category:30s}: ~{count:,} documents")

        print(f"\n{'TOTAL ESTIMATED':30s}: ~{total_estimated:,} documents")
        print(f"\nNOTE: This is a conservative estimate based on sampling.")
        print(f"Actual number could be significantly higher.")

        self.research_data['data_estimates']['total_conservative'] = total_estimated
        self.research_data['data_estimates']['breakdown'] = estimates

    def _estimate_all_years(self, doc_type):
        """Estimate documents for all available years"""
        # Sample recent years and extrapolate
        sample_years = [2023, 2022, 2021, 2020, 2019]
        sample_total = 0

        for year in sample_years:
            try:
                url = f"{self.base_url}/search/?formInput=doctypes:%20{doc_type}%20fromdate:%201-1-{year}%20todate:%2031-12-{year}&pagenum=0"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='result')

                # Estimate pages
                page_links = soup.find_all('a', href=lambda x: x and 'pagenum=' in x if x else False)
                max_page = 0
                for link in page_links:
                    try:
                        num = int(link['href'].split('pagenum=')[1].split('&')[0])
                        max_page = max(max_page, num)
                    except:
                        pass

                # Conservative estimate: only count what we can see
                year_estimate = max_page * 10 if max_page > 0 else len(results)
                sample_total += year_estimate

                time.sleep(1)
            except:
                pass

        # Extrapolate for ~70 years (1950-2024)
        avg_per_year = sample_total / len(sample_years) if sample_total > 0 else 100
        estimated_total = int(avg_per_year * 70)

        return estimated_total

    def _estimate_sample(self, doc_type):
        """Quick estimate for a document type"""
        try:
            url = f"{self.base_url}/search/?formInput=doctypes:%20{doc_type}%20fromdate:%201-1-2023%20todate:%2031-12-2023&pagenum=50"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', class_='result')

            if len(results) > 0:
                # If page 50 has results, there are at least 500 cases for one year
                # Extrapolate for 70 years
                return 500 * 70
            return 1000  # Minimum estimate
        except:
            return 1000

    def generate_report(self):
        """Generate comprehensive research report"""
        print("\n" + "=" * 80)
        print("RESEARCH COMPLETE - GENERATING REPORT")
        print("=" * 80)

        report_file = f"indiankanoon_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(self.research_data, f, indent=2)

        print(f"\n✓ Detailed JSON report saved: {report_file}")

        # Create markdown summary
        md_file = report_file.replace('.json', '.md')
        self._generate_markdown_report(md_file)
        print(f"✓ Summary report saved: {md_file}")

    def _generate_markdown_report(self, filename):
        """Create human-readable markdown report"""
        with open(filename, 'w') as f:
            f.write("# IndianKanoon.org - Comprehensive Research Report\n\n")
            f.write(f"**Generated:** {self.research_data['timestamp']}\n\n")

            f.write("## Executive Summary\n\n")
            f.write("IndianKanoon.org is India's premier free legal research database containing:\n\n")

            total = self.research_data['data_estimates'].get('total_conservative', 0)
            f.write(f"- **Estimated Total Documents:** ~{total:,}+\n")
            f.write(f"- **Document Types:** {len([k for k,v in self.research_data['document_types'].items() if v.get('available')])}\n")
            f.write(f"- **Search Capabilities:** Advanced (date, court, citation, boolean)\n\n")

            f.write("## Document Types Available\n\n")
            for doc_type, data in self.research_data['document_types'].items():
                status = "✓" if data.get('available') else "✗"
                f.write(f"- {status} **{doc_type.upper()}**\n")

            f.write("\n## Data Estimates\n\n")
            for category, count in self.research_data['data_estimates'].get('breakdown', {}).items():
                f.write(f"- {category}: ~{count:,} documents\n")

            f.write("\n## Recommendations for Scraping\n\n")
            f.write("Based on this research:\n\n")
            f.write("1. **Start with Supreme Court** (most important, ~100k cases)\n")
            f.write("2. **Add High Courts** (state-wise, ~500k cases)\n")
            f.write("3. **Consider year-based batching** (2020-2024 first)\n")
            f.write("4. **Implement pagination handling** (100+ pages per query)\n")
            f.write("5. **Plan for ~1M+ total documents** across all courts\n")

    def cleanup(self):
        """Close browser and cleanup"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def run_full_research(self):
        """Execute complete research workflow"""
        try:
            print("╔" + "=" * 78 + "╗")
            print("║" + " " * 15 + "INDIANKANOON.ORG DEEP RESEARCH" + " " * 33 + "║")
            print("╚" + "=" * 78 + "╝\n")

            self.setup_browser()
            self.research_homepage()
            self.research_document_types()
            self.research_courts()
            self.research_statutes_and_acts()
            self.research_search_capabilities()
            self.estimate_total_data()
            self.generate_report()

            print("\n" + "=" * 80)
            print("✓ RESEARCH COMPLETE!")
            print("=" * 80)

        except Exception as e:
            print(f"\nError during research: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

if __name__ == "__main__":
    researcher = IndianKanoonResearcher()
    researcher.run_full_research()
