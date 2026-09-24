from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


class VectorStore:

    def create(self, documents):
        embeddings = OllamaEmbeddings(
            model="qwen3-embedding:0.6b"
        )

        return Chroma.from_documents(
            documents,
            embeddings,
            persist_directory="vector_store",
            collection_name="automotive_knowledge"
        )