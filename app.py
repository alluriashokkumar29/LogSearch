import streamlit as st
import logging
from data_processor import DataProcessor
from rag_system import RAGSystem
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    try:
        if "data_processor" not in st.session_state:
            st.session_state.data_processor = DataProcessor()
            logger.info("DataProcessor initialized in session state")
        
        if "rag_system" not in st.session_state:
            st.session_state.rag_system = None
        
        if "documents_loaded" not in st.session_state:
            st.session_state.documents_loaded = False
        
        if "search_results" not in st.session_state:
            st.session_state.search_results = None
        
        if "ai_analysis" not in st.session_state:
            st.session_state.ai_analysis = None
    except Exception as e:
        logger.error(f"Error initializing session state: {e}")
        st.error(f"Error initializing application: {str(e)}")


def render_file_upload(key="file_upload"):
    """Render file upload interface."""
    st.subheader("Upload Log Data")
    
    uploaded_file = st.file_uploader(
        "Upload JSON log file",
        type=["json"],
        help="Upload a JSON file containing error or response logs",
        key=key
    )
    
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8")
            
            if not file_content:
                st.warning("Uploaded file is empty")
                return
            
            with st.spinner("Processing documents..."):
                # Process the file
                chunks = st.session_state.data_processor.process_file(file_content)
                
                if chunks:
                    # Initialize RAG system
                    try:
                        st.session_state.rag_system = RAGSystem()
                        st.session_state.rag_system.index_documents(chunks)
                        
                        st.session_state.documents_loaded = True
                        st.success(f"Successfully loaded {len(chunks)} document chunks")
                        logger.info(f"Successfully loaded {len(chunks)} document chunks")
                    except Exception as e:
                        logger.error(f"Error initializing RAG system: {e}")
                        st.error(f"Error initializing RAG system: {str(e)}")
                        st.session_state.rag_system = None
                else:
                    st.warning("No valid documents found in the uploaded file")
                    logger.warning("No valid documents found in uploaded file")
        
        except UnicodeDecodeError:
            st.error("Failed to decode file. Please ensure it's a valid UTF-8 JSON file.")
            logger.error("Unicode decode error for uploaded file")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"Error processing uploaded file: {e}")


