"""
Measures entity-extraction accuracy against the hand-labeled set in
eval_set.json.

Scoring methodology: for each document, compare unique (text, type) gold
entities with predicted entities, then compute recall, precision and F1.
Exact string matching is used.

Run: python3 -m src.evaluation.run_eval
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.nlp.entity_extractor import extract_entities

EVAL_SET_PATH = os.path.join(os.path.dirname(__file__), "eval_set.json")


def score_document(doc):
    gold = {(e["text"], e["type"]) for e in doc["gold_entities"]}
    predicted = {(e["text"], e["type"]) for e in extract_entities(doc["text"])}
    true_positives = gold & predicted
    false_negatives = gold - predicted
    false_positives = predicted - gold
    recall = len(true_positives) / len(gold) if gold else 1.0
    precision = len(true_positives) / len(predicted) if predicted else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "id": doc["id"], "source": doc["source"],
        "gold_count": len(gold), "predicted_count": len(predicted),
        "true_positives": len(true_positives), "recall": recall,
        "precision": precision, "f1": f1,
        "false_negatives": sorted(false_negatives),
        "false_positives": sorted(false_positives),
    }


def run_eval(verbose=True):
    with open(EVAL_SET_PATH) as f:
        eval_set = json.load(f)
    results = [score_document(doc) for doc in eval_set["documents"]]
    total_gold = sum(r["gold_count"] for r in results)
    total_predicted = sum(r["predicted_count"] for r in results)
    total_tp = sum(r["true_positives"] for r in results)
    overall_recall = total_tp / total_gold if total_gold else 1.0
    overall_precision = total_tp / total_predicted if total_predicted else 1.0
    overall_f1 = (2 * overall_precision * overall_recall / (overall_precision + overall_recall)
                  if (overall_precision + overall_recall) else 0.0)
    if verbose:
        print(f"{'Document':<35} {'Gold':>5} {'Pred':>5} {'TP':>5} {'Recall':>8} {'Precision':>10} {'F1':>6}")
        for r in results:
            print(f"{r['id']:<35} {r['gold_count']:>5} {r['predicted_count']:>5} {r['true_positives']:>5} "
                  f"{r['recall']:>8.1%} {r['precision']:>10.1%} {r['f1']:>6.1%}")
        print("-" * 90)
        print(f"{'OVERALL':<35} {total_gold:>5} {total_predicted:>5} {total_tp:>5} "
              f"{overall_recall:>8.1%} {overall_precision:>10.1%} {overall_f1:>6.1%}")
        for r in results:
            if r["false_negatives"]:
                print(f"[{r['id']}] MISSED: {r['false_negatives']}")
            if r["false_positives"]:
                print(f"[{r['id']}] SPURIOUS: {r['false_positives']}")
    return {"per_document": results, "overall_recall": overall_recall,
            "overall_precision": overall_precision, "overall_f1": overall_f1,
            "total_gold_entities": total_gold}


if __name__ == "__main__":
    run_eval()
