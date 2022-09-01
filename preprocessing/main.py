from preprocessing import Preprocessor
import pandas as pd

# Expected Directory Structure:
# 
# manufacturer_X/
# ├── machine_0/
# │   ├── manual_ger
# │   ├── manual_en
# │   ├── manual_fr
# │   └── ...
# ├── machine_1/
# │   └── manual_all_languages
# └── machine_2/
#     ├── manual_ger
#     ├── manual_en
#     ├── manual_fr
#     └── ...
# 
# manufacturer_Y/
# ├── machine_0/
# │   ├── manual_ger
# │   ├── manual_en
# │   ├── manual_fr
# │   └── ...
# ├── machine_1/
# │   └── manual_all_languages
# └── machine_2/
#     ├── manual_ger
#     ├── manual_en
#     ├── manual_fr
#     └── ...



if __name__ == '__main__':
    
    # load config
    
    # instantiate preprocessor
    pp = Preprocessor(output_dir='output_preprocessing')
    output = pp.process('example_pdfs/single_test_toc')  
    
    # output.to_csv("output/main_out.csv")