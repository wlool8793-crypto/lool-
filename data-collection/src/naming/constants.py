"""
Constants and Mappings for Universal Legal Document Naming System
World-Class Legal RAG System
"""

from typing import Dict, List, Set
from enum import Enum

# =============================================================================
# COUNTRY CODES (ISO 3166-1 alpha-2)
# =============================================================================

COUNTRY_CODES: Dict[str, str] = {
    "BD": "Bangladesh",
    "IN": "India",
    "PK": "Pakistan",
    "US": "United States",
    "UK": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "NZ": "New Zealand",
    "SG": "Singapore",
    "MY": "Malaysia",
    "LK": "Sri Lanka",
    "NP": "Nepal",
    "INTL": "International",
}

# =============================================================================
# DOCUMENT TYPE CODES
# =============================================================================

class DocType(str, Enum):
    CASE = "CAS"          # Court case / judgment
    ACT = "ACT"           # Legislation / statute
    RULE = "RUL"          # Subsidiary legislation / rules
    ORDER = "ORD"         # Executive orders
    ORDINANCE = "ORN"     # Ordinances
    REGULATION = "REG"    # Regulations
    TREATY = "TRE"        # International treaties
    CONSTITUTION = "CON"  # Constitution
    NOTIFICATION = "NOT"  # Government notifications
    CIRCULAR = "CIR"      # Circulars
    GAZETTE = "GAZ"       # Gazette notifications


DOC_TYPE_NAMES: Dict[str, str] = {
    "CAS": "Case/Judgment",
    "ACT": "Act/Statute",
    "RUL": "Rules",
    "ORD": "Order",
    "ORN": "Ordinance",
    "REG": "Regulation",
    "TRE": "Treaty",
    "CON": "Constitution",
    "NOT": "Notification",
    "CIR": "Circular",
    "GAZ": "Gazette",
}

# =============================================================================
# COURT/SUBTYPE CODES BY COUNTRY
# =============================================================================

COURT_CODES: Dict[str, Dict[str, str]] = {
    "BD": {
        "AD": "Appellate Division",
        "HCD": "High Court Division",
        "SC": "Supreme Court",
        "DIS": "District Court",
        "TRI": "Tribunal",
        "LAB": "Labor Court",
        "FAM": "Family Court",
        "CYB": "Cyber Tribunal",
        "CTR": "Central",  # For Acts
        "DIV": "Divisional",
    },
    "IN": {
        "SC": "Supreme Court",
        "HC": "High Court",
        "DHC": "Delhi High Court",
        "BHC": "Bombay High Court",
        "MHC": "Madras High Court",
        "CHC": "Calcutta High Court",
        "KHC": "Karnataka High Court",
        "AHC": "Allahabad High Court",
        "GHC": "Gujarat High Court",
        "PHC": "Punjab & Haryana High Court",
        "DIS": "District Court",
        "TRI": "Tribunal",
        "NCLT": "National Company Law Tribunal",
        "NCLAT": "National Company Law Appellate Tribunal",
        "ITAT": "Income Tax Appellate Tribunal",
        "CTR": "Central",
        "STA": "State",
    },
    "PK": {
        "SC": "Supreme Court",
        "HC": "High Court",
        "LHC": "Lahore High Court",
        "SHC": "Sindh High Court",
        "PHC": "Peshawar High Court",
        "BHC": "Balochistan High Court",
        "FSC": "Federal Shariat Court",
        "DIS": "District Court",
        "TRI": "Tribunal",
        "FED": "Federal",
        "PRO": "Provincial",
    },
}

# =============================================================================
# SUBJECT CODES (15 Primary Categories)
# =============================================================================

class SubjectCode(str, Enum):
    CRIMINAL = "CRM"
    CIVIL = "CIV"
    CONSTITUTIONAL = "CON"
    PROPERTY = "PRO"
    FAMILY = "FAM"
    COMMERCIAL = "COM"
    TAX = "TAX"
    LABOR = "LAB"
    ENVIRONMENTAL = "ENV"
    INTELLECTUAL_PROPERTY = "IPR"
    ADMINISTRATIVE = "ADM"
    CONSUMER = "CSM"
    INFORMATION_TECHNOLOGY = "IT"
    INTERNATIONAL = "INT"
    HUMAN_RIGHTS = "HUM"
    GENERAL = "GEN"


