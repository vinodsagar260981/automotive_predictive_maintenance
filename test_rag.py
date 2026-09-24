from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever


loader = DocumentLoader()
documents = loader.load("knowledge/vibration_diagnostics.txt")

splitter = TextSplitter()
chunks = splitter.split(documents)

vector_store = VectorStore()
store = vector_store.create(chunks)

retriever = RAGRetriever(store)

documents = retriever.retrieve("CAR-001 has an Engine RPM anomaly")

for document in documents:
    print(document.page_content)