from datetime import datetime, timedelta
from langchain.schema import SystemMessage, HumanMessage
now = datetime.now()
actual_minutes = now.hour * 60 + now.minute
correct_time = now.strftime("%I:%M %p").lstrip("0").lower()
from datetime import datetime, timedelta
now = datetime.now()
one_hour_above = (now + timedelta(hours=1)).strftime("%I:%M").lstrip("0")
one_hour_below = (now - timedelta(hours=1)).strftime("%I:%M").lstrip("0")

def normalize_time_response(raw_input: str, llm):
    """Classify and interpret user's time estimate response."""
    
    classify_prompt = f"""
    You are helping administer a cognitive screening test.
    The patient just gave a response to the question: "Without looking at your watch or clock, what time is it?"

    Classify this response into one of the following:
    - 'time': if the response includes a time with **hour and AM/PM** or includes a complete 24-hour format (e.g., "3:30pm", "14:00", "two thirty a.m.", "5 in the morning", "2 in the afternoon", "noon", "half past noon", etc.)
    - 'vague': if the response gave a partial or approximate time but does not include am or pm or says something like in the morning or in the afternoon(eg, one o'clock, 5, 12, 12:20, etc.)
    - 'question': if the user is asking a question (e.g., 'why am I here?', 'what are you doing?', 'Am I trying to figure out the current time or just stating the numerical value of the time?', 'what format', 'why?', etc.) or a clarifying question. Really any sort of question or confusion.
    - 'invalid': if the input is incorrect, unrelated, empty, or nonsensical

    Only respond with one of: time, vague, question, or invalid. Do not include quotations or anything, just the word.
    Do not explain.
    """

    category = llm.invoke([
        SystemMessage(content=classify_prompt.strip()),
        HumanMessage(content=raw_input.strip())
    ]).content.strip().lower()

    print(f"Response classified as: {category}")


    if category == "question":
        redirect = llm.invoke([
            SystemMessage(content="You are helping administer the SBT cognitive screening test. Calmly respond to the patient's question, then redirect by saying: 'What time is it now?' DO NOT reveal the correct time."),
            HumanMessage(content=raw_input)
        ])
        return ("question", redirect.content.strip())

    elif category == "invalid":
        return ("invalid", "Thank you. Let's continue.")

    elif category == "vague":
        return ("vague", "Can you give a more specific answer, like the exact hour and whether it's AM or PM?")

    elif category == "time":
        extract_prompt = """
        You are interpreting a time response given in a variety of possible human formats.
        Extract the approximate 24-hour time in HH:MM format from the user's answer (e.g., "three pm" → 15:00, 2:30am → 02:30, "2 in the morning" → 02:00, "a quarter past 5 in the afternoon" → 17:15).
        Only respond with a 24-hour time like "14:00".
        Do not explain.
        """
        interpreted = llm.invoke([
            SystemMessage(content=extract_prompt.strip()),
            HumanMessage(content=raw_input.strip())
        ]).content.strip()
        return ("time", interpreted)
    
    return ("invalid", "Thank you. Let's continue.")

def run_q3(llm, get_input=input, print_output=print):
    print_output("\n TEST: Without looking at your watch or clock, what time is it?")
    time_attempts = 0

    while time_attempts < 13:
        time_input = get_input("Your answer: ").strip().lower()
        category, result = normalize_time_response(time_input, llm)

        if category == "question":
            print_output(f"\nADMIN: {result}")
            time_attempts += 2
            continue

        elif category == "vague":
            if (time_attempts<9):
                print_output(f"\nADMIN: {result}")
            time_attempts += 4
            continue

        elif category == "invalid":
            print_output(result)
            return 3  # full penalty

        elif category == "time":
            try:
                h, m = map(int, result.split(":"))
                guessed_minutes = h * 60 + m

                # Compute forward and backward difference with wraparound (24 hours = 1440 minutes)
                diff = abs(actual_minutes - guessed_minutes)
                diff = min(diff, 1440 - diff)

                if diff > 60:
                    print("Thank you. Let's continue.")
                    return 3
                else:
                    print("Thank you. Let's continue.")
                    return 0
            except:
                return 3


    return 3  # if loop ends without valid answer
