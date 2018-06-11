from .HERE import SCRATCH_DIR, DOWNLOADS_DIR
import numpy as np
import pandas as pd
from sklearn.preprocessing import label_binarize
from scipy import sparse
import os

ORIGINAL_FEATURES = ['ip', 'app', 'device', 'os', 'channel']
CAT_COLS = ['ip', 'app', 'device', 'os', 'channel', 'click_minute_mod15', 'click_second_mod5']
NUM_COLS = ['click_hour', 'click_minute', 'click_second', 
            'clicks_by_ip', 'downloads_by_ip', 'download_ratio_by_ip', 
            'clicks_by_app', 'downloads_by_app', 'download_ratio_by_app', 
            'clicks_by_device', 'downloads_by_device', 'download_ratio_by_device', 
            'clicks_by_os', 'downloads_by_os', 'download_ratio_by_os', 
            'clicks_by_channel', 'downloads_by_channel', 'download_ratio_by_channel']
TARGET_COL = 'is_attributed'

def extend_datetime_features(df):
    df['click_time'] = pd.to_datetime(df['click_time'])
    df['click_hour'] = df['click_time'].dt.hour
    df['click_minute'] = df['click_time'].dt.minute
    df['click_second'] = df['click_time'].dt.second
    df['click_minute_mod15'] = df['click_minute'] % 15
    df['click_second_mod5'] = df['click_second'] % 5
    return df


def add_stats_by_feature(df, stats_by_feature):
    for ft in stats_by_feature.keys():
        if ft not in df.columns:
            print('{} not found in dataframe, no merge happens.'.format(ft))
            continue
        df = df.merge(stats_by_feature[ft], how='left', left_on=ft, right_index=True)
    df.fillna({col: 0 for col in stats_by_feature[ft].columns}, inplace=True)
    return df


class Preprocessor(object):
    def __init__(self):
        self.stats_by_ = {}
        self.recurring_ = {}
        self.load_stats_by_feature()
        self.load_recurring_values_in_feature()
    
    def load_stats_by_feature(self):
        for ft in ORIGINAL_FEATURES:
            # For each feature (ip, app, device, etc.) count clicks and downloads grouped by that feature
            # you'll have columns like `clicks_by_ip`, `downloads_by_ip`, `download_ratio_by_ip`, `clicks_by_app`, ...
            csv_file_path = os.path.join(SCRATCH_DIR, 'stats_by_{}.csv'.format(ft))
            
            if not os.path.exists(csv_file_path):
                train = pd.read_csv(os.path.join(DOWNLOADS_DIR, 'train.csv'))
                stats = train.groupby(ft).agg({'is_attributed': ['size', 'sum']})
                stats.columns = stats.columns.droplevel(0)
                cl_colname, dl_colname, ratio_colname = [col + '_by_' + ft for col in
                                                         ['clicks', 'downloads', 'download_ratio']]
                stats.rename(columns={'size': cl_colname, 'sum': dl_colname}, inplace=True)
                stats[ratio_colname] = stats[dl_colname] / stats[cl_colname]

                # Save the stats to csv file in scrach folder
                stats.to_csv()
                self.stats_by_[ft] = stats
            else:
                self.stats_by_[ft] = pd.read_csv(csv_file_path).set_index(ft)
    
    def load_recurring_values_in_feature(self):
        for ft in ORIGINAL_FEATURES:
            is_recurring = self.stats_by_[ft]['downloads_by_' + ft] > 1
            self.recurring_[ft] = set(self.stats_by_[ft].index[is_recurring].tolist())
            # print(len(self.recurring_[ft]), 'recurring', ft)
    
    def onehot_encode_catcols(self, df):
        onehot_ = {}
        for ft in CAT_COLS:
            print('One-hot encode:', ft)
            onehot_[ft] = label_binarize(df[ft],
                                         classes=list(self.recurring_.get(ft) or np.sort(df[ft].unique())),
                                         sparse_output=True)
        onehot = sparse.hstack([onehot_[col] for col in CAT_COLS])
        return onehot

    def transform(self, df):
        """
        
        :param df: DataFrame
        :return: SparseMatrix. Left columns are numerical features, right columns are one-hot encoded categorical 
        features
        """
        df = extend_datetime_features(df)
        df = add_stats_by_feature(df, self.stats_by_)
        onehot = self.onehot_encode_catcols(df)
        X = sparse.hstack((df[NUM_COLS], onehot))
        return X