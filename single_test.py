from simulation import simulate
import pandas as pd
import os

# SINGLE SIMULATION, REPLACE NUMBERS IN simulate(q1,q2,q3,q4,q5,q6) with the number of errors you want for each
                                                  (q1,q2,q3,q4,q5,q6)
scores_str, total_score, transcript_file = simulate(0, 0, 0, 0, 0, 0)

print("Score by question:", scores_str)     # e.g., "0~0~0~0~0~0"
print("Total score:", total_score)          # e.g., 0
print("Transcript saved to:", transcript_file)  # e.g., "transcript.txt"
