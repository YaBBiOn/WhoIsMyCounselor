import os

# 모델/추론
MERGED_DIR = os.environ.get("MODEL_DIR", "merger_model")
MAX_SEQ = int(os.environ.get("MAX_SEQ", "300"))

# 라벨/프리셋
LABEL_NAMES = {
    0: "담임 / 진로 교사",
    1: "전문가 / 교과 담당 교사",
}
PRESET_THRESHOLDS = {
    "담임교사": 0.31,   # f1이 가장 높은 2개의 데이터 중 recall이 높음
    "진로교사": 0.34,  # f1이 가장 높은 2개의 데이터 중 precision이 높음
}

# 교사 메시지
TEACHER_MESSAGE_MAX_LEN = 200
DEFAULT_TEACHER_MESSAGE = "자세한 상담 시간은 선생님과 직접 의논해요."

