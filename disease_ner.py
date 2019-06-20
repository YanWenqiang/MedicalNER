import os
import numpy as np
import anago
import re
import sys
import time
import logging
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", type = str)
parser.add_argument("--output", type = str)
parse = parser.parse_args()
#NER model file name
MODEL_FILE = './model/ner_20190520'

#load NER model
NER_MODEL = anago.Sequence.load(MODEL_FILE+'.weights.h5',MODEL_FILE+'.params.json',MODEL_FILE+'.preprocessor.pickle')

#punctuation Rex
PUNC = r'[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）；：]'

def predict(query):
    """ NER for a query
        Args:
            query : string, short query without punctuation
        Returns:
            disease_list: list of disease
            symptom_list: list of symptom
    """
    query = ' '.join(list(query))
    result = NER_MODEL.analyze(query)
    return result

def write_file(sent, symptom = None, fo = None):
    if len(symptom) != 0:
        sent = sent + "\t" + symptom[0]
    if fo is not None:
        fo.write(sent + "\n")
    else:    
        print(sent)

def get_disease_list(sents, interactive = False):
    """ Get all diseases and symptoms in document.
        Args:
            doc : Chinese string
        Returns:
            disease_list: list of disease
            symptom_list: list of symptom
    """
    assert isinstance(sents, list)
    fo = None
    if interactive is False:
        fo = open(parse.output, "w", encoding = "utf-8")
    for doc in sents:
        query_list = [x.strip() for x in re.split(PUNC, doc)]
        #query_list = [doc]
        disease_list = []
        symptom_list = []
        for query in query_list:
            if not query or query == '':
                continue
            tmp_res = predict(query)
            tmp_entities = tmp_res['entities']
            if len(tmp_entities) > 0:
                tmp_diseases = [x['text'] for x in tmp_entities if x['type'] == 'DISEASE']
                tmp_symptoms = [x['text'] for x in tmp_entities if x['type'] == 'SYMPTOM']
                disease_list.extend(tmp_diseases)
                symptom_list.extend(tmp_symptoms)

            
        write_file(doc, symptom_list, fo)
            

    if interactive is False:
        fo.close()

if __name__ == '__main__':
    doc = '由于眼部神经较为丰富，任何刺激神经的因素均可导致眼睛疼痛的发生。\
            因此，眼睛疼痛的原因较多，根据其疼痛类型可分为以下几方面：\
            1、持续性胀痛：青光眼、眼内肿物、眼肌肿胀、视疲劳，其中视疲劳又因配戴眼镜不适或长期用眼导致；\
            2、刺痛：眼内异物、角膜神经暴露、维生素缺乏、干眼症、泪膜功能异常；3、其他：炎症、外伤、手术等。'
    '''
    usage: get_disease_list(doc)
    '''
    
    sents = []
    if parse.input is not None and parse.output is not None:
        with open(parse.input, "r", encoding = "utf-8") as f:
            for line in f:
                try: 
                    _, sent = line.strip().split("\t")
                    sents.append(sent)
                except:
                    pass 
        get_disease_list(sents, False)
    else:
        while True:
            print("Please input one sentence:")
            sent = input()
            if sent == "":
                break
            get_disease_list([sent], True)
            

