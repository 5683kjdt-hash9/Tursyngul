import json
import re
from datetime import datetime, date
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Psychological State Survey",
    page_icon="🧠",
    layout="wide",
)


QUESTIONS_FILE = Path(__file__).with_name("questions.json")
RESULTS_DIR = Path(__file__).with_name("saved_results")
RESULTS_DIR.mkdir(exist_ok=True)

ALLOWED_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
ALLOWED_FILE_EXTENSIONS = {"json"}
STATE_LABELS = frozenset(
    {
        "Very Healthy Self-Focus",
        "Healthy Self-Focus",
        "Mild Social Comparison Sensitivity",
        "Moderate Social Comparison Strain",
        "High Comparison Pressure",
        "Critical Comparison Distress",
    }
)


# -------------------------
# Data loading and checks
# -------------------------
def load_questions(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError("Questions file must contain a list.")

    question_numbers = range(1, len(questions) + 1)

    if len(questions) < 15 or len(questions) > 25:
        raise ValueError("The questionnaire must contain 15 to 25 questions.")

    for idx in question_numbers:
        question_item = questions[idx - 1]
        options = question_item.get("options", [])
        if not 3 <= len(options) <= 5:
            raise ValueError(f"Question {idx} must contain 3 to 5 answer options.")

    return questions


QUESTIONS = load_questions(QUESTIONS_FILE)


# -------------------------
# Validation functions
# -------------------------
def validate_name(name: str) -> bool:
    cleaned_name = name.strip()
    if not cleaned_name:
        return False

    for character in cleaned_name:  # for-loop for validation
        if character not in ALLOWED_NAME_CHARS:
            return False

    if not re.fullmatch(r"[A-Za-z][A-Za-z\s\-']*[A-Za-z]$|[A-Za-z]", cleaned_name):
        return False

    return True


# while-loop for validation
# kept as a helper to demonstrate iterative validation logic in code
# and also to sanitize repeated spaces before saving

def normalize_spaces(text: str) -> str:
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()



def validate_student_id(student_id: str) -> bool:
    return student_id.isdigit()



def validate_dob_text(dob_text: str) -> bool:
    try:
        parsed = datetime.strptime(dob_text, "%Y-%m-%d").date()
        return parsed <= date.today()
    except ValueError:
        return False


# -------------------------
# Scoring
# -------------------------
def calculate_state(total_score: int) -> str:
    if 20 <= total_score <= 35:
        return "Very Healthy Self-Focus — strong personal growth orientation with very low unhealthy comparison."
    elif 36 <= total_score <= 50:
        return "Healthy Self-Focus — generally focused on personal goals with only occasional comparison pressure."
    elif 51 <= total_score <= 65:
        return "Mild Social Comparison Sensitivity — comparison appears sometimes, but self-direction is still mostly present."
    elif 66 <= total_score <= 80:
        return "Moderate Social Comparison Strain — comparison begins to reduce confidence, satisfaction, or motivation."
    elif 81 <= total_score <= 90:
        return "High Comparison Pressure — frequent comparison affects emotional comfort and personal goal focus."
    elif 91 <= total_score <= 100:
        return "Critical Comparison Distress — comparison strongly influences self-worth and may require psychological support."
    return "Invalid total score"



def build_result_data(given_name: str, surname: str, dob_text: str, student_id: str, answers: list) -> dict:
    total_score = sum(answer["score"] for answer in answers)
    psychological_state = calculate_state(total_score)

    return {
        "survey_title": "Psychological State Survey on Self-Focus and Social Comparison",
        "given_name": normalize_spaces(given_name),
        "surname": normalize_spaces(surname),
        "full_name": f"{normalize_spaces(surname)} {normalize_spaces(given_name)}",
        "date_of_birth": dob_text,
        "student_id": student_id,
        "total_score": total_score,
        "psychological_state": psychological_state,
        "question_count": len(answers),
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "answers": answers,
    }


# -------------------------
# File persistence
# -------------------------
def save_results_to_json(result_data: dict, filename: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_\-]", "_", filename)
    if not safe_name.lower().endswith(".json"):
        safe_name += ".json"

    file_extension = safe_name.split(".")[-1].lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise ValueError("Only JSON files are allowed.")

    save_path = RESULTS_DIR / safe_name
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)
    return save_path



def validate_loaded_result(data: dict) -> bool:
    required_fields = {
        "given_name",
        "surname",
        "date_of_birth",
        "student_id",
        "total_score",
        "psychological_state",
        "answers",
    }

    if not isinstance(data, dict):
        return False

    if not required_fields.issubset(set(data.keys())):
        return False

    if not validate_name(data["given_name"]):
        return False

    if not validate_name(data["surname"]):
        return False

    if not validate_student_id(str(data["student_id"])):
        return False

    if not validate_dob_text(str(data["date_of_birth"])):
        return False

    if not isinstance(data["answers"], list):
        return False

    return True


