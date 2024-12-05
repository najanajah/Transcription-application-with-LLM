import pandas as pd 
import time
import whisper
import os 
import torch

# Check if CUDA (GPU) is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
file_name = "audio.mp3"

# Define whisper models and temperatures
whisper_models = ["base.en" , "tiny.en", "small.en", "medium.en"]
temperatures = [0, 0.2, 0.4, 0.6, 0.8, 1.0] 
dir = os.getcwd()
os.makedirs(os.path.join(dir, "temperature-results"), exist_ok=True)

audio = os.path.join("data", "audio_files", file_name)
for model_name in whisper_models: 
    result_df = pd.DataFrame(columns=["Model" , "Temperature", "Result", "Transcription_Time"])
    results = []
    model = whisper.load_model(model_name, device=device)
    for temp in temperatures:
        start_time_t = time.time()
        result = model.transcribe(audio, temperature=temp)
        end_time_t = time.time()
        print(f'{model_name}====\noutput:\n{result["text"]}')
        transcribe_time = end_time_t - start_time_t
        results.append({"Model": model_name, "Result": result["text"], "Temperature": temp, "Transcription_Time": transcribe_time})
    for data in results: 
        result_df.loc[len(result_df)] = data
    file_name = f"{model_name}-audio.xlsx"
    file_path = os.path.join(dir, "temperature-results", file_name)
    result_df.to_excel(file_path)
