import pygame
import sys
from noon import Noon
from utils.ui import UIManager

def main():
    """
    새로운 Noon 컨트롤러와 기존 UI 매니저를 함께 사용하는 데모.
    """
    # 1. Init System
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("noon_noon (Controller Demo)")
    clock = pygame.time.Clock()

    # 2. Init Modules
    eyes = Noon(screen)
    # UI 매니저는 Noon 컨트롤러가 내부적으로 관리하는 state 객체를 공유합니다.
    ui_manager = UIManager(eyes.state, screen.get_width())

    # 3. Main Loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # UI 매니저가 이벤트를 처리 (슬라이더 조작 등)
            clicked_emotion = ui_manager.handle_event(event, eyes.state)
            if clicked_emotion:
                # 감정 버튼이 클릭되면 Noon 컨트롤러에 알림
                eyes.set_emotion(clicked_emotion)
                # 슬라이더의 is_modified 플래그를 리셋하여 새 감정 값이 적용되게 함
                ui_manager.reset_slider_modifications()

        # Update state
        # Noon 컨트롤러의 update는 프리셋에 따른 상태 전환과 동적 효과를 담당
        eyes.update()
        
        # 슬라이더에 의해 직접 조작된 값은 update 이후에도 유지됨
        # (단, 새 감정 선택 시 reset_slider_modifications가 호출되어 초기화됨)

        # Render
        screen.fill((0, 0, 0))
        eyes.draw()
        ui_manager.draw(screen, eyes.state)
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()