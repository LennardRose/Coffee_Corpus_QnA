import os
import fitz
import math
import re
import pandas as pd
import numpy as np
from pathlib import Path
from langdetect import detect
from collections import Counter
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline
from matplotlib import pyplot as plt
from numpy import where
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class Preprocessor:
    def __init__(self, train_data, output_dir=None):
        """
        Preprocessor for the coffee manufacturer manuals.

        Parameters
        ----------
        output_dir : Path | str
            Path for where the outputted csv-file should be saved. If not provided a pandas DataFrame will be returned.
        train_path : Path
            Path where the csv file which contains the data for  training the model. Input baby!!!
        """
        self.output_dir = output_dir
        self.train_data = train_data
           
    def _get_files(self, paths):
        """
        Method for finding all the file paths which should be processed.

        Parameters
        ----------
        paths : Path | str
            Can be a single path either to a file or a folder.
            
        Returns
        -------
        list[Path | str]
            List of all found file paths.
        """
        files = []
        
        if os.path.isfile(paths):
            print("Is File!")
            files.append(paths)
            
        if os.path.isdir(paths):
            self.machine_name = paths.rsplit('/', 1)[-1]
            print("Is Directory!")
            for file in Path(paths).glob(f"*.pdf"):
                files.append(str(file))
        
        return files
    
    def process(self, paths):
        """
        Main method for preprocessing the incoming pdf files.

        Parameters
        ----------
        paths : List[Path | str] | Path | str
            Can be either a list of file paths or simply a single path either to a file or a folder.
            
        Returns
        -------
        None | DataFrame
            Depending on if a output file path was given, if 
                - yes: the corresponding csv file will be saved at the given location
                - no: a pandas DataFrame will be outputted        
        """
        print("Processing ...")
        files = self._get_files(paths)
    
        df_list = []
        
        for file in files:
            print(f"Processing {file}")
            doc = fitz.open(file)
            
            
            file_df = self._read_pdf(doc)  
            data = pd.read_csv(self.train_data)
            classifier = self.training(data)
            df_file = self._header_classifier(file_df, classifier)
            print(df_file)
            #print(classifier)
            df_list.append(df_file)
            
        df = pd.concat(df_list, ignore_index=True)        
        #df = df[['file', 'page_nbr', 'language', 'paragraph']] #  'header1', 'header2',
                
        if self.output_dir:
            self._save_df(df)
        
        return df
    

    def _read_pdf(self, doc, cutoff=400): #, header_config
        """
        Method to extract the headers and paragraphs out of a given document.

        Parameters
        ----------
        doc : fitz.Document
            Fitz Document
        cutoff : int
            Value for how many chars should be detected on a single page in order to be deemed a "real" page
        
        Returns
        -------
        final_dic : pandas.DataFrame
            DataFrame containing information about every passage in the given document.
            With columns [file, page_nbr, language, paragraph].
        """
        passages = []
        

        for page in doc.pages():
            # determine if page is relevant for text extraction
            if not self.is_relevant_page(page, cutoff):
                continue
            
            # determine language of page
            page_language = self._get_page_language(page)
            
            # get page blocks in form of dictionary
            text = page.get_text('dict')
            for idx, block in enumerate(text['blocks']):
                if 'lines' in block:
                    for line in block['lines']:
                        for span in line['spans']:
                            span_text = span['text']
                            span_font = span['font']
                            span_size = span['size']
                            span_flags = self._flags_decomposer(span['flags'])
                            
                            
                            span_dic = {}

                            span_dic['paragraph'] = span_text                
                            span_dic['font'] = span_font
                            span_dic['size'] = span_size
                            span_dic['flags'] = span_flags
                            span_dic['page_nbr'] = page.number
                            span_dic['language'] = page_language
                            
                            passages.append(span_dic)
        
        final_dic = []
        

        
        for passage in passages:
            passage_dic = {}
            passage_text = passage['paragraph']
                            
            passage_dic['file'] = doc.name
            passage_dic['page_nbr'] = passage['page_nbr']
            passage_dic['language'] = passage['language']
            passage_dic['paragraph'] = passage_text
            passage_dic['font'] = passage['font']
            passage_dic['size'] = passage['size']
            
            final_dic.append(passage_dic)
                            
        return pd.DataFrame(final_dic)

    def is_relevant_page(self, page, cutoff):
        """
        Method to check if a page is relevant for the analysis.
        
        Parameters
        ----------
        page : fitz.Page
            Page to be checked.
        cutoff : int
            Value for how many chars should be detected on a single page in order to be deemed a "real" page
        
        Returns
        -------
        is_relevant : bool
            True if the page is relevant, False otherwise.
        """
        is_relevant = True
        text = page.get_text()
        
        if text.count('.') > 500 or sum(map(str.isdigit, text)) > 200:
            is_relevant = False
        
        if len(text) < cutoff:
            is_relevant = False
            
        # print(f"Page {page.number} has {text.count('.')} points and {sum(map(str.isdigit, text))} digits and is {is_relevant} relevant and length {len(text)}")
        
        return is_relevant

    def _get_page_language(self, page):
        """
        Method for detecting the language on a given page.

        Parameters
        ----------
        page : fitz.Page
            Pdf page read in through the fitz library.
        
        Returns
        -------
        str
            Language code for the detected language.
        """
        page_text = page.get_text('text')
        
        try:
            lang = detect(page_text)
        except:
            lang = 'No language detected!'
        
        return lang

    

    def training(self, data):
        """
        Method used to train the model using the existing training dataset

        Parameters
        ----------
        data : DataFrame
                Training dataset including the features, of course

        Returns
        -------
        classifier
                the trained model for classification
        """

        X = data.iloc[:,3:-1]   # 
        #X = data[['Bold', 'Capital', 'Text length', 'Font threshold', 'Cardinal number']]  #, 'Cardinal number'
        y =  data.iloc[:,-1:] # 
        #y = data[['Label']]

        # define pipeline
        a = len(data[data['Label']==2])
        sampling_strategy = {0: a, 2: a} # 1: a, #look into
        ros = RandomOverSampler(sampling_strategy=sampling_strategy)
        X_res, y_res = ros.fit_resample(X, y)
        #summarise the new class distribution
        counter = Counter(y)
        print(counter)

        X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2)
        classifier = tree.DecisionTreeClassifier()
        classifier = classifier.fit(X_train, y_train)

        test_prediction = classifier.predict(X_test)
        train_prediction = classifier.predict(X_train)
        test_score = accuracy_score(y_test, test_prediction)  #accuracy of test
        train_score = accuracy_score(y_train, train_prediction)  #accuracy of train
        # perform other evaluation measures
        print(f"Test accuracy: {test_score}")
        print(f"Train accuracy: {train_score}")

        return classifier


    def _header_classifier(self, final_dic, classifier):
        """
        Method to classify the paragraphs in a given document.
        Firstly, by extracting the features of the extracted text.

        Parameters
        ----------
        final_dic : pandas.DataFrame
        
        Returns
        -------
        df: pandas.DataFrame
        Dataframe containing the features extracted from .
        With columns [size, font, text, bold, capital, text length, font threshold, cardinal number, label]
        """
        df = pd.DataFrame(final_dic)
        df.columns = ['file', 'page_nbr', 'language', 'paragraph', 'font','size']
        
        df['Bold'] = df['font'].apply(lambda x: int('Bold' in x) if isinstance(x, str) else 0) # Checks if a the text in a span is bold or not
        df['Capital'] = df['paragraph'].apply(lambda x: 1 if x.isupper() else 0) # Checks if all letters in a text of a span is capital/uppercase hahahhhhh
        df['Text length'] = df['paragraph'].str.len() #sapply(strsplit(str1, " "), length)
        
        mode = df['size'].mode()
        threshold = mode[0]
        df['Font threshold'] = df['size'].apply(lambda x: 1 if x > threshold else 0)
        df['Cardinal number'] = df['paragraph'].apply(lambda x: 1 if x[0].isdigit() else 0)

        features = df[['Bold' , 'Capital', 'Text length', 'Font threshold', 'Cardinal number']] #, 'Cardinal number'
        prediction = classifier.predict(features)
        df['prediction'] = prediction

        df['grp'] = (df.prediction != df.prediction.shift()).cumsum()
        out = df.groupby(['grp', 'prediction', 'language'])['paragraph'].apply(lambda x: \
                 " ".join(x)).reset_index()[['prediction', 'paragraph', 'language']]

        df3 = out[['language', 'paragraph']]
        df4 =df3.groupby('language')['paragraph'].apply(lambda x: pd.concat([x], axis=1))
        df4.apply(lambda x: pd.Series(x.dropna().values))




        # for i in range(1, len(df)):
        #     a =df.loc[:i]
        #     if a.iloc[-1]['prediction']==2 or a.iloc[-1]['prediction']==1:
        #         df.loc[i, 'header'] = a[a['prediction']==0].iloc[-1]['paragraph']
        #     # elif a.iloc[-1]['prediction']==2:
        #     #     df.loc[i, 'subheader'] = a[a['prediction']==1].iloc[-1]['Text']
        #     else:
        #         " "

        return df4
        #return df[['file', 'page_nbr', 'language', 'paragraph', 'prediction']] #, 'header'




    def _combine_similar_blocks(self, page):
        """Method to combine following text blocks which have equal properties.

        Parameters
        ----------
        page : Fitz.Page
            A single Fitz page.
        
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the merged blocks.
        """
        passages = []

        last_span = 0   # flag for what the last span was (0 = paragraph, 1 = h1, 2 = h2)
        last_font = ""
        last_size = 0
        last_upper = False
        
        text = page.get_text('dict')

        for idx, block in enumerate(text['blocks']):
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        span_text = span['text']
                        span_font = span['font']
                        span_size = span['size']
                        span_flags = self._flags_decomposer(span['flags'])
                        
                        span_text_upper = span_text.isupper()
                        
                        span_dic = {}

                        if last_font == span_font and last_size == span_size:
                            passages[-1]['paragraph'] = passages[-1]['paragraph'] + " " + span_text
                            continue
                        else:
                            span_dic['paragraph'] = span_text
                                        
                        span_dic['font'] = span_font
                        span_dic['size'] = span_size
                        span_dic['flags'] = span_flags
                        span_dic['uppercase'] = span_text_upper
                        
                        last_font = span_font
                        last_size = span_size
                        last_upper = span_text_upper
                        
                        passages.append(span_dic)
            
        return pd.DataFrame(passages)
    
    def _combine_similar_blocks_toc(self, page):
        """
        Method to combine following text blocks in the toc which have equal properties.

        Parameters
        ----------
        page : Fitz.Page
            A single Fitz page.
        
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the merged blocks.
        """
        passages = []

        last_font = ""
        last_size = 0
        last_y0 = 0
        
        text = page.get_text('dict')

        for idx, block in enumerate(text['blocks']):
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        span_text = span['text']
                        span_font = span['font']
                        span_size = span['size']
                        span_flags = self._flags_decomposer(span['flags'])
                        span_y0 = span['bbox'][1]
                        
                        span_text_upper = span_text.isupper()
                        
                        span_dic = {}

                        if last_font == span_font and last_size == span_size and last_y0 == span_y0:
                            passages[-1]['paragraph'] = passages[-1]['paragraph'] + " " + span_text
                            continue
                        else:
                            span_dic['paragraph'] = span_text
                                        
                        span_dic['font'] = span_font
                        span_dic['size'] = span_size
                        span_dic['flags'] = span_flags
                        span_dic['uppercase'] = span_text_upper
                        
                        last_font = span_font
                        last_size = span_size
                        last_upper = span_text_upper
                        last_y0 = span_y0
                        
                        passages.append(span_dic)
            
        return pd.DataFrame(passages)
    
    def _flags_decomposer(self, flags):
        """
        Make font flags human readable.
        
        Parameters
        ----------
        flags : int
            Integer code which represent the identified flags.
        
        Returns
        -------
        string
            String which holds all flags in readable form.        
        """
        
        line = []    
        if flags & 2 ** 0:
            line.append("superscript")
        if flags & 2 ** 1:
            line.append("italic")
        if flags & 2 ** 2:
            line.append("serifed")
        else:
            line.append("sans")
        if flags & 2 ** 3:
            line.append("monospaced")
        else:
            line.append("proportional")
        if flags & 2 ** 4:
            line.append("bold")
        return ", ".join(line)
    
    
    def _save_df(self, df):
        """
        Method for saving the extracted information in a folder.

        Parameters
        ----------
        df : pandas.DataFrame
            A pandas DataFrame holding all information about the extracted values of the pdf.
        """
        out_dir_path = os.path.join(os.getcwd(), self.output_dir)
        os.makedirs(out_dir_path, exist_ok=True)
        #df.to_csv(out_dir_path + '/' + "abc3.csv")
        
        df.to_csv(out_dir_path + '/' + self.machine_name + ".csv")
        
