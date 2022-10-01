import layoutparser as lp
import time
import pandas as pd
import os
import sys
import glob
from loguru import logger
from segmentation import Segmenter


class Preprocessor:
    def __init__(self, mode=0, output_path=None, model_path=None, verbose="ERROR"):
        """
        Preprocessor for the coffee manufacturer manuals.

        Parameters
        ----------
        mode : int
            The mode of the preprocessor. 0 for character attribute model, 1 for visual detection model.            
        output_path : Path | str
            Path for where the outputted csv-file should be saved. If not provided a pandas DataFrame will be returned.
        model_path : Path | str
            Path for where the trained model lies.
        verbose : str
            Based on value more logging details will get outputted.
        """
        self._mode = mode
        self._output_path = output_path
        self._model = self._load_model(model_path)
        self._setup_logger(verbose)
        logger.info(f"Instantiated Preprocessor with specified model in path {'/' + model_path}")

    def _setup_logger(self, verbose):
        logger.remove()
        # logger.add("logs/logfile.log", level=verbose, rotation="100 MB")
        logger.add(sys.stdout, level=verbose)

    def _load_model(self, model_path):
        
        if self.mode == 0:
            # Load Character Attribute Model
            model = None
            
        if self.mode == 1:
            # Load Visual Detection Model
            model = lp.Detectron2LayoutModel(
                config_path = self.model_path + "/config.yaml",
                model_path = self.model_path + "/model_5_manufacturers.pth",
                label_map = {0: "Figure", 1: "Header", 2: "Subheader", 3: "Table", 4: "Text", 5: "ToC"},
                extra_config = ["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6] # <-- Only output high accuracy preds
            )

        # Maybe needs changes in the future if more models are added for specific manufacturers
        # model = lp.Detectron2LayoutModel(
        #     config_path = "/content/drive/MyDrive/vdu/model/config_single.yaml",
        #     model_path = "/content/drive/MyDrive/vdu/model/model_delonghi.pth",
        #     label_map = {0: "Header", 1: "Subheader", 2: "Table", 3: "ToC"},
        #     extra_config = ["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5] # <-- Only output high accuracy preds
        # )

        return model
      
    def process(self, manuals_path):
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
        time_start_all = time.time()
        
        corpus = []

        # First Loop through all Manufacturers
        for manufacturer in next(os.walk(manuals_path))[1]:
            manufacturer_dic = {}
            manufacturer_products = []

            subfolder = os.path.join(manuals_path, manufacturer)
            os.makedirs(os.path.join(self._output_path, manufacturer), exist_ok=True)

            # Second Loop through all Products of Manufacturer
            for product in next(os.walk(subfolder))[1]:
                product_dic = {}
                subsubfolder = os.path.join(subfolder, product)
                out_subsubfolder = os.path.join(self._output_path+manufacturer, product)
                os.makedirs(out_subsubfolder, exist_ok=True)

                df_list = []
                pdfs = glob.glob(subsubfolder + "/*.pdf")

                if not len(pdfs):
                    logger.error(f"No PDFs found in the file path. Skipping - {subsubfolder} -")
                    continue

                # Third Loop through all Manuals of Products
                for file in pdfs:
                    time_start_single = time.time()
                    logger.info(f"Processing {file}.")

                    segmenter = Segmenter(file, self._model)
                    file_df = segmenter.get_segments_df(self._mode)

                    file_df = self._filter(file_df)
                    file_df = self._correct_points(file_df)

                    df_list.append(file_df)
                    time_finish_single = time.time()
                    logger.info(f"Finished processing {file}. - Took {time_finish_single-time_start_single} seconds.")

                df = pd.concat(df_list, ignore_index=True)
                df = df[['file', 'language', 'label', 'text']]

                product_object = self._object_from_df(df)
                product_dic['product_id'] = product
                product_dic['languages'] = product_object
                manufacturer_products.append(product_dic)

                out_csv = out_subsubfolder + f"/{product}_preprocessed.csv"
                df.to_csv(out_csv)
                logger.info(f"Saving the output dataframe to {out_csv}")

            manufacturer_dic['manufacturer'] = manufacturer
            manufacturer_dic['products'] = manufacturer_products
            corpus.append(manufacturer_dic)

        time_finish_all = time.time()
        logger.info(f"Finished processing {len(df_list)} documents. - Took {time_finish_all-time_start_all} seconds.")

        return corpus

    def _object_from_df(self, df):
      language_dic = {}
      
      for language in df['language'].unique():
          language_df = df[df['language'] == language]

          
          language_list = []

          header_id_count = 1
          subheader_id_count = 1

          subheader_dic = {}

          for row in language_df.itertuples():
              language = row.language
              label = row.label
              text = row.text

              header_dic = None

              if "Header" in label:
                  header_dic = {
                      "headerId": header_id_count,
                      "headerText": text
                  }

                  if header_id_count > 1:
                      header_dic['children'] = header_children
                      language_list.append(header_dic)

                  header_children = []
                  header_id_count += 1
                  subheader_id_count = 1


              if "Subheader" in label:
                  subheader_dic = {
                      "subHeaderId": subheader_id_count,
                      "subHeaderText": text
                  }

                  subheader_id_count += 1

                  # current_subheader = text

              if label == 'Paragraph':
                  if subheader_dic:
                      subheader_dic['paragraphText'] = text
                      header_children.append(subheader_dic)
                  
                  else:
                      if header_dic is not None:
                          header_dic['paragraphText'] = text   

          language_dic[language] = language_list

      return language_dic

    def _filter(self, df):
        """
        Method for filtering certain unnecessary Paragraphs.

        Parameters
        ----------
        df : pandas.DataFrame
            Preprocessed Pandas DataFrame.
        
        Returns
        -------
        pandas.DataFrame
            Filtered Pandas DataFrame.
        """
        df = df.drop(df[df.text.str.len() <= 4].index)

        return df

    def _correct_points(self, df):
        df['text'] = df['text'].str.replace('�','.')

        return df