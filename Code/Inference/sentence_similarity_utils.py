from . import ElasticSearchClient
from . import config
import logging

def get_query_contexts(query: str,
                       manufacturer: str,
                       product: str,
                       language: str,
                       es_client: ElasticSearchClient,
                       num_contexts: int = 1):
    """
     Get context for a single query
    :param query:
    :param es_client:
    :return:
    """
    
    embedder = es_client.embedder
    query_vector = embedder.embed_single_text([query])[0].tolist()

    script_query = {
        "query": {
            "bool": {
                "must": [{ "match": { "manufacturer": manufacturer}},
                         { "match": { "product": product }},
                         { "match": { "language": language}}]
                }},
        "script": {
            "source": f"cosineSimilarity(params.query_vector, data['paragaraphTextVector']) + 1.0",
            # Add 1.0 because ES doesnt support negative score
            "params": {"query_vector": query_vector}
        }
    }


    try:
        response = es_client.search(
            index = config.corpus_metaIndex,
            body = {
                "size": num_contexts,
                "query": script_query,
                "_source": {"includes": ["paragraphText"]}
            })                          
                                    
        res = []
        for hit in response["hits"]["hits"]:
            res.append([hit["_source"]["paragraphText"], hit["_score"] - 1])
        return res

    except Exception as e:
        # use a logger here
        #logging.error("an error occured", e)
        print(e)


