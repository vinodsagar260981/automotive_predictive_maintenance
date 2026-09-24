from langchain_community.document_loaders import TextLoader


class DocumentLoader:

    def load(self, file_path: str):
        loader = TextLoader(file_path)
        return loader.load()