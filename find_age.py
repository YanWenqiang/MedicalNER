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
    exp1 = r'(\d+|\w{1,3})?周*岁'
    exp2 = r'年龄*(\w{1,3})'
    res1 = re.findall(exp1, ss)
    res2 = re.findall(exp2, ss)
    # print("res1: ",res1)
    # print("res2: ", res2)
    ans = []
    if len(res1) > 0:
        for i in res1:
            if hasNumbers(i):
                if len(re.findall('\d+',i)) != 0:
                    ans.append(re.findall('\d+',i)[0])
            else:
                if len(re.findall('[零一两二三四五六七八九十百]', i)) != 0:
                    ans.append(i)
                
    elif len(res2) > 0:
        for i in res2:
            if len(re.findall('\d', i)) != 0:
                f = 1
                for c in i:
                    if c not in "0123456789":
                        f = 0
                        break 
                if f:
                    ans.append(i)
            elif len(re.findall('[零一两二三四五六七八九十百]', i)) != 0:
                ans.append(i)
    else: # 婴儿案例
        if ss.find("个月") != -1 and (ss.find("宝宝") != -1 or ss.find("婴儿") != -1):
            idx = ss.find("个月")
            tmp = ss[max(0,idx - 3): idx]
            f = 0
            for i, c  in enumerate(tmp[::-1]):
                if c not in "0123456789零一两二三四五六七八九十百":
                    break 
                if c in "0123456789零一两二三四五六七八九十百":
                    f = 1
            if f == 1:
                ans.append(tmp[-i:])
        
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

def convert2num(ss):
    mapping = {
        "零":0,
        "一":1,
        "二":2,
        "三":3,
        "四":4,
        "五":5,
        "六":6,
        "七":7,
        "八":8,
        "九":9,
        "十":10,
        # "百":100,
    }
    if len(ss) == 1:
        return mapping[ss]
    elif len(ss) == 2:
        if ss[0] == "十": # 十二
            return 10 + mapping[ss[1]]
        elif ss[1] == "十": # 二十
            return 10 * mapping[ss[1]]
        elif ss[1] == "百": # 一百
            return 100 * mapping[ss[0]]
        else: # 一二，不正常的表达
            return mapping[ss[0]] * 10 + mapping[ss[1]]
    elif len(ss) == 3: 
        if ss[1] == "十":# 一十五，二十六
            return mapping[ss[0]] * 10 + mapping[ss[-1]]
        elif ss[1] == "百": # 一百二
            return mapping[ss[0]] * 100 + mapping[ss[-1]] * 10
        else: # 一二三, 不正常的表达
            try:
                mapping[ss[0]] * 100 + mapping[ss[1]] * 10 + mapping[ss[2]] 
            except:
                # print(ss)
                pass
    else: # len(ss) = 4 or len(ss) = 5
        bai = mapping[ss[:2][0]] * 100
        rest = ss[2:]
        num = bai
        if rest[0] == "零":
            num += mapping[rest[-1]]
        else:
            num += mapping[rest[0]] * 10
            if rest[-1] != "十":
                num += mapping[rest[-1]]
        return num



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
                # print(age_d, s)
                start = 0
                while not age_d[start].isdigit(): 
                    start += 1
                end = len(age_d)
                while not age_d[end - 1].isdigit():
                    end -= 1
                new_age = age_d[start:end]
                end = len(new_age)
                # new_age = convert2han(age_d)
                # s = s.replace(age_d, new_age)
                # end = len(new_age)
                
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
                new_age = convert2num(new_age)
                new_age = str(new_age)
                s = s.replace(age, new_age)
                end = len(new_age)
            # s = s.replace(age, new_age)
                
            if new_age + "个月" in s: # 处理不满一岁或者一岁左右婴儿的情况,全部将婴儿换成1岁
                s = s.replace(new_age, "1")
                new_age = "1"
                s = s.replace("个月", "岁")
        
            begin = s.find(new_age)
            end = len(new_age)
            

            if interactive is False:
                write_file(s, new_age, begin, end + begin, fo)
            else:
                write_file(s, new_age, begin, begin + end, None)
        
        
    if interactive is False:
        fo.close()


if __name__ == "__main__":
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
