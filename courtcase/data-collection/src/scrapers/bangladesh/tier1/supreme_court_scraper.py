"""
Supreme Court of Bangladesh Scraper - TIER 1
Supreme Court judgments, orders, and notices
"""

from bs4 import BeautifulSoup
import requests
import time
import logging
from typing import List, Dict, Optional, Any
import re
from urllib.parse import urljoin, urlparse
import os
from datetime import datetime

from ..base_scraper import BaseLegalScraper, DocumentInfo, ScrapingResult

logger = logging.getLogger(__name__)


class SupremeCourtScraper(BaseLegalScraper):
    """
    Scraper for Supreme Court of Bangladesh website
    Covers Appellate Division and High Court Division judgments
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://supremecourt.gov.bd')
        self.judgments_path = config.get('judgments_path', '/judgments')
        self.orders_path = config.get('orders_path', '/orders')
        self.notices_path = config.get('notices_path', '/notices')

        # Enhanced selectors for Supreme Court website
        self.selectors = {
            'judgment_list': '.judgment-item, .case-item, tr',
            'case_title': 'h3, .title, a',
            'case_link': 'a',
            'content_area': '.judgment-content, .content, .main-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'pagination': '.pagination a, .paging a',
            'case_info': '.case-info, .metadata, .header'
        }

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of available Supreme Court judgments and orders
        """
        documents = []

        try:
            # Get different document types
            document_types = [
                ('judgments', 'judgment'),
                ('orders', 'order'),
                ('notices', 'notice')
            ]

            for doc_type, doc_class in document_types:
                try:
                    path = f"/{doc_type}"
                    url = urljoin(self.base_url, path)
                    response = self._make_request(url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        type_docs = self._parse_document_list(soup, doc_class)
                        documents.extend(type_docs)

                        logger.info(f"Found {len(type_docs)} {doc_type}")

                except Exception as e:
                    logger.warning(f"Failed to get {doc_type}: {e}")
                    continue

            # Try to get by division (Appellate and High Court)
            divisions = ['appellate', 'high-court']
            for division in divisions:
                try:
                    path = f"/{division}/judgments"
                    url = urljoin(self.base_url, path)
                    response = self._make_request(url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        div_docs = self._parse_document_list(soup, 'judgment')

                        # Add division info to metadata
                        for doc in div_docs:
                            doc.metadata['division'] = division

                        documents.extend(div_docs)

                        logger.info(f"Found {len(div_docs)} judgments for {division} division")

                except Exception as e:
                    logger.warning(f"Failed to get {division} division judgments: {e}")
                    continue

            logger.info(f"Total Supreme Court documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting Supreme Court document list: {e}")
            return []

    def _parse_document_list(self, soup: BeautifulSoup, doc_class: str) -> List[DocumentInfo]:
        """Parse document list page to extract case information"""
        documents = []

        # Try different selectors for case items
        case_selectors = [
            'tr',  # Table rows
            '.judgment-item',
            '.case-item',
            '.result-item',
            'li'
        ]

        case_items = []
        for selector in case_selectors:
            items = soup.select(selector)
            if items and len(items) > 1:  # Found substantial content
                case_items = items
                break

        for item in case_items:
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

                # Extract case number if available
                case_number = self._extract_case_number(title)

                # Extract date if available
                date = None
                date_selectors = ['.date', '.year', '.judgment-date', 'td:last-child', '.published']
                for selector in date_selectors:
                    date_element = item.select_one(selector)
                    if date_element:
                        date_text = date_element.get_text(strip=True)
                        date = self._parse_date(date_text)
                        break

                # Extract judges if available
                judges = self._extract_judges(item)

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type=doc_class,
                    source=self.source_name,
                    date=date,
                    metadata={
                        'case_number': case_number,
                        'judges': judges,
                        'court': 'Supreme Court of Bangladesh',
                        'scraped_at': time.time()
                    }
                )

                documents.append(doc_info)

            except Exception as e:
                logger.warning(f"Error parsing case item: {e}")
                continue

        return documents

    def _extract_case_number(self, title: str) -> Optional[str]:
        """Extract case number from title"""
        # Common patterns for Bangladeshi case numbers
        patterns = [
            r'Writ\s+Petition\s+No\.\s*(\d+/\d+)',
            r'Civil\s+Appeal\s+No\.\s*(\d+/\d+)',
            r'Criminal\s+Appeal\s+No\.\s*(\d+/\d+)',
            r'Section\s+302\s*Case\s+No\.\s*(\d+)',
            r'Case\s+No\.\s*(\d+/\d+)',
            r'(\d{4}/\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        return None

    def _extract_judges(self, item_element) -> List[str]:
        """Extract judge names from case item"""
        judges = []

        judge_selectors = [
            '.judges',
            '.bench',
            '.coram',
            '.judge-name'
        ]

        for selector in judge_selectors:
            element = item_element.select_one(selector)
            if element:
                judges_text = element.get_text(strip=True)
                # Split by common separators
                judges = re.split(r'[,&;]|\s+and\s+', judges_text)
                judges = [j.strip() for j in judges if j.strip()]
                break

        return judges

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific Supreme Court document
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
                '.judgment-content',
                '.content',
                '.main-content',
                '.decision-text',
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

            # Extract case details
            case_details = self._extract_case_details(soup)

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
                'court': 'Supreme Court of Bangladesh',
                **case_details
            }

            return {
                'content': content,
                'metadata': metadata,
                'pdf_url': pdf_url
            }

        except Exception as e:
            logger.error(f"Error scraping Supreme Court document {doc_info.url}: {e}")
            return None

    def _extract_case_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed case information from the document page"""
        details = {}

        try:
            # Extract case number
            case_number = None
            number_patterns = [
                r'Writ\s+Petition\s+No\.\s*(\d+/\d+)',
                r'Civil\s+Appeal\s+No\.\s*(\d+/\d+)',
                r'Criminal\s+Appeal\s+No\.\s*(\d+/\d+)',
                r'Case\s+No\.\s*(\d+/\d+)'
            ]

            page_text = soup.get_text()
            for pattern in number_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['case_number'] = match.group(1) if match.groups() else match.group(0)
                    break

            # Extract judges
            judge_patterns = [
                r'(?i)Hon[\'’]ble\s+(?:Justice\s+|Justices?\s+)(.+?)(?:\n|$)',
                r'(?i)J[\.]\s+(.+?)(?:\n|$)',
                r'(?i)Bench:\s*(.+?)(?:\n|$)',
            ]

            judges = []
            for pattern in judge_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    judges.extend(matches)
                    break

            if judges:
                details['judges'] = judges

            # Extract decision date
            date_patterns = [
                r'Date\s*of\s*Decision:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Decided\s*on:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ]

            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    details['decision_date'] = self._parse_date(match.group(1))
                    break

            # Extract division
            if 'appellate' in page_text.lower():
                details['division'] = 'Appellate Division'
            elif 'high court' in page_text.lower():
                details['division'] = 'High Court Division'

            # Extract parties
            parties_match = re.search(r'(.+?)\s*vs\.?\s*(.+?)(?:\n|$)', page_text)
            if parties_match:
                details['petitioner'] = parties_match.group(1).strip()
                details['respondent'] = parties_match.group(2).strip()

        except Exception as e:
            logger.warning(f"Error extracting case details: {e}")

        return details

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search Supreme Court documents
        """
        documents = []

        try:
            # Build search query
            search_params = {
                'q': query,
                'type': filters.get('doc_type', ''),
                'year': filters.get('year', ''),
                'division': filters.get('division', '')
            }

            # Try search endpoint
            search_url = f"{self.base_url}/search"
            response = self._make_request(search_url, params=search_params)

            if not response or response.status_code != 200:
                # Fallback: return all documents and filter by keyword
                all_docs = self.get_document_list()
                filtered_docs = [doc for doc in all_docs if
                                query.lower() in doc.title.lower() or
                                (doc.metadata.get('case_number') and query.lower() in doc.metadata['case_number'].lower())]
                return filtered_docs

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse search results
            result_selectors = [
                '.search-result',
                '.result-item',
                '.case-item'
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

            logger.info(f"Found {len(documents)} Supreme Court search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching Supreme Court documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download Supreme Court document PDF
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

            # Add case number to filename if available
            case_number = doc_info.metadata.get('case_number', '')
            if case_number:
                filename = f"{self.source_name}_{case_number}_{safe_title}.pdf"
            else:
                filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/supreme_court')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading Supreme Court PDF: {e}")
            return False