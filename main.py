import pygame
import sys
from dataclasses import dataclass

# ==========================================
# 1. CORE PROTOCOL (State)
# ==========================================
@dataclass
class NoonState:
    # [Face Orientation] 고개 돌림 (Head Turn)
    gaze_x: float = 0.0
    gaze_y: float = 0.0
    
    # [1. Outer Circle] 제일 큰 원 (전체 크기 & 비율)
    eye_scale: float = 1.0        # 전체 크기 (지름)
    eye_eccentricity: float = 1.0 # 1.0=원, >1.0=가로타원 (이심률)
    
    # [2. Inner Circle] 두 번째 작은 원 (링 두께 결정)
    ring_inner_ratio: float = 0.65 # 외경 대비 내경 비율 (0.0~1.0)
                                   # 0.9 = 얇은 링, 0.5 = 두꺼운 링
    
    # [3. Reflection] 반사광 (Pill Shape)
    highlight_scale: float = 1.0   # 반사광 크기
    highlight_x: float = 0.3       # 반사광 위치 X (눈 중심 기준 비율)
    highlight_y: float = -0.3      # 반사광 위치 Y (눈 중심 기준 비율)
    
    # [Eyebrows] - Default
    eyebrow_lift: float = 0.0      # 눈썹 높이
    
    # [System]
    color: tuple = (180, 180, 180) # LG Styler 스타일의 밝은 회색

# ==========================================
# 2. UI SLIDER
# ==========================================
class SimpleSlider:
    def __init__(self, x, y, w, h, min_val, max_val, label, attr_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val, self.max_val = min_val, max_val
        self.label, self.attr_name = label, attr_name
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event, state):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging:
            mx, _ = pygame.mouse.get_pos()
            ratio = max(0.0, min(1.0, (mx - self.rect.x) / self.rect.width))
            setattr(state, self.attr_name, self.min_val + (ratio * (self.max_val - self.min_val)))

    def draw(self, screen, state):
        val = getattr(state, self.attr_name)
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (150, 150, 150), (self.rect.x, self.rect.y, self.rect.w * ratio, self.rect.h))
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 1)
        screen.blit(self.font.render(f"{self.label}: {val:.2f}", True, (220,220,220)), (self.rect.x, self.rect.y-18))

# ==========================================
# 3. ENGINE
# ==========================================
class NoonEngine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.base_spacing = width * 0.22 # 눈 사이 간격
        self.base_radius = min(width, height) * 0.22 # 기본 반지름

    def get_eye_center(self, is_right_eye, state):
        """ 얼굴 회전(Gaze)에 따른 눈의 중심 좌표 계산 """
        center_offset = self.base_spacing if is_right_eye else -self.base_spacing
        
        # Head Turn Logic (화면 범위의 30% 정도만 이동)
        move_x = state.gaze_x * (self.width * 0.3)
        move_y = state.gaze_y * (self.height * 0.2)
        
        cx = (self.width / 2) + center_offset + move_x
        cy = (self.height / 2) + move_y
        return cx, cy

