from OllamaGenerate import Ollama
from prompts import diarization_prompt_list, punctuation_prompt, correction_prompt_few_shot, KEYWORD_WHISPER_PROMPT, keywords_audio1
import json 
import re 
import os 
import whisper 
import pandas as pd 
from datetime import datetime


AUDIO = "audio"
base_dir = os.path.join(os.getcwd(), "transcription-error-correction", AUDIO)
FILES_DIR = os.path.join(os.getcwd(), "transcription-error-correction", AUDIO, "diarize")
LLM_MODEL = "llama3:instruct"
def extract_correction(response_string):
    # Pattern for Sentence
    sentence_pattern = re.compile(r'"Corrected Sentence":\s*"(.*?)"')
    # Pattern for Label
    
    # Find all matches
    sentence_matches = sentence_pattern.findall(response_string)
    print(sentence_matches)
    segment_text = ""
    for i in range(len(sentence_matches)):
        segment_text += sentence_matches[i] + "\n\n"
    return segment_text

def download_txt(response_string , filepath): 
    with open(filepath, "w") as f:
        f.write(response_string)
if __name__=="__main__":

    files = os.listdir(FILES_DIR)
    os.makedirs(os.path.join(base_dir, "corrected"), exist_ok=True)
    total_corrected_transcript = ""
    for id in range(len(files)):
        file = files[id]
        print(file)
        with open(os.path.join(FILES_DIR, file), "r") as f:
            segment_text = f.read()
        prompt = correction_prompt_few_shot.format(vocabulary=keywords_audio1,transcript=segment_text)
        corrected_segment= Ollama(model=LLM_MODEL, prompt=prompt).generate_retry()
        download_txt(corrected_segment, os.path.join(base_dir, f"corrected_segment_{id}.txt"))
        corrected_text = extract_correction(corrected_segment)
        download_txt(corrected_text, os.path.join(base_dir,"corrected", f"corrected_transcript_{id}.txt"))
        total_corrected_transcript += corrected_text
    download_txt(total_corrected_transcript, os.path.join(base_dir, "corrected", "total_corrected_transcript.txt"))

