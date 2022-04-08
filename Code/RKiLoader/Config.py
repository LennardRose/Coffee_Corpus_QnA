# -------------------------------miscellaneous------------------------------------------
path_to_city_csv = './Cities.csv'

german_state_list = ['Hamburg', 'Bremen', 'Bayern', 'Baden-Wuertemberg', 'Sachsen', 'Sachsen-Anhalt', 'Thueringen', 'Hessen',
                     'Schleswig-Holstein', 'Brandenburg', 'Nordrhein-Westfalen', 'Saarland', 'Niedersachsen', 'Berlin', 'Mecklenburg-Vorpommern', 'Rheinland-Pfalz']
german_state_list_abbreviated = ['BY', 'BE', 'BW', 'BB', 'HB',
                                 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH']

# -------------------------------corona api---------------------------------------------
corona_api_base_url = 'https://api.corona-zahlen.org/'
corona_api_states = 'states/'
corona_api_districts = 'districts/'
corona_api_vaccinations = 'vaccinations'
corona_api_testing = 'testing/history'

# -------------------------------elasticserach------------------------------------------
elasticsearch_url = '127.0.0.1'
elasticsearch_port = '9200'

elasticsearch_vaccination_index = 'rki_vaccination'
elasticsearch_meta_index = 'rki_meta'
elasticsearch_testing_index = 'rki_testing'
elasticsearch_incidence_index = 'rki_incidence'

# -------------------------------hdfs---------------------------------------------------
hdfs_base_url = '192.168.0.115'
hdfs_port = '9870'

hdfs_vaccination_base_path = '/datakraken/rki/vaccination/'
hdfs_testing_base_path = '/datakraken/rki/testing/'
hdfs_incidence_state_base_path = '/datakraken/rki/incidence/states/'
hdfs_incidence_district_base_path = '/datakraken/rki/incidence/districts/'
