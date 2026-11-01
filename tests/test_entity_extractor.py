import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.nlp.entity_extractor import extract_entities, extract_entities_grouped

def test_monetary_amount_with_crore():
    entities = extract_entities("the aggregate amount of ₹11,500 Crore (Face Value)")
    assert "₹11,500 Crore" in [e["text"] for e in entities if e["type"] == "MONETARY_AMOUNT"]

def test_percentage():
    entities = extract_entities("restricted to a maximum of 5 percent")
    assert "5 percent" in [e["text"] for e in entities if e["type"] == "PERCENTAGE"]

def test_tenor_pattern():
    entities = extract_entities("Auction of 91-Day, 182-Day and 364-Day Treasury Bills")
    assert {e["text"] for e in entities if e["type"] == "TENOR"} == {"91-Day", "182-Day", "364-Day"}

def test_regulatory_citation():
    entities = extract_entities("under Section 24 of the Banking Regulation Act, 1949.")
    assert any("Section 24" in e["text"] for e in entities if e["type"] == "REGULATORY_CITATION")

def test_circular_reference():
    entities = extract_entities("circular RBI/2025-26/45 dated November 12, 2025")
    assert "RBI/2025-26/45" in [e["text"] for e in entities if e["type"] == "CIRCULAR_REFERENCE"]

def test_dedup_keeps_unique_start_positions():
    entities = extract_entities("Sovereign Gold Bond Scheme")
    starts = [e["start"] for e in entities]
    assert len(starts) == len(set(starts))

def test_empty_text():
    assert extract_entities("") == []

def test_grouped_output_shape():
    grouped = extract_entities_grouped("₹500 Crore was raised by RBI on April 1, 2026.")
    assert isinstance(grouped, dict)
    assert all(isinstance(value, list) for value in grouped.values())

if __name__ == "__main__":
    import inspect
    tests = [(name, fn) for name, fn in inspect.getmembers(sys.modules[__name__], inspect.isfunction) if name.startswith("test_")]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as exc:
            print(f"FAIL  {name}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
