import os 
import re 
import string
import pandas as pd
from evaluate import load

audio = "audio_new"
wer_metric = load("wer")

KEYWORD = True
if audio == "audio":
    reference_transcript_path = "audio_1.txt"
else: 
    reference_transcript_path = "audio_2.txt"

if audio == "audio":
    reference_path = "audio-1-mtwer.txt"
elif KEYWORD: 
    reference_path = "audio-2-kwwer.txt"
else: 
    reference_path = "audio-2-mtwer.txt"

models_dir_path = os.path.join("initial_prompts", audio)
model_dirs = ["base.en", "small.en", "base.en", "medium.en"]

for file in os.listdir(models_dir_path):
    if os.path.isdir(os.path.join(models_dir_path, file)):
        model_dirs.append(file)

def remove_bracketed_data_and_punctuation(text):
    # Remove bracketed data
    text = re.sub(r'\(.*?\)', '', text)
    # Remove all punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Strip leading/trailing whitespace
    return text.strip()
def get_ordered_occurrences(transcript_text, unique_phrases):
    """
    Identifies and returns ordered occurrences of specified words/phrases in the transcript.
    
    Parameters:
    transcript_text (str): Full transcript as a single string.
    unique_phrases (set): A set of unique words/phrases to detect in order.

    Returns:
    list: Ordered list of detected occurrences with phrases as complete units.
    """
    ordered_occurrences = []
    words = transcript_text.split()  # Split transcript into words for sequential processing
    i = 0
    
    while i < len(words):
        # Check if any phrase starting at the current index exists in unique_phrases
        for phrase in unique_phrases:
            phrase_words = phrase.split()
            phrase_len = len(phrase_words)
            if words[i:i+phrase_len] == phrase_words:  # Match phrase
                ordered_occurrences.append(phrase)
                i += phrase_len  # Skip the entire phrase
                break
        else:
            # If no matching phrase, move to the next word
            i += 1
    
    return ordered_occurrences

if __name__ == "__main__":
    # Read and process the reference text
    with open(reference_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    text = remove_bracketed_data_and_punctuation(text)
    
    # Create a set of unique words or phrases, split by spaces and converted to lowercase
    standardized_unique_words = set(phrase.lower() for phrase in text.splitlines() if phrase)
    print(standardized_unique_words)
    df = pd.DataFrame(columns=["model", "audio", "step", "mt-wer"])

    # Read and process the transcript text
    filename = "nolabel.txt"
    steps = ["9-DIARIZE-STEP-only" , "10-correction-no-keywords" , "11-correction-keyword"]  
    step_label = ["diarize", "Correction (no-keywords)", "Correction (keywords)"]
    for i, step in enumerate(steps):
        for model in model_dirs: 
            file = os.path.join("transcription-error-correction", step, audio, model, filename)
            with open(file, "r", encoding="utf-8") as f:
                    transcript = f.read()
            
            # Split the transcript into words
            transcript = remove_bracketed_data_and_punctuation(transcript)
            transcript_words = transcript.lower().split()

            with open(reference_transcript_path , "r" , encoding="utf-8") as f: 
                reference = f.read()

            reference = remove_bracketed_data_and_punctuation(reference)
            reference = reference.lower()

            # List to hold occurrences of words or phrases in the order they appear
            ordered_occurrences = get_ordered_occurrences(transcript, standardized_unique_words)
            reference_occurences = get_ordered_occurrences(reference, standardized_unique_words)
            print(ordered_occurrences)


            wer = wer_metric.compute(references=[" ".join(reference_occurences)], predictions=["  ".join(ordered_occurrences)])
            df.loc[len(df)] = [model, audio, step_label[i],  wer] ###
    df.to_excel(f"{audio}_kwwer_correction.xlsx", index=False)
    # for dir in model_dirs:

    #     files = os.listdir(os.path.join(models_dir_path, dir))
    #     for file in files:
    #         with open(os.path.join(models_dir_path, dir , file), "r", encoding="utf-8") as f:
    #                 transcript = f.read()
    
    #         # Split the transcript into words
    #         transcript = remove_bracketed_data_and_punctuation(transcript)
    #         transcript_words = transcript.lower().split()

    #         with open(reference_transcript_path , "r" , encoding="utf-8") as f: 
    #             reference = f.read()

    #         reference = remove_bracketed_data_and_punctuation(reference)
    #         reference = reference.lower()

    # # List to hold occurrences of words or phrases in the order they appear
    #         ordered_occurrences = get_ordered_occurrences(transcript, standardized_unique_words)
    #         reference_occurences = get_ordered_occurrences(reference, standardized_unique_words)
    #         print(ordered_occurrences)
    #         print(reference_occurences)
    #         wer = wer_metric.compute(references=[" ".join(reference_occurences)], predictions=["  ".join(ordered_occurrences)])
    #         df.loc[len(df)] = [dir, audio, "step",  wer] ###
    # Search for each phrase in the transcript
    # df.to_excel(f"initial_prompts/{audio}_{dir}_mtwer.xlsx", index=False)
    # print(reference_occurences)
    # print("-"*50)
    # print("Ordered occurrences of unique words/phrases in the transcript:", ordered_occurrences)
   
    # print("Calculated word error rate:", wer)

