import csv
import glob
import fitz
import os
import numpy as np
import pandas as pd

class Data_preparation:
    def __init__(self, label_list, out_path=None):
        """
        Preparation of the dataset needed to train a ML model

        Parameters
        ----------
        out_path
                 path where the outputted csv file should be saved
        label_list
                 list containing the labelling parameters (kinda weird)
                 
        """
        self.out_path = out_path
        self.label_list = label_list

    def preparation(self, path):
        """
        Main method for preparing the dataset 

        Parameters
        ----------
        path
             file path of the manual

        Returns:
        -------
        None | DataFrame
            Depending on if a output file path was given, if 
                - yes: the corresponding csv file will be saved at the given location
                - no: a pandas DataFrame will be outputted        
        """

        self.path = path
        doc = fitz.open(path)
        results = self._read_pdf(doc)
        df = self._extract_features(results)

        #print(df)

        #df = df[['Size', 'Font', 'Text']]
        # , 'Bold', 'Capital', 'Text length', 'Font threshold', 'Cardinal number', 'Label

        if self.out_path:
            self._save_df(df) 
        
        return df
        
    def _read_pdf(self, doc):
        """
        Method to extract the text paragraphs out of a given document.

        Parameters
        ----------
        doc : fitz.Document
            Fitz Document
        
        Returns
        -------
        results : list
            List containing information about the properties of every span in the given document
            [size, font, text]
        """

        def _flags_decomposer(flags):
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

        results = []
        
        for page in doc:
            text = page.get_text("dict", flags=11)
            blocks = text["blocks"]
            
            for block in blocks: #iterate through the text block
                for line in block["lines"]: #iterate through the text lines
                    for span in line["spans"]: #iterate through the text span
                        results.append([span["size"], span["font"], span["text"]])
                        
        return results

    def _extract_features(self, results):
        """
        Method to extract the features of the lines of a given document

        Parameters
        ----------
        results : list
        List containing information about the properties (text, font, size) of each span

        Returns
        -------
        df: pandas.DataFrame
        Dataframe containing the features extracted from results and its corresponding label.
        With columns [size, font, text, bold, capital, text length, font threshold, cardinal number, label]
        Features vary w.r.t the manufacturers
        """
        df = pd.DataFrame(results)
        df.columns = ['Size', 'Font', 'Text']
        
        df['Bold'] = df['Font'].apply(lambda x: int('Bold' in x) if isinstance(x, str) else 0) # Checks if a the text in a span is bold or not
        df['Capital'] = df['Text'].apply(lambda x: 1 if x.isupper() else 0) # Checks if all letters in a text of a span is capital/uppercase hahahhhhh
        df['Text length'] = df['Text'].str.len() #sapply(strsplit(str1, " "), length)
        
        mode = df['Size'].mode()
        threshold = mode[0]
        df['Font threshold'] = df['Size'].apply(lambda x: 1 if x > threshold else 0)
        df['Cardinal number'] = df['Text'].apply(lambda x: 1 if x[0].isdigit() else 0)


        def label_df(df):
            if len(self.label_list)==6:
                if (df['Size'] == self.label_list[0]) and (df['Bold'] == self.label_list[1]) and (df['Capital'] == self.label_list[2]):
                    return 0  #Header
                elif (df['Size'] == self.label_list[3]) and (df['Bold'] == self.label_list[4]) and (df['Capital'] == self.label_list[5]):
                    return 1   #Subheader
                else:
                    return 2

            elif len(self.label_list)==3:
                if (df['Size'] == self.label_list[0]) and (df['Bold'] == self.label_list[1]) and (df['Capital'] == self.label_list[2]):
                    return 0  #Header
                else:
                    return 2
                    
        df['Label'] = df.apply(label_df, axis=1)

        return df


    def _save_df(self, df):
        """
        Method for saving the extracted information in a folder.

        Parameters
        ----------
        df : pandas.DataFrame
            A pandas DataFrame holding all information about the extracted values of the pdf.
        """
        name = str(os.path.split(self.path)[-1][:-4])
        df.to_csv(self.out_path + '\\' + name + '.csv', index=False, header=True)


    def merge_csv(self, dataset_path):
        """
        Method for merging all the csv files containing the extracted features into one csv file.

        Parameters
        ----------
        dataset_path/out_path

        """

        file_list = glob.glob(self.out_path + "/*.csv")

        # list of csv files to be merged.
        csv_list = []

        for file in file_list:
            csv_list.append(pd.read_csv(file))

        csv_merged = pd.DataFrame()

        for csv_file in csv_list:
            csv_merged = csv_merged.append(csv_file, ignore_index=True)

        """ALTERNATIVE TO DEPRECATED APEND"""
        # csv_merged = csv_merged.append(csv_file, ignore_index=True)
        #mit concat
        # csv_merged = pd.concat([csv_merged, pd.DataFrame.from_records(csv_file)])

        # exports the dataframe into excel file with specified name.
        return csv_merged.to_csv(dataset_path)

