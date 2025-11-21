"""
Embeddings Generator for RAG-Enhanced Legal Knowledge Graph

Generates embeddings using OpenAI's text-embedding-3-large model
and creates chunk nodes for Retrieval-Augmented Generation.
"""
import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")


@dataclass
class TextChunk:
    """Represents a text chunk for embeddings"""
    chunk_id: str
    text: str
    chunk_index: int
    source_id: str
    source_type: str  # 'case', 'section', 'statute'
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class EmbeddingsGenerator:
    """
    Generate embeddings for legal documents

    Features:
    - OpenAI text-embedding-3-large (1536 dimensions)
    - Intelligent text chunking (512 tokens, 50 overlap)
    - Batch processing
    - Multiple granularity levels (case, section, chunk)
    """

    def __init__(self, model: str = "text-embedding-3-large", api_key: Optional[str] = None):
        """
        Initialize embeddings generator

        Args:
            model: OpenAI embedding model
            api_key: API key (or from environment)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimension = 1536  # text-embedding-3-large dimension

        logger.info(f"Initialized embeddings generator with {model}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            List of floats (1536 dimensions)
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided, returning zero embedding")
            return [0.0] * self.dimension

        try:
            # Clean text
            text = self._clean_text(text)

            # Truncate if too long (max 8191 tokens for text-embedding-3-large)
            text = text[:32000]  # Approximate 8k tokens

            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return [0.0] * self.dimension

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts

        Returns:
            List of embeddings
        """
        if not texts:
            return []

        embeddings = []
        batch_size = 100  # OpenAI allows up to 2048

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                # Clean texts
                cleaned_batch = [self._clean_text(t)[:32000] for t in batch]

                response = self.client.embeddings.create(
                    model=self.model,
                    input=cleaned_batch,
                    encoding_format="float"
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i//batch_size + 1})")

            except Exception as e:
                logger.error(f"Batch embedding failed: {str(e)}")
                # Add zero embeddings for failed batch
                embeddings.extend([[0.0] * self.dimension] * len(batch))

        return embeddings

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 50,
        source_id: str = "",
        source_type: str = "case"
    ) -> List[TextChunk]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap size in tokens
            source_id: ID of source document
            source_type: Type of source

        Returns:
            List of TextChunk objects
        """
        if not text:
            return []

        # Approximate tokens by splitting on whitespace
        # 1 token ≈ 4 characters for English
        char_size = chunk_size * 4
        char_overlap = overlap * 4

        chunks = []
        text = self._clean_text(text)

        # Split into sentences for better chunk boundaries
        sentences = self._split_sentences(text)

        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > char_size and current_chunk:
                # Create chunk
                chunk = TextChunk(
                    chunk_id=f"{source_id}_chunk_{chunk_index}",
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    source_id=source_id,
                    source_type=source_type,
                    metadata={
                        "length": len(current_chunk),
                        "start_pos": chunk_index * (char_size - char_overlap)
                    }
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                # Keep last few sentences for context
                overlap_text = current_chunk[-char_overlap:] if len(current_chunk) > char_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence

        # Add final chunk
        if current_chunk.strip():
            chunk = TextChunk(
                chunk_id=f"{source_id}_chunk_{chunk_index}",
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                source_id=source_id,
                source_type=source_type,
                metadata={
                    "length": len(current_chunk),
                    "start_pos": chunk_index * (char_size - char_overlap)
                }
            )
            chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks

    def generate_case_embedding(self, case_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a legal case

        Args:
            case_data: Case dictionary with title, facts, holding, reasoning

        Returns:
            Embedding vector
        """
        # Combine relevant fields
        parts = []

        if case_data.get('title'):
            parts.append(f"Title: {case_data['title']}")

        if case_data.get('summary') or case_data.get('llm_summary'):
            parts.append(f"Summary: {case_data.get('llm_summary') or case_data.get('summary')}")

        if case_data.get('facts') or case_data.get('llm_facts'):
            parts.append(f"Facts: {case_data.get('llm_facts') or case_data.get('facts')}")

        if case_data.get('holding') or case_data.get('llm_holding'):
            parts.append(f"Holding: {case_data.get('llm_holding') or case_data.get('holding')}")

        if case_data.get('reasoning') or case_data.get('llm_reasoning'):
            parts.append(f"Reasoning: {case_data.get('llm_reasoning') or case_data.get('reasoning')}")

        text = "\n\n".join(parts)
        return self.generate_embedding(text)

    def generate_section_embedding(self, section_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a statute section

        Args:
            section_data: Section dictionary

        Returns:
            Embedding vector
        """
        parts = []

        if section_data.get('section_id'):
            parts.append(f"Section: {section_data['section_id']}")

        if section_data.get('title'):
            parts.append(f"Title: {section_data['title']}")

        if section_data.get('description'):
            parts.append(f"Description: {section_data['description']}")

        if section_data.get('text'):
            parts.append(f"Text: {section_data['text']}")

        text = "\n\n".join(parts)
        return self.generate_embedding(text)

    def _clean_text(self, text: str) -> str:
        """Clean text for embedding"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might cause issues
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        # This could be improved with nltk or spacy
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]


