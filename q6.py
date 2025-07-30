# q6.py

import re
from langchain.schema import SystemMessage, HumanMessage

# === Q6 Constants ===
target_components = {
    "john": 1,
    "brown": 2,
    "42": 3,
    "market": 4,
    "chicago": 5
}
max_errors_q6 = 5

def is_clarifying_question_q6(text: str, llm) -> bool:
    # If user speaks 15+ words, flag as question
    if len(text.strip().split()) >= 15:
        return True

    prompt = """
    You are administering a cognitive test. 
    A patient responded after being asked to repeat the name and address they were told earlier.
    Determine if their response is a clarifying question (e.g., asking for instructions, help, or asking for the question again),
    not an attempt to recall the answer. Respond with only "yes" or "no".
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])
    if(result.content.strip().lower() == "yes"):
        print("Response classified as: Clarifying question")
    else:
        print("Response classified as: Attempt to answer question")
    return result.content.strip().lower() == "yes"

def respond_to_clarifying_question_q6(text: str, llm) -> str:
    prompt = """
    You are the administrator of a cognitive test. 
    The patient asked a clarifying question after being asked to repeat a name and address.
    Kindly explain that they should repeat the name and address that was provided earlier.
    Do not reveal the correct answer.
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])
    return result.content.strip()

def detect_forty_two(tokens: list[str]) -> bool:
    combined = " ".join(tokens)
    return bool(re.search(r"\bfort[yi]?[ -]?tw[o0]\b", combined))

def score_recall_response(response: str) -> tuple[int, list[int]]:
    # Tokenize and clean words
    tokens = re.findall(r'\b\w+\b', response.lower())
    matched_ids = []

    # Direct match lookup
    for word in tokens:
        for key, val in target_components.items():
            if word == key:
                matched_ids.append(val)

    # Detect "forty two" as equivalent to 42 if 3 not already found
    if 3 not in matched_ids and detect_forty_two(tokens):
        matched_ids.append(3)

    matched_ids = list(set(matched_ids))  # Remove duplicates
    matched_count = len(matched_ids)
    errors = max(0, len(target_components) - matched_count)
    score = min(errors * 2, 10)

    return score, matched_ids

def run_q6(llm, get_input=input, print_output=print):
    print_output("\n TEST: Repeat the name and address I asked you to remember.")

    while True:
        q6_response = get_input(" Your answer: ").strip()

        if is_clarifying_question_q6(q6_response, llm):
            reply = respond_to_clarifying_question_q6(q6_response, llm)
            print_output(f" ADMIN: {reply}")
            continue

        q6_score, matched_items = score_recall_response(q6_response)
        break

    print_output(" ADMIN: Thank you.")
    return q6_score


