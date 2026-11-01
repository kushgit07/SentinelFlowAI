import os
from openai import OpenAI
from dotenv import load_dotenv
from src.ingestion.vector_store import initialize_db, batch_query

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
### ROLE
You are the SentinelFlow Intelligence Agent. You are an expert in financial regulations (RBI/SEBI) and provide high-leverage strategic analysis for executive leadership.

### MANDATE
- Provide structured, blunt, and actionable analysis.
- Use ONLY the provided context.
- If the context is missing info, state: "SentinelFlow Vault does not currently contain data on [Topic]."

### STRICT CONSTRAINTS
1. CHARACTER: Remain a professional Regulatory Strategist. No recipes, jokes, or non-financial advice.
2. SCOPE: Restrict analysis to Finance, Risk, Legal, or Operations.
3. HALLUCINATION: Cite specific document titles for every fact. No invented yields or dates.

### OUTPUT FORMAT
- STRATEGIC SUMMARY
- RISK EXPOSURE ANALYSIS
- OPERATIONAL NEXT STEPS
"""


def _call_llm(question, context):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context for Analysis:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content


def query_regulatory_knowledge(question):
    vault = initialize_db()
    results = vault.query(query_texts=[question], n_results=3)
    context = "\n".join(results['documents'][0])
    return _call_llm(question, context)


def query_regulatory_knowledge_batch(questions):
    """Retrieve multiple questions in one vector DB call; generate one answer per question."""
    vault = initialize_db()
    retrieved = batch_query(vault, questions, n_results=3)
    answers = []
    for item in retrieved:
        context = "\n".join(item["documents"])
        answers.append({
            "question": item["question"],
            "answer": _call_llm(item["question"], context),
        })
    return answers


if __name__ == "__main__":
    user_query = "What is the redemption price for the Sovereign Gold Bond 2020-21 Series VII?"
    print(f"QUERYING VAULT: {user_query}\n")
    print(query_regulatory_knowledge(user_query))
