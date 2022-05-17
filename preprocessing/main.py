from preprocessing import Preprocessor
import pandas as pd

if __name__ == '__main__':
    
    # load config
    
    # instantiate preprocessor
    pp = Preprocessor()
    
    # Out Delonghi
    # output = pp.process("example_pdfs/ESAM04110B-167807_DeLonghi.pdf")
    
    # Out Russelhobbs
    output = pp.process('example_pdfs/N25610-56_9707_11_OCT19_Russelhobbs.pdf')
    
    output.to_csv("output/main_out.csv")