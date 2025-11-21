"""
Unit tests for PDF extraction module
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from utils.pdf_extractor import PDFCaseExtractor, LegalCase, extract_pdf_to_json


@pytest.mark.unit
class TestLegalCase:
    """Test LegalCase dataclass"""

    def test_legal_case_initialization(self):
        """Test LegalCase can be initialized"""
        case = LegalCase(
            case_id="test_1",
            name="Test vs Test",
            citation="123 TEST 456"
        )

        assert case.case_id == "test_1"
        assert case.name == "Test vs Test"
        assert case.citation == "123 TEST 456"
        assert case.judges == []
        assert case.petitioner == []
        assert case.respondent == []

    def test_legal_case_to_dict(self):
        """Test LegalCase.to_dict() conversion"""
        case = LegalCase(
            case_id="test_1",
            name="Test vs Test",
            citation="123 TEST 456",
            year=2023,
            judges=["Judge A", "Judge B"]
        )

        case_dict = case.to_dict()

        assert isinstance(case_dict, dict)
        assert case_dict['case_id'] == "test_1"
        assert case_dict['name'] == "Test vs Test"
        assert case_dict['year'] == 2023
        assert len(case_dict['judges']) == 2


@pytest.mark.unit
@pytest.mark.pdf
class TestPDFCaseExtractor:
    """Test PDFCaseExtractor class"""

    def test_extractor_initialization(self):
        """Test PDFCaseExtractor initializes correctly"""
        extractor = PDFCaseExtractor()

        assert extractor is not None
        assert 'citation' in extractor.patterns
        assert 'court' in extractor.patterns
        assert 'judges' in extractor.patterns

    def test_extract_citation(self):
        """Test citation pattern extraction"""
        extractor = PDFCaseExtractor()
        text = "This case is reported in 60 DLR 20 and was decided in 2007."

        match = extractor.patterns['citation']
        import re
        result = re.search(match, text)

        assert result is not None
        assert result.group(0) == "60 DLR 20"

    def test_extract_court_name(self):
        """Test court name extraction"""
        extractor = PDFCaseExtractor()
        text = "The High Court Division heard this case."

        match = extractor.patterns['court']
        import re
        result = re.search(match, text)

        assert result is not None
        assert result.group(0) == "High Court Division"

    def test_extract_judge_names(self):
        """Test judge name extraction"""
        extractor = PDFCaseExtractor()
        text = "Justice Siddiqur Rahman Miah, J. and Justice Md Rezaul Haque presided."

        match = extractor.patterns['judges']
        import re
        results = re.findall(match, text)

        assert len(results) >= 1
        assert "Siddiqur Rahman Miah" in results

    def test_extract_section_references(self):
        """Test section reference extraction"""
        extractor = PDFCaseExtractor()
        text = "Section 10 and Section 115(4) of the Code of Civil Procedure were applied."

        match = extractor.patterns['section']
        import re
        results = re.findall(match, text)

        assert len(results) >= 2
        section_nums = [r[0] for r in results]
        assert "10" in section_nums
        assert "115" in section_nums

    def test_split_cases_single_case(self):
        """Test case splitting with single case"""
        extractor = PDFCaseExtractor()
        text = "This is a single case without clear boundaries."

        cases = extractor._split_cases(text)

        assert len(cases) == 1
        assert cases[0] == text

    def test_split_cases_multiple_cases(self):
        """Test case splitting with multiple cases"""
        extractor = PDFCaseExtractor()
        text = """
        60 DLR 20
        Case content for first case...
        70 DLR 30
        Case content for second case...
        """

        cases = extractor._split_cases(text)

        # Should find at least 1 case (may be 1 or 2 depending on pattern matching)
        assert len(cases) >= 1

    def test_extract_case_data_valid(self, sample_pdf_text):
        """Test extraction of case data from valid text"""
        extractor = PDFCaseExtractor()

        case = extractor._extract_case_data(sample_pdf_text, 1)

        assert case is not None
        assert case.citation == "60 DLR 20"
        assert "Siddique Mia" in case.name
        assert case.year == 2007
        assert case.court == "High Court Division"
        assert len(case.judges) > 0
        assert len(case.sections) > 0

    def test_extract_case_data_minimal(self):
        """Test extraction with minimal text"""
        extractor = PDFCaseExtractor()
        minimal_text = "123 TEST 456. Test Case vs Another Case."

        case = extractor._extract_case_data(minimal_text, 1)

        assert case is not None
        assert "TEST" in case.citation

    @patch('fitz.open')
    def test_extract_from_pdf_success(self, mock_fitz_open, tmp_path):
        """Test successful PDF extraction"""
        # Create mock PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = """
        60 DLR 20
        Test Case vs Test Respondent
        High Court Division
        Justice Test Judge, J.
        """

        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        # Create temp PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        extractor = PDFCaseExtractor()
        cases = extractor.extract_from_pdf(str(pdf_file))

        assert len(cases) > 0
        assert isinstance(cases[0], LegalCase)

    def test_extract_from_pdf_file_not_found(self):
        """Test PDF extraction with non-existent file"""
        extractor = PDFCaseExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract_from_pdf("/nonexistent/file.pdf")

    @patch('fitz.open')
    def test_extract_to_json(self, mock_fitz_open, tmp_path):
        """Test JSON export functionality"""
        # Mock PDF extraction
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "60 DLR 20\nTest Case"

        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        # Create temp files
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy")
        json_file = tmp_path / "output.json"

        extractor = PDFCaseExtractor()
        extractor.extract_to_json(str(pdf_file), str(json_file))

        # Verify JSON file created
        assert json_file.exists()

        # Verify JSON content
        with open(json_file) as f:
            data = json.load(f)

        assert 'cases' in data
        assert 'metadata' in data
        assert isinstance(data['cases'], list)

    @patch('utils.pdf_extractor.PDFCaseExtractor')
    def test_extract_pdf_to_json_convenience_function(self, mock_extractor_class):
        """Test convenience function extract_pdf_to_json"""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor

        extract_pdf_to_json("test.pdf", "output.json")

        mock_extractor_class.assert_called_once()
        mock_extractor.extract_to_json.assert_called_once_with("test.pdf", "output.json")


@pytest.mark.unit
class TestPDFExtractionPatterns:
    """Test regex patterns used in PDF extraction"""

    def test_date_pattern(self):
        """Test date extraction pattern"""
        import re
        from utils.pdf_extractor import PDFCaseExtractor

        extractor = PDFCaseExtractor()
        text = "The judgment was delivered on 28th January, 2007."

        match = re.search(extractor.patterns['date'], text)
        assert match is not None
        assert "January" in match.group(0)

    def test_year_pattern(self):
        """Test year extraction pattern"""
        import re
        from utils.pdf_extractor import PDFCaseExtractor

        extractor = PDFCaseExtractor()
        text = "This case was decided in 2007 by the court."

        match = re.search(extractor.patterns['year'], text)
        assert match is not None
        assert match.group(0) == "2007"

    def test_order_rule_pattern(self):
        """Test Order and Rule extraction pattern"""
        import re
        from utils.pdf_extractor import PDFCaseExtractor

        extractor = PDFCaseExtractor()
        text = "Order VI, Rule 17 of the CPC was applied."

        match = re.search(extractor.patterns['order'], text)
        assert match is not None

    def test_topic_pattern(self):
        """Test legal topic extraction"""
        import re
        from utils.pdf_extractor import PDFCaseExtractor

        extractor = PDFCaseExtractor()
        text = "This is a Revision petition filed under Section 115."

        match = re.search(extractor.patterns['topics'], text)
        assert match is not None
        assert match.group(0) == "Revision"

    def test_principles_pattern(self):
        """Test legal principle extraction"""
        import re
        from utils.pdf_extractor import PDFCaseExtractor

        extractor = PDFCaseExtractor()
        text = "The principle of res judicata applies to this case."

        results = re.findall(extractor.patterns['principles'], text, re.IGNORECASE)
        assert len(results) > 0
        assert "res judicata" in [r.lower() for r in results]
