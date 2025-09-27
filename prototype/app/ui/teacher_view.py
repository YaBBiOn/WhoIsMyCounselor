import streamlit as st
import numpy as np
from datetime import datetime
from app.infra.config import LABEL_NAMES, TEACHER_MESSAGE_MAX_LEN, DEFAULT_TEACHER_MESSAGE

def teacher_panel(summary: str, p0: float, p1: float, thr: float, review_low=None) -> int:
    st.subheader("교사용")

    st.markdown(f"**student_name:** {st.session_state.get('student_name','')}")
    with st.expander("step2+3 내용 확인", expanded=True):
        st.write(summary)

    # 판정과 관련된 숫자들 조정
    thr = float(thr)
    review_low = float(review_low) if review_low is not None else thr
    thr = round(thr, 3)
    review_low = round(float(np.clip(review_low, 0.0, thr)), 3)

    # 라벨 판정 및 리뷰 밴드 설정
    label = 1 if p1 >= thr else 0
    in_review_band = (review_low < thr) and (review_low <= p1 < thr)

    if in_review_band:
        route = "review" # 리뷰 밴드 안에 있을 경우
    elif label == 1:
        route = "auto_1"  # 교과 자동
    else:
        route = "auto_0"  # 담임 자동

    # --- 표시 ---
    st.markdown("---")
    st.write(f"**모델 판정 :** {LABEL_NAMES[label]}")
    st.write(
        f"- p0(담임): {p0:.3f} | p1(교과): {p1:.3f} | "
        f"기준점(thr): {thr:.3f} | 리뷰하한(low): {review_low:.3f}"
    )

    if route == "review":
        # 리뷰 밴드에 들어왔으면 반대 라벨 가능성을 보여주면서 리뷰 권고
        alt_label = 1 - label  
        st.warning(
            "이 사례는 **확인 필요 범위**에 속합니다. "
            f"**{LABEL_NAMES[alt_label]}** 가능성도 함께 검토해 주세요."
        )
    elif route == "auto_1":
        st.info("**권고(자동): 전문가 / 교과 담당 교사**")
    else:
        st.info("**권고(자동): 담임 / 진로 교사**")

    # 교사 메시지 입력 (미입력시 기본 문구 전송)
    st.markdown("### 학생에게 보내는 메시지")
    message = st.text_area(
        f"선택 입력 (최대 {TEACHER_MESSAGE_MAX_LEN}자)",
        key="teacher_message_draft",
        height=100,
        help="미입력 시 기본 문구가 전송됩니다."
    )
    msg_len = len((message or "").strip())
    st.caption(f"현재 글자수: {msg_len} / {TEACHER_MESSAGE_MAX_LEN}")
    final_msg = (message or "").strip() or DEFAULT_TEACHER_MESSAGE
    st.session_state["teacher_message"] = final_msg
    st.session_state["message_sent"] = True

    # 최종 선택 (클릭과 함께 교사 메시지도 함께 전송됨)
    c1, c2 = st.columns(2)

    def _finalize(decision: int):
        # 메시지가 너무 길면 한번 막아줌
        if msg_len > TEACHER_MESSAGE_MAX_LEN:
            st.error(f"메시지는 {TEACHER_MESSAGE_MAX_LEN}자 이내여야 합니다.")
            return
        final_msg = (message or "").strip() or DEFAULT_TEACHER_MESSAGE
        st.session_state["teacher_decision"] = decision
        st.session_state["teacher_message"] = final_msg
        st.session_state["message_sent"] = True
        st.session_state["sent_at"] = datetime.now().isoformat(timespec="seconds") # 향후 앱 고도화를 위해 추가
        st.success("최종 결정과 메시지를 전송했습니다.")

    if c1.button("최종 결정: 담임 / 진로 교사", use_container_width=True):
        _finalize(0)
    if c2.button("최종 결정: 전문가 / 교과 담당 교사", use_container_width=True):
        _finalize(1)

    return label
