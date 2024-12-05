from database.model import get_feature
import json
import re
import string

DEBUG = True
DEBUG_KEYWORDS = json.loads('''{\n"Keywords": [\n"Posting",\n"Surgical",\n"Emergency",\n"Healthcare",\n"Professionals",\n"Impact",\n"Interaction",\n"Palliative Care",\n"Surgery",\n"E.D.",\n"OT",\n"Clinics"\n]\n}''')

def make_text_readable_in_markdown(context: str , file_id: int ) -> str: 

    '''returns a markdown formatted text'''
    if DEBUG: 
        keyword_map = DEBUG_KEYWORDS
    else:
        keyword_map = json.loads(get_feature(file_id, "keywords"))

    lines = context.split("\n")
    result = []
    for line in lines:
        for keyword in keyword_map["Keywords"]:
            line = re.sub(rf"\b{re.escape(keyword)}\b", f":red[{keyword}]", line, flags=re.IGNORECASE)
        line = re.sub("SPEAKER_00", " :blue[SPEAKER_00]", line, flags=re.IGNORECASE)
        line = re.sub("INTERVIEWER", " :blue[INTERVIEWER]", line, flags=re.IGNORECASE)
        line = re.sub("SPEAKER_01", ":green[SPEAKER_01]", line, flags=re.IGNORECASE)
        line = re.sub("INTERVIEWEE", ":green[INTERVIEWEE]", line, flags=re.IGNORECASE)
        result.append(line)

    return "\n\n ".join(result)

def remove_numbers(text):
    # Use regex to replace numbers with an empty string
    return re.sub(r'\d+\.\d+', '', text).strip()

def remove_bracketed_data_and_punctuation(text):
    # Remove bracketed data
    text = re.sub(r'\(.*?\)', '', text)
    # Remove all punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Strip leading/trailing whitespace
    return text.strip()

def clean_transcript_for_wer(transcript: str) -> str:
    if transcript is None:
        return ""
    transcript = remove_bracketed_data_and_punctuation(transcript)
    transcript = remove_numbers(transcript)
    return transcript