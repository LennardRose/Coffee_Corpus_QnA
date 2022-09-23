from preparation import Data_preparation
import pandas as pd


if __name__ == '__main__':
    
    # load config
    
    # instantiate preprocessor
    label_list = [16,1,0,13,1,0]
    pp = Data_preparation(label_list, out_path= r'...\RusselHobbs') # output directory
    output = pp.preparation(r'...\RusselHobbs\N20680-56_9707_14_JUN19.pdf')  # file path

    #merge = pp.merge_csv(r'...\RusselHobbs\abcd.csv') # path of merged files
    
