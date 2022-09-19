本项目为一个清洗对话数据的多线程框架，针对知乎、微博、贴吧等。


项目基于https://github.com/lemon234071/clean-dialog 添加了更多的规则并打包

# 使用方法
## 基于源码安装
首先下载源码
```
git clone https://github.com/everks/dial-clean.git
```
然后进行安装
```
cd dial_clean
python setup.py install
```
最后调用命令即可
```
dial-clean --raw_dir xxx --out_dir xxx
```
## 也可以使用pypi安装
```
pip install dial-clean
```

# Auguments
除去raw_dir与out_dir外，其他均为可选参数
## general 
| 参数               | 描述                 |
| :---------------  | :------------------- |
| out_dir           | 清洗后的文件输出目录 |
| raw_dir           | 待处理文件所在mull  |
| n_p               | 多进程数 |
| batch_size        | 单个进程最大处理session数 |
| tool_dir          | 工具数据所在目录（如黑名单）|
| raw_format        | 待处理文件的格式（默认为jsonl，目前可使用jsonl和tsv）  |
| dirty_dir         | 存储清洗出来的脏数据，如为空则不存  |

## convenient
默认filter_type是all，即所有的filter均启用，用户可以将其设置为custom来手动选择参数
| 参数               | 描述                 |
| :---------------  | :------------------- |
| filter_type       | 通过filter_type可以进行调整(default: all) |

## session level filter
| 参数               | 描述                 |
| :---------------  | :------------------- |
| no_utter_dup   | dialog句间去重后如果集合len小于2，则丢弃数据  |
| no_session_ad     | 根据关键词去除广告    |
| context_filter    | 根据context内容进行清除(目前去除以vo:或三个以上数字结尾的context)   |

## utter level filter
| 参数               | 描述                 |
| :---------------  | :------------------- |
| split_multi_repost| 将微博转发数据按"//@aaa XXXX //@bbb XXX"撕开成多句  |
| no_toupiao        | 判断是否是微博投票 |
| remove_all        | 去除所有非中文和英文的字符  |
| no_specific_utter | 删除一些特定句子（包括图片相关内容） |
| de_specific       | 去除句中固定pattern    |
| de_reply_tag      | 去除微博中 "回复 @XXX:" |
| de_angle          | 去除 <XXX> 其中XX为非中文 |
| de_url            | 去除 url |
| de_weibo_url      | 去除 http:\\t.c |
| de_brackets       | 去除某些特定源中的 "\[XXX\]", 如微博，大部分应该是emoji表情 |
| de_hashtag        | 去除句中 "# XXX#" |
| de_emotion        | 去除句中 ": XXX:" |
| no_mention       | 去除包含 @XXX 的句子 |
| de_mention        | 去除句子中 "@Cindy"， "@Bob:"， "@Amy:" 等|
| de_single_repost_mention| 去掉 "@XXX:" |
| de_repost         | 去除句中 "//XXX" |
| de_showall        | 去除某些特定源中的 "...显示全部"，如知乎 |
| de_emoji          | 去除emoji       |
| de_alpha_num      | 去除长串无意义的数字字母组合 |
| de_phone          | 将11位以上的连续数字删除     |
| de_qq             | 去除qq号                  |
| cleantext_clean | 使用[clean-text]() 清理 （电话号、邮箱、unicode错误等） |
| bert_clean        | 使用transformers BertTokenizer 中非法字符检查函数清理句子 |
| contain_zh        | 删掉不包含中文的句子 |
| no_special_topic  | 过滤包含特定名单词的对话 |
| no_str_blacklist  | 过滤包含黑名单词的对话 |
| de_duplicated     | 句中短语降重 （待用后缀算法优化） |
| no_short          | 去除过短的句子(默认长度为<2) |
| no_long           | 去除过长的句子(默认长度为>300) |
| simplified        | 将繁体字转换为简体字  |
| punc_regularized  | 进行标点符号规格化    |
| de_other_brackets | 将【】等括号删除，保留中间内容，针对知乎源 |

        
# 更新计划
1. 实现word level filter: 2022-10-1之前
2. 实现默认支持更多的输入输出格式: 2022-9-25之前
3. 整理整个项目的文档和注释: 2022-9-25之前



# 下面为待完成功能，doing

| re_name           | 人名用 <NAME1>, <NAME2> ...替换 |
| no_ad             | 去除可能是广告的对话（同样的回复对应多个context）借鉴[论文](https://www.aclweb.org/anthology/D13-1096.pdf) |
| de_generic_dialog | 去通用回复 借鉴[论文](https://arxiv.org/abs/1911.00536)|
| no_short_response | 去掉对话尾部所有过短回复 |
| de_brackets       | 去除某些特定文件中的 "\[XXX\]" |
| no_word_blacklist | 过滤分此后的黑名单词的对话 |
| no_alpha_noise    | 过滤掉含有不成 英文单词的 字母组合 的句子 |
| check_confuse_word| 保存包含混淆名单词的对话进行recall |
| yda_dedupl        | 如果一个词语在句子中出现的比例 超过一个阈值则放弃该句子 |





