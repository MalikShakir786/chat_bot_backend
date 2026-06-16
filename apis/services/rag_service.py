import os
import uuid
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Any

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        
    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
            
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        self._load_model()
        return self.model.encode(texts, show_progress_bar=False)

class VectorStore:
    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "data/vectorstore"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
    def _initialize_store(self):
        if self.client is None:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF documents embedding for RAG"}
            )
            
    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        self._initialize_store()
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings do not match")
        
        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []
       
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)
            metadata = dict(doc.metadata) if hasattr(doc, 'metadata') else {}
            metadata["doc_index"] = i
            metadata['content_length'] = len(doc.page_content)
           
            metadatas.append(metadata)
            documents_text.append(doc.page_content)
            embeddings_list.append(embedding.tolist())
           
        self.collection.add(
            documents=documents_text,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )

# Initialize global managers lazily
embedding_manager = EmbeddingManager()
vector_store = VectorStore()

def ingest_document(file_path: str, file_type: str) -> bool:
    """
    Ingests a document into the vector database for Retrieval-Augmented Generation (RAG).

    Supported file types:
    - pdf
    - txt
    - text
    - docx
    """

    if not os.path.exists(file_path):
        print(f"File not found for RAG ingestion: {file_path}")
        return False

    try:
        # 1. Load document based on type
        if file_type.lower() == 'pdf':
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()

            for doc in documents:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['file_type'] = 'pdf'

        elif file_type.lower() in ['txt', 'text']:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()

            for doc in documents:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['file_type'] = 'txt'

        elif file_type.lower() in ['docx', 'doc']:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()

            for doc in documents:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['file_type'] = 'docx'

        else:
            print(f"Unsupported file type for RAG ingestion: {file_type}")
            return False

        # 2. Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )

        splits = text_splitter.split_documents(documents)

        if not splits:
            print("No text content could be extracted or split.")
            return False

        # 3. Generate embeddings
        texts = [doc.page_content for doc in splits]
        embeddings = embedding_manager.generate_embeddings(texts)

        # 4. Store in vector database
        vector_store.add_documents(splits, embeddings)

        print(f"Successfully ingested document {file_path} into vector store.")
        return True

    except Exception as e:
        print(f"Error ingesting document {file_path}: {e}")
        return False
