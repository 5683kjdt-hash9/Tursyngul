import json
import re
from datetime import date, datetime

import streamlit as st

import csv
import io

def result_to_txt(result: dict) -> str:
    output = io.StringIO()
    output.write(f"Name: {result['full_name']}\n")
    output.write(f"Date of Birth: {result['date_of_birth']}\n")
    output.write(f"Student ID: {result['student_id']}\n")
    output.write(f"Total Score: {result['total_score']}\n")
    output.write(f"Psychological State: {result['psychological_state']}\n\n")

    for i, ans in enumerate(result["answers"], 1):
        output.write(f"{i}. {ans['question']}\n")
        output.write(f"   Answer: {ans['selected_answer']}\n")
        output.write(f"   Score: {ans['score']}\n\n")

    return output.getvalue()


def result_to_csv(result: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Field", "Value"])
    writer.writerow(["Full Name", result["full_name"]])
    writer.writerow(["Date of Birth", result["date_of_birth"]])
    writer.writerow(["Student ID", result["student_id"]])
    writer.writerow(["Total Score", result["total_score"]])
    writer.writerow(["Psychological State", result["psychological_state"]])
    writer.writerow([])

    writer.writerow(["#", "Question", "Answer", "Score"])
    for i, ans in enumerate(result["answers"], 1):
        writer.writerow([i, ans["question"], ans["selected_answer"], ans["score"]])

    return output.getvalue()

st.set_page_config(
    page_title="Peer comparison avoidance survey",
    page_icon="🧠",
    layout="centered",
)

QUESTIONS = [
    {
        "question": "How often do you measure your success by your own improvement rather than by other people's results?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "When setting goals, how much do you focus on your personal starting point and progress?",
        "options": [
            ("Completely focus on my own progress", 1),
            ("Mostly focus on my own progress", 2),
            ("Focus on both equally", 3),
            ("Mostly compare with others", 4),
            ("Fully compare with others", 5),
        ],
    },
    {
        "question": "How often do you feel satisfied when you improve, even if others perform better?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you keep track of your own growth instead of checking where others stand?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How much does personal progress motivate you even without outside recognition?",
        "options": [
            ("Very strongly", 1),
            ("Strongly", 2),
            ("Moderately", 3),
            ("Slightly", 4),
            ("Not at all", 5),
        ],
    },
    {
        "question": "How often do other people's achievements make you question your own worth?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "When someone around you succeeds, how often can you stay focused on your own path?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you compare your academic or work results with those of your peers?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How often do you feel discouraged after seeing someone else progress faster than you?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How easy is it for you to appreciate others' success without feeling behind?",
        "options": [
            ("Very easy", 1),
            ("Easy", 2),
            ("Neutral", 3),
            ("Difficult", 4),
            ("Very difficult", 5),
        ],
    },
    {
        "question": "How often do social media posts make you feel that you are not doing enough?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How often do you compare your lifestyle or achievements with people you see online?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How well do you manage to remind yourself that what you see online of successful people doesn't show the whole picture?",
        "options": [
            ("Very well", 1),
            ("Well", 2),
            ("Fairly well", 3),
            ("Poorly", 4),
            ("Very poorly", 5),
        ],
    },
    {
        "question": "How often do other people's expectations make you forget your own speed of progress?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How much does it improve your motivation if you avoid comparisons?",
        "options": [
            ("Improves it very strongly", 1),
            ("Improves it strongly", 2),
            ("Improves it somewhat", 3),
            ("Improves it a little", 4),
            ("Does not help", 5),
        ],
    },
    {
        "question": "How often do you celebrate small victories of yours?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you manage to remind yourself that progress may look different for different people?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you lose motivation due to the feeling that other people are ahead of you?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How confident are you in pursuing your goals without needing to outperform others?",
        "options": [
            ("Very confident", 1),
            ("Confident", 2),
            ("Neutral", 3),
            ("Not very confident", 4),
            ("Not confident at all", 5),
        ],
    },
    {
        "question": "How often do you define what success means to you?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #eef4ff 0%, #f8f4ff 45%, #fffaf4 100%);
            }
            .main-card {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(120, 125, 255, 0.14);
                padding: 1.35rem 1.2rem;
                border-radius: 22px;
                box-shadow: 0 18px 40px rgba(71, 85, 160, 0.10);
                margin-bottom: 1rem;
            }
            .hero-title {
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.15;
                margin-bottom: 0.35rem;
                color: #20243a;
            }
            .hero-sub {
                color: #58607a;
                font-size: 1rem;
                margin-bottom: 0;
            }
            .mini-badge {
                display: inline-block;
                padding: 0.28rem 0.7rem;
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(122, 92, 255, 0.14), rgba(40, 170, 255, 0.14));
                color: #4b4f7c;
                font-size: 0.86rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #272b45;
                margin-bottom: 0.4rem;
            }
            .soft-text {
                color: #66708a;
                margin-bottom: 0.6rem;
            }
            .metric-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
                border: 1px solid rgba(90, 105, 210, 0.15);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                margin: 0.3rem 0;
            }
            .question-card {
                background: rgba(255,255,255,0.92);
                border: 1px solid rgba(110, 110, 190, 0.14);
                border-radius: 18px;
                padding: 1rem 1rem 0.4rem 1rem;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )



def validate_name(name: str) -> bool:
    pattern = r"^[A-Za-z\s\-']+$"
    return bool(re.fullmatch(pattern, name.strip()))



def calculate_result(total_score: int) -> str:
    if 20 <= total_score <= 35:
        return "Excellent Personal Focus - strong self-growth mindset, very little unhealthy comparison"
    if 36 <= total_score <= 50:
        return "Healthy Progress Orientation - mostly focused on personal goals with only occasional comparison"
    if 51 <= total_score <= 65:
        return "Mild Comparison Tendency - comparison with others occurs but still able to focus on self-progress"
    if 66 <= total_score <= 80:
        return "Moderate Comparison Strain - comparison begins to impact motivation, confidence, satisfaction"
    if 81 <= total_score <= 90:
        return "High Comparison Pressure - frequent comparison with others occurs with reduced self-focus and increasing strain"
    if 91 <= total_score <= 100:
        return "Critical Comparison Pattern - strong dependency on others' achievements with significant impact on self-esteem and motivation"
    return "Invalid total score"



def build_result() -> dict:
    structured_answers = []
    total_score = 0

    for index, question_data in enumerate(QUESTIONS, start=1):
        selected_text = st.session_state.get(f"q_{index}")
        selected_score = next(score for text, score in question_data["options"] if text == selected_text)
        structured_answers.append(
            {
                "question": question_data["question"],
                "selected_answer": selected_text,
                "score": selected_score,
            }
        )
        total_score += selected_score

    return {
        "full_name": st.session_state["full_name"].strip(),
        "date_of_birth": st.session_state["date_of_birth"].strftime("%Y-%m-%d"),
        "student_id": st.session_state["student_id"].strip(),
        "total_score": total_score,
        "psychological_state": calculate_result(total_score),
        "answers": structured_answers,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }



def reset_survey() -> None:
    st.session_state["survey_started"] = False
    st.session_state["survey_result"] = None
    for key in list(st.session_state.keys()):
        if key.startswith("q_"):
            del st.session_state[key]


inject_styles()

if "survey_started" not in st.session_state:
    st.session_state["survey_started"] = False
if "survey_result" not in st.session_state:
    st.session_state["survey_result"] = None