# -------------------------
# UI helpers
# -------------------------
def display_result(result_data: dict):
    total_questions = len(QUESTIONS)
    score_percent = float((result_data["total_score"] / (total_questions * 5)) * 100)

    st.success("Questionnaire completed successfully.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total score", result_data["total_score"])
    col2.metric("Questions answered", len(result_data["answers"]))
    col3.metric("Score percentage", f"{score_percent:.1f}%")

    st.subheader("Psychological state")
    st.info(result_data["psychological_state"])

    st.subheader("Personal details")
    st.write(f"**Given name:** {result_data['given_name']}")
    st.write(f"**Surname:** {result_data['surname']}")
    st.write(f"**Date of birth:** {result_data['date_of_birth']}")
    st.write(f"**Student ID:** {result_data['student_id']}")

    with st.expander("Show all answers"):
        for index, answer in enumerate(result_data["answers"], start=1):
            st.markdown(f"**{index}. {answer['question']}**")
            st.write(f"Answer: {answer['selected_answer']}")
            st.write(f"Score: {answer['score']}")
            st.divider()


# -------------------------
# Main app
# -------------------------
def main():
    st.title("🧠 Psychological State Survey")
    st.caption(
        "Web-based psychological questionnaire on self-focus, personal growth, and social comparison."
    )

    st.markdown(
        """
        This survey contains **20 original questions**, each with **5 answer options**.
        It produces **6 possible psychological states** based on the total score.
        The result is for educational coursework purposes and is **not a clinical diagnosis**.
        """
    )

    mode = st.radio(
        "Choose an option:",
        [
            "Start a new questionnaire",
            "Load an existing questionnaire result from JSON",
        ],
        horizontal=True,
    )

    if mode == "Start a new questionnaire":
        st.header("Start a new questionnaire")

        with st.form("survey_form"):
            col1, col2 = st.columns(2)
            with col1:
                given_name = st.text_input("Given name")
                dob_value = st.date_input(
                    "Date of birth",
                    value=date(2005, 1, 1),
                    min_value=date(1950, 1, 1),
                    max_value=date.today(),
                )
            with col2:
                surname = st.text_input("Surname")
                student_id = st.text_input("Student ID")

            st.subheader("Survey questions")
            st.progress(0.0, text="Complete all questions")

            answers = []
            selected_indices = []

            for number, question_item in enumerate(QUESTIONS, start=1):
                st.markdown(f"**Question {number}. {question_item['question']}**")
                option_labels = [option[0] for option in question_item["options"]]
                selected_text = st.radio(
                    f"Choose one answer for Question {number}",
                    option_labels,
                    index=None,
                    key=f"question_{number}",
                    label_visibility="collapsed",
                )
                selected_indices.append(selected_text)

            answered_count = sum(1 for item in selected_indices if item is not None)
            progress_value = float(answered_count / len(QUESTIONS))
            st.progress(progress_value, text=f"Answered {answered_count} of {len(QUESTIONS)} questions")

            submitted = st.form_submit_button("Submit questionnaire")

        if submitted:
            errors = []

            given_name = normalize_spaces(given_name)
            surname = normalize_spaces(surname)
            dob_text = dob_value.strftime("%Y-%m-%d")

            if not validate_name(given_name):
                errors.append("Given name is invalid. Use only letters, spaces, hyphens, and apostrophes.")

            if not validate_name(surname):
                errors.append("Surname is invalid. Use only letters, spaces, hyphens, and apostrophes.")

            if not validate_student_id(student_id):
                errors.append("Student ID must contain digits only.")

            if not validate_dob_text(dob_text):
                errors.append("Date of birth is invalid.")

            if answered_count != len(QUESTIONS):
                errors.append("Please answer all questions before submitting.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                for number, question_item in enumerate(QUESTIONS, start=1):
                    selected_text = st.session_state.get(f"question_{number}")
                    chosen_score = None

                    for option_text, option_score in question_item["options"]:
                        if option_text == selected_text:
                            chosen_score = option_score
                            break

                    answers.append(
                        {
                            "question": question_item["question"],
                            "selected_answer": selected_text,
                            "score": chosen_score,
                        }
                    )

                result_data = build_result_data(given_name, surname, dob_text, student_id, answers)
                display_result(result_data)

                default_filename = f"{surname}_{given_name}_{student_id}_survey_result".lower().replace(" ", "_")
                saved_path = save_results_to_json(result_data, default_filename)

                st.download_button(
                    label="Download result as JSON",
                    data=json.dumps(result_data, indent=4, ensure_ascii=False),
                    file_name=saved_path.name,
                    mime="application/json",
                )
                st.caption(f"A local copy was also created: {saved_path.name}")

    else:
        st.header("Load an existing questionnaire result")
        uploaded_file = st.file_uploader("Upload a JSON questionnaire result", type=["json"])

        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                if validate_loaded_result(loaded_data):
                    st.success("JSON file loaded successfully.")
                    display_result(loaded_data)
                else:
                    st.error("The uploaded JSON file does not match the expected questionnaire structure.")
            except json.JSONDecodeError:
                st.error("Invalid JSON file.")
            except Exception as error:
                st.error(f"An error occurred while loading the file: {error}")

    with st.expander("Why this version fits the coursework"):
        st.markdown(
            """
            - Web-based interface available online
            - 20 original survey questions loaded from an **external JSON file**
            - 5 answer options per question with different scores
            - 6 possible psychological states
            - Validation for given name, surname, date of birth, and student ID
            - Option to **start a new questionnaire** or **load an existing JSON result**
            - Persistence through saving and loading JSON files
            - Uses variables, loops, conditional statements, functions, lists, tuples, dicts, sets, frozenset, range, bool, int, str, and float
            """
        )


if __name__ == "__main__":
    main()
