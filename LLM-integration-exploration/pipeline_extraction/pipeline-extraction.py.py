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
from uuid import uuid4
from AudioToText.utils import merge_sentence 
from combined_transcripts_prompts import IDENTIFY_TOPICS_PROMPT, SUMMARY_PROMPT, hallucination_prompt, JSON_PROMPT, KEYWORD_WHISPER_PROMPT, SPEAKER_BACKGROUND_PROMPT, FORMAT_SUFFIX, REFLECTION_PROMPT,CONCLUSION_PROMPT

'''
This script implements a pipeline for extracting information from audio files using the following steps:
    1. Splitting the audio file into chunks
    2. Transcribing the audio file
    3. Retrieving the top 4 references from the vectorstore
    4. Transcribing the audio file with the top 4 references as prompts
    5. Generating summaries for each of the transcriptions
    6. Combining the summaries into a single summary
    7. Generating speaker background
    8. Generating reflection
    9. Generating conclusion

Excel files are downloaded at each stage of execution detailing the input, output and time taken. 

Variables to change: 
    1. LLM_MODEL: The model used for generating text
    2. AUDIO: The path to the audio file
    3. FILENAME: The name of the output files
    4. Credentials_path : The path to the credentials.json file containing the Huggingface token
    
'''

LLM_MODEL = "llama3:instruct"
### df for storing results
df = pd.DataFrame(columns=["id", "prompt","task", "model", "response", "time-taken", "start-time", "end-time"])
FILENAME = "results-WITH-SPLIT-AUDIO-TRANS-ONLY"
os.makedirs("output", exist_ok=True)
credentials_path = os.path.join(os.getcwd(),"credentials.json")

### creating vectorstore client 
files = os.listdir("references")
references = []

for file in files:
    with open(f"references/{file}", "r", encoding="utf-8") as f:
        references.append(f.read())

all_splits = []
for reference in references:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    all_splits.extend(text_splitter.split_text(reference))

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
persistent_client = chromadb.PersistentClient()
collection = persistent_client.get_or_create_collection("collection_name")
vector_store_from_client = Chroma(
    client=persistent_client,
    collection_name="collection_name",
    embedding_function=embeddings,
)
# collection.add(documents=all_splits, ids=[str(uuid4()) for _ in range(len(all_splits))])

### splitting audio for prompt matching 
def split_audio(audio_file, output_dir, chunk_size=3*60):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    command = f'ffmpeg -i "{audio_file}" -f segment -segment_time {chunk_size} -c copy "{output_dir}/part_%03d.mp3"'
    subprocess.call(command, shell=True)
    # return the audio data in the output directory
    list_files = os.listdir(output_dir)
    mid = len(list_files) // 2
    print(mid)
    print(list_files)
    path =  os.path.join(output_dir, list_files[mid])
    # remove all expect the middle file
    for file in list_files:
        print(file)
        if file != list_files[mid]:
            os.remove(os.path.join(output_dir, file))
    return path

def clean_split_audio(output="split_audio"): 
    for file in os.listdir(output):
        os.remove(os.path.join(output, file))

## setting audio file 
AUDIO = os.path.join("audio_files", "audio_cut_2.mp3")
split_audio_output = os.path.join(os.getcwd(), "split_audio")
path = split_audio(AUDIO, split_audio_output)


## transcribing audio file and retrieving prompts
model_name = "tiny.en"
device="cpu"
model = whisper.load_model(model_name, device=device)
st = datetime.datetime.now()
text = model.transcribe(AUDIO)
et = datetime.datetime.now()
text = text["text"]
df.loc[len(df)] = {"id": 1 ,"prompt" :"-", "model" : model_name, "task": "transcribing split audio" , "response": text , "time-taken": et-st, "start-time": st, "end-time": et}
df.to_excel(f"{FILENAME}-1.xlsx", index=False)
st = datetime.datetime.now()
docs = vector_store_from_client.similarity_search(text)
et = datetime.datetime.now()
print(len(docs))
clean_split_audio(split_audio_output)
df.loc[len(df)] = {"id": 2 ,"prompt" :"-", "model" : model_name, "task": "prompts retrieved" , "response": docs , "time-taken": et-st, "start-time": st, "end-time": et}
df.to_excel(f"{FILENAME}-2.xlsx", index=False)


## transcribing with prompts 
prompts = [doc.page_content for doc in docs]

prompts.append(KEYWORD_WHISPER_PROMPT)


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
 
key_path = os.path.join(credentials_path)
with open(key_path, "r") as file : 
            key =  json.load(file).get("HUGGINGFACE_TOKEN")
print("loading Pyannote pipeline...")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=key)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
if device == "cuda":
    pipeline = pipeline.to(device)  
print("Pyannote pipeline loaded successfully.")

os.makedirs("prompt_transcriptions", exist_ok=True)

