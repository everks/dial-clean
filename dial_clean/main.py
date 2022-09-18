from json import tool
import os
from multiprocessing import Pool
import time
import pkgutil
import pkg_resources

from .argument import get_parser
from .log import logger
from .dataloader import paths_dataloader
from .single_filter import main_filter
from .data_util import load_txt


def get_filter_set(tool_dir):
    blacklist = {}

    if os.path.exists(os.path.join(tool_dir, "black_str_vocab.txt")):
        black_str_set = set(load_txt(os.path.join(tool_dir, "black_str_vocab.txt")))
        blacklist["str_blacklist"] = black_str_set

    if os.path.exists(os.path.join(tool_dir, "black_list_vocab.txt")):
        black_list_set = set(load_txt(os.path.join(tool_dir, "black_list_vocab.txt")))
        blacklist["word_blacklist"] = black_list_set

    if os.path.exists(os.path.join(tool_dir, "special_topic.txt")):
        special_topic_str_set = set(load_txt(os.path.join(tool_dir, "special_topic.txt")))
        blacklist["special_topic"] = special_topic_str_set

    if os.path.exists(os.path.join(tool_dir, "person_name.txt")):
        person_name_set = set(load_txt(os.path.join(tool_dir, "person_name.txt")))
        blacklist["name"] = person_name_set

    en_set = {'l', '.', 'W', 't', 'o', 'z', 'k', 'C', 'B', 'y', '/', 'w', 'a', 's', 'h', 'x', '_', 'n', 'g', 'i',
              'd', 'e'}
    blacklist["english"] = en_set

    confuse_set = set()
    blacklist["confuse"] = confuse_set

    return blacklist


def main():
    args = get_parser()
    
    p = Pool(args.n_p)

    logger.info('Preparing')
    dataloader = paths_dataloader(args.raw_dir, args.out_dir, args.batch_size)
    
    if args.tool_dir == '':
        args.tool_dir = pkg_resources.resource_filename(__name__, 'tool_data/')

    blacklists = get_filter_set(args.tool_dir)

    # multi processing
    logger.info('Cleaning start!')

    for file_id, path, start, end, outpath in dataloader:
        data = (path, start, end)
        p.apply_async(main_filter, args=(args, file_id, data, blacklists, outpath, args.dirty_dir))
        time.sleep(0.01)
    time.sleep(0.01)
    p.close()
    p.join()
    logger.info('Cleaning over!')
    return 

if __name__ == '__main__':
    main()