def render_search_interface():
    """Render search input fields."""
    st.subheader("Search Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quote_number = st.text_input("Quote Number", placeholder="e.g., 3400021622408")
    
    with col2:
        version = st.text_input("Version", placeholder="e.g., 3")
    
    doc_type = st.selectbox(
        "Document Type",
        ["All", "Error", "Response"],
        help="Filter by document type"
    )
    
    search_button = st.button("Search", type="primary", disabled=not st.session_state.documents_loaded)
    
    return quote_number, version, doc_type, search_button


def render_semantic_search():
    """Render semantic search interface."""
    st.subheader("Semantic Search")
    
    query = st.text_input(
        "Enter your query",
        placeholder="e.g., payment validation errors"
    )
    
    semantic_button = st.button(
        "Semantic Search",
        type="secondary",
        disabled=not st.session_state.documents_loaded
    )
    
    return query, semantic_button


def render_results():
    """Render search results with formatting."""
    if st.session_state.search_results is None:
        st.info("No search results yet. Upload a file and perform a search.")
        return
    
    results = st.session_state.search_results
    
    if not results:
        st.warning("No documents found matching your criteria.")
        return
    
    st.subheader(f"Found {len(results)} Results")
    
    for i, doc in enumerate(results, 1):
        with st.expander(f"Result {i} - {doc.metadata.get('doc_type', 'unknown').upper()}"):
            st.json({
                "content": doc.page_content,
                "metadata": doc.metadata
            })


def render_ai_analysis():
    """Render AI-generated summaries."""
    if st.session_state.ai_analysis is None:
        return
    
    st.subheader("AI Analysis")
    st.markdown(st.session_state.ai_analysis)


def main():
    """Main Streamlit application."""
    try:
        st.set_page_config(
            page_title="RAG Log Search",
            page_icon="🔍",
            layout="wide"
        )
    except Exception as e:
        logger.error(f"Error setting page config: {e}")
    
    st.title("RAG-Based Log Search Application")
    st.markdown("Search and analyze JSON log documents from Dell's quote-purchase services")
    
    # Initialize session state
    initialize_session_state()
    
    # Check for API key
    from config import config
    if config is None:
        st.error("Configuration not initialized. Please check your .env file.")
        st.stop()
    
    if not config.openai_api_key:
        st.error("Please set OPENAI_API_KEY in your .env file")
        logger.error("OPENAI_API_KEY not set")
        st.stop()
    
    # Create tabs
    try:
        tab1, tab2 = st.tabs(["Quote Search", "Semantic Search"])
    except Exception as e:
        logger.error(f"Error creating tabs: {e}")
        st.error("Error creating interface tabs")
        st.stop()
    
    with tab1:
        # File upload
        render_file_upload(key="file_upload_tab1")
        
        st.divider()
        
        # Search interface
        quote_number, version, doc_type, search_button = render_search_interface()
        
        # Handle search
        if search_button:
            if not quote_number or not version:
                st.warning("Please enter both quote number and version")
            else:
                if st.session_state.rag_system is None:
                    st.error("RAG system not initialized. Please upload a file first.")
                else:
                    with st.spinner("Searching..."):
                        try:
                            doc_type_filter = None if doc_type == "All" else doc_type.lower()
                            results = st.session_state.rag_system.search_by_quote(
                                quote_number=quote_number,
                                version=version,
                                doc_type=doc_type_filter
                            )
                            st.session_state.search_results = results
                            
                            # Generate AI analysis
                            if results:
                                st.session_state.ai_analysis = st.session_state.rag_system.analyze_logs(results)
                            else:
                                st.session_state.ai_analysis = None
                        
                        except ValueError as e:
                            st.error(f"Search error: {str(e)}")
                            logger.error(f"Search validation error: {e}")
                        except Exception as e:
                            st.error(f"Error during search: {str(e)}")
                            logger.error(f"Search error: {e}")
        
        st.divider()
        
        # Display results
        render_results()
        
        # Display AI analysis
        render_ai_analysis()
    
    with tab2:
        # File upload (shared state)
        render_file_upload(key="file_upload_tab2")
        
        st.divider()
        
        # Semantic search interface
        query, semantic_button = render_semantic_search()
        
        # Handle semantic search
        if semantic_button:
            if not query:
                st.warning("Please enter a search query")
            else:
                if st.session_state.rag_system is None:
                    st.error("RAG system not initialized. Please upload a file first.")
                else:
                    with st.spinner("Searching..."):
                        try:
                            results = st.session_state.rag_system.semantic_search(query=query)
                            st.session_state.search_results = results
                            
                            # Generate AI analysis
                            if results:
                                st.session_state.ai_analysis = st.session_state.rag_system.analyze_logs(results)
                            else:
                                st.session_state.ai_analysis = None
                        
                        except ValueError as e:
                            st.error(f"Search error: {str(e)}")
                            logger.error(f"Semantic search validation error: {e}")
                        except Exception as e:
                            st.error(f"Error during search: {str(e)}")
                            logger.error(f"Semantic search error: {e}")
        
        st.divider()
        
        # Display results
        render_results()
        
        # Display AI analysis
        render_ai_analysis()
    
    # Sidebar with information
    try:
        with st.sidebar:
            st.header("Application Info")
            st.info(f"""
            **Model:** {config.openai_model}
            
            **Embedding Model:** {config.embedding_model}
            
            **Chunk Size:** {config.chunk_size}
            
            **Top K Results:** {config.top_k_results}
            
            **Temperature:** {config.temperature}
            """)
            
            st.header("Status")
            if st.session_state.documents_loaded:
                st.success("✅ Documents loaded")
            else:
                st.warning("⏳ No documents loaded")
    except Exception as e:
        logger.error(f"Error rendering sidebar: {e}")


if __name__ == "__main__":
    main()
