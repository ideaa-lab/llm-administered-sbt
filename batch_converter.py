# convert batch_run.py transcripts into question-seperated table

import pandas as pd
import re
from tqdm import tqdm

# === File paths ===
input_file = "476_sbt_simulation_log.csv"
output_file = "parsed_rows_161_470.csv"

# Load dataset
df = pd.read_csv(input_file)

# Focus only on rows 161–170 (0-based indices 160–169)
subset_df = df.iloc[161:470].copy()

# Constants
RECALL_SEPARATOR = "🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes."
RECALL_ATTEMPT_PATTERN = r"RECALL ATTEMPT \d+: (.*?)\n🧓 PATIENT: (.*?)\n"

def split_question_blocks(transcript):
    """
    Splits transcript into question blocks.
    - Inserts a fake TEST marker before recall separator so it becomes its own block.
    - Then splits by 🧠 TEST:
    """
    transcript = transcript.replace(RECALL_SEPARATOR, f"🧠 TEST:{RECALL_SEPARATOR}")
    return re.split(r"🧠 TEST:", transcript)

def extract_question_details(block):
    """
    Extracts normal question details:
    - Question text
    - Patient responses
    - Response classifications
    - Admin responses
    """
    q_match = re.search(r"^(.*?)\n", block.strip())
    question_text = q_match.group(1).strip() if q_match else None

    patient_responses = re.findall(r"🧓 PATIENT:?\s(.*?)\n", block)
    classifications = re.findall(r"Response classified as: (.*?)\n", block)
    admin_responses = re.findall(r"🧑‍⚕️ ADMIN: (.*?)\n", block)

    return question_text, patient_responses, classifications, admin_responses

def extract_recall_details(block):
    """
    Extracts recall attempts:
    - Each attempt has prompt + patient response
    Returns:
      - First recall attempt text (the 'Question')
      - Patient responses (1–3)
      - Next recall prompts as 'admin responses'
      - Final admin response after last attempt
    """
    attempts = re.findall(RECALL_ATTEMPT_PATTERN, block, flags=re.DOTALL)
    patient_responses = []
    admin_responses = []

    for idx, (recall_prompt, patient_reply) in enumerate(attempts):
        if idx > 0:  # second+ attempts become admin prompts
            admin_responses.append(f"RECALL ATTEMPT {idx+1}: {recall_prompt.strip()}")
        patient_responses.append(patient_reply.strip())

    # Find final admin message ("Good, now remember...")
    final_admin = re.search(r"🧑‍⚕️ ADMIN: (Good, now remember.*?)\n", block)
    if final_admin:
        admin_responses.append(final_admin.group(1).strip())

    first_question = f"RECALL ATTEMPT 1: {attempts[0][0].strip()}" if attempts else None

    return first_question, patient_responses, admin_responses

def process_trial(row):
    """
    Processes a single trial into multiple rows.
    Handles:
      - Normal questions
      - Special Recall block
    """
    intended_scores = list(map(int, row["subscoreID"].split("~")))
    actual_scores = list(map(int, row["Sim Scores"].split("~")))

    transcript = row["Transcript"]
    blocks = split_question_blocks(transcript)

    trial_rows = []
    normal_q_index = 0  # Q# counter for normal questions only

    for block in blocks[1:]:  # skip empty before first TEST
        # Detect if this is a recall block
        if RECALL_SEPARATOR in block:
            # Special recall processing
            first_question, patient_responses, admin_responses = extract_recall_details(block)

            recall_row = {
                "Question #": "Recall",
                "Intended Mistakes": "not applicable",
                "Actual Mistakes": "not applicable",
                "Difference": "not applicable",
                "Question": first_question
            }

            for i in range(3):
                recall_row[f"Patient Response #{i+1}"] = patient_responses[i] if i < len(patient_responses) else None
                recall_row[f"Response #{i+1} Classification"] = None
                recall_row[f"Admin Response #{i+1}"] = admin_responses[i] if i < len(admin_responses) else None

            trial_rows.append(recall_row)

        else:
            # Normal question
            normal_q_index += 1
            question_text, patient_responses, classifications, admin_responses = extract_question_details(block)

            intended = intended_scores[normal_q_index - 1] if normal_q_index <= len(intended_scores) else None
            actual = actual_scores[normal_q_index - 1] if normal_q_index <= len(actual_scores) else None
            difference = actual - intended if (intended is not None and actual is not None) else None

            row_data = {
                "Question #": f"Q{normal_q_index}",
                "Intended Mistakes": intended,
                "Actual Mistakes": actual,
                "Difference": difference,
                "Question": question_text
            }

            for i in range(3):
                row_data[f"Patient Response #{i+1}"] = patient_responses[i] if i < len(patient_responses) else None
                row_data[f"Response #{i+1} Classification"] = classifications[i] if i < len(classifications) else None
                row_data[f"Admin Response #{i+1}"] = admin_responses[i] if i < len(admin_responses) else None

            trial_rows.append(row_data)

    return trial_rows

