import pygame
import sys

# 모듈화된 패키지 import
from noon.model import NoonState
from noon.engine import NoonEngine
from noon.face import NoonFaceRenderer
from utils.ui import SimpleSlider

def main():
    # 1. Init System
    pygame.init()
    width, height = 800, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("noon_noon (Refactored v1.0)")
    clock = pygame.time.Clock()

    # 2. Init Modules (Dependency Injection)
    # 데이터를 처리하는 엔진과, 그것을 그리는 렌더러를 분리
    state = NoonState()
    engine = NoonEngine(width, height)
    renderer = NoonFaceRenderer(screen, engine)

    # 3. Setup UI (Debug Tools)
    sliders = [
        SimpleSlider(20, 30, 150, 15, 0.5, 1.5, "Eye Scale", "eye_scale"),
        SimpleSlider(20, 70, 150, 15, 0.3, 0.9, "Ring Thickness", "ring_inner_ratio"),
        SimpleSlider(20, 110, 150, 15, 0.8, 1.4, "Eccentricity", "eye_eccentricity"),
        SimpleSlider(20, 150, 150, 15, 0.5, 2.0, "Highlight Size", "highlight_scale"),
    ]

    # 4. Main Loop
    running = True
    while running:
        # [Input]
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for s in sliders: s.handle_event(event, state)

        # [Logic]
        if not any(s.dragging for s in sliders):
            mx, my = pygame.mouse.get_pos()
            # 마우스 입력을 Gaze 좌표로 변환 (-1.0 ~ 1.0)
            state.gaze_x = max(-1.0, min(1.0, (mx - width/2) / (width/2)))
            state.gaze_y = max(-1.0, min(1.0, (my - height/2) / (height/2)))

        # [Render]
        renderer.draw(state)
        
        # Draw UI on top
        for s in sliders: s.draw(screen, state)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()