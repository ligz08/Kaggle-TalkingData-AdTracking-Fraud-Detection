import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_df_nunique(df: pd.core.frame.DataFrame, cols: list, log_scale=False):
    n_unique = df[cols].nunique()
    sns.set(font_scale=1.2)
    ax = n_unique.plot.bar(log=log_scale)
    ax.set(xlabel='Feature',
           ylabel=('Log of ' if log_scale else '') + 'Unique Count',
           title='Count of unique values per feature')
    for p in ax.patches:
        h = p.get_height()
        ax.annotate(s=str(h), xy=[p.get_x(), h])
    
    return ax


def barplot_value_counts_by_col(df, col=None, ascending_index=None, color=['royalblue'], 
                                xlabel=None, ylabel=None, title=None, **kwargs):
    value_counts = df[col].value_counts() if col else df.value_counts()    # if `col` is not specifies, treat `df` as series
    if ascending_index is not None:
        value_counts.sort_index(ascending=ascending_index, inplace=True)
    ax = value_counts.plot.bar(color=color, **kwargs)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if title: ax.set_title(title)
    return ax