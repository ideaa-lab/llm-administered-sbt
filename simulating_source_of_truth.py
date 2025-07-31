# Simulating the transcripts from real med students, using their patient responses as a source of truth
# NEEDS FIXING: - Accurately going through the json file of convos on gpt and accurately extracting patient responses(doesn't get all of em)
#               - Making sure the correct patient response is plugged into the correct run_q#
# Batch CSV Simulation Processor

from langchain.schema import SystemMessage
from langchain_ollama import ChatOllama
import io
from contextlib import redirect_stdout
from datetime import datetime, timedelta
import random
import pandas as pd
import re
import os
from q1 import run_q1
from q2 import run_q2
from q3 import run_q3
from q4 import run_q4
from q5 import run_q5
from q6 import run_q6

class TranscriptParser:
    """Parse transcript to extract admin responses for each question"""
    
    @staticmethod
    def parse_transcript(transcript_text, trial_id):
        """Parse transcript and extract admin responses for each question"""
        lines = transcript_text.split('\n')
        admin_responses = {}
        current_question = None
        
        # Patterns to identify questions and admin responses
        question_patterns = {
            'Q1': r'TEST:\s*What year is it now\?',
            'Q2': r'What month is it now\?',
            'Q3': r'Without looking at your watch or clock.*time',
            'Q4': r'count.*backwards.*from 20 to 1',
            'Q5': r'months.*year.*reverse',
            'Q6': r'repeat.*name.*address'
        }
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Identify which question we're in
            for q_num, pattern in question_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    current_question = q_num
                    break
            
            # Extract admin responses (lines starting with ADMIN:)
            if line.startswith('ADMIN:') and current_question:
                admin_text = line.replace('ADMIN:', '').strip()
                if admin_text and admin_text not in ['', 'Thank you.', 'Thank you']:
                    if current_question not in admin_responses:
                        admin_responses[current_question] = []
                    admin_responses[current_question].append(admin_text)
        
        # Clean up admin responses - take the most relevant one for each question
        final_responses = {}
        for q_num, responses in admin_responses.items():
            if responses:
                # For most questions, take the last substantive response
                # Filter out very short generic responses
                substantive = [r for r in responses if len(r) > 10]
                if substantive:
                    final_responses[q_num] = substantive[-1]
                else:
                    final_responses[q_num] = responses[-1]
            else:
                final_responses[q_num] = "Thank you."
        
        return final_responses

