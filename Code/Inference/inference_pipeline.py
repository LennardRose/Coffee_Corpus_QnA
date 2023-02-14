from . import ElasticSearchClient
from . import config
import argparse
from sentence_similarity_utils import get_query_contexts
from qa_utils import get_qa_model

def get_elastic_client(reindex=False) -> ElasticSearchClient:
    """
    Get elastic client
    :param reindex:
    :return:
    """
    es_client = ElasticSearchClient()
    if reindex:
        es_client.index_corpusfile_metadata(config.CORPUSPATHS)

    return es_client


def generate_payload(query: str,
                     manufacturer: str,
                     product: str,
                     language: str,
                     es_client: ElasticSearchClient) -> dict:
    """

    :param query:
    :param manufacturer:
    :param product:
    :param es_client:
    :return:
    """
    context = get_query_contexts(query,
                                  manufacturer,
                                  product,
                                  language,
                                  es_client)
    payload = {
        "question": query,
        "context": context
    }

    return payload


def online_inference(pay_load: dict, model)-> dict:
    """
        Returns  json repsonse for
        a single query of the model


    Args:
        pay_load (str): all information required
                        to make a prediction
        model (_type_): _description_
    """
    response = model(question=pay_load["question"],
                context=pay_load["context"])
    response["question"] = pay_load["question"]
    return response




if __name__ == "main":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default="the query question")
    parser.add_argument("--manufacturer", type=str, default="the manufacturer")
    parser.add_argument("--product", type=str, default="the product")
    parser.add_argument("--language", type=str, default="the language")
    args = parser.parse_args()

    # get elastic search client
    es_client = get_elastic_client(config.reindex_corpus)

    # get trained qa model
    model = get_qa_model()

    # get context using similarity serach
    payload = generate_payload(args.query,
                               args.manufacturer,
                               args.product,
                               args.language,
                               es_client)

    # get answer
    answer = online_inference(payload, model)
