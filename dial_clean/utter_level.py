import re
import string
from zhon import hanzi
from hanziconv import HanziConv
import unicodedata


def split_multi_repost(utter):
    # 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
    if utter.find("//@") > -1:
        utters = [x.strip() for x in utter.split("//@")]
        for i in range(1, len(utters)):
            if utters[i]:
                utters[i] = "@" + utters[i]
        return utters
    return [utter]


def no_toupiao(utter):
    # 回归在即📣i灿们努力把数据做好💪🏻 选择选项toupiao,toupiao后选择分享我的观点及toupiao 🏅分享投票时请删除toupiao两个字🏅 🏅取消toupiao后 重新选其他选项 并重复以上步骤🏅 🌟tips:点进每个搜索词条并在该页面停留❗ 15秒以上才算有效哦! 【楷灿 气氛           参与了@terminatorhc楷>灿数据组 发起的【李楷灿指纹主唱 李楷灿无限魅力】,投给了"🌻"这个选项,你也快来表态吧~
    temp = utter.replace(" ", "")
    if "你也快来表态吧" in temp:
        return True
        # if "投给了" in temp:
        #     return True
        # if "这个选项" in temp:
        #     return True
    return False

REMOVE_ALL_PATTERN = re.compile('[^\u4e00-\u9fa5_a-zA-Z0-9%s%s]+' % (string.punctuation, hanzi.punctuation))
def remove_all(text):
    '''删除所有非中文和英文的字符'''
    return REMOVE_ALL_PATTERN.sub('', text)


NO_SPECIFIC = {"repost", "转发", "repostweibo", "分享图片",'转发微博', '图片评论', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7',
         'p8', 'p9', '图1', '图2', '图3', '图4', '图5', '图6', '图7', '图8', '图9',
         '图一','图二','图三','图四','图五','图六','图七','图八','图九', '微博会被推荐给更多用户', 'http'}
def no_specific_utter(utter):
    for item in NO_SPECIFIC:
        if item in utter:
            return True
    return False
DE_SPECIFIC = {"[图片]", "［图片］", "{ n楷体 s14}", "{ }", "{\\1c&H4080FF&}", "我擦", "\u200b"}
def de_specific(utter):
    for pattern in DE_SPECIFIC:
        utter = utter.replace(pattern, "")
    return utter

REPLY_MENTION_REGEX = re.compile(r"回复 *@.*?: *")
ANGLE_REGEX = re.compile(r"<[^\u4e00-\u9fa5]*?>")
URL_REGEX = re.compile(
    # r"(?:^|(?<![A-Za-z0-9\/\.]))"
    r"(?:^|(?<![A-Za-z0-9\/]))"
    # protocol identifier
    # r"(?:(?:https?|ftp)://)"  <-- alt?
    r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.))"
    # user:pass authentication
    r"(?:\S+(?::\S*)?@)?" r"(?:"
    # IP address exclusion
    # private & local networks
    r"(?!(?:10|127)(?:\.\d{1,3}){3})"
    r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    r"|"
    # host name
    r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
    # domain name
    # r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))" r"|" r"(?:(localhost))" r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:\/[^\)\]\}\s\u4e00-\u9fa5]*)?",
    # r"(?:$|(?![\w?!+&\/\)]))",
    # @jfilter: I removed the line above from the regex because I don't understand what it is used for, maybe it was useful?
    # But I made sure that it does not include ), ] and } in the URL.
    flags=re.UNICODE | re.IGNORECASE,
)
WEIBO_URL_REGEX = re.compile(
    r"(?:(?:https?:?\/\/|ftp:\/\/|www\d{0,3}\.)t\.cn?(\/[a-zA-Z0-9]{0,8})?)"
)
BRACKETS_REGEX = re.compile(r"\[.*?\] *|［.*?］ *")
# 感恩节# 感谢给予自己生命，养育我们长大的父母，他们教会了我们爱、善良和尊严。
HASHTAG_REGEX = re.compile(r"#.*?# *")
EMOTION_REGEX = re.compile(r":.*?: *")
SINGLE_REPOST_MENTION_REGEX = re.compile(r"(@+)(\S*?\s*?): *")
# 一起来吗？@Cindy //@Bob: 算我一个//@Amy: 今晚开派对吗？
REPOST_MENTION_REGEX = re.compile(r"/ ?/? ?@ ?(?:[\w \-] ?){,30}? ?:.+")
# 知乎特有
ZHIHU_SHOW_ALL_REGEX = re.compile(r"…* *显示全部\s*")
# "哈哈 sda83daj.jp 哈哈"
ALPHA_NUM_REGEX = re.compile(r" [a-zA-Z0-9.]+ ")
PHONE_REGEX = re.compile(r"\d{11,}")
QQ_REGEX = re.compile(r"[qQ]{2,}\d{5,12}\D")

