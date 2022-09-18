import os
import platform
import subprocess
from .log import logger



def wc_count(file_name):
    out = subprocess.getoutput(f"wc -l {file_name}")
    logger.info(f'wc_count: {out}')
    return int(out.split()[0]) + 1

def buff_count(file_name):
    with open(file_name, 'rb') as f:
        count = 0
        buf_size = 1024 * 1024
        buf = f.read(buf_size)
        while buf:
            count += buf.count(b'\n')
            buf = f.read(buf_size)
        logger.info(f'buff_count: {count}')
        return count

def paths_dataloader(dir_path, out_dir, batch_size):
    '''
    Load jsonl data, each line should be a list of dialog: ["你好", "你也好", "哈哈"]
    清洗过后的文件保存在"out_dir/cleaned_data/"目录下

    args:
        dir_path: 输入路径（notice！！！！：路径下不可有其他文件，因为可能数据文件没有后缀，无法根据后缀进行处理）
        out_dir: 输出路径
        batch_size: 每个进程处理的行数
    return:
        fid: 清洗后的数据存放的文件名（不包含后缀）
        path: 输入文件的路径
        start: 对应batch需要处理的输入文件开始行
        end -- 对应batch需要处理的输入文件结束行（不包含）
        out_path -- 清洗后的数据存放的文件路径
    '''

    cleaned_dir = os.path.join(out_dir, "cleaned_data")
    if not os.path.exists(cleaned_dir):
        os.makedirs(cleaned_dir)

    path_list = [(file, os.path.join(dir_path, file)) for file in os.listdir(dir_path)]

    for file, path in path_list:
        if platform.system() == "Windows":
            file_len = buff_count(path)
        elif platform.system() == "Linux":
            file_len = wc_count(path)
        else:
            raise Exception
        logger.info(f'path: {file_len}')
        for i in range(0, file_len, batch_size):
            fid = file.rsplit('.', 1)[0] + '_trunc' + str(i)
            out_subdir = cleaned_dir
            if not os.path.exists(out_subdir):
                os.mkdir(out_subdir)
            out_path = os.path.join(out_subdir, fid + '.txt')
            yield fid, path, i, i + batch_size, out_path
