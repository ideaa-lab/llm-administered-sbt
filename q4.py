import re
import difflib
from langchain.schema import SystemMessage, HumanMessage

def count_backward_errors(parsed: list[int], correct: list[int]) -> int:
    #print(correct)
    #print(parsed)
    if parsed == correct:
        return 0

    if len(parsed) < 19 or all(p == 0 for p in parsed):
        return 2

    position_errors = sum(1 for a, b in zip(parsed, correct) if a != b)

    inversions = 0
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if parsed[i] > parsed[j]:
                inversions += 1

    if position_errors == 1 or inversions == 1:
        return 1

    wrong_positions = [(i, a, b) for i, (a, b) in enumerate(zip(parsed, correct)) if a != b]
    if len(wrong_positions) == 2:
        a1, b1 = wrong_positions[0][1], wrong_positions[0][2]
        a2, b2 = wrong_positions[1][1], wrong_positions[1][2]
        if a1 == b2 and a2 == b1:
            return 1

    if abs(len(parsed) - len(correct)) == 1:
        trimmed_errors = sum(1 for a, b in zip(parsed, correct) if a != b)
        if trimmed_errors <= 1:
            return 1

    ratio = difflib.SequenceMatcher(None, parsed, correct).ratio()
    if ratio > 0.9:
        return 1

    return 2

def normalize_counting_response(raw_input: str, llm):
    """Classify and process a patient's backward counting response."""

    classify_prompt = """
    You are helping administer a cognitive screening test.
    The patient was asked to count backwards from 20 to 1.

    Classify their response as:
    - 'backward': counts backwards (either all or mostly correct, may be in words or digits)
    - 'forward': counts forwards (either all or mostly incorrect, may be in words or digits)
    - 'question': asks any sort of question, question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'Am I trying to figure out the 20 numbers or list them out?', 'what format', 'why?', etc.) or a clarifying question. Really any sort of question or confusion. 
    - 'invalid': gives up, is off-topic, or incomprehensible

    Only respond with: backward, forward, question, or invalid.
    Do not explain.
    """

    category = llm.invoke([
        SystemMessage(content=classify_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    print(f"Response classified as: {category}")

    if category == "question":
        redirection = llm.invoke([
            SystemMessage(content="You are helping administer a cognitive screening test. The patient asked a question. Gently answer and then redirect to say: 'Please count backwards from 20 to 1.'"),
            HumanMessage(content=raw_input)
        ]).content.strip()
        return ("question", redirection)

    elif category == "invalid":
        return ("invalid", "Let's try again — please count backwards from 20 to 1.")

    elif category == "forward":
        return ("forward", "It sounds like you’re counting forward. Let’s try again — count backwards from 20 to 1.")

    elif category == "backward":
        word_to_num = {
            "twenty": 20, "nineteen": 19, "eighteen": 18, "seventeen": 17,
            "sixteen": 16, "fifteen": 15, "fourteen": 14, "thirteen": 13,
            "twelve": 12, "eleven": 11, "ten": 10, "nine": 9, "eight": 8,
            "seven": 7, "six": 6, "five": 5, "four": 4, "three": 3,
            "two": 2, "one": 1
        }

        # Tokenize input
        tokens = re.findall(r"\b\w+\b", raw_input.lower())
        parsed = []

        for token in tokens:
            if token.isdigit():
                parsed.append(int(token))
            elif token in word_to_num:
                parsed.append(word_to_num[token])
            else:
                continue  # skip unrelated tokens (do not include 0s)

        expected = list(range(20, 0, -1))
        errors = count_backward_errors(parsed, expected)
        return ("backward", errors)



def run_q4(llm, get_input=input, print_output=print):
    print_output("\n TEST: Now, please count aloud backwards from 20 to 1.")
    total_errors = 0

    while total_errors < 2:
        response = get_input(" Your answer: ").strip()
        category, result = normalize_counting_response(response, llm)

        if category == "question":
            print_output(f"\n ADMIN: {result}")
            continue

        elif category == "invalid":
            print_output(f"\n ADMIN: {result}")
            total_errors += 1
            continue

        elif category == "forward":
            print_output(f"\n ADMIN: {result}")
            total_errors += 1
            continue

        elif category == "backward":
            total_errors += result
            break

    print_output("\n ADMIN: Thank you.")
    return min(total_errors, 2) * 2

'''
import re
from langchain.schema import SystemMessage, HumanMessage

def normalize_counting_response(raw_input: str, llm):
    """Classify and process a patient's backward counting response."""
    
    # 1. Classify the response
    classify_prompt = """
    You are helping administer a cognitive screening test.
    The patient was asked to count backwards from 20 to 1.

    Classify their response into:
    - 'backward': counts backwards from 20 (either all or mostly correct, may be in words or digits)
    - 'forward': counts forwards from 1
    - 'question': asks a clarifying question or expresses confusion
    - 'invalid': gives up, is off-topic, or incomprehensible

    Only respond with: backward, forward, question, or invalid.
    Do not explain.
    """
    category = llm.invoke([
        SystemMessage(content=classify_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    if category == "question":
        redirection = llm.invoke([
            SystemMessage(content="The patient asked a question. Gently answer and then redirect to say: 'Please count backwards from 20 to 1.'"),
            HumanMessage(content=raw_input)
        ]).content.strip()
        return ("question", redirection)

    elif category == "invalid":
        return ("invalid", "Let's try again — please count backwards from 20 to 1.")

    elif category == "forward":
        return ("forward", "It sounds like you’re counting forward. Let’s try again — count backwards from 20 to 1.")

    elif category == "backward":
        # Extract digits and compare to expected sequence
        conversion_prompt = """
        The patient attempted to count backwards from 20.
        Convert their response into a space-separated list of digits only (e.g., "twenty nineteen" → "20 19").
        Ignore punctuation and extra words. Do NOT explain.
        """
        cleaned = llm.invoke([
            SystemMessage(content=conversion_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ]).content.strip()

        found = list(map(int, re.findall(r"\b\d+\b", cleaned)))
        expected = list(range(20, 0, -1))
        missed = [n for n in expected if n not in found]

        return ("backward", len(missed))

    return ("invalid", "Let's move on.")

def run_q4(llm, get_input=input, print_output=print):
    print_output("\n🧠 TEST: Now, please count aloud backwards from 20 to 1.")
    errors = 0

    while errors < 2:
        response = get_input("👉 Your answer: ").strip()
        category, result = normalize_counting_response(response, llm)

        if category == "question":
            print_output(f"\n🧑‍⚕️ ADMIN: {result}")
            continue

        elif category == "invalid":
            print_output(f"\n🧑‍⚕️ ADMIN: {result}")
            errors += 1
            continue

        elif category == "forward":
            print_output(f"\n🧑‍⚕️ ADMIN: {result}")
            errors += 1
            continue

        elif category == "backward":
            missed = result
            if missed > 1:
                errors += 2
            elif missed == 1:
                errors += 1
            break

    print_output("\n🧑‍⚕️ ADMIN: Thank you.")
    return min(errors, 2) * 2  # max of 2 points
'''
'''
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
'''
