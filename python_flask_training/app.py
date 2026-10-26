
# from flask import Flask

# app = Flask(__name__)


# @app.route("/")
# def home():
#     return "Welcome to Python Web Development!"


# if __name__ == "__main__":
#     app.run(debug=True)



# This is to render the template of the index.html
# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)

# This to make different URLs display different pages or messages.
# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/about")
# def about():
#     return "<h1>About Us</h1><p>This website was built using Python and Flask.</p>"

# @app.route("/contact")
# def contact():
#     return "<h1>Contact Us</h1><p>Contact us for more information.</p>"

# @app.route("/assignments")
# def assignments():
#     assignment_list = [
#         {
#             "title": "Build a Flask Website",
#             "due_date": "20 October 2026",
#             "status": "Pending"
#         },
#         {
#             "title": "Python Functions Exercise",
#             "due_date": "18 October 2026",
#             "status": "Submitted"
#         },
#         {
#             "title": "HTML and CSS Practice",
#             "due_date": "22 October 2026",
#             "status": "Pending"
#         }
#     ]

#     return render_template(
#         "assignments.html",
#         assignments=assignment_list
#     )

# if __name__ == "__main__":
#     app.run(debug=True)



# from flask import Flask, render_template, request, redirect, url_for

# app = Flask(__name__)

# # Store assignment records while the application is running
# assignment_list = [
#     {
#         "title": "Build a Flask Website",
#         "due_date": "2026-10-20",
#         "status": "Pending"
#     },
#     {
#         "title": "Python Functions Exercise",
#         "due_date": "2026-10-18",
#         "status": "Submitted"
#     },
#     {
#         "title": "HTML and CSS Practice",
#         "due_date": "2026-10-22",
#         "status": "Pending"
#     }
# ]


# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/about")
# def about():
#     return "<h1>About Us</h1>"


# @app.route("/contact")
# def contact():
#     return "<h1>Contact Us</h1>"


# @app.route("/assignments", methods=["GET", "POST"])
# def assignments():

#     error = None

#     if request.method == "POST":

#         title = request.form.get("title", "").strip()
#         due_date = request.form.get("due_date", "").strip()

#         if not title or not due_date:
#             error = "Please enter an assignment title and due date."

#         else:
#             new_assignment = {
#                 "title": title,
#                 "due_date": due_date,
#                 "status": "Pending"
#             }

#             assignment_list.append(new_assignment)

#             return redirect(url_for("assignments"))

#     return render_template(
#         "assignments.html",
#         assignments=assignment_list,
#         error=error
#     )


# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection, init_db

# Adding new imports (update app.py) for the AI chat feature
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=api_key)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return "<h1>About Us</h1>"


@app.route("/contact")
def contact():
    return "<h1>Contact Us</h1>"


@app.route("/assignments", methods=["GET", "POST"])
def assignments():
    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due_date = request.form.get("due_date", "").strip()

        if not title or not due_date:
            error = "Please enter an assignment title and due date."
        else:
            connection = get_db_connection()

            connection.execute(
                "INSERT INTO assignments (title, due_date, status) VALUES (?, ?, ?)",
                (title, due_date, "Pending")
            )

            connection.commit()
            connection.close()
            

            return redirect(url_for("assignments"))

    connection = get_db_connection()

    assignment_list = connection.execute(
        "SELECT * FROM assignments ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "assignments.html",
        assignments=assignment_list,
        error=error
    )



@app.route("/assignments/<int:assignment_id>/edit",
           methods=["GET", "POST"])
def edit_assignment(assignment_id):

    connection = get_db_connection()

    assignment = connection.execute(
        "SELECT * FROM assignments WHERE id = ?",
        (assignment_id,)
    ).fetchone()

    connection.close()

    if assignment is None:
        return "Assignment not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "").strip()

        if not title or not due_date:
            return "Title and due date are required.", 400

        if status not in ["Pending", "Submitted"]:
            return "Invalid assignment status.", 400

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE assignments
            SET title = ?, due_date = ?, status = ?
            WHERE id = ?
            """,
            (title, due_date, status, assignment_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("assignments"))

    return render_template(
        "edit_assignment.html",
        assignment=assignment
    )

@app.route("/assignments/<int:assignment_id>/delete",
           methods=["POST"])
def delete_assignment(assignment_id):

    connection = get_db_connection()

    assignment = connection.execute(
        "SELECT id FROM assignments WHERE id = ?",
        (assignment_id,)
    ).fetchone()

    if assignment is None:
        connection.close()
        return "Assignment not found", 404

    connection.execute(
        "DELETE FROM assignments WHERE id = ?",
        (assignment_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("assignments"))


# Below is a placeholder for the demo AI chat feature.

# @app.route("/chat", methods=["GET", "POST"])
# def ai_chat():
#     question = ""
#     answer = ""

#     if request.method == "POST":
#         question = request.form.get("message", "").strip()

#         if question:
#             answer = (
#                 "Thank you for your question: "
#                 + question
#                 + ". This is a demo response. "
#                 "A real AI model will be connected next."
#             )

#     return render_template(
#         "ai_chat.html",
#         question=question,
#         answer=answer
#     )


# Below is a placeholder for the AI chat feature.

@app.route("/chat", methods=["GET", "POST"])
def ai_chat():
    question = ""
    answer = ""

    if request.method == "POST":
        question = request.form.get("message", "").strip()

        if question:
            try:
                response = client.models.generate_content(
                    # model="gemini-3.8-flash",
                    model="gemini-3.6-flash",
                    contents=question,
                    config={
                        "system_instruction": (
                            "You are a friendly, helpful, and knowledgeable AI assistant. "
                                "Answer questions on a wide range of subjects, including "
                                "education, science, mathematics, history, technology, "
                                "business, health, programming, and everyday life. "
                                "Explain difficult concepts in simple language. "
                                "When appropriate, provide examples and step-by-step guidance. "
                                "When asked for code, provide a complete example and explain "
                                "how it works. If you are uncertain about something, say so "
                                "rather than inventing facts. Keep answers relevant to the "
                                "user's question and aim to answer it completely."
                                "You are a friendly and patient programming tutor "
                                "helping beginner students learn Python, Flask, HTML, "
                                "databases, and programming. Answer the student's entire "
                                "question clearly and completely. Explain concepts "
                                "step by step using simple language and practical examples. "
                                "When code is requested, provide a complete working example "
                                "and explain how it works. Do not stop in the middle of "
                                "a sentence, explanation, or code block. Keep answers "
                                "focused and suitable for classroom learning."
                        ),
                        "max_output_tokens": 3500,
                    },
                )

                answer = response.text or (
                    "Sorry, the AI did not return a text response."
                )

            except Exception:
                app.logger.exception("Gemini API request failed")
                answer = (
                    "Sorry, I could not get an AI response. "
                    "Please check the Flask terminal for details."
                )

    return render_template(
        "ai_chat.html",
        question=question,
        answer=answer
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

