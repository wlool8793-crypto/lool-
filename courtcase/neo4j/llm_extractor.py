"""
LLM-Powered Entity Extraction for Legal Knowledge Graph

Uses GPT-4 or Gemini to intelligently extract legal entities and relationships
from PDFs, text files, and databases.
"""
import os
import json
import re
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import LLM clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenAI not available. Install with: pip install google-generativeai")


class LLMExtractor:
    """
    Extract legal entities using LLM (GPT-4 or Gemini)

    Features:
    - Intelligent entity recognition
    - Relationship extraction
    - Structured JSON output
    - Batch processing
    - Error handling
    """

    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        """
        Initialize LLM extractor

        Args:
            model: Model name ('gpt-4', 'gpt-4-turbo', 'gemini-2.5-pro')
            api_key: API key (or from environment)
        """
        self.model = model

        if "gpt" in model.lower():
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not installed")

            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            self.client = OpenAI(api_key=api_key)
            self.provider = "openai"

        elif "gemini" in model.lower():
            # Check for Vertex AI Express key first (preferred)
            vertex_key = os.getenv("VERTEX_AI_EXPRESS_KEY")
            google_key = api_key or os.getenv("GOOGLE_API_KEY")

            if vertex_key:
                # Use Vertex AI Express REST API
                self.api_key = vertex_key
                self.provider = "vertex-express"
                self.client = None
                logger.info("Using Vertex AI Express API")
            elif google_key:
                # Use standard Google GenAI
                if not GENAI_AVAILABLE:
                    raise ImportError("Google GenAI package not installed")
                genai.configure(api_key=google_key)
                self.client = genai.GenerativeModel(model)
                self.provider = "gemini"
                logger.info("Using Google GenAI API")
            else:
                raise ValueError("GOOGLE_API_KEY or VERTEX_AI_EXPRESS_KEY not found in environment")

        else:
            raise ValueError(f"Unsupported model: {model}")

        logger.info(f"Initialized LLM extractor with {model}")

    def extract_legal_entities(self, text: str, context: str = "legal case") -> Dict[str, Any]:
        """
        Extract legal entities from text using LLM

        Args:
            text: Input text
            context: Context type ('legal case', 'statute', 'order')

        Returns:
            Dictionary with extracted entities
        """
        prompt = self._create_extraction_prompt(text, context)

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a legal text analysis expert. Extract structured information from legal documents."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=4000
                )
                result_text = response.choices[0].message.content

            elif self.provider == "vertex-express":
                # Use Vertex AI Express REST API
                result_text = self._call_vertex_express(prompt)

            else:  # gemini standard
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4000
                    )
                )
                result_text = response.text

            # Parse JSON
            result = json.loads(result_text)
            logger.debug(f"Extracted {len(result.get('entities', []))} entities")

            return result

        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            return {"entities": [], "relationships": [], "error": str(e)}

    def _call_vertex_express(self, prompt: str) -> str:
        """Call Vertex AI Express API"""
        url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{self.model}:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        params = {
            "key": self.api_key
        }

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4000,
            }
        }

        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        result = response.json()

        # Extract text from response
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                text = candidate["content"]["parts"][0].get("text", "")
                # Clean markdown code blocks if present
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                return text.strip()

        raise ValueError("No valid response from Vertex AI Express")

    def _create_extraction_prompt(self, text: str, context: str) -> str:
        """Create extraction prompt based on context"""

        if context == "legal case":
            return f"""
Extract legal entities and relationships from this case text. Return JSON with this structure:

{{
  "case": {{
    "citation": "citation if found (e.g., 60 DLR 20)",
    "title": "case title (Petitioner vs Respondent)",
    "date": "date string if found",
    "year": integer year,
    "case_type": "type (Civil/Criminal/Writ/etc)",
    "jurisdiction": "Bangladesh/India/Pakistan",
    "court": "court name",
    "summary": "brief summary (2-3 sentences)",
    "facts": "key facts",
    "holding": "court's decision/holding",
    "reasoning": "legal reasoning",
    "outcome": "final outcome"
  }},
  "judges": [
    {{"name": "judge full name", "title": "Justice/J."}}
  ],
  "parties": {{
    "petitioners": ["name1", "name2"],
    "respondents": ["name1", "name2"]
  }},
  "sections": [
    {{
      "section_id": "Section 10",
      "statute": "Code of Civil Procedure, 1908",
      "description": "brief description if mentioned"
    }}
  ],
  "principles": [
    {{
      "name": "legal principle name (e.g., res judicata)",
      "description": "how it was applied",
      "category": "Procedural Law/Substantive Law/etc"
    }}
  ],
  "citations": [
    {{
      "cited_case": "case name",
      "citation": "citation",
      "cited_for": "reason for citation"
    }}
  ],
  "topics": ["Revision", "Appeal", "etc"]
}}

CASE TEXT:
{text[:8000]}

Return ONLY valid JSON, no markdown or explanation.
"""

        elif context == "statute":
            return f"""
Extract statute structure from this text. Return JSON with this structure:

{{
  "statute": {{
    "name": "statute name",
    "short_name": "abbreviation",
    "country": "country",
    "year": integer
  }},
  "parts": [
    {{
      "part_number": "Part I/II/etc",
      "title": "part title",
      "sections": ["Section 1", "Section 2"]
    }}
  ],
  "sections": [
    {{
      "section_id": "Section 10",
      "title": "section title",
      "description": "what it covers",
      "part": "Part I"
    }}
  ],
  "definitions": [
    {{
      "term": "decree",
      "definition": "definition text",
      "section": "Section 2"
    }}
  ]
}}

STATUTE TEXT:
{text[:8000]}

Return ONLY valid JSON, no markdown or explanation.
"""

        else:  # order/rule
            return f"""
Extract order and rule structure. Return JSON:

{{
  "orders": [
    {{
      "order_id": "Order VI",
      "title": "order title",
      "rules": [
        {{
          "rule_number": 17,
          "text": "rule text",
          "description": "what it covers"
        }}
      ]
    }}
  ]
}}

TEXT:
{text[:8000]}

Return ONLY valid JSON, no markdown or explanation.
"""

    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract entities from PDF using LLM

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of extracted case dictionaries
        """
        import fitz  # PyMuPDF

        logger.info(f"Processing PDF: {pdf_path}")

        doc = fitz.open(pdf_path)
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        doc.close()

        # Split into chunks if too long
        chunks = self._split_text(full_text, max_length=8000)

        cases = []
        for idx, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {idx + 1}/{len(chunks)}")

            result = self.extract_legal_entities(chunk, context="legal case")

            if "case" in result and result["case"]:
                # Merge entities
                case_data = result["case"]
                case_data["judges"] = result.get("judges", [])
                case_data["parties"] = result.get("parties", {})
                case_data["sections"] = result.get("sections", [])
                case_data["principles"] = result.get("principles", [])
                case_data["citations"] = result.get("citations", [])
                case_data["topics"] = result.get("topics", [])

                # Add metadata
                case_data["source"] = str(pdf_path)
                case_data["extracted_at"] = datetime.now().isoformat()
                case_data["extracted_by"] = "llm_extractor"
                case_data["confidence_score"] = 0.85  # LLM extraction confidence

                cases.append(case_data)

        logger.info(f"Extracted {len(cases)} cases from PDF")
        return cases

    def extract_from_text_file(self, text_path: str, file_type: str = "statute") -> Dict:
        """
        Extract entities from text file

        Args:
            text_path: Path to text file
            file_type: Type ('statute', 'order')

        Returns:
            Dictionary with extracted entities
        """
        logger.info(f"Processing text file: {text_path}")

        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()

        result = self.extract_legal_entities(text, context=file_type)

        # Add metadata
        result["source"] = str(text_path)
        result["extracted_at"] = datetime.now().isoformat()
        result["extracted_by"] = "llm_extractor"

        return result

    def extract_from_database_case(self, case_record: Dict) -> Dict:
        """
        Extract enhanced entities from database case using LLM

        Args:
            case_record: Case record from database

        Returns:
            Enhanced case data
        """
        full_text = case_record.get("full_text", "")
        title = case_record.get("title", "")

        if not full_text:
            logger.warning(f"No full text for case: {title}")
            return case_record

        # Create combined text
        text = f"Title: {title}\n\n{full_text[:8000]}"

        result = self.extract_legal_entities(text, context="legal case")

        # Merge with existing data
        enhanced = case_record.copy()

        if "case" in result:
            # Add/update fields from LLM extraction
            enhanced.update({
                "llm_summary": result["case"].get("summary"),
                "llm_facts": result["case"].get("facts"),
                "llm_holding": result["case"].get("holding"),
                "llm_reasoning": result["case"].get("reasoning"),
                "llm_judges": result.get("judges", []),
                "llm_sections": result.get("sections", []),
                "llm_principles": result.get("principles", []),
                "llm_citations": result.get("citations", []),
                "llm_topics": result.get("topics", []),
                "extracted_at": datetime.now().isoformat(),
                "extracted_by": "llm_extractor",
                "confidence_score": 0.80
            })

        return enhanced

    def _split_text(self, text: str, max_length: int = 8000) -> List[str]:
        """Split text into chunks"""
        chunks = []
        current_chunk = ""

        # Split by paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            if len(current_chunk) + len(para) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
            else:
                current_chunk += "\n\n" + para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text[:max_length]]


# Convenience functions
def extract_pdf_with_llm(pdf_path: str, model: str = "gpt-4") -> List[Dict]:
    """
    Extract cases from PDF using LLM

    Args:
        pdf_path: Path to PDF
        model: LLM model to use

    Returns:
        List of extracted cases

    Example:
        cases = extract_pdf_with_llm("cpc2.pdf", model="gpt-4-turbo")
    """
    extractor = LLMExtractor(model=model)
    return extractor.extract_from_pdf(pdf_path)


def extract_statute_with_llm(text_path: str, model: str = "gpt-4") -> Dict:
    """
    Extract statute from text file using LLM

    Example:
        statute = extract_statute_with_llm("cpc.txt", model="gpt-4")
    """
    extractor = LLMExtractor(model=model)
    return extractor.extract_from_text_file(text_path, file_type="statute")
