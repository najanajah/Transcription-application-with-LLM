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
from evaluate_prompt import hallucination_prompt
from task import SPEAKER_BACKGROUND_PROMPT, REFLECTION_PROMPT, CONCLUSION_PROMPT, SUMMARY_PROMPT_1

'''
Used to evaluate the direct and pipeline generations using a head-to-head comparison on 3 metrics.
    1. Comprehensiveness
    2. Directness
    3. Diversity

Ensure that the direct pipeline responses are generated before running this script.

the scripts for comparison should be in the following directory structure:
    evaluate
        audio_1
            direct
                background.txt
                summary.txt
                reflection.txt
                conclusion.txt
            generated
                background.txt
                summary.txt
                reflection.txt
                conclusion.txt
'''
LLM_MODEL = "llama3:instruct"

if __name__=="__main__":
    audio = "audio_1"
    dir = os.path.join(os.getcwd(), "evaluate", audio)
    direct_dir = os.path.join(dir, "direct")
    gen_dir = os.path.join(dir, "generated")
    reference = os.path.join(dir, "reference")
    audio ="audio_1"

    files = ["background.txt" , "summary.txt" , "reflection.txt", "conclusion.txt"]
    task = [SPEAKER_BACKGROUND_PROMPT, SUMMARY_PROMPT_1, REFLECTION_PROMPT, CONCLUSION_PROMPT]
    h_df = pd.DataFrame(columns=["id", "prompt","task", "audio", "response"])
    for file , task in zip(files, task):
        with open(os.path.join(direct_dir, file), "r") as f:
            direct = f.read()
        with open(os.path.join(gen_dir, file), "r") as f:
            gen = f.read()
        with open(os.path.join(reference, "trans.txt"), "r") as f:
            ref = f.read()
        
        for i in range(20):
            c_response = ollama.generate(model=LLM_MODEL, prompt=hallucination_prompt.format(transcript=ref, text1=direct, text2=gen))
            h_df.loc[len(h_df)] = {"id": 1, "prompt": hallucination_prompt.format(text2=direct, text1=gen ,task=task), "task": file, "audio": audio, "response": c_response["response"]}

    h_df.to_excel(f"evaluate/results/hallucination-{audio}.xlsx", index=False)
   