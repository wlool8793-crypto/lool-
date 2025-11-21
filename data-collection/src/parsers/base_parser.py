"""
Base HTML Parser
Common utilities for parsing legal document HTML pages
"""

import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag
from datetime import datetime


class BaseParser:
    """Base class with common HTML parsing utilities"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove special characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text

    @staticmethod
    def extract_text_from_element(element: Tag, selector: str = None) -> str:
        """
        Extract text from BeautifulSoup element.

        Args:
            element: BeautifulSoup Tag
            selector: CSS selector (optional)

        Returns:
            Extracted and cleaned text
        """
        if selector:
            found = element.select_one(selector)
            if found:
                return BaseParser.clean_text(found.get_text())
        else:
            return BaseParser.clean_text(element.get_text())
        return ""

    @staticmethod
    def extract_year(text: str) -> Optional[int]:
        """
        Extract year from text (finds 4-digit year).

        Args:
            text: Text containing year

        Returns:
            Year as integer or None
        """
        # Look for 4-digit year (1900-2099)
        match = re.search(r'\b(19|20)\d{2}\b', text)
        if match:
            return int(match.group())
        return None

    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """
        Extract date from text and normalize to ISO format.

        Args:
            text: Text containing date

        Returns:
            ISO format date string or None
        """
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # DD Month YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    # Try to parse date (this is simplified, could be improved)
                    if len(groups) == 3:
                        if pattern.startswith(r'(\d{4})'):
                            # YYYY-MM-DD format
                            return f"{groups[0]}-{groups[1]:>02}-{groups[2]:>02}"
                        else:
                            # Assume DD-MM-YYYY
                            return f"{groups[2]}-{groups[1]:>02}-{groups[0]:>02}"
                except:
                    pass

        return None

    @staticmethod
    def extract_links(html: str, pattern: str = None) -> List[str]:
        """
        Extract all links from HTML.

        Args:
            html: HTML content
            pattern: Regex pattern to filter links (optional)

        Returns:
            List of URLs
        """
        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if pattern:
                if re.search(pattern, href):
                    links.append(href)
            else:
                links.append(href)

        return links

    @staticmethod
    def extract_table_data(table: Tag) -> List[Dict[str, str]]:
        """
        Extract data from HTML table.

        Args:
            table: BeautifulSoup table element

        Returns:
            List of dictionaries (one per row)
        """
        if not table:
            return []

        data = []
        rows = table.find_all('tr')

        # Get headers (if present)
        headers = []
        if rows:
            first_row = rows[0]
            header_cells = first_row.find_all(['th', 'td'])
            headers = [BaseParser.clean_text(cell.get_text()) for cell in header_cells]

        # Extract data rows
        for row in rows[1:] if headers else rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                if headers and len(cells) == len(headers):
                    # Create dictionary with headers as keys
                    row_data = {
                        headers[i]: BaseParser.clean_text(cells[i].get_text())
                        for i in range(len(headers))
                    }
                else:
                    # Create dictionary with generic keys
                    row_data = {
                        f'column_{i}': BaseParser.clean_text(cell.get_text())
                        for i, cell in enumerate(cells)
                    }
                data.append(row_data)

        return data

    @staticmethod
    def remove_tags(html: str, tags_to_remove: List[str] = None) -> str:
        """
        Remove specific HTML tags while keeping content.

        Args:
            html: HTML content
            tags_to_remove: List of tag names to remove (e.g., ['script', 'style'])

        Returns:
            HTML with tags removed
        """
        if not tags_to_remove:
            tags_to_remove = ['script', 'style', 'iframe', 'noscript']

        soup = BeautifulSoup(html, 'lxml')

        for tag_name in tags_to_remove:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        return str(soup)

    @staticmethod
    def html_to_text(html: str) -> str:
        """
        Convert HTML to plain text.

        Args:
            html: HTML content

        Returns:
            Plain text with HTML tags removed
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    @staticmethod
    def extract_meta_tags(html: str) -> Dict[str, str]:
        """
        Extract all meta tags from HTML.

        Args:
            html: HTML content

        Returns:
            Dictionary of meta tag name/property to content
        """
        soup = BeautifulSoup(html, 'lxml')
        meta_tags = {}

        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')

            if name and content:
                meta_tags[name] = content

        return meta_tags

    @staticmethod
    def find_by_text(soup: BeautifulSoup, tag: str, text_pattern: str) -> Optional[Tag]:
        """
        Find element by text content.

        Args:
            soup: BeautifulSoup object
            tag: HTML tag name
            text_pattern: Regex pattern to match text

        Returns:
            First matching Tag or None
        """
        for element in soup.find_all(tag):
            if re.search(text_pattern, element.get_text(), re.IGNORECASE):
                return element
        return None

    @staticmethod
    def extract_numbered_list(html: str, list_type: str = 'ol') -> List[str]:
        """
        Extract items from numbered/bulleted list.

        Args:
            html: HTML content
            list_type: 'ol' for ordered, 'ul' for unordered

        Returns:
            List of text items
        """
        soup = BeautifulSoup(html, 'lxml')
        items = []

        for ol in soup.find_all(list_type):
            for li in ol.find_all('li'):
                items.append(BaseParser.clean_text(li.get_text()))

        return items
