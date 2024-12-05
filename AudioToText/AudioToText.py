import whisper 
import os
from typing import Optional, Any
from pyannote.audio import Pipeline
import json 
import subprocess
import torch
# import Logging 
from AudioToText.utils import to_wav, merge_sentence, write_to_txt_diarize, write_to_txt, clean
from pyannote.core import Segment, Annotation, Timeline
from FeatureExtractor.FeatureExtractor import replace_speaker_id_with_label
from database.model import add_new_transcription_to_db_return_features
from AudioToText.prompt import initial_prompt
import re 

'''
    AudioToText class is used to convert audio file to text.
    The class contains the following classes:
        AudioToText()
        DiarizePyannote()
'''
class AudioToText() :  
    '''Used to convert audio file to text'''
    model : str = "base.en"  
    '''whisper model type used for transcription'''
    audio_file_path : Optional[str] = None
    '''path to audio file for transcription'''
    audio_wav_path : Optional[str] = None
    '''file to .wav file for diarization'''
    audio_file : Optional[Any]  = None 
    '''audio file for transcription'''
    file_size : Optional[float] = None
    '''size of audio file'''
    model_dir : Optional[str] = None 
    '''directory to save the transcription and diarization models'''
    diarize : bool = True 
    '''flag used for diarization of audio'''
    allowed_extensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
    '''extensions that are acceptable by Whisper model'''
    output_file : Optional[str] = None 
    '''name to save the output as .txt file'''
    output_path : Optional[str] = None  
    '''path to save the output as .txt file'''
    whisper_model : Optional[Any] = None
    '''Whisper model object'''
    diarize_model : Optional[Any] = None
    '''Diarize model object'''
    device : str = "cpu"
    '''device to run the model'''
    audio_db_path = os.path.join(os.getcwd(), "file_db", "audio")
    '''path to the audio database'''
    transcription_db_path = os.path.join(os.getcwd(), "file_db", "transcription")
    '''path to the transcription database'''

    def __init__(self, model: str = None, model_dir: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
        # validate model 
        self.model = model  or "base.en"
        if self.model not in self.whisper_models:
            raise ValueError(f'model must belong to the following list {self.whisper_models}')

        # load model
        self.whisper_model , self.diarize_model = self._load_model_(model_name=self.model , diarize=self.diarize, device=self.device)
        return
    
    @property
    def whisper_models(self) : 
        return whisper.available_models()

 
    def _validate_file(self, path: str): 
        # check if file exists 
        if not os.path.exists(path): 
            raise FileNotFoundError(f"{path} not found")
        # check if the file is of the correct extension
        _, extension = os.path.splitext(path)
        if extension not in self.allowed_extensions : 
            raise ValueError("file {path} is of incorrect type. Must be {self.allowed_extensions}")        
        return 
    
    def _load_model_(self, model_name: str , diarize: bool, device: str):
        print(f"loading whisper model {model_name}...")
        try: 
            whisper_model = whisper.load_model(model_name, device=device)
            DiarizePyannote.load_model()
            return whisper_model, DiarizePyannote
        except Exception as e:
            print(f"Error during loading of transcription models: {e}")
            return None, None
        
        
        
    def transcribe(self, file_path: str=None, initial_prompt: str =None, diarize: bool = True):
        '''Transcribe the audio file'''
        self._validate_file(file_path)
        self.audio_file_path = file_path
        self.diarize = diarize
        self.audio_wav_path = to_wav(self.audio_file_path) 

        # get ouput path to save 
        _ , file = os.path.split(self.audio_file_path)
        self.output_file =  f"{os.path.splitext(file)[0]}-transcribed" + ".txt"
        self.output_path = os.path.join(os.getcwd(), "output", self.output_file)


        
            
        print("transcription in progress")
        whisper_result = self.whisper_model.transcribe(self.audio_file_path , initial_prompt=initial_prompt)
        print("whisper transcription completed")
        if self.diarize  :
            diarize_result = self.diarize_model.diarize(self.audio_wav_path, whisper_result)
            print("="*100)
            print("speaker id replacement")
            # diarize_result = replace_speaker_id_with_label(diarize_result)
            print("="*100)
            print(f"Result : {diarize_result}")
            print ("saving to file...")
            self.output_path = write_to_txt_diarize(diarize_result, self.output_path, self.output_file)
        else : 
            write_to_txt(whisper_result, self.output_path)

        # save audio file to audio database
        filename , extension = os.path.splitext(file)
        match = re.search(r'(\d{8})-(\d{6})', self.output_path)
        tm = match.group()
        filename_db = f"{filename}-{tm}"
        audio_db_file_path = os.path.join(self.audio_db_path, f"{filename_db}{extension}")
        # print("DEBUG AUDIO DB FILE PATH" , audio_db_file_path)
        # print("DEBUG AUDIO FILE PATH" , self.audio_file_path)
        # subprocess.run(["cp", self.audio_file_path, self.audio_db_path])
        os.rename(self.audio_file_path, audio_db_file_path)


        # removing the audio file from the local directory
        clean(self.audio_file_path)
        print("successfully transcribed")

        ## create file object to return 
        with open(self.output_path, "r") as file :
            content = file.read()
            ## writing the content to the database
            id , keywords, background, summary, reflection, conclusion  = add_new_transcription_to_db_return_features(filename=os.path.basename(self.output_path), transcription=content, audio_file_name=f"{filename_db}{extension}")
            return id, content, keywords, background, summary, reflection, conclusion        

class DiarizePyannote(): 
    '''Diarization using Pyannote 3.1'''
    key_path = os.path.join(os.getcwd(),"credentials.json")
    '''path to the config.json for Huggingface key'''
    pipeline : Any
    '''Pyannote pipeline object'''
    device : str = "cpu"
    '''device to run the model'''

    @classmethod
    def load_model(cls): 
        try : 
            with open(cls.key_path, "r") as file : 
                cls.key =  json.load(file).get("HUGGINGFACE_TOKEN")
            print("loading Pyannote pipeline...")
            cls.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=cls.key)
            cls.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if cls.device == "cuda":
                cls.pipeline = cls.pipeline.to(cls.device)  
            print("Pyannote pipeline loaded successfully.")
        except Exception as e: 
            print(f"Error during loading of Pyannote : {e}")


    @classmethod
    def diarize(cls, path: str, whisper_result):  
        print("diarization in progress...")
        diarization_result = cls.pipeline(path, num_speakers=2)
        print("diarization completed")
        processed = cls.diarize_result(whisper_result, diarization_result)
        return processed
    
    @classmethod 
    def diarize_result(cls, whisper_result, diarization_result): 
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
    
if __name__ =="__main__" : 
    pass