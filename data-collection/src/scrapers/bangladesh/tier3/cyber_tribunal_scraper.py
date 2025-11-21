"""
Cyber Tribunal Scraper - TIER 3
Bangladesh Cyber Security Tribunal - 8 tribunals nationwide for cyber crimes
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


class CyberTribunalScraper(BaseLegalScraper):
    """
    Scraper for Bangladesh Cyber Security Tribunal
    Handles cyber crime cases and decisions from 8 tribunals nationwide
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://cybertribunal.gov.bd')
        self.decisions_path = config.get('decisions_path', '/decisions')
        self.orders_path = config.get('orders_path', '/orders')

        # Tribunal locations
        self.tribunal_locations = [
            'dhaka',
            'chattogram',
            'rajshahi',
            'khulna',
            'sylhet',
            'barishal',
            'rangpur',
            'mymensingh'
        ]

        # Enhanced selectors for Cyber Tribunal website
        self.selectors = {
            'case_list': '.case-item, .decision-item, tr',
            'case_title': 'h3, .title, a',
            'case_link': 'a',
            'content_area': '.content, .main-content, .decision-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'case_info': '.case-info, .metadata, .header',
            'tribunal_info': '.tribunal, .location, .bench'
        }

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of available cyber tribunal cases
        """
        documents = []

        try:
            # Get cases by tribunal location
            for location in self.tribunal_locations:
                try:
                    location_url = urljoin(self.base_url, f"/{location}/decisions")
                    response = self._make_request(location_url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        location_docs = self._parse_case_list(soup, location)
                        documents.extend(location_docs)

                        logger.info(f"Found {len(location_docs)} cases for {location} tribunal")

                except Exception as e:
                    logger.warning(f"Failed to get {location} tribunal cases: {e}")
                    continue

            # Try general decisions section
            try:
                decisions_url = urljoin(self.base_url, self.decisions_path)
                response = self._make_request(decisions_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    general_docs = self._parse_case_list(soup, 'general')
                    documents.extend(general_docs)

                    logger.info(f"Found {len(general_docs)} general cyber tribunal decisions")

            except Exception as e:
                logger.warning(f"Failed to get general decisions: {e}")

            # Try orders section
            try:
                orders_url = urljoin(self.base_url, self.orders_path)
                response = self._make_request(orders_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    order_docs = self._parse_case_list(soup, 'order')
                    documents.extend(order_docs)

                    logger.info(f"Found {len(order_docs)} cyber tribunal orders")

            except Exception as e:
                logger.warning(f"Failed to get orders: {e}")

            logger.info(f"Total Cyber Tribunal documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting Cyber Tribunal document list: {e}")
            return []

    def _parse_case_list(self, soup: BeautifulSoup, location: str) -> List[DocumentInfo]:
        """Parse case list page to extract case information"""
        documents = []

        # Try different selectors for case items
        case_selectors = [
            'tr',  # Table rows
            '.case-item',
            '.decision-item',
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

                # Extract cyber law sections
                cyber_sections = self._extract_cyber_sections(title)

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type='cyber_case',
                    source=self.source_name,
                    date=date,
                    metadata={
                        'case_number': case_number,
                        'tribunal_location': location,
                        'cyber_sections': cyber_sections,
                        'court': 'Cyber Security Tribunal',
                        'scraped_at': time.time()
                    }
                )

                documents.append(doc_info)

            except Exception as e:
                logger.warning(f"Error parsing cyber tribunal case item: {e}")
                continue

        return documents

    def _extract_case_number(self, title: str) -> Optional[str]:
        """Extract case number from cyber tribunal case title"""
        # Cyber Tribunal case number patterns
        patterns = [
            r'Cyber\s+Tribunal\s+Case\s+No\.\s*(\d+/\d+)',
            r'Case\s+No\.\s*(\d+/\d+)',
            r'C\.?\s*T\.?\s*No\.?\s*(\d+/\d+)',
            r'(\d{4}/\d+)',
            r'under\s*section\s+(\d+)',  # Extract section number as case identifier
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        return None

    def _extract_cyber_sections(self, title: str) -> List[str]:
        """Extract sections of Cyber Security Act mentioned in title"""
        title_lower = title.lower()
        cyber_sections = []

        # Common cyber law sections
        section_patterns = [
            r'section\s+(\d+)',
            r's\.?\s*(\d+)',
            r'under\s+section\s+(\d+)',
            r'violation\s+of\s+section\s+(\d+)'
        ]

        for pattern in section_patterns:
            matches = re.findall(pattern, title_lower)
            for match in matches:
                cyber_sections.append(f"Section {match}")

        # Remove duplicates
        cyber_sections = list(set(cyber_sections))

        return cyber_sections

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific Cyber Tribunal case
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
                '.decision-content',
                '.content',
                '.main-content',
                '.case-content',
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
            case_details = self._extract_cyber_case_details(soup)

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
                'court': 'Cyber Security Tribunal, Bangladesh',
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
            logger.error(f"Error scraping Cyber Tribunal document {doc_info.url}: {e}")
            return None

    def _extract_cyber_case_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed cyber case information"""
        details = {}

        try:
            page_text = soup.get_text()

            # Extract tribunal location
            location_patterns = [
                r'Cyber\s+Tribunal,\s*(.+?)(?:\n|$)',
                r'Tribunal:\s*(.+?)(?:\n|$)',
                r'Bench:\s*(.+?)(?:\n|$)'
            ]

            for pattern in location_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['tribunal_location'] = match.group(1).strip()
                    break

            # Extract case sections
            sections = []
            section_patterns = [
                r'Section\s+(\d+)\s+of\s+the\s+Cyber\s+Security\s+Act',
                r'under\s+Section\s+(\d+)',
                r'violation\s+of\s+Section\s+(\d+)'
            ]

            for pattern in section_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                sections.extend(matches)

            if sections:
                details['sections'] = list(set(sections))

            # Extract complainant and respondent
            parties_match = re.search(r'(.+?)\s*vs\.?\s*(.+?)(?:\n|$)', page_text)
            if parties_match:
                details['complainant'] = parties_match.group(1).strip()
                details['respondent'] = parties_match.group(2).strip()

            # Extract judge/presiding officer
            judge_patterns = [
                r'(?:Judge|Presiding Officer|Magistrate):\s*(.+?)(?:\n|$)',
                r'Heard by:\s*(.+?)(?:\n|$)',
                r'Decided by:\s*(.+?)(?:\n|$)'
            ]

            for pattern in judge_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['presiding_officer'] = match.group(1).strip()
                    break

            # Extract case outcome
            outcome_patterns = [
                r'(?:Convicted|Acquitted|Dismissed|Allowed|Rejected)(?:\.|\:|$)',
                r'Judgment:\s*(.+?)(?:\n|$)',
                r'Order:\s*(.+?)(?:\n|$)'
            ]

            for pattern in outcome_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['outcome'] = match.group(1) if match.groups() else match.group(0)
                    break

            # Extract penalties if any
            penalty_patterns = [
                r'fine:\s*(.+?)(?:\n|$)',
                r'imprisonment:\s*(.+?)(?:\n|$)',
                r'penalty:\s*(.+?)(?:\n|$)',
                r'sentenced\s*to\s*(.+?)(?:\n|$)'
            ]

            penalties = []
            for pattern in penalty_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                penalties.extend(matches)

            if penalties:
                details['penalties'] = penalties

        except Exception as e:
            logger.warning(f"Error extracting cyber case details: {e}")

        return details

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search Cyber Tribunal documents
        """
        documents = []

        try:
            # Build search parameters
            search_params = {
                'q': query,
                'location': filters.get('location', ''),
                'section': filters.get('section', ''),
                'year': filters.get('year', '')
            }

            # Try search endpoint
            search_url = urljoin(self.base_url, '/search')
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
                    logger.warning(f"Error parsing cyber tribunal search result: {e}")
                    continue

            logger.info(f"Found {len(documents)} Cyber Tribunal search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching Cyber Tribunal documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download Cyber Tribunal document PDF
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

            # Add case number and tribunal location to filename
            case_number = doc_info.metadata.get('case_number', '')
            location = doc_info.metadata.get('tribunal_location', '')

            if case_number and location:
                filename = f"{self.source_name}_{location}_{case_number}_{safe_title}.pdf"
            else:
                filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/cyber_tribunal')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading Cyber Tribunal PDF: {e}")
            return False