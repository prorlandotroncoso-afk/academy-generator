from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "No se encontró GROQ_API_KEY en el archivo .env"
    )

client = Groq(api_key=api_key)

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)