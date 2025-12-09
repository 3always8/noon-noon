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
It provides a high-level controller that abstracts away all Pygame boilerplate, allowing you to render dynamic, emotional eyes with just a few lines of code.

> **Navigation:**
> [🇺🇸 English](#english) | [🇰🇷 한국어](#korean)
>
> **Note for Developers:** To update this README, please edit `README.template.md` and then run `uv run python build_readme.py`.

---

<a name="english"></a>
## 🇺🇸 English

### Core Philosophy
* **Zero Boilerplate:** The high-level `Noon` controller handles the Pygame loop, event handling, and rendering, so you don't have to.
* **Simple API:** A clean API lets you `set_emotion()` and register callbacks like `on_key_press()` without needing to know the internal details.
* **Data-Driven:** Emotions and dynamic effects (like shaking) are defined in a simple preset file, allowing for easy customization without changing library code.

### Features
* **High-Level Controller:** The `Noon` class encapsulates the entire application lifecycle.
* **Callback-Based Events:** Easily hook into keyboard events to control expressions without writing a Pygame event loop.
* **Emotion Preset System:** Easily switch between pre-defined emotions. Adding new emotions is as simple as editing the `presets.py` file.
* **Dynamic Effects:** The preset system supports defining dynamic animations, such as the shaking effect for the "angry" emotion.

### How to Use `noon_noon`

This project uses **[uv](https://github.com/astral-sh/uv)** for package management.

1. **Clone & Install**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **Run the Demo**
   This runs an application with UI controls for advanced testing.
   ```bash
   uv run main.py
   ```

### Using as a Library (Recommended)

The intended use of `noon_noon` is as a library in your own project. The `Noon` controller makes this incredibly simple, abstracting away all Pygame logic.

**Example (`rpi_example.py`):**

The following example shows how to switch between "neutral" and "angry" expressions by pressing 'n' and 'a'. The `Noon` object handles the entire window and event loop. The code below is sourced directly from `rpi_example.py`.

<!-- CODE_EXAMPLE_PLACEHOLDER -->

### Advanced Usage (Manual Loop)
If you need to integrate `noon_noon` into an existing Pygame loop, you can still manage the loop yourself. In this case, you would call `eyes.update()` and `eyes.draw()` manually each frame. See `main.py` for a detailed example of this advanced use case.

---

<div align="center">
<hr width="50%">
</div>

<a name="korean"></a>
## 🇰🇷 한국어

### 핵심 철학
* **제로 보일러플레이트:** `Noon` 컨트롤러가 Pygame 루프, 이벤트 처리, 렌더링을 모두 담당하므로, 사용자는 복잡한 초기 설정 코드를 작성할 필요가 없습니다.
* **단순한 API:** `set_emotion()`으로 감정을 설정하고 `on_key_press()`로 콜백을 등록하는 등, 내부 구조를 몰라도 되는 깔끔한 API를 제공합니다.
* **데이터 기반 설계:** 감정과 동적 효과(떨림 등)가 간단한 프리셋 파일에 정의되어 있어, 라이브러리 코드 수정 없이 쉽게 커스터마이징할 수 있습니다.

### 주요 기능
* **고수준 컨트롤러:** `Noon` 클래스가 애플리케이션의 전체 생명주기를 캡슐화합니다.
* **콜백 기반 이벤트:** Pygame 이벤트 루프를 직접 작성할 필요 없이, 키보드 이벤트에 반응하는 함수를 간단히 연결하여 표정을 제어할 수 있습니다.
* **감정 프리셋 시스템:** 미리 정의된 감정들을 쉽게 전환할 수 있습니다. `presets.py` 파일 수정만으로 새로운 감정을 간단히 추가할 수 있습니다.
* **동적 효과:** 프리셋 시스템을 통해 'angry' 감정의 떨림 효과와 같은 동적 애니메이션을 정의하고 적용할 수 있습니다.

### `noon_noon` 사용법

이 프로젝트는 **[uv](https://github.com/astral-sh/uv)**를 사용하여 패키지를 관리합니다.

1. **클론 및 설치**
   ```bash
   git clone https://github.com/3always8/noon_noon.git
   cd noon_noon
   uv sync
   ```

2. **데모 실행**
   고급 테스트를 위한 UI 컨트롤이 포함된 애플리케이션을 실행합니다.
   ```bash
   uv run main.py
   ```

### 라이브러리로 사용하기 (권장)

`noon_noon`은 당신의 프로젝트에서 라이브러리로 사용하는 것을 권장합니다. `Noon` 컨트롤러는 모든 Pygame 로직을 추상화하여 이 과정을 매우 간단하게 만들어줍니다.

**사용 예제 (`rpi_example.py`):**

아래 예제는 키보드의 'n'키와 'a'키를 눌러 'neutral'과 'angry' 표정을 전환하는 방법을 보여줍니다. `Noon` 객체가 윈도우와 이벤트 루프 전체를 관리합니다. 아래 코드는 `rpi_example.py` 파일의 내용과 동일합니다.

<!-- CODE_EXAMPLE_PLACEHOLDER -->

### 고급 사용법 (수동 루프 제어)
만약 `noon_noon`을 기존 Pygame 루프에 통합해야 한다면, 직접 루프를 관리할 수도 있습니다. 이 경우, 매 프레임 `eyes.update()`와 `eyes.draw()`를 수동으로 호출해야 합니다. 이러한 고급 사용법에 대한 자세한 예시는 `main.py` 파일을 참고하세요.
