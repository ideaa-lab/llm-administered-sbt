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

def simulate(result1, result2, result3, result4, result5, result6):
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
            print(f"🧓 PATIENT: {patient_answer}")
            return patient_answer

        # 0 → patient gets it right
        # 1 → patient gets it wrong
        #get_wrong_q1 = int(input("Should the patient get the answer wrong? (1 = yes, 0 = no): ").strip())

        # Run the question using the flag
        q1_score = run_q1(llm, lambda: simulated_patient_response(get_wrong_q1))
        total_score += q1_score

        print(f"\nScore after Q1: {total_score}")

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
            print(f"🧓 PATIENT: {answer}")
            return answer

        # === Simulation Driver ===
        #get_wrong_q2 = int(input("Should the patient get Q2 wrong? (1 = yes, 0 = no): ").strip())

        q2_score = run_q2(llm, get_input=lambda _: simulated_patient_response_q2(get_wrong_q2))
        total_score += q2_score

        print(f"\nScore after Q2: {total_score}")

        # ===== Q2 End


        # Intermission memmory question
        import re

        # === MEMORY ENCODING: Repeat the Name and Address ===
        print("\n🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes.")

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
            print(f"🧓 PATIENT: {patient_response}")

            # Tokenize and check required components
            tokens = set(patient_response.replace(",", "").split())
            has_all_words = required_components.issubset(tokens)
            has_42 = contains_42_variant(patient_response)

            if has_all_words and has_42:
                c_flag = False
                break

        print("\n🧑‍⚕️ ADMIN: Good, now remember that name and address for a few minutes.")

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
            print(f"🧓 PATIENT: {patient_answer}")
            return patient_answer

        #get_wrong_q3 = int(input("Should the patient get Q3 wrong? (1 = yes, 0 = no): ").strip())

        q3_score = run_q3(llm, get_input=lambda _: simulated_patient_response_q3(get_wrong_q3))
        total_score += q3_score
        print(f"Score after q3: {total_score}")

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
                print(f"🧓 PATIENT (Attempt {attempts}): {patient_answer}")
                return patient_answer

            return get_response


        #get_wrong_q4 = int(input("How many errors should the patient get for Q4? (2, 1, 0): ").strip())
        get_q4_response = simulated_patient_response_q4_factory(get_wrong_q4)
        q4_score = run_q4(llm, get_input=get_q4_response)
        total_score += q4_score
        print(f"Score after q4: {total_score}")

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
            print(f"🧓 PATIENT: {patient_answer}")
            return patient_answer

        #get_wrong_q5 = int(input("Should the patient get the answer wrong? (0, 1, 2): ").strip())

        q5_score = run_q5(llm, get_input=lambda _: simulated_patient_response_q5(llm, get_wrong_q5, 0))
        total_score += q5_score
        print(f"Total score after Q5: {total_score}")

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
                print(f"🧓 PATIENT: {answer}")
                return answer

            return get_response

        #get_wrong_q6 = int(input("How many components should the patient forget for Q6? (0 to 5): ").strip())
        get_q6_response = simulated_patient_response_q6_factory(llm, get_wrong_q6)
        q6_score = run_q6(llm, get_input=get_q6_response)
        total_score += q6_score
        print(f"Score after Q6: {total_score}")

        # ==== Q6 END ====


    transcript_text = f.getvalue()
    with open("transcript.txt", "w") as file:
        file.write(transcript_text)

    # optionally also:
    transcript_lines = transcript_text.splitlines()
    scores_str = f"{q1_score}~{q2_score}~{q3_score}~{q4_score}~{q5_score}~{q6_score}"
    return scores_str, total_score, "transcript.txt"
