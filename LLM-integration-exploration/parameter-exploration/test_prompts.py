from prompts import prompt_1, prompt_2, prompt_3
import datetime
import pandas as pd 
import os 
import whisper
from pyannote.audio import Pipeline
import pyannote
import torch
import json
from pyannote.core import Segment



audio_paths = [ os.path.join("audio_files", "audio.mp3")]


# def load_transcriber(model):
#     return AudioToText(model=model)


if __name__ == "__main__": 
    device="cpu"
    # dir = os.path.join(os.getcwd(), "test", "data")
    # ref_path = os.path.join(os.getcwd(), "test", "reference","trancript2_cleaned.txt")

    model_name = "base.en"
    os.makedirs("results-prompt", exist_ok=True)
    
    
    for id , name in enumerate(audio_paths):
        # transcriber = load_transcriber(model)
        # filepath = os.path.join(dir, name)
        print(model_name)
        df = pd.DataFrame(columns=["id", "prompt","task", "model", "response", "time-taken", "start-time", "end-time", "audio"])

        model = whisper.load_model(model_name, device=device)
        print("no prompt")
        st = datetime.datetime.now()
        transcribed_content = model.transcribe(name)
        et = datetime.datetime.now()
        df.loc[len(df)] = {"id": id ,"task" : "transcription", "prompt" :"no prompt", "model" : model_name, "response": transcribed_content["text"] , "time-taken": et-st, "start-time": st, "end-time": et, "audio": name}
        print("no prompt added to df for model: ")

        print("prompt 1")
        st = datetime.datetime.now()
        transcribed_content = model.transcribe(name, initial_prompt=prompt_1) 
        et = datetime.datetime.now()
        transcribed_content = transcribed_content["text"]
        df.loc[len(df)] = {"id": id ,"task" : "transcription", "prompt" :prompt_1, "model" : model_name, "response": transcribed_content , "time-taken": et-st, "start-time": st, "end-time": et, "audio": name}
        print("prompt added to df for model: ", prompt_1)
        
        print("prompt 2")
        st = datetime.datetime.now()
        transcribed_content = model.transcribe(name, initial_prompt=prompt_2)
        et = datetime.datetime.now()
        df.loc[len(df)] = {"id": id ,"task" : "transcription", "prompt" :prompt_2, "model" : model_name, "response": transcribed_content["text"] , "time-taken": et-st, "start-time": st, "end-time": et, "audio": name}
        print("prompt added to df for model: ", prompt_2)

        print("prompt 3")
        st = datetime.datetime.now()
        transcribed_content = model.transcribe(name, initial_prompt=prompt_3)
        et = datetime.datetime.now()
        df.loc[len(df)] = {"id": id ,"task" : "transcription", "prompt" :prompt_3, "model" : model_name, "response": transcribed_content["text"] , "time-taken": et-st, "start-time": st, "end-time": et, "audio": name}
        df.to_excel(os.path.join("results-prompt","prompts.xlsx", index=False))
        # id+=1