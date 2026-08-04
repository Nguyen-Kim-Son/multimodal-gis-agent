import json
from pathlib import Path
import pandas as pd

def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def build_reports(results_path: str | Path, output_dir: str | Path) -> dict[str, Path]:
    results_path, output_dir = Path(results_path), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = _read_jsonl(results_path)
    flat = []
    for record in records:
        evaluation = record.get("evaluation") or {}
        response = record.get("response") or {}
        row = {
            "task_id": record["task_id"],
            "task_name": record["task_name"],
            "model": record["model"],
            "provider": record["provider"],
            "passed": evaluation.get("passed", False),
            "overall_score": evaluation.get("overall_score", 0.0),
            "latency_seconds": response.get("latency_seconds"),
            "total_tokens": response.get("total_tokens"),
            "cost_usd": response.get("cost_usd"),
            "error": record.get("error"),
        }
        for metric, score in (evaluation.get("scores") or {}).items():
            row[f"metric_{metric}"] = score
        flat.append(row)
    frame = pd.DataFrame(flat)
    csv_path = output_dir / "results.csv"
    frame.to_csv(csv_path, index=False)
    summary = {
        "num_tasks": int(len(frame)),
        "success_rate": float(frame["passed"].mean()) if len(frame) else 0.0,
        "mean_score": float(frame["overall_score"].mean()) if len(frame) else 0.0,
        "mean_latency_seconds": float(frame["latency_seconds"].dropna().mean()) if len(frame) and frame["latency_seconds"].notna().any() else None,
        "total_tokens": int(frame["total_tokens"].fillna(0).sum()) if len(frame) else 0,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    latex_path = output_dir / "summary_table.tex"
    latex_path.write_text(
        "\\begin{tabular}{lr}\n\\toprule\nMetric & Value \\\\\n\\midrule\n"
        f"Tasks & {summary['num_tasks']} \\\\\n"
        f"Success rate & {summary['success_rate']:.3f} \\\\\n"
        f"Mean score & {summary['mean_score']:.3f} \\\\\n"
        "\\bottomrule\n\\end{tabular}\n",
        encoding="utf-8",
    )
    return {"csv": csv_path, "summary": summary_path, "latex": latex_path}