def write_to_txt_diarize(result , file:str, output_filename:str, prompt_id:str):
    file = os.path.join(os.getcwd(),"prompt_transcriptions", f"{output_filename}-{prompt_id}.txt")
    with open(file, 'w') as f:
         f.write(result)
  
    print(f"saved to {file}")
    return file

def to_wav(path: str): 
    path = path.replace("\\file_db", "")
    print("creating .wav file...")
    _ , file = os.path.split(path)
    filename, extension = os.path.splitext(file)
    output_path = os.path.join(os.getcwd(),"audio_files", filename+".wav")
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

# transcripts = []
d_transcripts = []
print(prompts)
for id , prompt in enumerate(prompts):
        st = datetime.datetime.now()
        print(f"generating transcript for prompt {id}")
        transcribed_content = model.transcribe(AUDIO, initial_prompt=prompt) 
        d_transcripts.append(transcribed_content["text"])
        transcribed_content = transcribed_content["text"]
        print("to wav")
        wav_path = to_wav(AUDIO)
        print("diarizing...")
        result = pipeline(wav_path, num_speakers=2)
        print("diarizing completed")
        diarization_result = diarize_result(transcribed_content, result)
        print(diarization_result)
        d_path = write_to_txt_diarize(result=transcribed_content, file=AUDIO, output_filename="diarization_result_test", prompt_id=id)
        with open(d_path, "r") as file :
            file_contents = file.read()
        d_transcripts.append(file_contents)
        et = datetime.datetime.now()
        df.loc[len(df)] = {"id": 3  ,"prompt" : prompt, "model" : model_name, "task": "generated" , "response": transcribed_content , "time-taken": et-st, "start-time": st, "end-time": et}

df.to_excel(f"{FILENAME}-3.xlsx", index=False)


def check_hallucination(transcript , generated_response): 
    try: 
        response = ollama.generate(model=LLM_MODEL, prompt=hallucination_prompt.format(context=transcript, text=generated_response))
        response = response['response']
        if response in ["YES", "NO"]:
            x = re.search(r'\b(YES|NO)\b', response)
            response = x.group()
            return response 
        else: 
            raise Exception("Invalid response")
    except Exception as e:
        print("Error: ", e)
        # should the default response be NO?
        return "NO"
    
def get_summary_list(txt:str) -> list:
    try: 
        return json.loads(txt)
    except Exception as e:
        pass
        response = ollama.generate(model=LLM_MODEL, prompt=JSON_PROMPT.format(context=txt, format="list of JSON objects"))
        txt = response['response']
        # txt = txt.encode('utf-8').decode('utf-8', errors='replace')
        return json.loads(txt)
         
        
MAX_RETRY = 3


def generate_summary(context: str) -> str:
    '''Return a summary of the context'''
    count = 1
    def retry(retry_count):
        try: 
            print("attempting to summarize")
            response = ollama.generate(model=LLM_MODEL, prompt=SUMMARY_PROMPT.format(context=context))
            response = response['response']
            summary_list = []
            return summary_list, response
        except Exception as e:
            if retry_count >= MAX_RETRY: 
                print("Encountered error: ", e, "Max retries reached")
                return "" , ""
            print("Encountered error: ", e, "Retrying")
            return retry(retry_count + 1)   
    return retry(count)


## generating summary 
sum_ls_ls = []
sum_str_ls = []
for id , trans in enumerate(d_transcripts): 
    st = datetime.datetime.now()
    print(f"generating summary for prompt {id}")
    summary_list, summary = generate_summary(trans)
    sum_ls_ls.append(summary_list)
    sum_str_ls.append(summary)
    et = datetime.datetime.now()
    df.loc[len(df)] = {"id": 4  ,"prompt" : id, "model" : LLM_MODEL, "task": "generate individual summaries" , "response": summary , "time-taken": et-st, "start-time": st, "end-time": et}
df.to_excel(f"{FILENAME}-4.xlsx", index=False)

with open("testing-list.txt", "w") as f:
    for item in sum_str_ls:
        f.write("%s\n" % item)

## combining summaries 
prompt = "CONTEXT \n"
for id, summary in enumerate(sum_str_ls):
    if type(summary) == str :
            prompt += f'''TRANSCRIPT - {id} \n  \n {summary}  \n\n'''

IDENTIFY_TOPICS_PROMPT =  IDENTIFY_TOPICS_PROMPT + prompt 
IDENTIFY_TOPICS_PROMPT = IDENTIFY_TOPICS_PROMPT + FORMAT_SUFFIX


# def generate_combined_summary() -> str:
#     response = ollama.generate(model=LLM_MODEL, prompt=COMBINE_SUMMARY_PROMPT)
#     response = response['response']
#     return response

def generate_combined_summary() -> str:
    response = ollama.generate(model=LLM_MODEL, prompt=IDENTIFY_TOPICS_PROMPT)
    response = response['response']
    return response


