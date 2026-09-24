class RAGRetriever:

    def __init__(self, vector_store):
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    def retrieve(self, query):
        return self.retriever.invoke(query)