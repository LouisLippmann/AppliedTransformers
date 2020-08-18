import os
import torch
import transformers
from kb.model import KnowBertForPretraining
from senticnet.kb import SenticNet

# sample text
sample = "Der Kaffee war heiß und lecker."
# model
tokenizer = "bert-base-german-cased"
bert_base_model = "data/results/bert-base-german-cased-yelp-entropy"

# create model
config = transformers.BertConfig.from_pretrained(bert_base_model)
model = KnowBertForPretraining(config)
# add knowledge bases
kb = model.add_kb(10, SenticNet("data/senticnet/german")).kb
# load model parameters
model.load_state_dict(torch.load(os.path.join(bert_base_model, "pytorch_model.bin"), map_location='cpu'))
model.eval()

# create tokenizer
tokenizer = transformers.BertTokenizer.from_pretrained(tokenizer)

# tokenize sample
tokens = tokenizer.tokenize(sample)
input_ids = tokenizer.convert_tokens_to_ids(tokens)
input_ids = torch.LongTensor([input_ids])

# prepare and apply model
mention_candidates = model.prepare_kbs([tokens])[0]
linking_scores = model.forward(input_ids=input_ids)[-2]

for layer, (layer_scores, d) in enumerate(zip(linking_scores, mention_candidates)):
  
    if d is not None:

        for (term, candidate_ids), scores in zip(d, layer_scores[0]):

            candidate_mask = (candidate_ids != -1)
            candidate_ids, scores = candidate_ids[candidate_mask], torch.softmax(scores[candidate_mask], dim=0)
            
            print(-(scores * torch.log(scores)).sum())
            candidate_ids, scores = candidate_ids.tolist(), scores.tolist()

            print(term)

            for candidate_id, score in zip(candidate_ids, scores):
                candidate_term = kb.id2entity(candidate_id)
                print(candidate_term, score)

            print()
