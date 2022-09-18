import argparse
from .log import logger

def add_filter_args(argparser):
    opt = argparser.add_argument_group('Filter Arguments')

    opt.add_argument('--no_utter_dup', action="store_true")
    opt.add_argument('--re_name', action="store_true")
    opt.add_argument('--split_multi_repost', action="store_true")
    opt.add_argument('--no_ad', action="store_true")
    opt.add_argument('--de_generic_dialog', action="store_true")
    opt.add_argument('--de_reply_tag', action="store_true")
    opt.add_argument('--de_hashtag', action="store_true")
    opt.add_argument('--de_emotion', action="store_true")
    opt.add_argument('--de_mention', action="store_true")
    opt.add_argument('--de_repost', action="store_true")
    opt.add_argument('--de_duplicated', action="store_true")
    opt.add_argument('--de_emoji', action="store_true")
    opt.add_argument('--no_short', action="store_true")
    opt.add_argument('--no_long', action="store_true")
    opt.add_argument('--no_special_topic', action="store_true")
    opt.add_argument('--bert_clean', action="store_true")
    opt.add_argument('--cleantext_clean', action="store_true")
    opt.add_argument('--no_str_blacklist', action="store_true")
    opt.add_argument('--no_toupiao', action="store_true")
    opt.add_argument('--no_short_response', action="store_true")
    opt.add_argument('--no_specific_utter', action="store_true")
    opt.add_argument('--contain_zh', action="store_true")
    opt.add_argument('--de_single_repost_mention', action="store_true")
    opt.add_argument('--de_weibo_url', action="store_true")
    opt.add_argument('--de_url', action="store_true")
    opt.add_argument('--no_mention', action="store_true")
    opt.add_argument('--de_angle', action="store_true")
    opt.add_argument('--de_alpha_num', action="store_true")
    opt.add_argument('--de_phone', action="store_true")
    opt.add_argument('--de_qq', action="store_true")
    opt.add_argument('--de_specific', action="store_true")

    # special files
    opt.add_argument('--de_showall', action="store_true")
    opt.add_argument('--de_brackets', action="store_true")

    # words list level
    opt.add_argument('--no_word_blacklist', action="store_true")
    opt.add_argument('--no_alpha_noise', action="store_true")
    opt.add_argument('--check_confuse_word', action="store_true")
    opt.add_argument('--yda_dedupl', action="store_true")
    # todo remedy http

    # songyi 10-6
    opt.add_argument('--simplified', action='store_true')
    opt.add_argument('--punc_regularized', action='store_true')
    opt.add_argument('--no_session_ad', action='store_true')
    opt.add_argument('--remove_all', action='store_true')
    opt.add_argument('--context_filter', action='store_true', 
            help='根据context内容来清洗对话，目前判断规则为context以\
                vo:或3个以上的数字结尾')
    opt.add_argument('--de_other_brackets', action='store_true')

    

def change_args(args):
    if args.filter_type == 'all':
        for key, value in vars(args).items():
            if value == False:
                setattr(args, key, True)
    return args

from IPython import embed
def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    opt = parser.add_argument_group('Required Arguments')
    opt.add_argument("--raw_dir", type=str, required=True, help="Dir of the raw dataset.")
    opt.add_argument("--out_dir", type=str, required=True, help="Main data dir.")

    opt = parser.add_argument_group('Optional Arguments')
    opt.add_argument("--n_p", type=int, default=32, help="Number of subprocess")
    opt.add_argument("--batch_size", type=int, default=500000)
    opt.add_argument("--tool_dir", type=str, default="",
                        help="Path of the tool data.")
    opt.add_argument("--dirty_dir", type=str, default="", help="Dir to save dirty cases.")
    opt.add_argument('--raw_format', type=str, default='jsonl', help="format of the raw dataset")

    opt = parser.add_argument_group('Convenient Arguments')

    opt.add_argument("--filter_type", choices=['all', 'weibo', 'zhihu', 'custom'])


    add_filter_args(parser)
    args = parser.parse_args()
    # 根据convenient argument改变filter argument
    args = change_args(args)

    logger.info(args)
    return args

