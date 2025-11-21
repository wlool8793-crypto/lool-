"""
Bangladesh Judiciary Portal Scraper - TIER 1
Bangladesh Judiciary portal with case information and court decisions
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


class JudiciaryPortalScraper(BaseLegalScraper):
    """
    Scraper for Bangladesh Judiciary Portal website
    Covers district courts, sessions courts, and subordinate judiciary decisions
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://judiciary.gov.bd')
        self.case_search_path = config.get('case_search_path', '/case-search')
        self.judgments_path = config.get('judgments_path', '/judgments')
        self.court_hierarchy_path = config.get('court_hierarchy_path', '/courts')

        # Enhanced selectors for Judiciary Portal
        self.selectors = {
            'case_list': '.case-item, .result-item, tr',
            'case_title': 'h3, .title, a',
            'case_link': 'a',
            'content_area': '.case-content, .content, .main-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'court_info': '.court-info, .district-info, .bench-info',
            'search_form': '.search-form, form'
        }

        # Court hierarchy for better organization
        self.court_types = [
            'district_court',
            'sessions_court',
            'magistrate_court',
            'family_court',
            'labor_court',
            'metropolitan_court'
        ]

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of available cases and judgments from district courts
        """
        documents = []

        try:
            # Get documents by court type
            for court_type in self.court_types:
                try:
                    path = f"/{court_type.replace('_', '-')}/judgments"
                    url = urljoin(self.base_url, path)
                    response = self._make_request(url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        court_docs = self._parse_case_list(soup, court_type)
                        documents.extend(court_docs)

                        logger.info(f"Found {len(court_docs)} documents for {court_type}")

                except Exception as e:
                    logger.warning(f"Failed to get {court_type} judgments: {e}")
                    continue

            # Try general judgments section
            try:
                judgments_url = urljoin(self.base_url, self.judgments_path)
                response = self._make_request(judgments_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    general_docs = self._parse_case_list(soup, 'general')
                    documents.extend(general_docs)

                    logger.info(f"Found {len(general_docs)} general judgments")

            except Exception as e:
                logger.warning(f"Failed to get general judgments: {e}")

            # Try recent cases
            try:
                recent_url = urljoin(self.base_url, '/recent-cases')
                response = self._make_request(recent_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    recent_docs = self._parse_case_list(soup, 'recent')
                    documents.extend(recent_docs)

                    logger.info(f"Found {len(recent_docs)} recent cases")

            except Exception as e:
                logger.warning(f"Failed to get recent cases: {e}")

            logger.info(f"Total Judiciary Portal documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting Judiciary Portal document list: {e}")
            return []

    def _parse_case_list(self, soup: BeautifulSoup, court_type: str) -> List[DocumentInfo]:
        """Parse case list page to extract case information"""
        documents = []

        # Try different selectors for case items
        case_selectors = [
            'tr',  # Table rows
            '.case-item',
            '.result-item',
            '.judgment-item',
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

                # Extract case number
                case_number = self._extract_case_number(title)

                # Extract date if available
                date = None
                date_selectors = ['.date', '.year', '.decision-date', 'td:last-child', '.published']
                for selector in date_selectors:
                    date_element = item.select_one(selector)
                    if date_element:
                        date_text = date_element.get_text(strip=True)
                        date = self._parse_date(date_text)
                        break

                # Extract court information
                court_name = self._extract_court_name(item, title, court_type)

                # Extract case type
                case_type = self._classify_case_type(title)

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type=case_type,
                    source=self.source_name,
                    date=date,
                    metadata={
                        'case_number': case_number,
                        'court_name': court_name,
                        'court_type': court_type,
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
        # Common patterns for district court case numbers
        patterns = [
            r'Case\s+No\.\s*(\d+/\d+)',
            r'Cr\.?\s*Case\s*No\.\s*(\d+/\d+)',
            r'C\.R\.?\s*Case\s*No\.\s*(\d+/\d+)',
            r'Civil\s+Suit\s*No\.\s*(\d+/\d+)',
            r'Criminal\s+Case\s*No\.\s*(\d+/\d+)',
            r'(\d{4}/\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        return None

    def _extract_court_name(self, item_element, title: str, court_type: str) -> str:
        """Extract court name from item or title"""
        # First try to find explicit court name in item
        court_selectors = ['.court', '.district', '.bench', '.court-name']
        for selector in court_selectors:
            element = item_element.select_one(selector)
            if element:
                court_name = element.get_text(strip=True)
                if court_name:
                    return court_name

        # Try to extract from title
        title_lower = title.lower()
        if 'dhaka' in title_lower:
            if 'metropolitan' in title_lower:
                return 'Dhaka Metropolitan Court'
            else:
                return 'Dhaka District Court'
        elif 'chattogram' in title_lower or 'chittagong' in title_lower:
            if 'metropolitan' in title_lower:
                return 'Chattogram Metropolitan Court'
            else:
                return 'Chattogram District Court'
        elif 'rajshahi' in title_lower:
            return 'Rajshahi District Court'
        elif 'khulna' in title_lower:
            return 'Khulna District Court'
        elif 'sylhet' in title_lower:
            return 'Sylhet District Court'
        elif 'barishal' in title_lower or 'barisal' in title_lower:
            return 'Barishal District Court'
        elif 'rangpur' in title_lower:
            return 'Rangpur District Court'
        elif 'mymensingh' in title_lower:
            return 'Mymensingh District Court'

        # Return default based on court_type
        return court_type.replace('_', ' ').title()

    def _classify_case_type(self, title: str) -> str:
        """Classify case type based on title content"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['cr', 'criminal', 'section 302', 'murder', 'theft']):
            return 'criminal_case'
        elif any(word in title_lower for word in ['civil suit', 'civil case', 'injunction', 'specific performance']):
            return 'civil_case'
        elif any(word in title_lower for word in ['family', 'divorce', 'maintenance', 'custody']):
            return 'family_case'
        elif any(word in title_lower for word in ['labor', 'workman', 'industrial']):
            return 'labor_case'
        elif any(word in title_lower for word in ['rent', 'eviction', 'house']):
            return 'rent_case'
        elif any(word in title_lower for word in ['land', 'property', 'title']):
            return 'land_case'
        else:
            return 'case_law'

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific Judiciary Portal document
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
                '.case-content',
                '.content',
                '.main-content',
                '.judgment-text',
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
                **case_details
            }

            # Preserve existing metadata
            metadata.update(doc_info.metadata)

            return {
                'content': content,
                'metadata': metadata,
                'pdf_url': pdf_url
            }

        except Exception as e:
            logger.error(f"Error scraping Judiciary Portal document {doc_info.url}: {e}")
            return None

    def _extract_case_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed case information from the document page"""
        details = {}

        try:
            page_text = soup.get_text()

            # Extract case number
            case_number_patterns = [
                r'Case\s+No\.\s*(\d+/\d+)',
                r'Cr\.?\s*Case\s*No\.\s*(\d+/\d+)',
                r'C\.R\.?\s*Case\s*No\.\s*(\d+/\d+)',
                r'Civil\s+Suit\s*No\.\s*(\d+/\d+)'
            ]

            for pattern in case_number_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['case_number'] = match.group(1) if match.groups() else match.group(0)
                    break

            # Extract court name
            court_patterns = [
                r'(?:In the\s+)?(?:Court of\s+)?(.+?)(?:District|Sessions|Metropolitan)',
                r'(?:Judicial\s+)?Magistrate\s+(.+?)(?:Court|Thana)',
                r'(.+?)(?:District|Sessions) Court'
            ]

            for pattern in court_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['court_name'] = match.group(1).strip()
                    break

            # Extract judge name
            judge_patterns = [
                r'(?:Judge|Judicial Magistrate|Presiding Officer):\s*(.+?)(?:\n|$)',
                r' Hon[\'’]ble\s+(.+?)(?:\n|$)',
                r' BM\.?\s*(.+?)(?:\n|$)'
            ]

            for pattern in judge_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['judge_name'] = match.group(1).strip()
                    break

            # Extract parties
            parties_match = re.search(r'(.+?)\s*vs\.?\s*(.+?)(?:\n|$)', page_text)
            if parties_match:
                details['petitioner'] = parties_match.group(1).strip()
                details['respondent'] = parties_match.group(2).strip()

            # Extract case outcome
            outcome_patterns = [
                r'(?:Allowed|Dismissed|Disposed|Convicted|Acquitted)(?:\.|\:|$)',
                r'Judgment:\s*(.+?)(?:\n|$)',
                r'Order:\s*(.+?)(?:\n|$)'
            ]

            for pattern in outcome_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['outcome'] = match.group(1) if match.groups() else match.group(0)
                    break

        except Exception as e:
            logger.warning(f"Error extracting case details: {e}")

        return details

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search Judiciary Portal documents
        """
        documents = []

        try:
            # Build search parameters
            search_params = {
                'q': query,
                'case_type': filters.get('case_type', ''),
                'district': filters.get('district', ''),
                'year': filters.get('year', '')
            }

            # Try case search endpoint
            search_url = urljoin(self.base_url, self.case_search_path)
            response = self._make_request(search_url, params=search_params)

            if not response or response.status_code != 200:
                # Fallback: get all documents and filter
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

            logger.info(f"Found {len(documents)} Judiciary Portal search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching Judiciary Portal documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download Judiciary Portal document PDF
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

            # Add case number and court to filename
            case_number = doc_info.metadata.get('case_number', '')
            court_name = doc_info.metadata.get('court_name', '').replace(' ', '_')

            if case_number and court_name:
                filename = f"{self.source_name}_{court_name}_{case_number}_{safe_title}.pdf"
            else:
                filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/judiciary_portal')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading Judiciary Portal PDF: {e}")
            return False