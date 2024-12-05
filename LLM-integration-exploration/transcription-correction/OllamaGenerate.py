import ollama
import json 
import re
import random

MAX_RETRY = 3
DEBUG = False
class Ollama():
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
                    if DEBUG:
                         return "debug"
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

