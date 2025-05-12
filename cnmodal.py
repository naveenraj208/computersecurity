import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.metrics import accuracy_score
from zkp.proof_commitment import create_commitment  # ✅ Import for proof
from blockchain.logger import log_to_blockchain  # ✅ Import blockchain logging

# Define protocol mapping for packet processing
protocol_mapping = {
    0: 'UDP',
    1: 'TCP',
    2: 'IGMP',
    3: 'GGP',
    4: 'IP-in-IP',
    6: 'ICMP',
    7: 'HOPOPT',
    8: 'EGP',
    9: 'IGP',
    17: 'UDP',
    41: 'IPv6',
    50: 'ESP',
    51: 'AH',
    58: 'ICMPv6',
    89: 'OSPF',
    132: 'SCTP',
    253: 'PIM',
    254: 'Reserved',
    255: 'Reserved',
}

# Function to load and preprocess datasets, train model, and save it
def train_model():
    df1 = pd.read_csv('../Preprocesseddataset/balanced_dataset.csv')
    df2 = pd.read_csv('../Preprocesseddataset/file2.csv')
    df_combined = pd.concat([df1, df2])

    label_encoder = LabelEncoder()
    df_combined['label_encoded'] = label_encoder.fit_transform(df_combined['label'])

    X = df_combined.drop(columns=['label', 'label_encoded'])
    y = df_combined['label_encoded']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    base_models = [
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42))
    ]
    final_estimator = MLPClassifier(hidden_layer_sizes=(100, 50), activation='relu', max_iter=500, random_state=42)

    stacking_model = StackingClassifier(estimators=base_models, final_estimator=final_estimator)
    stacking_model.fit(X_train, y_train)

    y_pred = stacking_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Training completed. Model accuracy: {accuracy}")

    joblib.dump(stacking_model, 'trained_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')

    return {"accuracy": accuracy, "message": "Model trained and saved successfully"}

# Load trained model and associated components
def load_model():
    stacking_model = joblib.load('trained_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    return stacking_model, scaler, label_encoder

# Predict from packet and return ZKP-like proof if malicious
def predict_packet(packet):
    stacking_model, scaler, label_encoder = load_model()
    try:
        if hasattr(packet, 'ip'):
            ttl = int(packet.ip.ttl)
            total_len = int(packet.length)
            protocol = int(packet.transport_layer) if str(packet.transport_layer).isdigit() else 0
            t_delta = float(packet.sniff_time.timestamp())

            # Create DataFrame for prediction
            packet_data = pd.DataFrame([[ttl, total_len, protocol, t_delta]],
                                       columns=['ttl', 'total_len', 'protocol', 't_delta'])

            # Scale features
            packet_data_scaled = scaler.transform(packet_data)

            # Predict using model
            prediction = stacking_model.predict(packet_data_scaled)
            label = label_encoder.inverse_transform(prediction)[0]

            result = {
                "status": label,
                "message": "Prediction completed"
            }

            # Add ZKP-like hash proof and blockchain log if malicious
            if label == "malware":
                proof_hash = create_commitment(ttl, total_len, protocol)  # Generate ZKP-like proof
                tx_hash = log_to_blockchain(proof_hash)  # Log proof to blockchain
                result["proof_hash"] = proof_hash  # Add proof hash to the result
                result["tx_hash"] = tx_hash  # Add blockchain transaction hash

            return result
        else:
            return {"error": "Packet does not have an IP layer"}

    except Exception as e:
        return {"error": str(e)}
