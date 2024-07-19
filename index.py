import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte

DATABASE = 'test.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/score', methods=['POST'])
def add_score():
    data = request.json
    username = data.get('username')
    score = data.get('score')
    time_saved = data.get('time_saved')
    
    if not all([username, score, time_saved]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scores (username, score, time_saved) VALUES (?, ?, ?)",
            (username, score, time_saved)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": new_id, "message": "Score added successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        leaderboard = cursor.execute("""
            SELECT username, MAX(score) as score, MAX(time_saved) as time_saved
            FROM scores
            GROUP BY username
            ORDER BY score DESC, time_saved DESC
            LIMIT 10
        """).fetchall()
        conn.close()
        return jsonify([dict(row) for row in leaderboard])
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)