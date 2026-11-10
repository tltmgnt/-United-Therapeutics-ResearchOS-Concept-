"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")

def sample(path):
    return json.loads((ROOT / path).read_text())



def run():
    from therapeutics_research.dossier import evaluate
    data = sample("examples/dossier.json")
    r = evaluate(data)
    summary = r["assay"]["summary"]
    check("control mean from 1 and 3", summary["groups"]["control"]["mean"], 2)
    check("control sample variance", summary["groups"]["control"]["sample_variance"], 2)
    check("test mean", summary["groups"]["test"]["mean"], 5)
    check("descriptive mean difference", summary["treatment_minus_control_mean"], 3)
    check("review remains missing", "HUMAN_REVIEW_MISSING" in r["claims"]["summary-claim"]["blockers"], True)
    bad = copy.deepcopy(data); bad["artifacts"][0]["context"]["unit"] = "different_unit"
    q = evaluate(bad)
    check("context mismatch blocks assay", q["assay"]["status"], "blocked")
    check("no scientific validation inferred", r["scientific_validity_established"], False)
    check("no company relationship inferred", r["company_affiliation_established"], False)

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
