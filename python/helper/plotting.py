import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_df_nunique(df: pd.core.frame.DataFrame, cols: list, log=False):
    n_unique = df[cols].nunique()
    sns.set(font_scale=1.2)
    ax = n_unique.plot.bar(log=log)
    ax.set(xlabel='Feature', 
           ylabel=('Log of ' if log else '')+'Unique Count',
           title='Count of unique values per feature')
    for p in ax.patches:
        h = p.get_height()
        ax.annotate(s=str(h), xy=[p.get_x(), h])
    
    return ax