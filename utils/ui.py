import pygame

class Button:
    """ 클릭 가능한 UI 버튼 """
    def __init__(self, x, y, w, h, label, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.is_pressed = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_pressed = True
            return self.label
        if event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        return None

    def draw(self, screen):
        color = (self.color[0]-20, self.color[1]-20, self.color[2]-20) if self.is_pressed else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200,200,200), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class SimpleSlider:
    """ 개발자용 파라미터 튜닝 슬라이더 """
    def __init__(self, x, y, w, h, min_val, max_val, label, attr_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val, self.max_val = min_val, max_val
        self.label, self.attr_name = label, attr_name
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.is_modified = False # 사용자 수정 여부 플래그

    def handle_event(self, event, state_obj):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging:
            self.is_modified = True # 사용자가 조작함
            mx, _ = pygame.mouse.get_pos()
            ratio = max(0.0, min(1.0, (mx - self.rect.x) / self.rect.width))
            new_val = self.min_val + (ratio * (self.max_val - self.min_val))
            setattr(state_obj, self.attr_name, new_val)

    def draw(self, screen, state_obj):
        val = getattr(state_obj, self.attr_name)
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        
        # Style
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w * ratio, self.rect.height)
        pygame.draw.rect(screen, (100, 180, 255), fill_rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 1)
        
        # Text
        text = f"{self.label}: {val:.2f}"
        screen.blit(self.font.render(text, True, (200,200,200)), (self.rect.x, self.rect.y-18))

class UIManager:
    """UI 컴포넌트들을 종합적으로 관리하는 클래스"""
    def __init__(self, state, width):
        self.buttons = []
        button_labels = ["neutral", "angry"]
        btn_w, btn_h, btn_margin = 110, 40, 10
        total_w = len(button_labels) * (btn_w + btn_margin) - btn_margin
        start_x = (width - total_w) / 2
        
        for i, label in enumerate(button_labels):
            self.buttons.append(Button(start_x + i * (btn_w + btn_margin), 20, btn_w, btn_h, label))

        self.sliders = [
            SimpleSlider(20, 100, 150, 15, 0.5, 1.5, "Eye Scale", "eye_scale"),
            SimpleSlider(20, 140, 150, 15, 0.3, 0.9, "Ring Thickness", "ring_inner_ratio"),
            SimpleSlider(20, 180, 150, 15, 0.8, 1.4, "Eccentricity", "eye_eccentricity"),
            SimpleSlider(20, 220, 150, 15, 0.5, 2.0, "Highlight Size", "highlight_scale"),
        ]
        self.font = pygame.font.SysFont("Arial", 12)

    def handle_event(self, event, state):
        for btn in self.buttons:
            emotion = btn.handle_event(event)
            if emotion:
                return emotion

        for s in self.sliders:
            s.handle_event(event, state)
        return None

    def is_dragging(self):
        return any(s.dragging for s in self.sliders)

    def get_slider_for_attribute(self, attr_name):
        """ 속성 이름으로 해당 슬라이더를 찾습니다. """
        for s in self.sliders:
            if s.attr_name == attr_name:
                return s
        return None

    def reset_slider_modifications(self):
        """ 모든 슬라이더의 '수정됨' 상태를 리셋합니다. """
        for s in self.sliders:
            s.is_modified = False

    def draw(self, screen, state):
        for btn in self.buttons:
            btn.draw(screen)
        for s in self.sliders:
            s.draw(screen, state)
        
        debug_text = f"Gaze(x,y): ({state.gaze_x:.2f}, {state.gaze_y:.2f})"
        screen.blit(self.font.render(debug_text, True, (150,150,150)), (20, screen.get_height() - 20))