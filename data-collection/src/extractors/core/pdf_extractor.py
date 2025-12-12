"""
PDF extraction for Legal RAG Extraction System (Phase 3)
Multi-engine PDF extraction with OCR fallback for scanned documents
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import re

# PDF libraries
import pdfplumber
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract
from pdfminer.pdfparser import PDFSyntaxError

from ..base_extractor import BaseExtractor
from ..config import config
from ..exceptions import PDFExtractionError, PDFNotReadableError, PDFPageLimitExceededError
from ..schemas import PDFExtractionResult, PDFPageSchema, PDFQuality, ExtractionStatus
from ..validators import validate_pdf_file
from ..utils import hash_content, hash_file
from ..logging_config import get_logger

logger = get_logger(__name__)


class PDFExtractor(BaseExtractor):
    """
    Multi-engine PDF extractor with fallback chain and OCR support.

    Extraction strategy:
    1. Try pdfplumber (best quality, tables, formatting)
    2. Fallback to PyPDF2 (faster, basic text)
    3. Fallback to pdfminer.six (robust, handles complex PDFs)
    4. Fallback to Tesseract OCR (scanned PDFs)
    """

    def __init__(self):
        super().__init__(name="PDFExtractor")
        self.engines = config.pdf_fallback_engines

    def validate_input(self, input_data: Any) -> bool:
        """Validate PDF file path"""
        if not input_data or not isinstance(input_data, str):
            return False

        try:
            validate_pdf_file(input_data)
            return True
        except Exception as e:
            self.logger.error(f"PDF validation failed: {e}")
            return False

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate PDF extraction output"""
        if not output:
            return False

        # Must have extracted some text
        full_text = output.get('full_text', '')
        if not full_text or len(full_text.strip()) < 50:
            self.logger.warning("Extracted text too short")
            return False

        # Must have page count
        if output.get('page_count', 0) <= 0:
            return False

        return True

    def _extract_impl(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        Core PDF extraction implementation.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFExtractionResult dict
        """
        self.logger.info(f"Extracting PDF: {pdf_path}")

        # Check if scanned PDF
        is_scanned = self._detect_scanned_pdf(pdf_path)

        if is_scanned and config.enable_ocr:
            self.logger.info("Detected scanned PDF, using OCR")
            return self._extract_with_ocr(pdf_path)

        # Try engines in order
        for engine in self.engines:
            try:
                self.logger.debug(f"Trying engine: {engine}")

                if engine == 'pdfplumber':
                    result = self._extract_with_pdfplumber(pdf_path)
                elif engine == 'PyPDF2':
                    result = self._extract_with_pypdf2(pdf_path)
                elif engine == 'pdfminer':
                    result = self._extract_with_pdfminer(pdf_path)
                else:
                    self.logger.warning(f"Unknown engine: {engine}")
                    continue

                # Check if extraction was successful
                if result and result.get('full_text') and len(result['full_text'].strip()) > 50:
                    self.logger.info(f"Successfully extracted with {engine}")
                    return result
                else:
                    self.logger.warning(f"Engine {engine} produced insufficient text")

            except Exception as e:
                self.logger.warning(f"Engine {engine} failed: {e}")
                continue

        # All engines failed, try OCR as last resort
        if config.enable_ocr:
            self.logger.info("All engines failed, trying OCR")
            return self._extract_with_ocr(pdf_path)

        # Complete failure
        raise PDFExtractionError("All extraction methods failed")

    # ==================== Engine: pdfplumber ====================

    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF using pdfplumber (best quality)"""
        pages = []
        full_text = []

        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)

            # Check page limit
            if page_count > config.pdf_max_pages:
                raise PDFPageLimitExceededError(page_count, config.pdf_max_pages)

            # Extract page by page
            for i, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text() or ""
                    full_text.append(text)

                    pages.append({
                        'page_num': i,
                        'text': text,
                        'char_count': len(text)
                    })

                except Exception as e:
                    self.logger.warning(f"Failed to extract page {i}: {e}")
                    pages.append({
                        'page_num': i,
                        'text': "",
                        'char_count': 0
                    })

        # Combine text
        combined_text = '\n\n'.join(full_text)

        # Post-process
        return self._build_result(
            full_text=combined_text,
            pages=pages,
            pdf_path=pdf_path,
            extraction_method='pdfplumber'
        )

    # ==================== Engine: PyPDF2 ====================

    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF using PyPDF2 (fast, basic)"""
        pages = []
        full_text = []

        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)

            if page_count > config.pdf_max_pages:
                raise PDFPageLimitExceededError(page_count, config.pdf_max_pages)

            for i, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text() or ""
                    full_text.append(text)

                    pages.append({
                        'page_num': i,
                        'text': text,
                        'char_count': len(text)
                    })

                except Exception as e:
                    self.logger.warning(f"Failed to extract page {i}: {e}")
                    pages.append({
                        'page_num': i,
                        'text': "",
                        'char_count': 0
                    })

        combined_text = '\n\n'.join(full_text)

        return self._build_result(
            full_text=combined_text,
            pages=pages,
            pdf_path=pdf_path,
            extraction_method='PyPDF2'
        )

    # ==================== Engine: pdfminer ====================

    def _extract_with_pdfminer(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF using pdfminer.six (robust)"""
        try:
            # pdfminer extracts all text at once
            full_text = pdfminer_extract(pdf_path)

            # Estimate page count
            page_count = self._estimate_page_count(pdf_path)

            # Split into pages (rough approximation)
            pages = self._split_text_into_pages(full_text, page_count)

            return self._build_result(
                full_text=full_text,
                pages=pages,
                pdf_path=pdf_path,
                extraction_method='pdfminer'
            )

        except PDFSyntaxError as e:
            raise PDFNotReadableError(f"PDF syntax error: {e}")

    # ==================== Engine: Tesseract OCR ====================

    def _extract_with_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """Extract scanned PDF using Tesseract OCR"""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            import numpy as np

            self.logger.info("Starting OCR extraction...")

            pages = []
            full_text = []
            confidence_scores = []

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            for i, img in enumerate(images, 1):
                try:
                    # OCR with confidence data
                    ocr_data = pytesseract.image_to_data(
                        img,
                        output_type=pytesseract.Output.DICT,
                        config='--psm 6'  # Assume uniform text block
                    )

                    # Extract text and confidence
                    text_parts = []
                    confidences = []

                    for j, word in enumerate(ocr_data['text']):
                        if word.strip():
                            text_parts.append(word)
                            conf = int(ocr_data['conf'][j])
                            if conf >= 0:  # -1 means no confidence
                                confidences.append(conf)

                    page_text = ' '.join(text_parts)
                    full_text.append(page_text)

                    # Calculate page confidence
                    if confidences:
                        page_conf = np.mean(confidences)
                        confidence_scores.append(page_conf)

                    pages.append({
                        'page_num': i,
                        'text': page_text,
                        'char_count': len(page_text)
                    })

                    self.logger.debug(f"OCR page {i}/{len(images)} complete")

                except Exception as e:
                    self.logger.error(f"OCR failed on page {i}: {e}")
                    pages.append({
                        'page_num': i,
                        'text': "",
                        'char_count': 0
                    })

            # Calculate overall OCR confidence
            ocr_confidence = float(np.mean(confidence_scores)) / 100.0 if confidence_scores else 0.0

            combined_text = '\n\n'.join(full_text)

            result = self._build_result(
                full_text=combined_text,
                pages=pages,
                pdf_path=pdf_path,
                extraction_method='tesseract_ocr'
            )

            result['ocr_confidence'] = ocr_confidence
            result['is_scanned'] = True

            self.logger.info(f"OCR extraction complete. Confidence: {ocr_confidence:.2f}")

            return result

        except ImportError as e:
            self.logger.error(f"OCR libraries not available: {e}")
            raise PDFExtractionError("OCR extraction failed: missing dependencies")
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            raise PDFExtractionError(f"OCR extraction failed: {str(e)}")

    # ==================== Helper Methods ====================

    def _detect_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Detect if PDF is scanned (image-based).

        Strategy: Quick extraction with PyPDF2. If very little text, likely scanned.
        """
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                # Check first few pages
                pages_to_check = min(3, len(reader.pages))
                total_text = ""

                for i in range(pages_to_check):
                    text = reader.pages[i].extract_text() or ""
                    total_text += text

                # If less than 100 characters from 3 pages, likely scanned
                word_count = len(total_text.split())
                is_scanned = word_count < 50

                self.logger.debug(f"Scanned detection: {word_count} words, is_scanned={is_scanned}")

                return is_scanned

        except Exception as e:
            self.logger.warning(f"Scanned detection failed: {e}")
            return False

    def _estimate_page_count(self, pdf_path: str) -> int:
        """Estimate page count using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except:
            return 0

    def _split_text_into_pages(self, text: str, page_count: int) -> List[Dict]:
        """Split text into pages (rough approximation)"""
        if page_count <= 0:
            return [{'page_num': 1, 'text': text, 'char_count': len(text)}]

        # Split by form feed or evenly
        if '\f' in text:
            parts = text.split('\f')
        else:
            # Split evenly
            chunk_size = len(text) // page_count
            parts = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        pages = []
        for i, part in enumerate(parts, 1):
            pages.append({
                'page_num': i,
                'text': part,
                'char_count': len(part)
            })

        return pages

    def _assess_quality(self, text: str) -> PDFQuality:
        """
        Assess PDF extraction quality.

        Based on:
        - Text density
        - Character variety
        - Presence of garbled text
        """
        if not text or len(text) < 100:
            return PDFQuality.LOW

        # Calculate metrics
        char_count = len(text)
        unique_chars = len(set(text))
        words = text.split()
        word_count = len(words)

        # Check for garbled text (lots of special characters)
        special_char_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_char_ratio = special_char_count / char_count if char_count > 0 else 1.0

        # Check average word length
        avg_word_len = sum(len(w) for w in words) / word_count if word_count > 0 else 0

        # Scoring
        if special_char_ratio > 0.3:
            return PDFQuality.LOW
        elif avg_word_len < 3 or avg_word_len > 15:
            return PDFQuality.MEDIUM
        elif unique_chars < 50:
            return PDFQuality.MEDIUM
        else:
            return PDFQuality.HIGH

    def _build_result(
        self,
        full_text: str,
        pages: List[Dict],
        pdf_path: str,
        extraction_method: str
    ) -> Dict[str, Any]:
        """Build standardized PDF extraction result"""

        # Calculate metrics
        word_count = len(full_text.split())
        char_count = len(full_text)
        page_count = len(pages)

        # Generate hashes
        content_hash = hash_content(full_text, length=16)  # Phase 1 compatible
        file_hash = hash_file(pdf_path)

        # Assess quality
        quality = self._assess_quality(full_text)

        return {
            'status': 'success',
            'full_text': full_text,
            'page_count': page_count,
            'word_count': word_count,
            'character_count': char_count,
            'hash': content_hash,
            'pdf_hash_sha256': file_hash,
            'quality': quality.value,
            'is_scanned': False,
            'extraction_method': extraction_method,
            'ocr_confidence': None,
            'pages': pages,
            'error': None
        }
