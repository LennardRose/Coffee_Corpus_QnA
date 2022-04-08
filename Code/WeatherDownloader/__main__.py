from ElasticSearchWrapper import ElasticSearchClient
import pandas as pd
from Config import *
import time

if __name__ == "__main__":
    es_client = ElasticSearchClient()
    city_df = pd.read_csv(file_to_city_csv, header=0, sep=';')
    for index, row in city_df.iterrows():
        if(index == 50):
            time.sleep(70)
        es_client.get_weather_data_by_city(
            city=row['name'], federal_state=row['federalState'], border='border')
