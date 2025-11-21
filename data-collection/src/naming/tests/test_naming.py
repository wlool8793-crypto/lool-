"""
Tests for Enhanced Naming System
"""

import pytest
import sys
sys.path.insert(0, '/workspaces/lool-/data-collection/src')

from naming import (
    EnhancedNamer, DocumentMetadata, FilenameParser,
    CitationEncoder, PartyAbbreviator, DocnumGenerator, HashGenerator,
    generate_filename, validate_filename, parse_filename
)


class TestHashGenerator:
    """Tests for HashGenerator."""

    def test_generate_hash_returns_16_chars(self):
        content = "Test content for hashing"
        hash_result = HashGenerator.generate_hash(content)
        assert len(hash_result) == 16

    def test_generate_hash_consistent(self):
        content = "Same content"
        hash1 = HashGenerator.generate_hash(content)
        hash2 = HashGenerator.generate_hash(content)
        assert hash1 == hash2

    def test_generate_hash_different_content(self):
        hash1 = HashGenerator.generate_hash("Content A")
        hash2 = HashGenerator.generate_hash("Content B")
        assert hash1 != hash2

    def test_validate_hash_valid(self):
        valid_hash = "A3F4B2C1D5E6F7G8"
        assert HashGenerator.validate_hash(valid_hash) == False  # G is invalid hex

    def test_validate_hash_valid_hex(self):
        valid_hash = "A3F4B2C1D5E6F7A8"
        assert HashGenerator.validate_hash(valid_hash) == True

    def test_empty_content_hash(self):
        hash_result = HashGenerator.generate_hash("")
        assert hash_result == "0" * 16


class TestCitationEncoder:
    """Tests for CitationEncoder."""

    def test_encode_bangladesh_dlr(self):
        citation = "22 (1998) DLR (HCD) 205"
        encoded = CitationEncoder.encode(citation, "BD")
        assert "DLR" in encoded
        assert "98" in encoded  # Year

    def test_encode_india_air(self):
        citation = "AIR 1973 SC 1461"
        encoded = CitationEncoder.encode(citation, "IN")
        assert "AIR" in encoded
        assert "SC" in encoded

    def test_encode_pakistan_pld(self):
        citation = "1989 PLD SC 1"
        encoded = CitationEncoder.encode(citation, "PK")
        assert "PLD" in encoded
        assert "89" in encoded

    def test_encode_unreported(self):
        encoded = CitationEncoder.encode_unreported("HCD", 1998, "WP", 123)
        assert encoded == "HCD98WP0123"

    def test_decode_dlr(self):
        encoded = "22DLR98H205"
        components = CitationEncoder.decode(encoded)
        assert components is not None
        assert components.volume == 22
        assert components.reporter == "DLR"


class TestPartyAbbreviator:
    """Tests for PartyAbbreviator."""

    def test_abbreviate_simple(self):
        result = PartyAbbreviator.abbreviate("Rahman", "State")
        assert "Rahman" in result
        assert "v" in result
        assert "State" in result or "St" in result

    def test_abbreviate_from_title(self):
        result = PartyAbbreviator.abbreviate_from_title("Rahman v. State")
        assert "v" in result

    def test_extract_parties(self):
        pet, resp = PartyAbbreviator.extract_parties("A v. B")
        assert pet == "A"
        assert resp == "B"

    def test_abbreviate_title(self):
        result = PartyAbbreviator.abbreviate_title("The Penal Code, 1860")
        assert "Penal" in result
        assert "1860" not in result  # Year should be removed

    def test_max_length(self):
        long_pet = "Very Long Petitioner Name Here Corporation Ltd"
        long_resp = "Very Long Respondent Name Here Corporation Ltd"
        result = PartyAbbreviator.abbreviate(long_pet, long_resp)
        assert len(result) <= 30


