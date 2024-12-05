import sqlite3
import os
import uuid 
import datetime
import json  
from FeatureExtractor.FeatureExtractor import generate_keywords, generate_background, generate_summary, generate_reflection, generate_conclusion


'''
    This module contains the database model for the application.
    The module contains the following functions:
        add_new_transcription_to_db_return_features(filename: str, transcription: str, audio_file_name: str) -> Tuple[int, str, str, str, str, str]
        update_features(id: int, feature: str, new_value:str) -> int
        update_report(id: int, feature: str, new_value:str) -> int
        get_transcription(id: int) -> List[str]
        get_audio_file_name(id: int) -> List[str]
        get_all_id_and_filename() -> List[Tuple[int, str]]
        get_feature(id: int, feature: str) -> List[str]
        get_report(id: int, feature: str) -> List[str]
        update_transcription(id: int, new_transcription: str) -> Tuple[str, str, str, str, str]
        regenerate_report_col(id: int, feature: str) -> int
'''
with open("config.json", "r") as file : 
                DEBUG =  json.load(file).get("DEBUG", True)

PATH = os.path.join(os.getcwd(), "database.db")
def add_new_transcription_to_db_return_features(filename, transcription, audio_file_name): 
    try : 
        connection = sqlite3.connect(PATH)
        cursor = sqlite3.Cursor(connection)
        dt = datetime.datetime.now()
        result = cursor.execute("INSERT INTO transcriptions (file_name, transcription, date_created, audio_file_name) VALUES (?,?,?,?)", (filename, transcription,dt.strftime("%Y-%m-%d %H:%M:%S"), audio_file_name))
        id = result.lastrowid
        if DEBUG:
            summary = "updated summary"
            keywords = "updated keywords"
            background = "updated background"
            reflection = "updated reflection"
            conclusion = "updated conclusion"
        else:
            try:
                summary = generate_summary(transcription)
                keywords = generate_keywords(transcription)
                background = generate_background(transcription)   
                reflection = generate_reflection(transcription, summary, background)
                conclusion = generate_conclusion(summary, background, reflection)
            except Exception as e:
                print("Error during feature extraction: ", e)
                return None, None, None, None

        result = cursor.execute("INSERT INTO features (id , keywords) VALUES (?,?)", (id, str(keywords))) 
        result = cursor.execute("INSERT INTO report (id , background, summary, reflection, conclusion) VALUES (?,?,?,?,?)", (id, background, summary, reflection, conclusion)) 
        connection.commit()
        return id, keywords, background, summary, reflection, conclusion
    except Exception as e:
        print("Error during insertion: ", e)
        return None, None, None, None
    

def update_features(id: int, feature: str, new_value:str): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute(f"UPDATE features SET {feature} = ? WHERE id = ?", (new_value, id))
    connection.commit()
    return 1 

def update_report(id: int, feature: str, new_value:str):
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute(f"UPDATE report SET {feature} = ? WHERE id = ?", (new_value, id))
    connection.commit()
    return 1

def get_transcription(id: int): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute("SELECT transcription FROM transcriptions WHERE id = ?", (id,))
    return result.fetchall()

def get_audio_file_name(id: int):
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute("SELECT audio_file_name FROM transcriptions WHERE id = ?", (id,))
    return result.fetchall()

def get_all_id_and_filename(): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute('SELECT id, file_name FROM transcriptions')
    ## return a list of tuples
    return result.fetchall() 

def get_feature(id: int, feature: str): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute(f"SELECT {feature} FROM features WHERE id = ?", (id,))
    if result:
        return result.fetchall()
    else: 
        return None

def get_report(id: int, feature: str):
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute(f"SELECT {feature} FROM report WHERE id = ?", (id,))
    if result:
        return result.fetchall()
    else: 
        return None
def update_transcription(id: int, new_transcription: str): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute("UPDATE transcriptions SET transcription = ? WHERE id = ?", (new_transcription, id))
    if DEBUG:
        background = "updated background"
        summary = "updated summary"
        reflection = "updated reflection"
        conclusion = "updated conclusion"
    else:
        summary = generate_summary(new_transcription)
        keywords = generate_keywords(new_transcription)
        background = generate_background(new_transcription)
        reflection = generate_reflection(new_transcription, summary, background)
        conclusion = generate_conclusion(summary, background, reflection)
    result = cursor.execute("UPDATE features SET keywords = ? WHERE id = ?", (keywords, id))
    result = cursor.execute("UPDATE report SET background = ?, summary = ?, reflection = ?, conclusion = ? WHERE id = ?", (background, summary, reflection, conclusion, id))
    connection.commit()
    return keywords, background, summary, reflection, conclusion

def regenerate_report_col(id: int, feature: str): 
    connection = sqlite3.connect(PATH)
    cursor = sqlite3.Cursor(connection)
    result = cursor.execute("SELECT transcription FROM transcriptions WHERE id = ?", (id,))
    transcription = result.fetchall()[0][0]
    if DEBUG:
        print("here")
        update_report(id, feature, "regenerated " + feature)
    else:
        if feature == "background":
            new_background = generate_background(transcription)
            update_report(id, feature, new_background)
            new = new_background
        elif feature == "summary":
            new_summary = generate_summary(transcription)
            update_report(id, feature, new_summary)
            new = new_summary
        elif feature == "reflection":
            summary = get_report(id, "Summary")[0][0]
            background = get_report(id, "Background")[0][0]
            new_reflection = generate_reflection(transcription, summary, background)
            update_report(id, feature, new_reflection)
            new = new_reflection
        elif feature == "conclusion":
            background = get_report(id, "Background")[0][0]
            summary = get_report(id, "Summary")[0][0]
            reflection = get_report(id, "Reflection")[0][0]
            new_conclusion = generate_conclusion(summary, background, reflection)
            update_report(id, feature, new_conclusion)
            new = new_conclusion
        return new