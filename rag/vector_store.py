from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings


class VectorStore:

    def create(self, documents):
        embeddings = OllamaEmbeddings(
            model="qwen3-embedding:0.6b"
        )

        return FAISS.from_documents(documents, embeddings)