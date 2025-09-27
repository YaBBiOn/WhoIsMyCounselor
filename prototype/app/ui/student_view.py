import streamlit as st

def student_panel():
    st.subheader("학생용")
    name = st.text_input("step1) 학생의 이름을 알려주세요.")
    topic = st.text_area("step2) 상담 주제를 입력해주세요.", height=100,
                         placeholder="예) 진로, 성적, 과목선택 등")
    detail = st.text_area("step3) 상담 세부 내용을 기록해주세요.", height=200,
                          placeholder="구체적으로 어떤 상황인지, 무엇이 고민인지, 지금까지 해본 노력 등")
    st.caption("※ step2+step3 합계 200~300자 권장")

    length = len((topic or "") + (detail or ""))
    st.write(f"현재 글자수(공백 포함): **{length}자**")

    submit = st.button("step4) 제출하기")
    return name, topic, detail, length, submit