SUBJECT_NAMES: Dict[str, str] = {
    "CRM": "Criminal Law",
    "CIV": "Civil Law",
    "CON": "Constitutional Law",
    "PRO": "Property Law",
    "FAM": "Family Law",
    "COM": "Commercial Law",
    "TAX": "Tax & Revenue",
    "LAB": "Labor & Employment",
    "ENV": "Environmental Law",
    "IPR": "Intellectual Property",
    "ADM": "Administrative Law",
    "CSM": "Consumer Protection",
    "IT": "Information Technology",
    "INT": "International Law",
    "HUM": "Human Rights",
    "GEN": "General",
}

# Subject keywords for auto-classification
SUBJECT_KEYWORDS: Dict[str, List[str]] = {
    "CRM": ["murder", "theft", "robbery", "criminal", "penal", "offense", "crime",
            "punishment", "bail", "fir", "police", "arrest", "section 302", "section 304",
            "crpc", "ipc", "evidence act", "narcotics", "arms act"],
    "CIV": ["contract", "tort", "negligence", "damages", "civil", "suit", "decree",
            "injunction", "specific performance", "breach", "cpc", "limitation"],
    "CON": ["constitution", "fundamental", "writ", "article", "amendment", "parliament",
            "legislative", "executive", "judicial review", "habeas corpus", "mandamus",
            "certiorari", "prohibition", "quo warranto"],
    "PRO": ["property", "land", "transfer", "sale deed", "mutation", "partition",
            "possession", "title", "easement", "mortgage", "lease", "tenancy"],
    "FAM": ["marriage", "divorce", "custody", "maintenance", "adoption", "guardianship",
            "succession", "inheritance", "family", "matrimonial", "dowry", "domestic violence"],
    "COM": ["company", "partnership", "contract", "commercial", "banking", "insurance",
            "securities", "arbitration", "negotiable", "corporate", "shareholder", "director"],
    "TAX": ["income tax", "tax", "revenue", "assessment", "refund", "penalty", "gst",
            "customs", "excise", "vat", "tribunal", "commissioner"],
    "LAB": ["labor", "employment", "industrial", "wages", "termination", "dismissal",
            "workman", "factory", "trade union", "strike", "lockout", "compensation"],
    "ENV": ["environment", "pollution", "forest", "wildlife", "conservation", "climate",
            "water", "air", "waste", "biodiversity", "green tribunal"],
    "IPR": ["patent", "copyright", "trademark", "design", "intellectual property",
            "infringement", "passing off", "trade secret", "geographical indication"],
    "ADM": ["administrative", "government", "tender", "contract", "service", "pension",
            "promotion", "transfer", "disciplinary", "public servant", "corruption"],
    "CSM": ["consumer", "deficiency", "service", "goods", "complaint", "compensation",
            "unfair trade", "misleading advertisement"],
    "IT": ["cyber", "digital", "electronic", "computer", "data", "privacy", "internet",
            "information technology", "hacking", "phishing"],
    "INT": ["international", "treaty", "convention", "extradition", "refugee", "asylum",
            "diplomatic", "foreign", "bilateral", "multilateral"],
    "HUM": ["human rights", "discrimination", "equality", "dignity", "freedom", "liberty",
            "right to life", "torture", "detention"],
}

# =============================================================================
# LEGAL STATUS CODES
# =============================================================================

class LegalStatus(str, Enum):
    ACTIVE = "ACT"         # Active / In force
    REPEALED = "REP"       # Repealed
    AMENDED = "AMD"        # Amended (but active)
    SUPERSEDED = "SUP"     # Superseded by new law
    OVERRULED = "OVR"      # Overruled (for cases)
    PENDING = "PND"        # Pending appeal
    EXPIRED = "EXP"        # Expired (temporary laws)


STATUS_NAMES: Dict[str, str] = {
    "ACT": "Active",
    "REP": "Repealed",
    "AMD": "Amended",
    "SUP": "Superseded",
    "OVR": "Overruled",
    "PND": "Pending",
    "EXP": "Expired",
}

# =============================================================================
# CITATION REPORTER CODES
# =============================================================================

