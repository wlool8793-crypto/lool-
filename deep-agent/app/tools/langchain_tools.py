import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from langchain.tools import Tool, BaseTool
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.utilities import PythonREPL, GoogleSearchAPIWrapper, WikipediaAPIWrapper
from langchain.tools.python.tool import PythonAstREPLTool
from langchain.tools.file_management import ReadFileTool, WriteFileTool
from langchain.tools.bing_search import BingSearchRun
from langchain.tools.shell import ShellTool
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from app.services.cache_service import cache_service
from app.core.config import settings
from app.models import ToolExecution
import logging

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    SEARCH = "search"
    FILE_OPERATIONS = "file_operations"
    CODE_EXECUTION = "code_execution"
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"
    AI_LLM = "ai_llm"
    DATABASE = "database"
    WEB_SCRAPING = "web_scraping"
    CALCULATION = "calculation"
    SYSTEM = "system"


class LangChainToolManager:
    """
    Advanced LangChain tool management and integration system
    """

    def __init__(self):
        self.tools = {}
        self.tool_categories = {}
        self.llm = None
        self.chat_llm = None
        self.embeddings = None
        self.memory = None
        self.vector_stores = {}
        self.chains = {}
        self.agents = {}

        # Initialize LangChain components
        self._initialize_langchain_components()

        # Register built-in tools
        self._register_builtin_tools()

    def _initialize_langchain_components(self):
        """Initialize LangChain core components"""
        try:
            # Initialize LLMs
            if settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.7,
                    max_tokens=1000
                )
                self.chat_llm = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.7,
                    max_tokens=1000
                )
                self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            else:
                logger.warning("OpenAI API key not found. Using mock LLM.")
                self._create_mock_llm()

            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )

        except Exception as e:
            logger.error(f"Error initializing LangChain components: {e}")
            self._create_mock_llm()

    def _create_mock_llm(self):
        """Create mock LLM for development/testing"""
        class MockLLM:
            def __call__(self, prompt, **kwargs):
                return f"Mock response for: {prompt[:100]}..."

            def predict(self, text, **kwargs):
                return f"Mock prediction for: {text[:100]}..."

        self.llm = MockLLM()
        self.chat_llm = MockLLM()

    def _register_builtin_tools(self):
        """Register built-in LangChain tools"""

        # Search tools
        if settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID:
            google_search = GoogleSearchAPIWrapper(
                google_api_key=settings.GOOGLE_API_KEY,
                google_cse_id=settings.GOOGLE_CSE_ID
            )
            self.register_tool(
                tool_name="google_search",
                tool_instance=google_search,
                category=ToolCategory.SEARCH,
                description="Search the web using Google"
            )

        # Wikipedia tool
        wikipedia = WikipediaAPIWrapper()
        self.register_tool(
            tool_name="wikipedia_search",
            tool_instance=wikipedia,
            category=ToolCategory.SEARCH,
            description="Search Wikipedia for information"
        )

        # File operations
        read_file = ReadFileTool()
        write_file = WriteFileTool()
        self.register_tool(
            tool_name="read_file",
            tool_instance=read_file,
            category=ToolCategory.FILE_OPERATIONS,
            description="Read and analyze file contents"
        )
        self.register_tool(
            tool_name="write_file",
            tool_instance=write_file,
            category=ToolCategory.FILE_OPERATIONS,
            description="Write content to files"
        )

        # Python execution
        python_repl = PythonAstREPLTool()
        self.register_tool(
            tool_name="python_execution",
            tool_instance=python_repl,
            category=ToolCategory.CODE_EXECUTION,
            description="Execute Python code safely"
        )

        # Shell operations (if enabled)
        if settings.ENABLE_SHELL_TOOLS:
            shell_tool = ShellTool()
            self.register_tool(
                tool_name="shell_command",
                tool_instance=shell_tool,
                category=ToolCategory.SYSTEM,
                description="Execute shell commands"
            )

        # Calculator tool
        from langchain.tools import Tool
        from langchain.chains import LLMMathChain
        math_chain = LLMMathChain(llm=self.llm)
        calculator = Tool(
            name="calculator",
            func=math_chain.run,
            description="Useful for performing mathematical calculations"
        )
        self.register_tool(
            tool_name="calculator",
            tool_instance=calculator,
            category=ToolCategory.CALCULATION,
            description="Perform mathematical calculations"
        )

    def register_tool(
        self,
        tool_name: str,
        tool_instance: Union[BaseTool, Tool, Callable],
        category: ToolCategory,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register a new tool"""
        tool_id = str(uuid.uuid4())

        tool_data = {
            "id": tool_id,
            "name": tool_name,
            "instance": tool_instance,
            "category": category,
            "description": description,
            "metadata": metadata or {},
            "registered_at": datetime.utcnow().isoformat(),
            "usage_count": 0
        }

        self.tools[tool_name] = tool_data

        # Add to category
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        self.tool_categories[category].append(tool_name)

        logger.info(f"Registered tool: {tool_name} in category {category.value}")

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool by name"""
        return self.tools.get(tool_name)

    def get_tools_by_category(self, category: ToolCategory) -> List[Dict[str, Any]]:
        """Get all tools in a category"""
        category_tools = self.tool_categories.get(category, [])
        return [self.tools[tool_name] for tool_name in category_tools]

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools"""
        return list(self.tools.values())

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool with proper error handling"""
        tool_data = self.tools.get(tool_name)
        if not tool_data:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "tool_name": tool_name
            }

        try:
            # Record execution start
            execution_id = str(uuid.uuid4())
            start_time = datetime.utcnow()

            # Prepare tool input
            if isinstance(tool_input, dict):
                # Add context to tool input if provided
                if context:
                    tool_input["context"] = context
                formatted_input = tool_input
            else:
                formatted_input = str(tool_input)

            # Execute tool
            tool_instance = tool_data["instance"]

            if hasattr(tool_instance, 'run'):
                # LangChain tool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, tool_instance.run, formatted_input
                )
            elif hasattr(tool_instance, '__call__'):
                # Callable tool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, tool_instance, formatted_input
                )
            elif hasattr(tool_instance, 'arun'):
                # Async tool
                result = await tool_instance.arun(formatted_input)
            else:
                raise ValueError(f"Tool {tool_name} has no executable method")

            # Record execution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            tool_data["usage_count"] += 1

            # Store execution result
            execution_record = {
                "id": execution_id,
                "tool_name": tool_name,
                "input": formatted_input,
                "output": result,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "success": True
            }

            # Cache execution result
            cache_key = f"tool_execution:{tool_name}:{execution_id}"
            await cache_service.set(cache_key, execution_record, ttl=3600)

            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "execution_id": execution_id,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "execution_id": execution_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    def create_agent(
        self,
        agent_name: str,
        tools: List[str],
        agent_type: AgentType = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory: bool = True,
        verbose: bool = False
    ) -> str:
        """Create a LangChain agent with specified tools"""

        # Get tool instances
        tool_instances = []
        for tool_name in tools:
            tool_data = self.tools.get(tool_name)
            if tool_data:
                tool_instances.append(tool_data["instance"])

        if not tool_instances:
            raise ValueError("No valid tools provided for agent")

        # Initialize agent memory if requested
        agent_memory = self.memory if memory else None

        # Create agent
        try:
            agent = initialize_agent(
                tools=tool_instances,
                llm=self.chat_llm,
                agent=agent_type,
                memory=agent_memory,
                verbose=verbose,
                handle_parsing_errors=True
            )

            # Store agent
            agent_id = str(uuid.uuid4())
            self.agents[agent_name] = {
                "id": agent_id,
                "name": agent_name,
                "agent": agent,
                "tools": tools,
                "agent_type": agent_type,
                "created_at": datetime.utcnow().isoformat(),
                "usage_count": 0
            }

            logger.info(f"Created agent: {agent_name} with {len(tools)} tools")
            return agent_id

        except Exception as e:
            logger.error(f"Error creating agent {agent_name}: {e}")
            raise

    async def run_agent(
        self,
        agent_name: str,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a LangChain agent"""
        agent_data = self.agents.get(agent_name)
        if not agent_data:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found"
            }

        try:
            # Prepare input with context
            full_input = input_text
            if context:
                context_str = json.dumps(context, indent=2)
                full_input = f"Context: {context_str}\n\nTask: {input_text}"

            # Run agent
            start_time = datetime.utcnow()
            result = await asyncio.get_event_loop().run_in_executor(
                None, agent_data["agent"].run, full_input
            )

            # Update usage count
            agent_data["usage_count"] += 1

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "result": result,
                "agent_name": agent_name,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_name": agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    def create_chain(
        self,
        chain_name: str,
        chain_type: str,
        prompt_template: Optional[str] = None,
        **kwargs
    ) -> str:
        """Create a LangChain chain"""
        try:
            if chain_type == "conversation":
                chain = ConversationChain(
                    llm=self.chat_llm,
                    memory=self.memory,
                    verbose=kwargs.get("verbose", False)
                )
            elif chain_type == "llm":
                if prompt_template:
                    prompt = PromptTemplate(
                        template=prompt_template,
                        input_variables=kwargs.get("input_variables", ["input"])
                    )
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                else:
                    chain = LLMChain(llm=self.llm)
            elif chain_type == "summarize":
                chain = load_summarize_chain(self.llm, chain_type="map_reduce")
            elif chain_type == "qa":
                chain = load_qa_chain(self.llm, chain_type="stuff")
            else:
                raise ValueError(f"Unknown chain type: {chain_type}")

            # Store chain
            chain_id = str(uuid.uuid4())
            self.chains[chain_name] = {
                "id": chain_id,
                "name": chain_name,
                "chain": chain,
                "type": chain_type,
                "created_at": datetime.utcnow().isoformat(),
                "usage_count": 0
            }

            logger.info(f"Created chain: {chain_name} of type {chain_type}")
            return chain_id

        except Exception as e:
            logger.error(f"Error creating chain {chain_name}: {e}")
            raise

    async def run_chain(
        self,
        chain_name: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a LangChain chain"""
        chain_data = self.chains.get(chain_name)
        if not chain_data:
            return {
                "success": False,
                "error": f"Chain '{chain_name}' not found"
            }

        try:
            # Run chain
            start_time = datetime.utcnow()
            result = await asyncio.get_event_loop().run_in_executor(
                None, chain_data["chain"].run, **inputs
            )

            # Update usage count
            chain_data["usage_count"] += 1

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "result": result,
                "chain_name": chain_name,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error running chain {chain_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chain_name": chain_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    def create_vector_store(
        self,
        store_name: str,
        documents: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a vector store for document retrieval"""
        try:
            if not self.embeddings:
                raise ValueError("Embeddings not initialized")

            # Convert text documents to LangChain documents
            from langchain.schema import Document
            langchain_docs = []
            for i, doc_text in enumerate(documents):
                doc = Document(
                    page_content=doc_text,
                    metadata={"source": f"doc_{i}", **(metadata or {})}
                )
                langchain_docs.append(doc)

            # Split documents
            split_docs = self.text_splitter.split_documents(langchain_docs)

            # Create vector store
            vector_store = FAISS.from_documents(split_docs, self.embeddings)

            # Store vector store
            store_id = str(uuid.uuid4())
            self.vector_stores[store_name] = {
                "id": store_id,
                "name": store_name,
                "vector_store": vector_store,
                "document_count": len(split_docs),
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            logger.info(f"Created vector store: {store_name} with {len(split_docs)} documents")
            return store_id

        except Exception as e:
            logger.error(f"Error creating vector store {store_name}: {e}")
            raise

    async def search_vector_store(
        self,
        store_name: str,
        query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """Search a vector store"""
        store_data = self.vector_stores.get(store_name)
        if not store_data:
            return {
                "success": False,
                "error": f"Vector store '{store_name}' not found"
            }

        try:
            # Search vector store
            results = store_data["vector_store"].similarity_search(query, k=k)

            return {
                "success": True,
                "results": results,
                "store_name": store_name,
                "query": query,
                "result_count": len(results),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error searching vector store {store_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "store_name": store_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    def create_retrieval_qa_chain(
        self,
        chain_name: str,
        store_name: str,
        chain_type: str = "stuff"
    ) -> str:
        """Create a retrieval QA chain"""
        store_data = self.vector_stores.get(store_name)
        if not store_data:
            raise ValueError(f"Vector store '{store_name}' not found")

        try:
            # Create retrieval QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.chat_llm,
                chain_type=chain_type,
                retriever=store_data["vector_store"].as_retriever()
            )

            # Store chain
            chain_id = str(uuid.uuid4())
            self.chains[chain_name] = {
                "id": chain_id,
                "name": chain_name,
                "chain": qa_chain,
                "type": "retrieval_qa",
                "vector_store": store_name,
                "created_at": datetime.utcnow().isoformat(),
                "usage_count": 0
            }

            logger.info(f"Created retrieval QA chain: {chain_name}")
            return chain_id

        except Exception as e:
            logger.error(f"Error creating retrieval QA chain {chain_name}: {e}")
            raise

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        stats = {
            "total_tools": len(self.tools),
            "tools_by_category": {},
            "total_executions": sum(tool["usage_count"] for tool in self.tools.values()),
            "top_tools": sorted(
                self.tools.values(),
                key=lambda x: x["usage_count"],
                reverse=True
            )[:10]
        }

        for category, tool_names in self.tool_categories.items():
            stats["tools_by_category"][category.value] = len(tool_names)

        return stats

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent usage statistics"""
        return {
            "total_agents": len(self.agents),
            "total_executions": sum(agent["usage_count"] for agent in self.agents.values()),
            "agents": [
                {
                    "name": agent["name"],
                    "usage_count": agent["usage_count"],
                    "tools_count": len(agent["tools"]),
                    "created_at": agent["created_at"]
                }
                for agent in self.agents.values()
            ]
        }

    def get_chain_stats(self) -> Dict[str, Any]:
        """Get chain usage statistics"""
        return {
            "total_chains": len(self.chains),
            "total_executions": sum(chain["usage_count"] for chain in self.chains.values()),
            "chains_by_type": {},
            "chains": [
                {
                    "name": chain["name"],
                    "type": chain["type"],
                    "usage_count": chain["usage_count"],
                    "created_at": chain["created_at"]
                }
                for chain in self.chains.values()
            ]
        }

    async def process_document(
        self,
        document_path: str,
        document_type: str = "text"
    ) -> Dict[str, Any]:
        """Process and load documents into the system"""
        try:
            # Load document based on type
            if document_type == "text":
                loader = TextLoader(document_path)
            elif document_type == "pdf":
                loader = PyPDFLoader(document_path)
            elif document_type == "csv":
                loader = CSVLoader(document_path)
            elif document_type == "web":
                loader = WebBaseLoader(document_path)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")

            # Load documents
            documents = loader.load()

            # Split documents
            split_docs = self.text_splitter.split_documents(documents)

            # Create vector store
            store_name = f"doc_{uuid.uuid4().hex[:8]}"
            store_id = self.create_vector_store(
                store_name,
                [doc.page_content for doc in split_docs],
                metadata={"source": document_path, "type": document_type}
            )

            return {
                "success": True,
                "document_path": document_path,
                "document_type": document_type,
                "document_count": len(documents),
                "chunk_count": len(split_docs),
                "store_name": store_name,
                "store_id": store_id,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing document {document_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_path": document_path,
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
langchain_tool_manager = LangChainToolManager()