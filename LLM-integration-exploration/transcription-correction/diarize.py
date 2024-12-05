from OllamaGenerate import Ollama
from prompts import diarization_prompt_list, punctuation_prompt, KEYWORD_WHISPER_PROMPT
import json 
import re 
import os 
import whisper 
import pandas as pd 
from datetime import datetime

LLM_MODEL = "llama3:instruct"
WHISPER_MODEL = "base.en"
AUDIO_NAME = "audio_new"
AUDIO_FILE = os.path.join("audio_files", f"{AUDIO_NAME}.mp3")

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
    
        


if __name__=="__main__":
    device="cpu"
    model = whisper.load_model(WHISPER_MODEL, device=device)
    os.makedirs(os.path.join("transcription-error-correction",AUDIO_NAME), exist_ok=True)
    save_dir = os.path.join("transcription-error-correction",AUDIO_NAME)
    os.makedirs(os.path.join(save_dir,"diarize"), exist_ok=True)

    df_all = pd.DataFrame(columns=["id", "step","prompt", "response","start","end", "time-taken"])
    # df_segment = pd.DataFrame(columns=["step","prompt", "response","start","end", "time-taken"])

    # transcript generation 
    result = model.transcribe(AUDIO_FILE)
    all_text = result['text']
    
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
        download_txt(text_segment, os.path.join(save_dir,"diarize",f"diarized_transcript_{id}.txt"))
        return text_segment

        # correction 
        # correction_result_all = Ollama(LLM_MODEL, correction_prompt.format(vocabulary=KEYWORD_WHISPER_PROMPT,transcript=diarization_result_all)).generate_retry()
        # df_all.loc[len(df_all)] = [id, "correction", correction_prompt.format(vocabulary=KEYWORD_WHISPER_PROMPT,transcript=diarization_result_all), correction_result_all, st, et, et-st]
        # download_txt(correction_result_all, os.path.join(save_dir,f"correction_output_all_{id}.txt"))
        # corrected_json = parse_list(correction_result_all)
        # corrected_transcript = ""
        # for sentence_dict in corrected_json:
        #     corrected_transcript += sentence_dict["Corrected Sentence"] + "\n\n"
        # download_txt(corrected_transcript, os.path.join(save_dir,f"corrected_transcript_{id}.txt"))

    print("total segments", len(compiled_segments))
    total_text = ""
    for i, segment in enumerate(compiled_segments):
        print(f"Processing segment {i}")
        flag = True 
        # while flag:
        try: 
            sentence = process(i, segment)
            total_text += sentence
            # flag = False
        except Exception as e:
            print("Error processing segment", id , e)
    download_txt(total_text, os.path.join(save_dir,f"total_transcript.txt"))
    file_suffix = AUDIO_FILE.split("\\")[-1].split(".")[0]
    df_all.to_excel(os.path.join(save_dir,f"output_all_{AUDIO_NAME}.xlsx"), index=False)

    