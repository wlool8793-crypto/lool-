"""
Automated PDF extraction for legal case documents
Replaces manual extraction with intelligent parsing
"""
import re
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class LegalCase:
    """Structured legal case data"""
    case_id: str
    name: str
    citation: str
    year: Optional[int] = None
    date: Optional[str] = None
    topic: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    judges: List[str] = None
    petitioner: List[str] = None
    respondent: List[str] = None
    sections: List[str] = None
    principles: List[str] = None
    abstract: Optional[str] = None
    issue: Optional[str] = None
    holding: Optional[str] = None
    significance: Optional[str] = None
    full_text: Optional[str] = None

    def __post_init__(self):
        # Initialize lists if None
        if self.judges is None:
            self.judges = []
        if self.petitioner is None:
            self.petitioner = []
        if self.respondent is None:
            self.respondent = []
        if self.sections is None:
            self.sections = []
        if self.principles is None:
            self.principles = []

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class PDFCaseExtractor:
    """
    Extract structured legal case data from PDF documents

    Features:
    - Automatic case name and citation extraction
    - Judge and party identification
    - Section reference parsing
    - Legal principle detection
    - Court and date extraction
    """

    def __init__(self):
        # Regex patterns for legal text extraction
        self.patterns = {
            # Case citation patterns (e.g., "60 DLR 20", "74 DLR 101")
            'citation': r'(\d+)\s+([A-Z]{2,5})\s+(\d+)',

            # Court names
            'court': r'(Supreme Court|High Court Division|District (?:Judge|Court)|Trial Court|Appellate Division)',

            # Judge names (Justice, J., etc.)
            'judges': r'(?:Justice|J\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',

            # Section references
            'section': r'Section\s+(\d+[A-Z]?)(?:\s*\(\d+\))?(?:\s+of\s+(?:the\s+)?([A-Za-z\s,]+?))?(?=\s|,|\.|;|$)',

            # Order and Rule references
            'order': r'Order\s+([IVXLC]+),?\s*(?:Rule|rule)\s+(\d+)',

            # Date patterns
            'date': r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})',

            # Year patterns
            'year': r'\b(19|20)\d{2}\b',

            # Case name pattern (Petitioner vs Respondent)
            'case_name': r'([A-Z][A-Za-z\s&.]+?)\s+(?:vs?\.?|versus)\s+([A-Z][A-Za-z\s&.]+?)(?:\s+and\s+others?)?(?=\s+on|\s+\(|\s+\[|$)',

            # Legal topics
            'topics': r'(Revision|Appeal|Inherent Power|Writ Petition|Review|Reference|Contempt)',

            # Legal principles (common patterns)
            'principles': r'(res judicata|stare decisis|doctrine of merger|inherent power|clean hands|functus officio|natural justice|due process)',
        }

    def extract_from_pdf(self, pdf_path: str) -> List[LegalCase]:
        """
        Extract cases from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of extracted LegalCase objects
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting cases from: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            full_text = ""

            # Extract all text from PDF
            for page_num in range(len(doc)):
                page = doc[page_num]
                full_text += page.get_text()

            doc.close()

            # Split into individual cases (if multiple cases in one PDF)
            cases = self._split_cases(full_text)

            logger.info(f"Found {len(cases)} cases in PDF")

            # Extract structured data from each case
            structured_cases = []
            for idx, case_text in enumerate(cases):
                case_data = self._extract_case_data(case_text, idx + 1)
                if case_data:
                    structured_cases.append(case_data)

            return structured_cases

        except Exception as e:
            logger.error(f"Error extracting from PDF {pdf_path}: {str(e)}")
            raise

    def _split_cases(self, text: str) -> List[str]:
        """
        Split PDF text into individual case sections

        Args:
            text: Full PDF text

        Returns:
            List of case text blocks
        """
        # Try to find case boundaries (look for citation patterns or case numbers)
        case_pattern = r'(?:Case\s+(?:No\.?\s+)?\d+|^\d+\s+[A-Z]{2,5}\s+\d+)'

        # Split by case pattern
        parts = re.split(f'({case_pattern})', text, flags=re.MULTILINE)

        if len(parts) <= 1:
            # No clear case boundaries, treat as single case
            return [text]

        # Combine parts into cases
        cases = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                case_text = parts[i] + parts[i + 1]
                if len(case_text.strip()) > 200:  # Minimum text length
                    cases.append(case_text)

        return cases if cases else [text]

    def _extract_case_data(self, text: str, case_num: int) -> Optional[LegalCase]:
        """
        Extract structured data from case text

        Args:
            text: Case text
            case_num: Case number for ID generation

        Returns:
            LegalCase object or None if extraction fails
        """
        try:
            # Extract citation
            citation_match = re.search(self.patterns['citation'], text)
            citation = f"{citation_match.group(0)}" if citation_match else f"Case-{case_num}"

            # Extract case name (parties)
            name_match = re.search(self.patterns['case_name'], text[:2000])
            if name_match:
                case_name = name_match.group(0)
                petitioner = [name_match.group(1).strip()]
                respondent = [name_match.group(2).strip()]
            else:
                case_name = f"Case {citation}"
                petitioner = []
                respondent = []

            # Extract year
            year_match = re.search(self.patterns['year'], text[:1000])
            year = int(year_match.group(0)) if year_match else None

            # Extract date
            date_match = re.search(self.patterns['date'], text[:2000])
            date = date_match.group(0) if date_match else None

            # Extract court
            court_match = re.search(self.patterns['court'], text[:3000])
            court = court_match.group(0) if court_match else None

            # Extract judges
            judges = list(set(re.findall(self.patterns['judges'], text[:5000])))[:5]

            # Extract sections
            section_matches = re.findall(self.patterns['section'], text)
            sections = []
            for section_num, statute in section_matches[:20]:
                section_id = f"Section {section_num}"
                if statute.strip():
                    section_id += f" ({statute.strip()})"
                sections.append(section_id)
            sections = list(set(sections))  # Remove duplicates

            # Extract orders/rules
            order_matches = re.findall(self.patterns['order'], text)
            for order_num, rule_num in order_matches[:10]:
                sections.append(f"Order {order_num}, Rule {rule_num}")

            # Extract topic
            topic_match = re.search(self.patterns['topics'], text[:2000])
            topic = topic_match.group(0) if topic_match else None

            # Extract legal principles
            principles = list(set(re.findall(self.patterns['principles'], text, re.IGNORECASE)))

            # Generate case ID
            case_id = f"case_{case_num}"

            # Extract abstract/summary (first 500 characters after case name)
            if name_match:
                start_pos = name_match.end()
                abstract = text[start_pos:start_pos+500].strip()
                abstract = abstract[:abstract.rfind('.')+1] if '.' in abstract else abstract
            else:
                abstract = text[:500].strip()

            # Create LegalCase object
            case = LegalCase(
                case_id=case_id,
                name=case_name,
                citation=citation,
                year=year,
                date=date,
                topic=topic,
                court=court,
                judges=judges,
                petitioner=petitioner,
                respondent=respondent,
                sections=sections,
                principles=principles,
                abstract=abstract,
                full_text=text[:10000]  # Store first 10k chars
            )

            logger.debug(f"Extracted case: {case.name} ({case.citation})")

            return case

        except Exception as e:
            logger.error(f"Error extracting case data: {str(e)}")
            return None

    def extract_to_json(self, pdf_path: str, output_path: str) -> None:
        """
        Extract cases from PDF and save to JSON file

        Args:
            pdf_path: Path to PDF file
            output_path: Path to output JSON file
        """
        import json

        cases = self.extract_from_pdf(pdf_path)

        output_data = {
            "cases": [case.to_dict() for case in cases],
            "metadata": {
                "source_pdf": str(pdf_path),
                "total_cases": len(cases),
                "extraction_method": "automated_pdf_extraction"
            }
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(cases)} cases to {output_path}")


def extract_pdf_to_json(pdf_path: str, output_path: str = "extracted_cases.json") -> None:
    """
    Convenience function to extract PDF and save to JSON

    Args:
        pdf_path: Path to PDF file
        output_path: Output JSON file path

    Example:
        extract_pdf_to_json("cpc2.pdf", "cpc_data_auto.json")
    """
    extractor = PDFCaseExtractor()
    extractor.extract_to_json(pdf_path, output_path)
