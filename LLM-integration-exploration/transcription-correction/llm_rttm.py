from datetime import datetime
import os
from OllamaGenerate import Ollama
from prompts import diarization_prompt_list, punctuation_prompt,  KEYWORD_WHISPER_PROMPT, correction_prompt_few_shot_no_vocab, keywords_audio1, keywords_audio2, all_keywords,initial_prompt 
import json 
import whisper 
import re 
import pandas as pd 


LLM_MODEL = "llama3:instruct"
WHISPER_MODEL = "base.en"
AUDIO_NAME = "audio"
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
    return segment_text, label_matches, sentence_matches

def download_json(response_string , filepath): 
    response_string = response_string.replace("'", "\"")
    response_json = json.loads(response_string)
    with open(filepath, "w") as f:
        json.dump(response_json, f)

def download_txt(response_string , filepath): 
    with open(filepath, "w") as f:
        f.write(response_string)

def write_to_rttm(diarized_segments, whisper_result , output_filename):
    # diarized_texts = [ ]

    # for segment in diarized_segments: 
    #     diarized_texts.extend(segment.split("\n\n"))

    speakers_list = []
    no_label_segments = diarized_segments
    # for i, segment in enumerate(diarized_texts):
    #     if "INTERVIEWER" in segment:
    #         speakers_list.append("SPEAKER_INTERVIEWER")
    #         no_label_segments.append(segment.replace("INTERVIEWER: ", ""))
    #     elif "INTERVIEWEE" in segment:
    #         speakers_list.append("SPEAKER_INTERVIEWEE")
    #         no_label_segments.append(segment.replace("INTERVIEWEE: ", ""))
    
    
    with open(output_filename, 'w') as f:
        for i, segment in enumerate(no_label_segments):
            start_time = whisper_result['segments'][i]['start']
            duration = whisper_result['segments'][i]['end'] - whisper_result['segments'][i]['start']
            speaker_id = no_label_segments[i]
            line = (
                f"SPEAKER {AUDIO_NAME} 1 {start_time:.3f} {duration:.3f} <NA> <NA> {speaker_id} <NA> <NA> \n"
            )
            f.write(line)

    print(f"RTTM file created at: {output_filename}")

# Use the above function to save the .rttm file after diarization processing
if __name__ == "__main__":
    
    device="cpu"
    model = whisper.load_model(WHISPER_MODEL, device=device)
    os.makedirs(os.path.join("transcription-error-correction",AUDIO_NAME), exist_ok=True)
    save_dir = os.path.join("transcription-error-correction",AUDIO_NAME)
    os.makedirs(os.path.join(save_dir,"diaraize"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "corrected"), exist_ok=True)

    df_all = pd.DataFrame(columns=["id", "step","prompt", "response","start","end", "time-taken"])
    # df_segment = pd.DataFrame(columns=["step","prompt", "response","start","end", "time-taken"])

    # transcript generation 
    result = model.transcribe(AUDIO_FILE )
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
        text_segment, label_matches , sentence_matches = extract_information(diarization_result_all)
        download_txt(text_segment, os.path.join(save_dir,"diaraize",f"diarized_transcript_{id}.txt"))
        return text_segment, label_matches , sentence_matches


    print("total segments", len(compiled_segments))
    total_text = ""
    diarize_rttm = ""
    diarized_segments_ls = []
    # for i, segment in enumerate(compiled_segments):
    #     print(f"Processing segment {i}")
    #     flag = True 
        
    #     try: 
    #         sentence = process(i, segment)
    #         total_text += sentence
    #         diarized_segments_ls.append(sentence)            
    #     except Exception as e:
    #         print("Error processing segment", id , e)
    # download_txt(total_text, os.path.join(save_dir,f"total_transcript.txt"))

    total_text = ""
    diarized_segments_ls = []
    
    total_st = datetime.now()
    labels = []
    for i, segment in enumerate(compiled_segments):
        print(f"Processing segment {i}")
        
        try: 
            sentence,  speaker_labels, sntences   = process(i, segment)
            total_text += sentence
            diarized_segments_ls.append(sentence)
            labels.extend(speaker_labels)
        except Exception as e:
            print("Error processing segment", i, e)

    total_et = datetime.now()
    # Save full transcript
    download_txt(total_text, os.path.join(save_dir, f"total_transcript.txt"))
    df_all.loc[len(df_all)] = [i, "total", "total", total_text, total_st, total_et, total_et-total_st]
    df_all.to_excel(os.path.join(save_dir, f"output_all_{AUDIO_NAME}.xlsx"), index=False)

    # Create RTTM file for diarized output
    rttm_filename = os.path.join(save_dir, f"{AUDIO_NAME}.rttm")
    write_to_rttm(labels, result,  rttm_filename)
