import pygame
import sys
import random
from noon.model import NoonState
from noon.engine import NoonEngine
from noon.face import NoonFaceRenderer
from noon.presets import EMOTION_PRESETS
from noon.transition import transition_state, lerp
from utils.ui import UIManager

class App:
    def __init__(self):
        # 1. Init System
        pygame.init()
        self.width, self.height = 800, 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("noon_noon (v1.1)")
        self.clock = pygame.time.Clock()

        # 2. Init Modules
        self.state = NoonState()
        self.engine = NoonEngine(self.width, self.height)
        self.renderer = NoonFaceRenderer(self.screen, self.engine)
        self.ui_manager = UIManager(self.state, self.width)
        
        # 3. Emotion State
        self.current_emotion = "neutral"
        self.target_state_dict = EMOTION_PRESETS["neutral"]
        self._apply_emotion_preset("neutral", immediate=True)

    def run(self):
        running = True
        while running:
            running = self._handle_events()
            self._update_state()
            self._render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            clicked_emotion = self.ui_manager.handle_event(event, self.state)
            if clicked_emotion:
                self._apply_emotion_preset(clicked_emotion)

        return True

    def _apply_emotion_preset(self, emotion_name, immediate=False):
        """ 지정된 감정 프리셋을 타겟으로 설정하고, 슬라이더 상태를 리셋합니다. """
        if emotion_name in EMOTION_PRESETS:
            self.current_emotion = emotion_name
            self.target_state_dict = EMOTION_PRESETS[emotion_name]
            self.ui_manager.reset_slider_modifications() # 슬라이더 수정 상태 리셋
            
            if immediate:
                for key, value in self.target_state_dict.items():
                    setattr(self.state, key, value)

    def _update_state(self):
        """ 상태를 보간하고, 'angry' 감정의 애니메이션을 처리합니다. """
        # 사용자가 슬라이더를 조작하지 않은 속성만 보간 대상으로 필터링
        unmodified_targets = {}
        for key, target_value in self.target_state_dict.items():
            slider = self.ui_manager.get_slider_for_attribute(key)
            if not slider or not slider.is_modified:
                unmodified_targets[key] = target_value
        
        # 상태 전환 함수 호출
        transition_state(self.state, unmodified_targets, 0.1)

        # Handle angry shake animation
        if self.current_emotion == "angry":
            shake_intensity = 2.0
            self.state.shake_x = random.uniform(-shake_intensity, shake_intensity)
            self.state.shake_y = random.uniform(-shake_intensity, shake_intensity)
        else:
            self.state.shake_x = lerp(self.state.shake_x, 0, 0.2)
            self.state.shake_y = lerp(self.state.shake_y, 0, 0.2)

    def _render(self):
        self.renderer.draw(self.state)
        self.ui_manager.draw(self.screen, self.state)
        pygame.display.flip()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
