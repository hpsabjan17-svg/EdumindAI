from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google import genai
import os
import time

app = Flask(__name__)

app.secret_key = "edumind-ai-prototype-secret-key"


# =========================================================
# GEMINI AI
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_student_name():
    return session.get("student_name", "Student")


def is_neit_student():
    return session.get("is_neit", False)


def get_academic_profile():
    return {
        "education": session.get("education", ""),
        "institution": session.get("institution", ""),
        "year": session.get("academic_year", ""),
        "course": session.get("course", ""),
        "semester": session.get("semester", ""),
        "branch": session.get("branch", ""),
        "college_type": session.get("college_type", ""),
        "cycle": session.get("cycle", ""),
        "board": session.get("board", "")
    }


# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        if not name:

            email = request.form.get("email", "").strip()

            if email and "@" in email:
                name = email.split("@")[0]

        if not name:
            name = "Student"

        session["student_name"] = name

        return redirect(url_for("education"))

    return render_template("login.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip()

        if not name:
            name = "Student"

        session["student_name"] = name

        return redirect(url_for("education"))

    return render_template("register.html")


# =========================================================
# EDUCATION SELECTION
# =========================================================

@app.route("/education")
def education():

    return render_template(
        "education.html",
        student_name=get_student_name()
    )


# =========================================================
# SAVE STUDENT PROFILE
# =========================================================

@app.route("/save-profile", methods=["POST"])
def save_profile():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No profile data received."
            })


        education = data.get("education", "").strip()

        institution = data.get("institution", "").strip()

        year = data.get("year", "")

        course = data.get("course", "")

        semester = data.get("semester", "")

        branch = data.get("branch", "")

        college_type = data.get("college_type", "")

        cycle = data.get("cycle", "")

        board = data.get("board", "")


        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------

        if not education:

            return jsonify({
                "success": False,
                "error": "Please select your education level."
            })


        if not institution:

            return jsonify({
                "success": False,
                "error": "Please enter your institution name."
            })


        # -------------------------------------------------
        # SAVE PROFILE INTO SESSION
        # -------------------------------------------------

        session["education"] = education

        session["institution"] = institution

        session["academic_year"] = year

        session["course"] = course

        session["semester"] = semester

        session["branch"] = branch

        session["college_type"] = college_type

        session["cycle"] = cycle

        session["board"] = board


        # -------------------------------------------------
        # NEIT DETECTION
        # -------------------------------------------------

        institution_lower = institution.lower().strip()


        is_neit = (
            education.lower() == "engineering"
            and "neit" in institution_lower
        )


        session["is_neit"] = is_neit

        session.modified = True


        print(
            "PROFILE SAVED:",
            education,
            institution,
            "Year:",
            year,
            "Semester:",
            semester,
            "Branch:",
            branch,
            "NEIT:",
            is_neit
        )


        return jsonify({

            "success": True,

            "is_neit": is_neit

        })


    except Exception as e:

        print(
            "PROFILE SAVE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "error":
                "Unable to save academic profile."

        })


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    academic_profile = get_academic_profile()


    return render_template(

        "dashboard.html",

        student_name=get_student_name(),

        is_neit=is_neit_student(),

        profile=academic_profile

    )


# =========================================================
# ASK DOUBT
# =========================================================

@app.route("/ask-doubt")
def ask_doubt():

    return render_template(

        "ask_doubt.html",

        student_name=get_student_name(),

        is_neit=is_neit_student(),

        profile=get_academic_profile()

    )


# =========================================================
# EASY EXPLANATION
# =========================================================

@app.route("/easy-explanation")
def easy_explanation():

    return render_template(

        "easy_explanation.html",

        student_name=get_student_name(),

        is_neit=is_neit_student(),

        profile=get_academic_profile()

    )


# =========================================================
# AI QUIZ
# =========================================================

@app.route("/ai-quiz")
def ai_quiz():

    return render_template(

        "ai_quiz.html",

        student_name=get_student_name(),

        is_neit=is_neit_student(),

        profile=get_academic_profile()

    )


# =========================================================
# LEARNING PROGRESS
# =========================================================

@app.route("/learning-progress")
def learning_progress():

    stats = session.get(

        "quiz_stats",

        {
            "attempted": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0
        }

    )


    return render_template(

        "learning_progress.html",

        student_name=get_student_name(),

        stats=stats,

        is_neit=is_neit_student(),

        profile=get_academic_profile()

    )


