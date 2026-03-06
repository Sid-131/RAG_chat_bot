"""
retrieval_eval.py
-----------------
Evaluates retrieval quality on the 30-question golden QA dataset.

Metrics computed:
  - Recall@5:      is the correct chunk present in the top-5 results?
  - MRR:           Mean Reciprocal Rank
  - Precision@1:   is the top result the correct chunk?

Target thresholds (from architecture):
  Recall@5 ≥ 0.85  |  MRR ≥ 0.75  |  Precision@1 ≥ 0.70

Usage:
    python evaluation/retrieval_eval.py --dataset data/golden_qa.json
"""

import argparse
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# TODO: Implement retrieval evaluation
# ---------------------------------------------------------------------------

def load_golden_qa(path: Path) -> list[dict]:
    """Load the golden QA JSON file."""
    with open(path) as f:
        return json.load(f)


def evaluate(dataset_path: Path) -> dict:
    """
    Run retrieval on each golden question and compute metrics.

    Returns:
        { 'recall_at_5': float, 'mrr': float, 'precision_at_1': float }
    """
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/golden_qa.json")
    args = parser.parse_args()

    metrics = evaluate(Path(args.dataset))
    print(json.dumps(metrics, indent=2))