class BatchCSVProcessor:
    def __init__(self, csv_file_path, output_file_path, batch_size=10):
        self.csv_file_path = csv_file_path
        self.output_file_path = output_file_path
        self.batch_size = batch_size
        self.df = pd.read_csv(csv_file_path)
        self.llm = ChatOllama(model="llama3")
        
        # Initialize output dataframe with new columns
        self.output_df = self.df.copy()
        self.output_df.insert(self.output_df.columns.get_loc('actual_mistakes') + 1, 
                             'recorded_mistakes_by_llm', None)
        self.output_df.insert(self.output_df.columns.get_loc('admin_response') + 1, 
                             'llm_admin_response', None)
        
        # Create checkpoint file name
        self.checkpoint_file = f"checkpoint_{os.path.basename(output_file_path)}"
        
    def load_checkpoint(self):
        """Load progress from checkpoint if it exists"""
        if os.path.exists(self.checkpoint_file):
            try:
                checkpoint_df = pd.read_csv(self.checkpoint_file)
                print(f"Loaded checkpoint with {len(checkpoint_df)} processed rows")
                return checkpoint_df
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                return None
        return None
    
    def save_checkpoint(self, df, batch_num):
        """Save current progress"""
        df.to_csv(self.checkpoint_file, index=False)
        print(f"Checkpoint saved after batch {batch_num}")
    
    def simulate_single_trial(self, trial_id):
        """Run simulation for a single trial and return scores and admin responses"""
        trial_data = self.df[self.df['trial_id'] == trial_id]
        
        if trial_data.empty:
            return None, None
        
        # Capture stdout to get transcript
        f = io.StringIO()
        scores = {}
        
        try:
            with redirect_stdout(f):
                print(f"\n=== Running simulation for Trial ID: {trial_id} ===")
                
                # Create response functions for each question
                def get_q1_response():
                    q1_data = trial_data[trial_data['question_number'] == 'Q1']
                    if not q1_data.empty:
                        response = q1_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "2024"  # fallback
                
                def get_q2_response(_):
                    q2_data = trial_data[trial_data['question_number'] == 'Q2']
                    if not q2_data.empty:
                        response = q2_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "October"  # fallback
                
                def get_q3_response(_):
                    q3_data = trial_data[trial_data['question_number'] == 'Q3']
                    if not q3_data.empty:
                        response = q3_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "3 pm"  # fallback
                
                def get_q4_response(_):
                    q4_data = trial_data[trial_data['question_number'] == 'Q4']
                    if not q4_data.empty:
                        response = q4_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1"  # fallback
                
                def get_q5_response(_):
                    q5_data = trial_data[trial_data['question_number'] == 'Q5']
                    if not q5_data.empty:
                        response = q5_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "Dec Nov Oct Sep Aug Jul Jun May Apr Mar Feb Jan"  # fallback
                
                def get_q6_response(_):
                    q6_data = trial_data[trial_data['question_number'] == 'Q6']
                    if not q6_data.empty:
                        response = q6_data.iloc[0]['patient_response']
                        print(f"🧓 PATIENT: {response}")
                        return response
                    return "John Brown, 42 Market Street, Chicago"  # fallback
                
                # Memory encoding simulation
                print("\n🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes.")
                print("\n RECALL ATTEMPT: John Brown, 42 Market Street, Chicago. Please repeat the name and address.")
                print("🧓 PATIENT: John Brown, 42 Market Street, Chicago")
                print("\n🧑‍⚕️ ADMIN: Good, now remember that name and address for a few minutes.")
                
                # Run each question
                scores['Q1'] = run_q1(self.llm, get_q1_response)
                print(f"\nScore of Q1: {scores['Q1']}")
                
                scores['Q2'] = run_q2(self.llm, get_input=get_q2_response)
                print(f"\nScore of Q2: {scores['Q2']}")
                
                scores['Q3'] = run_q3(self.llm, get_input=get_q3_response)
                print(f"Score of Q3: {scores['Q3']}")
                
                scores['Q4'] = run_q4(self.llm, get_input=get_q4_response)
                print(f"Score of Q4: {scores['Q4']}")
                
                scores['Q5'] = run_q5(self.llm, get_input=get_q5_response)
                print(f"Total score of Q5: {scores['Q5']}")
                
                scores['Q6'] = run_q6(self.llm, get_input=get_q6_response)
                print(f"Score of Q6: {scores['Q6']}")
            
            # Parse transcript for admin responses
            transcript_text = f.getvalue()
            admin_responses = TranscriptParser.parse_transcript(transcript_text, trial_id)
            
            return scores, admin_responses
            
        except Exception as e:
            print(f"Error processing trial {trial_id}: {e}")
            return None, None
    
    def process_all_trials(self):
        """Process all trials in batches"""
        # Check for existing checkpoint
        checkpoint_df = self.load_checkpoint()
        if checkpoint_df is not None:
            self.output_df = checkpoint_df
            processed_trials = set(checkpoint_df[checkpoint_df['recorded_mistakes_by_llm'].notna()]['trial_id'].unique())
        else:
            processed_trials = set()
        
        # Get unique trial IDs that haven't been processed
        all_trial_ids = self.df['trial_id'].unique()
        remaining_trials = [tid for tid in all_trial_ids if tid not in processed_trials]
        
        print(f"Processing {len(remaining_trials)} remaining trials out of {len(all_trial_ids)} total trials")
        
        batch_count = 0
        for i, trial_id in enumerate(remaining_trials):
            print(f"\n--- Processing Trial {trial_id} ({i+1}/{len(remaining_trials)}) ---")
            
            scores, admin_responses = self.simulate_single_trial(trial_id)
            
            if scores and admin_responses:
                # Update the output dataframe for this trial
                trial_mask = self.output_df['trial_id'] == trial_id
                
                for question_num in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6']:
                    question_mask = trial_mask & (self.output_df['question_number'] == question_num)
                    
                    if question_mask.any():
                        # Update LLM score
                        if question_num in scores:
                            self.output_df.loc[question_mask, 'recorded_mistakes_by_llm'] = scores[question_num]
                        
                        # Update LLM admin response
                        if question_num in admin_responses:
                            self.output_df.loc[question_mask, 'llm_admin_response'] = admin_responses[question_num]
                        else:
                            self.output_df.loc[question_mask, 'llm_admin_response'] = "Thank you."
            
            # Save checkpoint every batch_size trials
            if (i + 1) % self.batch_size == 0:
                batch_count += 1
                self.save_checkpoint(self.output_df, batch_count)
                print(f"Completed batch {batch_count}")
        
        # Final save
        self.output_df.to_csv(self.output_file_path, index=False)
        print(f"\nFinal results saved to {self.output_file_path}")
        
        # Clean up checkpoint
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print("Checkpoint file removed")
        
        return self.output_df
    
    def get_summary_stats(self):
        """Get summary statistics of the processing"""
        if hasattr(self, 'output_df'):
            total_rows = len(self.output_df)
            processed_rows = len(self.output_df[self.output_df['recorded_mistakes_by_llm'].notna()])
            unique_trials = self.output_df['trial_id'].nunique()
            
            print(f"\n=== SUMMARY STATISTICS ===")
            print(f"Total rows: {total_rows}")
            print(f"Processed rows: {processed_rows}")
            print(f"Unique trials: {unique_trials}")
            print(f"Completion rate: {processed_rows/total_rows*100:.1f}%")
            
            # Show accuracy comparison
            if processed_rows > 0:
                comparison = self.output_df[self.output_df['recorded_mistakes_by_llm'].notna()]
                matches = (comparison['actual_mistakes'] == comparison['recorded_mistakes_by_llm']).sum()
                accuracy = matches / len(comparison) * 100
                print(f"LLM scoring accuracy: {accuracy:.1f}% ({matches}/{len(comparison)} matches)")

