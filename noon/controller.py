# noon/controller.py
import pygame
from .model import NoonState
from .engine import NoonEngine
from .face import NoonFaceRenderer
from .presets import EMOTION_PRESETS
from .transition import transition_state
from .effects import EFFECT_HANDLER_MAP

class Noon:
    """
    noon_noon 라이브러리의 모든 기능을 관리하는 고수준 컨트롤러 클래스.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = NoonState()
        self.engine = NoonEngine(screen.get_width(), screen.get_height())
        self.renderer = NoonFaceRenderer(screen, self.engine)
        
        self.current_emotion = "neutral"
        self.target_values = EMOTION_PRESETS["neutral"]["values"]
        
        # 초기 상태 즉시 적용
        for key, value in self.target_values.items():
            setattr(self.state, key, value)

    def set_emotion(self, emotion_name: str):
        """
        눈의 목표 감정을 설정합니다.
        해당 감정은 update() 메소드 호출을 통해 점진적으로 적용됩니다.
        """
        if emotion_name in EMOTION_PRESETS and self.current_emotion != emotion_name:
            self.current_emotion = emotion_name
            self.target_values = EMOTION_PRESETS[emotion_name]["values"]

    def update(self):
        """
        매 프레임 호출되어야 하는 메인 업데이트 메소드.
        상태 전환 및 동적 효과를 처리합니다.
        """
        # 1. 목표 값으로 상태를 부드럽게 전환
        transition_state(self.state, self.target_values, 0.1)
        
        # 2. 현재 감정에 따른 동적 효과 처리
        self._handle_dynamic_effects()

    def draw(self):
        """
        눈을 화면에 그립니다. 배경을 채운 후 호출해야 합니다.
        """
        self.renderer.draw(self.state)

    def _handle_dynamic_effects(self):
        """
        현재 감정 프리셋의 'effects' 목록을 기반으로 애니메이션을 적용합니다.
        """
        active_effects = {effect['type'] for effect in EMOTION_PRESETS[self.current_emotion]['effects']}

        # 모든 효과 핸들러를 순회
        for effect_type, handler in EFFECT_HANDLER_MAP.items():
            if effect_type in active_effects:
                # 현재 감정에 이 효과가 포함되어 있으면 'apply' 함수 호출
                preset_effect = next((e for e in EMOTION_PRESETS[self.current_emotion]['effects'] if e['type'] == effect_type), None)
                if preset_effect:
                    params = {k: v for k, v in preset_effect.items() if k != 'type'}
                    handler['apply'](self.state, **params)
            else:
                # 포함되어 있지 않으면 'clear' 함수로 효과를 제거
                if 'clear' in handler:
                    handler['clear'](self.state)
