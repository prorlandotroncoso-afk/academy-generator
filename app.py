from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd
import requests

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "No se encontró GROQ_API_KEY en el archivo .env"
    )

client = Groq(api_key=api_key)

app = Flask(__name__)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g6NNANlvTFe5dM9r7jTy1QnGh9aKLXKMcNuMJLYMxrY/export?format=csv&gid=0"
# Cola temporal de quizzes pendientes
QUIZ_QUEUE = []
def get_active_subunit():

    try:

        df = pd.read_csv(SHEET_URL)

        active = df[df["STATUS"] == "ACTIVE"]

        if active.empty:
            return None

        row = active.iloc[0]

        return {
            "unit": str(row["UNIT"]),
            "subunit": str(row["SUBUNIT"]),
            "course_id": int(row["COURSE_ID"]),
            "activity_id": int(row["ACTIVITY_ID"]),
            "final_quiz_id": int(row["FINAL_QUIZ_ID"]),
            "drive_link": str(row["DRIVE_LINK"])
        }

    except Exception as e:

        print("ERROR SHEET:", e)

        return None
UNITS = {

    "1A": {
        "grammar": "be: I and you",
        "vocabulary": "countries",
        "pronunciation": "short forms of be",
        "speaking": "introduce yourself"
    },

    "1B": {
        "grammar": "be: he she it",
        "vocabulary": "jobs",
        "pronunciation": "short forms of be",
        "speaking": "ask and answer about jobs"
    },

    "1C": {
        "grammar": "be: we and they",
        "vocabulary": "nationalities",
        "pronunciation": "short forms of be",
        "speaking": "talk about nationalities"
    },

    "1D": {
        "grammar": "contact information",
        "vocabulary": "personal information",
        "pronunciation": "spelling names",
        "speaking": "ask for and give contact information"
    }

}


@app.route("/", methods=["GET", "POST"])
def home():

    result = ""

    active_data = get_active_subunit()

    print(active_data)

    if request.method == "POST":

        unit = request.form["unit"]

        selected_subunits = request.form.getlist("subunits")

        result = f"""
UNIT SELECTED: {unit}

SUBUNITS:
{selected_subunits}
"""

    return render_template(
        "index.html",
        result=result
    )


# ============================
# API PARA WORDPRESS
# ============================

@app.route("/save_quiz", methods=["POST"])
def save_quiz():

    data = request.get_json()

    QUIZ_QUEUE.append(data)

    return jsonify({
        "success": True,
        "pending": len(QUIZ_QUEUE)
    })


@app.route("/quizzes_pending", methods=["GET"])
def quizzes_pending():

    return jsonify({
        "count": len(QUIZ_QUEUE),
        "quizzes": QUIZ_QUEUE
    })


@app.route("/clear_quizzes", methods=["POST"])
def clear_quizzes():

    QUIZ_QUEUE.clear()

    return jsonify({
        "success": True
    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(debug=True)