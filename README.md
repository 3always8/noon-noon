# noon_noon (👁️__👁️)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-fast-purple)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

<div align="center">
  <img src="assets/preview.png" width="80%" alt="noon_noon Preview" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <br>
  <p><em>(Note: The preview image may not reflect the latest UI.)</em></p>
</div>


**noon_noon** is a universal, hardware-agnostic robot eye expression library for Python.  
It provides a high-level controller to easily render dynamic, emotional eyes, abstracting away complex state management and rendering logic.

> **Navigation:**
> [🇺🇸 English](#english) | [🇰🇷 한국어](#korean)

---

<a name="english"></a>
## 🇺🇸 English

### Core Philosophy
* **Simple API:** A high-level `Noon` controller class handles all the complexity. You only need to call `set_emotion()`, `update()`, and `draw()`.
* **Data-Driven:** Emotions and dynamic effects (like shaking) are defined in a simple preset file, allowing for easy customization without changing library code.
* **Hardware Agnostic:** The core logic is independent of physical hardware, making it adaptable to any screen-based project (Raspberry Pi, desktop, etc.).

### Features
* **High-Level Controller:** The `Noon` class encapsulates all necessary components (`engine`, `renderer`, `state`).
* **Emotion Preset System:** Easily switch between pre-defined emotions. Adding new emotions is as simple as editing the `presets.py` file.
* **Dynamic Effects:** The preset system supports defining dynamic animations, such as the shaking effect for the "angry" emotion.
* **Smooth Transitions:** Built-in logic for smooth interpolation between different emotional states.

### How to Use `noon_noon`

This project uses **[uv](https://github.com/astral-sh/uv)** for package management.

1. **Clone & Install**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **Run the Demo**
   This runs an application with UI controls for testing.
   ```bash
   uv run main.py
   ```

### Using as a Library (Recommended)

The intended use of `noon_noon` is as a library in your own project. The `Noon` controller makes this incredibly simple.

**Example (`rpi_example.py`):**

The following example shows how to switch between "neutral" and "angry" expressions by pressing 'n' and 'a' on the keyboard. You can find this file in the repository.

```python
import pygame
import sys
from noon import Noon  # Import the main controller

def main():
    # 1. Initialize Pygame and a screen
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()

    # 2. Initialize the Noon controller (just one line)
    eyes = Noon(screen)

    print("App running... Press 'n' for neutral, 'a' for angry. Press 'q' to quit.")

    # 3. Main application loop
    running = True
    while running:
        # --- Handle your inputs (e.g., GPIO, keyboard) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    eyes.set_emotion("angry") # Simply set the desired emotion
                elif event.key == pygame.K_n:
                    eyes.set_emotion("neutral")
        
        # --- Update and Render ---
        screen.fill((0, 0, 0))  # Clear screen with your background color
        
        eyes.update()  # Update all internal states, transitions, and effects
        eyes.draw()    # Draw the eyes to the screen
        
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
* **단순한 API:** `Noon` 컨트롤러 클래스가 모든 복잡성을 관리합니다. `set_emotion()`, `update()`, `draw()`만 호출하면 됩니다.
* **데이터 기반 설계:** 감정과 동적 효과(떨림 등)가 간단한 프리셋 파일에 정의되어 있어, 라이브러리 코드 수정 없이 쉽게 커스터마이징할 수 있습니다.
* **하드웨어 독립성:** 핵심 로직이 물리 하드웨어와 독립적이므로, 어떤 스크린 기반 프로젝트(라즈베리파이, 데스크탑 등)에도 적용할 수 있습니다.

### 주요 기능
* **고수준 컨트롤러:** `Noon` 클래스가 `engine`, `renderer`, `state` 등 모든 필요 컴포넌트를 캡슐화합니다.
* **감정 프리셋 시스템:** 미리 정의된 감정들을 쉽게 전환할 수 있습니다. `presets.py` 파일 수정만으로 새로운 감정을 간단히 추가할 수 있습니다.
* **동적 효과:** 프리셋 시스템을 통해 'angry' 감정의 떨림 효과와 같은 동적 애니메이션을 정의하고 적용할 수 있습니다.
* **부드러운 전환:** 서로 다른 감정 상태를 부드럽게 보간하는 로직이 내장되어 있습니다.

### `noon_noon` 사용법

이 프로젝트는 **[uv](https://github.com/astral-sh/uv)**를 사용하여 패키지를 관리합니다.

1. **클론 및 설치**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **데모 실행**
   테스트용 UI 컨트롤이 포함된 애플리케이션을 실행합니다.
   ```bash
   uv run main.py
   ```

### 라이브러리로 사용하기 (권장)

`noon_noon`은 당신의 프로젝트에서 라이브러리로 사용하는 것을 권장합니다. `Noon` 컨트롤러는 이 과정을 매우 간단하게 만들어줍니다.

**사용 예제 (`rpi_example.py`):**

아래 예제는 키보드의 'n'키와 'a'키를 눌러 'neutral'과 'angry' 표정을 전환하는 방법을 보여줍니다. 이 파일은 레포지토리 내에서 직접 확인할 수 있습니다.

```python
import pygame
import sys
from noon import Noon  # 메인 컨트롤러 임포트

def main():
    # 1. Pygame 및 스크린 초기화
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()

    # 2. Noon 컨트롤러 초기화 (단 한 줄)
    eyes = Noon(screen)

    print("App running... Press 'n' for neutral, 'a' for angry. Press 'q' to quit.")

    # 3. 메인 애플리케이션 루프
    running = True
    while running:
        # --- 입력 처리 (예: GPIO, 키보드) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    eyes.set_emotion("angry") # 원하는 감정을 간단히 설정
                elif event.key == pygame.K_n:
                    eyes.set_emotion("neutral")
        
        # --- 업데이트 및 렌더링 ---
        screen.fill((0, 0, 0))  # 원하는 배경색으로 스크린 채우기
        
        eyes.update()  # 모든 내부 상태, 전환, 효과를 업데이트
        eyes.draw()    # 스크린에 눈 그리기
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
```