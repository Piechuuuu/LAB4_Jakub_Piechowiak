import os
from flask import Flask, request, jsonify
import joblib
import numpy as np
import redis

app = Flask(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = None
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
except Exception:
    r = None

model = None

def load_model():
    global model
    model = joblib.load(MODEL_PATH)

try:
    load_model()
except Exception as e:
    app.logger.exception(f"Failed to load model: {e}")

@app.get("/health")
def health():
    return jsonify(status="ok", redis=bool(r))

@app.post("/predict")
def predict():
    """
    Oczekuje JSON:
    {
      "features": [1.2, 3.4, 5.6, 7.8]
    }
    """
    data = request.get_json(silent=True) or {}
    features = data.get("features", None)
    if model is None:
        return jsonify(error="Model not loaded"), 500

    if features is None:
        return jsonify(error="Missing 'features' in JSON body"), 400

    try:
        X = np.array(features, dtype=float).reshape(1, -1)
        y_pred = model.predict(X)
        result = {"prediction": float(y_pred[0]) if np.isscalar(y_pred[0]) else y_pred[0]}
    except Exception as e:
        return jsonify(error=str(e)), 400

    # zapis do redis (opcjonalny)
    if r:
        try:
            r.incr("predict_calls")
        except Exception:
            pass

    return jsonify(result)

if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5000, debug=True)