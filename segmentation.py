import jieba
import pandas
import re
import math

with open(r'./res/stop_cn', 'r', encoding='utf-8') as f:
    sw = {w.strip() for w in f.readlines()}


# segmentation and calculate the tf
def to_vector(paragraph, stop_mode='cn', weight=1, returntf=True):
    if len(paragraph) is 0:
        raise Exception("The length of string is 0.")

    # 过滤非中文
    pattern = re.compile(r"[^\u4e00-\u9fa5A-Za-z]")
    segs = jieba.lcut(pattern.sub('', paragraph), cut_all=False)

    # # 去中文停用词
    if stop_mode is 'cn':
        segs = list(filter(lambda x: x not in sw, segs))

    return segs if not returntf else tf_counter(segs, weight)


def tf_counter(segs, weight):
    seg_df = pandas.DataFrame({'segment': segs})
    # 计算TF
    seg_df['num'] = weight
    tf_df = seg_df.groupby('segment').sum()
    vector = tf_df.to_dict(orient='dict')['num']
    return vector


# 实现dv = nv + c*nbi
def combination_dict(old, new, coefficient=1.0):
    if coefficient == 1.0:
        for k in set(new.keys()).intersection(old.keys()):
            new[k] += old[k]
    else:
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


if __name__ == '__main__':
    d1 = {'a':1, 'b': 2}
    d2 = {'b':2, 'c':3}
    d = combination_dict(d1, d2)
    print(d)
