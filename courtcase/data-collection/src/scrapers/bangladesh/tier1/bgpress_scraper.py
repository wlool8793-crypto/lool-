"""
Bangladesh Gazette Scraper - TIER 1
Bangladesh Gazette - official government publications and notifications
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


class BgpressScraper(BaseLegalScraper):
    """
    Scraper for Bangladesh Gazette website (bgpress.gov.bd)
    Official government publications, extraordinary gazettes, and legal notifications
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://bgpress.gov.bd')
        self.gazette_path = config.get('gazette_path', '/gazette')
        self.archives_path = config.get('archives_path', '/archives')

        # Enhanced selectors for Bangladesh Gazette
        self.selectors = {
            'gazette_list': '.gazette-item, .publication-item, tr',
            'gazette_title': 'h3, .title, a',
            'gazette_link': 'a',
            'content_area': '.content, .main-content, .gazette-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'gazette_type': '.type, .gazette-type, .category',
            'publication_date': '.date, .published, .publication-date'
        }

        # Gazette types for Bangladesh Gazette
        self.gazette_types = [
            'extraordinary',
            'regular',
            'government',
            'presidential',
            'parliamentary',
            'notifications',
            'acts',
            'ordinances',
            'rules',
            'regulations'
        ]

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of available gazettes and publications
        """
        documents = []

        try:
            # Get gazettes by type
            for gazette_type in self.gazette_types:
                try:
                    type_url = urljoin(self.base_url, f"/{gazette_type}")
                    response = self._make_request(type_url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        type_docs = self._parse_gazette_list(soup, gazette_type)
                        documents.extend(type_docs)

                        logger.info(f"Found {len(type_docs)} {gazette_type} gazettes")

                except Exception as e:
                    logger.warning(f"Failed to get {gazette_type} gazettes: {e}")
                    continue

            # Try general gazette section
            try:
                gazette_url = urljoin(self.base_url, self.gazette_path)
                response = self._make_request(gazette_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    general_docs = self._parse_gazette_list(soup, 'general')
                    documents.extend(general_docs)

                    logger.info(f"Found {len(general_docs)} general gazettes")

            except Exception as e:
                logger.warning(f"Failed to get general gazettes: {e}")

            # Try archives section
            try:
                archives_url = urljoin(self.base_url, self.archives_path)
                response = self._make_request(archives_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    archive_docs = self._parse_gazette_list(soup, 'archive')
                    documents.extend(archive_docs)

                    logger.info(f"Found {len(archive_docs)} archive gazettes")

            except Exception as e:
                logger.warning(f"Failed to get archive gazettes: {e}")

            # Try to get recent gazettes
            try:
                recent_url = urljoin(self.base_url, '/recent')
                response = self._make_request(recent_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    recent_docs = self._parse_gazette_list(soup, 'recent')
                    documents.extend(recent_docs)

                    logger.info(f"Found {len(recent_docs)} recent gazettes")

            except Exception as e:
                logger.warning(f"Failed to get recent gazettes: {e}")

            # Try to get gazettes by year
            current_year = time.strftime('%Y')
            for year in range(int(current_year), int(current_year) - 5, -1):
                try:
                    year_url = urljoin(self.base_url, f"/gazette/{year}")
                    response = self._make_request(year_url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        year_docs = self._parse_gazette_list(soup, f'year_{year}')
                        documents.extend(year_docs)

                        logger.info(f"Found {len(year_docs)} gazettes for year {year}")

                except Exception as e:
                    logger.warning(f"Failed to get gazettes for year {year}: {e}")
                    continue

            logger.info(f"Total Bangladesh Gazette documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting Bangladesh Gazette document list: {e}")
            return []

    def _parse_gazette_list(self, soup: BeautifulSoup, gazette_type: str) -> List[DocumentInfo]:
        """Parse gazette list page to extract gazette information"""
        documents = []

        # Try different selectors for gazette items
        gazette_selectors = [
            'tr',  # Table rows
            '.gazette-item',
            '.publication-item',
            '.result-item',
            'li'
        ]

        gazette_items = []
        for selector in gazette_selectors:
            items = soup.select(selector)
            if items and len(items) > 1:  # Found substantial content
                gazette_items = items
                break

        for item in gazette_items:
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

                # Determine gazette type
                doc_type = self._classify_gazette(title, gazette_type)

                # Extract date if available
                date = self._extract_date_from_item(item)

                # Extract gazette number/identifier
                gazette_number = self._extract_gazette_number(title, item)

                # Extract gazette details
                gazette_details = self._extract_gazette_details_from_item(item, title)

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type=doc_type,
                    source=self.source_name,
                    date=date,
                    metadata={
                        'gazette_type': gazette_type,
                        'gazette_number': gazette_number,
                        **gazette_details,
                        'scraped_at': time.time()
                    }
                )

                documents.append(doc_info)

            except Exception as e:
                logger.warning(f"Error parsing gazette item: {e}")
                continue

        return documents

    def _classify_gazette(self, title: str, category: str) -> str:
        """Classify gazette type based on title and category"""
        title_lower = title.lower()

        # Check for specific gazette types
        if 'extraordinary' in title_lower or 's.o.' in title_lower:
            return 'extraordinary_gazette'
        elif 'regular' in title_lower:
            return 'regular_gazette'
        elif 'act' in title_lower:
            return 'act_gazette'
        elif 'ordinance' in title_lower:
            return 'ordinance_gazette'
        elif 'rule' in title_lower or 'rules' in title_lower:
            return 'rules_gazette'
        elif 'regulation' in title_lower or 'regulations' in title_lower:
            return 'regulations_gazette'
        elif 'amendment' in title_lower:
            return 'amendment_gazette'
        elif 'presidential' in title_lower:
            return 'presidential_gazette'
        elif 'parliamentary' in title_lower:
            return 'parliamentary_gazette'
        elif 'notification' in title_lower:
            return 'notification_gazette'
        elif 'appointment' in title_lower:
            return 'appointment_gazette'
        elif 'transfer' in title_lower or 'posting' in title_lower:
            return 'transfer_gazette'
        else:
            return category.replace('_', '_gazette')

    def _extract_date_from_item(self, item_element) -> Optional[str]:
        """Extract publication date from list item"""
        date_selectors = [
            '.date',
            '.published',
            '.publication-date',
            '.issue-date',
            'td:last-child',
            '.date-text',
            '.gazette-date'
        ]

        for selector in date_selectors:
            date_element = item_element.select_one(selector)
            if date_element:
                date_text = date_element.get_text(strip=True)
                date = self._parse_date(date_text)
                if date:
                    return date

        return None

    def _extract_gazette_number(self, title: str, item_element) -> Optional[str]:
        """Extract gazette number/identifier"""
        # Try to extract from title first
        patterns = [
            r'No\.?\s*(\d+)',
            r'S\.?\s*No\.?\s*(\d+)',
            r'(\d{4}/\d+)',
            r'Gazette\s*No\.?\s*(\d+)',
            r'Volume\s*(\d+)',
            r'Part\s*([IVX]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        # Try to extract from item element
        number_selectors = [
            '.gazette-number',
            '.issue-number',
            '.serial-no',
            '.volume',
            '.part'
        ]

        for selector in number_selectors:
            element = item_element.select_one(selector)
            if element:
                number_text = element.get_text(strip=True)
                if number_text:
                    return number_text

        return None

    def _extract_gazette_details_from_item(self, item_element, title: str) -> Dict[str, Any]:
        """Extract additional gazette details from list item"""
        details = {}

        try:
            # Extract gazette type indicator
            type_selectors = [
                '.gazette-type',
                '.type',
                '.category',
                '.classification'
            ]

            for selector in type_selectors:
                element = item_element.select_one(selector)
                if element:
                    details['gazette_category'] = element.get_text(strip=True)
                    break

            # Extract volume/part information
            volume_part_selectors = [
                '.volume',
                '.part',
                '.section'
            ]

            for selector in volume_part_selectors:
                element = item_element.select_one(selector)
                if element:
                    details[selector.replace('.', '')] = element.get_text(strip=True)

            # Extract ministry/department if available
            ministry_selectors = [
                '.ministry',
                '.department',
                '.directorate',
                '.office'
            ]

            for selector in ministry_selectors:
                element = item_element.select_one(selector)
                if element:
                    details['issuing_office'] = element.get_text(strip=True)
                    break

            # Check if PDF is available
            pdf_element = item_element.select_one('a[href*="pdf"], .pdf-link')
            if pdf_element:
                details['pdf_available'] = True

        except Exception as e:
            logger.warning(f"Error extracting gazette details: {e}")

        return details

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific Bangladesh Gazette document
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
                '.gazette-content',
                '.publication-content',
                '#content',
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

            # Extract gazette details
            gazette_details = self._extract_gazette_page_details(soup)

            # Update metadata
            metadata = {
                'title': doc_info.title,
                'url': doc_info.url,
                'doc_type': doc_info.doc_type,
                'source': doc_info.source,
                'date': doc_info.date,
                'pdf_url': pdf_url,
                'scraped_at': time.time(),
                'content_length': len(content),
                **gazette_details
            }

            # Preserve existing metadata
            metadata.update(doc_info.metadata)

            return {
                'content': content,
                'metadata': metadata,
                'pdf_url': pdf_url
            }

        except Exception as e:
            logger.error(f"Error scraping Bangladesh Gazette document {doc_info.url}: {e}")
            return None

    def _extract_gazette_page_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed gazette information from the document page"""
        details = {}

        try:
            page_text = soup.get_text()

            # Extract gazette number
            gazette_patterns = [
                r'Bangladesh Gazette\s*[^:]*:\s*(.+?)(?:\n|$)',
                r'Government Gazette\s*No\.?\s*(\d+)',
                r'Extraordinary Gazette\s*No\.?\s*(\d+)',
                r'S\.?\s*No\.?\s*(\d+)'
            ]

            for pattern in gazette_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['gazette_reference'] = match.group(1) if match.groups() else match.group(0)
                    break

            # Extract publication details
            pub_patterns = [
                r'Published?\s*by:\s*(.+?)(?:\n|$)',
                r'Printed by:\s*(.+?)(?:\n|$)',
                r'Published at:\s*(.+?)(?:\n|$)'
            ]

            for pattern in pub_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['publication_details'] = match.group(1).strip()
                    break

            # Extract date details
            date_patterns = [
                r'Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Published?\s*on:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ]

            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    details['publication_date'] = self._parse_date(match.group(1))
                    break

            # Extract government notifications
            notification_patterns = [
                r'S\.?\s*O\.?\s*([A-Z0-9\-/]+)',
                r'Notification\s*No\.?\s*(\d+)',
                r'Order\s*No\.?\s*(\d+)'
            ]

            notifications = []
            for pattern in notification_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    notifications.extend(matches)

            if notifications:
                details['notifications'] = notifications

            # Extract effective date
            effective_patterns = [
                r'Effective?\s*from:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Shall come into force on (\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Commences from (\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ]

            for pattern in effective_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['effective_date'] = self._parse_date(match.group(1))
                    break

        except Exception as e:
            logger.warning(f"Error extracting gazette page details: {e}")

        return details

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search Bangladesh Gazette documents
        """
        documents = []

        try:
            # Build search parameters
            search_params = {
                'q': query,
                'type': filters.get('gazette_type', ''),
                'year': filters.get('year', ''),
                'category': filters.get('category', '')
            }

            # Try search endpoint
            search_url = urljoin(self.base_url, '/search')
            response = self._make_request(search_url, params=search_params)

            if not response or response.status_code != 200:
                # Fallback: get all documents and filter
                all_docs = self.get_document_list()
                filtered_docs = [doc for doc in all_docs if
                                query.lower() in doc.title.lower() or
                                (doc.metadata.get('gazette_number') and query.lower() in doc.metadata['gazette_number'].lower())]
                return filtered_docs

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse search results
            result_selectors = [
                '.search-result',
                '.result-item',
                '.gazette-item'
            ]

            results = []
            for selector in result_selectors:
                results = soup.select(selector)
                if results:
                    break

            for result in results:
                try:
                    title_element = result.select_one('a, h3, .title')
                    if not title_element:
                        continue

                    title = title_element.get_text(strip=True)
                    url = title_element.get('href') if title_element.name == 'a' else None

                    if url:
                        url = self._get_absolute_url(url)

                    doc_info = DocumentInfo(
                        title=title,
                        url=url,
                        doc_type='search_result',
                        source=self.source_name,
                        metadata={
                            'search_query': query,
                            'filters': filters
                        }
                    )

                    documents.append(doc_info)

                except Exception as e:
                    logger.warning(f"Error parsing search result: {e}")
                    continue

            logger.info(f"Found {len(documents)} Bangladesh Gazette search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching Bangladesh Gazette documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download Bangladesh Gazette PDF
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

            # Add gazette number and date to filename
            gazette_number = doc_info.metadata.get('gazette_number', '')
            date = doc_info.date or ''

            if gazette_number and date:
                filename = f"{self.source_name}_{date}_{gazette_number}_{safe_title}.pdf"
            elif gazette_number:
                filename = f"{self.source_name}_{gazette_number}_{safe_title}.pdf"
            else:
                filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/bgpress')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading Bangladesh Gazette PDF: {e}")
            return False