# noon/presets.py

"""
감정 표현을 위한 데이터 기반 프리셋.
'values'는 정적인 상태 값을, 'effects'는 매 프레임 적용될 동적 효과를 정의합니다.
"""

EMOTION_PRESETS = {
    "neutral": {
        "values": {
            "eye_scale": 1.0,
            "eye_eccentricity": 1.0,
            "eyelid_top": 0.0,
            "eyelid_btm": 0.0,
            "eyebrow_lift": 0.0,
            "eyebrow_shape": "arc",
            "gaze_y": 0.0,
        },
        "effects": []
    },
    "angry": {
        "values": {
            "eye_scale": 1.15,
            "eye_eccentricity": 1.1,
            "eyelid_top": 0.1,
            "eyelid_btm": 0.0,
            "eyebrow_lift": -0.6,
            "eyebrow_shape": "angry",
            "gaze_y": -0.15,
        },
        "effects": [
            {"type": "shake", "intensity": 2.0}
        ]
    },
}