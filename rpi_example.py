# rpi_example.py
# 이 파일은 noon_noon 라이브러리의 사용법을 보여주는 예제입니다.
# README.md에 이 코드의 일부가 포함되므로, 설명을 명확하게 유지해주세요.

# README_EXAMPLE_START
from noon import Noon, EyeTracker
# pygame.locals에서 키보드 입력에 필요한 키 상수만 가져옵니다.
from pygame.locals import K_a, K_n

# 1. Noon 컨트롤러 객체를 생성합니다.
# 이 한 줄이 Pygame 초기화, 윈도우 생성 등 모든 준비를 끝냅니다.
eyes = Noon(width=800, height=400)

# 2. 웹캠 기반 눈 추적기를 초기화합니다.
# MediaPipe가 설치되어 있으면 자동으로 사용하고, 없으면 OpenCV Haar Cascades를 사용합니다.
# show_preview=True로 설정하면 "User Face" 창이 표시되고, 감지된 얼굴 영역이 사각형으로 표시됩니다.
try:
    eye_tracker = EyeTracker(camera_index=0, smoothing_factor=0.7, show_preview=True)
    if eye_tracker.start():
        print("Eye tracking initialized successfully.")
        print("Two windows opened:")
        print("  - 'Robot Face': Shows robot eyes that track your head movement")
        print("  - 'User Face': Shows webcam feed with face tracking rectangle")
    else:
        print("Warning: Could not start webcam. Eye tracking disabled.")
        eye_tracker = None
except Exception as e:
    print(f"Warning: Eye tracking initialization failed: {e}")
    eye_tracker = None

# 3. 키 입력이 있을 때 실행될 함수를 정의합니다.
# 이 함수는 눌린 키의 `key` 코드를 인자로 받습니다.
def handle_keyboard_input(key):
    if key == K_a:
        print("Set emotion -> angry")
        eyes.set_emotion("angry")
    elif key == K_n:
        print("Set emotion -> neutral")
        eyes.set_emotion("neutral")

# 4. 위에서 정의한 함수를 키 입력 콜백으로 등록합니다.
# 이제 키가 눌릴 때마다 handle_keyboard_input 함수가 자동으로 호출됩니다.
eyes.on_key_press(handle_keyboard_input)

# 5. 매 프레임마다 웹캠에서 얼굴을 감지하여 눈의 시선을 업데이트합니다.
def update_eye_tracking():
    if eye_tracker:
        eye_tracker.update(eyes.state)

eyes.on_every_frame(update_eye_tracking)

# 6. noon_noon 애플리케이션을 실행합니다.
# 이 함수는 사용자가 'q' 키를 누르거나 창을 닫기 전까지
# 모든 이벤트 처리, 상태 업데이트, 렌더링 루프를 알아서 처리합니다.
print("Application running... Press 'n' for neutral, 'a' for angry. Press 'q' to quit.")
try:
    eyes.run()
finally:
    # 웹캠 리소스 정리
    if eye_tracker:
        eye_tracker.stop()

print("Application has quit.")
# README_EXAMPLE_END