st = datetime.datetime.now()
response = generate_combined_summary()
et = datetime.datetime.now()
df.loc[len(df)] = {"id": 5  ,"prompt" : IDENTIFY_TOPICS_PROMPT, "model" : LLM_MODEL, "task": "combine summaries" , "response": response , "time-taken": et-st, "start-time": st, "end-time": et}
df.to_excel(f"{FILENAME}-5.xlsx", index=False)
print(response)

st = datetime.datetime.now()
try: 
    json_response = get_summary_list(response)
except Exception as e:
    print("Error: ", e)
    print("response\n", response)
    json_response = None
et = datetime.datetime.now()
combined_summary_path = os.path.join(os.getcwd(), "output","combined_summary.json")
with open(combined_summary_path, "w") as file :
            json.dump(json_response, file)
df.loc[len(df)] = {"id": 6  ,"prompt" : JSON_PROMPT, "model" : LLM_MODEL, "task": "get_json" , "response": json_response , "time-taken": et-st, "start-time": st, "end-time": et}


## speaker background 
APPENDED_SPEAKER_BACKGROUND_PROMPT = ""
def generate_background(transcripts:list ) -> str:
    '''Return a summary of the context'''
    count = 1
    global APPENDED_SPEAKER_BACKGROUND_PROMPT
    APPENDED_SPEAKER_BACKGROUND_PROMPT = SPEAKER_BACKGROUND_PROMPT + "".join(transcripts)
    def retry(retry_count):
        try: 
            print("attempting to summarize")
            response = ollama.generate(model=LLM_MODEL, prompt=APPENDED_SPEAKER_BACKGROUND_PROMPT)
            response = response['response']
            return response
        except Exception as e:
            if retry_count >= MAX_RETRY: 
                print("Encountered error: ", e, "Max retries reached")
                return "" 
            print("Encountered error: ", e, "Retrying")
            return retry(retry_count + 1)   
    return retry(count)


st = datetime.datetime.now()
background_response = generate_background(transcripts=d_transcripts)
et = datetime.datetime.now()
background_path = os.path.join(os.getcwd(), "output","background.txt")
with open(background_path, "w") as file :
            file.write(background_response)
df.loc[len(df)] = {"id": 7  ,"prompt" : APPENDED_SPEAKER_BACKGROUND_PROMPT, "model" : LLM_MODEL, "task": "speaker background" , "response": background_response , "time-taken": et-st, "start-time": st, "end-time": et}

## reflection generation 

def generate_reflection(background_response: str , context: str ) -> str:
    '''Return a summary of the context'''
    count = 1
    def retry(retry_count):
        try: 
            print("attempting to summarize")
            response = ollama.generate(model=LLM_MODEL, prompt=REFLECTION_PROMPT.format(background=background_response , context=context))
            response = response['response']
            return response
        except Exception as e:
            if retry_count >= MAX_RETRY: 
                print("Encountered error: ", e, "Max retries reached")
                return "" 
            print("Encountered error: ", e, "Retrying")
            return retry(retry_count + 1)   
    return retry(count)

st = datetime.datetime.now()
reflection_response = generate_reflection(background_response,response)
et = datetime.datetime.now()
reflection_path = os.path.join(os.getcwd(), "output","reflection.txt")
with open(reflection_path, "w") as file :
            file.write(reflection_response)
df.loc[len(df)] = {"id": 8  ,"prompt" : REFLECTION_PROMPT, "model" : LLM_MODEL, "task": "speaker background" , "response": reflection_response , "time-taken": et-st, "start-time": st, "end-time": et}

## conclusion generation
def generate_conclusion(context ,reflection, background ) -> str:
    '''Return a summary of the context'''
    count = 1
    def retry(retry_count):
        try: 
            print("attempting to summarize")
            response = ollama.generate(model=LLM_MODEL, prompt=CONCLUSION_PROMPT.format(context=context, reflection=reflection, background=background))
            response = response['response']
            return response
        except Exception as e:
            if retry_count >= MAX_RETRY: 
                print("Encountered error: ", e, "Max retries reached")
                return "" 
            print("Encountered error: ", e, "Retrying")
            return retry(retry_count + 1)   
    return retry(count)

st = datetime.datetime.now()
conclusion_response = generate_conclusion(response, background=background_response, reflection=reflection_response)
et = datetime.datetime.now()
conclusion_path = os.path.join(os.getcwd(), "output","conclusion.txt")
with open(conclusion_path, "w") as file :
            file.write(conclusion_response)
df.loc[len(df)] = {"id": 8  ,"prompt" : CONCLUSION_PROMPT, "model" : LLM_MODEL, "task": "speaker background" , "response": conclusion_response , "time-taken": et-st, "start-time": st, "end-time": et}


df.to_excel(f"{FILENAME}.xlsx", index=False)