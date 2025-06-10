# CMS/backend/app/utils/moderation.py

# 示例敏感词列表 
DEFAULT_SENSITIVE_WORDS = [
    "脏话", "妈的", "操", "滚", "傻逼", "去死", "神经病",
    "色情", "裸聊", "约炮", "卖淫", "嫖娼", 
    "暴力", "砍人", "自杀", "恐怖袭击",
    # 可以根据需要添加更多词汇
]

def contains_sensitive_word(text, sensitive_words_list=None):
    """
    检测文本中是否包含敏感词列表中的任何词汇。
    :param text: 要检测的文本字符串。
    :param sensitive_words_list: 包含敏感词的列表。如果为None，则使用DEFAULT_SENSITIVE_WORDS。
    :return: True 如果包含敏感词，否则 False。
    """
    if not text:
        return False
    
    words_to_check = sensitive_words_list if sensitive_words_list is not None else DEFAULT_SENSITIVE_WORDS
    
    # 对于较长的敏感词列表和文本，可以考虑更高级的匹配算法 (如Aho-Corasick)
    # 但对于简易版本，直接遍历检查即可。
    for word in words_to_check:
        if word.lower() in text.lower(): # 忽略大小写进行匹配
            return True
    return False 