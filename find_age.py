import re 
import os 
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", type = str)
parser.add_argument("--output", type = str)
parse = parser.parse_args()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def find_age(ss):
    exp1 = r'(\d+|\w{1,3})?岁'
    exp2 = r'年龄*(\w{1,3})'
    res1 = re.findall(exp1, ss)
    res2 = re.findall(exp2, ss)
    ans = []
    if len(res1) > 0:
        for i in res1:
            if hasNumbers(i):
                ans.append(re.findall('\d+',i)[0])
            else:
                if len(re.findall('[一两二三四五六七八九十百]', i)) != 0:
                    ans.append(i)
                
    elif len(res2) > 0:
        for i in res2:
            if len(re.findall('\d', i)) != 0:
                
                ans.append(i)
            elif len(re.findall('[零一两二三四五六七八九十百]', i)) != 0:
                ans.append(i)
    else: # 婴儿案例
        if ss.find("个月") != -1 and (ss.find("宝宝") != -1 or ss.find("婴儿") != -1):
            idx = ss.find("个月")
            tmp = ss[max(0,idx - 3): idx]
            ans.append(tmp)
        
    return ans

def convert2han(ss):
    mapping = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
    n = len(ss)
    ans = ""
    if n == 1:
        ans = mapping[ss[0]]
    elif n == 2:
        ans += mapping[ss[0]] + "十" 
        if ss[1] != "0":
            ans += mapping[ss[1]]
    else:
        ans += mapping[ss[0]] + "百" 
        if ss[1] != "0":
            ans += mapping[ss[1]] + "十" 
            if ss[2] != "0":
                ans += mapping[ss[2]]
        else:
            if ss[2] != "0":
                ans += "零" + mapping[ss[2]]
            
    return ans

def write_file(sent, age = None, start = None, end = None, fo = None):
    if age is not None:
        entity = "]{Age}"
        sent = sent[:end] + entity + sent[end:]
        sent = sent[:start] + "[" + sent[start:]
    if fo is not None:
        fo.write(sent + "\n") 
    else:
        print(sent)
    


def predict(sents, interactive = False):
    assert isinstance(sents, list)
    if interactive is False:
        fo = open(parse.output, "w", encoding = "utf-8")
    for s in sents:
        age = find_age(s)
        if len(age) == 0: # 样例中没有年龄实体
            if interactive is False:
                write_file(s, age = None, fo = fo)
            else:
                write_file(s, age = None, fo = None)
        else: # 样例中出现年龄
            age = age[0]
            begin = s.find(age)
            end = len(age)
            if hasNumbers(age):# 年龄以数字的形式出现
                age_d = age
                start = 0
                while not age_d[start].isdigit(): 
                    start += 1
                end = len(age_d)
                while not age_d[end - 1].isdigit():
                    end -= 1
                age_d = age_d[start:end]
                new_age = convert2han(age_d)
                s = s.replace(age_d, new_age)
                end = len(new_age)
                
            else: # 年龄以汉字的形式出现
                age_d = age
                
                start = 0
                while  age_d[start] not in "零一两二三四五六七八九十百": 
                    
                    start += 1
                end = len(age_d)
                while  age_d[end - 1] not in "零一两二三四五六七八九十百" :
                    end -= 1
                age = age_d[start:end]
                new_age = age.replace("两", "二")
            s = s.replace(age, new_age)
                
            if new_age + "个月" in s: # 处理不满一岁或者一岁左右婴儿的情况
                s = s.replace(new_age, "一")
                new_age = "一"
                s = s.replace("个月", "岁")
        
            begin = s.find(new_age)
            end = len(new_age)
            print(s, begin,end, new_age)    

            if interactive is False:
                write_file(s, new_age, begin, end + begin, fo)
            else:
                write_file(s, new_age, begin, begin + end, None)
        
        
    if interactive is False:
        fo.close()


if __name__ == "__main__":
    # s11 = "我儿子今年快28岁，身高175公分"
    # s12 = "我儿子今年三十五，身高175公分"
    # # s13 = "身高175， 我儿子快28了" bad case
    # s13 = "我儿子年龄二十八，身高一七五"
    # s14 = "我儿子今年28岁，身高175公分"
    # s15 = "我儿子今年二十八岁，身高175公分"
    # s16 = "我儿子二十八岁，身高175公分"
    # s17 = "三个月的宝宝吃什么好"
    # sents = [s11, s12 ,s13, s14, s15, s16, s17]

    sents = []
    if parse.input is not None and parse.output is not None:
        with open(parse.input, "r", encoding = "utf-8") as f:
            for line in f:
                sents.append(line.strip())
        predict(sents, False)
    else:
        while True:
            print("Please input one sentence:")
            sent = input()
            if sent == "":
                break
            predict([sent], True)