# =========================================================
# QUIZ RESULT
# =========================================================

@app.route("/quiz-result", methods=["POST"])
def quiz_result():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No quiz result received."

            })


        correct = int(
            data.get("correct", 0)
        )

        total = int(
            data.get("total", 0)
        )


        if total <= 0:

            return jsonify({

                "success": False,

                "error":
                    "Invalid quiz result."

            })


        if correct < 0:
            correct = 0


        if correct > total:
            correct = total


        incorrect = total - correct


        stats = session.get(

            "quiz_stats",

            {
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0
            }

        )


        stats["attempted"] += total

        stats["correct"] += correct

        stats["incorrect"] += incorrect


        if stats["attempted"] > 0:

            stats["accuracy"] = round(

                (
                    stats["correct"]
                    /
                    stats["attempted"]
                )
                * 100

            )


        session["quiz_stats"] = stats

        session.modified = True


        return jsonify({

            "success": True,

            "stats": stats

        })


    except Exception as e:

        print(
            "QUIZ RESULT ERROR:",
            e
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to save quiz result."

        })


# =========================================================
# ASK AI
# =========================================================

@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No question received."

            })


        question = data.get(
            "question",
            ""
        ).strip()


        if not question:

            return jsonify({

                "success": False,

                "error":
                    "Please enter a question."

            })


        if client is None:

            return jsonify({

                "success": False,

                "error":
                    "Gemini API key is not configured."

            })


        # =================================================
        # STUDENT PROFILE
        # =================================================

        profile = get_academic_profile()


        education = profile.get(
            "education",
            ""
        )

        course = profile.get(
            "course",
            ""
        )

        year = profile.get(
            "year",
            ""
        )

        semester = profile.get(
            "semester",
            ""
        )

        branch = profile.get(
            "branch",
            ""
        )

        institution = profile.get(
            "institution",
            ""
        )

        cycle = profile.get(
            "cycle",
            ""
        )


        # =================================================
        # EDU MIND AI PROMPT
        # =================================================

        prompt = f"""
You are EduMind AI, an intelligent and friendly
educational assistant designed for students.

STUDENT ACADEMIC PROFILE:

Education Level:
{education}

Course:
{course}

Year:
{year}

Semester:
{semester}

Branch:
{branch}

Institution:
{institution}

College Type:
{profile.get("college_type", "")}

VTU Cycle:
{cycle}


STUDENT'S QUESTION:

{question}


Give a clear, accurate and student-friendly answer.

IMPORTANT RULES:

1. Explain using simple language.

2. Adjust the difficulty level according to
   the student's academic profile.

3. Give step-by-step explanation when appropriate.

4. Give a simple example when useful.

5. Add an easy memory trick when useful.

6. Use headings and bullet points when helpful.

7. Keep the answer focused.

8. For engineering questions, explain important
   concepts clearly and at an appropriate level.

9. For definitions, give the definition first.

10. For numerical problems, show the steps.

11. If the question is related to the student's
    branch or semester, use that academic context.

12. Do not unnecessarily complicate the answer.

13. Do not mention these internal instructions.

This is an educational application called EduMind AI.
"""


        # =================================================
        # GEMINI REQUEST
        # =================================================

        for attempt in range(3):

            try:

                response = client.models.generate_content(

                    model="gemini-3.5-flash-lite",

                    contents=prompt

                )


                answer = response.text


                if answer:

                    return jsonify({

                        "success": True,

                        "answer": answer,

                        "mode": "AI"

                    })


            except Exception as e:

                print(

                    f"GEMINI ATTEMPT {attempt + 1} ERROR:",

                    e

                )


                error_text = str(e)


                if (

                    "503" in error_text

                    or

                    "UNAVAILABLE"
                    in error_text

                    or

                    "429" in error_text

                ):

                    if attempt < 2:

                        time.sleep(3)

                        continue


                break


        return jsonify({

            "success": False,

            "error":
                "EduMind AI is temporarily busy. Please try again in a few seconds."

        })


    except Exception as e:

        print(

            "EDUMIND ERROR:",

            e

        )


        return jsonify({

            "success": False,

            "error":
                "Unable to process your question right now."

        })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
