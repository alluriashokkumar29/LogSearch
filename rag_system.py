from typing import List, Dict, Any, Optional
import logging
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from config import config
from data_processor import DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """Handles RAG implementation with vector store and LLM integration."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.retrieval_chain = None
        
        try:
            self._initialize_embeddings()
            self._initialize_llm()
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def _initialize_embeddings(self):
        """Initialize OpenAI embeddings."""
        if config is None:
            raise ValueError("Config not initialized")
        
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=config.openai_api_key,
                model=config.embedding_model
            )
            logger.info(f"Embeddings initialized with model: {config.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize OpenAI LLM."""
        if config is None:
            raise ValueError("Config not initialized")
        
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        try:
            self.llm = ChatOpenAI(
                openai_api_key=config.openai_api_key,
                model=config.openai_model,
                temperature=config.temperature
            )
            logger.info(f"LLM initialized with model: {config.openai_model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def create_vector_store(self, persist_directory: Optional[str] = None):
        """Set up ChromaDB vector store."""
        if self.embeddings is None:
            raise ValueError("Embeddings not initialized")
        
        try:
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            logger.info("Vector store created successfully")
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def index_documents(self, chunks: List[DocumentChunk]):
        """Add documents to vector store."""
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return
        
        try:
            if self.vector_store is None:
                self.create_vector_store()
            
            # Convert DocumentChunk to LangChain Documents
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.text,
                    metadata=chunk.metadata
                )
                documents.append(doc)
            
            # Add to vector store
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Indexed {len(documents)} document chunks")
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            raise
    
    def _deduplicate(self, documents: List[Document]) -> List[Document]:
        """Drop chunks that belong to the same source log event.

        Chunks of one document share the Splunk event identifiers
        (``_bkt``/``_cd``), so we keep only the first chunk per event to
        avoid returning the same log as several near-identical results.
        """
        seen = set()
        unique: List[Document] = []
        for doc in documents:
            metadata = doc.metadata or {}
            key = (metadata.get("_bkt") or "", metadata.get("_cd") or "")
            if key == ("", ""):
                key = ("content", doc.page_content)
            if key in seen:
                continue
            seen.add(key)
            unique.append(doc)
        return unique
    
    def search_by_quote(
        self, 
        quote_number: str, 
        version: str,
        doc_type: Optional[str] = None
    ) -> List[Document]:
        """Search with metadata filter by quote number and version."""
        if self.vector_store is None:
            logger.error("Vector store not initialized")
            raise ValueError("Vector store not initialized")
        
        if not quote_number or not version:
            logger.warning("Quote number and version are required")
            return []
        
        try:
            # Build filter with ChromaDB $and operator syntax
            filter_conditions = [
                {"quote_number": {"$eq": quote_number}},
                {"version": {"$eq": version}}
            ]
            
            if doc_type:
                filter_conditions.append({"doc_type": {"$eq": doc_type}})
            
            filter_dict = {"$and": filter_conditions}
            
            # Over-fetch then dedupe so top_k counts distinct log events
            results = self.vector_store.similarity_search(
                query=f"quote {quote_number} version {version}",
                k=config.top_k_results * 5,
                filter=filter_dict
            )
            results = self._deduplicate(results)[:config.top_k_results]
            
            logger.info(f"Found {len(results)} results for quote {quote_number} version {version}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching by quote: {e}")
            raise
    
    def semantic_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Perform semantic search without metadata filters."""
        if self.vector_store is None:
            logger.error("Vector store not initialized")
            raise ValueError("Vector store not initialized")
        
        if not query:
            logger.warning("Query is required for semantic search")
            return []
        
        try:
            k = k or config.top_k_results
            
            # Over-fetch then dedupe so top_k counts distinct log events
            results = self.vector_store.similarity_search(
                query=query,
                k=k * 5
            )
            results = self._deduplicate(results)[:k]
            
            logger.info(f"Found {len(results)} results for semantic search: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            raise
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate AI-powered answer using LLM."""
        if self.llm is None:
            logger.error("LLM not initialized")
            raise ValueError("LLM not initialized")
        
        if not query:
            logger.warning("Query is required for answer generation")
            return ""
        
        if not context:
            logger.warning("Context is required for answer generation")
            return ""
        
        try:
            prompt = PromptTemplate(
                template="""You are a log analysis assistant. Use the following context from log documents to answer the user's question.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the log data. If the context doesn't contain relevant information, say so.""",
                input_variables=["context", "question"]
            )
            
            chain = prompt | self.llm
            response = chain.invoke({"context": context, "question": query})
            
            logger.info("Answer generated successfully")
            return response.content
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def get_reasoning_chain(self):
        """Create reasoning chain for analysis."""
        if self.llm is None:
            logger.error("LLM not initialized")
            raise ValueError("LLM not initialized")
        
        try:
            prompt = PromptTemplate(
                template="""Analyze the following log data and provide insights.

Log Data:
{context}

Provide:
1. Summary of the issue or event
2. Key observations
3. Potential root causes (if applicable)
4. Recommendations (if applicable)

Be specific and reference the actual data from the logs.""",
                input_variables=["context"]
            )
            
            return prompt | self.llm
        
        except Exception as e:
            logger.error(f"Error creating reasoning chain: {e}")
            raise
    
    def analyze_logs(self, documents: List[Document]) -> str:
        """Analyze retrieved log documents with AI."""
        if not documents:
            logger.info("No documents to analyze")
            return "No documents found to analyze."
        
        try:
            # Combine context from all documents
            context_parts = []
            for doc in documents:
                context_parts.append(f"Document (Type: {doc.metadata.get('doc_type', 'unknown')}):")
                context_parts.append(doc.page_content)
                context_parts.append("---")
            
            context = "\n".join(context_parts)
            
            # Use reasoning chain
            chain = self.get_reasoning_chain()
            response = chain.invoke({"context": context})
            
            logger.info(f"Analyzed {len(documents)} documents successfully")
            return response.content
        
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return f"Error analyzing logs: {str(e)}"
    
    def clear_vector_store(self):
        """Clear all documents from the vector store."""
        if self.vector_store is None:
            logger.debug("Vector store is None, nothing to clear")
            return
        
        try:
            # ChromaDB doesn't have a direct clear method, so we recreate
            self.create_vector_store()
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
