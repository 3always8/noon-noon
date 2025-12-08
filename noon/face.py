import pygame
import math
from .model import NoonState
from .engine import NoonEngine

class NoonFaceRenderer:
    """
    NoonState와 NoonEngine을 사용하여 실제 화면에 픽셀을 그리는 렌더러.
    """
    def __init__(self, screen: pygame.Surface, engine: NoonEngine):
        self.screen = screen
        self.engine = engine
        self.bg_color = (0, 0, 0)

    def draw(self, state: NoonState):
        self.screen.fill(self.bg_color)
        self._draw_eye(state, is_right=False)
        self._draw_eye(state, is_right=True)

    def _draw_eye(self, state: NoonState, is_right: bool):
        # 1. 계산 (Engine 위임)
        cx, cy = self.engine.get_eye_center(is_right, state)
        w, h = self.engine.get_eye_dimensions(state)
        
        # 2. Outer Ring (도넛 몸통)
        rect = pygame.Rect(cx - w/2, cy - h/2, w, h)
        pygame.draw.ellipse(self.screen, state.color, rect)

        # 3. Inner Hole (구멍 뚫기)
        inner_w, inner_h = w * state.ring_inner_ratio, h * state.ring_inner_ratio
        inner_rect = pygame.Rect(cx - inner_w/2, cy - inner_h/2, inner_w, inner_h)
        pygame.draw.ellipse(self.screen, self.bg_color, inner_rect)

        # 4. Reflection (알약 하이라이트)
        self._draw_highlight(cx, cy, inner_w, inner_h, state)

        # 5. Eyebrows
        self._draw_eyebrow(cx, cy, w, h, state)

    def _draw_highlight(self, cx, cy, w, h, state):
        hl_w = w * 0.3 * state.highlight_scale
        hl_h = h * 0.2 * state.highlight_scale
        hl_x = cx + (state.highlight_x * w * 0.4)
        hl_y = cy + (state.highlight_y * h * 0.4)
        
        rect = pygame.Rect(hl_x - hl_w/2, hl_y - hl_h/2, hl_w, hl_h)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=int(hl_h))

    def _draw_eyebrow(self, cx, cy, w, h, state):
        brow_y = cy - (h * 0.6) - (state.eyebrow_lift * 20)
        rect = pygame.Rect(cx - w * 0.6, brow_y - h * 0.3, w * 1.2, h * 0.6)
        pygame.draw.arc(self.screen, state.color, rect, math.radians(40), math.radians(140), width=12)