from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:

    def split(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        return splitter.split_documents(documents)