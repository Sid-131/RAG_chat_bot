"""
answer_eval.py
--------------
Evaluates answer quality against the 30-question golden QA dataset.

Metrics:
  - Source link inclusion:  regex check for URL in every answer (target 100%)
  - 3-sentence constraint:  sentence count ≤ 3 for every answer  (target 100%)
  - Answer faithfulness:    LLM-as-judge prompt                  (target ≥ 90%)

Usage:
    python evaluation/answer_eval.py --dataset data/golden_qa.json
"""

import argparse
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# TODO: Implement answer quality evaluation
# ---------------------------------------------------------------------------

def evaluate(dataset_path: Path) -> dict:
    """
    For each golden QA item, generate an answer and score it.

    Returns:
        {
          'citation_rate':    float,
          'sentence_rate':    float,
          'faithfulness_rate': float,
        }
    """
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/golden_qa.json")
    args = parser.parse_args()

    metrics = evaluate(Path(args.dataset))
    print(json.dumps(metrics, indent=2))
