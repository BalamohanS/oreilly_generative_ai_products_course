import warnings

from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_aws import BedrockLLM
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langfuse.callback import CallbackHandler
# from presidio_analyzer import AnalyzerEngine
# from presidio_anonymizer import AnonymizerEngine
from config import AppConfig, create_database_engine

warnings.filterwarnings("ignore")


class Services:
    def __init__(self):
        self._init_config()
        self._init_callback_handler()
        self._init_database()
        self._init_retrievers()
        self._init_llms()
        self._init_sql_chains()
        self._init_retrieval_chains()
        self._init_advice_chains()
        self._init_recommended_chains()
        # self._init_analyzers()  # Uncomment if needed

    def _init_config(self):
        self.config = AppConfig()

    def _init_callback_handler(self):
        self.callback_handler = CallbackHandler(
            public_key=self.config.LANGFUSE_PUBLIC_KEY,
            secret_key=self.config.LANGFUSE_SECRET_KEY,
            host=self.config.LANGFUSE_HOST
        )

    def _init_database(self):
        self.db_engine = create_database_engine(self.config)
        self.sql_database = SQLDatabase(self.db_engine)

    def _init_retrievers(self):
        self.customer_support_retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=self.config.KNOWLEDGE_BASE_CUSTOMER_SUPPORT_ID,
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
        )
        self.marketing_bot_retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=self.config.KNOWLEDGE_BASE_MARKETING_BOT_ID,
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
        )

    def _init_llms(self):
        self.bedrock_llm = BedrockLLM(model_id="amazon.titan-text-express-v1")
        self.openai_llm = OpenAI(
            temperature=0,
            verbose=True,
            openai_api_key=self.config.OPENAI_API_KEY
        )

    def _init_sql_chains(self):
        self.sql_database_chain = SQLDatabaseChain(
            llm=self.openai_llm,
            database=self.sql_database,
            verbose=False
        )
        self.sql_toolkit = SQLDatabaseToolkit(db=self.sql_database, llm=self.openai_llm)
        self.sql_agent_executor = create_sql_agent(
            llm=self.openai_llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            toolkit=self.sql_toolkit,
            max_iterations=15,
            max_execution_time=60,
            top_k=3,
            verbose=True
        )

    def _init_retrieval_chains(self):
        system_prompt = (
            "Use the given context to answer the question. "
            "If you don't know the answer, say you don't know. "
            "Use three sentence maximum and keep the answer concise. "
            "Context: {context}"
        )
        self.chat_prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{input}")]
        )
        self.document_qa_chain = create_stuff_documents_chain(self.bedrock_llm, self.chat_prompt_template)
        self.retrieval_qa_chain = create_retrieval_chain(
            self.customer_support_retriever,
            self.document_qa_chain
        )

    def _init_advice_chains(self):
        classification_prompt = (
            "Given the user question below, classify it as either being about "
            "`products`, `customer reviews`, or `other`.\n\n"
            "Do not respond with more than one word.\n\n"
            "<question>\n{question}\n</question>\n\nClassification:"
        )
        self.classification_chain = (
            PromptTemplate.from_template(classification_prompt)
            | self.bedrock_llm
            | StrOutputParser()
        )

        product_prompt = (
            "You are an expert in products. Always answer questions starting with "
            '"Great that you ask about products!". Respond to the following question:\n\n'
            "Question: {question}\nAnswer:"
        )
        self.product_response_chain = PromptTemplate.from_template(product_prompt) | self.bedrock_llm

        review_prompt = (
            "You are an expert in customer reviews. Always answer questions starting with "
            '"Great that you ask about customer reviews!". Respond to the following question:\n\n'
            "Question: {question}\nAnswer:"
        )
        self.review_response_chain = PromptTemplate.from_template(review_prompt) | self.bedrock_llm

        fallback_prompt = "Respond that you cannot help with this query."
        self.fallback_response_chain = PromptTemplate.from_template(fallback_prompt) | self.bedrock_llm

        def advice_router(payload):
            topic = payload.get("topic", "").lower()
            if "product" in topic:
                return self.product_response_chain
            elif "reviews" in topic:
                return self.review_response_chain
            else:
                return self.fallback_response_chain

        self.general_advice_chain = (
            {"topic": self.classification_chain, "question": lambda payload: payload["question"]}
            | RunnableLambda(advice_router)
        )

    def _init_recommended_chains(self):
        recommended_image_template = PromptTemplate.from_template(
            """You are helping select the best image to represent a persona.

            Persona description:
            {persona}

            Available images and captions:
            {caption_list}

            From the above, select the most fitting image filename and explain why.
            Return your answer in this format:

            Filename: <filename>
            Reason: <short explanation>
            """
        )
        self.recommended_image_chain = recommended_image_template | self.bedrock_llm

        self.marketing_tours_chain = create_stuff_documents_chain(self.bedrock_llm, self.chat_prompt_template)
        self.recommended_tour_chain = create_retrieval_chain(
            self.marketing_bot_retriever,
            self.marketing_tours_chain
        )

    # Uncomment and adjust the following if you need to initialize analyzers.
    # def _init_analyzers(self):
    #     self.pii_analyzer = AnalyzerEngine()
    #     self.pii_anonymizer = AnonymizerEngine()


services = Services()