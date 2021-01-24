import os, json
from .base import RelExDataset, RelExDatasetItem
from itertools import combinations

class SmartdataCorpus(RelExDataset):
    """ German Smartdata Corpus
        Download: https://github.com/DFKI-NLP/smartdata-corpus/tree/master/v2_20190802
    """

    TRAIN_FILE = "SmartdataCorpus/train.json"
    EVAL_FILE = "SmartdataCorpus/test.json"

    LABELS = ["Acquisition", "Insolvency", "Layoffs", "Merger", "OrganizationLeadership", "SpinOff", "Strike"]

    yield_train_items = lambda self: self.yield_items(
        os.path.join(self.data_base_dir, SmartdataCorpus.TRAIN_FILE))
    yield_eval_items = lambda self: self.yield_items(
        os.path.join(self.data_base_dir, SmartdataCorpus.EVAL_FILE))

    def yield_items(self, fpath:str):
        # read data
        with open(fpath, 'r', encoding='utf-8') as f:
            json_dumps = f.read().split('}\n{')
            json_dumps = [('' if i == 0 else '{') +  s + ('' if i == len(json_dumps) - 1 else '}') for i, s in enumerate(json_dumps)]
            documents = [json.loads(dump) for dump in json_dumps][1:]

        # process data
        for doc in documents:
            for sent in doc['sentences']['array']:
                # get sentence string
                begin, end = sent['span']['start'], sent['span']['end']
                sent_string = doc['text']['string'][begin:end]
                off = -begin

                for rel in sent['relationMentions']['array']:
                    rel_type = rel['name']

                    # check type
                    if rel_type not in SmartdataCorpus.LABELS:
                        continue
                    
                    types = ['organization-company', 'person', 'org-position', 'trigger', 'organization']
                    args = tuple(arg for arg in rel['args']['array'] if arg['conceptMention']['type'] in types)
                    # create bi-relations from n-ary relations
                    for argA, argB in combinations(args, 2):
                        # get entity spans
                        argA, argB = argA['conceptMention'], argB['conceptMention']
                        spanA = (argA['span']['start'] + off, argA['span']['end'] + off)
                        spanB = (argB['span']['start'] + off, argB['span']['end'] + off)
                        # yield dataset item
                        yield RelExDatasetItem(
                            sentence=sent_string,
                            source_entity_span=spanA,
                            target_entity_span=spanB,
                            relation_type=SmartdataCorpus.LABELS.index(rel_type)
                        )