REPORTER_CODES: Dict[str, Dict[str, str]] = {
    "BD": {
        "DLR": "Dhaka Law Reports",
        "BLD": "Bangladesh Legal Decisions",
        "BLC": "Bangladesh Law Chronicles",
        "BCR": "Bangladesh Case Reports",
        "MLR": "Mainstream Law Reports",
        "ADC": "Appellate Division Cases",
    },
    "IN": {
        "AIR": "All India Reporter",
        "SCC": "Supreme Court Cases",
        "SCR": "Supreme Court Reports",
        "SCALE": "Supreme Court Almanac",
        "JT": "Judgment Today",
        "MANU": "Manupatra",
        "SLP": "Special Leave Petition",
    },
    "PK": {
        "PLD": "Pakistan Legal Decisions",
        "PCRLJ": "Pakistan Criminal Law Journal",
        "CLC": "Civil Law Cases",
        "MLD": "Monthly Law Digest",
        "SCMR": "Supreme Court Monthly Review",
        "YLR": "Yearly Law Reports",
    },
}

# =============================================================================
# LANGUAGE CODES (ISO 639-1)
# =============================================================================

LANGUAGE_CODES: Dict[str, str] = {
    "en": "English",
    "bn": "Bengali",
    "hi": "Hindi",
    "ur": "Urdu",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
}

# =============================================================================
# PARTY NAME ABBREVIATIONS
# =============================================================================

PARTY_ABBREVIATIONS: Dict[str, str] = {
    "Secretary": "Secy",
    "Ministry": "Min",
    "Department": "Dept",
    "Government": "Gov",
    "Corporation": "Corp",
    "Limited": "Ltd",
    "Private": "Pvt",
    "Company": "Co",
    "Association": "Assn",
    "Federation": "Fed",
    "Organization": "Org",
    "Institution": "Inst",
    "University": "Univ",
    "Commission": "Comm",
    "Committee": "Cmte",
    "Authority": "Auth",
    "Board": "Brd",
    "Council": "Cncl",
    "Republic": "Rep",
    "State": "St",
    "Union": "Un",
    "Territory": "Ter",
    "District": "Dist",
    "Municipal": "Mun",
    "National": "Natl",
    "International": "Intl",
    "Bangladesh": "BD",
    "India": "IN",
    "Pakistan": "PK",
}

# Words to remove from party names
PARTY_REMOVE_WORDS: Set[str] = {
    "the", "of", "and", "&", "or", "in", "on", "at", "by", "for", "with",
    "through", "via", "etc", "etc.", "m/s", "m/s.", "mr.", "mr", "mrs.",
    "mrs", "ms.", "ms", "dr.", "dr", "shri", "smt", "kumari", "sri",
}

# =============================================================================
# FILENAME CONSTRAINTS
# =============================================================================

MAX_FILENAME_LENGTH = 100
MAX_IDENTIFIER_LENGTH = 30
MAX_DOCNUM_LENGTH = 15
HASH_LENGTH = 16
GLOBAL_ID_LENGTH = 10

# Valid characters in filename (excluding extension)
VALID_FILENAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

# =============================================================================
# ROMAN NUMERALS
# =============================================================================

ROMAN_NUMERALS: Dict[str, int] = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
    "XXI": 21, "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25,
    "XXVI": 26, "XXVII": 27, "XXVIII": 28, "XXIX": 29, "XXX": 30,
    "XXXI": 31, "XXXII": 32, "XXXIII": 33, "XXXIV": 34, "XXXV": 35,
    "XXXVI": 36, "XXXVII": 37, "XXXVIII": 38, "XXXIX": 39, "XL": 40,
    "XLI": 41, "XLII": 42, "XLIII": 43, "XLIV": 44, "XLV": 45,
    "XLVI": 46, "XLVII": 47, "XLVIII": 48, "XLIX": 49, "L": 50,
    "LI": 51, "LII": 52, "LIII": 53, "LIV": 54, "LV": 55,
    "LVI": 56, "LVII": 57, "LVIII": 58, "LIX": 59, "LX": 60,
}

# Reverse mapping: number to Roman numeral
NUMBERS_TO_ROMAN: Dict[int, str] = {v: k for k, v in ROMAN_NUMERALS.items()}
