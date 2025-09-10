# evals/eval.py
from __future__ import annotations
import json, time, statistics, pathlib, sys
from typing import Dict, List

# Asigură importurile indiferent de unde rulezi
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.pipelines.redact import redact_pii
from app.pipelines.classify import classify_text
from app.pipelines.summarize import summarize_text
from app.pipelines.actions import suggest_actions
from app.schemas import AnalyzeResponse

SAMPLES_PATH = ROOT / "evals" / "samples.jsonl"
REPORT_PATH  = ROOT / "evals" / "eval_report.json"

PII_MARKERS = {
    "email":   "[EMAIL]",
    "phone":   "[PHONE]",
    "iban":    "[IBAN]",
    "cnp":     "[CNP]",
    "address": "[ADDRESS]",
}

def run_pipeline(text: str) -> Dict:
    t0 = time.perf_counter()
    red = redact_pii(text)
    category = classify_text(red) or "other"
    summary = summarize_text(red, max_words=30)
    actions = suggest_actions(category, red)
    # validare JSON cu schema (ridică eroare dacă nu e valid)
    resp = AnalyzeResponse(
        redacted_text=red,
        category=category,
        summary=summary,
        actions=actions,
    )
    t1 = time.perf_counter()
    return {"resp": resp.model_dump(), "latency_ms": (t1 - t0) * 1000.0}

def load_samples(path: pathlib.Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

def main():
    samples = load_samples(SAMPLES_PATH)

    n = len(samples)
    json_valid = 0
    correct = 0
    latencies: List[float] = []

    # PII recall counters
    pii_found: Dict[str, int] = {k: 0 for k in PII_MARKERS.keys()}
    pii_expected: Dict[str, int] = {k: 0 for k in PII_MARKERS.keys()}

    rows_out: List[Dict] = []

    for s in samples:
        text = s["text"]
        label = s["label"]
        pii_list = s.get("pii", [])

        try:
            out = run_pipeline(text)
            data = out["resp"]
            latencies.append(out["latency_ms"])
            json_valid += 1

            # accuracy
            if data["category"] == label:
                correct += 1

            # pii recall by type
            red_text = data["redacted_text"].lower()
            for t in pii_list:
                pii_expected[t] += 1
                marker = PII_MARKERS[t].lower()
                if marker in red_text:
                    pii_found[t] += 1

            rows_out.append({
                "label": label,
                "pred": data["category"],
                "latency_ms": round(out["latency_ms"], 2),
                "redacted_text": data["redacted_text"],
                "summary": data["summary"],
                "actions": data["actions"],
            })
        except Exception as e:
            rows_out.append({"error": str(e), "text": text})

    accuracy = correct / n if n else 0.0
    json_validity = json_valid / n if n else 0.0
    median_latency = float(statistics.median(latencies)) if latencies else 0.0

    # compute recall per type and overall
    recall_by_type: Dict[str, float] = {}
    tot_found = 0
    tot_expected = 0
    for t in PII_MARKERS.keys():
        exp = pii_expected[t]
        got = pii_found[t]
        tot_expected += exp
        tot_found += got
        recall_by_type[t] = (got / exp) if exp else 1.0  # dacă nu așteptăm nimic, îl considerăm 1.0

    overall_recall = (tot_found / tot_expected) if tot_expected else 1.0

    report = {
        "num_samples": n,
        "json_validity": round(json_validity, 4),
        "category_accuracy": round(accuracy, 4),
        "pii_recall_by_type": {k: round(v, 4) for k, v in recall_by_type.items()},
        "pii_recall_overall": round(overall_recall, 4),
        "median_latency_ms": round(median_latency, 2),
        "rows": rows_out[:5],  # primele 5 pentru inspecție rapidă
    }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # print scurt în terminal
    print("\nEVAL SUMMARY")
    print("============")
    print(f"samples               : {n}")
    print(f"json_validity         : {report['json_validity']*100:.1f}%")
    print(f"category_accuracy     : {report['category_accuracy']*100:.1f}%")
    print(f"pii_recall_overall    : {report['pii_recall_overall']*100:.1f}%")
    print("pii_recall_by_type    :", report["pii_recall_by_type"])
    print(f"median_latency_ms     : {report['median_latency_ms']}")
    print(f"\nSaved report → {REPORT_PATH}")

if __name__ == "__main__":
    main()
