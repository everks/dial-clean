from IPython import embed

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

if __name__ == '__main__':
    utter = '我是我是我是我是'
    ret = reduce_duplicated_phrase(utter)
    print('ret: ', ret)