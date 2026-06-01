# RAG-Based Log Search Application

A comprehensive Retrieval-Augmented Generation (RAG) application with Streamlit UX for searching and analyzing JSON log documents from Dell's quote-purchase services.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Use Cases](#use-cases)
- [Architecture](#architecture)
- [Data Structure](#data-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This application provides intelligent search and analysis capabilities for JSON log documents from Dell's quote-purchase services. It combines:

- **RAG Architecture**: Retrieves relevant log documents and uses AI to generate insights
- **Semantic Search**: Understands natural language queries beyond exact matching
- **Metadata Filtering**: Precise filtering by quote number, version, and document type
- **AI-Powered Analysis**: Leverages OpenAI LLMs for deep log analysis and reasoning

## Features

### Core Features

- **Document Type Support**: Handle both error logs and regular response logs
- **Intelligent Search**: Use quote number/version for filtering with semantic search
- **AI-Powered Analysis**: Leverage OpenAI LLM for reasoning and insight generation
- **Reactive UI**: Streamlit-based interface with real-time updates
- **Flexible Data Loading**: File upload support for JSON documents

### Advanced Features

- **Dual Search Modes**: Quote-based exact search and semantic natural language search
- **Real-time AI Analysis**: Automatic generation of insights from search results
- **Document Chunking**: Intelligent text chunking for optimal vector embeddings
- **Metadata Enrichment**: Automatic extraction and indexing of quote information
- **Session Management**: Stateful handling of uploaded documents across interactions
- **Comprehensive Error Handling**: Defensive programming with validation at every layer
- **Logging System**: Detailed logging for debugging and monitoring

## Use Cases

### Error Analysis
Search by quote number/version to retrieve exception details, stack traces, and error identifiers for debugging and troubleshooting.

### Response Analysis
Search by quote number/version to retrieve response content, request details, and HTTP headers for understanding service behavior.

### Mixed Document Handling
Process both error and response document types in a single JSON file, enabling comprehensive log analysis across different log sources.

### Semantic Querying
Ask natural language questions like "show me payment validation errors" to find relevant logs without knowing specific quote numbers.

## Installation

### Prerequisites

- **Python 3.8 or higher**: Required for all dependencies
- **OpenAI API key**: Required for embeddings and LLM operations
- **pip**: Python package manager
- **Virtual environment** (recommended): For isolated dependency management

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd LogSearch
```

#### 2. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- streamlit>=1.28.0 - Web application framework
- openai>=1.0.0 - OpenAI API client
- langchain>=0.1.0 - LLM framework
- langchain-openai>=0.0.5 - LangChain OpenAI integration
- langchain-community>=0.0.10 - LangChain community integrations
- chromadb>=0.4.0 - Vector database
- python-dotenv>=1.0.0 - Environment variable management
- pydantic>=2.0.0 - Data validation
- pydantic-settings>=2.0.0 - Pydantic settings support

#### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
TEMPERATURE=0.7
```

#### 5. Verify Installation

```bash
python -c "import streamlit; import openai; import langchain; print('All dependencies installed successfully')"
```

## Usage

### Running the Application

#### Start the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

#### Advanced Run Options

```bash
# Specify a different port
streamlit run app.py --server.port 8502

# Run in development mode with auto-reload
streamlit run app.py --logger.level debug

# Run with file watcher for development
streamlit run app.py --server.runOnSave true
```

### Using the Interface

#### Tab 1: Quote Search

1. **Upload Log Data**
   - Click "Browse files" to upload a JSON log file
   - Wait for processing confirmation
   - Status indicator shows "Documents loaded"

2. **Enter Search Criteria**
   - **Quote Number**: Enter the quote number (e.g., 3000000000000)
   - **Version**: Enter the version number (e.g., 3)
   - **Document Type**: Select "All", "Error", or "Response" to filter

3. **Perform Search**
   - Click "Search" button
   - Results appear with expandable sections
   - Each result shows document type and metadata

4. **View AI Analysis**
   - AI-generated insights appear below results
   - Analysis includes summary, observations, and recommendations

#### Tab 2: Semantic Search

1. **Upload Log Data** (if not already uploaded)
2. **Enter Natural Language Query**
   - Example: "payment validation errors"
   - Example: "order creation failures"
   - Example: "high response times"
3. **Perform Semantic Search**
   - Click "Semantic Search" button
   - Results ranked by semantic relevance
4. **View Results and Analysis**

### Example Workflows

#### Workflow 1: Debug a Specific Error

```
1. Upload Today_Errors.json
2. Enter quote number: 3000000000000
3. Enter version: 3
4. Select document type: Error
5. Click Search
6. Review stack trace and AI analysis
```

#### Workflow 2: Analyze All Payment Issues

```
1. Switch to Semantic Search tab
2. Upload log file
3. Enter query: "payment transaction errors"
4. Click Semantic Search
5. Review all related errors across different quotes
6. Use AI analysis to identify patterns
```

#### Workflow 3: Compare Request/Response Pairs

```
1. Upload regularResponse.json
2. Enter quote number: 3700025978808
3. Enter version: 1
4. Select document type: Response
5. Click Search
6. Review request/response data
```

## Data Structure

### JSON Document Structure

Both document types share a common wrapper structure:

```json
{
  "preview": false,
  "result": {
    "_bkt": "bucket_identifier",
    "_cd": "cluster_data",
    "_indextime": "timestamp",
    "_raw": "JSON_STRING_CONTAINING_ACTUAL_LOG_DATA"
  }
}
```

### Error Document Structure (Today_Errors.json)

Key fields in `_raw` JSON:

```json
{
  "msg": {
    "exception": {
      "Message": "Error message content",
      "StackTrace": "Full stack trace details",
      "StatusCode": 500,
      "Source": "Error source"
    },
    "fullRequestUrl": "http://quote-purchase-bridge-service.g2z1p.pcf.dell.com/api/v1/paymentTransaction/Paypal/validate/QuoteNumber/QuoteVersion/en-UK",
    "errorId": "unique_error_identifier",
    "eventId": "event_identifier"
  }
}
```

**URL Pattern Example:**
```
http://quote-purchase-bridge-service.g2z1p.pcf.dell.com/api/v1/paymentTransaction/Paypal/validate/QuoteNumber/QuoteVersion/en-UK
```
- **Quote Number**: 3000000000000
- **Version**: 3

### Regular Response Document Structure (regularResponse.json)

Key fields in `_raw` JSON:

```json
{
  "msg": {
    "responseBody": { "response": "data" },
    "requestBody": { "request": "data" },
    "fullRequestUrl": "http://quote-purchase-bridge-service.g2z1p.pcf.dell.com/api/v1/order/createBundledOrder/QuoteNumber/QuoteVersion/en-cn/premier",
    "requestUrl": "/api/v1/order/createBundledOrder",
    "requestHeaders": { "header": "values" },
    "log_level": "Information"
  }
}
```

**URL Pattern Example:**
```
http://quote-purchase-bridge-service.g2z1p.pcf.dell.com/api/v1/order/createBundledOrder/QuoteNumber/QuoteVersion/en-cn/premier
```
- **Quote Number**: 3700025978808
- **Version**: 1

### Document Metadata

Each document chunk is enriched with the following metadata:

```python
{
  "quote_number": "extracted_quote_number",
  "version": "extracted_version",
  "url": "full_request_url",
  "doc_type": "error" or "response",
  "_bkt": "bucket_identifier",
  "_cd": "cluster_data",
  "_indextime": "timestamp",
  "chunk_index": 0
}
```

## Architecture

The application follows a 4-layer architecture designed for scalability and maintainability:

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                      │
│  - File Upload Interface                                     │
│  - Search Input (Quote #/Version)                           │
│  - Results Display (JSON + AI Summary)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Application Logic Layer                    │
│  - Data Processor Module                                    │
│  - RAG System Module                                        │
│  - Session State Management                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAG Infrastructure Layer                  │
│  - OpenAI Embeddings                                        │
│  - ChromaDB Vector Store                                    │
│  - LangChain Retrieval Chain                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                     │
│  - In-Memory Vector Store (ChromaDB)                        │
│  - Session-Based Document Cache                             │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

1. **Streamlit UI Layer**
   - File upload interface for JSON documents
   - Search input fields (quote number, version)
   - Semantic search input for natural language queries
   - Results display with expandable JSON views
   - AI-generated analysis and insights display
   - Session state management for user interactions

2. **Application Logic Layer**
   - **Data Processor Module**: Parses nested JSON, extracts log data, identifies document types
   - **RAG System Module**: Manages vector store, embeddings, and LLM interactions
   - **Session Management**: Maintains state across user interactions

3. **RAG Infrastructure Layer**
   - **OpenAI Embeddings**: Converts text to vector representations
   - **ChromaDB Vector Store**: Stores and retrieves document embeddings
   - **LangChain Retrieval Chain**: Orchestrates retrieval and generation

4. **Data Storage Layer**
   - **In-Memory Vector Store**: Fast document retrieval during session
   - **Session-Based Cache**: Temporary storage for uploaded documents

### Data Flow

```
User Uploads JSON File
         ↓
    ┌─────────────────────────────────────────────┐
    │         File Upload & Validation             │
    │  - Check file is not empty                   │
    │  - Validate UTF-8 encoding                   │
    │  - Parse JSON structure                       │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Data Processing Layer                │
    │  - Extract result object                      │
    │  - Parse _raw field                          │
    │  - Identify document type (error/response)   │
    │  - Extract quote number/version from URL     │
    │  - Prepare metadata                          │
    │  - Flatten text for embedding                │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Document Chunking                    │
    │  - Split text into chunks (configurable)     │
    │  - Add overlap between chunks                │
    │  - Attach metadata to each chunk             │
    │  - Create DocumentChunk objects              │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         RAG Initialization                   │
    │  - Validate OPENAI_API_KEY                  │
    │  - Initialize OpenAI embeddings              │
    │  - Initialize ChatOpenAI LLM                 │
    │  - Create ChromaDB vector store              │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Document Indexing                    │
    │  - Convert DocumentChunk to LangChain Doc   │
    │  - Generate embeddings via OpenAI API        │
    │  - Store in ChromaDB with metadata           │
    │  - Log indexing statistics                   │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Search Operations                    │
    │  - Quote Search:                            │
    │    • Filter by quote_number + version       │
    │    • Optional doc_type filter                │
    │  - Semantic Search:                         │
    │    • Natural language query                  │
    │    • Vector similarity search                │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Document Retrieval                   │
    │  - Retrieve top-k results                   │
    │  - Return with metadata                     │
    │  - Log search results count                 │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         AI Analysis                          │
    │  - Combine retrieved documents              │
    │  - Create context for LLM                   │
    │  - Generate insights via ChatOpenAI          │
    │  - Return summary + observations             │
    └─────────────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────────────┐
    │         Results Display                      │
    │  - Show expandable JSON for each result      │
    │  - Display metadata                         │
    │  - Show AI-generated analysis               │
    │  - Status indicators                        │
    └─────────────────────────────────────────────┘
```

### Detailed Data Flow Diagram

```
┌──────────────┐
│  User Action │
│  Upload File │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    app.py                                    │
│  render_file_upload()                                        │
│  • st.file_uploader()                                        │
│  • Read file content                                        │
│  • Validate file not empty                                  │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│              data_processor.py                              │
│  process_file(file_content)                                 │
│  • parse_json_file() - Validate JSON structure             │
│  • For each document:                                       │
│    - process_document()                                     │
│      • extract_raw_data() - Parse _raw field               │
│      • identify_document_type() - error vs response        │
│      • extract_quote_info() - Regex URL parsing            │
│      • prepare_for_embedding() - Flatten text              │
│      • create_document_chunks() - Split with overlap       │
└──────┬──────────────────────────────────────────────────────┘
       │ DocumentChunk[]
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  rag_system.py                               │
│  RAGSystem.__init__()                                        │
│  • _initialize_embeddings() - OpenAI API validation         │
│  • _initialize_llm() - ChatOpenAI setup                     │
│  • create_vector_store() - ChromaDB initialization          │
│  • index_documents(chunks)                                  │
│    - Convert to LangChain Documents                         │
│    - Generate embeddings                                     │
│    - Store in vector store                                  │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    app.py                                    │
│  User enters search query                                    │
│  • Quote Search: search_by_quote()                          │
│    - Build metadata filter                                  │
│    - ChromaDB similarity_search() with filter               │
│  • Semantic Search: semantic_search()                       │
│    - ChromaDB similarity_search() without filter            │
└──────┬──────────────────────────────────────────────────────┘
       │ Document[]
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  rag_system.py                               │
│  analyze_logs(documents)                                     │
│  • Combine document contexts                               │
│  • get_reasoning_chain() - Create prompt template          │
│  • LLM.invoke() - Generate analysis                         │
└──────┬──────────────────────────────────────────────────────┘
       │ Analysis string
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    app.py                                    │
│  render_results()                                            │
│  • Display expandable JSON for each document               │
│  render_ai_analysis()                                       │
│  • Display AI-generated markdown                            │
└─────────────────────────────────────────────────────────────┘
```

### Error Flow

```
Error Occurs
     ↓
┌─────────────────────────────────────────┐
│         Layer Detection                  │
│  • Config Layer: Validation errors      │
│  • Data Processing: JSON parsing        │
│  • RAG System: API/Vector store errors │
│  • UI Layer: User input errors          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Error Logging                    │
│  • logger.error() with context          │
│  • Include stack trace if applicable    │
│  • Log user action that caused error    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Error Handling                  │
│  • Catch specific exceptions           │
│  • Provide fallback values             │
│  • Return empty results gracefully     │
│  • Prevent application crash           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         User Notification               │
│  • st.error() for critical errors      │
│  • st.warning() for non-critical       │
│  • Clear, actionable error messages    │
│  • Guidance for resolution              │
└─────────────────────────────────────────┘
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and LLM | Yes | - | `sk-...` |
| `OPENAI_MODEL` | OpenAI model name for text generation | No | `gpt-3.5-turbo` | `gpt-4` |
| `EMBEDDING_MODEL` | OpenAI embedding model | No | `text-embedding-ada-002` | `text-embedding-3-small` |
| `CHUNK_SIZE` | Character size for document chunks | No | `1000` | `1500` |
| `CHUNK_OVERLAP` | Character overlap between chunks | No | `200` | `300` |
| `TOP_K_RESULTS` | Number of search results to return | No | `5` | `10` |
| `TEMPERATURE` | LLM temperature (0.0-1.0) | No | `0.7` | `0.5` |

### Configuration File

The `config.py` file contains the `Config` class that manages all application settings with built-in validation:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    temperature: float = 0.7
    
    # Automatic validation ensures:
    # - chunk_size must be positive
    # - chunk_overlap must be less than chunk_size
    # - top_k_results must be positive
    # - temperature must be between 0 and 2
```

### Recommended Settings

#### For Faster Performance
```
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
TOP_K_RESULTS=3
```

#### For Better Analysis Quality
```
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-large
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=10
TEMPERATURE=0.3
```

## Project Structure

```
LogSearch/
├── app.py                    # Main Streamlit application
├── data_processor.py         # JSON parsing and data extraction
├── rag_system.py            # RAG implementation
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env.example            # Environment variables template
└── data/                   # Sample data directory (optional)
    ├── Today_Errors.json
    └── regularResponse.json
```

### File Descriptions

| File | Description | Key Classes/Functions |
|------|-------------|----------------------|
| `app.py` | Streamlit UI application | `main()`, `initialize_session_state()`, `render_file_upload()` |
| `data_processor.py` | JSON parsing and extraction | `DataProcessor`, `process_document()`, `extract_quote_info()` |
| `rag_system.py` | RAG system implementation | `RAGSystem`, `search_by_quote()`, `semantic_search()` |
| `config.py` | Configuration management | `Config`, `get_config()` |
| `requirements.txt` | Python dependencies | - |
| `.env.example` | Environment template | - |

## Technology Stack

### Core Technologies

- **Frontend Framework**: Streamlit 1.28+
  - Reactive UI components
  - Session state management
  - File upload handling

- **LLM Provider**: OpenAI
  - GPT-4/GPT-3.5-turbo for text generation
  - text-embedding-ada-002 for embeddings
  - API-based integration

- **Vector Database**: ChromaDB 0.4.0+
  - In-memory vector storage
  - Similarity search capabilities
  - Metadata filtering

- **Orchestration Framework**: LangChain 0.1+
  - Document processing
  - Retrieval chains
  - Prompt templates

- **Data Processing**: Python Standard Library
  - `json`: JSON parsing
  - `re`: Regex pattern matching
  - `dataclasses`: Data structures

### Dependency Tree

```
app.py
├── streamlit (UI framework)
├── data_processor.py
│   ├── json (standard library)
│   └── re (standard library)
├── rag_system.py
│   ├── langchain (orchestration)
│   │   ├── langchain-openai (OpenAI integration)
│   │   └── langchain-community (community integrations)
│   ├── chromadb (vector store)
│   └── openai (API client)
└── config.py
    ├── pydantic (validation)
    ├── pydantic-settings (settings management)
    └── python-dotenv (environment variables)
```

## Error Handling and Logging

### Comprehensive Error Handling

The application implements defensive programming with error handling at every layer:

- **Configuration Layer**: Validates all environment variables on startup with clear error messages
- **Data Processing Layer**: Handles malformed JSON, missing fields, and invalid data gracefully
- **RAG System Layer**: Validates API keys, handles OpenAI errors, and manages vector store failures
- **UI Layer**: Provides user-friendly error messages and prevents crashes from invalid inputs

### Logging System

The application uses Python's logging module for debugging and monitoring:

```python
import logging

# Logging is configured at INFO level by default
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Key Logging Points:**
- Configuration initialization and validation
- Document processing and chunking
- Vector store operations
- Search operations and results
- API interactions and errors
- User actions and errors

### Viewing Logs

**Enable debug logging:**
```bash
streamlit run app.py --logger.level debug
```

**View logs in real-time:**
```bash
# On macOS/Linux
tail -f logs/app.log

# On Windows
Get-Content logs/app.log -Wait
```

**Common log messages:**
- `INFO: RAG system initialized successfully` - System ready
- `WARNING: OPENAI_API_KEY not set` - Configuration issue
- `ERROR: Failed to parse JSON` - Data format issue
- `INFO: Successfully loaded X document chunks` - Processing complete
- `ERROR: Error during search` - Search operation failed

## API Documentation

### DataProcessor Module

#### `DataProcessor` Class

```python
class DataProcessor:
    """Handles JSON parsing and data extraction for log documents."""
    
    def parse_json_file(self, file_content: str) -> List[Dict[str, Any]]
    def extract_raw_data(self, result_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]
    def identify_document_type(self, msg_obj: Dict[str, Any]) -> str
    def extract_quote_info(self, url: str) -> Tuple[Optional[str], Optional[str]]
    def prepare_for_embedding(self, document: Dict[str, Any], doc_type: str) -> str
    def create_document_chunks(self, text: str, metadata: Dict[str, Any], doc_type: str, chunk_size: int, chunk_overlap: int) -> List[DocumentChunk]
    def process_document(self, document: Dict[str, Any]) -> List[DocumentChunk]
    def process_file(self, file_content: str) -> List[DocumentChunk]
```

### RAGSystem Module

#### `RAGSystem` Class

```python
class RAGSystem:
    """Handles RAG implementation with vector store and LLM integration."""
    
    def __init__(self)
    def create_vector_store(self, persist_directory: Optional[str] = None)
    def index_documents(self, chunks: List[DocumentChunk])
    def search_by_quote(self, quote_number: str, version: str, doc_type: Optional[str] = None) -> List[Document]
    def semantic_search(self, query: str, k: Optional[int] = None) -> List[Document]
    def generate_answer(self, query: str, context: str) -> str
    def get_reasoning_chain(self)
    def analyze_logs(self, documents: List[Document]) -> str
    def clear_vector_store(self)
```

## Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd LogSearch

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Configure environment
copy .env.example .env
# Edit .env with your API keys
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all classes and public methods
- Maximum line length: 100 characters

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Adding New Features

1. **New Document Type**: Add parsing logic in `data_processor.py`
2. **New Search Mode**: Add method in `rag_system.py` and UI in `app.py`
3. **New Configuration**: Add field to `Config` class in `config.py`

## Performance Considerations

### Document Processing

- **Chunk Size**: Larger chunks (1500+) reduce embedding calls but may lose context
- **Chunk Overlap**: Higher overlap (300+) improves context continuity but increases storage
- **Batch Processing**: Process multiple documents in parallel for large files

### Vector Store Performance

- **Memory Usage**: In-memory ChromaDB uses ~1-2MB per 1000 chunks
- **Search Speed**: Semantic search typically <500ms for 10K documents
- **Indexing Time**: ~100-200ms per document for embedding generation

### API Costs

- **Embeddings**: ~$0.0001 per 1K tokens (text-embedding-ada-002)
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **GPT-4**: ~$0.03 per 1K tokens

### Optimization Tips

1. Use GPT-3.5-turbo for cost efficiency
2. Adjust `TOP_K_RESULTS` based on needs (3-5 is usually sufficient)
3. Cache frequently accessed documents
4. Use semantic search for broad queries, quote search for precise lookups

## Troubleshooting

### Common Issues

#### 1. "OPENAI_API_KEY is required"
**Cause**: API key not set in environment variables or config not initialized
**Solution**: 
```bash
# Ensure .env file exists and contains:
OPENAI_API_KEY=your_actual_api_key_here
```
**Error Handling**: The application will display a clear error message on startup and in the logs if the API key is missing.

#### 2. "No valid documents found"
**Cause**: JSON structure doesn't match expected format or file is empty
**Solution**: 
- Verify your JSON follows the wrapper structure with `_raw` field
- Check that the file is not empty
- Ensure the file is valid UTF-8 encoded JSON
**Error Handling**: The application will log specific parsing errors and display user-friendly messages.

#### 3. "Configuration not initialized"
**Cause**: Invalid configuration values or missing .env file
**Solution**: 
- Check that all required environment variables are set
- Validate that configuration values are within acceptable ranges
- Review logs for specific validation errors
**Error Handling**: The config module validates all values and provides specific error messages for invalid settings.

#### 4. "RAG system not initialized"
**Cause**: No documents have been uploaded or RAG system initialization failed
**Solution**: 
- Upload a valid JSON file first
- Check logs for initialization errors
- Verify OpenAI API key is valid
**Error Handling**: The UI prevents search operations until documents are loaded and provides clear status indicators.

#### 5. Vector store errors during search
**Cause**: Documents not properly indexed or vector store issue
**Solution**: 
- Re-upload the file to re-index documents
- Check logs for vector store errors
- Verify ChromaDB compatibility
**Error Handling**: Search operations catch vector store errors and display user-friendly messages.

#### 6. "Failed to decode file"
**Cause**: File encoding issue or corrupted file
**Solution**: 
- Ensure file is UTF-8 encoded
- Verify file is not corrupted
- Check file size (very large files may timeout)
**Error Handling**: The application catches UnicodeDecodeError specifically and provides helpful guidance.

#### 7. Slow response times
**Cause**: Large document sets or slow API calls
**Solution**: 
- Reduce `TOP_K_RESULTS` in configuration
- Increase `CHUNK_SIZE` to reduce embedding calls
- Use faster model (gpt-3.5-turbo)
- Check network connectivity to OpenAI API
**Error Handling**: The application uses spinner indicators and timeout handling for long operations.

#### 8. Import errors
**Cause**: Missing dependencies or version conflicts
**Solution**: 
```bash
pip install -r requirements.txt
pip install --upgrade pip
```
**Error Handling**: The application checks for config initialization and provides clear dependency error messages.

### Debug Mode

Enable debug logging:
```bash
streamlit run app.py --logger.level debug
```

**What debug mode shows:**
- Detailed configuration loading
- Step-by-step document processing
- Vector store operations
- API call details
- Stack traces for errors

### Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working as expected (default)
- **WARNING**: Something unexpected happened, but software is still working
- **ERROR**: Due to a more serious problem, software has not been able to perform some function
- **CRITICAL**: Serious error, indicating that the program itself may be unable to continue running

### Getting Help

- Check the [Issues](../../issues) page for known problems
- Review the [Architecture](#architecture) section for system design
- Enable debug mode for detailed error messages
- Check logs for specific error messages and stack traces
- Verify all environment variables are correctly set
- Ensure all dependencies are installed with correct versions

## License

[Add your license here]

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- Orchestration by [LangChain](https://langchain.com/)


Screenshots:
<img width="1731" height="800" alt="image" src="https://github.com/user-attachments/assets/4069eea1-0ae2-4891-9c8a-9a576d16989d" />

<img width="1154" height="648" alt="image" src="https://github.com/user-attachments/assets/f22b9671-77d0-42fb-946f-9c7dbf0c2f99" />


