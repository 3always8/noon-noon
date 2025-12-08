from dataclasses import dataclass

@dataclass
class NoonState:
    """
    로봇의 표정과 동작을 결정하는 상태 데이터 모델.
    모든 값은 가능한 0.0 ~ 1.0 (비율) 또는 -1.0 ~ 1.0 (좌표) 범위를 권장합니다.
    """
    # [Face Orientation]
    gaze_x: float = 0.0  # -1.0(Left) ~ 1.0(Right)
    gaze_y: float = 0.0  # -1.0(Up) ~ 1.0(Down)
    
    # [Eye Geometry]
    eye_scale: float = 1.0        # 전체 크기 배율
    eye_eccentricity: float = 1.0 # 1.0=원, >1.0=가로타원
    ring_inner_ratio: float = 0.65 # 링 두께 (0.0=꽉참 ~ 1.0=투명)
    
    # [Reflection]
    highlight_scale: float = 1.0
    highlight_x: float = 0.3
    highlight_y: float = -0.3
    
    # [Emotion/Expression]
    eyebrow_lift: float = 0.0     # 눈썹 높이
    eyelid_top: float = 0.0       # 윗 눈꺼풀 닫힘 (0.0~1.0)
    eyelid_btm: float = 0.0       # 아랫 눈꺼풀 닫힘
    
    # [System]
    color: tuple = (180, 180, 180) # Main Eye Color