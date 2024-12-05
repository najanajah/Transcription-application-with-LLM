import ollama
import json 
import re
import random
from FeatureExtractor import pipeline_prompts as prompts

'''
This module is used to generate text using the Ollama API.

The module contains the following functions:
generate_keywords(context: str) -> str
generate_background(context: str) -> str
generate_summary(context: str) -> str
generate_reflection(context: str) -> str
generate_conclusion(context: str) -> str
replace_speaker_id_with_label(context: str) -> str

Class for generating text using Ollama API:
Ollama(model:str, prompt:str)
'''

with open("config.json", "r") as file : 
                DEBUG =  json.load(file).get("DEBUG", True)
MAX_RETRY = 3
LLM = 'llama3:instruct'
KEYWORDS_DEBUG =  ['Posting', 'Surgical', 'Emergency', 'Healthcare', 'Professionals', 'Impact', 'Interaction', 'Palliative Care', 'Surgery', 'E.D.', 'OT', 'Clinics']
   

def generate_keywords(context: str) -> str:
    '''Return keywords of the context. accepts list or string'''
    if DEBUG: 
        kw_ls = [random.choice(KEYWORDS_DEBUG) for i in range(5)] 
        print("Feature extractor keywords: ", kw_ls)
        keyword_dict = {"Keywords": kw_ls}
        return json.dumps(keyword_dict)
    prompt = prompts.KEYWORDS_PROMPT.format(context=context)
    Ollama = Ollama(model=LLM, prompt=prompt)
    response = Ollama.generate_retry()
    return response

def generate_background(context: str) -> str:
    '''Return background of the context'''
    if DEBUG:
        return "This is a background"
    prompt = prompts.BACKGROUND_PROMPT.format(context=context)
    Ollama = Ollama(model=LLM, prompt=prompt)
    response = Ollama.generate_retry()
    return response

def generate_summary(context: str) -> str:
    '''Return summary of the context'''
    if DEBUG:
        return "This is a summary"
    prompt = prompts.SUMMARY_PROMPT.format(context=context)
    Ollama = Ollama(model=LLM, prompt=prompt)
    response = Ollama.generate_retry()
    return response

def generate_reflection(transcription:str , context: str, background: str) -> str:
    '''Return reflection of the context'''
    if DEBUG:
        return "This is a reflection"
    prompt = prompts.REFLECTION_PROMPT.format(transcript=transcription, context=context, background=background)
    Ollama = Ollama(model=LLM, prompt=prompt)
    response = Ollama.generate_retry()
    return response

def generate_conclusion(context: str, background: str , reflection: str) -> str:
    '''Return conclusion of the context'''
    if DEBUG:
        return "This is a conclusion"
    prompt = prompts.CONCLUSION_PROMPT.format(context=context, background=background, reflection=reflection)
    Ollama = Ollama(model=LLM, prompt=prompt)
    response = Ollama.generate_retry()
    return response
     
def replace_speaker_id_with_label(context: str) -> str:
    '''Return speaker id of the context and replace in the original context'''
    if DEBUG:
        speaker_json = '''{"SPEAKER_00": "INTERVIEWER","SPEAKER_01": "INTERVIEWEE"}'''
    else: 
        prompt = prompts.SPEAKER_ID_PROMPT.format(context=context)
        Ollama = Ollama(model='llama3:instruct', prompt=prompt)
        response = Ollama.generate_retry()
        speaker_json = response['response']
    try: 
        speaker_json = speaker_json.encode('utf-8').decode('utf-8', errors='replace')
        json_speaker = json.loads(speaker_json)
        for spk, label in json_speaker.items():
                transcript = re.sub(rf'\b{spk}\b', label, transcript)
    except Exception as e:
                print("Error replacing label: ", e)

    return transcript

class Ollama():
    '''Ollama class for generating text using ollama API'''
    model:str 
    '''model to use for generation'''
    prompt: str 
    '''prompt to use for generation'''
    
    def __init__(self, model:str, prompt:str):
        assert isinstance(prompt, str), "Prompt should be a string"
        assert isinstance(model, str), "Model should be a string"
        _allowed_models = [ d['name']  for d in ollama.list()['models']]
        if model not in _allowed_models:
            try:
                ollama.chat(model)
            except ollama.ResponseError as e:
                    print('Error:', e.error)
                    if e.status_code == 404:
                        print('Model not found')
                        try: 
                            ollama.pull(model)  
                        except Exception as e:
                            raise ValueError(f"Model {model} not found. Please check the model name and try again")
                                   
        self.model = model
        self.prompt = prompt

    def generate_retry(self) -> str:
            count = 1
            def retry(retry_count):
                try: 
                    print("attempting to  generate ")
                    response = ollama.generate(model=self.model, prompt=self.prompt)
                    response = response['response']
                    return response
                except Exception as e:
                    if retry_count >= MAX_RETRY: 
                        print("Encountered error: ", e, "Max retries reached")
                        return "" , ""
                    print("Encountered error: ", e, "Retrying")
                    return retry(retry_count + 1)   
            return retry(count)

