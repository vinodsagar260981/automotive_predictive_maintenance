from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class LLMService:

    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0
        )

    def explain_prediction(self, prediction, documents):
        context = "\n\n".join(document.page_content for document in documents)

        prompt = f"""
            You are an automotive predictive maintenance engineer.

            Vehicle prediction:
            Vehicle ID: {prediction["vehicle_id"]}
            Anomaly Status: {prediction["anomaly_status"]}
            Failure Probability: {prediction["failure_probability"]}

            Engineering knowledge:
            {context}

            Explain the prediction using the engineering knowledge provided.

            Rules:
            - Do not invent sensor values.
            - Do not invent faults.
            - Do not claim a failure will occur.
            - Do not introduce information that is not supported by the provided engineering knowledge.
            - If the provided knowledge is insufficient, clearly say so.
            - Keep the explanation concise and technical.
            """

        response = self.llm.invoke(prompt)

        return response.content