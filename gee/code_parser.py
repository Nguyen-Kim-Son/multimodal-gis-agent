import re

def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"```(?P<language>[a-zA-Z0-9_+-]*)\s*\n(?P<code>.*?)```", re.DOTALL)
    return [(m.group("language").lower(), m.group("code").strip()) for m in pattern.finditer(text)]
