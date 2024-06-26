from typing import List

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select

from dialog.models import CompanyContent
from dialog.models.db import get_session
from dialog.settings import Settings

EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=Settings().OPENAI_API_KEY)

def generate_embeddings(documents: List[str]):
    """
    Generate embeddings for a list of documents
    """
    return EMBEDDINGS_LLM.embed_documents(documents)


def generate_embedding(document: str):
    """
    Generate embeddings for a single instance of document
    """
    return EMBEDDINGS_LLM.embed_query(document)


def get_most_relevant_contents_from_message(message, top=5, dataset=None, session=None):
    if session is None:
        session = next(get_session())

    message_embedding = generate_embedding(message)
    filters = [
        CompanyContent.embedding.cosine_distance(message_embedding) < Settings().COSINE_SIMILARITY_THRESHOLD,
    ]

    if dataset is not None:
        filters.append(CompanyContent.dataset == dataset)

    possible_contents = session.scalars(
        select(CompanyContent)
        .filter(*filters)
        .order_by(CompanyContent.embedding.cosine_distance(message_embedding))
        .limit(top)
    ).all()
    return possible_contents
