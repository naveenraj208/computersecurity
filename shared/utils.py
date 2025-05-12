import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def load_data(path):
    df = pd.read_csv(path)
    label_encoder = LabelEncoder()
    df['label'] = label_encoder.fit_transform(df['label'])

    X = df.drop(columns=['label'])
    y = df['label']

    return train_test_split(X, y, test_size=0.2, random_state=42)
