# noon/controller.py
import pygame
import sys
from .model import NoonState
from .engine import NoonEngine
from .face import NoonFaceRenderer
from .presets import EMOTION_PRESETS
from .transition import transition_state
from .effects import EFFECT_HANDLER_MAP

class Noon:
    """
    noon_noon 라이브러리의 모든 기능을 관리하는 고수준 컨트롤러 클래스.
    Pygame 루프를 내장하여 사용자가 Pygame을 몰라도 쉽게 사용할 수 있습니다.
    """
    def __init__(self, width: int = 800, height: int = 400, bg_color: tuple = (0, 0, 0)):
        # Pygame 초기화를 클래스 내부에서 처리
        pygame.init()
        pygame.display.set_caption("noon_noon")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.bg_color = bg_color
        
        # 내부 컴포넌트 초기화
        self.state = NoonState()
        self.engine = NoonEngine(width, height)
        self.renderer = NoonFaceRenderer(self.screen, self.engine)
        
        self.current_emotion = "neutral"
        self.target_values = EMOTION_PRESETS["neutral"]["values"]
        
        # 콜백 함수
        self._key_press_callback = None
        self._every_frame_callback = None
        
        # 초기 상태 즉시 적용
        for key, value in self.target_values.items():
            setattr(self.state, key, value)

    def set_emotion(self, emotion_name: str):
        """ 눈의 목표 감정을 설정합니다. """
        if emotion_name in EMOTION_PRESETS and self.current_emotion != emotion_name:
            self.current_emotion = emotion_name
            self.target_values = EMOTION_PRESETS[emotion_name]["values"]

    def on_key_press(self, callback):
        """ 키보드 키가 눌렸을 때 호출될 콜백 함수를 등록합니다. """
        self._key_press_callback = callback

    def on_every_frame(self, callback):
        """ 매 프레임마다 호출될 콜백 함수를 등록합니다. """
        self._every_frame_callback = callback

    def update(self):
        """ 상태 전환 및 동적 효과를 처리합니다. (수동 루프 제어용) """
        transition_state(self.state, self.target_values, 0.1)
        self._handle_dynamic_effects()

    def draw(self):
        """ 눈을 화면에 그립니다. (수동 루프 제어용) """
        self.renderer.draw(self.state)

    def run(self):
        """
        메인 애플리케이션 루프를 시작합니다.
        이 메소드는 사용자의 Pygame 보일러플레이트를 모두 추상화합니다.
        """
        running = True
        while running:
            # 1. 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: # 'q' 키로 종료
                        running = False
                    if self._key_press_callback:
                        self._key_press_callback(event.key)
            
            # 2. 매 프레임 콜백 실행
            if self._every_frame_callback:
                self._every_frame_callback()

            # 3. 내부 상태 업데이트 및 렌더링
            self.screen.fill(self.bg_color)
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _handle_dynamic_effects(self):
        """ 현재 감정 프리셋의 'effects' 목록을 기반으로 애니메이션을 적용합니다. """
        active_effects = {effect['type'] for effect in EMOTION_PRESETS[self.current_emotion]['effects']}
        for effect_type, handler in EFFECT_HANDLER_MAP.items():
            if effect_type in active_effects:
                preset_effect = next((e for e in EMOTION_PRESETS[self.current_emotion]['effects'] if e['type'] == effect_type), None)
                if preset_effect:
                    params = {k: v for k, v in preset_effect.items() if k != 'type'}
                    handler['apply'](self.state, **params)
            elif 'clear' in handler:
                handler['clear'](self.state)