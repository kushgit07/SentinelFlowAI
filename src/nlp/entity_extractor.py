"""Rule-based financial entity extraction for RBI / regulatory press releases."""
import re

_MONETARY_AMOUNT = re.compile(r"₹\s?[\d,]+(?:\.\d+)?\s?(?:Crore|crore|Lakh|lakh)?(?:/-)?")
_PERCENTAGE = re.compile(r"\d+(?:\.\d+)?\s?(?:per\s*cent|percent|%)")
_TENOR = re.compile(r"\b\d+-Day\b")
_DATE = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}\b")
_REGULATORY_CITATION = re.compile(r"Section\s+\d+[A-Za-z]?\s+of\s+the\s+[A-Z][A-Za-z ,]+?\sAct,\s*\d{4}")
_LEGAL_REFERENCE = re.compile(r"\b[A-Z][A-Za-z]*(?:\s[A-Z][A-Za-z]*){0,5}\s(?:Act|Regulations),\s*\d{4}")
_CIRCULAR_REFERENCE = re.compile(r"\bRBI/\d{4}-\d{2,4}/\d+\b")

_INSTRUMENTS = [
    "Sovereign Gold Bond", "SGB", "Treasury Bills", "Treasury Bill",
    "Government Securities", "State Government Securities", "G-Sec",
    "Cash Management Bills", "Floating Rate Bonds",
]
_ORGANIZATIONS = [
    "Reserve Bank of India", "RBI", "Public Debt Office", "IBJA",
    "SEBI", "NBFC", "Retail Direct",
]

def _find_keyword_entities(text, keywords, entity_type):
    entities = []
    for keyword in keywords:
        for match in re.finditer(re.escape(keyword), text):
            entities.append({
                "text": match.group(), "type": entity_type,
                "start": match.start(), "end": match.end(),
            })
    return entities

def _find_pattern_entities(text, pattern, entity_type):
    return [
        {"text": match.group().strip(), "type": entity_type, "start": match.start(), "end": match.end()}
        for match in pattern.finditer(text)
    ]

def extract_entities(text):
    """Return extracted entities sorted by source position, deduplicating overlaps."""
    entities = []
    for pattern, label in [
        (_MONETARY_AMOUNT, "MONETARY_AMOUNT"), (_PERCENTAGE, "PERCENTAGE"),
        (_TENOR, "TENOR"), (_DATE, "DATE"),
        (_REGULATORY_CITATION, "REGULATORY_CITATION"),
        (_LEGAL_REFERENCE, "LEGAL_REFERENCE"),
        (_CIRCULAR_REFERENCE, "CIRCULAR_REFERENCE"),
    ]:
        entities += _find_pattern_entities(text, pattern, label)
    entities += _find_keyword_entities(text, _INSTRUMENTS, "INSTRUMENT")
    entities += _find_keyword_entities(text, _ORGANIZATIONS, "ORGANIZATION")
    by_start = {}
    for entity in entities:
        current = by_start.get(entity["start"])
        if current is None or entity["end"] - entity["start"] > current["end"] - current["start"]:
            by_start[entity["start"]] = entity
    return sorted(by_start.values(), key=lambda entity: entity["start"])

def extract_entities_grouped(text):
    """Return entities grouped by type for API responses."""
    grouped = {}
    for entity in extract_entities(text):
        grouped.setdefault(entity["type"], []).append(entity["text"])
    return grouped
