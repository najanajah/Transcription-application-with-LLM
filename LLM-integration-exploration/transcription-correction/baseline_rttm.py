from pyannote.audio import Pipeline
import os
import json 
import pandas as pd
from datetime import datetime

TOKEN = os.path.join(os.getcwd(),"credentials.json")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                    use_auth_token=TOKEN)

audio = "audio"
audio_input = os.path.join("audio_files", f"{audio}.wav")

st = datetime.now()
# apply the pipeline to an audio file
diarization = pipeline(audio_input, num_speakers = 2)
et = datetime.now()

df = pd.DataFrame(columns=["id", "task", "model", "time-taken", "start-time", "end-time", "audio"])
df.loc[len(df)] = [id, "diarize", "pyannote", et-st, st, et, audio]
# dump the diarization output to disk using RTTM format
os.makedirs("diarization", exist_ok=True)
with open(os.path.join("diarization",f"{audio}-pyannote.rttm"), "w") as rttm:
    diarization.write_rttm(rttm)

df.to_excel(os.path.join("diarization","time_{audio}.xlsx"), index=False)