import operator
from functools import reduce
from sklearn.externals import joblib
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", type = str)
parser.add_argument("--output", type = str)
parse = parser.parse_args()


def add_border_and_pos(sent):
    
    import jieba.posseg as pseg

    border = ""
    sent_postag = []
    seg_list = pseg.cut("".join(sent), HMM = False)
    for token, pos in seg_list:
        # print(token)
        
        postag = [pos] * len(token)
        # print(postag)
        sent_postag.append(postag)
        if len(token) == 1:
            border += "W"
            continue
        for i in range(len(token)):
            if i == 0:
                border += "B"
            elif i == len(token) - 1:
                border += "E"
            else:
                border += "M" 

    sent_postag = reduce(operator.add, sent_postag)

    assert len(sent) == len(border) == len(sent_postag)
    return border, sent_postag
    
#### 全角转半角
def setQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif inside_code >= 65280 and inside_code <= 65374:
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring

table = {ord(f):ord(t) for f,t in zip(
    u'，。！？【】（）％＃＠＆、‘’“”',
    u',.!?[]()%#@&\\\'\'""')}

def body(word):
    if word in ["耳","鼻","喉","眼","嘴","咽","手","脚","肚","胃","股","腰",\
               "腿", "背", "巴", "脸", "心", "肝", "脾", "肾"]:
        return True
    else:
        return False
    
def is_punc(word):
    if word in ',<>?/;:\'"[]{}+=()~`!@#$%^&*\\':
        return True
    return False


    
def word2features(sent,i):
    word = sent[i][0]
    border = sent[i][1]
    pos = sent[i][2]
    
    
    features = {
        "word": word,
        "word.isdigit()": word.isdigit(),
        "word.body()": body(word),
        "word.pos()": pos,
        "word.border()": border,
        "word.punc()": is_punc(word),
        "word.alpha()":  'a' <= word <= 'z' or "A" <= word <= 'Z'
    }
            
    
    if i > 0:
        features["BOS"] = False

    else:
        features["BOS"] = True

    if i < len(sent) - 1:
        features["EOS"] = False

    else:
        features["EOS"] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token,border, pos, label in sent]



def sent2tokens(sent):
    return [token for token,  border, pos ,label in sent]


def write_file(originals, preds, fout = None, levels = None, scores = None, titleranks = None, newtitleranks = None):   
    lines = []
    line = []
    flag_body = False
    flag_sympton = False
    flag_disease = False
    
    for j, (sent, pred) in enumerate(zip(originals, preds)):
        
        line = []
        for i in range(len(pred)):
            token = sent[i][0]
            p = pred[i]
            if p == "O":
                if flag_sympton == True:
                    line.append("]")
                    line.append("{Symptom}")
                    flag_sympton = False
                elif flag_body == True:
                    line.append("]")
                    line.append("{Body}")
                    flag_body = False
                elif flag_disease == True:
                    line.append("]")
                    line.append("{Disease}")
                    flag_disease = False

                line.append(token)
            elif p == "B-Symptom":
                if flag_sympton == True:
                    line.append("]")
                    line.append("{Symptom}")
                    flag_sympton = False
                elif flag_body == True:
                    line.append("]")
                    line.append("{Body}")
                    flag_body = False
                elif flag_disease == True:
                    line.append("]")
                    line.append("{Disease}")
                    flag_disease = False
                line.append("[")
                line.append(token)
                flag_sympton = True

            elif p == "B-Body":
                if flag_sympton == True:
                    line.append("]")
                    line.append("{Symptom}")
                    flag_sympton = False
                elif flag_body == True:
                    line.append("]")
                    line.append("{Body}")
                    flag_body = False
                elif flag_disease == True:
                    line.append("]")
                    line.append("{Disease}")
                    flag_disease = False
                line.append("[")
                line.append(token)
                flag_body = True
            elif p == "B-Disease":
                if flag_sympton == True:
                    line.append("]")
                    line.append("{Symptom}")
                    flag_sympton = False
                elif flag_body == True:
                    line.append("]")
                    line.append("{Body}")
                    flag_body = False
                elif flag_disease == True:
                    line.append("]")
                    line.append("{Disease}")
                    flag_disease = False
                line.append("[")
                line.append(token)
                flag_disease = True
            else:
                line.append(token)
        if i == len(pred) - 1:
            if p == "I-Symptom" or p == "B-Symptom":
                line.append("]")
                line.append("{Symptom}")
                flag_sympton = False

            elif p == "I-Body" or p == "B-Body":
                line.append("]")
                line.append("{Body}")
                flag_body = False
            elif p == "I-Disease" or p == "B-Disease":
                line.append("]")
                line.append("{Disease}")
                flag_disease = False
        
        if fout is None:
            lines.append(("".join(line)))
            
        else:
            if scores is None:
                fout.write(("".join(line)) + "\n")
            else:
                fout.write("".join(line) + '\t' + str(levels[j]) + '\t' + str(scores[j]) + '\t' + str(titleranks[j]) + '\t'+ str(newtitleranks[j]) + '\n')
                
        
    return lines
            
            
def predict(sents, interactive = False):
    
    assert isinstance(sents, (list, tuple))
    if interactive is False:
        fo = open(parse.output, "w", encoding = "utf-8")
    crf = joblib.load("crf_suite_model.m")
    for query in sents:
        tmp_single_query = []
        tmp_queries = []
        query = setQ2B(query)
        query = query.translate(table)
        border, sent_postag = add_border_and_pos(query)
        for i in range(len(query)):
            tmp_single_query.append((query[i], border[i], sent_postag[i]))
        tmp_queries.append(tmp_single_query)

        query_data = [sent2features(s) for s in tmp_queries]
        query_pred = crf.predict(query_data)
        
        if interactive is False:
            write_file(tmp_queries, query_pred, fo)
        else:
            lines = write_file(tmp_queries, query_pred)
            for line in lines:
                print(line)
    if interactive is False:
        fo.close()
        

if __name__ == "__main__":
    sents = []
    if parse.input is not None and parse.output is not None:
        with open(parse.input, "r", encoding = "utf-8") as f:
            for line in f:
                try:
                    _, sent = line.strip().split()
                    sents.append(sent)
                except:
                    pass
        predict(sents, False)
    else:
        while True:
            print("Please input one sentence:")
            sent = input()
            if sent == "":
                break
            predict([sent], True)
    
    
