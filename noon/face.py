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
        base_cx, base_cy = self.engine.get_eye_center(is_right, state)
        w, h = self.engine.get_eye_dimensions(state)
        
        # Outer ring 위치 (shake + outer ring offset 적용)
        outer_cx = base_cx + state.shake_x + (state.outer_ring_offset_x * w * 0.3)
        outer_cy = base_cy + state.shake_y + (state.outer_ring_offset_y * h * 0.3)
        
        # 2. Outer Ring (도넛 몸통) - offset이 적용된 위치에 그리기
        rect = pygame.Rect(outer_cx - w/2, outer_cy - h/2, w, h)
        pygame.draw.ellipse(self.screen, state.color, rect)

        # Inner hole 위치 (outer ring 위치 기준으로 inner hole offset 적용)
        inner_offset_x = state.inner_hole_offset_x * w * 0.3
        inner_offset_y = state.inner_hole_offset_y * h * 0.3
        inner_cx = outer_cx + inner_offset_x
        inner_cy = outer_cy + inner_offset_y

        # 3. Inner Hole (구멍 뚫기) - outer ring 내부에서 offset된 위치
        inner_w, inner_h = w * state.ring_inner_ratio, h * state.ring_inner_ratio
        inner_rect = pygame.Rect(inner_cx - inner_w/2, inner_cy - inner_h/2, inner_w, inner_h)
        pygame.draw.ellipse(self.screen, self.bg_color, inner_rect)

        # 4. Reflection (알약 하이라이트) - inner hole 위치 기준으로 bounce 적용
        self._draw_highlight(inner_cx, inner_cy, inner_w, inner_h, state)

        # 5. Eyebrows - outer ring 위치 기준
        self._draw_eyebrow(outer_cx, outer_cy, w, h, state, is_right)

    def _draw_highlight(self, cx, cy, w, h, state):
        hl_w = w * 0.3 * state.highlight_scale
        hl_h = h * 0.2 * state.highlight_scale
        # 기본 위치 + bounce 효과
        hl_x = cx + (state.highlight_x * w * 0.4) + (state.highlight_bounce_x * w * 0.3)
        hl_y = cy + (state.highlight_y * h * 0.4) + (state.highlight_bounce_y * h * 0.3)
        
        rect = pygame.Rect(hl_x - hl_w/2, hl_y - hl_h/2, hl_w, hl_h)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=int(hl_h))

    def _draw_eyebrow(self, cx, cy, w, h, state, is_right: bool):
        if state.eyebrow_shape == 'angry':
            y_offset = cy - (h * 0.6) - (state.eyebrow_lift * 30)
            x_extent = w * 0.6
            angle_offset = w * 0.25
            
            if is_right:
                start_pos = (cx - x_extent, y_offset + angle_offset)
                end_pos = (cx + x_extent, y_offset - angle_offset)
            else: # left eye
                start_pos = (cx - x_extent, y_offset - angle_offset)
                end_pos = (cx + x_extent, y_offset + angle_offset)
            
            pygame.draw.line(self.screen, state.color, start_pos, end_pos, width=14)
        
        else: # default "arc" shape
            brow_y = cy - (h * 0.6) - (state.eyebrow_lift * 20)
            rect = pygame.Rect(cx - w * 0.6, brow_y - h * 0.3, w * 1.2, h * 0.6)
            pygame.draw.arc(self.screen, state.color, rect, math.radians(40), math.radians(140), width=12)
