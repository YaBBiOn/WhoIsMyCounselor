import streamlit as st
import numpy as np
from app.infra.config import PRESET_THRESHOLDS, LABEL_NAMES,  DEFAULT_TEACHER_MESSAGE


def sidebar_env():
    st.subheader("환경설정")
    mode = st.selectbox("설정 모드 선택", ["간편 설정", "세부 설정"], index=0)

    if mode == "간편 설정":
        st.caption("선생님의 담당을 알려주세요. 선택 결과에 따라 분류 결과가 달라집니다.")
        pick = st.radio("담당 선택", list(PRESET_THRESHOLDS.keys()), index=0)

        # 분류 기준점(thr)
        thr = float(PRESET_THRESHOLDS[pick])

        # 절대 하한(review_low) 사용: 필요에 맞게 매핑
        # (담임교사면 0.31, 그 외 0.21)
        review_low = 0.31 if pick == "담임교사" else 0.21

        # 리뷰 밴드 : 하한은 항상 [0, thr]로 설정
        review_low = float(np.clip(review_low, 0.0, thr))

        strict = st.checkbox("글자수 규칙 엄격 적용 (200~300자)", value=False)
        return thr, review_low, strict

    # 세부 설정(커스텀)
    st.caption("1) 분류 기준점을 정해주세요. (p1이 이 값 이상이면 '교과')")
    thr = float(st.slider("분류 기준점 (p1)", 0.0, 1.0, 0.33, 0.01))

    st.caption("2) 확인 필요 범위(리뷰 밴드)의 **절대 하한**을 지정하세요. "
                "리뷰 밴드는 [하한, 기준점) 구간입니다.")
    
    # 기본값은 진로교사 리뷰밴드인 0.21을 가지고 옴. 
    default_low = min(0.21, max(0.0, thr - 0.01))
    review_low = st.number_input("리뷰 하한 (p1)", min_value=0.0, max_value=1.0,
                                    value=default_low, step=0.01, format="%.2f")

    # 절대 하한을 thr 범위로 설정
    review_low = float(np.clip(review_low, 0.0, thr))

    # 현재 선택 상태 안내
    if review_low >= thr:
        st.caption("리뷰 밴드: OFF (하한 ≥ 기준점)")
        band_text = "OFF"
    else:
        band_text = f"[ {review_low:.2f} , {thr:.2f} )"
        st.caption(f"리뷰 밴드: {band_text}")

    strict = st.checkbox("글자수 규칙 엄격 적용 (200~300자)", value=False)
    return thr, review_low, strict
		
def final_panel(thr: float, left: float):
    st.markdown("---")
    st.subheader("최종 결과")
    if st.session_state.get("teacher_decision") is None:
        st.info("교사가 최종 결정을 내리면 결과가 여기에 표시됩니다.")
        return

    dec = st.session_state["teacher_decision"]
    st.success(f"최종 배정: **{dec} · {LABEL_NAMES[dec]}**")
    st.markdown(
        f"- 학생: {st.session_state.get('student_name','')} \n"
        # 아래는 프로토타입 디버깅을 위해 임시로 둠. 실제 학생들에게는 보여주진 않는 것을 권함.
        f"- 모델 추천: {st.session_state.get('model_label')} "
        f"({LABEL_NAMES.get(st.session_state.get('model_label'), '?')}) \n"
        f"- p0(담임): {st.session_state.get('p0', 0.0):.3f} | "
        f"p1(교과): {st.session_state.get('p1', 0.0):.3f} \n"
        f"- 리뷰밴드(p1 기준): [ {left:.2f} , {thr:.2f} ] \n"
    )
    msg = (st.session_state.get("teacher_message") or DEFAULT_TEACHER_MESSAGE).strip()
    st.info(f"학생에게 전송된 메시지:\n\n> {msg}")

def init_session_state():
    if "student_submitted" not in st.session_state:
        st.session_state.update(
            student_submitted=False,
            case_id=None,
            student_name="",
            topic="",
            detail="",
            summary="",
            p0=None, p1=None, model_label=None,
            teacher_decision=None,
            # 메시지 상태
            teacher_message_draft="",
            teacher_message=None,
            message_sent=False,
            sent_at=None,
        )

def render_reset():
    st.markdown("")
    if st.button("초기화"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
