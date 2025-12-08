# noon_noon (👁️__👁️)

<div align="center">
  <img src="assets/preview.png" width="80%" alt="noon_noon Preview" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <br>
  
  [![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
  [![uv](https://img.shields.io/badge/uv-fast-purple)](https://github.com/astral-sh/uv)
  [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

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
   * **Motor Agnostic:** Works with or without physical motors. The simulation layer visualizes physical movements (Neck Pan/Tilt) on screen.

   ### Features
   * **Binocular Rendering:** Independent control for left/right eyes with adjustable IPD.
   * **Geometric Flexibility:** Support for Eye Eccentricity (Round ↔ Ellipse) to define character personality.
   * **On-Screen Configurator:** Built-in UI sliders to tune parameters in real-time.
   * **Hardware Abstraction:** "Digital Twin" HUD displays motor states even without physical servos.

   ### Prerequisites
   This project uses **[uv](https://github.com/astral-sh/uv)** for extremely fast package management.
   * **Python:** 3.12+
   * **Package Manager:** uv

   ### Installation & Setup

   1. **Clone the repository**
      ```bash
      git clone [https://github.com/your-username/noon_noon.git](https://github.com/your-username/noon_noon.git)
      cd noon_noon
      ```

   2. **Install Dependencies**
      `uv` will automatically create a virtual environment and install the locked dependencies.
      ```bash
      uv sync
      ```

   ### How to Run

   Execute the main application using `uv`:

   ```bash
   uv run main.py
   ```

   ### Controls
   * **Mouse Move:** Controls the gaze direction (`pupil_x`, `pupil_y`).
   * **Mouse Click:** Blinks the eyes (`eyelid` close/open).
   * **Keyboard (← / →):** Simulates the robot's neck rotation (`head_pan`).
   * **UI Sliders:** Adjust eye shape, pupil size, and eyelid levels in real-time.

   ---

   <div align="center">
   <hr width="50%">
   </div>

   <a name="korean"></a>
   ## 🇰🇷 한국어

   ### 프로젝트 소개
   **noon_noon(눈눈)**은 특정 하드웨어에 종속되지 않는 범용 로봇 눈 표현 라이브러리입니다.
   화면 해상도나 모터의 유무와 관계없이, 일관된 감정과 시선을 표현하기 위해 설계되었습니다.

   ### 핵심 철학
   * **Ratio over Pixel:** 좌표는 픽셀이 아닌 비율(`-1.0` ~ `1.0`)로 소통합니다.
   * **Config over Code:** 코드를 수정하는 대신, 파라미터 값만으로 다양한 디자인을 만듭니다.
   * **Motor Agnostic:** 모터가 없어도 화면 내 시뮬레이션(HUD)을 통해 물리적 움직임의 논리를 검증할 수 있습니다.

   ### 주요 기능
   * **양안(Binocular) 렌더링:** 두 개의 눈을 독립적으로 제어하며, 눈 사이 간격 등을 조절할 수 있습니다.
   * **형태 가변성 (Eccentricity):** 이심률 조절을 통해 원형부터 타원형까지 다양한 캐릭터 성격을 부여합니다.
   * **실시간 설정 UI:** 프로그램 실행 중 슬라이더를 통해 눈의 모양과 크기를 즉시 튜닝할 수 있습니다.
   * **디지털 트윈:** 물리 모터가 없는 환경에서도 목 회전(Pan) 등의 움직임을 시각화합니다.

   ### 개발 환경 설정
   이 프로젝트는 초고속 Python 패키지 관리자인 **[uv](https://github.com/astral-sh/uv)**를 사용합니다.

   1. **레포지토리 복제**
      ```bash
      git clone [https://github.com/your-username/noon_noon.git](https://github.com/your-username/noon_noon.git)
      cd noon_noon
      ```

   2. **의존성 설치**
      `uv`가 자동으로 가상환경을 생성하고 필요한 라이브러리(Pygame 등)를 설치합니다.
      ```bash
      uv sync
      ```

   ### 실행 방법

   아래 명령어로 바로 실행할 수 있습니다.

   ```bash
   uv run main.py
   ```

   ### 조작 방법
   * **마우스 이동:** 로봇의 시선(`pupil_x`, `pupil_y`)이 마우스를 따라갑니다.
   * **마우스 클릭:** 눈을 깜빡입니다.
   * **키보드 방향키 (← / →):** 로봇의 목 회전(`head_pan`)을 시뮬레이션합니다 (화면 하단 붉은 인디케이터 확인).
   * **좌측 UI 슬라이더:** 눈의 찌그러짐 정도(이심률), 동공 크기 등을 실시간으로 조절합니다.
</div>
