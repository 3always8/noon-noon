# noon/effects.py
import random
from .transition import lerp

def apply_shake(state, intensity: float):
    """ state에 떨림 효과를 적용합니다. """
    state.shake_x = random.uniform(-intensity, intensity)
    state.shake_y = random.uniform(-intensity, intensity)

def clear_shake(state):
    """ 떨림 효과를 부드럽게 제거합니다. """
    state.shake_x = lerp(state.shake_x, 0, 0.2)
    state.shake_y = lerp(state.shake_y, 0, 0.2)

# 효과의 'type' 문자열과 실제 함수를 매핑합니다.
# 'apply'는 효과가 활성화될 때, 'clear'는 비활성화될 때 호출됩니다.
EFFECT_HANDLER_MAP = {
    "shake": {
        "apply": apply_shake,
        "clear": clear_shake,
    }
}
