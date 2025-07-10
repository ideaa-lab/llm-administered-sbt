from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage

current_year = str(datetime.now().year)

def normalize_first_response(raw_input, llm):
    classifier_prompt = """You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "What year is it now?"

    Your job is to classify this response into one of three categories:
    - 'year': if the user is giving a valid or potentially valid year (even if written out, e.g., 'twenty twenty four' and even if they make a mistake like 'twenty twenty three' or typos)
    - 'question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'Am I trying to figure out the current time or just stating the numerical value of the calendar year?', 'what format', 'why?', etc.) or a clarifying question. Really any sort of question or confusion. DO NOT REVEAL THE YEAR
    - 'invalid': if the input is unrelated, empty, nonsensical, or says they don't know the answer.

    Only respond with one of: year, question, or invalid. Do not include quotations or anything, just the word.
    Do not explain.""" 
    classification = llm.invoke([
        SystemMessage(content=classifier_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    if classification == "year":
        normalize_prompt = """You are interpreting a user's spoken or typed response for a cognitive screening test.
        Your task is to extract the YEAR they intended (e.g., 'twenty twenty five' → '2025').
        Only return the 4-digit year like '2025'. If unclear or invalid, return 'invalid'.
        Do NOT explain or respond with commentary."""
        result = llm.invoke([
            SystemMessage(content=normalize_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("year", result.content.strip())
    elif classification == "question":
        redirect_prompt = """You are helping administer the SBT cognitive screening test.  The patient responded with a question instead of answering. ANSWER THE QUESTION BUT DO NOT GIVE THEM ANY YEAR IN YOUR RESPONSE
        Calmly answer their question and then redirect back to asking: 'What year is it now?'"""
        response = llm.invoke([
            SystemMessage(content=redirect_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("question", response.content.strip())
    else:
        return ("invalid", "Thank you, let's move on to the next question.")


def run_q1(llm, get_response):
    """
    Run Q1 of the SBT. `get_response()` should be a function that returns the patient's response as a string.
    """
    total_score = 0
    print("\n🧠 TEST: What year is it now?")

    while True:
        year_input = get_response()
        category, result = normalize_first_response(year_input, llm)

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

    return total_score
