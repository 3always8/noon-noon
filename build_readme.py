# build_readme.py
import re

def get_example_code():
    """ rpi_example.py에서 # README_EXAMPLE_START/END 사이의 코드를 추출합니다. """
    with open("rpi_example.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 정규 표현식을 사용하여 마커 사이의 내용을 찾습니다.
    match = re.search(r"# README_EXAMPLE_START\n(.*?)\n# README_EXAMPLE_END", content, re.DOTALL)
    if not match:
        raise ValueError("Could not find README example markers in rpi_example.py")
    
    return match.group(1).strip()

def build():
    """ README.template.md를 기반으로 최종 README.md를 생성합니다. """
    with open("README.template.md", "r", encoding="utf-8") as f:
        template = f.read()

    example_code = get_example_code()
    
    # 마크다운 코드 블록으로 포맷합니다.
    formatted_code = f"```python\n{example_code}\n```"
    
    # 템플릿의 플레이스홀더를 실제 코드로 교체합니다.
    final_readme = template.replace("<!-- CODE_EXAMPLE_PLACEHOLDER -->", formatted_code)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(final_readme)
    
    print("✅ README.md has been successfully updated.")

if __name__ == "__main__":
    build()

