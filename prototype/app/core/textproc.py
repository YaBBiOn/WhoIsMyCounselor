def build_summary(student_name: str, topic: str, detail: str) -> str:
    parts = [
        f"[학생] {student_name.strip()}",
        f"[상담 주제] {topic.strip()}",
        f"[세부 내용] {detail.strip()}",
    ]
    return "\n".join(parts).strip() 