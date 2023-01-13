from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
from elasticsearch.helpers import bulk
import json

class Elastic(object):
	def __init__(self):
		self.client = Elasticsearch('http://localhost:9200')

	def create_index(self, name, config_file):
		try:
			with open(config_file) as file:
				config = json.load(file)

			self.client.indices.create(index=name, body=config)
			print(f"[INFO] index {name} has been created!")
		except Exception as e:
			print(e)

	def index_documents(self, data):
		"""
		Save multiple documents with the same structure to an elastic index
		:param data: list documents, e.g.
		[
			{'_op_type': 'index', '_index': 'name', 'text': 'doc1',...},
			{'_op_type': 'index', '_index': 'name', 'text': 'doc2',...},
		]
		where: 	`_op_type` is the operation, we want to `index` documents in this case,
				`_index` is the name of the index to which we want to store our documents.
		"""
		bulk(self.client, actions=data)


	def search(self, index_name: str, script_query: dict, n_returns: int, list_fields_to_return: list):
		try:
			response = self.client.search(
				index=index_name,
				body={
					"size": n_returns,
					"query": script_query,
					"_source": {"includes": list_fields_to_return}
				},
			)
			return response
		except ConnectionError:
			print("Elastic server not found!")
		except NotFoundError:
			print(f"Index {index_name} not found!")

	def delete_index(self, name):
		try:
			self.client.indices.delete(index=name)
			print(f"Index {name} has been deleted successfully!")
		except ConnectionError:
			print("Elastic server not found!")
		except NotFoundError:
			print(f"Index {name} not found!")
