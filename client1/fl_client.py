import flwr as fl
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load local data (update file path for client2)
data = pd.read_csv("../datasets/client2_data.csv")  # ← CHANGE to client2_data.csv for other client
X = data.drop("label", axis=1)
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()

class MalwareClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return []  # No parameters to share for RandomForest

    def fit(self, parameters, config):
        model.fit(X_train, y_train)
        return [], len(X_train), {}

    def evaluate(self, parameters, config):
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Client accuracy: {acc}")
        return float(acc), len(X_test), {"accuracy": acc}

if __name__ == "__main__":
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=MalwareClient())
