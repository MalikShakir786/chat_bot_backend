import os
import uuid
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from typing import List, Any, Dict, Optional


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

    def query(self, query_embedding: List[float], top_k: int = 5):
        self._initialize_store()
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )


class RagRetriever:
    """
    Retrieves the most relevant chunks for a query.

    Note on scoring: Chroma's default distance metric is L2 distance (lower = more
    similar), NOT a similarity score. We convert distance -> a 0..1 "similarity"
    value (1 / (1 + distance)) so that higher = better matches the intuitive meaning
    of `min_score`/`confidence` used by API consumers.
    """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def get_relevant_documents(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        results = self.vector_store.query(query_embedding.tolist(), top_k=top_k)

        retrieved_docs: List[Dict[str, Any]] = []

        if results.get('documents') and results['documents'][0]:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]

            for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
                similarity_score = 1.0 / (1.0 + distance)

                if similarity_score >= min_score:
                    retrieved_docs.append({
                        "page_content": doc,
                        "metadata": metadata,
                        "distance": distance,
                        "similarity_score": similarity_score,
                        "doc_id": doc_id,
                        "rank": i + 1
                    })

        return retrieved_docs


# Initialize global managers lazily
embedding_manager = EmbeddingManager()
vector_store = VectorStore()
rag_retriever = RagRetriever(vector_store, embedding_manager)

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        _llm = ChatGroq(
            api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=1024,
        )
    return _llm


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


def query_documents(
    query: str,
    top_k: int = 3,
    min_score: float = 0.0,
) -> Dict[str, Any]:
    """
    Runs the retrieve -> generate RAG pipeline for a chat query.

    Returns a dict with: answer, sources, confidence, has_context
    """
    results = rag_retriever.get_relevant_documents(query, top_k=top_k, min_score=min_score)

    if not results:
        return {
            "answer": "I couldn't find anything relevant in the uploaded documents to answer that.",
            "sources": [],
            "confidence": 0.0,
            "has_context": False,
        }

    context = "\n\n".join([doc["page_content"] for doc in results])

    sources = [
        {
            "source": doc["metadata"].get("source", "unknown"),
            "file_type": doc["metadata"].get("file_type", "unknown"),
            "page": doc["metadata"].get("page", None),
            "similarity_score": round(doc["similarity_score"], 4),
            "preview": doc["page_content"][:200],
        }
        for doc in results
    ]

    confidence = max(doc["similarity_score"] for doc in results)

    prompt = f"""Use the following context to answer the question concisely.
If the answer cannot be found in the context, say so honestly instead of guessing.

Context:
{context}

Question:
{query}

Answer:"""

    llm = _get_llm()
    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources,
        "confidence": round(confidence, 4),
        "has_context": True,
    }