# NOTES FOR MICHAEL:
# q6 hard-coded unless question, believe it makes more sense to do it this way
# "i think it's december..."
# github

from langchain_community.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from datetime import datetime
import re

"""
main.py

Description:
------------
This script implements an interactive, LLM-assisted version of the Short Blessed Test (SBT)
for cognitive impairment screening. It simulates an administrator administering the test
to a patient using a local language model (e.g., LLaMA via LangChain).

Features:
- Handles clarifying questions with redirection (zero penalty)
- Uses LLM for robust input parsing (e.g., months, names, numbers)
- Applies SBT scoring rules for each of the six questions
- Dynamically computes and reports final score with interpretation

Requirements:
- Python 3.9+
- LangChain
- Ollama or compatible local LLM backend

Usage:
------
Run the script from the terminal:
$ python main.py
"""

# === Setup ===
MODEL = "llama3"
llm = ChatOllama(model=MODEL)
total_score = 0

# === Current date reference for some of the q's ===
current_year = str(datetime.now().year)

# QUESTION 1: What year is it now?

def normalize_first_response(raw_input: str):
    """Classifies and processes user's year response."""
    
    classifier_prompt = """
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "What year is it now?"

    Your job is to classify this response into one of three categories:
    - 'year': if the user is giving a valid or potentially valid year (even if written out, e.g., 'twenty twenty four' and even if they make a mistake like 'twenty twenty three' or typos)
    - 'question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?') or a clarifying question. DO NOT REVEAL THE YEAR
    - 'invalid': if the input is unrelated, empty, nonsensical, or says they don't know the answer.

    Only respond with one of: year, question, or invalid.
    Do not explain.
    """

    classification = llm.invoke([
        SystemMessage(content=classifier_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    if classification == "year":
        normalize_prompt = """
        You are interpreting a user's spoken or typed response for a cognitive screening test.
        Your task is to extract the YEAR they intended (e.g., 'twenty twenty five' → '2025').
        Only return the 4-digit year like '2025'. If unclear or invalid, return 'invalid'.
        Do NOT explain or respond with commentary.
        """
        result = llm.invoke([
            SystemMessage(content=normalize_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("year", result.content.strip())

    elif classification == "question":
        redirect_prompt = """
        You are administering a cognitive test. The patient responded with a question instead of answering.
        Calmly answer their question and then redirect back to asking: 'What year is it now?'
        """
        response = llm.invoke([
            SystemMessage(content=redirect_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("question", response.content.strip())

    else:
        return ("invalid", "Thank you, let's move on to the next question.")


# === Run Year Question ===
print("\n🧠 TEST: What year is it now?")
while True:
    year_input = input("👉 Your answer: ").strip()
    category, result = normalize_first_response(year_input)

    if category == "year":
        if result != current_year:
            total_score += 4
        print("🧑‍⚕️ ADMIN: Thank you, let's move on to the next question.")
        break
    elif category == "question":
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        continue
    else:
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        total_score += 4
        break

# === Optional: Display Score So Far ===
print(f"\n🧾 Score after Q1: {total_score}")



# Question 2: What month is it now?

# === Current month reference ===
current_month_name = datetime.now().strftime("%B").lower()
current_month_number = str(datetime.now().month)

def normalize_month_response(raw_input: str):
    """Classifies and processes user's month response."""
    
    classifier_prompt = """
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "What month is it now?"

    Your job is to classify this response into one of three categories:
    - 'month': if the user is giving a valid or potentially valid month (even if written out, like "jun", or misspelled, like "junee")
    - 'question': if the user is asking a question (e.g., 'why are you asking that', 'what is this for') or a clarifying question. DO NOT REVEAL THE MONTH
    - 'invalid': if the input is unrelated, empty, nonsensical, or says they don't know.

    Only respond with one of: month, question, or invalid.
    Do not explain.
    """

    classification = llm.invoke([
        SystemMessage(content=classifier_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    if classification == "month":
        normalize_prompt = """
        You are interpreting a user's spoken or typed response for a cognitive screening test.
        Your task is to extract the MONTH they intended, either by name (e.g., 'June') or number (e.g., '6').
        Only return the lowercase month name (e.g., 'june') or numeric string 1–12. If unclear or invalid, return 'invalid'.
        Do NOT explain or respond with commentary.
        """
        result = llm.invoke([
            SystemMessage(content=normalize_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("month", result.content.strip().lower())

    elif classification == "question":
        redirect_prompt = """
        You are administering a cognitive test. The patient responded with a question instead of answering.
        Calmly answer their question and then redirect back to asking: 'What month is it now?'
        """
        response = llm.invoke([
            SystemMessage(content=redirect_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("question", response.content.strip())

    else:
        return ("invalid", "Thank you, let's move on to the next question.")


# === Run Month Question ===
print("\n🧠 TEST: What month is it now?")
while True:
    month_input = input("👉 Your answer: ").strip()
    category, result = normalize_month_response(month_input)

    if category == "month":
        # Check if the month is correct
        if result == current_month_name or result == current_month_number:
            pass  # correct, 0 points
        else:
            total_score += 3  # incorrect month
        print("🧑‍⚕️ ADMIN: Thank you, let's move on to the next question.")
        break

    elif category == "question":
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        continue  # re-ask the question

    else:  # invalid
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        total_score += 3
        break

# === Optional: Display Score So Far ===
print(f"\n🧾 Score after Q2: {total_score}")



# === Immediate Recall: Name and Address ===
print("\n🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes.")

correct_phrase = "john brown, 42 market street, chicago"
c_flag = True  # becomes False if user fails correctly recall the name and address
for attempt in range(1, 4):
    print(f"🧠 RECALL ATTEMPT {attempt}: John Brown, 42 Market Street, Chicago. Please repeat the name and address.")
    response = input("👉 Your answer: ").lower().strip()

    if correct_phrase in response:
        c_flag = False  # success

print("\n🧑‍⚕️ ADMIN: Good, now remember that name and address for a few minutes.")

if c_flag:
    total_score += 2  # or whatever value is appropriate
    recall_score_note = "C recorded"
else:
    recall_score_note = "Phrase successfully recalled"

print(f"\n🧾 Recall Score Note: {recall_score_note}")


def normalize_time_response(raw_input: str):
    """Classify and interpret user's time estimate response."""
    
    classify_prompt = """
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "Without looking at your watch or clock, what time is it?"

    Classify their response into:
    - 'time': if they gave a time with **hour and AM/PM** or in a complete 24-hour format (e.g., "3:30pm", "14:00", "two thirty a.m.")
    - 'vague': if they gave a partial or approximate time like "around 2", "2", "4", "mid-afternoon", or something without AM/PM
    - 'question': if they asked something like "why are you asking?"
    - 'invalid': if the input is unrelated, empty, or nonsensical.

    Only respond with one of: time, vague, question, or invalid.
    Do not explain.
    """

    category = llm.invoke([
        SystemMessage(content=classify_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    if category == "question":
        redirect = llm.invoke([
            SystemMessage(content="The patient asked a question instead of answering the time. Gently respond and redirect to the original question: 'Without looking at your watch or clock, what time is it?'"),
            HumanMessage(content=raw_input)
        ])
        return ("question", redirect.content.strip())

    elif category == "invalid":
        return ("invalid", "⚠️ That didn't sound like a valid time. Let's move on.")

    elif category == "vague":
        return ("vague", "Can you please give me a more specific answer, like the exact hour and whether it's AM or PM?")

    elif category == "time":
        extract_prompt = """
        You are interpreting a time response given in a variety of possible human formats.
        Extract the approximate 24-hour time in HH:MM format from the user's answer (e.g., "three pm" → "15:00", "2:30am" → "02:30").
        Only respond with a 24-hour time like "14:00". If you can't extract it reliably, return "invalid".
        Do not explain.
        """
        interpreted = llm.invoke([
            SystemMessage(content=extract_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ]).content.strip()
        return ("time", interpreted)
    
    return ("invalid", "Thank you. Let's continue.")

# === Run Question 3 ===
print("\n🧠 TEST: Without looking at your watch or clock, what time is it?")
time_attempts = 0
while time_attempts < 12:
    time_input = input("👉 Your answer: ").strip().lower()
    category, result = normalize_time_response(time_input)

    if category == "question":
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        continue

    elif category == "vague":
        print(f"\n🧑‍⚕️ ADMIN: {result}")
        time_attempts += 1
        continue

    elif category == "invalid":
        print(result)
        total_score += 3
        break

    elif category == "time":
        now = datetime.now()
        actual_minutes = now.hour * 60 + now.minute

        try:
            h, m = map(int, result.split(":"))
            guessed_minutes = h * 60 + m
            diff = abs(actual_minutes - guessed_minutes)
            if diff > 60:
                total_score += 3  # more than 1 hour off
        except:
            total_score += 3  # couldn't parse time
        break

else:
    # after 2 vague attempts
    print("🧑‍⚕️ ADMIN: Let's continue to the next part.")
    total_score += 3

print(f"\n🧾 Score after Q3: {total_score}")



def assess_backward_counting(llm):
    print("\n🧠 TEST: Now, please count aloud backwards from 20 to 1.")
    error_count = 0

    while error_count < 2:
        response = input("👉 Your answer: ").strip().lower()

        # Classify the type of response
        classification = llm.invoke([
            SystemMessage(content="""
You are helping administer a cognitive screening test.
The patient was asked to count backwards from 20 to 1.

Classify their response as:
- 'backward': counts backwards from 20.
- 'forward': counts forwards from 1.
- 'clarification': asks a clarifying/meta question like "why are we doing this?"
- 'nonsense': confused, off-topic, forgot task, or gives up.

Respond with: backward, forward, clarification, or nonsense.
Do NOT explain.
"""),
            HumanMessage(content=response)
        ]).content.strip().lower()

        if classification == "clarification":
            reply = llm.invoke([
                SystemMessage(content="""
The patient asked a clarifying question during a cognitive test. 
Gently answer and restate: 'Please count backwards from 20 to 1.'
"""),
                HumanMessage(content=response)
            ])
            print(f"\n🧑‍⚕️ ADMIN: {reply.content.strip()}")
            continue

        if classification == "nonsense":
            reply = llm.invoke([
                SystemMessage(content="""
The patient gave a confused or unrelated response.
Gently redirect and restate the task: 'Let's try again — please count backwards from 20 to 1.'
"""),
                HumanMessage(content=response)
            ])
            print(f"\n🧑‍⚕️ ADMIN: {reply.content.strip()}")
            error_count += 1
            continue

        if classification == "forward":
            print("\n🧑‍⚕️ ADMIN: It sounds like you’re counting forward. Let’s try again — please count backwards from 20 to 1.")
            error_count += 1
            continue

        if classification == "backward":
            # Convert written numbers to digits
            converted = llm.invoke([
                SystemMessage(content="""
The patient was asked to count backwards from 20 to 1.
They may have written numbers as words (e.g., "twenty, nineteen...").
Convert their response to a space-separated list of digits only (e.g., "20 19 18 ...").
Ignore punctuation or extra words. Do not explain.
"""),
                HumanMessage(content=response)
            ]).content.strip()

            found = list(map(int, re.findall(r"\b\d+\b", converted)))
            expected = list(range(20, 0, -1))
            missed = [n for n in expected if n not in found]

            if len(missed) > 1:
                print("\n🧑‍⚕️ ADMIN: It looks like you skipped some numbers. Let's try once more — count backwards from 20 to 1.")
                error_count += 1
                continue
            elif len(missed) == 1:
                error_count += 1
            break

    return min(error_count, 2) * 2  # Final score contribution

errors = assess_backward_counting(llm)
total_score += errors
print(f"\n🧾 Score after Q4: {total_score}")

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
total_score += month_errors * 2
print(f"\n🧾 Score after Q5: {total_score} | Parsed: {parsed}")

# === Q6 Constants ===
target_components = {
    "john": 1,
    "brown": 2,
    "42": 3,
    "market": 4,
    "chicago": 5
}
max_errors_q6 = 5

def is_clarifying_question_q6(text: str) -> bool:
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
    return result.content.strip().lower() == "yes"

def respond_to_clarifying_question_q6(text: str) -> str:
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

import re

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

# === Q6 Logic ===
print("\n🧠 TEST: Repeat the name and address I asked you to remember.")

while True:
    q6_response = input("👉 Your answer: ").strip()

    if is_clarifying_question_q6(q6_response):
        reply = respond_to_clarifying_question_q6(q6_response)
        print(f"🧑‍⚕️ ADMIN: {reply}")
        continue

    q6_score, matched_items = score_recall_response(q6_response)
    break

# === Score Update ===
total_score += q6_score
print("🧑‍⚕️ ADMIN: Thank you. Let's move on to the next question.")
print(f"\n🧾 Score after Q6: {total_score} | Matched components: {sorted(matched_items)}")






































































'''
# === Month question with redirect and limit ===
invalid_month_attempts = 0
while True:
    print("\n🧠 TEST: What month is it now?")
    month_input = input("👉 Your answer: ").lower()
    normalized_month = normalize_response(month_input, "month")

    if normalized_month in [current_month_name, current_month_number]:
        break
    elif normalized_month in [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ] or (normalized_month.isdigit() and 1 <= int(normalized_month) <= 12):
        total_score += 3
        break
    elif any(phrase in month_input for phrase in ["i don't know", "dont know", "no idea", "idk", "i do not know"]):
        total_score += 3
        break
    else:
        invalid_month_attempts += 1
        if invalid_month_attempts >= 2:
            print("\n🧑‍⚕️ ADMIN: That's okay, we'll move on.")
            total_score += 3
            break
        redirection = llm.invoke([
            SystemMessage(content="You are administering a cognitive test. The patient gave a confused or unrelated answer (e.g., 'who am I?'). Gently redirect them and re-ask: 'What month is it now?'"),
            HumanMessage(content=month_input)
        ])
        print(f"\n🧑‍⚕️ ADMIN: {redirection.content.strip()}")

# === Immediate Recall: Name and Address ===
print("\n🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes.")


correct_phrase = "john brown, 42 market street, chicago"
max_attempts = 3
learned = False

for attempt in range(1, max_attempts + 1):
    print(f"🧠 RECALL ATTEMPT {attempt}: John Brown, 42 Market Street, Chicago. Please repeat the name and address.")
    response = input("👉 Your answer: ").lower().strip()
    if correct_phrase in response:
        learned = True   # DOES NEED TO BE REPEATED REGARDLESS
        break
    elif any(phrase in response for phrase in ["i don't know", "idk", "can't remember", "no idea"]):
        continue

if learned:
    print("\n🧑‍⚕️ ADMIN: Good, now remember that name and address for a few minutes.")
else:
    print("\n🧑‍⚕️ ADMIN: We'll continue with the test.")
    total_score += 3  # Q3 weight

# === Time Estimation ===
from dateutil import parser

def normalize_time(raw_input):
    instruction = """
    You are interpreting a user's response in a cognitive test.
    Extract the intended clock time in 24-hour format (HH:MM) from natural input like:
    "one thirty pm", "around 3 pm", "about 4 o'clock am", "15:00", etc.
    If user gives a number such as "3", classify as vague

    - Return time in HH:MM (e.g., "13:30").
    - If AM/PM is not provided, assume closest to actual time.
    - If unclear, vague, or no time given, return 'vague'.
    - If nonsensical or unrelated, return 'invalid'.
    Do NOT explain or comment.
    """
    result = llm.invoke([
        SystemMessage(content=instruction.strip()),
        HumanMessage(content=raw_input.strip())
    ])
    return result.content.strip().lower()

print("\n🧠 TEST: Without looking at your watch or clock, tell me about what time it is (include AM / PM).")
time_attempts = 0
while time_attempts < 2:
    time_input = input("👉 Your answer: ")
    parsed_time_str = normalize_time(time_input)

    if parsed_time_str == "invalid":
        print("\n🧑‍⚕️ ADMIN: That didn’t seem to be a time. Let’s try again with a specific hour and minute, like '2:30 PM'.")
        time_attempts += 1
        continue
    elif parsed_time_str == "vague":
        print("\n🧑‍⚕️ ADMIN: Could you please be more specific? Try to give an exact time, like '2:15 PM'.")
        time_attempts += 1
        continue

    try:
        guessed_time = parser.parse(parsed_time_str)
        now = datetime.now()
        now_minutes = now.hour * 60 + now.minute
        guessed_minutes = guessed_time.hour * 60 + guessed_time.minute
        time_diff = abs(now_minutes - guessed_minutes)

        if time_diff <= 60:
            break  # Correct
        else:
            total_score += 3
            break
    except:
        print("⚠️ Could not interpret your time format. We'll move on.")
        total_score += 3
        break

if time_attempts == 2 and parsed_time_str in ["invalid", "vague"]:
    print("\n🧑‍⚕️ ADMIN: That’s okay. We’ll continue.")
    total_score += 3



# === Reverse Counting from 20 to 1 ===
def analyze_counting(response, repeated):
    instruction = f"""
    You are interpreting a patient's response to the prompt:
    "Count aloud backwards from 20 to 1."

    Rules:
    - Missing/skipping a number = 1 error
    - Counting forward (e.g., 1, 2, 3...) = 1 error
    - If they forgot the task or gave unrelated/confused content, that counts as 1 error and the task should be repeated ONCE (if not already repeated).
    Maximum: 2 errors.

    Their response:
    \"{response}\"

    Return ONLY a number: 0, 1, or 2.
    """
    result = llm.invoke([
        SystemMessage(content=instruction.strip()),
        HumanMessage(content=response.strip())
    ])
    try:
        errors = int(re.search(r"\d", result.content).group())
        return min(errors, 2)
    except:
        return 2

print("\n🧠 TEST: Count aloud backwards from 20 to 1.")
print("🧑‍⚕️ ADMIN: Please count aloud backwards starting at 20 and ending at 1.")

repeat_once = False
while True:
    count_input = input("👉 Your answer: ")

    # hallucination check
    if any(phrase in count_input.lower() for phrase in ["who am i", "where am i", "what is this", "what are you doing", "why"]):
        redirect = llm.invoke([
            SystemMessage(content="You are the admin for a cognitive test. The patient is giving confused answers (e.g., hallucinating or asking unrelated questions). Redirect them gently and repeat: 'Please count aloud backwards from 20 to 1.'"),
            HumanMessage(content=count_input)
        ])
        print(f"\n🧑‍⚕️ ADMIN: {redirect.content.strip()}")
        continue

    errors = analyze_counting(count_input, repeated=repeat_once)

    if errors == 1 and not repeat_once:
        print("\n🧑‍⚕️ ADMIN: Let’s try that again. Please count backwards starting at 20 and go all the way down to 1.")
        repeat_once = True
        continue

    total_score += min(errors, 2) * 2
    break

# === Question 6: Months in Reverse ===
def analyze_months_response(response, repeated):
    instruction = f"""
    You are evaluating a response to the question: "Say the months of the year in reverse order."

    Rules:
    - If the patient needs help starting, and the admin provides "December", score 1 error.
    - If they skip months or go forward accidentally, score 1–2 errors max.
    - If hallucinating or confused, the task should be repeated once (if not already repeated).
    Return ONLY 0, 1, or 2.
    
    Response: {response}
    """
    result = llm.invoke([
        SystemMessage(content=instruction.strip()),
        HumanMessage(content=response.strip())
    ])
    try:
        return min(int(re.search(r"\d", result.content).group()), 2)
    except:
        return 2

print("\n🧠 TEST: Say the months of the year in reverse order.")
print("🧑‍⚕️ ADMIN: Please start with the last month of the year and go backward.")

month_repeat = False
while True:
    month_reverse_input = input("👉 Your answer: ")

    # hallucination redirect
    if any(phrase in month_reverse_input.lower() for phrase in ["who am i", "where am i", "what is this", "why", "vision", "hallucination"]):
        redirect = llm.invoke([
            SystemMessage(content="You are the test administrator. The patient is hallucinating or confused. Calmly redirect: 'Let’s get back to the test. Please say the months of the year in reverse order, starting with the last month.'"),
            HumanMessage(content=month_reverse_input)
        ])
        print(f"\n🧑‍⚕️ ADMIN: {redirect.content.strip()}")
        continue

    errors = analyze_months_response(month_reverse_input, repeated=month_repeat)

    if errors == 1 and not month_repeat:
        print("\n🧑‍⚕️ ADMIN: Let’s try again. Start with December and say the months in reverse.")
        month_repeat = True
        continue

    total_score += errors * 2
    break


# === Question 7: Recall Name and Address ===
correct_answer = ["john", "brown", "42", "market", "chicago"]

def analyze_address_recall(response):
    instruction = f"""
    You're checking if the patient recalled the phrase "John Brown, 42 Market Street, Chicago".

    Rules:
    - All 5 items must be present: name, number, street name, city.
    - "Street" is optional. Substitutes like "lane" or "drive" are allowed.
    - Address number ("42") must be exact.
    - Minor typos or casing issues are acceptable.
    - Each missing/misrecalled component = 1 error. Max 2 errors.

    Return ONLY a number: 0, 1, or 2.
    
    Response: {response}
    """
    result = llm.invoke([
        SystemMessage(content=instruction.strip()),
        HumanMessage(content=response.strip())
    ])
    try:
        return min(int(re.search(r"\d", result.content).group()), 2)
    except:
        return 2

print("\n🧠 TEST: Repeat the name and address I asked you to remember.")


while True:
    address_input = input("👉 Your answer: ")

    if any(phrase in address_input.lower() for phrase in ["who am i", "where am i", "what is this", "vision", "hallucination"]):
        redirect = llm.invoke([
            SystemMessage(content="You are the test admin. The patient appears confused or hallucinating. Gently redirect them: 'Try to remember the name and address I asked you to memorize. Can you repeat it for me?'"),
            HumanMessage(content=address_input)
        ])
        print(f"\n🧑‍⚕️ ADMIN: {redirect.content.strip()}")
        continue

    errors = analyze_address_recall(address_input)
    total_score += errors * 2
    break
'''


'''
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import SystemMessage, HumanMessage
import time

# === CONFIG ===
PATIENT_DIFFICULTY = "moderate"  # normal, mild, moderate, severe
MODEL = "llama3.2"
REFERENCE_PATH = "reference.txt"

# === Load and Embed Reference Doc ===
loader = TextLoader(REFERENCE_PATH)
documents = loader.load()
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(documents)
embedding = OllamaEmbeddings(model=MODEL)
vectorstore = Chroma.from_documents(split_docs, embedding)
retriever = vectorstore.as_retriever(search_type="similarity", k=2)

# === SBT QUESTIONS AND SCORING RULES ===
QUESTIONS = [
    {"prompt": "What year is it now?", "answer": "2025", "weight": 4, "max_errors": 1},
    {"prompt": "What month is it now?", "answer": "June", "weight": 3, "max_errors": 1},
    {"prompt": "Please repeat this name and address: John Brown, 42 Market Street, Chicago", "answer": "John Brown, 42 Market Street, Chicago", "weight": 0, "max_errors": 0},
    {"prompt": "Without looking at a clock, what time is it right now?", "answer": "3", "weight": 3, "max_errors": 1},
    {"prompt": "Please count backwards from 20 to 1.", "answer": "20 to 1", "weight": 2, "max_errors": 2},
    {"prompt": "Say the months of the year in reverse order.", "answer": "December to January", "weight": 2, "max_errors": 2},
    {"prompt": "Now please recall the name and address I asked you to remember.", "answer": "John Brown, 42 Market Street, Chicago", "weight": 2, "max_errors": 5},
]

# === PROMPT DEFINITIONS ===
admin_base_prompt = """
You are an SBT (Short Blessed Test) administrator.
Ask exactly one question per turn, as specified.
Reference clinical guidelines below if needed.
Do not skip, reword, or assist.
"""

def get_patient_prompt(level):
    base = "You are a patient taking a memory test. Respond naturally to each question. Your cognitive ability is as follows:\n"
    profiles = {
        "normal": "You have full memory and attention. Answer all questions correctly and quickly.",
        "mild": "You make 1–2 small mistakes, such as missing a part of the address or skipping one number.",
        "moderate": "You are forgetful. You might miss parts of the address, give a wrong year or month, or struggle with reverse months.",
        "severe": "You are very confused. You struggle to recall the year, address, and cannot count or name months correctly."
    }
    return base + profiles.get(level, "normal")

# === SETUP LLMS ===
admin_llm = ChatOllama(model=MODEL)
patient_llm = ChatOllama(model=MODEL)
admin_messages = [SystemMessage(content=admin_base_prompt)]
patient_messages = [SystemMessage(content=get_patient_prompt(PATIENT_DIFFICULTY))]

# === RUN SIMULATION ===
print("=== SHORT BLESSED TEST SIMULATION ===\n")
total_score = 0

for i, item in enumerate(QUESTIONS):
    context_docs = retriever.get_relevant_documents(item['prompt'])
    context = "\n\n".join([doc.page_content for doc in context_docs])
    forced_instruction = f"Ask this question: {item['prompt']}\n\nReference:\n{context}"
    admin_messages.append(SystemMessage(content=forced_instruction))

    admin_response = admin_llm.invoke(admin_messages)
    print(f"\n🧑‍⚕️ ADMIN: {admin_response.content.strip()}")

    patient_messages.append(HumanMessage(content=admin_response.content))
    time.sleep(1)

    patient_response = patient_llm.invoke(patient_messages)
    print(f"🧓 PATIENT: {patient_response.content.strip()}")

    response_text = patient_response.content.lower()
    expected = item['answer'].lower()
    error_count = 0

    if i == 2:
        pass  # immediate recall is not scored
    elif i == 6:
        for part in ["john", "brown", "42", "market", "chicago"]:
            if part not in response_text:
                error_count += 1
    else:
        if expected not in response_text:
            error_count = 1

    score = min(error_count, item['max_errors']) * item['weight']
    total_score += score

    patient_messages.append(SystemMessage(content=patient_response.content))
    admin_messages.append(HumanMessage(content=patient_response.content))
    time.sleep(1)

# === INTERPRETATION ===
if total_score <= 4:
    interpretation = "Normal Cognition"
elif total_score <= 9:
    interpretation = "Questionable Impairment"
else:
    interpretation = "Likely Dementia"

print("\n🧑‍⚕️ FINAL SCORE")
print(f"Total Score: {total_score} → {interpretation}")

'''
'''
# Short Blessed Test (SBT) Simulation with GPT-4o
import os
import openai
from dotenv import load_dotenv
import random

# Load API key from .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load file contents
def load_file(path):
    return open(path).read().strip() if os.path.exists(path) else ""

admin_instructions = load_file("admin_instructions.txt")
patient_instructions = load_file("patient_instructions.txt")
reference_text = load_file("reference.txt")

if reference_text:
    reference_block = f"\n\nREFERENCE MATERIAL (for context only):\n{reference_text}"
    admin_instructions += reference_block
    patient_instructions += reference_block

# Score logic
def sample_target_score():
    level = random.choice(["normal", "questionable", "impaired"])
    if level == "normal": return random.randint(0, 4)
    if level == "questionable": return random.randint(5, 9)
    return random.randint(10, 20)

QUESTIONS = [
    "What year is it now?",
    "What month is it now?",
    "Without looking at your watch or clock, tell me about what time it is.",
    "Count aloud backwards from 20 to 1.",
    "Say the months of the year in reverse order.",
    "Repeat the name and address I asked you to remember: John Brown, 42 Market Street, Chicago."
]

def run_sbt():
    score_target = sample_target_score()
    print(f"\n[DEBUG] Patient Target Score: {score_target}")

    if score_target <= 4:
        level = "normal cognition"
    elif score_target <= 9:
        level = "mild cognitive impairment"
    else:
        level = "moderate to severe cognitive impairment"

    score_intro = (
        f"You are simulating a patient taking the SBT with a target score of {score_target}, "
        f"consistent with {level}. You must behave accordingly.\n\n"
        f"At the end of the test, you must say: SCORE_TRUE: {score_target}\n\n"
    )

    patient_prompt = score_intro + patient_instructions
    patient_msgs = [{"role": "system", "content": patient_prompt}]
    admin_msgs = [{"role": "system", "content": admin_instructions}]
    convo = []

    # Intro
    intro = "Now I would like to ask you some questions to check your memory and concentration. Some of them may be easy and some may be hard."
    admin_msgs.append({"role": "assistant", "content": intro})
    convo.append(f"SBT: {intro}")

    patient_msgs.append({"role": "user", "content": intro})
    patient_reply = client.chat.completions.create(
        model="gpt-4o", messages=patient_msgs, temperature=0.7
    ).choices[0].message.content.strip()
    convo.append(f"Patient: {patient_reply}")

    patient_msgs.append({"role": "assistant", "content": patient_reply})
    admin_msgs.append({"role": "user", "content": patient_reply})

    for q in QUESTIONS:
        admin_msgs.append({"role": "assistant", "content": q})
        convo.append(f"SBT: {q}")

        patient_msgs.append({"role": "user", "content": q})
        reply = client.chat.completions.create(
            model="gpt-4o", messages=patient_msgs, temperature=0.7
        ).choices[0].message.content.strip()
        convo.append(f"Patient: {reply}")

        patient_msgs.append({"role": "assistant", "content": reply})
        admin_msgs.append({"role": "user", "content": reply})

    # Ask for scores
    patient_msgs.append({"role": "user", "content": "Please now reveal your score as SCORE_TRUE: <value>."})
    true_resp = client.chat.completions.create(model="gpt-4o", messages=patient_msgs).choices[0].message.content.strip()
    convo.append(f"Patient Final: {true_resp}")

    admin_msgs.append({"role": "user", "content": "Please now reveal your estimated score as SCORE_ESTIMATED: <value>."})
    est_resp = client.chat.completions.create(model="gpt-4o", messages=admin_msgs).choices[0].message.content.strip()
    convo.append(f"SBT Final: {est_resp}")

    def extract_score(text, key):
        for line in text.splitlines():
            if key in line:
                try: return int(line.split(":")[1].strip())
                except: return None
        return None

    true_score = extract_score(true_resp, "SCORE_TRUE")
    est_score = extract_score(est_resp, "SCORE_ESTIMATED")
    diff = None if None in (true_score, est_score) else abs(true_score - est_score)

    return convo, true_score, est_score, diff

# Main
if __name__ == "__main__":
    convo, true, est, gap = run_sbt()

    print("\n=== GPT-on-GPT SBT Conversation ===\n")
    for line in convo:
        print(line)

    print("\n=== Final Scores ===")
    print(f"True Score (Patient): {true}")
    print(f"Estimated Score (Administrator): {est}")
    print(f"Score Difference: {gap}")

'''


'''
#ORIGINAL
import os
import openai
from dotenv import load_dotenv
import random
import time

# Load environment variables from .env
load_dotenv()

# Confirm API key loaded
api_key = os.getenv("OPENAI_API_KEY")
print("API Key loaded?", api_key is not None)
if api_key:
    print("API key preview:", api_key[:8] + "...")
else:
    print("⚠️ API key not loaded. Check your .env file and try again.")

# Set up OpenAI client (for v1+ SDK)
client = openai.OpenAI(api_key=api_key)

# Short Blessed Test Questions
SBT_QUESTIONS = [
    "What year is it now?",
    "What month is it now?",
    "Without looking at your watch or clock, tell me about what time it is.",
    "Count aloud backwards from 20 to 1.",
    "Say the months of the year in reverse order.",
    "Repeat the name and address I asked you to remember: John Brown, 42 Market Street, Chicago."
]

# Map score to level
def score_to_level(score):
    if score <= 4:
        return "Normal"
    elif 5 <= score <= 9:
        return "Questionable Impairment"
    else:
        return "Impairment Consistent with Dementia"

# Build patient simulation prompt
def get_patient_prompt(question, target_score):
    level = score_to_level(target_score)
    return f"""
You are simulating an elderly patient undergoing a cognitive test (Short Blessed Test).
Your target score is {target_score}, which falls under the category: {level}.

Respond to the following question realistically based on this level of cognitive impairment.
Do NOT say you are simulating or mention impairment. Respond naturally.

Question: "{question}"
"""

# Query GPT for a response
def get_gpt_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Run one SBT test with 6 questions
def run_single_sbt_test(target_score):
    responses = []
    print(f"\n[Simulating Patient with Target Score: {target_score} ({score_to_level(target_score)})]\n")
    for i, question in enumerate(SBT_QUESTIONS):
        prompt = get_patient_prompt(question, target_score)
        messages = [{"role": "system", "content": prompt}]
        reply = get_gpt_response(messages)
        responses.append((question, reply))
        print(f"Q{i+1}: {question}")
        print(f"A{i+1}: {reply}\n")
        time.sleep(1)
    return responses

# Run the script
if __name__ == "__main__":
    target_score = random.randint(0, 20)
    run_single_sbt_test(target_score)
'''
