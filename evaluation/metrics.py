import re

def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold().strip())

def exact_match(prediction: str, expected: str | None) -> float:
    return 0.0 if expected is None else float(normalize_text(prediction) == normalize_text(expected))

def keyword_coverage(prediction: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    normalized = normalize_text(prediction)
    return sum(normalize_text(k) in normalized for k in keywords) / len(keywords)

def code_presence(prediction: str) -> float:
    return float(any(signal in prediction for signal in ("```", "ee.Image", "ee.ImageCollection", "Map.addLayer", "import ee")))
