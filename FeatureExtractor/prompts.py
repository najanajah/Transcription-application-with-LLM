KEYWORDS_PROMPT = '''{context}
extract keywords from the above context and combine them in a JSON format. Do not answer with anything other than the json text'''

SPEAKER_ID_PROMPT = '''{context} \n Identify which SPEAKER from SPEAKER_00 and SPEAKER_01 is INTERVIEWER and INTERVIEWEE in the above context return as a json file. Do not answer with anything other than the json text \n example of returned answer \n {{ "SPEAKER_01" : "INTERVIEWER", "SPEAKER_00" : "INTERVIEWEE"}}'''

SUMMARY_PROMPT = '''{context} \n Write a summary of the above context. Do not answer with anything other than the text'''

QA_PROMPT = '''{context} \n from the above context return a list of tuples that have all the questions asked and summarized answer.  Do not answer with anything other than the list of tuples. DO NOT return any other information such as 'heres are the 5 required questions...' EXAMPLE RESPONSE [('What is the purpose of the posting?', 'The purpose of the posting is to understand how different disciplines work together.')]'''

