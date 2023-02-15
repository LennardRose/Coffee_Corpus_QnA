from sentence_transformers import SentenceTransformer
import Code.Clients.client_factory as factory
import json
from tqdm import tqdm
from Code.config import config
from Code.SimilaritySearch.embedders import FinetunedAllMiniLMEmbedder


if __name__ == '__main__':
    with open("output_preprocessing/corpus.json") as f:
        corpus = json.load(f)

    docs = []
    batch_size = 1000
    count = 0
    embedder = SentenceTransformer(config.EMBEDDER)

    for entry in tqdm(corpus, "manufacturers"):
        manufacturer = entry["manufacturer"]
        for product in tqdm(entry["products"], "products"):
            p_id = product["product_id"]
            for language in product["languages"]:
                lang = language
                for header in product["languages"][language]:
                    h_id = header["headerId"]
                    h_text = header["headerText"]
                    h_paragraph = header["paragraphText"]
                    # TODO: filter entries with empty paragraphs etc.
                    if header["headerChildren"]:
                        for subheader in header["headerChildren"]:
                            sh_id = subheader["subHeaderId"]
                            sh_text = subheader["subHeaderText"]
                            sh_paragraph = subheader["paragraphText"]

                            embedding = embedder.encode(h_text + " " + h_paragraph + " " + sh_text + " " + sh_paragraph)
                            doc = {
                                "manufacturer": manufacturer,
                                "product": p_id,
                                "language": lang,
                                "headerId": h_id,
                                "headerText": h_text,
                                "headerParagraphText": h_paragraph,
                                "subHeaderId": sh_id,
                                "SubHeaderText": sh_text,
                                "subHeaderParagraphText": sh_paragraph,
                                "vector_embedding": embedding
                            }

                    else:
                        embedding = embedder.encode(h_text + " " + h_paragraph)
                        doc = {
                            "manufacturer_name": manufacturer,
                            "product_name": p_id,
                            "language": lang,
                            "headerId": h_id,
                            "headerText": h_text,
                            "headerParagraphText": h_paragraph,
                            "subHeaderId": None,
                            "SubHeaderText": None,
                            "subHeaderParagraphText": None,
                            "vector_embedding": embedding
                        }

                    docs.append(doc)
                    count += 1

                    if count % batch_size == 0:
                        factory.get_context_client().bulk_index_contexts(docs)
                        docs = []