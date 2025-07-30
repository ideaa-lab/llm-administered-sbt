# q5.py

import difflib
from langchain.schema import SystemMessage, HumanMessage

correct_sequence = list(range(12, 0, -1))  # [12, 11, ..., 1]

def is_clarifying_question(text: str, llm) -> bool:
    prompt = """
    Respond YES if Asks any sort of question, question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'what format', 'why?', etc.) or a clarifying question.
    Respond NO for anything else

    Respond only with "yes" or "no", do not include quotation marks or anything else.
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])

    if(result.content.strip().lower() == "yes"):
        print("Response classified as: Clarifying question")
    else:
        print("Response classified as: Attempt")
        
    return result.content.strip().lower() == "yes"

def respond_to_clarifying_question(text: str, llm) -> str:
    prompt = """
    You are the administrator of a cognitive test. The patient asked a clarifying question about saying months in reverse order.
    Kindly explain and redirect them to try again, starting with December. Do not provide the answer or any other months. Tell them to start with December, always! Tell them to "Try saying the months backward beginning with December."
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])
    return result.content.strip()

def parse_each_word_to_month_number(response: str, llm) -> list:
    words = response.strip().split()
    parsed_numbers = []

    for word in words:
        prompt = f"""
        You are classifying a single word as part of a cognitive screening test. 
        Your task is to determine if this word refers to a month of the year (even with misspellings or abbreviations like for september: sep, sept, 9, S, sepetemba, etc.). 
        Respond with the numeric month (e.g., "1" for January, "12" for December). 
        If it does not clearly refer to a month, respond with "0". 
        Do NOT explain.
        Word: {word}
        """
        result = llm.invoke([SystemMessage(content=prompt.strip())])
        try:
            parsed = int(result.content.strip())
        except:
            parsed = 0
        parsed_numbers.append(parsed)

    return parsed_numbers

def clean_month_sequence(parsed: list[int]) -> list[int]:
    # Remove all zeros
    parsed = [p for p in parsed if p != 0]

    # Remove repeating 12s after the first one
    cleaned = []
    found_first_12 = False
    for val in parsed:
        if val == 12:
            if not found_first_12:
                cleaned.append(val)
                found_first_12 = True
            # Skip subsequent 12s
        else:
            cleaned.append(val)

    # Remove extra 1s that appear before the final position
    if cleaned.count(1) > 1:
        first_1_idx = cleaned.index(1)
        cleaned = [val for i, val in enumerate(cleaned) if val != 1 or i == len(cleaned) - 1]

    return cleaned

def count_month_errors(parsed: list[int], correct: list[int]) -> int:
    if parsed == correct:
        return 0

    if len(parsed) < 11 or all(p == 0 for p in parsed):
        return 2
    
    parsed = [p for p in parsed if p != 0]

    parsed = clean_month_sequence(parsed)


    # Count how many values are incorrect by position
    position_errors = sum(1 for a, b in zip(parsed, correct) if a != b)

    # Count inversions (pairs out of order)
    inversions = 0
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if parsed[i] > parsed[j]:
                inversions += 1

    # Accept 1 misplaced value or 1 inversion
    if position_errors == 1 or inversions == 1:
        return 1

    # Accept a clean 2-element swap
    wrong_positions = [(i, a, b) for i, (a, b) in enumerate(zip(parsed, correct)) if a != b]
    if len(wrong_positions) == 2:
        a1, b1 = wrong_positions[0][1], wrong_positions[0][2]
        a2, b2 = wrong_positions[1][1], wrong_positions[1][2]
        if a1 == b2 and a2 == b1:
            return 1

    # Handle one missing value (off-by-one length)
    if abs(len(parsed) - len(correct)) == 1:
        trimmed_errors = sum(1 for a, b in zip(parsed, correct) if a != b)
        if trimmed_errors <= 1:
            return 1

    # Use difflib to compare similarity ratio
    ratio = difflib.SequenceMatcher(None, parsed, correct).ratio()
    if ratio > 0.9:
        return 1

    return 2

def run_q5(llm, get_input=input, print_output=print):
    print_output("\n TEST: Say the months of the year in reverse order.")
    print_output(" ADMIN: Start with the last month of the year.")

    month_errors = 0
    already_prompted_forward = False

    while month_errors < 2:
        response = get_input("👉 Your answer: ").strip()

        if is_clarifying_question(response, llm):
            reply = respond_to_clarifying_question(response, llm)
            print_output(f"ADMIN: {reply}")
            continue

        parsed = parse_each_word_to_month_number(response, llm)
        parsed = [p for p in parsed if p != 0]
        #print_output(f"[DEBUG] Parsed as: {parsed}")

        if not already_prompted_forward:
            if len(parsed) < 2 or parsed[0] != 12 or parsed[1] not in [11, 10]:
                already_prompted_forward = True
                print_output(" ADMIN: Let’s start again. Try saying the months backward beginning with December.")
                continue

        month_errors = count_month_errors(parsed, correct_sequence)
        break

    print_output(" ADMIN: Thank you. Let's move on to the next question.")
    return min(month_errors, 2) * 2

