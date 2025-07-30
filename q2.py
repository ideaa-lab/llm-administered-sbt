from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage

# === Current month reference ===
current_month_name = datetime.now().strftime("%B").lower()
current_month_number = str(datetime.now().month)         

def normalize_month_response(raw_input: str, llm):
    """Classifies and processes user's month response using the LLM."""
    
    classifier_prompt = """
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "What month is it now?"

    Your job is to classify this response into one of three categories:
    - 'month': if the user is giving a valid or potentially valid month (even if written out or misspelled)
    - 'question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'Am I trying to figure out the current time or just stating the numerical value of the calendar month?', 'what format', 'why?', etc.) or a clarifying question. Really any sort of question or confusion. DO NOT REVEAL THE MONTH
    - 'invalid': if the input is unrelated, empty, or nonsensical

    Only respond with: month, question, or invalid. Do not explain. Do not include quotations or anything, just the word.
    """

    classification = llm.invoke([
        SystemMessage(content=classifier_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    print(f"Response classified as: {classification}")

    if classification == "month":
        normalize_prompt = """
        Extract the month the patient intended as the name of the month(example: june). If they responded with a number convert it to the correct month name. 
        Only return the lowercase month name. If unclear, return 'invalid'. Do not explain.
        Your output should have no quotes or anything apart from the name of the month
        """
        result = llm.invoke([
            SystemMessage(content=normalize_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("month", result.content.strip().lower())

    elif classification == "question":
        redirect_prompt = """
        You are helping administer the SBT cognitive screening test. 
        Calmly respond to the patient's question, then redirect by saying: 'What month is it now?'
        DO NOT reveal the correct month.
        """
        response = llm.invoke([
            SystemMessage(content=redirect_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("question", response.content.strip())

    else:
        return ("invalid", "Thank you, let's move on to the next question.")

def run_q2(llm, get_input=input, print_output=print):
    """Runs Q2 interaction. Returns Q2 score only."""
    print_output("\nADMIN: What month is it now?")
    q2_score = 0

    while True:
        month_input = get_input("Your answer: ").strip()
        category, result = normalize_month_response(month_input, llm)

        if category == "month":
            if result != current_month_name and result != current_month_number:
                q2_score += 3
            print_output(" ADMIN: Thank you, let's move on to the next question.")
            break

        elif category == "question":
            print_output(f"\n ADMIN: {result}")
            continue  # re-ask the question

        else:
            print_output(f"\n ADMIN: {result}")
            q2_score += 3
            break

    return q2_score

'''
from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage

# === Current month reference ===
current_month_name = datetime.now().strftime("%B").lower()
current_month_number = str(datetime.now().month)

def normalize_month_response(raw_input: str, llm):
    """Classifies and processes user's month response using the LLM."""
    
    classifier_prompt = """
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "What month is it now?"

    Your job is to classify this response into one of three categories:
    - 'month': if the user is giving a valid or potentially valid month (even if written out, like "jun", or misspelled, like "junee")
    - 'question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'Am I trying to figure out the current month or just stating the numerical month of the calendar year?', 'what format', 'why?', etc.) or a clarifying question. Really any sort of question or confusion.
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
        Calmly answer their question and then redirect back to asking: 'What month is it now?' DO NOT SAY ANY MONTH NAME IN YOUR RESPONSE
        """
        response = llm.invoke([
            SystemMessage(content=redirect_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ])
        return ("question", response.content.strip())

    else:
        return ("invalid", "Thank you, let's move on to the next question.")

def run_q2(llm, total_score, get_input=input, print_output=print):
    """Runs Q2 interaction and returns updated total_score."""
    print_output("\n TEST: What month is it now?")

    while True:
        month_input = get_input(" Your answer: ").strip()
        category, result = normalize_month_response(month_input, llm)

        if category == "month":
            if result == current_month_name or result == current_month_number:
                pass  # correct
            else:
                total_score += 3
            print_output(" ADMIN: Thank you, let's move on to the next question.")
            break

        elif category == "question":
            print_output(f"\n ADMIN: {result}")
            continue

        else:
            print_output(f"\n ADMIN: {result}")
            total_score += 3
            break

    print_output(f"\nScore after Q2: {total_score}")
    return total_score
'''
