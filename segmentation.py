import jieba
import pandas
import re
import math


# segmentation and calculate the tf
def to_vector(paragraph, stop_mode='punctuation', returntf=True):
    if len(paragraph) is 0:
        raise Exception("The length of string is 0.")

    # 过滤非中文
    pattern = re.compile(r"[^\u4e00-\u9fa5A-Za-z0-9]")
    segs = jieba.lcut(pattern.sub('', paragraph), cut_all=False)

    # # 去中文停用词
    if stop_mode is 'cn':
        with open(r'./res/stop_cn', 'r', encoding='utf-8') as f:
            sw = (w.strip() for w in f.readlines())
        segs = list(filter(lambda x: x not in sw, segs))

    if not returntf:
        return segs
    else:
        return tf_counter(segs)


def tf_counter(segs):
    seg_df = pandas.DataFrame({'segment': segs})
    # 计算TF
    seg_df['num'] = 1
    tf_df = seg_df.groupby('segment').sum()
    vector = tf_df.to_dict(orient='dict')['num']
    return vector


# 实现dv = nv + c*nbi
def combination_dict(old, new, coefficient=1.0):
    for k in new.keys():
        new[k] *= coefficient
        if k in old.keys():
            new[k] += old[k]

    return dict(old, **new)


# 归一化
def simple_normalization(vector):
    summary = math.fsum(vector.values())
    for k, v in vector.items():
        vector[k] = v/summary
    return vector
