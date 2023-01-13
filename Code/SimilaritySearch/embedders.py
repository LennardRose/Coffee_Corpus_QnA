import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import tensorflow_text as text

class EmbedderBase(object):
    def format_text(self, plain_text):
        """
        Modify this function when formatting input of other embedders.
        """
        pass

    def embed_single_text(self, single_text):
        pass

    def embed_list_text(self, list_text):
        pass

class SwivelEmbedder(EmbedderBase):
    def __init__(self, model_link="https://tfhub.dev/tensorflow/cord-19/swivel-128d/3"):
        self.embedder = hub.KerasLayer(model_link)
        print(f"Loaded pre-trained model {model_link} successfully!")

    def embed_single_text(self, plain_text):
        formated_text = tf.constant([plain_text])
        return np.array(self.embedder(formated_text))

    def embed_list_text(self, list_text):
        return np.array(self.embedder(tf.constant(list_text)))

class BertEmbedder(EmbedderBase):
    def __init__(self, bert_link="https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-128_A-2/1",
                 preprocessor_link="https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/1",
                 sequence_length=128):
        self.preprocessor = hub.load(preprocessor_link)
        self.embedder = hub.KerasLayer(bert_link, trainable=False)
        self.sequence_length = sequence_length
        print(f"Loaded pre-trained model {bert_link} successfully!")

    def embed_single_text(self, plain_text):
        text = tf.constant([plain_text])
        tokenized_text = self.preprocessor.tokenize(text)
        encoder_input = self.preprocessor.bert_pack_inputs(
            [tokenized_text], seq_length=self.sequence_length) # ['input_mask', 'input_type_ids', 'input_word_ids']

        outputs = self.embedder(encoder_input)
        return np.array(outputs["pooled_output"]) # Embedding of the whole sentence, shape [1, 768]

    def embed_list_text(self, list_text):
        text = tf.constant(list_text)
        tokenized_text = self.preprocessor.tokenize(text)
        encoder_input = self.preprocessor.bert_pack_inputs(
            [tokenized_text], seq_length=self.sequence_length)  # ['input_mask', 'input_type_ids', 'input_word_ids']

        outputs = self.embedder(encoder_input)
        return np.array(outputs["pooled_output"])  # Embedding of the whole sentence, shape [1, 768]