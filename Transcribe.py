import streamlit as st 
from AudioToText.AudioToText import AudioToText
from Utils.utils import make_text_readable_in_markdown
from stqdm import stqdm
import logging 
import os 

## contants 
MODEL = "base.en"
OUTPUT_PATH = os.path.join(os.getcwd(), "output")
DATAPATH = os.path.join(os.getcwd(), "file_db", "audio")

## set page config
st.set_page_config(page_title="Transcription Application", page_icon=":microphone:", layout="wide", initial_sidebar_state="expanded")
st.title("Transcription Application")

## set logging level
logging.basicConfig(level=logging.WARNING)

## caching function to load model only once 
@st.cache_resource()
def load_transcriber():
    return AudioToText(model=MODEL)

transcriber = load_transcriber()

## create dirs 
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)


## Uploading files 
try: 
    st.write("Upload your audio file for transcription and speaker diarization.")
    with st.form("my-form", clear_on_submit=True):
        audio_file_list = st.file_uploader("Upload a file", type=["wav", "mp3", "mp4"] , accept_multiple_files=True) 
        print(len(audio_file_list))
        ## replay audio file 
        if audio_file_list: 
            for i in range(0, len(audio_file_list)):
                audio_file = audio_file_list[i-1] # i-1 ?? 
                print(audio_file)
                filepath = os.path.join(DATAPATH, audio_file.name)
                with open(filepath, "wb") as f:
                    f.write(audio_file.getbuffer())
                st.audio(audio_file, format='audio/mp3')
                st.write("File uploaded successfully")
            initial_prompt = st.text_area("Provide an initial transcription of the audio including any keywords expected from the audio" , height=250)
        submit = st.form_submit_button("transcribe") 
        if submit:
            if audio_file_list:         
                for i in stqdm(range(0, len(audio_file_list))):
                    try : 
                        audio_file = audio_file_list[i]
                        filepath = os.path.join(DATAPATH, audio_file.name)
                        st.info(f"Transcription in progress for file {audio_file.name}... \n Please do not change the page while waiting.")
                        id, transcribed_content, keywords, background, summary , reflection, conclusion   = transcriber.transcribe(filepath,initial_prompt=initial_prompt, diarize=True)
                        st.success(f"File {audio_file.name} transcribed successfully. Find the downloaded file in your output folder on your local machine.")
                        markdown_content = make_text_readable_in_markdown(transcribed_content, id)
                        st.markdown(markdown_content)
                    except Exception as e:
                        st.error(f"Error during transcription: {e} \n {audio_file.name} discarded from queue")
                        continue 
except Exception as e:
    pass
    
            


    





        
    