st.markdown(
    """
    <div class="main-card">
        <div class="mini-badge">Psychological survey</div>
        <div class="hero-title">Peer comparison avoidance </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio("Choose section", ["Take survey", "Load saved JSON"])

if page == "Take survey":
    if st.session_state["survey_result"] is not None:
        result = st.session_state["survey_result"]
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Result summary</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="metric-box"><b>Name:</b> {result['full_name']}</div>
            <div class="metric-box"><b>Date of Birth:</b> {result['date_of_birth']}</div>
            <div class="metric-box"><b>Student ID:</b> {result['student_id']}</div>
            <div class="metric-box"><b>Total Score:</b> {result['total_score']}</div>
            <div class="metric-box"><b>Psychological State:</b> {result['psychological_state']}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Show answers"):
            for idx, answer in enumerate(result["answers"], start=1):
                st.write(f"**{idx}. {answer['question']}**")
                st.write(f"Answer: {answer['selected_answer']}")
                st.write(f"Score: {answer['score']}")

        # --- FORMAT SELECTOR ---
        format_choice = st.selectbox(
            "Choose file format",
            ["JSON", "TXT", "CSV"]
        )

        if format_choice == "JSON":
            data = json.dumps(result, indent=4, ensure_ascii=False)
            file_name = "survey_result.json"
            mime = "application/json"

        elif format_choice == "TXT":
            data = result_to_txt(result)
            file_name = "survey_result.txt"
            mime = "text/plain"

        else:
            data = result_to_csv(result)
            file_name = "survey_result.csv"
            mime = "text/csv"

        col_a, col_b = st.columns(2)

        with col_a:
            st.download_button(
                label=f"Download as {format_choice}",
                data=data,
                file_name=file_name,
                mime=mime,
                use_container_width=True,
            )
        with col_b:
            if st.button("Start new survey", use_container_width=True):
                reset_survey()
                st.rerun()

    elif not st.session_state["survey_started"]:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Step 1 of 2 · Participant information</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="soft-text">Fill in the personal details first. After clicking the button, the questionnaire page will open.</p>',
            unsafe_allow_html=True,
        )

        with st.form("participant_form"):
            full_name = st.text_input("Surname and given name", placeholder="Enter full name")
            date_of_birth = st.date_input(
                "Date of birth",
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                value=None,
                format="YYYY-MM-DD",
            )
            student_id = st.text_input("Student ID", placeholder="Digits only")
            start_clicked = st.form_submit_button("Start questionnaire", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if start_clicked:
            errors = []
            if not full_name.strip() or not validate_name(full_name):
                errors.append("Enter a valid name using only letters, spaces, hyphens, and apostrophes.")
            if date_of_birth is None:
                errors.append("Select a valid date of birth.")
            if not student_id.strip().isdigit():
                errors.append("Student ID must contain digits only.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.session_state["full_name"] = full_name
                st.session_state["date_of_birth"] = date_of_birth
                st.session_state["student_id"] = student_id
                st.session_state["survey_started"] = True
                st.rerun()

    else:
        answered = sum(1 for i in range(1, len(QUESTIONS) + 1) if st.session_state.get(f"q_{i}") is not None)
        progress = answered / len(QUESTIONS)

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Step 2 of 2 · Questionnaire</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="soft-text"><b>Participant:</b> {st.session_state["full_name"]} &nbsp;|&nbsp; <b>Student ID:</b> {st.session_state["student_id"]}</p>',
            unsafe_allow_html=True,
        )
        st.progress(progress)
        st.caption(f"Answered {answered} of {len(QUESTIONS)} questions")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("survey_form"):
            for index, question_data in enumerate(QUESTIONS, start=1):
                st.markdown('<div class="question-card">', unsafe_allow_html=True)
                option_texts = [text for text, _ in question_data["options"]]
                st.radio(
                    f"{index}. {question_data['question']}",
                    option_texts,
                    index=None,
                    key=f"q_{index}",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                back_clicked = st.form_submit_button("Back to personal info", use_container_width=True)
            with col2:
                submitted = st.form_submit_button("Submit survey", use_container_width=True)

        if back_clicked:
            st.session_state["survey_started"] = False
            st.rerun()

        if submitted:
            unanswered = [str(i) for i in range(1, len(QUESTIONS) + 1) if st.session_state.get(f"q_{i}") is None]
            if unanswered:
                st.error("Answer all questions before submitting.")
            else:
                st.session_state["survey_result"] = build_result()
                st.success("Survey submitted successfully.")
                st.rerun()

else:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Load saved questionnaire result</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="soft-text">Upload a JSON result file to view the saved participant data and scores.</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload a JSON result file", type=["json"])
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            st.success("JSON loaded successfully.")
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="metric-box"><b>Name:</b> {data.get('full_name', '-')}</div>
                <div class="metric-box"><b>Date of Birth:</b> {data.get('date_of_birth', '-')}</div>
                <div class="metric-box"><b>Student ID:</b> {data.get('student_id', '-')}</div>
                <div class="metric-box"><b>Total Score:</b> {data.get('total_score', '-')}</div>
                <div class="metric-box"><b>Psychological State:</b> {data.get('psychological_state', '-')}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            answers = data.get("answers", [])
            if answers:
                with st.expander("Show answers"):
                    for idx, answer in enumerate(answers, start=1):
                        st.write(f"**{idx}. {answer.get('question', '')}**")
                        st.write(f"Answer: {answer.get('selected_answer', '')}")
                        st.write(f"Score: {answer.get('score', '')}")
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")
        except Exception as error:
            st.error(f"Error loading file: {error}")
