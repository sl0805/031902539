'''
Author: your name
Date: 2021-09-11 09:56:10
LastEditTime: 2021-10-08 19:16:00
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \python\softwareE\main.py
'''
'''目前实现中文基础检测、中文拼音替换、中文首字母替换、英文不分大小写'''
'''只能在少量文本检测的情况下完成谐音字检测，文本数据一大就耗时很长，故删掉了'''




import sys
from xpinyin import Pinyin
import itertools
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
    with open(filename, 'w', encoding='utf-8') as fileobject:
        fileobject.write(context)
    fileobject.close()


class DFA(object):
    # 建立词库，为字典
    def __init__(self, word_library):
        # 敏感词库入口
        self.root = dict()
        # 用于把汉字用拼音替代后找原汉字敏感词
        self.same_dict = dict()
        # 汉字和英文情况下可跳过的符号交集
        self.skip = [' ', '!', '@', '#', '$', '%', '^', '&',
                          '*', '(', ')', '_', '-', '+', '[', ']',
                          '{', '}', '\\', '|', '+', '=', '`', '~',
                          ',', '.', '<', '>', '?', '/', ':', ';']
        # 把所有读入的词变成小写，这样添加进词库后就不存在小写的词了
        word_library = self.get_pinyin(word_library)
        for word in word_library:
            self.add_word(word)

    def add_word(self, word):
        # 往词库中添加单个词
        now_dict = self.root
        word_length = len(word)
        for i in range(word_length):
            word_key = word[i]
            if word_key in now_dict.keys():
                # 在当前字典下找得到相应的key值
                now_dict = now_dict.get(word[i])
                # 判断是否为该词的最后一个字
                if i == word_length-1:
                    now_dict['is_end'] = True
                    continue
                else:
                    now_dict['is_end'] = False
            else:
                # 若找不到以该词首字为key值的，则另外建一个字典
                new_dict = dict()
                if i == word_length-1:
                    new_dict['is_end'] = True
                else:
                    new_dict['is_end'] = False
                now_dict[word_key] = new_dict
                # 把新的字典嵌套进大字典中
                now_dict = new_dict

    def check_match(self, txt, begin_index):
        # 检查是否包含敏感词
        flag = False
        # 敏感词库入口
        now_map = self.root
        # 匹配文本长度
        matched_length = 0
        # 原敏感词
        ori_word = ''
        # 可跳过字符
        skip = self.skip
        for i in range(begin_index, len(txt)):
            # word为当前字符
            word = txt[i]
            if word in skip:
                # 如果word为可跳过字符，且之前已有可匹配文本，则可匹配长度+1，否则跳过
                if matched_length > 0:
                    matched_length += 1
                continue
            judge = ord(word.lower())
            if judge in range(97, 123):
                # 字母所对应的可跳过字符比汉字多了一类：数字
                skip = self.skip+['0', '1', '2', '3',
                                  '4', '5', '6', '7', '8', '9']
                # 判断是否为字母，若是，则不区分大小写，统一转成小写
                word = word.lower()
            else:
                skip = self.skip
            now_map = now_map.get(word)
            if now_map:
                # 找得到对应key值
                matched_length += 1
                if now_map.get("is_end"):
                    # 找到一个匹配文本了
                    flag = True
                ori_word += word
            else:
                break
        if matched_length < 2 or not flag:
            # 到了行末对应敏感词还没结束或者是找不到对应的敏感词，即无匹配文本
            matched_length = 0
        ret = dict()
        ret['matched_length'] = matched_length
        ret['ori_word'] = ori_word
        return ret

    def get_match(self, txt):
        # 得到匹配出来的含敏感词的部分，返回该部分以及对应敏感词
        matched_word_list = list()
        for i in range(len(txt)):
            # 得到匹配文本的长度以及原敏感词
            check_dict = self.check_match(txt, i)
            # 匹配文本长度
            length = check_dict['matched_length']
            if length > 0:
                # word为匹配文本
                word = txt[i:i+length]
                matched_word_list.append(word)
                ori_word = check_dict['ori_word']
                if ori_word in self.same_dict.keys():
                    ori_word = self.same_dict[ori_word]
                matched_word_list.append(ori_word)
        # 偶数下标存匹配文本，奇数下标存敏感词
        return matched_word_list

    def get_pinyin(self, word_base):
        # 把汉字对应的拼音也加进敏感词字典中
        # base现在为原词库的小写状态
        base = []
        base = base+[x.lower() for x in word_base]
        length = len(base)
        for word in range(0, length):
            # 循环遍历word_base中的每一个小写词，word为下标
            self.same_dict[base[word]] = word_base[word]
            judge = ord(base[word][0])
            # 判断该首字母是否为汉字，若不是，则不进行拼音转换，继续循环下一个敏感词
            if judge in range(97, 123):
                continue
            p = Pinyin()
            str_pinyin = p.get_pinyin(base[word])
            # 把拼音字符串转成拼音数组
            pinyin_list = str_pinyin.split('-')
            # 以下对一个敏感词进行组合，即把哪几个汉字变成拼音
            order_list = [k for k in range(0, len(base[word]))]
            for i in range(1, len(base[word])+1):
                # i是指要替换多少个汉字为拼音
                for j in itertools.combinations(order_list, i):
                    # j是指组合结果中的元组，循环遍历每一元组
                    str_txt = base[word]
                    str_txt_initial = base[word]
                    # 循环遍历得到的每个组合的元组
                    for k in range(0, i):
                        # 将汉字替换成拼音，比如：邪教--xie教--邪jiao--xiejiao
                        str_txt = str_txt.replace(
                            base[word][j[k]], pinyin_list[j[k]])
                        str_txt_initial = str_txt_initial.replace(
                            base[word][j[k]], pinyin_list[j[k]][0])
                    # 一个元组遍历结束
                    # 拼音替换
                    base.append(str_txt)
                    # 首字母替换
                    base.append(str_txt_initial)
                    self.same_dict[str_txt] = word_base[word]
                    self.same_dict[str_txt_initial] = word_base[word]
            # 添加这个进词典是用于谐音字检测
            base.append(pinyin_list)
        # print(base)
        return base


# 命令行输入内容
command_in = sys.argv
# 三个文件路径
words_txt = command_in[1]
org_txt = command_in[2]
result_txt = command_in[3]
words_base = readorg(words_txt)
# 创建类实例
dfa = DFA(word_library=words_base)
org = readorg(org_txt)
# 检测结果字符串
result = ''
total = 0
for i in range(0, len(org)):
    res = dfa.get_match(org[i])
    # 一行里面可能包含多个敏感词汇
    for j in range(1, len(res), 2):
        s = 'Line'+str(i+1)+': <'+res[j]+'> '+res[j-1]+'\n'
        total += 1
        result += s
result = 'Total: '+str(total)+'\n'+result
write_ans(result_txt, result)
