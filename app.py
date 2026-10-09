import os
import pickle

import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Form field -> column name the random forest was trained on.
FEATURES = {
    "cylinders": "cylinders",
    "displacement": "displacement",
    "horsepower": "horsepower",
    "weight": "weight",
    "acceleration": "acceleration",
    "modelYear": "model year",
    "origin": "origin",
}

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)


@app.route("/")
def home():
    return render_template("finalweb.html")


@app.route("/Result", methods=["POST"])
def result():
    try:
        row = [float(request.form[field]) for field in FEATURES]
    except (KeyError, ValueError):
        return render_template("finalweb.html", resultText="Please enter a number in every field."), 400

    X = pd.DataFrame([row], columns=list(FEATURES.values()))
    output = model.predict(X)[0]
    return render_template("finalweb.html", resultText="The mpg prediction is: {:.2f}".format(output))


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
