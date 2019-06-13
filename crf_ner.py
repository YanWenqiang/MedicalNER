from itertools import chain
from sklearn.externals import joblib
import random
import json
import sklearn
import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics


punc = '[,<>?/;:\'"\[\]{}+=()~`!@#$%^&*\\. ]'


data = open("example_only_body_and_diease.data", encoding = "utf-8")
lines = data.readlines()
sents = []
sent = []
flag = False
for line in lines:
    if len(line.strip()) == 0:
        if flag:
            sents.append(sent)
        sent = []
        flag = False

    else:
        word, border, pos, label = line.strip().split("\t")
            
        if "Body" in label or "Disease" in label:
            flag = True
        sent.append((word, border, pos, label))
    

print(len(sents))
num = len(sents)
train_sents = sents[:int(num * 0.7)]
test_sents = sents[int(num * 0.7) : ]

new_train_sents = []
for sent in train_sents:
    for elem in sent:
        if elem[3] != "O":
            new_train_sents.append(sent)
            break
print(len(train_sents))
print(len(new_train_sents))

# train_sents_tokens = []
# test_sents_tokens = []

# def extract_sents_char_level(sents):
#     sents_tokens = []

#     for sent in sents:
#         tokens = []
#         for token, border, pos, label in sent:
#             tokens.append(token)
#         sents_tokens.append(" ".join(tokens))
        
#     return sents_tokens



# train_sents_tokens = extract_sents_char_level(train_sents)
# test_sents_tokens = extract_sents_char_level(test_sents)


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
    # return [label if "Symptom" not in label else "O" for token,border, pos, label in sent]
    return [label for token,border, pos, label in sent]



def sent2tokens(sent):
    return [token for token,  border, pos ,label in sent]


X_train = [sent2features(s) for s in new_train_sents]
y_train = [sent2labels(s) for s in new_train_sents]


X_test = [sent2features(s) for s in test_sents]
y_test = [sent2labels(s) for s in test_sents]

crf = sklearn_crfsuite.CRF(
    algorithm = "lbfgs",
    c1 = 0.001,
    c2 = 0.001,
    max_iterations = 150,
    all_possible_transitions= True
)
crf.fit(X_train, y_train)

labels = list(crf.classes_)
labels.remove('O')
y_pred = crf.predict(X_test)
f1 = metrics.flat_f1_score(y_test, y_pred, 
                      average='weighted', labels=labels)
print("f1: ", f1)

entity = 0
correct_entity = 0
for y_pred_sent, y_test_sent in zip(y_pred, y_test):
    for y_pred_sent_token, y_test_sent_token in zip(y_pred_sent, y_test_sent):
        if y_test_sent_token != "O":
            entity += 1
            if y_pred_sent_token == y_test_sent_token:
                correct_entity += 1
acc = float(correct_entity) / entity
print("entity-level accuracy: ", acc)

all_sent = 0
correct_sent = 0
for y_pred_sent, y_test_sent in zip(y_pred, y_test):
    all_sent += 1
    is_correct = False
    for y_pred_sent_token, y_test_sent_token in zip(y_pred_sent, y_test_sent):
        if y_pred_sent_token != y_test_sent_token:
            break
        is_correct = True
    if is_correct == True:
        correct_sent += 1
acc = float(correct_sent) / all_sent
print("sentence-level accuracy: ", acc)

sorted_labels = sorted(
    labels, 
    key=lambda name: (name[1:], name[0])
)
print(metrics.flat_classification_report(
    y_test, y_pred, labels=sorted_labels, digits=3
))

joblib.dump(crf, "crf_suite_model.m")