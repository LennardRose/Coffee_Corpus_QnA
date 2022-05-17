import os
import fitz
import pandas as pd
from pathlib import Path
from langdetect import detect

class Preprocessor:
    def __init__(self, safe_path=None):
        """
        Preprocessor for the coffee manufacturer manuals.

        Parameters
        ----------
        safe_path : Path | str
            Path for where the outputted csv-file should be saved. If not provided a pandas DataFrame will be returned.
        """
        self.safe_path = safe_path
        
        # TODO: Dynamically set the font and sizes to search for the headings in the document
        # self.font_header = "MyriadPro-BoldCond"
        # self.size_header1 = 11
        # self.size_header2 = 9
        self.font_header = "MyriadPro-Bold"
        self.size_header1 = 12
        self.size_header2 = 9
    
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
        
        # TODO: Test if it works for folders
        if os.path.isfile(paths):
            print("Is File!")
            files.append(paths)
            
        if os.path.isdir(paths):
            print("Is Directory!")
            for file in Path(paths).glob(f"*.pdf"):
                files.append(str(file))
        
        print(files)
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
                - yes: the corresponding csv file will be safed at the given location
                - no: a pandas DataFrame will be outputted        
        """
        print("Processing ...")
        files = self._get_files(paths)
        
        # if len(files) > 1:
        #     # do preprocessing for multiple pdfs
        #     pass
        # else:
        #     # do preprocessing for single pdf   
        #     extracted_structure = self._read_pdf() 
        #     pass
        
        # TODO: Implement logic for reading in different language manuals for the same coffee machine
        for file in files:
            df = pd.DataFrame(self._read_pdf(file))
                
        df = df[['file', 'language', 'header1', 'header2', 'paragraph']]
        
        # TODO: If self.save_path is set save the output there
        
        return df
    
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
        return detect(page.get_text('text'))
        
    
    def _read_pdf(self, single_path):
        """
        Method for reading in a single pdf and extracting the wanted information.

        Parameters
        ----------
        single_path : Path | str
            Specific path for a single pdf.
            
        Returns
        -------
        list[dict[]]
            List of each identified paragraph in the form of ['file', 'language', 'page_nbr', 'paragraph', 'header1', 'header2'].
        """
        # TODO: Refactor this method
        document = fitz.open(single_path)
        document_pages = document.pages()
        
        headline1 = None
        headline2 = None

        terminating_symbols = ('.', ':', '!', '?', ';')
        
        last_span = 0   # flag for what the last span was (0 = paragraph, 1 = h1, 2 = h2)
        
        page_structure = []
        
        for idx, page in enumerate(document_pages):
            page_language = self._get_page_language(page)
            text = page.get_text('dict')
            
            for block in text['blocks']:
                if 'lines' in block:
                    for line in block['lines']:

                        for span in line['spans']:
                            span_text = span['text']
                            span_font = span['font']
                            span_size = span['size']
                            span_dic = {}

                            
                            if span_text.isnumeric():
                                continue
                            
                            if span_font == self.font_header and span_size == self.size_header1:
                                last_span = 1
                                headline1 = span_text
                                headline2 = None
                                continue
                            
                            if span_font == self.font_header and span_size == self.size_header2:
                                last_span = 2
                                headline2 = span_text
                                continue
                            
                            span_dic['file'] = single_path
                            span_dic['language'] = page_language
                            span_dic['page_nbr'] = idx + 1
                            span_dic['paragraph'] = span_text
                            
                            if not headline1:
                                continue
                            
                            if page_structure and not page_structure[-1]['paragraph'].rstrip().endswith(terminating_symbols) and last_span == 0:
                                page_structure[-1]['paragraph'] = page_structure[-1]['paragraph'] + span_text
                                continue
                                
                            span_dic['header1'] = headline1
                            span_dic['header2'] = headline2
                            
                            last_span = 0
                            
                            page_structure.append(span_dic)

        return page_structure