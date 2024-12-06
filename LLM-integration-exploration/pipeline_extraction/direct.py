import whisper
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os
import subprocess
from pyannote.audio import Pipeline
import pyannote
import torch
import json
import re
import ollama
import datetime 
from pyannote.core import Segment
import pandas as pd
from combined_transcripts_prompts import IDENTIFY_TOPICS_PROMPT, SUMMARY_PROMPT_1, SUMMARY_PROMPT_2, SUMMARY_PROMPT_3, hallucination_prompt, JSON_PROMPT, KEYWORD_WHISPER_PROMPT, SPEAKER_BACKGROUND_PROMPT, FORMAT_SUFFIX, REFLECTION_PROMPT,CONCLUSION_PROMPT,SPEAKER_ID_PROMPT

'''
Used to generate the direct pipeline responses for transcripts as baseline approach for evaluation. 
'''

LLM_MODEL = "llama3:instruct"

if __name__=="__main__":
    
    trans_dir = os.path.join(os.getcwd(), "evaluate", "transcripts")
    files = os.listdir(trans_dir)

    transcripts = []
    for id, file in enumerate(files):
        # read file 
        with open(os.path.join(trans_dir, file), "r") as f:
            transcript = f.read()
            
        # sub speaker 
        response = ollama.generate(model=LLM_MODEL, prompt=SPEAKER_ID_PROMPT.format(context=transcript))
        speaker_json = response['response']
        with open(os.path.join(os.getcwd(), "evaluate", f"response_{id}.txt"), "w") as file :
            file.write(speaker_json)
        try: 
            speaker_json = speaker_json.encode('utf-8').decode('utf-8', errors='replace')
            json_speaker = json.loads(speaker_json)
            for spk, label in json_speaker.items():
                transcript = re.sub(rf'\b{spk}\b', label, transcript)

        except Exception as e:
                print("Error replacing label: ", e)

        # transcripts.append(transcript)
        with open(os.path.join(os.getcwd(), "evaluate", f"replaced_transcript_{id}.txt"), "w") as file :
            file.write(transcript)

        # gen topic - save 
        response = ollama.generate(model=LLM_MODEL, prompt=SUMMARY_PROMPT_1.format(context=transcript))
        response = response['response']

        with open(os.path.join(os.getcwd(), "evaluate", f"topic_{id}.txt"), "w") as file :
            file.write(response)

        # gen back -save 
        SPEAKER_BACKGROUND_PROMPT += transcript
        bk_response = ollama.generate(model=LLM_MODEL, prompt=SPEAKER_BACKGROUND_PROMPT)
        bk_response = bk_response['response']

        with open(os.path.join(os.getcwd(), "evaluate", f"background_{id}.txt"), "w") as file :
            file.write(bk_response)


        # gen reflection - save
        ref_response = ollama.generate(model=LLM_MODEL, prompt=REFLECTION_PROMPT.format(background=bk_response, context=response))
        ref_response = ref_response['response']

        with open(os.path.join(os.getcwd(), "evaluate", f"reflection_{id}.txt"), "w") as file :
            file.write(ref_response)

        # gen conclusion - save
        con_response = ollama.generate(model=LLM_MODEL, prompt=CONCLUSION_PROMPT.format(background=bk_response, context=transcript, reflection=ref_response))
        con_response = con_response['response']

        with open(os.path.join(os.getcwd(), "evaluate", f"conclusion_{id}.txt"), "w") as file :
            file.write(con_response)