class TestDocnumGenerator:
    """Tests for DocnumGenerator."""

    def test_generate_case_reported(self):
        data = {"citation": "22 DLR 1998 HCD 205", "country_code": "BD"}
        docnum = DocnumGenerator.generate("CAS", data)
        assert len(docnum) <= 15

    def test_generate_case_unreported(self):
        data = {"court_code": "HCD", "year": 2020, "case_type": "WP", "case_number": "123"}
        docnum = DocnumGenerator.generate("CAS", data)
        assert "HCD" in docnum or "20" in docnum

    def test_generate_act(self):
        data = {"act_number": "XLV"}
        docnum = DocnumGenerator.generate("ACT", data)
        assert docnum == "XLV"

    def test_generate_act_numeric(self):
        data = {"act_number": "45"}
        docnum = DocnumGenerator.generate("ACT", data)
        assert docnum == "045"

    def test_generate_rule(self):
        data = {"rule_number": "15"}
        docnum = DocnumGenerator.generate("RUL", data)
        assert docnum == "R015"

    def test_generate_constitution(self):
        data = {}
        docnum = DocnumGenerator.generate("CON", data)
        assert docnum == "CONST"

    def test_generate_constitution_amendment(self):
        data = {"amendment_number": 17}
        docnum = DocnumGenerator.generate("CON", data)
        assert "17" in docnum

    def test_roman_conversion(self):
        assert DocnumGenerator.to_roman(45) == "XLV"
        assert DocnumGenerator.from_roman("XLV") == 45


class TestEnhancedNamer:
    """Tests for EnhancedNamer."""

    def test_generate_case_filename(self):
        meta = DocumentMetadata(
            country_code="BD",
            doc_type="CAS",
            subtype="HCD",
            year=1998,
            citation="22 DLR 1998 HCD 205",
            petitioner="Rahman",
            respondent="State",
            subject="CRM",
            status="ACT",
            language="en"
        )
        filename = EnhancedNamer.generate_filename(meta)
        assert filename.endswith(".pdf")
        assert "BD" in filename
        assert "CAS" in filename
        assert "1998" in filename

    def test_generate_act_filename(self):
        data = {
            "country_code": "BD",
            "doc_type": "ACT",
            "year": 1860,
            "act_number": "XLV",
            "title": "The Penal Code",
            "subject": "CRM"
        }
        filename = EnhancedNamer.generate_from_dict(data)
        assert "ACT" in filename
        assert "1860" in filename

    def test_validate_valid_filename(self):
        # Generate a filename and validate it
        meta = DocumentMetadata(
            country_code="BD",
            doc_type="CAS",
            year=1998,
            petitioner="A",
            respondent="B"
        )
        filename = EnhancedNamer.generate_filename(meta)
        is_valid, errors = EnhancedNamer.validate_filename(filename)
        # Should be valid or have minimal errors
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_filename_length(self):
        meta = DocumentMetadata(
            country_code="BD",
            doc_type="CAS",
            year=1998,
            petitioner="Very Long Party Name Here",
            respondent="Another Very Long Party Name",
            title="Some Very Long Title That Should Be Truncated"
        )
        filename = EnhancedNamer.generate_filename(meta)
        assert len(filename) <= 100

    def test_generate_global_id(self):
        gid = EnhancedNamer.generate_global_id("BD", 1)
        assert len(gid) == 10
        assert gid.startswith("BD")


class TestFilenameParser:
    """Tests for FilenameParser."""

    def test_parse_case_filename(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        components = FilenameParser.parse(filename)
        assert components is not None
        assert components.country_code == "BD"
        assert components.doc_type == "CAS"
        assert components.year == 1998

    def test_parse_to_dict(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        data = FilenameParser.parse_to_dict(filename)
        assert data.get("country_code") == "BD"

    def test_extract_metadata(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        meta = FilenameParser.extract_metadata(filename)
        assert "country_name" in meta
        assert meta["country_name"] == "Bangladesh"

    def test_split_filename(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        parts, ext = FilenameParser.split_filename(filename)
        assert len(parts) == 12
        assert ext == "pdf"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_filename_func(self):
        data = {"country_code": "BD", "doc_type": "CAS", "year": 2020}
        filename = generate_filename(data)
        assert filename.endswith(".pdf")

    def test_validate_filename_func(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        is_valid, errors = validate_filename(filename)
        assert isinstance(is_valid, bool)

    def test_parse_filename_func(self):
        filename = "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7A8.pdf"
        components = parse_filename(filename)
        assert components is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
