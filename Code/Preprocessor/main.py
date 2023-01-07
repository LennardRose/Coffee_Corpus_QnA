from Code.Preprocessor.preprocessor import Preprocessor
import json


if __name__ == '__main__':
        
    # instantiate preprocessor
    pp = Preprocessor(mode=1, output_path='output_preprocessing/', model_path='models/visual', verbose='DEBUG')
    output = pp.process('PATH TO MANUALS')
    
    # save json output to file
    with open('output_preprocessing/corpus.json', 'w') as fp:
        json.dump(output, fp, indent=2)