def contain_at(seq, tail_length=30):
    flag = re.search(r"(@+)\S{,30} ", seq)
    if flag is not None:
        return True
    r_at_idx = seq.rfind("@")
    return r_at_idx > -1 and len(seq[r_at_idx:]) < tail_length

def no_at(seq, tail_length=30):
    temp_pat = re.compile(r"(@+)\S{,30} ")
    seq = temp_pat.sub("", seq)
    r_at_idx = seq.rfind("@")
    if len(seq[r_at_idx:]) < tail_length:
        seq = seq[:r_at_idx]
    return seq

EMOJI_REGEX = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002500-\U00002BEF"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"
    "\u3030"
    "\\*\u20e3"
    "#\u20e3"
    "]+",
    flags=re.UNICODE,
)
COLON_REGEX = re.compile(r"[:\s]{4,}")
def remove_emoji(text):
    text = EMOJI_REGEX.sub(r"", text)
    text = COLON_REGEX.sub(r"", text)
    return text.strip()

def bert_clean(text):
    """From transformers.BertTokenizer"""
    """Performs invalid character removal and whitespace cleanup on text."""

    def _is_control(char):
        """Checks whether `chars` is a control character."""
        # These are technically control characters but we count them as whitespace
        # characters.
        if char in ["\t", "\n", "\r"]:
            return False
        cat = unicodedata.category(char)
        return bool(cat.startswith("C"))

    def _is_whitespace(char):
        """Checks whether `chars` is a whitespace character."""
        # \t, \n, and \r are technically contorl characters but we treat them
        # as whitespace since they are generally considered as such.
        if char in [" ", "\t", "\n", "\r"]:
            return True
        cat = unicodedata.category(char)
        return cat == "Zs"

    output = []
    for char in text:
        cp = ord(char)
        if cp == 0 or cp == 0xFFFD or _is_control(char):
            continue
        if _is_whitespace(char):
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)

def is_chinese_char(cp):
    return (
            (cp >= 0x4E00 and cp <= 0x9FFF)
            or (cp >= 0x3400 and cp <= 0x4DBF)  #
            or (cp >= 0x20000 and cp <= 0x2A6DF)  #
            or (cp >= 0x2A700 and cp <= 0x2B73F)  #
            or (cp >= 0x2B740 and cp <= 0x2B81F)  #
            or (cp >= 0x2B820 and cp <= 0x2CEAF)  #
            or (cp >= 0xF900 and cp <= 0xFAFF)
            or (cp >= 0x2F800 and cp <= 0x2FA1F)  #
    )

def contains_Chinese(seq):
    for char in seq:
        cp = ord(char)
        if is_chinese_char(cp):
            return True
    return False

# TODO speed up
def de_str_blacklist(utter, blacklist):
    for word in blacklist:
        if word in utter:
            return word
    return None


def reduce_duplicated_phrase(seq_str, times=3, length=1):
    '''长度为length的短语最多出现times次'''
    while length * (times + 1) < len(seq_str):
        # 0 1 2 3 4, 5 6 7 8 9 10 11
        # l = 2,  t = 3
        i = 0
        while i + length * (times + 1) <= len(seq_str):
            substr = seq_str[i: i + length]
            j = i + length
            while (j + length) <= len(seq_str) and seq_str[j: j + length] == substr:
                j += length
            if (i + length * times) < j:
                seq_str = seq_str[: i + length * times] + seq_str[j:]
            i += 1
        length += 1
    return seq_str

def too_short(utter, length=2):
    temp = utter.replace(" ", "")
    return len(temp) < length

def too_long(utter, length=300):
    temp = utter.replace(" ", "")
    return length < len(temp)

def toSimplified(text):
    return HanziConv.toSimplified(text)

def puncRegularized(text):
    '''如果有多个标点符号连在一起，调整为最后一个出现的符号'''
    punctuation = string.punctuation + hanzi.punctuation
    return re.sub("(?!</)([%s]+)([%s])" %(punctuation, punctuation), "\\2", text)

OTHER_BRACKETS = re.compile("【(.*?)】|「(.*?)」|『(.*?)』|<(.*?)>")
def remove_other_brackets(text: str):
    '''针对知乎数据：如 有哪些年轻人「千万不能碰」的东西 
        将【】,「」,『』,<>删除，保留中间内容'''
    return OTHER_BRACKETS.sub("\\1\\2\\3\\4", text)

MULTI_BLANK = re.compile(" {2,}")
def remove_multi_blank(text: str):
    '''之前的清洗替换出了很多空格，格式化一下'''
    return MULTI_BLANK.sub(" ", text)