import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of document text with metadata."""
    text: str
    metadata: Dict[str, Any]
    doc_type: str  # 'error' or 'response'


class DataProcessor:
    """Handles JSON parsing and data extraction for log documents."""
    
    # URL pattern to extract quote number and version
    QUOTE_PATTERN = re.compile(r'/(\d+)/(\d+)/')
    
    def parse_json_file(self, file_content: str) -> List[Dict[str, Any]]:
        """Load and parse JSON file content."""
        if not file_content:
            logger.warning("Empty file content provided")
            return []
        
        try:
            data = json.loads(file_content)
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Invalid JSON structure type: {type(data)}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            raise ValueError(f"Unexpected error parsing JSON: {e}")
    
    def extract_msg_fields(self, result_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Rebuild the msg object from the flattened ``msg.*`` keys on result.

        The raw log duplicates the message under both ``_raw`` and the
        flattened ``msg.*`` columns. We rely on the flattened columns so the
        large ``responseBody`` carried only inside ``_raw`` is not re-indexed.
        """
        if not isinstance(result_obj, dict):
            logger.debug("Result object is not a dictionary")
            return None
        
        msg: Dict[str, Any] = {}
        for key, value in result_obj.items():
            if not isinstance(key, str) or not key.startswith("msg."):
                continue
            
            path = key[len("msg."):].split(".")
            node = msg
            for part in path[:-1]:
                child = node.get(part)
                if not isinstance(child, dict):
                    child = {}
                    node[part] = child
                node = child
            node[path[-1]] = value
        
        if not msg:
            logger.debug("No msg.* fields found in result object")
            return None
        
        return msg
    
    def identify_document_type(self, msg_obj: Dict[str, Any]) -> str:
        """Determine if document is error or response type."""
        if not isinstance(msg_obj, dict):
            logger.debug("Message object is not a dictionary")
            return "unknown"
        
        if "exception" in msg_obj:
            return "error"
        elif "responseBody" in msg_obj or "requestBody" in msg_obj:
            return "response"
        else:
            logger.debug("Unknown document type - no exception, responseBody, or requestBody found")
            return "unknown"
    
    def extract_quote_info(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract quote number and version from URL."""
        if not url or not isinstance(url, str):
            logger.debug("Invalid URL provided for quote extraction")
            return None, None
        
        try:
            match = self.QUOTE_PATTERN.search(url)
            if match:
                quote_number = match.group(1)
                version = match.group(2)
                return quote_number, version
        except Exception as e:
            logger.error(f"Error extracting quote info from URL: {e}")
        
        return None, None
    
    def prepare_for_embedding(self, document: Dict[str, Any], doc_type: str) -> str:
        """Prepare text for embedding by flattening and cleaning data."""
        if not isinstance(document, dict):
            logger.warning("Document is not a dictionary for embedding preparation")
            return ""
        
        text_parts = []
        
        try:
            if doc_type == "error":
                # Extract error-related fields
                if "exception" in document:
                    exc = document["exception"]
                    if isinstance(exc, dict):
                        text_parts.append(f"Exception: {exc.get('Message', '')}")
                        text_parts.append(f"StackTrace: {exc.get('StackTrace', '')}")
                        text_parts.append(f"StatusCode: {exc.get('StatusCode', '')}")
                        text_parts.append(f"Source: {exc.get('Source', '')}")
                
                if "fullRequestUrl" in document:
                    text_parts.append(f"URL: {document['fullRequestUrl']}")
                
                if "errorId" in document:
                    text_parts.append(f"Error ID: {document['errorId']}")
                
                if "eventId" in document:
                    text_parts.append(f"Event ID: {document['eventId']}")
            
            elif doc_type == "response":
                # Extract response-related fields
                if "responseBody" in document:
                    text_parts.append(f"Response: {str(document['responseBody'])}")
                
                if "requestBody" in document:
                    text_parts.append(f"Request: {str(document['requestBody'])}")
                
                if "fullRequestUrl" in document:
                    text_parts.append(f"URL: {document['fullRequestUrl']}")
                
                if "log_level" in document:
                    text_parts.append(f"Log Level: {document['log_level']}")
            
            else:
                logger.warning(f"Unknown document type for embedding: {doc_type}")
        
        except Exception as e:
            logger.error(f"Error preparing text for embedding: {e}")
            return ""
        
        return " ".join(text_parts)
    
    def create_document_chunks(
        self, 
        text: str, 
        metadata: Dict[str, Any],
        doc_type: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[DocumentChunk]:
        """Create chunks for vector store with metadata."""
        if not text:
            logger.warning("Empty text provided for chunking")
            return []
        
        if not isinstance(metadata, dict):
            logger.warning("Metadata is not a dictionary")
            metadata = {}
        
        if chunk_overlap >= chunk_size:
            logger.warning("Chunk overlap >= chunk size, adjusting overlap")
            chunk_overlap = chunk_size - 1
        
        chunks = []
        
        try:
            # Simple chunking strategy
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk_text = text[i:i + chunk_size]
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i // (chunk_size - chunk_overlap)
                
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    doc_type=doc_type
                ))
        
        except Exception as e:
            logger.error(f"Error creating document chunks: {e}")
            return []
        
        return chunks
    
    def process_document(self, document: Dict[str, Any]) -> List[DocumentChunk]:
        """Process a single document and return chunks."""
        if not isinstance(document, dict):
            logger.warning("Document is not a dictionary")
            return []
        
        try:
            # Extract result object
            result_obj = document.get("result", {})
            if not result_obj:
                logger.debug("No result object found in document")
                return []
            
            # Build msg object from the flattened msg.* columns (not _raw)
            msg_obj = self.extract_msg_fields(result_obj)
            if not msg_obj:
                logger.debug("No msg fields found in result object")
                return []
            
            # Identify document type
            doc_type = self.identify_document_type(msg_obj)
            if doc_type == "unknown":
                logger.debug("Unknown document type, skipping")
                return []
            
            # Extract quote info
            url = msg_obj.get("fullRequestUrl", "")
            quote_number, version = self.extract_quote_info(url)
            
            # Prepare metadata
            metadata = {
                "quote_number": quote_number,
                "version": version,
                "url": url,
                "doc_type": doc_type,
                "_bkt": result_obj.get("_bkt", ""),
                "_cd": result_obj.get("_cd", ""),
                "_indextime": result_obj.get("_indextime", "")
            }
            
            # Prepare text for embedding
            text = self.prepare_for_embedding(msg_obj, doc_type)
            if not text:
                logger.debug("No text prepared for embedding")
                return []
            
            # Create chunks
            from config import config
            if config is None:
                logger.error("Config not initialized")
                return []
            
            chunks = self.create_document_chunks(
                text, 
                metadata, 
                doc_type,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap
            )
            
            return chunks
        
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return []
    
    def process_file(self, file_content: str) -> List[DocumentChunk]:
        """Process entire JSON file and return all chunks."""
        if not file_content:
            logger.warning("Empty file content provided")
            return []
        
        try:
            documents = self.parse_json_file(file_content)
            all_chunks = []
            
            for doc in documents:
                chunks = self.process_document(doc)
                all_chunks.extend(chunks)
            
            logger.info(f"Processed {len(documents)} documents, generated {len(all_chunks)} chunks")
            return all_chunks
        
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return []