class Neo4jEmbeddingsLoader:
    """
    Load embeddings into Neo4j

    Features:
    - Create Chunk nodes
    - Add embedding properties to existing nodes
    - Create vector indexes
    - Link chunks to parent nodes
    """

    def __init__(self, driver):
        """
        Initialize loader

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver
        logger.info("Initialized Neo4j embeddings loader")

    def create_vector_indexes(self):
        """Create vector indexes in Neo4j"""
        logger.info("Creating vector indexes...")

        with self.driver.session() as session:
            # Create vector index for Case embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX case_embeddings IF NOT EXISTS
                    FOR (c:Case)
                    ON c.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                logger.info("✓ Created vector index for Case nodes")
            except Exception as e:
                logger.warning(f"Case vector index might already exist: {str(e)}")

            # Create vector index for Section embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX section_embeddings IF NOT EXISTS
                    FOR (s:Section)
                    ON s.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                logger.info("✓ Created vector index for Section nodes")
            except Exception as e:
                logger.warning(f"Section vector index might already exist: {str(e)}")

            # Create vector index for Chunk embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
                    FOR (ch:Chunk)
                    ON ch.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                logger.info("✓ Created vector index for Chunk nodes")
            except Exception as e:
                logger.warning(f"Chunk vector index might already exist: {str(e)}")

    def load_chunks(self, chunks: List[TextChunk]):
        """
        Load chunks into Neo4j

        Args:
            chunks: List of TextChunk objects with embeddings
        """
        if not chunks:
            return

        logger.info(f"Loading {len(chunks)} chunks to Neo4j...")

        with self.driver.session() as session:
            for chunk in chunks:
                try:
                    session.run("""
                        MERGE (ch:Chunk {chunk_id: $chunk_id})
                        SET ch.text = $text,
                            ch.chunk_index = $chunk_index,
                            ch.source_type = $source_type,
                            ch.embedding = $embedding,
                            ch.metadata = $metadata
                    """, {
                        'chunk_id': chunk.chunk_id,
                        'text': chunk.text,
                        'chunk_index': chunk.chunk_index,
                        'source_type': chunk.source_type,
                        'embedding': chunk.embedding or [],
                        'metadata': str(chunk.metadata)
                    })

                    # Link chunk to parent node
                    if chunk.source_type == 'case':
                        session.run("""
                            MATCH (c:Case {case_id: $source_id})
                            MATCH (ch:Chunk {chunk_id: $chunk_id})
                            MERGE (c)-[:HAS_CHUNK]->(ch)
                        """, {
                            'source_id': chunk.source_id,
                            'chunk_id': chunk.chunk_id
                        })
                    elif chunk.source_type == 'section':
                        session.run("""
                            MATCH (s:Section {section_id: $source_id})
                            MATCH (ch:Chunk {chunk_id: $chunk_id})
                            MERGE (s)-[:HAS_CHUNK]->(ch)
                        """, {
                            'source_id': chunk.source_id,
                            'chunk_id': chunk.chunk_id
                        })

                except Exception as e:
                    logger.error(f"Failed to load chunk {chunk.chunk_id}: {str(e)}")

        logger.info(f"✓ Loaded {len(chunks)} chunks")

    def update_case_embeddings(self, case_id: str, embedding: List[float]):
        """Update embedding for a Case node"""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Case {case_id: $case_id})
                SET c.embedding = $embedding
            """, {
                'case_id': case_id,
                'embedding': embedding
            })

    def update_section_embeddings(self, section_id: str, embedding: List[float]):
        """Update embedding for a Section node"""
        with self.driver.session() as session:
            session.run("""
                MATCH (s:Section {section_id: $section_id})
                SET s.embedding = $embedding
            """, {
                'section_id': section_id,
                'embedding': embedding
            })


# Convenience functions
def generate_embeddings_for_cases(cases: List[Dict], api_key: Optional[str] = None) -> List[Dict]:
    """
    Generate embeddings for a list of cases

    Args:
        cases: List of case dictionaries
        api_key: OpenAI API key

    Returns:
        Cases with embedding field added
    """
    generator = EmbeddingsGenerator(api_key=api_key)

    for case in cases:
        embedding = generator.generate_case_embedding(case)
        case['embedding'] = embedding

    return cases


def create_chunks_with_embeddings(
    text: str,
    source_id: str,
    source_type: str = "case",
    api_key: Optional[str] = None
) -> List[TextChunk]:
    """
    Create text chunks and generate embeddings

    Args:
        text: Input text
        source_id: Source document ID
        source_type: Type of source
        api_key: OpenAI API key

    Returns:
        List of TextChunk objects with embeddings
    """
    generator = EmbeddingsGenerator(api_key=api_key)

    # Create chunks
    chunks = generator.chunk_text(text, source_id=source_id, source_type=source_type)

    # Generate embeddings
    texts = [chunk.text for chunk in chunks]
    embeddings = generator.generate_batch_embeddings(texts)

    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding

    return chunks
