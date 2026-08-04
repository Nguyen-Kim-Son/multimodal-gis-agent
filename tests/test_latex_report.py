import pandas as pd

from experiments.report import model_summary_to_latex


def test_latex_generation_without_jinja2():
    frame = pd.DataFrame(
        [
            {
                "model_key": "qwen_model",
                "mean_score": 0.75,
                "pass_rate": 0.5,
                "mean_latency_seconds": 1.25,
                "failure_rate": 0.0,
            }
        ]
    )

    latex = model_summary_to_latex(frame)

    assert "\\begin{tabular}" in latex
    assert "qwen\\_model" in latex
    assert "0.750" in latex
