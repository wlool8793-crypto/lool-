"""
HTML extraction for Legal RAG Extraction System (Phase 3)
Extract metadata from HTML pages with Open Graph and Dublin Core support
"""

from typing import Dict, Any, Optional, List
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from ..base_extractor import SimpleExtractor
from ..config import config
from ..exceptions import InvalidInputError
from ..validators import validate_html_content
from ..logging_config import get_logger

logger = get_logger(__name__)


class HTMLExtractor(SimpleExtractor):
    """
    HTML metadata extractor for legal documents.

    Extracts:
    - Title from <title> tag
    - Meta tags (Open Graph, Dublin Core, standard)
    - PDF download URLs
    - Court name and case information
    - Structured data (JSON-LD)
    - Date information
    """

    def __init__(self):
        super().__init__(name="HTMLExtractor")

    def _extract_impl(self, html_content: str, base_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from HTML content.

        Args:
            html_content: HTML string
            base_url: Base URL for resolving relative links
            **kwargs: Additional parameters

        Returns:
            Dictionary with extracted metadata
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract all metadata
        title = self._extract_title(soup)
        meta_tags = self._extract_meta_tags(soup)
        og_data = self._extract_open_graph(soup)
        dc_data = self._extract_dublin_core(soup)
        pdf_url = self._extract_pdf_url(soup, base_url)
        court_name = self._extract_court_name(soup, meta_tags)
        case_info = self._extract_case_info(soup)
        dates = self._extract_dates(soup, meta_tags)
        structured_data = self._extract_structured_data(soup)

        # Combine all metadata
        metadata = {
            **meta_tags,
            **og_data,
            **dc_data,
            **structured_data,
            **dates
        }

        return {
            'status': 'success',
            'data': {
                'title_full': title,
                'source_url': base_url or '',
                'pdf_url': pdf_url or '',
                'court_name': court_name,
                'case_info': case_info,
                'metadata': metadata,
            }
        }

    # ==================== Title Extraction ====================

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try <title> tag
        if soup.title:
            title = soup.title.string
            if title:
                return title.strip()

        # Try <h1> tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Try Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        return ""

    # ==================== Meta Tags ====================

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract standard meta tags"""
        metadata = {}

        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            # Standard meta tags (name attribute)
            if tag.get('name') and tag.get('content'):
                name = tag['name'].lower()
                content = tag['content'].strip()

                # Map to standardized names
                if name in ['description', 'keywords', 'author', 'date', 'language']:
                    metadata[f'meta_{name}'] = content

        return metadata

    # ==================== Open Graph ====================

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract Open Graph metadata.

        Common in modern legal websites for social sharing.
        """
        og_data = {}

        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            property_name = tag.get('property', '')
            content = tag.get('content', '').strip()

            if content:
                # Remove 'og:' prefix and store
                key = property_name.replace('og:', 'og_')
                og_data[key] = content

        return og_data

    # ==================== Dublin Core ====================

    def _extract_dublin_core(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract Dublin Core metadata.

        Dublin Core is a standard metadata schema used by many legal repositories.
        """
        dc_data = {}

        # Dublin Core can be in <meta> or <link> tags
        dc_tags = soup.find_all('meta', attrs={'name': re.compile(r'^DC\.|^dc\.')})
        dc_tags += soup.find_all('link', attrs={'rel': re.compile(r'^DC\.|^dc\.')})

        for tag in dc_tags:
            # Get name/rel
            name = tag.get('name') or tag.get('rel', '')
            name = name.lower()

            # Get content
            content = tag.get('content', '').strip()

            if content:
                # Standardize name (remove dc. prefix)
                key = name.replace('dc.', 'dc_')
                dc_data[key] = content

        return dc_data

    # ==================== PDF URL Extraction ====================

    def _extract_pdf_url(self, soup: BeautifulSoup, base_url: Optional[str] = None) -> Optional[str]:
        """
        Extract PDF download URL.

        Strategies:
        1. Look for <a> tags with .pdf extension
        2. Look for buttons/links with "download" text
        3. Check meta tags for PDF URL
        4. Look for iframe with PDF
        """
        # Strategy 1: Direct PDF links
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        if pdf_links:
            url = pdf_links[0].get('href')
            return self._resolve_url(url, base_url)

        # Strategy 2: Links with .pdf anywhere in URL
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf', re.IGNORECASE))
        if pdf_links:
            url = pdf_links[0].get('href')
            return self._resolve_url(url, base_url)

        # Strategy 3: Download buttons/links
        download_links = soup.find_all('a', string=re.compile(r'download|pdf', re.IGNORECASE))
        if download_links:
            url = download_links[0].get('href')
            if url:
                return self._resolve_url(url, base_url)

        # Strategy 4: Links with download attribute
        download_links = soup.find_all('a', download=True)
        if download_links:
            url = download_links[0].get('href')
            if url:
                return self._resolve_url(url, base_url)

        # Strategy 5: iframe with PDF
        iframes = soup.find_all('iframe', src=re.compile(r'\.pdf', re.IGNORECASE))
        if iframes:
            url = iframes[0].get('src')
            return self._resolve_url(url, base_url)

        # Strategy 6: Look in meta tags
        pdf_meta = soup.find('meta', attrs={'name': 'pdf_url'})
        if pdf_meta and pdf_meta.get('content'):
            return pdf_meta['content']

        return None

    def _resolve_url(self, url: Optional[str], base_url: Optional[str]) -> Optional[str]:
        """Resolve relative URL to absolute"""
        if not url:
            return None

        # Already absolute
        if url.startswith('http://') or url.startswith('https://'):
            return url

        # Relative URL - need base_url
        if base_url:
            return urljoin(base_url, url)

        return url

    # ==================== Court Name Extraction ====================

    def _extract_court_name(self, soup: BeautifulSoup, metadata: Dict[str, str]) -> Optional[str]:
        """
        Extract court name.

        Strategies:
        1. Look in metadata
        2. Look for court name patterns in text
        3. Look in specific HTML elements
        """
        # Strategy 1: Metadata
        if 'dc_publisher' in metadata:
            return metadata['dc_publisher']

        if 'meta_author' in metadata and 'court' in metadata['meta_author'].lower():
            return metadata['meta_author']

        # Strategy 2: Common court name patterns
        court_patterns = [
            r'(Supreme Court of [A-Z][a-z]+)',
            r'(High Court of [A-Z][a-z]+)',
            r'([A-Z][a-z]+ High Court)',
            r'(District Court of [A-Z][a-z]+)',
            r'(Court of [A-Z][a-z]+)',
        ]

        text = soup.get_text()
        for pattern in court_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # Strategy 3: Look in specific elements
        court_div = soup.find('div', class_=re.compile(r'court', re.IGNORECASE))
        if court_div:
            return court_div.get_text(strip=True)

        return None

    # ==================== Case Information ====================

    def _extract_case_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract case-specific information.

        Returns:
            Dictionary with case number, parties, etc.
        """
        case_info = {}

        # Case number
        case_num_patterns = [
            r'Case No\.?\s*:?\s*([A-Z0-9\-\/]+)',
            r'Civil Appeal No\.?\s*:?\s*([A-Z0-9\-\/]+)',
            r'Criminal Appeal No\.?\s*:?\s*([A-Z0-9\-\/]+)',
            r'Writ Petition No\.?\s*:?\s*([A-Z0-9\-\/]+)',
        ]

        text = soup.get_text()
        for pattern in case_num_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                case_info['case_number'] = match.group(1)
                break

        # Citation (if in HTML)
        citation_pattern = r'\b(\d+)\s+\((\d{4})\)\s+([A-Z]{2,})\s+\(([A-Z]+)\)\s+(\d+)\b'
        match = re.search(citation_pattern, text)
        if match:
            case_info['citation_text'] = match.group(0)

        return case_info

    # ==================== Date Extraction ====================

    def _extract_dates(self, soup: BeautifulSoup, metadata: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Extract date information.

        Returns:
            Dictionary with judgment_date, filing_date, etc.
        """
        dates = {}

        # From Dublin Core
        if 'dc_date' in metadata:
            dates['date_judgment'] = metadata['dc_date']

        # From meta tags
        if 'meta_date' in metadata:
            dates['date_judgment'] = metadata['meta_date']

        # Look for date labels in text
        date_patterns = {
            'date_judgment': r'Date of Judgment\s*:?\s*([0-9\-\/\.]+)',
            'date_filing': r'Date of Filing\s*:?\s*([0-9\-\/\.]+)',
            'date_hearing': r'Date of Hearing\s*:?\s*([0-9\-\/\.]+)',
            'date_order': r'Date of Order\s*:?\s*([0-9\-\/\.]+)',
        }

        text = soup.get_text()
        for date_type, pattern in date_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match and date_type not in dates:
                dates[date_type] = match.group(1)

        return dates

    # ==================== Structured Data ====================

    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract JSON-LD structured data.

        Some modern legal websites include structured data.
        """
        structured = {}

        # Find JSON-LD scripts
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                import json
                data = json.loads(script.string)

                # Extract useful fields
                if isinstance(data, dict):
                    if '@type' in data:
                        structured['schema_type'] = data['@type']

                    if 'name' in data:
                        structured['schema_name'] = data['name']

                    if 'datePublished' in data:
                        structured['date_published'] = data['datePublished']

            except Exception as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")

        return structured

    # ==================== Utility Methods ====================

    def extract_all_links(self, html_content: str, base_url: Optional[str] = None) -> List[str]:
        """
        Extract all links from HTML.

        Args:
            html_content: HTML string
            base_url: Base URL for resolving relative links

        Returns:
            List of URLs
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = []

        for a_tag in soup.find_all('a', href=True):
            url = self._resolve_url(a_tag['href'], base_url)
            if url:
                links.append(url)

        return links

    def extract_text_content(self, html_content: str) -> str:
        """
        Extract plain text from HTML.

        Args:
            html_content: HTML string

        Returns:
            Plain text
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        return text


# ==================== Convenience Function ====================

def extract_html_metadata(html_content: str, base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick extract metadata from HTML (convenience function).

    Args:
        html_content: HTML string
        base_url: Base URL for resolving links

    Returns:
        Dictionary with metadata
    """
    extractor = HTMLExtractor()
    result = extractor.extract(html_content, base_url=base_url)
    return result.get('data', {})