# ==========================================
# 4. RENDERER (Updated for Image Style)
# ==========================================
class NoonRenderer:
    def __init__(self, screen, engine):
        self.screen = screen
        self.engine = engine
        self.bg_color = (0, 0, 0) # 완전 블랙 배경

    def draw(self, state: NoonState):
        self.screen.fill(self.bg_color)
        self._draw_eye_unit(state, is_right=False)
        self._draw_eye_unit(state, is_right=True)

    def _draw_eye_unit(self, state, is_right):
        cx, cy = self.engine.get_eye_center(is_right, state)
        
        # 치수 계산
        outer_w = self.engine.base_radius * 2 * state.eye_eccentricity * state.eye_scale
        outer_h = self.engine.base_radius * 2 * state.eye_scale
        
        inner_w = outer_w * state.ring_inner_ratio
        inner_h = outer_h * state.ring_inner_ratio

        # -------------------------------------------------
        # [Element 1] Outer Circle (Ring Body)
        # -------------------------------------------------
        # 그라데이션 대신 단색 Flat 디자인 적용 (이미지 기반)
        outer_rect = pygame.Rect(cx - outer_w/2, cy - outer_h/2, outer_w, outer_h)
        pygame.draw.ellipse(self.screen, state.color, outer_rect)

        # -------------------------------------------------
        # [Element 2] Inner Circle (Hole)
        # -------------------------------------------------
        # 배경색과 동일한 원을 그려 구멍을 뚫은 효과를 냄
        inner_rect = pygame.Rect(cx - inner_w/2, cy - inner_h/2, inner_w, inner_h)
        pygame.draw.ellipse(self.screen, self.bg_color, inner_rect)

        # -------------------------------------------------
        # [Element 3] Reflection (Highlight)
        # -------------------------------------------------
        # 위치: Inner Hole 내부에서의 상대 좌표
        # 알약 모양(Pill Shape) = Rounded Rect
        hl_w = inner_w * 0.3 * state.highlight_scale
        hl_h = inner_h * 0.2 * state.highlight_scale
        
        # 하이라이트 위치 오프셋 (비율 -> 픽셀 변환)
        hl_cx = cx + (state.highlight_x * inner_w * 0.4)
        hl_cy = cy + (state.highlight_y * inner_h * 0.4)
        
        hl_rect = pygame.Rect(hl_cx - hl_w/2, hl_cy - hl_h/2, hl_w, hl_h)
        
        # Pill Shape: border_radius를 높이의 절반으로 설정하면 알약 모양이 됨
        pygame.draw.rect(self.screen, (255, 255, 255), hl_rect, border_radius=int(hl_h))

        # -------------------------------------------------
        # [Element 4] Eyebrow (Default)
        # -------------------------------------------------
        self._draw_eyebrow(cx, cy, outer_w, outer_h, state)

    def _draw_eyebrow(self, cx, cy, eye_w, eye_h, state):
        """ 심플한 회색 아치형 눈썹 """
        # 눈 위쪽으로 위치 잡기
        brow_y = cy - (eye_h * 0.6) - (state.eyebrow_lift * 20)
        
        # 아치 그리기 (Arc)
        # Rect: 아치가 그려질 가상의 사각형 박스
        arc_w = eye_w * 1.2
        arc_h = eye_h * 0.6
        arc_rect = pygame.Rect(cx - arc_w/2, brow_y - arc_h/2, arc_w, arc_h)
        
        # Start/End Angle (Radian): 0 ~ Pi (180도) -> 약간 평평하게 조정
        # Pygame의 arc는 0도가 3시 방향, 시계 반대방향 증가
        # 45도 ~ 135도 사이를 그림
        import math
        pygame.draw.arc(self.screen, state.color, arc_rect, 
                        math.radians(40), math.radians(140), width=12)

# ==========================================
# 5. MAIN
# ==========================================
def main():
    pygame.init()
    width, height = 800, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("noon_noon (Ring Topology)")
    clock = pygame.time.Clock()

    engine = NoonEngine(width, height)
    renderer = NoonRenderer(screen, engine)
    state = NoonState()

    # 컨트롤러 구성
    sliders = [
        SimpleSlider(20, 20, 150, 15, 0.5, 1.5, "1. Eye Scale", "eye_scale"),
        SimpleSlider(20, 50, 150, 15, 0.3, 0.9, "2. Ring Thickness (Inner)", "ring_inner_ratio"),
        SimpleSlider(20, 80, 150, 15, 0.5, 2.0, "3. Highlight Size", "highlight_scale"),
        SimpleSlider(20, 110, 150, 15, -1.0, 1.0, "Reflect Pos X", "highlight_x"),
        SimpleSlider(20, 140, 150, 15, -1.0, 1.0, "Reflect Pos Y", "highlight_y"),
        SimpleSlider(20, 170, 150, 15, 0.8, 1.4, "Eccentricity", "eye_eccentricity"),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for s in sliders: s.handle_event(event, state)

        # Logic: 마우스 = 고개 돌리기 (Head Turn)
        if not any(s.dragging for s in sliders):
            mx, my = pygame.mouse.get_pos()
            state.gaze_x = max(-1.0, min(1.0, (mx - width/2) / (width/2)))
            state.gaze_y = max(-1.0, min(1.0, (my - height/2) / (height/2)))

        renderer.draw(state)
        for s in sliders: s.draw(screen, state)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()