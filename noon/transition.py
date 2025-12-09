# noon/transition.py

def lerp(start, end, t):
    """ 선형 보간(Linear Interpolation) 함수. """
    return start + t * (end - start)

def transition_state(current_state, target_dict, speed):
    """
    current_state를 target_dict의 값으로 부드럽게 전환합니다.
    숫자형 데이터는 보간하고, 다른 타입은 즉시 변경합니다.
    """
    for key, target_value in target_dict.items():
        current_value = getattr(current_state, key)
        
        if isinstance(current_value, (int, float)):
            new_value = lerp(current_value, target_value, speed)
            setattr(current_state, key, new_value)
        else:
            # For non-numeric types (like strings), apply immediately
            setattr(current_state, key, target_value)
