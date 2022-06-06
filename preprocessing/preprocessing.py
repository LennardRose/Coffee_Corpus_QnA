import os
import fitz
import pandas as pd
import numpy as np
import statistics
from pathlib import Path
from langdetect import detect

class Preprocessor:
    def segment(document):
        def flags_decomposer(flags):
            """Make font flags human readable."""
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
        for page in document:
            # read page text as a dictionary, suppressing extra spaces in CJK fonts (%dic)
            dict= page.get_text("dict", flags=11)
            blocks = dict["blocks"]

            for block in blocks:  # iterate through the text blocks

                for line in block["lines"]:  # iterate through the text lines

                    for span in line["spans"]:  # iterate through the text spans
                        results.append([span["size"], span["font"],span["text"]])  #,s["font"],s["color"]

        header = []
        counter = 0
        substring = "Bold"

        for t in range(len(results)):
            if (substring in results[t][1] and len(results[t][2])>4):
                header.append(results[t][0])
                if (results[t][0]>10.8 and results[t][0]<11.2):
                    counter=counter+1

        header2 = []
        mode1=statistics.mode(header)

        for u in range(len(header)):
            if(header[u] != mode1):
                header2.append(header[u])
        mode2=statistics.mode(header2)

        if (mode1 > mode2):
            size_header1 = mode1
            size_header2 = mode2
        else:
            size_header1 = mode2
            size_header2 = mode1

        return size_header1, size_header2
    
    def __init__(self, output_dir=None):
        """
        Preprocessor for the coffee manufacturer manuals.

        Parameters
        ----------
        safe_path : Path | str
            Path for where the outputted csv-file should be saved. If not provided a pandas DataFrame will be returned.
        """
        self.output_dir = output_dir

    
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
                - yes: the corresponding csv file will be safed at the given location
                - no: a pandas DataFrame will be outputted        
        """
        print("Processing ...")
        files = self._get_files(paths)
    
        df_list = []
        
        for file in files:
            print(f"Processing {file}")
            doc = fitz.open(file)
            header_config = self._get_header_properties(doc)
            file_df = self._read_pdf(doc, header_config)
            print(file_df)
            df_list.append(file_df)
            
        df = pd.concat(df_list, ignore_index=True)        
        df = df[['file', 'page_nbr', 'language', 'header1', 'header2', 'paragraph']]
                
        if self.output_dir:
            self._save_df(df)
        
        return df
    
    def _get_header_properties(self, doc):
        """
        Method to identify the header properties in a given pdf document for header.
        
        TODO: What if document does not have ToC -> How to determine Header Properties?

        Parameters
        ----------
        doc : fitz.Document
            Document object read in with the Fitz Library.
            
        Returns
        -------
        header_config : dict
            Dictionary containing the information about both header1 and header2.

        """
        header_config = {}
        
        fitz_toc = doc.get_toc()
        
        if fitz_toc:
            # if fitz finds an underlying toc in the document, use that to find the attributes of the headers
            
            if len(fitz_toc) > 10:
                # do sth
                df_toc = pd.DataFrame(fitz_toc, columns=['header_lvl', 'header', 'page_nbr'])
                
                header1_entry = df_toc.loc[df_toc['header_lvl'] == 1].iloc[0]
                header1 = header1_entry['header']
                page_nbr_header1 = header1_entry['page_nbr']
                
                header2_entry = df_toc.loc[df_toc['header_lvl'] == 2].iloc[0]
                header2 = header2_entry['header']
                page_nbr_header2 = header2_entry['page_nbr']
            
                header1_dic = {}    
                page_blocks = self._combine_similar_blocks(doc.load_page(int(page_nbr_header1 - 1)))

                # TODO: Refactor the block into a reusable function
                matched_block = page_blocks[page_blocks['paragraph'].str.replace(" ", "").str.contains(header1.replace(" ", "").replace("\t", ""))].iloc[0]
                header1_dic['font'] = matched_block['font']
                header1_dic['size'] = matched_block['size']
                header1_dic['flags'] = matched_block['flags']
                header1_dic['uppercase'] = matched_block['uppercase']
                
                header2_dic = {}
                page_blocks = self._combine_similar_blocks(doc.load_page(int(page_nbr_header2 - 1)))

                matched_block = page_blocks[page_blocks['paragraph'].str.replace(" ", "").str.contains(header2.replace(" ", "").replace("\t", ""))].iloc[0]           
                header2_dic['font'] = matched_block['font']
                header2_dic['size'] = matched_block['size']
                header2_dic['flags'] = matched_block['flags']
                header2_dic['uppercase'] = matched_block['uppercase']
                
                header_config['header1'] = header1_dic
                header_config['header2'] = header2_dic
            else:
                # if fitz does not find a toc, manually search for one in the document
                toc_page = self._manually_find_toc_page(doc)
                page_blocks_toc = self._combine_similar_blocks_toc(toc_page)
                
                # for the case the toc has numbers
                page_blocks_toc = page_blocks_toc.loc[(page_blocks_toc['paragraph'].str[0].str.isdigit()) & (page_blocks_toc['paragraph'].str.len() > 1)]
                
                # TODO: Find a more sophisticated method to chose examples for h1 and h2
                # TODO: Page Nbr from ToC is not always true
                header1_entry = page_blocks_toc.iloc[0]
                header1, page_nbr_header1 = "1. Introduction", 5     # TODO: Replace with regex to extract groups
                
                header2_entry = page_blocks_toc.iloc[1]
                header2, page_nbr_header2 = "1.1 Letters in brackets", 5    # TODO: Replace with regex to extract groups
                
                header1_dic = {}    
                page_blocks = self._combine_similar_blocks(doc.load_page(int(page_nbr_header1 - 1)))
                            
                matched_block = page_blocks[page_blocks['paragraph'].str.replace(" ", "").str.lower().str.contains(header1.replace(" ", "").replace("\t", "").lower())].iloc[0]
                header1_dic['font'] = matched_block['font']
                header1_dic['size'] = matched_block['size']
                header1_dic['flags'] = matched_block['flags']
                header1_dic['uppercase'] = matched_block['uppercase']
                
                header2_dic = {}
                page_blocks = self._combine_similar_blocks(doc.load_page(int(page_nbr_header2 - 1)))

                matched_block = page_blocks[page_blocks['paragraph'].str.replace(" ", "").str.lower().str.contains(header2.replace(" ", "").replace("\t", "").lower())].iloc[0]        
                header2_dic['font'] = matched_block['font']
                header2_dic['size'] = matched_block['size']
                header2_dic['flags'] = matched_block['flags']
                header2_dic['uppercase'] = matched_block['uppercase']
                
                header_config['header1'] = header1_dic
                header_config['header2'] = header2_dic            

        return header_config
    
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
        
        df.to_csv(out_dir_path + '/' + self.machine_name + ".csv")
    
    def _manually_find_toc_page(self, doc):
        """
        Method to manually search for the ToC in a given pdf document.

        Parameters
        ----------
        pages : fitz.Document
            Document object read in with the Fitz Library.
            
        Returns
        -------
        toc_page : fitz.Page
            Fitz page of a given document.
        """
        
        point_count = []
        number_count = []

        doc_pages = doc.pages()

        for page in doc_pages:
            text = page.get_text()

            point_count.append(text.count('.'))
            number_count.append(sum(map(str.isdigit, text)))
            
        np.array(point_count)
        np.array(number_count)

        idx = int(np.argmax(point_count))   
        toc_page = doc.load_page(idx)
        
        return toc_page
    
    
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
        
    
    def _read_pdf(self, doc, header_config, cutoff=500):
        """
        Method to extract the headers and paragraphs out of a given document.

        Parameters
        ----------
        doc : fitz.Document
            Fitz Document
        header_config : dict
            Dictionary containing the information about both header1 and header2
        cutoff : int
            Value for how many chars should be detected on a single page in order to be deemed a "real" page
        
        Returns
        -------
        final_dic : pandas.DataFrame
            DataFrame containing information about every passage in the given document.
            With columns [file, page_nbr, language, header1, header2, paragraph].
        """
        passages = []
        
        header1_config = header_config['header1']
        header2_config = header_config['header2']
        
        last_span = 0   # flag for what the last span was (0 = paragraph, 1 = h1, 2 = h2)
        last_font = ""
        last_size = 0
        last_upper = False

        for page in self._get_relevant_pages(doc, cutoff):
            text = page.get_text('dict')
            page_language = self._get_page_language(page)
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

                            if last_font == span_font and last_size == span_size and last_upper == span_text_upper:
                                passages[-1]['paragraph'] = passages[-1]['paragraph'] + " " + span_text
                                continue
                            else:
                                span_dic['paragraph'] = span_text
                                            
                            span_dic['font'] = span_font
                            span_dic['size'] = span_size
                            span_dic['flags'] = span_flags
                            span_dic['uppercase'] = span_text_upper
                            span_dic['page_nbr'] = page.number
                            span_dic['language'] = page_language
                            
                            last_font = span_font
                            last_size = span_size
                            last_upper = span_text_upper
                            
                            passages.append(span_dic)
        
        final_dic = []
        
        header1 = None
        header2 = None
        
        for passage in passages:
            passage_dic = {}
            
            passage_text = passage['paragraph']
            
            if passage_text.isnumeric() or len(passage_text) <= 2:
                continue
            
            if self._check_header_conditions(passage, header1_config):
                header1 = passage_text
                header2 = None
                continue
                
            if self._check_header_conditions(passage, header2_config):
                header2 = passage_text
                continue
                
            passage_dic['file'] = doc.name
            passage_dic['page_nbr'] = passage['page_nbr']
            passage_dic['language'] = passage['language']
            passage_dic['header1'] = header1
            passage_dic['header2'] = header2
            passage_dic['paragraph'] = passage_text
            
            final_dic.append(passage_dic)
                            
        return pd.DataFrame(final_dic)
    
    def _check_header_conditions(self, passage_dic, header_dic):
        """
        Method to check if passages match with the identified header properties.

        Parameters
        ----------
        passage_dic : dict
            Dictionary containing information about a single passage from a given document.
        header_dic : dict
            Dictionary containing information about the identified header properties in the given document.
            
        Returns
        -------
        bool
            Returns either True or False based on if the attributes completely match or not.
        """
        if passage_dic['font'] != header_dic['font']:
            return False
        
        if passage_dic['size'] != header_dic['size']:
            return False
        
        if passage_dic['flags'] != header_dic['flags']:
            return False
    
        if passage_dic['uppercase'] != header_dic['uppercase']:
            return False
        
        return True
    
    def _get_relevant_pages(self, doc, cutoff):
        """
        Method to identify all relevant pages in a given pdf document.

        Parameters
        ----------
        doc : fitz.Document
            Fitz Document
        cutoff : int
            Integer defining the cutoff for the amount of chars on a single page for what is a relevant page.
            
        Returns
        -------
        relevant_pages : list[fitz.Pages]
            List of identified relevant pages.
        """
        relevant_pages = []
        
        for page in doc.pages():
            text = page.get_text()

            # Probably ToC
            if text.count('.') > 500 or sum(map(str.isdigit, text)) > 200:
                continue
            
            if len(text) > cutoff:
                relevant_pages.append(page)
                    
        return relevant_pages
    
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
