import pygame

class SimpleSlider:
    """ 개발자용 파라미터 튜닝 슬라이더 """
    def __init__(self, x, y, w, h, min_val, max_val, label, attr_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val, self.max_val = min_val, max_val
        self.label, self.attr_name = label, attr_name
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event, state_obj):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging:
            mx, _ = pygame.mouse.get_pos()
            ratio = max(0.0, min(1.0, (mx - self.rect.x) / self.rect.width))
            new_val = self.min_val + (ratio * (self.max_val - self.min_val))
            setattr(state_obj, self.attr_name, new_val)

    def draw(self, screen, state_obj):
        val = getattr(state_obj, self.attr_name)
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        
        # Style
        pygame.draw.rect(screen, (50, 50, 50), self.rect) # BG
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w * ratio, self.rect.height)
        pygame.draw.rect(screen, (100, 180, 255), fill_rect) # Fill
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 1) # Border
        
        # Text
        text = f"{self.label}: {val:.2f}"
        screen.blit(self.font.render(text, True, (200,200,200)), (self.rect.x, self.rect.y-18))