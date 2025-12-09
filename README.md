# noon_noon (👁️__👁️)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-fast-purple)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

<div align="center">
  <img src="assets/preview.png" width="80%" alt="noon_noon Preview" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <br>
  <p><em>(Note: The preview image shows a previous version. The UI now features emotion buttons.)</em></p>
</div>


**noon_noon** is a universal, hardware-agnostic robot eye expression library.  
It decouples logic from hardware, using a **"Ratio over Pixel"** philosophy to ensure consistent expressions across any screen resolution or motor configuration.

> **Navigation:**
> [🇺🇸 English](#english) | [🇰🇷 한국어](#korean)

---

<a name="english"></a>
## 🇺🇸 English

### Core Philosophy
* **Ratio over Pixel:** Position and scale are communicated via ratios (`-1.0` to `1.0`), not absolute pixels.
* **Config over Code:** Design expressions by tweaking parameters, not rewriting rendering loops.
* **Motor Agnostic:** The core logic is independent of physical motors, making it adaptable to various hardware setups.

### Features
* **Emotion Preset System:** Easily switch between pre-defined emotions like "neutral" and "angry."
* **Dynamic Expressions:** The "angry" emotion includes a unique eyebrow shape and a shaking animation for added effect.
* **Smooth Transitions:** A built-in `transition_state` function allows for smooth interpolation between different emotional states.
* **Real-Time Tuning:** Use on-screen sliders to override and fine-tune emotion parameters in real-time. The adjusted values persist until a new emotion is selected.

### How to Run the Demo

This project uses **[uv](https://github.com/astral-sh/uv)** for package management.

1. **Clone & Install**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **Run the Demo with UI**
   This runs the main application which includes UI sliders for debugging.
   ```bash
   uv run main.py
   ```

### Using as a Library (e.g., on Raspberry Pi)

You can import `noon_noon`'s core modules into your own Python application. This is ideal for projects like Raspberry Pi robots where you control emotions via GPIO buttons or other inputs, without the need for UI sliders.

The key is to create your own application loop and use `noon_noon`'s components to manage state and render the eyes.

**Example (`rpi_example.py`):**

The following example shows how to switch between "neutral" and "angry" expressions by pressing 'n' and 'a' on the keyboard. You can find this file in the repository.

```python
import pygame
import sys
import random

# Import core modules from the noon_noon library
from noon.model import NoonState
from noon.engine import NoonEngine
from noon.face import NoonFaceRenderer
from noon.presets import EMOTION_PRESETS
from noon.transition import transition_state, lerp

def main():
    # 1. Initialize Pygame and screen
    pygame.init()
    # On Raspberry Pi, you might use fullscreen
    # screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((800, 400))
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # 2. Initialize noon_noon components
    state = NoonState()
    engine = NoonEngine(screen.get_width(), screen.get_height())
    renderer = NoonFaceRenderer(screen, engine)

    # 3. Set initial emotion
    current_emotion = "neutral"
    target_state_dict = EMOTION_PRESETS[current_emotion]
    for key, value in target_state_dict.items():
        setattr(state, key, value)

    # 4. Main application loop
    running = True
    while running:
        # --- Handle your inputs (e.g., GPIO, keyboard) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    current_emotion = "angry"
                    target_state_dict = EMOTION_PRESETS[current_emotion]
                elif event.key == pygame.K_n:
                    current_emotion = "neutral"
                    target_state_dict = EMOTION_PRESETS[current_emotion]
        
        # --- Update state ---
        # 1. Smoothly transition to the target emotion state
        transition_state(state, target_state_dict, 0.1)
        
        # 2. Add dynamic effects for specific emotions
        if current_emotion == "angry":
            state.shake_x = random.uniform(-2.0, 2.0)
            state.shake_y = random.uniform(-2.0, 2.0)
        else:
            state.shake_x = lerp(state.shake_x, 0, 0.2)
            state.shake_y = lerp(state.shake_y, 0, 0.2)
            
        # --- Render the eyes ---
        renderer.draw(state)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
```

---

<div align="center">
<hr width="50%">
</div>

<a name="korean"></a>
## 🇰🇷 한국어

### 핵심 철학
* **Ratio over Pixel:** 좌표는 픽셀이 아닌 비율(`-1.0` ~ `1.0`)로 소통합니다.
* **Config over Code:** 코드를 수정하는 대신, 파라미터 값만으로 다양한 디자인을 만듭니다.
* **Motor Agnostic:** 핵심 로직이 물리 모터와 독립적이므로, 다양한 하드웨어 환경에 적용할 수 있습니다.

### 주요 기능
* **감정 프리셋 시스템:** 'neutral'(중립)과 'angry'(화남) 등 미리 정의된 감정 표현을 쉽게 전환합니다.
* **동적 표현:** 'angry' 감정은 고유한 눈썹 모양과 미세한 떨림 애니메이션을 포함하여 표현을 극대화합니다.
* **부드러운 전환:** `transition_state` 함수를 통해 서로 다른 감정 상태를 부드럽게 보간할 수 있습니다.
* **실시간 튜닝:** 화면의 슬라이더를 사용해 감정 프리셋의 값을 덮어쓰고 실시간으로 미세 조정할 수 있습니다. 조정된 값은 다른 감정을 선택하기 전까지 유지됩니다.

### 데모 실행 방법

이 프로젝트는 **[uv](https://github.com/astral-sh/uv)**를 사용하여 패키지를 관리합니다.

1. **클론 및 설치**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **UI 데모 실행**
   디버깅용 UI 슬라이더가 포함된 메인 애플리케이션을 실행합니다.
   ```bash
   uv run main.py
   ```

### 라이브러리로 사용하기 (예: 라즈베리파이)

`noon_noon`의 핵심 모듈을 당신의 파이썬 프로젝트로 가져와 사용할 수 있습니다. 이 방식은 GPIO 버튼 등 별도의 입력으로 감정을 제어하는 라즈베리파이 로봇 프로젝트에 이상적입니다.

핵심은 UI 슬라이더 없이, 자신만의 애플리케이션 루프를 만들고 `noon_noon`의 컴포넌트를 사용해 상태를 관리하고 눈을 그리는 것입니다.

**사용 예제 (`rpi_example.py`):**

아래 예제는 키보드의 'n'키와 'a'키를 눌러 'neutral'과 'angry' 표정을 전환하는 방법을 보여줍니다. 이 파일은 레포지토리 내에서 직접 확인할 수 있습니다.

```python
import pygame
import sys
import random

# noon_noon 라이브러리의 핵심 모듈들을 가져옵니다.
from noon.model import NoonState
from noon.engine import NoonEngine
from noon.face import NoonFaceRenderer
from noon.presets import EMOTION_PRESETS
from noon.transition import transition_state, lerp

def main():
    # 1. Pygame 및 스크린 초기화
    pygame.init()
    # 라즈베리파이에서는 전체화면으로 설정할 수 있습니다.
    # screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((800, 400))
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # 2. noon_noon 컴포넌트 초기화
    state = NoonState()
    engine = NoonEngine(screen.get_width(), screen.get_height())
    renderer = NoonFaceRenderer(screen, engine)

    # 3. 초기 감정 설정
    current_emotion = "neutral"
    target_state_dict = EMOTION_PRESETS[current_emotion]
    for key, value in target_state_dict.items():
        setattr(state, key, value)

    # 4. 메인 애플리케이션 루프
    running = True
    while running:
        # --- 입력 처리 (예: GPIO, 키보드) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    current_emotion = "angry"
                    target_state_dict = EMOTION_PRESETS[current_emotion]
                elif event.key == pygame.K_n:
                    current_emotion = "neutral"
                    target_state_dict = EMOTION_PRESETS[current_emotion]
        
        # --- 상태 업데이트 ---
        # 1. 목표 감정 상태로 부드럽게 전환
        transition_state(state, target_state_dict, 0.1)
        
        # 2. 특정 감정에 대한 동적 효과 추가
        if current_emotion == "angry":
            state.shake_x = random.uniform(-2.0, 2.0)
            state.shake_y = random.uniform(-2.0, 2.0)
        else:
            state.shake_x = lerp(state.shake_x, 0, 0.2)
            state.shake_y = lerp(state.shake_y, 0, 0.2)
            
        # --- 렌더링 ---
        renderer.draw(state)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
```
