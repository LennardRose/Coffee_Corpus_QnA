from sentence_transformers import SentenceTransformer, util
from datasets import load_dataset
from sentence_transformers import InputExample
from torch.utils.data import DataLoader
from sentence_transformers import losses
import pandas as pd


def embedder(model_id,data_files):
    model = SentenceTransformer(model_id)
    dataset = load_dataset("json", data_files)
    train_examples = []
    train_data = dataset['train']['set'] #
    n_examples = dataset['train'].num_rows  #['train']

    for i in range(n_examples):
        example = train_data[i]
        train_examples.append(InputExample(texts=[example[0], example[1]]))

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
    train_loss = losses.MultipleNegativesRankingLoss(model=model)
    num_epochs = 4
    warmup_steps = int(len(train_dataloader) * num_epochs * 0.1) #10% of train data

    model.fit(train_objectives=[(train_dataloader, train_loss)],
          epochs=num_epochs,
          #optimizer_params={'lr': 3e-5},
          warmup_steps=warmup_steps) 

    return model

def main():
    model_id = 'sentence-transformers/all-MiniLM-L6-v2'
    data_files = './train_data.json'
    embedder = embedder(model_id, data_files)

if __name__ == "__main__":
    main()

