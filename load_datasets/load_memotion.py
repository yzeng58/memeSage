import pandas as pd
import os, sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from configs import get_dataset_dir


def load_memotion(binary_classification = False):
    memotion_dir = get_dataset_dir('memotion')
    memotion_labels = pd.read_csv(f'{memotion_dir}/labels.csv')

    humor_mapping = {
        'not_funny': 1,
        'funny': 2,
        'very_funny': 3,
        'hilarious': 4
    }

    # Apply the mapping to create a new column 'humor_level'
    memotion_labels['humor_level'] = memotion_labels['humour'].map(humor_mapping)
    df = memotion_labels[['image_name', 'humor_level', 'text_corrected']]
    df.columns = ['image_name', 'humor_level', 'text']
    df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    df['image_path'] = df['image_name'].apply(lambda img_name: f'{memotion_dir}/images/{img_name}')
    df['humor_level'] = df['humor_level'].astype(int)
    df = df[['image_path', 'text', 'humor_level']]

    if binary_classification:
        # Filter the dataframe to include only rows where humor_level is 1 or 4
        df = df[df['humor_level'].isin([1, 4])]
        df['label'] = df['humor_level'].replace({1:0, 4:1})
        df = df[['image_path', 'text', 'label']].reset_index(drop=True)
    return df

