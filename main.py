import pygame
import sys
from dataclasses import dataclass

# ==========================================
# 1. CORE PROTOCOL (State)
# ==========================================
@dataclass
class NoonState:
    # [Eye Shape]
    eye_eccentricity: float = 1.0  # 1.0=원, >1.0=가로타원, <1.0=세로타원
    
    # [Eye Motion]
    pupil_x: float = 0.0
    pupil_y: float = 0.0
    pupil_scale: float = 1.0
    
    # [Eyelids]
    eyelid_top: float = 0.0
    eyelid_btm: float = 0.0
    
    # [Color & Hardware]
    color: tuple = (100, 200, 255) 
    head_pan: float = 0.0

# ==========================================
# 2. UI SYSTEM (New!)
# ==========================================
class SimpleSlider:
    """ 개발/디자인 단계에서 파라미터를 실시간 튜닝하기 위한 UI 컴포넌트 """
    def __init__(self, x, y, w, h, min_val, max_val, label, attr_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.label = label
        self.attr_name = attr_name # NoonState의 속성 이름
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event, state: NoonState):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging:
            mx, my = pygame.mouse.get_pos()
            # 마우스 위치를 0.0 ~ 1.0 비율로 변환
            ratio = (mx - self.rect.x) / self.rect.width
            ratio = max(0.0, min(1.0, ratio))
            
            # 값 계산 (Lerp)
            val = self.min_val + (ratio * (self.max_val - self.min_val))
            
            # State 업데이트 (Reflection)
            setattr(state, self.attr_name, val)

    def draw(self, screen, state: NoonState):
        # 현재 값 가져오기
        current_val = getattr(state, self.attr_name)
        
        # 배경 바
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        
        # 채워진 바
        ratio = (current_val - self.min_val) / (self.max_val - self.min_val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width * ratio, self.rect.height)
        pygame.draw.rect(screen, (100, 180, 255), fill_rect)
        
        # 테두리
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 1)

        # 텍스트 라벨 (이름 + 값)
        text = f"{self.label}: {current_val:.2f}"
        text_surf = self.font.render(text, True, (220, 220, 220))
        screen.blit(text_surf, (self.rect.x, self.rect.y - 18))

# ==========================================
# 3. ENGINE (Logic)
# ==========================================
class NoonEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.eye_spacing = width * 0.25 
        self.base_radius = min(width, height) * 0.18 # 기본 반지름

    def get_eye_geometry(self, is_right_eye, eccentricity):
        """ 눈의 위치와 타원형 사각형(Rect) 정보를 계산 """
        cx_offset = self.eye_spacing if is_right_eye else -self.eye_spacing
        cx = (self.width // 2) + cx_offset
        cy = self.height // 2
        
        # 이심률 적용: 가로 길이 = 반지름 * 이심률, 세로 길이 = 반지름
        w = self.base_radius * 2 * eccentricity
        h = self.base_radius * 2
        
        return cx, cy, w, h

    def ratio_to_pixel(self, x_ratio, y_ratio, cx, cy, w, h):
        """ 타원의 크기에 맞춰 동공 위치 계산 """
        # 동공 이동 범위 (흰자위 크기의 60%)
        move_x = (w / 2) * 0.6
        move_y = (h / 2) * 0.6
        
        px = cx + (x_ratio * move_x)
        py = cy + (y_ratio * move_y)
        return px, py

# ==========================================
# 4. RENDERER (View)
# ==========================================
class NoonRenderer:
    def __init__(self, screen, engine):
        self.screen = screen
        self.engine = engine

    def draw(self, state: NoonState):
        self.screen.fill((30, 30, 30)) # 배경

        self._draw_eye(state, is_right=False)
        self._draw_eye(state, is_right=True)

    def _draw_eye(self, state, is_right):
        cx, cy, w, h = self.engine.get_eye_geometry(is_right, state.eye_eccentricity)
        
        # 1. Sclera (흰자위) - Ellipse
        # Pygame의 draw.ellipse는 감싸는 사각형(Rect)을 받습니다.
        eye_rect = pygame.Rect(cx - w/2, cy - h/2, w, h)
        pygame.draw.ellipse(self.screen, (220, 220, 220), eye_rect)

        # 2. Pupil (동공)
        px, py = self.engine.ratio_to_pixel(state.pupil_x, state.pupil_y, cx, cy, w, h)
        
        # 동공 크기도 이심률을 따라갈 것인가? -> 보통은 동공은 원형 유지 or 약간 변형
        # 여기서는 동공은 원형을 유지하되 크기만 조절
        pupil_r = (self.engine.base_radius * 0.45 * state.pupil_scale)
        pygame.draw.circle(self.screen, state.color, (int(px), int(py)), int(pupil_r))
        
        # Highlight
        pygame.draw.circle(self.screen, (255, 255, 255), 
                           (int(px - pupil_r*0.3), int(py - pupil_r*0.3)), 
                           int(pupil_r * 0.3))

        # 3. Eyelids (눈꺼풀)
        # 타원형 눈꺼풀을 그리는 건 복잡하므로, 현재는 직사각형으로 심플하게 가림 (Robot Style)
        if state.eyelid_top > 0:
            lid_h = h * state.eyelid_top
            pygame.draw.rect(self.screen, (30, 30, 30), 
                             (cx - w/2 - 5, cy - h/2 - 5, w + 10, lid_h + 5)) # 조금 넉넉하게

        if state.eyelid_btm > 0:
            lid_h = h * state.eyelid_btm
            pygame.draw.rect(self.screen, (30, 30, 30), 
                             (cx - w/2 - 5, (cy + h/2) - lid_h, w + 10, lid_h + 5))

# ==========================================
# 5. MAIN
# ==========================================
def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("noon_noon Configurator")
    clock = pygame.time.Clock()

    engine = NoonEngine(width, height)
    renderer = NoonRenderer(screen, engine)
    state = NoonState()

    # [UI 구성] 슬라이더 패널 생성
    sliders = [
        SimpleSlider(20, 50, 200, 20, 0.5, 2.5, "Eccentricity (Shape)", "eye_eccentricity"),
        SimpleSlider(20, 100, 200, 20, 0.5, 2.0, "Pupil Scale", "pupil_scale"),
        SimpleSlider(20, 150, 200, 20, 0.0, 1.0, "Eyelid Top", "eyelid_top"),
        SimpleSlider(20, 200, 200, 20, 0.0, 1.0, "Eyelid Bottom", "eyelid_btm"),
        # 시선은 마우스로 제어하므로 슬라이더 제외
    ]

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # UI 이벤트 전달
            for slider in sliders:
                slider.handle_event(event, state)

        # 2. Logic (Mouse Gaze)
        # 슬라이더 조작 중이 아닐 때만 시선 추적 (간섭 방지)
        if not any(s.dragging for s in sliders):
            mx, my = pygame.mouse.get_pos()
            state.pupil_x = (mx - width/2) / (width/2)
            state.pupil_y = (my - height/2) / (height/2)
            # Clamp
            state.pupil_x = max(-1.0, min(1.0, state.pupil_x))
            state.pupil_y = max(-1.0, min(1.0, state.pupil_y))

        # 3. Render
        renderer.draw(state)
        
        # Draw UI on top
        for slider in sliders:
            slider.draw(screen, state)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()