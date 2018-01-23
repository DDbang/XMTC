'''
Created on Nov, 2017

@author: FrancesZhou
'''

from __future__ import absolute_import
import numpy as np


# if len(np.intersect1d(pre_labels, true_labels)):
#     count += 1
# return count*1.0/num
# return count, count * 1.0 / num

def dcg_at_k(r, k):
    r = np.asfarray(r)[:k]
    return np.sum(r / np.log2(np.arange(2, r.size + 2)))

def ndcg_at_k(r, k, true_num):
    #dcg_max = dcg_at_k(sorted(r, reverse=True), k)
    dcg_max = dcg_at_k(np.ones(k), min(k, true_num))
    if not dcg_max:
        return 0.
    return dcg_at_k(r, k) / dcg_max

def precision(pre, tar, indices):
    p_1 = []
    p_3 = []
    p_5 = []
    ndcg_1 = []
    ndcg_3 = []
    ndcg_5 = []
    for i in range(len(pre)):
        # pre_labels = np.argsort(pre[i])
        label_score = []
        s_indices = np.array(indices[i])
        s_pre = pre[i]
        for k in range(len(s_indices)):
            label_score.append((s_indices[k], s_pre[k]))
        label_score = sorted(label_score, key=lambda x :x[1])
        label_score.reverse()
        pre_labels = [x[0] for x in label_score]
        true_pos = np.squeeze(np.nonzero(tar[i]))
        true_labels = np.array(s_indices[true_pos])
        r = []
        for p_ in pre_labels:
            if p_ in true_labels:
                r.append(1)
            else:
                r.append(0)
        p_1.append(np.mean(r[:1]))
        p_3.append(np.mean(r[:3]))
        p_5.append(np.mean(r[:5]))
        ndcg_1.append(ndcg_at_k(r, 1))
        ndcg_3.append(ndcg_at_k(r, 3))
        ndcg_5.append(ndcg_at_k(r, 5))

    return np.mean([p_1, p_3, p_5, ndcg_1, ndcg_3, ndcg_5], axis=0)

def precision_for_all(tar_pid_label, pred_pid_label, pred_pid_score):
    p_1 = []
    p_3 = []
    p_5 = []
    ndcg_1 = []
    ndcg_3 = []
    ndcg_5 = []
    for pid, score in pred_pid_score.items():
        indices = np.argsort(score)
        indices = indices[::-1]
        pre_labels = np.array(pred_pid_label[pid])[indices]
        true_labels = tar_pid_label[pid]
        r = []
        for p_ in pre_labels:
            if p_ in true_labels:
                r.append(1)
            else:
                r.append(0)
        p_1.append(np.mean(r[:1]))
        p_3.append(np.mean(r[:3]))
        p_5.append(np.mean(r[:5]))
        ndcg_1.append(ndcg_at_k(r, 1))
        ndcg_3.append(ndcg_at_k(r, 3))
        ndcg_5.append(ndcg_at_k(r, 5))
    return np.mean([p_1, p_3, p_5, ndcg_1, ndcg_3, ndcg_5], axis=1)

def precision_for_label_vector(tar_pid_label, pred_pid_score):
    p_1 = []
    p_3 = []
    p_5 = []
    ndcg_1 = []
    ndcg_3 = []
    ndcg_5 = []
    for pid, true_labels in tar_pid_label.items():
        # pre_labels = np.argsort(-pred_pid_score[pid])[:5]
        # true_labels = np.squeeze(np.nonzero(tar_pid_label[pid]))
        pre_labels = pred_pid_score[pid]
        r = []
        for p_ in pre_labels:
            if p_ in true_labels:
                r.append(1)
            else:
                r.append(0)
        p_1.append(np.mean(r[:1]))
        p_3.append(np.mean(r[:3]))
        p_5.append(np.mean(r[:5]))
        ndcg_1.append(ndcg_at_k(r, 1))
        ndcg_3.append(ndcg_at_k(r, 3))
        ndcg_5.append(ndcg_at_k(r, 5))
    return np.mean([p_1, p_3, p_5, ndcg_1, ndcg_3, ndcg_5], axis=1)

def precision_for_comp_score_vector(true_labels, tar_pid_y, pre_pid_score):
    p_1 = p_3 = p_5 = []
    ndcg_1 = ndcg_3 = ndcg_5 = []
    i = 0
    for pid, y in tar_pid_y.items():
        if i == 0:
            print y
        i += 1
        pre_label_index = np.argsort(-pre_pid_score[pid])[:5]
        r = []
        for ind in pre_label_index:
            r.append(y[ind])
        p_1.append(np.mean(r[:1]))
        p_3.append(np.mean(r[:3]))
        p_5.append(np.mean(r[:5]))
        ndcg_1.append(ndcg_at_k(r, 1, true_labels[pid]))
        ndcg_3.append(ndcg_at_k(r, 3, true_labels[pid]))
        ndcg_5.append(ndcg_at_k(r, 5, true_labels[pid]))
    return np.mean([p_1, p_3, p_5, ndcg_1, ndcg_3, ndcg_5], axis=1)

def precision_for_batch_comp_score(true_label_num, tar_pid_y, pre_pid_score):
    p_1 = p_3 = p_5 = []
    ndcg_1 = ndcg_3 = ndcg_5 = []
    for i in range(len(tar_pid_y)):
        pre_label_index = np.argsort(-pre_pid_score[i])[:5]
        y = tar_pid_y[i]
        r = []
        for ind in pre_label_index:
            r.append(y[ind])
        p_1.append(np.mean(r[:1]))
        p_3.append(np.mean(r[:3]))
        p_5.append(np.mean(r[:5]))
        ndcg_1.append(ndcg_at_k(r, 1, true_label_num[i]))
        ndcg_3.append(ndcg_at_k(r, 3, true_label_num[i]))
        ndcg_5.append(ndcg_at_k(r, 5, true_label_num[i]))
    return np.mean([p_1, p_3, p_5, ndcg_1, ndcg_3, ndcg_5], axis=1)
