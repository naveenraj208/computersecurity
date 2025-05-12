from flask import Flask, jsonify, request, Response
from cnmodal import train_model, predict_packet
from zkp.proof_commitment import verify_commitment
import pyshark
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Malware Detection API!"

# Train model route
@app.route('/train-model', methods=['GET'])
def train():
    try:
        result = train_model()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

# Live packet capture and prediction route
@app.route('/start-capture', methods=['GET'])
def start_capture():
    def stream_packets():
        try:
            capture = pyshark.LiveCapture(interface='en0')  # change to your active interface
            for packet in capture.sniff_continuously():
                result = predict_packet(packet)
                yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_packets(), mimetype='text/event-stream')

# ZKP verification route
@app.route('/verify-proof', methods=['POST'])
def verify_proof():
    try:
        data = request.get_json()
        ttl = int(data["ttl"])
        length = int(data["length"])
        protocol = int(data["protocol"])
        given_hash = data["proof"]

        is_valid = verify_commitment(ttl, length, protocol, given_hash)
        return jsonify({"valid": is_valid})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
