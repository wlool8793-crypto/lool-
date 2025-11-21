"""
Ministry of Law, Justice and Parliamentary Affairs Scraper - TIER 1
Ministry of Law official documents, notifications, circulars, and policies
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


class MoljScraper(BaseLegalScraper):
    """
    Scraper for Ministry of Law, Justice and Parliamentary Affairs website
    Official notifications, circulars, policies, and administrative documents
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://molj.gov.bd')
        self.documents_path = config.get('documents_path', '/documents')
        self.publications_path = config.get('publications_path', '/publications')
        self.notifications_path = config.get('notifications_path', '/notifications')

        # Enhanced selectors for MOLJ website
        self.selectors = {
            'document_list': '.doc-item, .notification-item, .publication-item, tr',
            'document_title': 'h3, .title, a',
            'document_link': 'a',
            'content_area': '.content, .main-content, .document-content',
            'pdf_link': '.pdf-download, a[href*="download"], .download-btn',
            'date_published': '.date, .published, .publication-date',
            'document_type': '.type, .category, .doc-type'
        }

        # Document categories for MOLJ
        self.document_categories = [
            'notifications',
            'circulars',
            'policies',
            'reports',
            'guidelines',
            'acts',
            'ordinances',
            'amendments'
        ]

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get list of available documents from Ministry of Law
        """
        documents = []

        try:
            # Get documents by category
            for category in self.document_categories:
                try:
                    category_url = urljoin(self.base_url, f"/{category}")
                    response = self._make_request(category_url)

                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        category_docs = self._parse_document_list(soup, category)
                        documents.extend(category_docs)

                        logger.info(f"Found {len(category_docs)} documents in {category}")

                except Exception as e:
                    logger.warning(f"Failed to get {category} documents: {e}")
                    continue

            # Try general documents section
            try:
                documents_url = urljoin(self.base_url, self.documents_path)
                response = self._make_request(documents_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    general_docs = self._parse_document_list(soup, 'general')
                    documents.extend(general_docs)

                    logger.info(f"Found {len(general_docs)} general documents")

            except Exception as e:
                logger.warning(f"Failed to get general documents: {e}")

            # Try publications section
            try:
                publications_url = urljoin(self.base_url, self.publications_path)
                response = self._make_request(publications_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    pub_docs = self._parse_document_list(soup, 'publication')
                    documents.extend(pub_docs)

                    logger.info(f"Found {len(pub_docs)} publications")

            except Exception as e:
                logger.warning(f"Failed to get publications: {e}")

            # Try notifications section
            try:
                notifications_url = urljoin(self.base_url, self.notifications_path)
                response = self._make_request(notifications_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    notif_docs = self._parse_document_list(soup, 'notification')
                    documents.extend(notif_docs)

                    logger.info(f"Found {len(notif_docs)} notifications")

            except Exception as e:
                logger.warning(f"Failed to get notifications: {e}")

            # Try to get recent documents
            try:
                recent_url = urljoin(self.base_url, '/recent')
                response = self._make_request(recent_url)

                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    recent_docs = self._parse_document_list(soup, 'recent')
                    documents.extend(recent_docs)

                    logger.info(f"Found {len(recent_docs)} recent documents")

            except Exception as e:
                logger.warning(f"Failed to get recent documents: {e}")

            logger.info(f"Total MOLJ documents found: {len(documents)}")
            return documents

        except Exception as e:
            logger.error(f"Error getting MOLJ document list: {e}")
            return []

    def _parse_document_list(self, soup: BeautifulSoup, category: str) -> List[DocumentInfo]:
        """Parse document list page to extract document information"""
        documents = []

        # Try different selectors for document items
        doc_selectors = [
            'tr',  # Table rows
            '.doc-item',
            '.notification-item',
            '.publication-item',
            '.result-item',
            'li'
        ]

        doc_items = []
        for selector in doc_selectors:
            items = soup.select(selector)
            if items and len(items) > 1:  # Found substantial content
                doc_items = items
                break

        for item in doc_items:
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
                date = self._extract_date_from_item(item)

                # Extract document number/identifier
                doc_number = self._extract_document_number(title, item)

                # Extract ministry/division info
                ministry_info = self._extract_ministry_info(item, title)

                doc_info = DocumentInfo(
                    title=title,
                    url=url,
                    doc_type=doc_type,
                    source=self.source_name,
                    date=date,
                    metadata={
                        'category': category,
                        'document_number': doc_number,
                        'ministry': ministry_info,
                        'scraped_at': time.time()
                    }
                )

                documents.append(doc_info)

            except Exception as e:
                logger.warning(f"Error parsing document item: {e}")
                continue

        return documents

    def _classify_document(self, title: str, category: str) -> str:
        """Classify document type based on title and category"""
        title_lower = title.lower()

        # Check specific keywords in title
        if any(word in title_lower for word in ['notification', 'gazette', 's.r.o']):
            return 'notification'
        elif any(word in title_lower for word in ['circular', 'office order', 'o.m.']):
            return 'circular'
        elif any(word in title_lower for word in ['policy', 'strategy', 'framework']):
            return 'policy'
        elif any(word in title_lower for word in ['report', 'annual report', 'survey']):
            return 'report'
        elif any(word in title_lower for word in ['guideline', 'manual', 'handbook']):
            return 'guideline'
        elif any(word in title_lower for word in ['act', 'law']):
            return 'act'
        elif any(word in title_lower for word in ['ordinance', 'order']):
            return 'ordinance'
        elif any(word in title_lower for word in ['amendment', 'amended']):
            return 'amendment'
        elif any(word in title_lower for word in ['rule', 'rules']):
            return 'rule'
        elif any(word in title_lower for word in ['regulation', 'regs']):
            return 'regulation'
        else:
            return category

    def _extract_date_from_item(self, item_element) -> Optional[str]:
        """Extract publication date from list item"""
        date_selectors = [
            '.date',
            '.published',
            '.publication-date',
            '.issue-date',
            'td:last-child',
            '.date-text'
        ]

        for selector in date_selectors:
            date_element = item_element.select_one(selector)
            if date_element:
                date_text = date_element.get_text(strip=True)
                date = self._parse_date(date_text)
                if date:
                    return date

        return None

    def _extract_document_number(self, title: str, item_element) -> Optional[str]:
        """Extract document number/identifier"""
        # Try to extract from title first
        patterns = [
            r'S\.R\.O\.?\s*No\.\s*(\d+/\d+)',
            r'Notification\s*No\.\s*(\d+)',
            r'Order\s*No\.\s*(\d+)',
            r'Memo\s*No\.\s*([A-Z0-9/-]+)',
            r'F\.?\s*No\.\s*(\d+)',
            r'(\d{4}/\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)

        # Try to extract from item element
        number_selectors = [
            '.doc-number',
            '.notification-no',
            '.reference-no',
            '.sl-no'
        ]

        for selector in number_selectors:
            element = item_element.select_one(selector)
            if element:
                number_text = element.get_text(strip=True)
                if number_text:
                    return number_text

        return None

    def _extract_ministry_info(self, item_element, title: str) -> str:
        """Extract ministry/division information"""
        ministry_selectors = [
            '.ministry',
            '.division',
            '.department',
            '.directorate'
        ]

        for selector in ministry_selectors:
            element = item_element.select_one(selector)
            if element:
                ministry_text = element.get_text(strip=True)
                if ministry_text:
                    return ministry_text

        # Try to extract from title
        title_lower = title.lower()
        if any(word in title_lower for word in ['law', 'justice', 'parliamentary']):
            return 'Ministry of Law, Justice and Parliamentary Affairs'
        elif 'legislative' in title_lower:
            return 'Legislative Division'
        elif 'justice' in title_lower:
            return 'Justice Division'
        elif 'parliamentary' in title_lower:
            return 'Parliamentary Affairs Division'

        return 'Ministry of Law, Justice and Parliamentary Affairs'

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific MOLJ document
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
                '.document-content',
                '.notification-content',
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

            # Extract document details
            doc_details = self._extract_document_details(soup)

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
                **doc_details
            }

            # Preserve existing metadata
            metadata.update(doc_info.metadata)

            return {
                'content': content,
                'metadata': metadata,
                'pdf_url': pdf_url
            }

        except Exception as e:
            logger.error(f"Error scraping MOLJ document {doc_info.url}: {e}")
            return None

    def _extract_document_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed document information"""
        details = {}

        try:
            page_text = soup.get_text()

            # Extract S.R.O. number
            sro_patterns = [
                r'S\.R\.O\.?\s*No\.\s*(\d+/\d+)',
                r'S\.R\.O\.?\s*#?\s*(\d+)',
                r'S\.R\.O\.?\s*\((\d+)\)'
            ]

            for pattern in sro_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['sro_number'] = match.group(1) if match.groups() else match.group(0)
                    break

            # Extract publication date
            pub_date_patterns = [
                r'Published?\s*on:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ]

            for pattern in pub_date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    details['publication_date'] = self._parse_date(match.group(1))
                    break

            # Extract effective date
            eff_date_patterns = [
                r'Effective?\s*from:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Effective?\s*date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                r'Shall come into force on (\d{1,2}[-/]\d{1,2}[-/]\d{4})'
            ]

            for pattern in eff_date_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['effective_date'] = self._parse_date(match.group(1))
                    break

            # Extract issuing authority
            authority_patterns = [
                r'Issued by:\s*(.+?)(?:\n|$)',
                r'Authority:\s*(.+?)(?:\n|$)',
                r'Signed by:\s*(.+?)(?:\n|$)'
            ]

            for pattern in authority_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['issuing_authority'] = match.group(1).strip()
                    break

            # Extract subject/section
            subject_patterns = [
                r'Subject:\s*(.+?)(?:\n|$)',
                r'Reference:\s*(.+?)(?:\n|$)',
                r'In exercise of (.+?)(?:\n|$)'
            ]

            for pattern in subject_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['subject'] = match.group(1).strip()
                    break

        except Exception as e:
            logger.warning(f"Error extracting document details: {e}")

        return details

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search MOLJ documents
        """
        documents = []

        try:
            # Build search parameters
            search_params = {
                'q': query,
                'type': filters.get('doc_type', ''),
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
                                (doc.metadata.get('document_number') and query.lower() in doc.metadata['document_number'].lower())]
                return filtered_docs

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse search results
            result_selectors = [
                '.search-result',
                '.result-item',
                '.doc-item'
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

            logger.info(f"Found {len(documents)} MOLJ search results for '{query}'")

        except Exception as e:
            logger.error(f"Error searching MOLJ documents: {e}")

        return documents

    def download_pdf(self, pdf_url: str, doc_info: DocumentInfo) -> bool:
        """
        Download MOLJ document PDF
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

            # Add document number and category to filename
            doc_number = doc_info.metadata.get('document_number', '')
            category = doc_info.metadata.get('category', '')

            if doc_number and category:
                filename = f"{self.source_name}_{category}_{doc_number}_{safe_title}.pdf"
            else:
                filename = f"{self.source_name}_{safe_title}.pdf"

            # Use configured PDF directory or default
            pdf_dir = self.config.get('pdf_dir', './data/pdfs/bangladesh/molj')
            save_path = os.path.join(pdf_dir, filename)

            return self._download_pdf(pdf_url, save_path)

        except Exception as e:
            logger.error(f"Error downloading MOLJ PDF: {e}")
            return False