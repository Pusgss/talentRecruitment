from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm


def tf_similarity(s1, s2):
    def add_space(s):
        return ' '.join(list(s))

    # 将字中间加入空格
    s1, s2 = add_space(s1), add_space(s2)
    # 转化为TF矩阵
    cv = CountVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))

li=[]
s1 = '本科女北京项目经理'
s2 = '本科男北京测试人员能力强'
s3 = '本科女北京测试人员工作能力强'
s4= '本科女北京系统测试人员工作能力强'
print(type(float(tf_similarity(s1, s2))))
li.append(tf_similarity(s1, s2))
li.append(tf_similarity(s3, s2))
li.append(tf_similarity(s3, s4))

li.sort(reverse = True)
print(li)

li = [[4, 2, 9], [1, 5, 6], [7, 8, 3],[8, 1, 0]]
#一次排序
new_list1 = sorted(li, key=lambda k: k[0], reverse=True)
print(new_list1)
# #二次排序
# new_list = sorted(li, key=lambda k: (k[0],k[1]), reverse=True)
# print(new_list)
b=[]
a = [['a','b'],['a','c'],['b','b']]
b.append(a[0])
for item in a:
    for items in b:
        if item[0]!=items[0]:
            b.append(item)
        print(b)
print(b)
