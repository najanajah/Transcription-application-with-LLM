from OllamaGenerate import Ollama
from prompts import diarization_prompt_list, correction_prompt_few_shot, punctuation_prompt,  KEYWORD_WHISPER_PROMPT, correction_prompt_few_shot_no_vocab, keywords_audio1, keywords_audio2, all_keywords,initial_prompt 

import json 
import re 
import os 
import whisper 
import pandas as pd 
from datetime import datetime

LLM_MODEL = "llama3:instruct"
WHISPER_MODEL = "small.en"
AUDIO_NAME = "audio"
AUDIO_FILE = os.path.join("audio_files", f"{AUDIO_NAME}.mp3")
models = ["base.en" , "small.en" , "medium.en"]

def extract_information(response_string):
    # Pattern for Sentence
    sentence_pattern = re.compile(r'"Sentence":\s*"(.*?)"')
    # Pattern for Label
    label_pattern = re.compile(r'"Label":\s*"(.*?)"')
    # Find all matches
    sentence_matches = sentence_pattern.findall(response_string)
    label_matches = label_pattern.findall(response_string)

    segment_text = ""
    total = min(len(sentence_matches), len(label_matches))
    for i in range(total):
        segment_text += label_matches[i] + ": " + sentence_matches[i] + "\n\n"
    return segment_text

def download_json(response_string , filepath): 
    response_string = response_string.replace("'", "\"")
    response_json = json.loads(response_string)
    with open(filepath, "w") as f:
        json.dump(response_json, f)

def download_txt(response_string , filepath): 
    with open(filepath, "w") as f:
        f.write(response_string)

def parse_list(response_string): 
    response_string = response_string.replace("'", "\"")
    json_match = re.search(r'\[(.*?)\]', response_string, re.DOTALL)
    if json_match:
        json_text = '[' + json_match.group(1) + ']'
    try:
        json_str = json.loads(json_text)
        return json_str
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)

def parse_dict(response_string):
    response_string = response_string.replace("'", "\"")
    try: 
        response_json = json.loads(response_string)
        return response_json
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
    
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


if __name__=="__main__":
    
    for model_name in models:
        model = whisper.load_model(model_name)
        os.makedirs(os.path.join("transcription-error-correction",AUDIO_NAME, model_name), exist_ok=True)
        save_dir = os.path.join("transcription-error-correction",AUDIO_NAME, model_name)
        os.makedirs(os.path.join(save_dir,"diaraize"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "corrected"), exist_ok=True)

        df_all = pd.DataFrame(columns=["id", "step","prompt", "response","start","end", "time-taken"])
        # df_segment = pd.DataFrame(columns=["step","prompt", "response","start","end", "time-taken"])

        # transcript generation 
        result = model.transcribe(AUDIO_FILE , initial_prompt=initial_prompt)
        all_text = result['text']
        with open(os.path.join(save_dir,"whisper-result.json"), "w") as f:
            json.dump(result, f)

        segment_texts = [segment_d["text"] for segment_d in result["segments"]]
        # list of joined 10 segments each 
        compiled_segments = ["\n\n".join(segment_texts[i:i+10]) for i in range(0, len(segment_texts), 10)]
        all_text = "\n\n".join(segment_texts)
        download_txt(all_text, os.path.join(save_dir,"transcript.txt"))

        def process(id, all_text) -> str: 
            # diarization
            st = datetime.now()
            diarization_result_all = Ollama(LLM_MODEL, diarization_prompt_list.format(transcript=all_text)).generate_retry()
            et = datetime.now()
            df_all.loc[len(df_all)] = [id ,"diarization", diarization_prompt_list.format(transcript=all_text), diarization_result_all, st, et, et-st]
            download_txt(diarization_result_all, os.path.join(save_dir,f"diarization_output_all_{id}.txt"))
            text_segment = extract_information(diarization_result_all)
            download_txt(text_segment, os.path.join(save_dir,"diaraize",f"diarized_transcript_{id}.txt"))
            return text_segment

        def correct(id, segment_text) -> str:
            # correction
            st = datetime.now()
            prompt = correction_prompt_few_shot.format(transcript=segment_text, vocabulary=keywords_audio1)
            corrected_segment= Ollama(model=LLM_MODEL, prompt=prompt).generate_retry()
            download_txt(corrected_segment, os.path.join(save_dir, f"corrected_segment_{id}.txt"))
            corrected_text = extract_correction(corrected_segment)
            download_txt(corrected_text, os.path.join(save_dir,"corrected", f"corrected_transcript_{id}.txt"))
            return corrected_text


        print("total segments", len(compiled_segments))
        total_text = ""
        diarize_rttm = ""
        diarized_segments_ls = []
        for i, segment in enumerate(compiled_segments):
            print(f"Processing segment {i}")
            flag = True 
            
            try: 
                sentence = process(i, segment)
                total_text += sentence
                diarized_segments_ls.append(sentence)            
            except Exception as e:
                print("Error processing segment", id , e)
        download_txt(total_text, os.path.join(save_dir,f"total_transcript.txt"))
        file_suffix = AUDIO_FILE.split("\\")[-1].split(".")[0]
        df_all.to_excel(os.path.join(save_dir,f"output_all_{AUDIO_NAME}-{model_name}.xlsx"), index=False)

        corrected_text_full=""
        for i, segment in enumerate(diarized_segments_ls):
            try:
                corrected_text = correct(i, segment)
                corrected_text_full += corrected_text
            except Exception as e:
                print("Error processing segment", id , e)
        download_txt(corrected_text_full, os.path.join(save_dir,f"total_corrected_transcript.txt"))