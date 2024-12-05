import ollama 
import datetime
import pandas as pd 
import os 
import whisper
from pyannote.audio import Pipeline
import pyannote
import torch
import json
# from AudioToText.AudioToText import AudioToText
from AudioToText.utils import to_wav, merge_sentence
from pyannote.core import Segment


def write_to_rttm(result, file: str, output_filename: str):
    """
    Write diarization results to an .rttm file.

    Parameters:
    - result: List of tuples (Segment, speaker, sentence) from the diarization result.
    - file (str): Original audio file path.
    - output_filename (str): Name of the output RTTM file.
    """
    print(file, "for downloading")
    filename, _ = os.path.splitext(file)
    output_filename = os.path.splitext(output_filename)[0]
    
    # Generate timestamped filenames
    tm = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"{output_filename}-{tm}.rttm"
    
    # Write to RTTM format
    with open(output_filename, 'w') as f:
        for segment, speaker, sentence in result:
            start_time = segment.start
            duration = segment.end - segment.start
            speaker_id = speaker.replace("SPEAKER_", "")  # Remove prefix if needed

            # Write RTTM line
            line = (
                f"SPEAKER {filename} 1 {start_time:.2f} {duration:.2f} <NA> <NA> {speaker_id} <NA> <NA> {sentence}\n"
            )
            f.write(line)
    
    print("RTTM file created at:", output_filename)
    return output_filename


audio_path = os.path.join("audio_files", "audio.mp3")

def diarize_result(whisper_result, diarization_result): 
        # list of segments with timestamp 
        timestamp_texts = []
        for item in whisper_result['segments']:
            start = item['start']
            end = item['end']
            text = item['text']
            timestamp_texts.append((Segment(start, end), text))

        # Adding speaker to each segment   
        spk_text = []
        for seg, text in timestamp_texts:
            # return the argmax value of "speaker" within the timestamps of segement passed 
            speaker = diarization_result.crop(seg).argmax()
            spk_text.append((seg, speaker, text))

            # merge together consecutive segments with the same speaker
        processed = merge_sentence(spk_text)
            
        return processed

# def load_transcriber(model):
#     return AudioToText(model=model)


if __name__ == "__main__": 
    
    # dir = os.path.join(os.getcwd(), "test", "data")
    # ref_path = os.path.join(os.getcwd(), "test", "reference","trancript2_cleaned.txt")
    # files = []
    # for file in os.listdir(dir): 
    #     files.append(file)

    # print(f'files   {files}')
    audio = "audio"
    filepath = os.path.join(os.getcwd(), "audio_files", f"{audio}.mp3")
    # whisper_models = ["base.en", "tiny.en"]
    model_name = "base.en"
    key_path = os.path.join(os.getcwd(),"credentials.json")
    with open(key_path, "r") as file : 
                key =  json.load(file).get("HUGGINGFACE_TOKEN")
    print("loading Pyannote pipeline...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=key)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cuda":
        pipeline = pipeline.to(device)  
    print("Pyannote pipeline loaded successfully.")

    
    
 
    
        
    print("prompt 1")
    print(model_name)
    df = pd.DataFrame(columns=["id", "task", "model", "time-taken", "start-time", "end-time", "audio"])

    model = whisper.load_model(model_name)
    st = datetime.datetime.now()
    transcribed_content = model.transcribe(filepath) 
    tt = datetime.datetime.now()
    # get transcription and diarization time separately
    wav_path = to_wav(filepath)
    result = pipeline(wav_path, num_speakers=2)
    diarization_result = diarize_result(transcribed_content, result)
    d_path = write_to_rttm(diarization_result, filepath, "diarization_result_test")
    with open(d_path, "r") as file :
        diarization_result = file.read() #.replace("\n", " ").replace(",", " ")
    # transcribed_content = "etcetc"
    et = datetime.datetime.now()
    transcribed_content = transcribed_content["text"]
    df.loc[len(df)] = [id, "diarize", "pyannote", et-st, st, et, audio]

    df.to_excel(f"test\\results-prompt\\_{model_name}_{audio}.xlsx", index=False)
        # id+=1


    