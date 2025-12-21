# noon/controller.py
import pygame
import sys
from .model import NoonState
from .engine import NoonEngine
from .face import NoonFaceRenderer
from .presets import EMOTION_PRESETS
from .transition import transition_state
from .effects import EFFECT_HANDLER_MAP
from .eyetracking import EyeTracker

class Noon:
    """
    noon_noon 라이브러리의 모든 기능을 관리하는 고수준 컨트롤러 클래스.
    Pygame 루프를 내장하여 사용자가 Pygame을 몰라도 쉽게 사용할 수 있습니다.
    """
    def __init__(self, width: int = 800, height: int = 400, bg_color: tuple = (0, 0, 0), 
                 enable_eye_tracking: bool = False, camera_index: int = 0, 
                 eye_tracking_smoothing: float = 0.7, show_eye_tracking_preview: bool = True):
        """
        Args:
            width: 화면 너비
            height: 화면 높이
            bg_color: 배경색
            enable_eye_tracking: 눈 추적 활성화 여부
            camera_index: 웹캠 인덱스
            eye_tracking_smoothing: 눈 추적 스무딩 계수 (0.0~1.0)
            show_eye_tracking_preview: 눈 추적 미리보기 창 표시 여부
        """
        # Pygame 초기화를 클래스 내부에서 처리
        pygame.init()
        pygame.display.set_caption("Robot Face")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self._frame_clock = pygame.time.Clock()  # Delta time 계산용
        self.bg_color = bg_color
        
        # 내부 컴포넌트 초기화
        self.state = NoonState()
        self.engine = NoonEngine(width, height)
        self.renderer = NoonFaceRenderer(self.screen, self.engine)
        
        # Eye tracking 초기화
        self.eye_tracker: EyeTracker = None
        if enable_eye_tracking:
            try:
                self.eye_tracker = EyeTracker(
                    camera_index=camera_index,
                    smoothing_factor=eye_tracking_smoothing,
                    show_preview=show_eye_tracking_preview
                )
                if not self.eye_tracker.start():
                    print("Warning: Could not start webcam. Eye tracking disabled.")
                    self.eye_tracker = None
                else:
                    print("Eye tracking initialized successfully.")
            except Exception as e:
                print(f"Warning: Eye tracking initialization failed: {e}")
                self.eye_tracker = None
        
        self.current_emotion = "neutral"
        self.target_values = EMOTION_PRESETS["neutral"]["values"]
        
        # 콜백 함수
        self._key_press_callback = None
        self._every_frame_callback = None
        
        # Eye movement animation tracking
        self.prev_gaze_x = 0.0
        self.prev_gaze_y = 0.0
        self.prev_inner_hole_x = 0.0
        self.prev_inner_hole_y = 0.0
        self.highlight_bounce_velocity_x = 0.0
        self.highlight_bounce_velocity_y = 0.0
        
        # Blinking animation tracking
        self.blink_interval = 3.0  # 초 단위 (기본값: 3초)
        self.blink_duration = 0.15  # 깜빡임 지속 시간 (초)
        self.time_since_last_blink = 0.0
        self.is_blinking = False
        self.blink_progress = 0.0  # 0.0 (열림) ~ 1.0 (완전히 닫힘)
        self.delta_time = 0.0
        
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
        # Delta time 계산 (60 FPS 기준)
        self.delta_time = self._frame_clock.tick(60) / 1000.0  # 밀리초를 초로 변환
        
        # Eye tracking 업데이트 (가장 먼저 실행하여 gaze 값 업데이트)
        if self.eye_tracker:
            self.eye_tracker.update(self.state)
        
        transition_state(self.state, self.target_values, 0.1)
        self._handle_dynamic_effects()
        self._update_eye_movement_animation()
        self._update_blinking_animation()

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

        # 리소스 정리
        if self.eye_tracker:
            self.eye_tracker.stop()
        
        pygame.quit()
        sys.exit()
    
    def enable_eye_tracking(self, camera_index: int = 0, smoothing_factor: float = 0.7, 
                            show_preview: bool = True) -> bool:
        """
        눈 추적을 활성화합니다.
        
        Args:
            camera_index: 웹캠 인덱스
            smoothing_factor: 스무딩 계수 (0.0~1.0)
            show_preview: 미리보기 창 표시 여부
            
        Returns:
            성공 여부
        """
        if self.eye_tracker:
            return True  # 이미 활성화됨
        
        try:
            self.eye_tracker = EyeTracker(
                camera_index=camera_index,
                smoothing_factor=smoothing_factor,
                show_preview=show_preview
            )
            if self.eye_tracker.start():
                print("Eye tracking enabled.")
                return True
            else:
                print("Warning: Could not start webcam.")
                self.eye_tracker = None
                return False
        except Exception as e:
            print(f"Warning: Eye tracking initialization failed: {e}")
            self.eye_tracker = None
            return False
    
    def disable_eye_tracking(self):
        """눈 추적을 비활성화합니다."""
        if self.eye_tracker:
            self.eye_tracker.stop()
            self.eye_tracker = None
            print("Eye tracking disabled.")

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
    
    def _update_eye_movement_animation(self):
        """
        시선 변화에 따라 눈의 움직임 애니메이션을 업데이트합니다.
        1. Inner hole이 먼저 움직임
        2. Outer ring이 따라감 (지연)
        3. Highlight가 움직이고 반동 효과
        """
        # 시선 변화량 계산
        gaze_delta_x = self.state.gaze_x - self.prev_gaze_x
        gaze_delta_y = self.state.gaze_y - self.prev_gaze_y
        gaze_movement = abs(gaze_delta_x) + abs(gaze_delta_y)
        
        # 적응형 속도: 움직임이 클수록 더 빠르게 반응
        if gaze_movement > 0.1:
            inner_speed = 0.5  # 빠른 움직임: 빠른 추적
            outer_speed = 0.2
        elif gaze_movement > 0.05:
            inner_speed = 0.4  # 중간 움직임
            outer_speed = 0.15
        else:
            inner_speed = 0.3  # 느린 움직임: 부드러운 추적
            outer_speed = 0.12
        
        # Inner hole: 즉시 반응 (빠른 추적)
        target_inner_x = self.state.gaze_x * 0.3  # 최대 이동 범위
        target_inner_y = self.state.gaze_y * 0.2
        
        # Ease-out 적용으로 더 자연스러운 움직임
        inner_diff_x = target_inner_x - self.state.inner_hole_offset_x
        inner_diff_y = target_inner_y - self.state.inner_hole_offset_y
        
        # 거리에 따른 적응형 속도
        inner_distance = abs(inner_diff_x) + abs(inner_diff_y)
        if inner_distance > 0.1:
            adaptive_inner_speed = inner_speed * 1.2  # 멀리 있을 때 더 빠르게
        else:
            adaptive_inner_speed = inner_speed * 0.8  # 가까이 있을 때 더 부드럽게
        
        self.state.inner_hole_offset_x += inner_diff_x * adaptive_inner_speed
        self.state.inner_hole_offset_y += inner_diff_y * adaptive_inner_speed
        
        # Outer ring: Inner hole을 따라감 (지연된 추적)
        outer_diff_x = self.state.inner_hole_offset_x - self.state.outer_ring_offset_x
        outer_diff_y = self.state.inner_hole_offset_y - self.state.outer_ring_offset_y
        
        # 거리에 따른 적응형 속도
        outer_distance = abs(outer_diff_x) + abs(outer_diff_y)
        if outer_distance > 0.05:
            adaptive_outer_speed = outer_speed * 1.1
        else:
            adaptive_outer_speed = outer_speed * 0.9
        
        self.state.outer_ring_offset_x += outer_diff_x * adaptive_outer_speed
        self.state.outer_ring_offset_y += outer_diff_y * adaptive_outer_speed
        
        # Highlight: Inner hole의 움직임을 따라가고 반동 효과
        inner_delta_x = self.state.inner_hole_offset_x - self.prev_inner_hole_x
        inner_delta_y = self.state.inner_hole_offset_y - self.prev_inner_hole_y
        
        if abs(inner_delta_x) > 0.001 or abs(inner_delta_y) > 0.001:
            # Inner hole이 움직이면 반동 시작 (반대 방향으로)
            bounce_strength = min(0.25, (abs(inner_delta_x) + abs(inner_delta_y)) * 2.0)
            # 반동은 움직임의 반대 방향
            self.highlight_bounce_velocity_x -= inner_delta_x * bounce_strength
            self.highlight_bounce_velocity_y -= inner_delta_y * bounce_strength
        
        # Highlight 위치 업데이트 (반동 효과 포함)
        # 기본적으로 inner hole 위치를 따라가되, bounce offset 추가
        highlight_follow_speed = 0.3
        target_hl_x = self.highlight_bounce_velocity_x
        target_hl_y = self.highlight_bounce_velocity_y
        
        self.state.highlight_bounce_x += (target_hl_x - self.state.highlight_bounce_x) * highlight_follow_speed
        self.state.highlight_bounce_y += (target_hl_y - self.state.highlight_bounce_y) * highlight_follow_speed
        
        # 반동 감쇠 (damping)
        damping = 0.88
        self.highlight_bounce_velocity_x *= damping
        self.highlight_bounce_velocity_y *= damping
        
        # 이전 값 저장
        self.prev_gaze_x = self.state.gaze_x
        self.prev_gaze_y = self.state.gaze_y
        self.prev_inner_hole_x = self.state.inner_hole_offset_x
        self.prev_inner_hole_y = self.state.inner_hole_offset_y
    
    def _update_blinking_animation(self):
        """
        깜빡임 애니메이션을 업데이트합니다.
        설정된 간격에 따라 자동으로 깜빡임을 실행합니다.
        """
        self.time_since_last_blink += self.delta_time
        
        if self.is_blinking:
            # 깜빡임 진행 중
            self.blink_progress += self.delta_time / self.blink_duration
            
            if self.blink_progress >= 1.0:
                # 깜빡임 완료
                self.is_blinking = False
                self.blink_progress = 0.0
                self.time_since_last_blink = 0.0
                # 눈꺼풀 열기
                self.state.eyelid_top = 0.0
                self.state.eyelid_btm = 0.0
            else:
                # 깜빡임 애니메이션 (부드러운 곡선)
                # Ease-in-out 곡선 사용
                t = self.blink_progress
                if t < 0.5:
                    # 닫히는 중 (0.0 -> 1.0)
                    blink_value = 2.0 * t * t
                else:
                    # 열리는 중 (1.0 -> 0.0)
                    t = (t - 0.5) * 2.0
                    blink_value = 1.0 - (2.0 * t * t)
                
                self.state.eyelid_top = blink_value
                self.state.eyelid_btm = blink_value * 0.3  # 아랫 눈꺼풀은 덜 닫힘
        else:
            # 깜빡임 대기 중
            if self.time_since_last_blink >= self.blink_interval:
                # 깜빡임 시작
                self.is_blinking = True
                self.blink_progress = 0.0
    
    def set_blink_interval(self, interval: float):
        """
        깜빡임 간격을 설정합니다.
        
        Args:
            interval: 깜빡임 간격 (초 단위). 예: 2.0 = 2초마다 깜빡임
        """
        if interval > 0:
            self.blink_interval = interval
        else:
            raise ValueError("Blink interval must be greater than 0")
    
    def trigger_blink(self):
        """ 수동으로 깜빡임을 트리거합니다. """
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_progress = 0.0
            self.time_since_last_blink = 0.0