# Process rows 161–170
all_rows = []
for _, row in tqdm(subset_df.iterrows(), total=len(subset_df)):
    all_rows.extend(process_trial(row))

# Build final DataFrame
final_df = pd.DataFrame(all_rows)
final_df.to_csv(output_file, index=False)

print(f"✅ Parsed data (rows 161–170) with Recall blocks saved to {output_file}")

'''
import pandas as pd
import re
from tqdm import tqdm

# === File paths ===
input_file = "476_sbt_simulation_log.csv"
output_file = "parsed_rows_161_170.csv"

# Load dataset
df = pd.read_csv(input_file)

# Focus only on rows 161–170 (0-based indices 160–169)
subset_df = df.iloc[161:171].copy()

# Constants
RECALL_SEPARATOR = "🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes."
RECALL_ATTEMPT_PATTERN = r"RECALL ATTEMPT \d+: (.*?)\n🧓 PATIENT: (.*?)\n"

def split_question_blocks(transcript):
    """
    Splits transcript into question blocks.
    - Inserts a fake TEST marker before recall separator so it becomes its own block.
    - Then splits by 🧠 TEST:
    """
    transcript = transcript.replace(RECALL_SEPARATOR, f"🧠 TEST:{RECALL_SEPARATOR}")
    return re.split(r"🧠 TEST:", transcript)

def extract_question_details(block):
    """
    Extracts normal question details:
    - Question text
    - Patient responses
    - Response classifications
    - Admin responses
    """
    q_match = re.search(r"^(.*?)\n", block.strip())
    question_text = q_match.group(1).strip() if q_match else None

    patient_responses = re.findall(r"🧓 PATIENT: (.*?)\n", block)
    classifications = re.findall(r"Response classified as: (.*?)\n", block)
    admin_responses = re.findall(r"🧑‍⚕️ ADMIN: (.*?)\n", block)

    return question_text, patient_responses, classifications, admin_responses

def extract_recall_details(block):
    """
    Extracts recall attempts:
    - Each attempt has prompt + patient response
    Returns:
      - First recall attempt text (the 'Question')
      - Patient responses (1–3)
      - Next recall prompts as 'admin responses'
      - Final admin response after last attempt
    """
    attempts = re.findall(RECALL_ATTEMPT_PATTERN, block, flags=re.DOTALL)
    patient_responses = []
    admin_responses = []

    for idx, (recall_prompt, patient_reply) in enumerate(attempts):
        # For the first one, the prompt will be the "Question"
        if idx > 0:
            admin_responses.append(f"RECALL ATTEMPT {idx+1}: {recall_prompt.strip()}")
        patient_responses.append(patient_reply.strip())

    # Find final admin message ("Good, now remember...")
    final_admin = re.search(r"🧑‍⚕️ ADMIN: (Good, now remember.*?)\n", block)
    if final_admin:
        admin_responses.append(final_admin.group(1).strip())

    # The first recall prompt is the "Question"
    first_question = f"RECALL ATTEMPT 1: {attempts[0][0].strip()}" if attempts else None

    return first_question, patient_responses, admin_responses

def process_trial(row):
    """
    Processes a single trial into multiple rows.
    Handles:
      - Normal questions
      - Special Recall block
    """
    intended_scores = list(map(int, row["subscoreID"].split("~")))
    actual_scores = list(map(int, row["Sim Scores"].split("~")))

    transcript = row["Transcript"]
    blocks = split_question_blocks(transcript)

    trial_rows = []

    for q_idx, block in enumerate(blocks[1:], start=1):
        # Detect if this is a recall block
        if RECALL_SEPARATOR in block:
            # Special recall processing
            first_question, patient_responses, admin_responses = extract_recall_details(block)

            recall_row = {
                "Question #": "Recall",
                "Intended Mistakes": "not applicable",
                "Actual Mistakes": "not applicable",
                "Difference": "not applicable",
                "Question": first_question
            }

            # Map attempts → responses
            for i in range(3):
                recall_row[f"Patient Response #{i+1}"] = patient_responses[i] if i < len(patient_responses) else None
                recall_row[f"Response #{i+1} Classification"] = None  # No classification for recall
                recall_row[f"Admin Response #{i+1}"] = admin_responses[i] if i < len(admin_responses) else None

            trial_rows.append(recall_row)

        else:
            # Normal question
            question_text, patient_responses, classifications, admin_responses = extract_question_details(block)

            intended = intended_scores[q_idx - 1] if q_idx <= len(intended_scores) else None
            actual = actual_scores[q_idx - 1] if q_idx <= len(actual_scores) else None
            difference = actual - intended if (intended is not None and actual is not None) else None

            row_data = {
                "Question #": f"Q{q_idx}",
                "Intended Mistakes": intended,
                "Actual Mistakes": actual,
                "Difference": difference,
                "Question": question_text
            }

            for i in range(3):
                row_data[f"Patient Response #{i+1}"] = patient_responses[i] if i < len(patient_responses) else None
                row_data[f"Response #{i+1} Classification"] = classifications[i] if i < len(classifications) else None
                row_data[f"Admin Response #{i+1}"] = admin_responses[i] if i < len(admin_responses) else None

            trial_rows.append(row_data)

    return trial_rows

# Process rows 161–170
all_rows = []
for _, row in tqdm(subset_df.iterrows(), total=len(subset_df)):
    all_rows.extend(process_trial(row))

# Build final DataFrame
final_df = pd.DataFrame(all_rows)
final_df.to_csv(output_file, index=False)

print(f"✅ Parsed data (rows 161–170) with Recall blocks saved to {output_file}")
'''
'''
import pandas as pd
import re
from tqdm import tqdm

# === File paths ===
input_file = "476_sbt_simulation_log.csv"
output_file = "parsed_rows_161_170.csv"

# Load the dataset
df = pd.read_csv(input_file)

# Focus only on rows 161-170 (0-based index 160–169)
subset_df = df.iloc[160:170].copy()

# Custom separator for recall attempts
RECALL_SEPARATOR = "🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes."


def extract_question_blocks(transcript):
    """
    Splits transcript into blocks for each question based on '🧠 TEST:' marker.
    Returns a list of question blocks.
    """
    # First, insert a fake 🧠 TEST marker before the recall separator
    transcript = transcript.replace(RECALL_SEPARATOR, f"🧠 TEST:{RECALL_SEPARATOR}")
    
    # Now split by 🧠 TEST:
    return re.split(r"🧠 TEST:", transcript)

def extract_question_details(block):
    """
    Extracts:
    - Question text
    - Patient responses
    - Response classifications
    - Admin responses
    """
    # First line is the question text
    q_match = re.search(r"^(.*?)\n", block.strip())
    question_text = q_match.group(1).strip() if q_match else None
    
    # All patient responses
    patient_responses = re.findall(r"🧓 PATIENT: (.*?)\n", block)
    # Classifications for each response
    classifications = re.findall(r"Response classified as: (.*?)\n", block)
    # Admin responses
    admin_responses = re.findall(r"🧑‍⚕️ ADMIN: (.*?)\n", block)
    
    return question_text, patient_responses, classifications, admin_responses

def process_trial(row):
    """
    Processes a single trial row, returning multiple rows (one per question).
    """
    # Extract intended & actual mistake counts for each question
    intended_scores = list(map(int, row["subscoreID"].split("~")))
    actual_scores = list(map(int, row["Sim Scores"].split("~")))

    transcript = row["Transcript"]
    blocks = extract_question_blocks(transcript)

    trial_rows = []

    # Start from 1 because split before first TEST is empty
    for q_idx, block in enumerate(blocks[1:], start=1):
        question_text, patient_responses, classifications, admin_responses = extract_question_details(block)

        # Get intended & actual mistakes for this specific question index
        intended = intended_scores[q_idx - 1] if q_idx <= len(intended_scores) else None
        actual = actual_scores[q_idx - 1] if q_idx <= len(actual_scores) else None
        difference = actual - intended if (intended is not None and actual is not None) else None

        row_data = {
            "Question #": f"Q{q_idx}",
            "Intended Mistakes": intended,
            "Actual Mistakes": actual,
            "Difference": difference,
            "Question": question_text
        }

        # Add up to 3 responses dynamically
        for i in range(3):
            if i < len(patient_responses):
                row_data[f"Patient Response #{i+1}"] = patient_responses[i]
                row_data[f"Response #{i+1} Classification"] = classifications[i] if i < len(classifications) else None
                row_data[f"Admin Response #{i+1}"] = admin_responses[i] if i < len(admin_responses) else None
            else:
                # Fill with None if no more responses
                row_data[f"Patient Response #{i+1}"] = None
                row_data[f"Response #{i+1} Classification"] = None
                row_data[f"Admin Response #{i+1}"] = None

        trial_rows.append(row_data)

    return trial_rows

# Process each trial row in the subset
all_rows = []
for _, row in tqdm(subset_df.iterrows(), total=len(subset_df)):
    all_rows.extend(process_trial(row))

# Convert to final DataFrame
final_df = pd.DataFrame(all_rows)

# Save to CSV
final_df.to_csv(output_file, index=False)

print(f"✅ Parsed data for rows 161-170 saved to {output_file}")

'''
