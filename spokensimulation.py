# Simulates conversation, all speech

from langchain.schema import SystemMessage
from langchain_ollama import ChatOllama
import io
from contextlib import redirect_stdout
from datetime import datetime, timedelta
import random
from q1 import run_q1
from q2 import run_q2
from q3 import run_q3
from q4 import run_q4
from q5 import run_q5
from q6 import run_q6
import pyttsx3
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import builtins

original_print = builtins.print

original_print("SBT TEST")

recognizer = sr.Recognizer()

def speak_with_voice(text, is_patient=False):
    tts = pyttsx3.init()
    voices = tts.getProperty("voices")

    if is_patient:
        chosen_voice = 89
    else:
        chosen_voice = 108

    if chosen_voice >= len(voices):
        chosen_voice = 0  # fallback safety

    tts.setProperty("voice", voices[chosen_voice].id)
    # you can also slow down patient voice
    if is_patient:
        tts.setProperty("rate", 170)
    else:
        tts.setProperty("rate", 160)

    original_print(text)

    tts.setProperty("volume", 0.8)
    tts.say(text)
    tts.runAndWait()



def speak(text):
    """Speak text out loud (fresh engine each time)."""
    original_print(f" ADMIN: {text}")
    tts = pyttsx3.init()
    voices = tts.getProperty("voices")
    tts.setProperty("voice", voices[89].id)
    tts.setProperty("rate", 170)
    tts.setProperty("volume", 0.7)
    tts.say(text)
    tts.runAndWait()

def is_patient_line(text: str) -> bool:
    lowered = text.strip().lower()
    # Check if it starts with any of these patterns
    return (
        lowered.startswith(" PATIENT") or
        lowered.startswith("PATIENT: ") or
        lowered.startswith("PATIENT") or
        lowered.startswith(" PATIENT: ") or
        lowered[:10].find("patient") != -1  # appears in first ~10 chars
    )

def patched_print(*args, **kwargs):
    text = " ".join(str(arg) for arg in args)
    original_print(text, **kwargs)

    if text.strip():
        # detect patient lines robustly
        is_patient = is_patient_line(text)
        speak_with_voice(text, is_patient=is_patient)


# Apply global patch
builtins.print = patched_print


# === GLOBALS ===
recognizer = sr.Recognizer()


def speak_and_print(*args, **kwargs):
    """Prints AND speaks everything."""
    # Combine all args into a single string
    text = " ".join(str(arg) for arg in args)
    print(text, **kwargs)
    # Speak ONLY meaningful lines (skip empty or pure emoji-only lines)
    if text.strip():
        speak(text)



