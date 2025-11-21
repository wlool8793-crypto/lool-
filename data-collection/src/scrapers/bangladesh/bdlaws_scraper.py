"""
Bangladesh Laws Scraper
Scrapes legal documents from bdlaws.minlaw.gov.bd
"""

import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .base_scraper import BaseLegalScraper
from ..parsers.base_parser import BaseParser


class BangladeshLawsScraper(BaseLegalScraper):
    """Scraper for Bangladesh Laws (bdlaws.minlaw.gov.bd)"""

    def __init__(self, config: Dict[str, Any], database):
        super().__init__(config, database)

        # Bangladesh-specific settings
        self.indexes = config.get('indexes', {
            'chronological': '/laws-of-bangladesh-chronological-index.html',
            'alphabetical': '/laws-of-bangladesh-alphabetical-index.html'
        })

    def get_document_list(self) -> List[str]:
        """
        Get list of all law URLs from both chronological and alphabetical indexes.

        Returns:
            List of unique law URLs
        """
        all_urls = set()

        # Scrape chronological index
        self.logger.info("Scraping chronological index...")
        chron_url = urljoin(self.base_url, self.indexes['chronological'])
        chron_urls = self._scrape_index_page(chron_url)
        all_urls.update(chron_urls)
        self.logger.info(f"Found {len(chron_urls)} laws in chronological index")

        # Scrape alphabetical index
        self.logger.info("Scraping alphabetical index...")
        alpha_url = urljoin(self.base_url, self.indexes['alphabetical'])
        alpha_urls = self._scrape_index_page(alpha_url)
        all_urls.update(alpha_urls)
        self.logger.info(f"Found {len(alpha_urls)} laws in alphabetical index")

        # Convert set to sorted list
        urls_list = sorted(list(all_urls))
        self.logger.info(f"Total unique laws: {len(urls_list)}")

        return urls_list

    def _scrape_index_page(self, index_url: str) -> List[str]:
        """
        Scrape a single index page and extract all law URLs.

        Args:
            index_url: URL of the index page

        Returns:
            List of law URLs
        """
        urls = []

        try:
            # Fetch the index page
            html = self.fetch_page(index_url, use_selenium=False)
            if not html:
                self.logger.error(f"Failed to fetch index: {index_url}")
                return urls

            soup = BeautifulSoup(html, 'lxml')

            # Find all links that point to act pages
            # Pattern: act-XXX.html or similar
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']

                # Look for act/law page patterns
                if re.search(r'(act|law|ordinance)-\d+\.html', href, re.I):
                    full_url = urljoin(self.base_url, href)
                    urls.append(full_url)

            # Also look for links in tables (common structure)
            for table in soup.find_all('table'):
                for a_tag in table.find_all('a', href=True):
                    href = a_tag['href']
                    if 'act' in href.lower() or 'law' in href.lower():
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)

        except Exception as e:
            self.logger.error(f"Error scraping index {index_url}: {e}")

        return urls

    def parse_document(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse a Bangladesh law page and extract all information.

        Args:
            url: URL of the law page

        Returns:
            Dictionary containing law data
        """
        try:
            # Fetch the page
            html = self.fetch_page(url, use_selenium=False)
            if not html:
                return None

            soup = BeautifulSoup(html, 'lxml')

            # Extract basic information
            title = self._extract_title(soup)
            if not title:
                self.logger.warning(f"No title found for {url}")
                return None

            # Extract act ID from URL (e.g., "act-367" from /act-367.html)
            act_id = self._extract_act_id_from_url(url)

            # Extract other fields
            year = self._extract_year(soup, title)
            doc_type = self._extract_document_type(soup, title)
            act_number = self._extract_act_number(soup, title)
            ministry = self._extract_ministry(soup)

            # Extract content
            plain_text = self._extract_full_text(soup)
            summary = self._extract_summary(soup)

            # Look for PDF
            pdf_url = self.extract_pdf_url(html, url)

            # Save HTML to file
            html_path = self.save_html(html, act_id or 0)

            # Build document data
            doc_data = {
                'country': 'bangladesh',
                'country_doc_id': act_id,
                'title': title,
                'doc_type': doc_type,
                'year': year,
                'category': self._extract_category(soup),
                'court_or_ministry': ministry,
                'citation': act_number,
                'source_url': url,
                'source_site': 'bdlaws.minlaw.gov.bd',
                'source_index': self._determine_source_index(url),
                'html_content': html,
                'plain_text': plain_text,
                'summary': summary,
                'pdf_url': pdf_url,
                'status': 'active',  # Assume active unless stated otherwise
                'metadata': self.extract_metadata(html, url)
            }

            return doc_data

        except Exception as e:
            self.logger.error(f"Error parsing document {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract law title from page"""
        # PRIORITY 1: Extract from <title> tag (most reliable for bdlaws.minlaw.gov.bd)
        title_tag = soup.find('title')
        if title_tag:
            title = BaseParser.clean_text(title_tag.get_text())
            # Clean up common suffixes
            title = title.replace(' - Laws of Bangladesh', '').strip()
            title = title.replace(' | Laws of Bangladesh', '').strip()
            # Accept both English AND Bengali titles
            # Bengali keywords: আইন (Act), অধ্যাদেশ (Ordinance), বিধি (Rule)
            if title and 10 < len(title) < 300:
                english_keywords = ['Act', 'Ordinance', 'Code', 'Regulation', 'Order', 'Rules']
                bengali_keywords = ['আইন', 'অধ্যাদেশ', 'বিধি']
                has_keyword = any(kw in title for kw in english_keywords + bengali_keywords)
                if has_keyword or len(title) > 20:  # Accept longer titles even without keyword
                    return title

        # PRIORITY 2: Try h1/h2 headers
        for selector in ['h1', 'h2']:
            element = soup.select_one(selector)
            if element:
                title = BaseParser.clean_text(element.get_text())
                if title and 10 < len(title) < 300 and ('Act' in title or 'Ordinance' in title):
                    return title

        # PRIORITY 3: Look for specific patterns in paragraphs
        for tag in ['h3', 'p', 'div']:
            for element in soup.find_all(tag):
                text = element.get_text()
                # Match patterns like "The XYZ Act, 1860" or "XYZ Ordinance, 1969"
                if re.search(r'(The\s+)?[\w\s]+\s+(Act|Ordinance|Code|Regulation),?\s+\d{4}', text, re.I):
                    title = BaseParser.clean_text(text)
                    if 15 < len(title) < 300:
                        return title

        return None

    def _extract_act_id_from_url(self, url: str) -> Optional[str]:
        """Extract act ID from URL (e.g., 'act-367' from /act-367.html)"""
        match = re.search(r'/(act|law|ordinance)-(\d+)', url, re.I)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        return None

    def _extract_year(self, soup: BeautifulSoup, title: str) -> Optional[int]:
        """Extract year from title or content"""
        # PRIORITY 1: Extract from title using regex
        if title:
            # Match 4-digit years (1700-2099)
            year_match = re.search(r'\b(1[7-9]\d{2}|20\d{2})\b', title)
            if year_match:
                return int(year_match.group(1))

        # PRIORITY 2: Use BaseParser
        year = BaseParser.extract_year(title) if title else None
        if year:
            return year

        # PRIORITY 3: Look in the page content
        for tag in ['p', 'div', 'span', 'h1', 'h2']:
            for element in soup.find_all(tag):
                text = element.get_text()
                year_match = re.search(r'\b(1[7-9]\d{2}|20\d{2})\b', text)
                if year_match:
                    return int(year_match.group(1))

        return None

    def _extract_document_type(self, soup: BeautifulSoup, title: str) -> str:
        """Determine document type (Act, Ordinance, etc.)"""
        text = title.lower()

        if 'ordinance' in text:
            return 'Ordinance'
        elif 'act' in text:
            return 'Act'
        elif 'order' in text:
            return 'Presidential Order'
        elif 'code' in text:
            return 'Code'
        elif 'regulation' in text:
            return 'Regulation'
        else:
            return 'Law'

    def _extract_act_number(self, soup: BeautifulSoup, title: str) -> Optional[str]:
        """Extract act number/citation"""
        # Look for patterns like "Act No. 123" or "Act XLII of 1973"
        patterns = [
            r'Act\s+(No\.|Number)?\s*(\d+|[IVXLCDM]+)',
            r'Ordinance\s+(No\.|Number)?\s*(\d+|[IVXLCDM]+)',
            r'Act\s+([IVXLCDM]+)\s+of\s+(\d{4})'
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.I)
            if match:
                return BaseParser.clean_text(match.group(0))

        return None

    def _extract_ministry(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract responsible ministry"""
        # Look for ministry mentions
        keywords = ['ministry', 'minister', 'department']

        for tag in soup.find_all(['p', 'div', 'span']):
            text = tag.get_text().lower()
            if any(keyword in text for keyword in keywords):
                ministry_text = BaseParser.clean_text(tag.get_text())
                if 10 < len(ministry_text) < 100:
                    return ministry_text

        return None

    def _extract_full_text(self, soup: BeautifulSoup) -> str:
        """Extract full text content of the law"""
        # Remove script, style, nav elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()

        # Get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')

        if main_content:
            return BaseParser.html_to_text(str(main_content))

        return BaseParser.html_to_text(str(soup))

    def _extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract summary or preamble"""
        # Look for common summary indicators
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text().lower()
            if 'whereas' in text or 'preamble' in text or 'short title' in text:
                summary = BaseParser.clean_text(tag.get_text())
                if 50 < len(summary) < 500:
                    return summary

        # Fallback: first substantial paragraph
        for p in soup.find_all('p'):
            text = BaseParser.clean_text(p.get_text())
            if len(text) > 100:
                return text[:500]  # First 500 characters

        return None

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract subject category/topic"""
        # Look for category indicators
        for tag in soup.find_all(['meta', 'span', 'div']):
            if 'category' in str(tag.get('class', [])).lower():
                return BaseParser.clean_text(tag.get_text())

            if tag.get('name') == 'keywords':
                return tag.get('content')

        return None

    def _determine_source_index(self, url: str) -> str:
        """Determine which index the URL likely came from"""
        if 'chronological' in url:
            return 'chronological'
        elif 'alphabetical' in url:
            return 'alphabetical'
        else:
            return 'direct'

    def extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract Bangladesh-specific metadata.

        Args:
            html: HTML content
            url: Page URL

        Returns:
            Dictionary of metadata
        """
        soup = BeautifulSoup(html, 'lxml')
        metadata = {}

        # Extract meta tags
        meta_tags = BaseParser.extract_meta_tags(html)
        metadata.update(meta_tags)

        # Look for specific Bangladesh law metadata
        # (This would be customized based on actual site structure)

        return metadata


if __name__ == "__main__":
    # Test the Bangladesh scraper
    from src.unified_database import UnifiedDatabase

    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': 2,
        'use_selenium': False,
        'headless': True,
        'download_pdfs': True,
        'pdf_dir': './data/pdfs/bangladesh',
        'html_dir': './data/html/bangladesh',
        'indexes': {
            'chronological': '/laws-of-bangladesh-chronological-index.html',
            'alphabetical': '/laws-of-bangladesh-alphabetical-index.html'
        }
    }

    db = UnifiedDatabase()
    scraper = BangladeshLawsScraper(config, db)

    # Test getting document list
    print("Testing document list retrieval...")
    urls = scraper.get_document_list()
    print(f"Found {len(urls)} laws")

    if urls:
        print(f"\nTesting document parsing on first URL: {urls[0]}")
        doc_data = scraper.parse_document(urls[0])
        if doc_data:
            print(f"Title: {doc_data.get('title')}")
            print(f"Year: {doc_data.get('year')}")
            print(f"Type: {doc_data.get('doc_type')}")
