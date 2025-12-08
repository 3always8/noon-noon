import math
from .model import NoonState

class NoonEngine:
    """
    렌더링을 위한 좌표 계산 및 물리 로직 엔진.
    그래픽 라이브러리(Pygame)와 독립적으로 작동합니다.
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # 기본 설정값 (Configurable)
        self.base_spacing_ratio = 0.22  # 화면 너비 대비 눈 간격
        self.base_radius_ratio = 0.22   # 화면 크기(min) 대비 눈 반지름

    @property
    def base_radius(self) -> float:
        return min(self.width, self.height) * self.base_radius_ratio

    def get_eye_center(self, is_right_eye: bool, state: NoonState) -> tuple[float, float]:
        """ Gaze(시선)에 따른 눈의 중심 좌표 계산 (Head Turn Logic) """
        spacing = self.width * self.base_spacing_ratio
        center_offset = spacing if is_right_eye else -spacing
        
        # 시선 이동 범위 제한 (화면의 30%까지만 이동)
        max_pan_x = self.width * 0.3
        max_pan_y = self.height * 0.2
        
        cx = (self.width / 2) + center_offset + (state.gaze_x * max_pan_x)
        cy = (self.height / 2) + (state.gaze_y * max_pan_y)
        return cx, cy

    def get_eye_dimensions(self, state: NoonState) -> tuple[float, float]:
        """ 이심률과 스케일이 적용된 눈의 너비/높이 계산 """
        r = self.base_radius
        w = r * 2 * state.eye_eccentricity * state.eye_scale
        h = r * 2 * state.eye_scale
        return w, h