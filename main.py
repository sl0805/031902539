'''
Author: your name
Date: 2021-09-11 09:56:10
LastEditTime: 2021-09-13 21:40:58
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \python\softwareE\main.py
'''
'''目前仅实现中文最基础的检测'''


def readorg(filename):
    # 按行读取待检测文本，并去除行首行末的空格及回车，将非空行加入列表
    org = open(filename, encoding="utf-8")
    lines = list()
    for line in org.readlines():
        lines.append(line.strip())
    org.close()
    return lines


def write_ans(filename, context):
    # 每次检测到就把内容添加进文件
    ans = open(filename, 'a')
    ans.write(context)


class DFA(object):
    # 建立词库，为字典
    def __init__(self, word_library):
        self.root = dict()
        self.skip = [' ', '!', '@', '#', '$', '%', '^', '&',
                          '*', '(', ')', '_', '-', '+', '[', ']',
                          '{', '}', '\\', '|', '+', '=', '`', '~',
                          ',', '.', '<', '>', '?', '/', ':', ';']
        for word in word_library:
            self.add_word(word)

    def add_word(self, word):
        # 忘词库中添加词
        now_dict = self.root
        word_length = len(word)
        for i in range(word_length):
            word_key = word[i]
            if word_key in now_dict.keys():
                now_dict = now_dict.get(word[i])
                # 若为这个词的最后一个字，则定义为true
                now_dict['is_end'] = False
            else:
                # 若找不到以该词首字为key值的，则另外建一个字典
                new_dict = dict()
                if i == word_length-1:
                    new_dict['is_end'] = True
                else:
                    new_dict['is_end'] = False
                # 把新的字典嵌套进大字典中
                now_dict[word_key] = new_dict
                now_dict = new_dict

    def check_match(self, txt, begin_index):
        # 检查是否包含敏感词
        flag = False
        now_map = self.root
        matched_length = 0
        ori_word = ''
        for i in range(begin_index, len(txt)):
            word = txt[i]
            if word in self.skip and matched_length > 0:
                matched_length += 1
                continue
            now_map = now_map.get(word)
            if now_map:
                matched_length += 1
                if now_map.get("is_end"):
                    flag = True
                ori_word += word
            else:
                break
        if matched_length < 2 or not flag:
            matched_length = 0
        ret = dict()
        ret['matched_length'] = matched_length
        ret['ori_word'] = ori_word
        return ret

    def get_match(self, txt):
        # 得到匹配出来的含敏感词的部分，返回该部分以及对应敏感词
        matched_word_list = list()
        for i in range(len(txt)):
            check_dict = self.check_match(txt, i)
            length = check_dict['matched_length']
            if length > 0:
                word = txt[i:i+length]
                matched_word_list.append(word)
                ori_word = check_dict['ori_word']
                matched_word_list.append(ori_word)
        return matched_word_list


# 三个文件路径输入
words_txt = input()
org_txt = input()
result_txt = input()
# 读取敏感词汇
# words_base = readorg('C:\\Users\\1\\Desktop\\words.txt')
words_base = readorg(words_txt)
# 创建类实例
dfa = DFA(word_library=words_base)
# 读取待检测文件
# org = readorg('C:\\Users\\1\\Desktop\\org1.txt')
org = readorg(org_txt)
# 检测结果字符串
result = ''
for i in range(0, len(org)):
    res = dfa.get_match(org[i])
    # 一行里面可能包含多个敏感词汇
    for j in range(1, len(res), 2):
        s = 'Line'+str(i+1)+':<'+res[j]+'>'+res[j-1]+'\n'
        result += s
write_ans(result_txt, result)
