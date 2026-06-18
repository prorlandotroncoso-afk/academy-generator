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
OCR_API_KEY = "helloworld"

def extract_text_from_drive_pdf(drive_url):

    try:

        file_id = drive_url.split("/d/")[1].split("/")[0]

        download_url = (
            f"https://drive.google.com/uc?export=download&id={file_id}"
        )

        pdf_response = requests.get(
            download_url,
            timeout=60
        )

        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={
                "file": (
                    "document.pdf",
                    pdf_response.content,
                    "application/pdf"
                )
            },
            data={
                "apikey": OCR_API_KEY,
                "language": "eng"
            },
            timeout=120
        )

        result = response.json()

        if result.get("IsErroredOnProcessing"):
            return "OCR ERROR"

        text = ""

        for page in result.get("ParsedResults", []):

            text += page.get(
                "ParsedText",
                ""
            )

            text += "\n"

        return text

    except Exception as e:

        return f"ERROR OCR: {str(e)}"
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
def get_active_subunit():

    try:

        df = pd.read_csv(SHEET_URL)

        return df.to_string()

    except Exception as e:

        return f"ERROR SHEET: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def home():

    result = ""

    active_data = get_active_subunit()

    print(active_data)

    if request.method == "POST":

        unit = request.form["unit"]

        selected_subunits = request.form.getlist("subunits")

        df = pd.read_csv(SHEET_URL)

        result = ""

        for subunit in selected_subunits:

            match = df[
                (df["UNIT"].astype(str) == str(unit))
                &
                (df["SUBUNIT"].astype(str) == str(subunit))
            ]

            if not match.empty:

                row = match.iloc[0]
                pdf_text = extract_text_from_drive_pdf(
                    row["DRIVE_LINK"]
                )
                result += f"""
UNIT {row['UNIT']}{row['SUBUNIT']}

COURSE_ID: {row['COURSE_ID']}
ACTIVITY_ID: {row['ACTIVITY_ID']}
FINAL_QUIZ_ID: {row['FINAL_QUIZ_ID']}

DRIVE_LINK:
{row['DRIVE_LINK']}

PDF TEXT:

{pdf_text[:3000]}

------------------------------------

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