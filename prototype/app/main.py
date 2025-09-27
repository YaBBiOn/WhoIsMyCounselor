import streamlit as st
from app.infra.config import MERGED_DIR
from app.core.inference import load_tokenizer_and_model, predict_proba
from app.core.textproc import build_summary
from app.ui.shared import sidebar_env, final_panel, init_session_state, render_reset
from app.ui.student_view import student_panel
from app.ui.teacher_view import teacher_panel

def main():
    init_session_state()

    # 사이드바
    with st.sidebar:
        thr, review_low, strict = sidebar_env()

    # 모델 로딩
    with st.spinner("모델 로딩 중..."):
        model, tok = load_tokenizer_and_model(MERGED_DIR)
    st.success("모델 로딩 완료")

    st.markdown("## Who is my Counsellor?")
    st.write("학생의 진로 상담 내용을 바탕으로 진로 상담 담당 선생님을 추천하는 앱입니다.")

    col_student, col_teacher = st.columns([1, 1])

    with col_student:
        name, topic, detail, length, submit = student_panel()
        if submit:
            if not (name.strip() and topic.strip() and detail.strip()):
                st.error("세 항목을 모두 입력해주세요.")
            elif strict and not (200 <= length <= 300):
                st.error("엄격 모드: step2+3의 총 글자수가 200~300자 범위를 벗어났습니다.")
            else:
                summary = build_summary(name, topic, detail)
                probs = predict_proba([summary], model, tok)[0]
                p0, p1 = float(probs[0]), float(probs[1])  # p0=담임, p1=교과
                label = 1 if p1 >= thr else 0

                st.session_state.update(
                    student_submitted=True,
                    student_name=name.strip(),
                    topic=topic,
                    detail=detail,
                    summary=summary,
                    p0=p0, p1=p1, model_label=label,
                    teacher_decision=None,
                )
                st.success("상담 요청이 전송되었습니다.")

    with col_teacher:
        if not st.session_state["student_submitted"]:
            st.subheader("교사용")
            st.info("학생으로부터 상담 요청이 들어오면 여기가 활성화됩니다.")
        else:
            model_label = teacher_panel(
                summary=st.session_state["summary"],
                p0=st.session_state["p0"],
                p1=st.session_state["p1"],
                thr=thr,
                review_low=review_low,
            )
            st.session_state["model_label"] = model_label

    final_panel(thr=thr, left=review_low)
    render_reset()
