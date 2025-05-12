import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('Preprocesseddataset/balanced_dataset.csv')  # Adjust path if needed
df1, df2 = train_test_split(df, test_size=0.5, random_state=42)

df1.to_csv('datasets/client1_data.csv', index=False)
df2.to_csv('datasets/client2_data.csv', index=False)

print("Datasets split and saved in /datasets folder.")
