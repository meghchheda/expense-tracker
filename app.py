import os
from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

FILEPATH = "expenses.csv"


def load_expenses():
    if os.path.isfile(FILEPATH):
        df = pd.read_csv(FILEPATH)
        # Ensure correct column types
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["description"] = df["description"].fillna("")
        df["category"] = df["category"].fillna("Uncategorised")
        df["date"] = df["date"].fillna("")
        return df
    return pd.DataFrame(columns=["date", "category", "amount", "description"])


def save_expenses(df):
    df.to_csv(FILEPATH, index=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    df = load_expenses()
    records = df.to_dict(orient="records")
    return jsonify(records)


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    date = data.get("date", "")
    category = data.get("category", "").strip() or "Uncategorised"
    description = data.get("description", "").strip()

    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    df = load_expenses()
    new_row = pd.DataFrame([{
        "date": date,
        "category": category,
        "amount": amount,
        "description": description
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_expenses(df)
    return jsonify({"ok": True})


@app.route("/api/expenses/<int:idx>", methods=["DELETE"])
def delete_expense(idx):
    df = load_expenses()
    if idx < 0 or idx >= len(df):
        return jsonify({"error": "Index out of range"}), 400
    df = df.drop(idx).reset_index(drop=True)
    save_expenses(df)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)