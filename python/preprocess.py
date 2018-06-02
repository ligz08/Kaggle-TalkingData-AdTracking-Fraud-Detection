#!/usr/bin/env python3

import numpy as np
import pandas as pd
import os
import sys
import gc
from sklearn.preprocessing import OneHotEncoder
from scipy import sparse


use_train_sample = False
train = pd.read_csv('../downloads/train_sample.csv') if use_train_sample else pd.read_csv('../downloads/train.csv')
test = pd.read_csv('../downloads/test.csv')


# ## Feature Engineering
print('train shape:', train.shape)
print('test shape:', test.shape)

train.drop(columns=['attributed_time'], inplace=True)


def extend_datetime_features(df):
    df['click_time'] = pd.to_datetime(df['click_time'])
    df['click_hour'] = df['click_time'].dt.hour
    df['click_minute'] = df['click_time'].dt.minute
    df['click_second'] = df['click_time'].dt.second
    df['click_minute_mod15'] = df['click_minute'] % 15
    df['click_second_mod5'] = df['click_second'] % 5
    return df


train = extend_datetime_features(train)
test = extend_datetime_features(test)

for ft in ['ip', 'app', 'device', 'os', 'channel']:
    stats = train.groupby(ft).agg({'is_attributed': ['size', 'sum']})
    stats.columns = stats.columns.droplevel(0)
    cl_colname, dl_colname, ratio_colname = map(lambda col: col + '_by_' + ft, ['clicks', 'downloads', 'download_ratio'])
    stats.rename(columns={'size': cl_colname, 'sum': dl_colname}, inplace=True)
    stats[ratio_colname] = stats[dl_colname] / stats[cl_colname]

    train = train.merge(stats, how='left', left_on=ft, right_index=True)
    test = test.merge(stats, how='left', left_on=ft, right_index=True)

    del stats
    gc.collect()

train.fillna(0, inplace=True)
test.fillna(0, inplace=True)
gc.collect()

print('train shape:', train.shape)


# ## Preprocessing
cat_cols = ['ip', 'app', 'device', 'os', 'channel', 'click_minute_mod15', 'click_second_mod5']
num_cols = ['click_hour', 'click_minute', 'click_second',
            'clicks_by_ip', 'downloads_by_ip', 'download_ratio_by_ip',
            'clicks_by_app', 'downloads_by_app', 'download_ratio_by_app',
            'clicks_by_device', 'downloads_by_device', 'download_ratio_by_device',
            'clicks_by_os', 'downloads_by_os', 'download_ratio_by_os',
            'clicks_by_channel', 'downloads_by_channel', 'download_ratio_by_channel']
target_col = 'is_attributed'

onehot_encoder = OneHotEncoder()

train_onehot = onehot_encoder.fit_transform(train[cat_cols])
test_onehot = onehot_encoder.transform(test[cat_cols])


X_train = sparse.hstack((train[num_cols], train_onehot))
y_train = train[target_col].values

del train
gc.collect()

print('X_train shape:', X_train.shape)
print('y_train shape:', y_train.shape)


X_test = sparse.hstack((test[num_cols], test_onehot))
del test
gc.collect()
print('X_test shape:', X_test.shape)


sys.mkdir('../scratch') if not os.path.exists('../scratch') else None
sparse.save_npz('../scratch/X_train', X_train)
np.save('../scratch/y_train', y_train)
sparse.save_npz('../scratch/X_test', X_test)
