from flask import Flask, request, jsonify
import supplier_agent
import os
import sqlite3

app = Flask(__name__)

@app.route("/verify_supplier", methods=["POST"])
def verify_supplier():
    data = request.get_json()
    supplier_name = data.get("supplier_name", "New Supplier")
    form_data = data.get("form_data", None)
    result = supplier_agent.initiate_supplier_interview(supplier_name, form_data)
    return jsonify(result)

if __name__ == "__main__":
    # Ensure DB exists
    conn_init = sqlite3.connect("supplier_verification.db")
    c = conn_init.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS supplier_verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT,
            trust_score INTEGER,
            decision TEXT
        )
    """)
    conn_init.commit()
    conn_init.close()
    app.run(debug=True, host='0.0.0.0', port=5000)
