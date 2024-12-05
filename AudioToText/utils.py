import subprocess
import os 
from datetime import datetime
import shutil
from pyannote.core import Segment, Annotation, Timeline
from pydub import AudioSegment
import io
from typing import Any
import numpy as np 
import pandas as pd 

PUNC_SENT_END = ['.', '?', '!']

def to_wav(path: str): 

    print("creating .wav file...")
    _ , file = os.path.split(path)
    filename, extension = os.path.splitext(file)
    output_path = os.path.join(os.getcwd(), "file_db" ,"audio", filename+".wav")
    if  extension!=".wav" and not os.path.exists(output_path): 
        command = [
        'ffmpeg',
        '-i', path,
        # '-loglevel error',  # used to quiet the command 
        output_path
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Conversion completed. WAV file saved as {output_path}")
        except Exception as e:
            print(f"Error during conversion to .wav: {e}")
    else : 
        print(".wav file already exists")
    return output_path
    

def merge_cache(text_cache):
    sentence = ''.join([item[-1] for item in text_cache])
    spk = text_cache[0][1]
    start = text_cache[0][0].start
    end = text_cache[-1][0].end
    return Segment(start, end), spk, sentence

def merge_sentence(spk_text):
    merged_spk_text = []
    pre_spk = None
    text_cache = []
    for seg, spk, text in spk_text:
        if spk != pre_spk and pre_spk is not None and len(text_cache) > 0:
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = [(seg, spk, text)]
            pre_spk = spk

        elif text and len(text) > 0 and text[-1] in PUNC_SENT_END:
            text_cache.append((seg, spk, text))
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = []
            pre_spk = spk
        else:
            text_cache.append((seg, spk, text))
            pre_spk = spk
    if len(text_cache) > 0:
        merged_spk_text.append(merge_cache(text_cache))
    return merged_spk_text

def write_to_txt_diarize(result , file:str, output_filename:str):
    print(file, " for downloading ")
    filename , extension = os.path.splitext(file)
    output_filename = os.path.splitext(output_filename)[0]
    # if os.path.exists(file):
    tm = datetime.now()
    tm = tm.strftime("%Y%m%d-%H%M%S")
    filename = f'{filename}-{tm}'
    output_filename = f"{output_filename}-{tm}"
    file = f"{filename}{extension}"
    print("result", result)
    # saving as csv file : not needed? 
    # df = pd.DataFrame(columns=["start", "end", "speaker", "sentence"])
    # for segment, speaker, sentence in result:
    #     df.loc[len(df)] = {"start": segment.start, "end": segment.end, "speaker": speaker, "sentence": sentence}
    

    # csv_file_path = os.path.join(os.getcwd(), "file_db", f"{output_filename}.csv")
    # print(f"saving to csv file...{csv_file_path}")
    # df.to_csv(csv_file_path, index=False)

    # saving to output
    with open(file, 'w') as f:
        for segment, speaker, sentence in result:
            line = f'{segment.start:.2f} {segment.end:.2f} {speaker} {sentence}\n'
            f.write(line)

    # saving to file db          
    transcription_db_path = os.path.join(os.getcwd(), "file_db", "transcription", f"{output_filename}.txt")
    with open(transcription_db_path, 'w') as f:
        for segment, speaker, sentence in result:
            line = f'{segment.start:.2f} {segment.end:.2f} {speaker} {sentence}\n'
            f.write(line)

    return file

    

def write_to_txt(result, file:str ):
    print(file, " for downloading ")
    if os.path.exists(file):
        filename , extension = os.path.splitext(file)
        tm = datetime.now()
        tm = tm.strftime("%Y%m%d-%H%M%S")
        file = f"{filename}-{tm}{extension}"
    with open(file, 'w') as file : 
        for segment in result["segments"]: 
            file.write(f'{segment["text"]}\n')
    

def clean(path: str): 

    directory, mp3_filename = os.path.split(path)
    filename , extension = os.path.splitext(mp3_filename)
    
    wav_file_path = os.path.join(directory, filename+".wav")
    if os.path.exists(wav_file_path):
        os.remove(wav_file_path)
    # if os.path.exists(path):
    #     os.remove(path)
    print(f"removing file {wav_file_path}")
    return

    # processed_dir = os.path.join(os.getcwd(),"data", "processed")
    # os.makedirs(processed_dir, exist_ok=True)

    # if os.path.exists(path):
    #     shutil.move(path, os.path.join(processed_dir, mp3_filename))





