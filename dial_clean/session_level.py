import re

def isAd(dialog):
    '''判断当前dialog是否为广告，通过判断dialog的第一句话即context来决定（后续可进行更改）'''
    context = dialog[0]
    
    ad_list = ['京东','出租','转卖','成新','代购','出售','转让','合租',
        '直租','整租','开团','便宜卖','买家','淘宝','没货','有货',
        '正品','团购','兰蔻','雅诗兰黛', '转租', '/phone', '手机号', '领劵', '购物劵',
        '猫超',]

    for ad_word in ad_list:
        if ad_word in context:
            return True
    return False

context_filter_pattern = re.compile('[0-9]{3,}$')
def context_filter(dialog):
    text = dialog[0]
    if text.endswith('vo:') or context_filter_pattern.search(text):
        return True
    return False