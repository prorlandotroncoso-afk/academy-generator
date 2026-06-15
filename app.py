from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import requests
import io
import os
import pandas as pd

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


def extract_text_from_drive_pdf(drive_url):

    try:

        file_id = drive_url.split("/d/")[1].split("/")[0]

        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        response = requests.get(download_url, timeout=30)

        pdf_bytes = response.content

        # 🔥 convertir PDF a imágenes
        images = convert_from_bytes(pdf_bytes)

        text = ""

        for img in images:

            page_text = pytesseract.image_to_string(img)

            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception as e:

        return f"ERROR OCR: {str(e)}"

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

    if active_data:

        pdf_text = extract_text_from_drive_pdf(
        active_data['drive_link']
    )

    result = f"""
ACTIVE FOUND

UNIT: {active_data['unit']}
SUBUNIT: {active_data['subunit']}

COURSE_ID: {active_data['course_id']}
ACTIVITY_ID: {active_data['activity_id']}
FINAL_QUIZ_ID: {active_data['final_quiz_id']}

========== PDF TEXT ==========

{pdf_text[:5000]}
"""

    if request.method == "POST":

        unit = request.form["unit"]

        data = UNITS[unit]

        prompt = f"""
You are an expert LearnPress quiz creator.

Generate a quiz for UNIT {unit}.

Grammar:
{data['grammar']}

Vocabulary:
{data['vocabulary']}

Pronunciation:
{data['pronunciation']}

Speaking:
{data['speaking']}

IMPORTANT RULES:

1. Generate EXACTLY 20 questions.

2. Distribution:
- Grammar: 8 questions
- Vocabulary: 6 questions
- Usage/Speaking: 4 questions
- Pronunciation: 2 questions

3. Use ONLY these question types:
- Multiple Choice
- Fill in the Blank
- True/False
- Matching
- Sentence Order

4. DO NOT create:
- Open speaking questions
- Subjective questions
- Questions requiring teacher correction
- Free writing tasks

5. Every question MUST be automatically gradable.

6. Use a balanced mix of question types.

7. Follow this output format exactly:

QUESTION TYPE:
CATEGORY:
QUESTION:
OPTIONS:
CORRECT ANSWER:

Example:

QUESTION TYPE: Multiple Choice
CATEGORY: Grammar
QUESTION: He ___ a teacher.
OPTIONS:
A) am
B) is
C) are
CORRECT ANSWER: B

Return only the quiz.
No introduction.
No explanations.
"""

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response.choices[0].message.content

        except Exception as e:

            result = f"ERROR: {str(e)}"

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