# Main execution function
def main():
    input_csv = "Corrected_Responses.csv"
    output_csv = "simulation_results_with_llm_scores.csv"
    
    # Initialize processor
    processor = BatchCSVProcessor(input_csv, output_csv, batch_size=10)
    
    try:
        # Process all trials
        result_df = processor.process_all_trials()
        
        # Show summary statistics
        processor.get_summary_stats()
        
        print(f"\nProcessing complete! Results saved to {output_csv}")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted. Progress has been saved to checkpoint.")
        processor.save_checkpoint(processor.output_df, "interrupted")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        # Save what we have so far
        if hasattr(processor, 'output_df'):
            processor.save_checkpoint(processor.output_df, "error")

if __name__ == "__main__":
    main()

'''
# SAY SCORE OF EACH QUESTION

from langchain.schema import SystemMessage
from langchain_ollama import ChatOllama
import io
from contextlib import redirect_stdout
from datetime import datetime, timedelta
import random
import pandas as pd
from q1 import run_q1
from q2 import run_q2
from q3 import run_q3
from q4 import run_q4
from q5 import run_q5
from q6 import run_q6

class CSVResponseProvider:
    def __init__(self, csv_file_path, trial_id):
        """Initialize with CSV data for a specific trial"""
        self.df = pd.read_csv(csv_file_path)
        self.trial_id = trial_id
        self.trial_data = self.df[self.df['trial_id'] == trial_id]
        
        if self.trial_data.empty:
            raise ValueError(f"No data found for trial_id {trial_id}")
        
        print(f"Loaded trial {trial_id} with {len(self.trial_data)} responses")
    
    def get_response(self, question_number):
        """Get patient response for a specific question"""
        question_data = self.trial_data[self.trial_data['question_number'] == question_number]
        
        if question_data.empty:
            raise ValueError(f"No response found for trial {self.trial_id}, question {question_number}")
        
        # If there are multiple entries for the same question (like duplicates in your data), take the first one
        response = question_data.iloc[0]['patient_response']
        print(f"🧓 PATIENT: {response}")
        return response
    
    def get_expected_mistakes(self, question_number):
        """Get the expected number of mistakes for a question"""
        question_data = self.trial_data[self.trial_data['question_number'] == question_number]
        
        if question_data.empty:
            return 0
        
        return question_data.iloc[0]['actual_mistakes']

def simulate_with_csv(csv_file_path, trial_id):
    """
    Modified simulate function that uses CSV responses instead of LLM-generated ones
    """
    f = io.StringIO()
    with redirect_stdout(f):
        # Initialize CSV response provider
        csv_provider = CSVResponseProvider(csv_file_path, trial_id)
        
        total_score = 0
        llm = ChatOllama(model="llama3")

        print(f"\n=== Running simulation for Trial ID: {trial_id} ===")

        # ===== Q1 START =====
        def csv_patient_response_q1():
            return csv_provider.get_response('Q1')

        q1_score = run_q1(llm, csv_patient_response_q1)
        total_score += q1_score
        print(f"\nScore of Q1: {q1_score}")

        # ===== Q2 START =====
        def csv_patient_response_q2(_):
            return csv_provider.get_response('Q2')

        q2_score = run_q2(llm, get_input=csv_patient_response_q2)
        total_score += q2_score
        print(f"\nScore of Q2: {q2_score}")

        # ===== MEMORY ENCODING =====
        # For the memory encoding part, we'll simulate the admin giving the address
        # and assume the patient can recall it (since Q6 will test the actual recall)
        
        print("\n🧑‍⚕️ ADMIN: I will give you a name and address to remember for a few minutes.")
        print("\n RECALL ATTEMPT: John Brown, 42 Market Street, Chicago. Please repeat the name and address.")
        
        # We can simulate a successful encoding for now, since the real test is in Q6
        print("🧓 PATIENT: John Brown, 42 Market Street, Chicago")
        print("\n🧑‍⚕️ ADMIN: Good, now remember that name and address for a few minutes.")
        
        # ===== Q3 START =====
        def csv_patient_response_q3(_):
            return csv_provider.get_response('Q3')

        q3_score = run_q3(llm, get_input=csv_patient_response_q3)
        total_score += q3_score
        print(f"Score of Q3: {q3_score}")

        # ===== Q4 START =====
        q4_attempt_count = 0
        def csv_patient_response_q4(_):
            nonlocal q4_attempt_count
            q4_attempt_count += 1
            response = csv_provider.get_response('Q4')
            print(f"🧓 PATIENT (Attempt {q4_attempt_count}): {response}")
            return response

        # Reset the counter and get the first response normally
        q4_attempt_count = 0
        q4_score = run_q4(llm, get_input=lambda _: csv_provider.get_response('Q4'))
        total_score += q4_score
        print(f"Score of Q4: {q4_score}")

        # ===== Q5 START =====
        q5_attempt_count = 0
        def csv_patient_response_q5(_):
            nonlocal q5_attempt_count
            response = csv_provider.get_response('Q5')
            q5_attempt_count += 1
            return response

        q5_score = run_q5(llm, get_input=csv_patient_response_q5)
        total_score += q5_score
        print(f"Total score of Q5: {q5_score}")

        # ===== Q6 START =====
        def csv_patient_response_q6(_):
            return csv_provider.get_response('Q6')

        q6_score = run_q6(llm, get_input=csv_patient_response_q6)
        total_score += q6_score
        print(f"Score of Q6: {q6_score}")

        print(f"\n=== FINAL RESULTS ===")
        print(f"Trial ID: {trial_id}")
        print(f"Q1: {q1_score}, Q2: {q2_score}, Q3: {q3_score}, Q4: {q4_score}, Q5: {q5_score}, Q6: {q6_score}")
        print(f"Total Score: {total_score}")

    transcript_text = f.getvalue()
    
    # Save transcript with trial ID in filename
    transcript_filename = f"transcript_trial_{trial_id}.txt"
    with open(transcript_filename, "w") as file:
        file.write(transcript_text)

    scores_str = f"{q1_score}~{q2_score}~{q3_score}~{q4_score}~{q5_score}~{q6_score}"
    return scores_str, total_score, transcript_filename

# Original simulate function (keeping for backward compatibility)
def simulate(result1, result2, result3, result4, result5, result6):
    """Original simulate function - kept for backward compatibility"""
    # ... (original code remains the same)
    pass

# Example usage:
if __name__ == "__main__":
    # Example: Run simulation for trial 35
    csv_file = "Corrected_Responses.csv"
    trial_id = 35
    
    try:
        scores, total, transcript_file = simulate_with_csv(csv_file, trial_id)
        print(f"\nSimulation completed!")
        print(f"Scores: {scores}")
        print(f"Total: {total}")
        print(f"Transcript saved to: {transcript_file}")
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        
    # You can also run multiple trials:
    # for trial_id in [35, 63, 64, 72]:  # example trial IDs from your data
    #     try:
    #         scores, total, transcript_file = simulate_with_csv(csv_file, trial_id)
    #         print(f"Trial {trial_id}: {scores} (Total: {total})")
    #     except Exception as e:
    #         print(f"Error with trial {trial_id}: {e}")

'''
