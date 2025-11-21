"""
Bangladesh Laws Scraper - TIER 1
Primary legislation database from Ministry of Law, Justice and Parliamentary Affairs
Enhanced version of existing bdlaws scraper
"""

from bs4 import BeautifulSoup
import requests
import time
import logging
from typing import List, Dict, Optional, Any
import re
from urllib.parse import urljoin, urlparse
import os

from ..base_scraper import BaseLegalScraper, DocumentInfo, ScrapingResult

logger = logging.getLogger(__name__)


class BDLawsScraper(BaseLegalScraper):
    """
    Enhanced scraper for Bangladesh Laws website (bdlaws.minlaw.gov.bd)
    Primary source for Bangladesh legislation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://bdlaws.minlaw.gov.bd')
        self.act_list_url = urljoin(self.base_url, '/act-list')
        self.search_url = urljoin(self.base_url, '/search')
        self.pdf_download_path = config.get('pdf_download_path', '/download-pdf')

        # Enhanced selectors for BD Laws website
        self.selectors = {
            'act_list': '.act-item, .law-item, tr',
            'act_title': 'h3, .title, a',
            'act_link': 'a',
            'content_area': '.content, .main-content, .law-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'pagination': '.pagination a, .paging a',
            'search_results': '.search-result, .result-item'
        }

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of all available acts and laws
        """
        documents = []

        try:
            # Try to get acts by category first
            categories = ['acts', 'ordinances', 'codes', 'amendments']

            for category in categories:
                try:
                    category_url = f"{self.act_list_url}?category={category}"
                    response = self._make_request(category_url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        category_docs = self._parse_act_list(soup, category)
                        documents.extend(category_docs)

                        logger.info(f"Found {len(category_docs)} documents in {category} category")

                except Exception as e:
                    logger.warning(f"Failed to get {category} list: {e}")
                    continue

            # If no categories found, try general act list
            if not documents:
                try:
                    response = self._make_request(self.act_list_url)
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        documents = self._parse_act_list(soup, 'all')
                except Exception as e:
                    logger.error(f"Failed to get general act list: {e}")

            logger.info(f"Total documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting document list: {e}")
            return []

    def _parse_act_list(self, soup: BeautifulSoup, category: str) -> List[DocumentInfo]:
        """Parse the act list page to extract document information"""
        documents = []

        # Try different selectors for act items
        act_selectors = [
            'tr',  # Table rows
            '.act-item',
            '.law-item',
            '.result-item',
            'li'
        ]

        act_items = []
        for selector in act_selectors:
            items = soup.select(selector)
            if items and len(items) > 1:  # Found substantial content
                act_items = items
                break

        for item in act_items:
            try:
                # Extract title
                title_selectors = ['h3 a', '.title a', 'a', 'h3', '.title', 'td:first-child']
                title = ""
                title_element = None

                for selector in title_selectors:
                    element = item.select_one(selector)
                    if element:
                        title = element.get_text(strip=True)
                        if title:
                            title_element = element if element.name == 'a' else element.select_one('a')
                            break

                if not title or len(title) < 5:  # Skip if title is too short
                    continue

                # Extract URL
                url = ""
                if title_element and title_element.get('href'):
                    url = self._get_absolute_url(title_element['href'])
                elif item.select_one('a'):
                    url = self._get_absolute_url(item.select_one('a')['href'])

                # Determine document type
                doc_type = self._classify_document(title, category)

                # Extract date if available
                date = None
                date_selectors = ['.date', '.year', 'td:last-child', '.published']
                for selector in date_selectors:
                    date_element = item.select_one(selector)
                    if date_element:
                        date_text = date_element.get_text(strip=True)
                        date = self._parse_date(date_text)
                        break

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type=doc_type,
                    source=self.source_name,
                    date=date,
                    metadata={
                        'category': category,
                        'scraped_at': time.time()
                    }
                )

                documents.append(doc_info)

            except Exception as e:
                logger.warning(f"Error parsing act item: {e}")
                continue

        return documents

    def _classify_document(self, title: str, category: str) -> str:
        """Classify document type based on title and category"""
        title_lower = title.lower()

        if category == 'acts' or 'act' in title_lower:
            return 'act'
        elif category == 'ordinances' or 'ordinance' in title_lower:
            return 'ordinance'
        elif category == 'codes' or 'code' in title_lower:
            return 'code'
        elif 'amendment' in title_lower or 'amended' in title_lower:
            return 'amendment'
        elif 'order' in title_lower:
            return 'order'
        elif 'rule' in title_lower:
            return 'rule'
        elif 'regulation' in title_lower:
            return 'regulation'
        else:
            return 'legislation'

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific document page to extract content
        """
        if not doc_info.url:
            return None

        try:
            response = self._make_request(doc_info.url)
            if not response or response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract content
            content_selectors = [
                '.content',
                '.main-content',
                '.law-content',
                '#content',
                '.act-content',
                'main'
            ]

            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text('\n', strip=True)
                    break

            if not content:
                # Fallback to entire body text
                content = soup.get_text('\n', strip=True)

            # Extract PDF URL if available
            pdf_url = None
            pdf_selectors = [
                'a[href*="download"]',
                '.pdf-download',
                '.download-btn',
                'a[href*=".pdf"]'
            ]

            for selector in pdf_selectors:
                pdf_element = soup.select_one(selector)
                if pdf_element and pdf_element.get('href'):
                    pdf_url = self._get_absolute_url(pdf_element['href'])
                    break

            # Extract metadata
            metadata = {
                'title': doc_info.title,
                'url': doc_info.url,
                'doc_type': doc_info.doc_type,
                'source': doc_info.source,
                'date': doc_info.date,
                'pdf_url': pdf_url,
                'scraped_at': time.time(),
                'content_length': len(content)
            }

            # Add additional metadata from page
            self._extract_additional_metadata(soup, metadata)

            return {
                'content': content,
                'metadata': metadata,
                'pdf_url': pdf_url
            }

        except Exception as e:
            logger.error(f"Error scraping document {doc_info.url}: {e}")
            return None

    def _extract_additional_metadata(self, soup: BeautifulSoup, metadata: Dict[str, Any]):
        """Extract additional metadata from the document page"""
        try:
            # Extract act number
            act_number = None
            number_selectors = ['.act-number', '.number', '[data-act-number]']
            for selector in number_selectors:
                element = soup.select_one(selector)
                if element:
                    act_number = element.get_text(strip=True)
                    break

            if act_number:
                metadata['act_number'] = act_number

            # Extract year
            year = None
            year_selectors = ['.year', '.act-year', '[data-year]']
            for selector in year_selectors:
                element = soup.select_one(selector)
                if element:
                    year_text = element.get_text(strip=True)
                    if year_text.isdigit() and len(year_text) == 4:
                        year = year_text
                        break

            if year:
                metadata['year'] = year

            # Extract ministry/department
            ministry = None
            ministry_selectors = ['.ministry', '.department', '.authority']
            for selector in ministry_selectors:
                element = soup.select_one(selector)
                if element:
                    ministry = element.get_text(strip=True)
                    break

            if ministry:
                metadata['ministry'] = ministry

        except Exception as e:
            logger.warning(f"Error extracting additional metadata: {e}")

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search for documents matching a query
        """
        documents = []

        try:
            # Construct search URL
            search_params = {
                'q': query,
                'type': filters.get('doc_type', 'all'),
                'year': filters.get('year', ''),
                'category': filters.get('category', '')
            }

            search_url = f"{self.search_url}?" + "&".join([f"{k}={v}" for k, v in search_params.items() if v])

            response = self._make_request(search_url)
            if not response or response.status_code != 200:
                return documents

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse search results
            result_selectors = [
                '.search-result',
                '.result-item',
                '.search-item'
            ]

            results = []
            for selector in result_selectors:
                results = soup.select(selector)
                if results:
                    break

            for result in results:
                try:
                    # Extract title and link
                    title_element = result.select_one('a, h3, .title')
                    if not title_element:
                        continue

                    title = title_element.get_text(strip=True)
                    url = title_element.get('href') if title_element.name == 'a' else None

                    if url:
                        url = self._get_absolute_url(url)

                    # Extract snippet/description
                    snippet = ""
                    snippet_element = result.select_one('.snippet, .description, .abstract')
                    if snippet_element:
                        snippet = snippet_element.get_text(strip=True)

                    doc_info = DocumentInfo(
                        title=title,
                        url=url,
                        doc_type='search_result',
                        source=self.source_name,
                        content=snippet if snippet else None,
                        metadata={
                            'search_query': query,
                            'filters': filters
                        }
                    )

                    documents.append(doc_info)

                except Exception as e:
                    logger.warning(f"Error parsing search result: {e}")
                    continue

            logger.info(f"Found {len(documents)} search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download PDF document
        """
        try:
            if not pdf_url:
                # Try to find PDF URL from document page
                if doc_info.url:
                    doc_data = self.scrape_document(doc_info)
                    if doc_data and doc_data.get('pdf_url'):
                        pdf_url = doc_data['pdf_url']

                if not pdf_url:
                    logger.warning(f"No PDF URL found for {doc_info.title}")
                    return False

            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', doc_info.title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/bdlaws')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return False