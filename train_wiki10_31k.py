'''
Created on Nov, 2017

@author: FrancesZhou
'''

from __future__ import absolute_import

import os
import argparse
import numpy as np
import scipy.io as sio
from model.preprocessing.preprocessing import generate_label_embedding_from_file, get_train_test_doc_label_data
from model.preprocessing.dataloader import DataLoader2, DataLoader4
from model.core.biLSTM import biLSTM
from model.core.LSTM import LSTM
from model.core.CNN import CNN
from model.core.solver import ModelSolver
from model.utils.io_utils import load_pickle, load_txt

#os.environ['CUDA_VISIBLE_DEVICES'] = '1'

def main():
    parse = argparse.ArgumentParser()
    # ---------- environment setting: which gpu -------
    parse.add_argument('-gpu', '--gpu', type=str, default='0', help='which gpu to use: 0 or 1')
    # ---------- foler path of train/test data -------
    parse.add_argument('-folder', '--folder_path', type=str,
                       default='datasets/Wiki10/data/deeplearning_data/adjacent_labels/all_para/',
                       help='path to train/test data')
    # ---------- vocab and word embeddings --------
    parse.add_argument('-vocab', '--vocab_path', type=str, default='datasets/material/vocab', help='path to the vocab')
    parse.add_argument('-word_embeddings', '--word_embedding_path', type=str,
                       default='datasets/material/word_embeddings.npy',
                       help='path to the word embeddings')
    # ---------- model ----------
    parse.add_argument('-max_seq_len', '--max_seq_len', type=int, default=500,
                       help='maximum sequence length')
    parse.add_argument('-model', '--model', type=str, default='biLSTM', help='model: LSTM, biLSTM, CNN')
    parse.add_argument('-pretrained_model', '--pretrained_model_path', type=str,
                       default=None, help='path to the pretrained model')
    # parse.add_argument('-if_use_seq_len', '--if_use_seq_len', type=int,
    #                    default=0, help='if model uses sequence length, 0 and 1 for use and not-use')
    # ---------- params for CNN ------------
    parse.add_argument('-num_filters', '--num_filters', type=int,
                       default=32, help='number of filters in CNN')
    parse.add_argument('-pooling_units', '--pooling_units', type=int,
                       default=64, help='number of pooling units')
    parse.add_argument('-dropout_keep_prob', '--dropout_keep_prob', type=float,
                       default=0.5, help='keep probability in dropout layer')
    filter_sizes = [2, 4, 8]
    # ---------- training parameters --------
    parse.add_argument('-if_all_true', '--if_all_true', type=int, default=0, help='if use all true labels for training')
    parse.add_argument('-n_epochs', '--n_epochs', type=int, default=10, help='number of epochs')
    parse.add_argument('-batch_size', '--batch_size', type=int, default=16, help='batch size')
    parse.add_argument('-show_batches', '--show_batches', type=int,
                       default=20, help='show how many batches have been processed.')
    parse.add_argument('-lr', '--learning_rate', type=float, default=0.0002, help='learning rate')
    parse.add_argument('-update_rule', '--update_rule', type=str, default='adam', help='update rule')
    args = parse.parse_args()

    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    print 'load vocab and word embeddings'
    vocab = load_pickle(args.vocab_path)
    word_embeddings = np.load(args.word_embedding_path)
    print 'load label embeddings'
    label_embeddings = generate_label_embedding_from_file(args.folder_path + 'label.embeddings')
    all_labels = label_embeddings.keys()
    print 'load train/test data'
    train_doc = load_pickle(args.folder_path + 'train_doc_wordID.pkl')
    test_doc = load_pickle(args.folder_path + 'test_doc_wordID.pkl')
    train_label = load_pickle(args.folder_path + 'train_title_label.pkl')
    test_label = load_pickle(args.folder_path + 'test_title_label.pkl')
    train_candidate_label = load_pickle(args.folder_path + 'train_candidate_label.pkl')
    test_candidate_label = load_pickle(args.folder_path + 'test_candidate_label.pkl')
    print 'number of labels: ' + str(len(all_labels))
    print 'create train/test data loader...'
    train_loader = DataLoader4(train_doc, train_label, train_candidate_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, given_seq_len=False, max_seq_len=args.max_seq_len)
    max_seq_len = train_loader.max_seq_len
    print 'max_seq_len: ' + str(max_seq_len)
    test_loader = DataLoader4(test_doc, test_label, test_candidate_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, given_seq_len=True, max_seq_len=max_seq_len)
    # ----------------------- train ------------------------
    label_embedding_dim = len(label_embeddings[0])
    print 'build model ...'
    if args.model == 'biLSTM':
        print 'build biLSTM model ...'
        # biLSTM: max_seq_len, word_embedding_dim, hidden_dim, label_embedding_dim, num_classify_hidden, args.batch_size
        model = biLSTM(max_seq_len, 300, 64, label_embedding_dim, 32, args)
        args.if_use_seq_len = 1
    elif args.model == 'LSTM':
        print 'build LSTM model ...'
        # LSTM: max_seq_len, word_embedding_dim, hidden_dim, label_embedding_dim, num_classify_hidden, args.batch_size
        model = LSTM(max_seq_len, 300, 64, label_embedding_dim, 32, args)
        args.if_use_seq_len = 1
    elif args.model == 'CNN':
        print 'build CNN model ...'
        # CNN: sequence_length, word_embedding_dim, filter_sizes, label_embedding_dim, num_classify_hidden, args
        # args.num_filters, args.pooling_units, args.batch_size, args.dropout_keep_prob
        model = CNN(max_seq_len, 300, filter_sizes, label_embedding_dim, 32, args)
        args.if_use_seq_len = 0

    print 'model solver ...'
    # solver: __init__(self, model, train_data, test_data, **kwargs):
    solver = ModelSolver(model, train_loader, test_loader,
                         if_use_seq_len=args.if_use_seq_len,
                         show_batches=args.show_batches,
                         n_epochs=args.n_epochs,
                         batch_size=args.batch_size,
                         update_rule=args.update_rule,
                         learning_rate=args.learning_rate,
                         pretrained_model=args.pretrained_model_path,
                         model_path=args.folder_path + args.model + '/',
                         test_path=args.folder_path + args.model + '/')
    print 'begin training...'
    solver.train(args.folder_path + args.model + '/outcome.txt')

    # test
    # test_all = DataLoader3(test_doc, test_label, all_labels, label_embeddings, args.batch_size, vocab, word_embeddings, max_seq_len)
    # solver.test(test_all)


if __name__ == "__main__":
    main()
