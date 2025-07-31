# GO TO === File paths === to change input file and output file
# (input file should be name of the csv you are using)

import pandas as pd
import os
from simulation import simulate
from tqdm import tqdm

# === Normalization ===
def normalize_score_string(scores_str):
    scores = list(map(int, scores_str.split("~")))
    weights = [4, 3, 3, 2, 2, 2]
    normalized = [s // w for s, w in zip(scores, weights)]
    return "~".join(map(str, normalized))

# === Difference tracker ===
def compute_differences(expected_str, observed_str):
    expected = list(map(int, expected_str.split("~")))
    observed = list(map(int, observed_str.split("~")))
    return ", ".join([f"question {i+1}" for i, (e, o) in enumerate(zip(expected, observed)) if e != o]) or "none"

# === File paths ===
input_file = "Mistake Pattern Distribution.csv"
#input_file = "Sample.csv"
#MUST BE CSV
#input_file = "Your CSV File Name.csv"
output_file = "x_simulation_log.csv" # name whatever you want it to be
append_log = "x_simulation_output.csv" # name whatever you want it to be

# === Load input data ===
df = pd.read_csv(input_file)

# === Resume support ===
if os.path.exists(output_file):
    result_df = pd.read_csv(output_file)
    processed_ids = set(result_df["SBT Trial ID"])
else:
    result_df = pd.DataFrame()
    processed_ids = set()

# === Prepare log file if it doesn't exist ===
if not os.path.exists(append_log):
    with open(append_log, "w") as f:
        f.write(",".join([
            "SBT Trial ID", "Q1 Mistakes", "Q2 Mistakes", "Q3 Mistakes", "Q4 Mistakes", "Q5 Mistakes", "Q6 Mistakes",
            "subscoreID", "Differences", "Sim Scores", "Total Score", "Transcript"
        ]) + "\n")

# === Main simulation loop ===
new_rows = []

for i, subscore in tqdm(enumerate(df["subscoreID"]), total=len(df), desc="Simulating"):
    trial_id = i + 1
    if trial_id in processed_ids:
        continue

    # Parse Q1–Q6 
    q_values = list(map(int, subscore.split("~")))
    scores_str, total_score, transcript_path = simulate(*q_values)

    # Normalize score string
    normalized_scores_str = normalize_score_string(scores_str)

    # Read and delete transcript
    with open(transcript_path, "r") as f:
        transcript_text = f.read()
    os.remove(transcript_path)

    # Compute error diffs
    differences = compute_differences(subscore, normalized_scores_str)

    row_dict = {
        "SBT Trial ID": trial_id,
        "Q1 Mistakes": q_values[0],
        "Q2 Mistakes": q_values[1],
        "Q3 Mistakes": q_values[2],
        "Q4 Mistakes": q_values[3],
        "Q5 Mistakes": q_values[4],
        "Q6 Mistakes": q_values[5],
        "subscoreID": subscore,
        "Differences": differences,
        "Sim Scores": normalized_scores_str,
        "Total Score": total_score,
        "Transcript": transcript_text.strip()
    }

    new_rows.append(row_dict)

    # === Save every 10 ===
    if trial_id % 10 == 0:
        df_new = pd.DataFrame(new_rows)
        result_df = pd.concat([result_df, df_new], ignore_index=True)
        result_df.to_csv(output_file, index=False)

        with open(append_log, "a") as f:
            for row in new_rows:
                csv_line = ",".join([f'"{str(row[col]).replace("\"", "\"\"")}"' for col in row])
                f.write(csv_line + "\n")

        new_rows = []

# === Final save for leftover rows ===
if new_rows:
    df_new = pd.DataFrame(new_rows)
    result_df = pd.concat([result_df, df_new], ignore_index=True)
    result_df.to_csv(output_file, index=False)

    with open(append_log, "a") as f:
        for row in new_rows:
            csv_line = ",".join([f'"{str(row[col]).replace("\"", "\"\"")}"' for col in row])
            f.write(csv_line + "\n")

print("✅ All simulations complete.")
print("🗃️ Clean file saved to:", output_file)
print("🛡️  Log file saved to:", append_log)
