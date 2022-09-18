import os
import collections
import json
import gc
from cleantext import clean

from .log import logger
from . import session_level, utter_level
from .data_util import save_txt, save_json, save_jsonl

def load_lines(path, start, end, data_format):
    '''
    Args:
        path: 输入文件路径
        start: 开始行
        end: 结束行
        data_format: 文件格式，目前实现了jsonl和tsv
    Returns:
        data -> list: path文件中的[start, end)行，每一行是一个dialog。
    '''
    data = []
    with open(path, encoding='utf-8') as f:
        i = -1
        for line in f:
            i += 1
            if i > end - 1:
                break
            if i > start - 1:
                if len(line.strip()) > 0:
                    if data_format == 'jsonl':
                        data.append(json.loads(line))
                    elif data_format == 'tsv':
                        data.append(line.strip('\n').strip('\t').split('\t'))
                    else:
                        raise RuntimeError('输入格式错误')
    return data


def main_filter(args, file_id, data, blacklist, out_path, dirty_dir, cut=True):
    '''
    Args:
        args: 命令行参数args
        file_id: 清洗后的数据应该存放的文件名（不包含后缀）
        data: (path, start, end) 分别为需要清洗的数据文件存放路径，文件中开始行数（包含）和结束行数（不包含）
        blacklist: 字典类型，存放各种辅助数据，TODO: 待补充
        out_path: 清洗后的数据应该存放的文件路径
        dirty_dir: 清洗后的脏数据应该存放的文件路径
        cut: 是否使用结巴分词
    Returns:

    '''

    logger.info(f'The saved path of data is {out_path}')

    logger.info(f'Start: {file_id}')

    dirty_data = {k: collections.defaultdict(set) for k in
                    ["other", "name", "str_blacklist", "word_blacklist", "not_en", "confused", "generic", "emoji",
                    "duplicated", "confuse"]} if dirty_dir else None
    
    res = []
    data = load_lines(data[0], data[1], data[2], args.raw_format)
    logger.info(f"Size of this batch : {len(data)}, log in {file_id}")
    logger.info(f"Batch sample: {data[0][0]}, log in {file_id}")

    while len(data):
        dialog = data.pop(0)

        # session level
        if args.no_utter_dup and len(set(dialog)) < 2:
            if dirty_data and len(set(dialog)) > 0:
                dirty_data["other"]["less_pair"].add(dialog[0])
            continue
        if args.no_session_ad and session_level.isAd(dialog):
            if dirty_data:
                dirty_data['other']['session_ad'].add(dialog[0])
            continue
        if args.context_filter and not session_level.context_filter(dialog):
            if dirty_data:
                dirty_data['other']['session_filter'].add(dialog[0])
            continue

        # utterance level
        new_dialog = []
        # 对dialog中的每一个uttr进行清洗，将清洗后的数据放入new_dialog
        for i in range(len(dialog)):
            # 根据微博转发规则将对话拆开, utters 是对话的数组，即数组的数组。
            if args.split_multi_repost:
                utters = utter_level.split_multi_repost(dialog[i])
            else:
                utters = [dialog[i]]

            # 对于拆分出来的utters
            skip_utter = False
            for j, utterance in enumerate(utters):
                if skip_utter:
                    skip_utter = False
                    continue
                # 判断如果数据是微博投票，将数据过滤掉
                # 如果下一句是投票的话，则跳过这句和下一句 
                if args.no_toupiao and (j+1) < len(utters):
                    toupiao = utter_level.no_toupiao(utters[j+1])
                    if toupiao:
                        skip_utter = True
                        if dirty_data:
                            dirty_data["other"]["toupiao"].add(utters[j] + "\t\t" + utters[j + 1])
                        continue
        
                # 删除所有非中文字符
                if args.remove_all:
                    utterance = utter_level.remove_all(utterance)
            
                orig_utter = utterance
                logger.info(utterance.index("¡ 评论"))
               
                # 一种特定pattern
                if "¡ 评论" in utterance:
                    utterance = utterance[:utterance.index("¡ 评论")]
                    if dirty_data:
                        dirty_data["other"]["¡ 评论"].add(orig_utter)
            
                # 去除一些特定的句子，如 "转发" 
                if utterance and args.no_specific_utter:
                    specific_utter = utter_level.no_specific_utter(orig_utter)
                    if specific_utter:
                        if dirty_data:
                            dirty_data["other"]["no_specific_utter"].add(orig_utter)
                        utterance = ""
                
                # 去除微博中 "回复 @XXX:"
                if utterance and args.de_reply_tag:
                    len_before = len(utterance)
                    utterance = utter_level.REPLY_MENTION_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_reply_tag"].add(orig_utter)
                
                # 去除 <XXX> 其中XXX为非中文
                if utterance and args.de_angle:
                    len_before = len(utterance)
                    utterance = utter_level.ANGLE_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["angle"].add(orig_utter)

                if utterance and args.de_url:
                    len_before = len(utterance)
                    utterance = utter_level.URL_REGEX.sub(" ", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["url"].add(orig_utter)

                if utterance and args.de_weibo_url:
                    len_before = len(utterance)
                    utterance = utter_level.WEIBO_URL_REGEX.sub(" ", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["weibo_url"].add(orig_utter)
                
                if utterance and args.de_brackets:
                    len_before = len(utterance)
                    utterance = utter_level.BRACKETS_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["weibo_emoji"].add(orig_utter)

                if utterance and args.de_hashtag:
                    len_before = len(utterance)
                    utterance = utter_level.HASHTAG_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["hashtag"].add(orig_utter)

                if utterance and args.de_emotion:
                    len_before = len(utterance)
                    utterance = utter_level.EMOTION_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["emotion"].add(orig_utter)
                
                if utterance and args.no_mention:
                    if utter_level.contain_at(utterance):
                        if dirty_data:
                            dirty_data["other"]["mention"].add(orig_utter)
                        utterance = ""

                if utterance and args.de_mention:
                    len_before = len(utterance)
                    # utterance = str_level.COMMON_MENTION_REGEX.sub("", utterance).strip()
                    utterance = utter_level.no_at(utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["no_at"].add(orig_utter)

                if utterance and args.de_single_repost_mention:
                    len_before = len(utterance)
                    utterance = utter_level.SINGLE_REPOST_MENTION_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["single_repost"].add(orig_utter)

                if utterance and args.de_repost:
                    len_before = len(utterance)
                    utterance = utter_level.REPOST_MENTION_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["repost_mention"].add(orig_utter)

                if utterance and args.de_showall:
                    len_before = len(utterance)
                    utterance = utter_level.ZHIHU_SHOW_ALL_REGEX.sub("", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["showall"].add(orig_utter)
            
                if utterance and args.de_emoji:
                    len_before = len(utterance)
                    utterance = utter_level.remove_emoji(utterance)
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["emoji"]["emoji"].add(orig_utter)

                if utterance and args.de_alpha_num:
                    len_before = len(utterance)
                    utterance = utter_level.ALPHA_NUM_REGEX.sub(" ", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_alpha_num"].add(orig_utter)

                if utterance and args.de_specific:
                    len_before = len(utterance)
                    utterance = utter_level.de_specific(utterance)
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_specific"].add(orig_utter)
            
                if utterance and args.de_phone:
                    len_before = len(utterance)
                    utterance = utter_level.PHONE_REGEX.sub(" ", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_phone"].add(orig_utter)

                if utterance and args.de_qq:
                    len_before = len(utterance)
                    utterance = utter_level.QQ_REGEX.sub(" ", utterance).strip()
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_qq"].add(orig_utter)
                
                # 调用clean-text lib
                if utterance and args.cleantext_clean:
                    len_before = len(utterance)
                    utterance = clean(
                        utterance,
                        fix_unicode=True,
                        to_ascii=False,
                        normalize_whitespace=True,
                        no_line_breaks=True,
                        no_urls=False,
                        no_emails=True,
                        no_phone_numbers=True,
                        replace_with_url=" ",
                        replace_with_email=" ",
                        replace_with_phone_number=" ")
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["cleantext"].add(orig_utter)

                if utterance and args.bert_clean:
                    utterance = utter_level.bert_clean(utterance)
                if utterance and args.contain_zh:
                    if not utter_level.contains_Chinese(utterance):
                        if dirty_data:
                            dirty_data["other"]["contain_zh"].add(orig_utter)
                        utterance = ""

                if utterance and args.no_special_topic:
                    special_topic_word = utter_level.de_str_blacklist(utterance, blacklist["special_topic"])
                    if special_topic_word:
                        if dirty_data:
                            dirty_data["special_topic"][special_topic_word].add(orig_utter)
                        utterance = ""

                if utterance and args.no_str_blacklist:
                    utterance = utter_level.TM_REGEX.sub(lambda m: m.group(1) + m.group(3), utterance)
                    MAX_LEN_STR_BLACKWORD = 120
                    black_word = utter_level.de_str_blacklist2(utterance, blacklist["str_blacklist"], MAX_LEN_STR_BLACKWORD)
                    if black_word:
                        if dirty_data:
                            dirty_data["str_blacklist"][black_word].add(orig_utter)
                        utterance = ""
                
                if utterance and args.de_duplicated:
                    len_before = len(utterance)
                    utterance = utter_level.reduce_duplicated_phrase(utterance)
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_duplicated"].add(orig_utter)
            
                if utterance and args.no_short:
                    len_flag = utter_level.too_short(utterance)
                    if len_flag:
                        if dirty_data:
                            dirty_data["other"]["short"].add(orig_utter)
                        utterance = ""

                if utterance and args.no_long:
                    len_flag = utter_level.too_long(utterance)
                    if len_flag:
                        if dirty_data:
                            dirty_data["other"]["long"].add(orig_utter)
                        utterance = ""
                
                if utterance and args.simplified:
                    utterance = utter_level.toSimplified(utterance)
            
                if utterance and args.punc_regularized:
                    utterance = utter_level.puncRegularized(utterance)

                if utterance and args.de_other_brackets:
                    len_before = len(utterance)
                    utterance = utter_level.remove_other_brackets(utterance)
                    if dirty_data and len(utterance) < len_before:
                        dirty_data["other"]["de_other_brackets"].add(orig_utter)

                if utterance:
                    utterance = utter_level.remove_multi_blank(utterance)


                # TODO：暂时删去所有的word level级别filter，后续版本再加入
                pass

                utterance = utterance.strip()

                new_dialog.append(utterance)
                
                
                
        # 根据dialog中的空字符串将对话拆分成好几个对话
        # 如果对话第一句为空，则从第二句开始算起
        start_idx = 0 if new_dialog[0] else 1
        # 遍历dialog
        for i in range(1, len(new_dialog) + 1):
            # 如果遍历完毕或当前sentence为空字符串
            if i == len(new_dialog) or not new_dialog[i]:
                if len(new_dialog[start_idx: i]) > 1:
                    res.append(new_dialog[start_idx: i])
                start_idx = i + 1

    if len(res) > 0:
        save_txt("\n".join(["\t\t".join(x) for x in res]), out_path)
        logger.info(f'Resulting {len(res)} dialogs')
        del res, data
        gc.collect()
    if dirty_data:
        save_dirty(dirty_dir, dirty_data, file_id)

    logger.info(f'{file_id} over')

    return file_id

def save_dirty(dirty_dir, dirty_data, file_id):
    dirty_dir = os.path.join(dirty_dir, "dirty_data")
    if not os.path.isdir(dirty_dir):
        os.makedirs(dirty_dir)
    for k, v in dirty_data.items():
        k_path = os.path.join(dirty_dir, k)
        if sum(len(subv) for subv in v.values()):
            if not os.path.isdir(k_path):
                os.mkdir(k_path)
            if "blacklist" in k and len(v) > 0:
                temp_bl = {bk: len(bv) for bk, bv in v.items()}
                temp_bl = sorted(temp_bl.items(), key=lambda x: x[1], reverse=True)
                save_json(temp_bl, os.path.join(k_path, "sta_{}.json".format(file_id)))
                save_json({bk: list(bv) for bk, bv in v.items()}, os.path.join(k_path, "{}.json".format(file_id)))
            else:
                for sub_k, sub_v in v.items():
                    if len(sub_v) > 0:
                        save_jsonl(sub_v, os.path.join(k_path, "{}_{}.jsonl".format(sub_k, file_id)))
    del dirty_data
    gc.collect()
    return