'''
import difflib
from langchain.schema import SystemMessage, HumanMessage

# === Q5 Constants ===
correct_sequence = list(range(12, 0, -1))  # [12, 11, ..., 1]
already_prompted_forward = False

def is_clarifying_question(text: str) -> bool:
    prompt = """
    You are administering a cognitive test. 
    A patient responded after being asked to say the months of the year in reverse (December to January).

    Your task is to decide whether this response is a **clarifying or unrelated question**, such as:
    - "What am I doing"
    - "What do you mean"
    - "Why am i doing this"
    - "Do I start with December"
    - Repeat that

    Respond "No" for anything that seems like an attempt or a list, even if it is incorrect — even with typos (like "decemba", "novem", etc. or that seem to be listing anything).

    Respond only with "yes" or "no".
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])
    return result.content.strip().lower() == "yes"

def respond_to_clarifying_question(text: str) -> str:
    prompt = """
    You are the administrator of a cognitive test. The patient asked a clarifying question about saying months in reverse order.
    Kindly explain and redirect them to try again, starting with December. Do not provide the answer or any other months. Tell them to start with December, always! tell them to "Try saying the months backward beginning with December."
    """
    result = llm.invoke([
        SystemMessage(content=prompt.strip()),
        HumanMessage(content=text.strip())
    ])
    return result.content.strip()

def parse_each_word_to_month_number(response: str) -> list:
    words = response.strip().split()
    parsed_numbers = []

    for word in words:
        prompt = f"""
        You are classifying a single word as part of a cognitive screening test. 
        Your task is to determine if this word refers to a month of the year (even with misspellings or abbreviations like for september: sep, sept, 9, S, sepetemba, etc.). 
        Respond with the numeric month (e.g., "1" for January, "12" for December). 
        If it does not clearly refer to a month, respond with "0". 
        Do NOT explain.
        Word: {word}
        """
        result = llm.invoke([SystemMessage(content=prompt.strip())])
        try:
            parsed = int(result.content.strip())
        except:
            parsed = 0
        parsed_numbers.append(parsed)

    return parsed_numbers

import difflib

def count_month_errors(parsed: list[int], correct: list[int]) -> int:
    if parsed == correct:
        return 0

    if len(parsed) < 11 or all(p == 0 for p in parsed):
        return 2

    # Count how many values are incorrect by position
    position_errors = sum(1 for a, b in zip(parsed, correct) if a != b)

    # Count inversions (pairs out of order)
    inversions = 0
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if parsed[i] > parsed[j]:
                inversions += 1

    # Accept 1 misplaced value or 1 inversion
    if position_errors == 1 or inversions == 1:
        return 1

    # Accept a clean 2-element swap
    wrong_positions = [(i, a, b) for i, (a, b) in enumerate(zip(parsed, correct)) if a != b]
    if len(wrong_positions) == 2:
        a1, b1 = wrong_positions[0][1], wrong_positions[0][2]
        a2, b2 = wrong_positions[1][1], wrong_positions[1][2]
        if a1 == b2 and a2 == b1:
            return 1

    # Handle one missing value (off-by-one length)
    if abs(len(parsed) - len(correct)) == 1:
        trimmed_errors = sum(1 for a, b in zip(parsed, correct) if a != b)
        if trimmed_errors <= 1:
            return 1

    # Use difflib to compare similarity ratio
    ratio = difflib.SequenceMatcher(None, parsed, correct).ratio()
    if ratio > 0.9:
        return 1

    return 2




# === Q5 Logic ===
print("\n🧠 TEST: Say the months of the year in reverse order.")
print("🧑‍⚕️ ADMIN: Start with the last month of the year.")

month_errors = 0
attempts = 0  # make sure this exists earlier in your main script

while month_errors < 2:
    response = input("👉 Your answer: ").strip()

    if is_clarifying_question(response):
        reply = respond_to_clarifying_question(response)
        print(f"🧑‍⚕️ ADMIN: {reply}")
        continue

    parsed = parse_each_word_to_month_number(response)
    print(f"[DEBUG] Parsed as: {parsed}")

    # FIRST check: was the sequence started correctly?
    if not already_prompted_forward:
        if len(parsed) < 2 or parsed[0] != 12 or parsed[1] not in [11, 10]:
            already_prompted_forward = True
            print("🧑‍⚕️ ADMIN: Let’s start again. Try saying the months backward beginning with December.")
            continue  # no error yet

    month_errors = count_month_errors(parsed, correct_sequence)
    break

print("🧑‍⚕️ ADMIN: Thank you. Let's move on to the next question.")

# === Score ===
return month_errors * 2
'''
