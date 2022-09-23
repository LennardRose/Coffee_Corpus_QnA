from preprocessing import Preprocessor
import pandas as pd

if __name__ == '__main__':
    
    # load config
    
    # instantiate preprocessor
    train_data = r'...\RusselHobbs\RusselHobbs.csv'
    pp = Preprocessor(train_data, output_dir=r'...\RusselHobbs')
    
    
    output = pp.process(r'...\RusselHobbs\test\N27011-56_9707_19_FEB20.pdf') # path/directory of input pdf