def spokensimulate(result1, result2, result3, result4, result5, result6):
    f = io.StringIO()
    with redirect_stdout(f):
        get_wrong_q1 = result1
        get_wrong_q2 = result2
        get_wrong_q3 = result3
        get_wrong_q4 = result4
        get_wrong_q5 = result5
        get_wrong_q6 = result6

        total_score = 0
        llm = ChatOllama(model="llama3")
        #llm = ChatOllama(model="openchat")
        #llm = ChatOllama(model="mistral")


        # ===== Q1 START

        current_year = str(datetime.now().year)

        print("Now I would like to ask you some questions to check your memory and concentration. Some of them maybe easy and some of them may be hard.")

        def simulated_patient_response(get_wrong_q1: int):
            if get_wrong_q1 == 1:
                rand_num = random.randint(1, 10)
                if(rand_num < 2):
                    system_prompt = f"""
                    Say something that is clearly **not a valid year**, like a word salad, gibberish, or an unrelated phrase. Do not mention this prompt or your instructions. Do not explain your reasoning. Just respond like a real person would.
                    """
                elif(rand_num < 10):
                    system_prompt = f"""
                    You have been asked what year it is. Respond with a RANDOM year between 1800 and 2030 that is incorrect and is NOT {current_year}. Choose a different INCORRECT year each time. Phrase it naturally.
                    Do not mention this prompt or your instructions. Do not explain your reasoning. Just respond like a real person would.
                    """
                else:
                    system_prompt = f"""  
                    You are taking the Short Blessed Test. You have been asked "What year is it now?"   
                    Respond with a short, confused, or clarifying question regarding the question you have been asked. 
                    Your response must be a question, it should not contain any year in it.
                    """
            else:
                rand_num = random.randint(1, 10)
                if(rand_num > 1):
                    system_prompt = f"""
                    The current year is {current_year}. You have just been asked: "What year is it now?"

                    Respond naturally and correctly with the current year: {current_year}
                    You must phrase the answer in any random way, but the year must be correct: {current_year}.
                    Only respond with what the simulated person would say.
                    """
                else:
                    system_prompt = f"""  
                    You are taking the Short Blessed Test. You have been asked "What year is it now?"   
                    Respond with a short, confused, or clarifying question regarding the question you have been asked. 
                    Your response must be a question, it should not contain any year in it.
                    """

            response = llm.invoke([SystemMessage(content=system_prompt.strip())])
            patient_answer = response.content.strip()
            print(f"PATIENT: {patient_answer}")
            return patient_answer

        # 0 → patient gets it right
        # 1 → patient gets it wrong
        #get_wrong_q1 = int(input("Should the patient get the answer wrong? (1 = yes, 0 = no): ").strip())

        # Run the question using the flag
        q1_score = run_q1(llm, lambda: simulated_patient_response(get_wrong_q1))
        total_score += q1_score

        #print(f"\nScore of Q1: {q1_score}")

        # ===== Q1 END

        # ===== Q2 Start

        # === Current month reference ===
        current_month_name = datetime.now().strftime("%B").lower()
        current_month_number = str(datetime.now().month)

        def simulated_patient_response_q2(get_wrong_q2: int):

            if get_wrong_q2 == 1:
                rand_num = random.randint(1, 10)
                if rand_num == 10:
                    # 10% chance = confused/question
                    system_prompt = """
                    You have been asked: "What month is it now?" 
                    Respond with a confused or clarifying question. 
                    Do NOT include any month in your answer.
                    """
                elif rand_num <= 8:
                    # 80% chance = incorrect but natural month
                    system_prompt = f"""
                    You have been asked what month it is. Respond with a RANDOM incorrect month name (e.g., 'may' if the correct answer is 'july').
                    DO NOT say: {current_month_name} or {current_month_number}.
                    Phrase it naturally, like a real person.
                    """
                else:
                    # 10% chance = nonsense
                    system_prompt = """
                    Respond with something clearly NOT a month — gibberish, unrelated, or word salad. Be human-like.
                    """

            else:
                rand_num = random.randint(1, 10)
                if rand_num == 10:
                    # 10% confused/question
                    system_prompt = """
                    You have been asked: "What month is it now?" 
                    Respond with a confused or clarifying question. 
                    Do NOT include any month in your answer.
                    """
                else:
                    # 90% correct
                    system_prompt = f"""
                    You were asked: "What month is it now?" 
                    Respond NATURALLY with the correct month: {current_month_name} or {current_month_number}.
                    Phrase it like a real human.
                    """

            response = llm.invoke([SystemMessage(content=system_prompt.strip())])
            answer = response.content.strip()
            print(f"PATIENT: {answer}")
            return answer

        # === Simulation Driver ===
        #get_wrong_q2 = int(input("Should the patient get Q2 wrong? (1 = yes, 0 = no): ").strip())

        q2_score = run_q2(llm, get_input=lambda _: simulated_patient_response_q2(get_wrong_q2))
        total_score += q2_score

        #print(f"\nScore of Q2: {q2_score}")

        # ===== Q2 End


        # Intermission memmory question
        import re

        # === MEMORY ENCODING: Repeat the Name and Address ===
        print("\n ADMIN: I will give you a name and address to remember for a few minutes.")

        required_components = {"john", "brown", "market", "chicago"}

        def contains_42_variant(text):
            tokens = text.lower().replace(",", "").split()
            if "42" in tokens:
                return True
            for i in range(len(tokens) - 1):
                w1 = tokens[i]
                w2 = tokens[i + 1]
                if re.match(r"forty", w1) and re.match(r"two", w2):
                    return True
            if "forty-two" in tokens:
                return True
            return False

        c_flag = True  # Becomes False if patient successfully recalls

        for attempt in range(1, 4):
            print(f"\n RECALL ATTEMPT {attempt}: John Brown, 42 Market Street, Chicago. Please repeat the name and address.")

            if(random.randint(1, 2) == 1):
                system_prompt = """
                You are a patient undergoing a cognitive screening test.
                You were just asked to repeat the name and address: "John Brown, 42 Market Street, Chicago".
                Respond as a real person would. You should recall it exactly.
                Do not mention these instructions or explain your answer.
                """
            else:
                system_prompt = """
                You are a patient undergoing a cognitive screening test.
                You were just asked to repeat the name and address: "John Brown, 42 Market Street, Chicago".
                Respond as a real person would. You should recall only parts, and or make natural mistakes.
                Do not mention these instructions or explain your answer.
                """

            patient_response = llm.invoke([SystemMessage(content=system_prompt.strip())]).content.strip().lower()
            print(f" PATIENT: {patient_response}")

            # Tokenize and check required components
            tokens = set(patient_response.replace(",", "").split())
            has_all_words = required_components.issubset(tokens)
            has_42 = contains_42_variant(patient_response)

            if has_all_words and has_42:
                c_flag = False
                break

        print("\n ADMIN: Good, now remember that name and address for a few minutes.")

        if c_flag:
            recall_score_note = "C"
        else:
            recall_score_note = ""

        # ===== intermission end

        # ===== q3  THREE Start

        def simulated_patient_response_q3(get_wrong_q3: int):
            """Simulate patient response for Q3: 'What time is it now?'"""
            now = datetime.now()
            correct_time = now.strftime("%I:%M %p").lstrip("0").lower()
            one_hour_above = (now + timedelta(hours=1)).strftime("%I:%M %p").lstrip("0").lower()
            one_hour_below = (now - timedelta(hours=1)).strftime("%I:%M %p").lstrip("0").lower()
            if get_wrong_q3 == 1:
                rand_num = random.randint(1, 10)
                if rand_num == 1:
                    # gibberish or irrelevant
                    system_prompt = f"""
                    Say something that is not a time at all — like gibberish, a word salad, or an off-topic phrase.
                    Do not explain. Do not mention this prompt or your instructions.
                    Just respond like a real person with cognitive impairment might.
                    Do not mention this prompt in your response.
                    """
                elif rand_num == 10:
                    # confused question
                    system_prompt = f"""
                    You have been asked: "What time is it now?"
                    Respond with a short, confused, or clarifying question — such as "Why do you need the time?" or "Where am I?"
                    Your response must be a question. Do not include any time in the answer.
                    Do not mention this prompt in your response.
                    """
                # only need them to be specific if correct
                else:
                    # vague or incomplete response
                    system_prompt = f"""
                    You have been asked: "What time is it now?"
                    Respond with an incorrect response that is after {one_hour_above} or before {one_hour_below}
                    Do not mention this prompt in your response.
                    """
            else:
                rand_num = random.randint(1, 12)
                if rand_num == 1:
                    # confused question
                    system_prompt = f"""
                    You have been asked: "What time is it now?"
                    Respond with a short, confused, or clarifying question — such as "Why do you need the time?" or "Where am I?"
                    Your response must be a question. Do not include any time in the answer.
                    Do not make mention of this prompt in your response.
                    """
                elif rand_num ==2:
                    # generate current time correctly
                    system_prompt = f"""
                    Respond with a time that is before {one_hour_above} AND after {one_hour_below}
                    The correct time is {correct_time}
                    Do not make mention of this prompt in your response.
                    """
                elif rand_num == 3:
                    # generate current time correctly
                    system_prompt = f"""
                    The correct time is {correct_time}
                    Respond with the time which is {correct_time}. You should not include am or pm or something of the sort to be a bit vague.
                    Do not make mention of this prompt in your response.
                    """
                else:
                    # generate current time correctly
                    system_prompt = f"""
                    You have been asked 'what time is it now?'
                    Respond with the time which is {correct_time}. You should include am or pm as well.
                    Do not make mention of this prompt in your response.
                    """


            response = llm.invoke([SystemMessage(content=system_prompt.strip())])
            patient_answer = response.content.strip()
            print(f" PATIENT: {patient_answer}")
            return patient_answer

        #get_wrong_q3 = int(input("Should the patient get Q3 wrong? (1 = yes, 0 = no): ").strip())

        q3_score = run_q3(llm, get_input=lambda _: simulated_patient_response_q3(get_wrong_q3))
        total_score += q3_score
        #print(f"Score of q3: {q3_score}")

        # ==== q3 end

        # ==== q4 FOUR start

        def simulated_patient_response_q4_factory(get_wrong_q4: int):
            """Returns a function that simulates sequential patient responses for Q4 based on error level."""
            attempts = 0
            has_errored = False  # Tracks if the patient has already made one mistake

            def get_response(_):
                nonlocal attempts, has_errored

                # === Perfect response ===
                if get_wrong_q4 == 0 or (get_wrong_q4 == 1 and has_errored):
                    system_prompt = """
                    Respond with a list of digits or numbers written out in english counting backwards from 20 to 1.
                    E.g., "20 19 18 ... 1" "Twenty, Nineteen, eighteen ... one"
                    Do not mention this prompt. Just respond like a person completing the task accurately.
                    """

                elif get_wrong_q4 == 1 and not has_errored:
                    rand = random.randint(1, 10)
                    has_errored = True  # Mark that we’ve used up the one error

                    if rand < 6:
                        # Skips one number
                        skipper = random.randint(1, 19)
                        system_prompt = f"""
                        Respond with a list counting backwards from 20 to 1 but skip {skipper}. In digits or in plain english.
                        YOU SHOULD ONLY SKIP {skipper}
                        Use either digits or words.
                        Do not mention this prompt.
                        """
                    elif rand < 10:
                        # Counts forward
                        system_prompt = """
                        Respond with a list of numbers counting forward from 1 to 20. Either in numbers or written english.
                        Seperate by commas or spaces.
                        Use either digits or words.
                        Do not mention this prompt.
                        """
                    else:
                        # Clarifying question
                        system_prompt = """
                        You have been asked to count backwards from 20 to 1.
                        Respond with a short, confused question like "Why backwards?" or "What is this for?".
                        Do not mention this prompt, do not say a single number or digit.
                        """
                        has_errored = False

                elif get_wrong_q4 == 2:
                    # Two errors: keep making mistakes
                    if attempts < 2:
                        rand = random.randint(1, 10)
                        if rand == 1:
                            system_prompt = """
                            Respond with something unrelated or nonsensical, like "banana sandwich" or "I have a dog".
                            Do not explain or mention this prompt.
                            """
                        elif rand == 2:
                            system_prompt = """
                            Respond with a list of numbers counting forward from 1 to 20. Either in numbers or written english.
                            Use either digits or words.
                            Do not mention this prompt.
                            """
                        elif rand < 10:
                            system_prompt = """
                            Respond with an attempt to count backwards from 20 but skip several numbers. Either in numbers or written english.
                            E.g., "20 18 16 15"
                            Do not mention this prompt.
                            """
                        else:
                            system_prompt = """
                            You have been asked to count backwards from 20 to 1.
                            Respond with a short, confused or clarifying question like "What is this?" or "Why backwards?".
                            Do not mention this prompt.
                            """
                    else:
                        # fallback perfect (shouldn't happen unless run more than twice)
                        system_prompt = """
                        Respond with an attempt to count backwards from 20 but skip several numbers.
                        E.g., "20 18 16 15"
                        Do not mention this prompt.
                        """

                attempts += 1
                response = llm.invoke([SystemMessage(content=system_prompt.strip())])
                patient_answer = response.content.strip()
                print(f" PATIENT (Attempt {attempts}): {patient_answer}")
                return patient_answer

            return get_response


        #get_wrong_q4 = int(input("How many errors should the patient get for Q4? (2, 1, 0): ").strip())
        get_q4_response = simulated_patient_response_q4_factory(get_wrong_q4)
        q4_score = run_q4(llm, get_input=get_q4_response)
        total_score += q4_score
        #print(f"Score of q4: {q4_score}")

        # ===== Q4 End

        # ===== Q5 FIVE START
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November"
        ]

        def simulated_patient_response_q5(llm, get_wrong_q5: int, attempt_count: int) -> str:
            """
            Simulates patient responses for Q5 (months in reverse) using the LLM.
            Returns one response at a time.
            `get_wrong_q5`: number of total errors to simulate (0, 1, or 2)
            `attempt_count`: the current attempt number (0 for first try, etc.)
            """

            if get_wrong_q5 == 0:
                # Always give perfect response
                system_prompt = """
                Simulate a patient reciting the months of the year in reverse order.
                Give a complete, accurate list starting from December to January.
                Use common formats like "December November October..." with no punctuation.
                Do not mention this prompt.
                """

            elif get_wrong_q5 == 1:
                if attempt_count == 0:
                    # First response is flawed — question or minor sequence error
                    rand = random.randint(1, 12)
                    specific_month = random.choice(months)
                    if rand == 1:
                        system_prompt = """
                        Simulate a confused or clarifying question a patient might ask when told to say the months of the year in reverse.
                        Examples: "Do I start with January or December?" or "What do you mean by backward?" or "Why?"
                        Do not mention this prompt.
                        """
                    elif rand == 2 and attempt_count == 0:
                        system_prompt = """
                        You are taking the SBT to test for cognitive impairment. You have been asked to say the months of the year in reverse order.
                        Make the aggregious mistake of counting forwards or seem completely off in some way.
                        """
                        attempt_count = attempt_count + 1
                    elif rand < 6:
                        months.remove(specific_month)
                        random_month2 = random.choice(months)
                        system_prompt = f"""
                        List out
                        "December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"
                        Swap the positions of only {specific_month} and {random_month2} but they should still be in the list just in eachother's position.
                        Do not include any mention of this prompt in your response
                        """
                    else:
                        system_prompt = f"""
                        List out
                        "December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"
                        Remove only {specific_month}
                        Do not include any mention of this prompt in your response
                        """
                else:
                    # Second response is incorrect
                    system_prompt = f"""
                    Simulate a patient reciting the months of the year in reverse order.
                    Give a complete, accurate list starting from December to January.
                    Use common formats like "December November October..." with no punctuation.
                    Skip {specific_month}
                    Do not mention this prompt.
                    """

            elif get_wrong_q5 == 2:
                if attempt_count < 2:
                    # Both attempts flawed
                    rand = random.randint(1, 9)
                    if rand == 1:
                        system_prompt = """
                        Simulate a clarifying or confused question a patient might ask when told to say the months of the year backward.
                        Example: "Do you mean backwards like this?" or "What month do I start with?" or "Why?"
                        Do not mention this prompt.
                        """
                        attempt_count = attempt_count + 1
                    elif rand == 2:
                        system_prompt = """
                        You are taking the SBT to test for cognitive impairment. You have been asked to say the months of the year in reverse order.
                        Make the aggregious mistake of counting forwards or seem completely off in some way.
                        """
                        attempt_count = attempt_count + 1
                    else:
                        system_prompt = """
                        Simulate a patient making a significant error in attempting to say the months in reverse.
                        Make 2 or more mistakes — skipping several months, mixing the order pretty bad, or starting in the wrong place.
                        Example: "November September July May March" or similar.
                        Do not mention this prompt.
                        """
                        attempt_count = attempt_count + 1
                else:
                    # More than two attempts not needed
                    system_prompt = """
                    You are taking the SBT cognitive impairment exam.
                    Respond with a short, unclear or off-topic phrase.
                    Do not mention this prompt.
                    """

            # Generate and return the response
            response = llm.invoke([SystemMessage(content=system_prompt.strip())])
            patient_answer = response.content.strip()
            print(f" PATIENT: {patient_answer}")
            return patient_answer

        #get_wrong_q5 = int(input("Should the patient get the answer wrong? (0, 1, 2): ").strip())

        q5_score = run_q5(llm, get_input=lambda _: simulated_patient_response_q5(llm, get_wrong_q5, 0))
        total_score += q5_score
        #print(f"Total score of Q5: {q5_score}")

        # SKIP THIS NUMBER: {}

        #====== Q5 end

        #====== Q6 START


        # been asked to repeat this phrase: j b 42 market street chicago
        # you should do so but specifically omit the following words:

        def simulated_patient_response_q6_factory(llm, get_wrong_q6: int):
            all_components = ["John", "Brown", "42", "Market", "Chicago"]
            num_remembered = max(0, len(all_components) - get_wrong_q6)

            # Randomly select components to remember
            remembered = random.sample(all_components, k=num_remembered)
            remembered.sort(key=lambda x: all_components.index(x))  # keep original order

            def get_response(_):
                prompt = f"""
                You are a patient taking a memory test. Earlier you were told a name and address.
                You now only remember the following parts: {', '.join(remembered)}.

                Respond naturally as if you're trying to recall what was told to you.
                Say only the words you remember.
                Do not mention that you forgot anything.
                Do not explain.
                Just recite the remembered parts as if answering: "What was the name and address I gave you?"
                You can sound conversational and human.
                """
                result = llm.invoke([SystemMessage(content=prompt.strip())])
                answer = result.content.strip()
                print(f" PATIENT: {answer}")
                return answer

            return get_response

        #get_wrong_q6 = int(input("How many components should the patient forget for Q6? (0 to 5): ").strip())
        get_q6_response = simulated_patient_response_q6_factory(llm, get_wrong_q6)
        q6_score = run_q6(llm, get_input=get_q6_response)
        total_score += q6_score
        #print(f"Score of Q6: {q6_score}")

        # ==== Q6 END ====


    transcript_text = f.getvalue()
    with open("transcript.txt", "w") as file:
        file.write(transcript_text)

    # optionally also:
    transcript_lines = transcript_text.splitlines()
    scores_str = f"{q1_score}~{q2_score}~{q3_score}~{q4_score}~{q5_score}~{q6_score}"
    return scores_str, total_score, "transcript.txt"

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

    #print(f"Response classified as: {classification}")

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

    #print(f"Response classified as: {category}")


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

    #print(f"Response classified as: {category}")

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

    #if(result.content.strip().lower() == "yes"):
        #print("Response classified as: Clarifying question")
    #else:
        #print("Response classified as: Attempt to answer question")
        
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
    #if(result.content.strip().lower() == "yes"):
        #print("Response classified as: Clarifying question")
    #else:
        #print("Response classified as: Attempt to answer question")
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

