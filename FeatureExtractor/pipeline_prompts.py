SPEAKER_BACKGROUND_PROMPT = ''' Use the provided transcripts to identify the background of the interviewee. Return the background of the speakers in a JSON format. For example:
~
"The speaker participated in a medical posting that spanned two weeks, focusing on both General Surgery (GS) and Emergency Medicine (EM). The primary focus was on enhancing their surgical knowledge and exposure to emergency medicine, specifically through the use of point-of-care ultrasound (POCUS). This was an elective experience aimed at revising existing medical knowledge and gaining hands-on skills."
~
Only provide the requested string format. Do not answer with anything other than the string. Do not answer with "Here is the background" or "The background is" or anything similar. Just provide the format response. ONLY use the information provided after TRANSCRIPTS to generate the background. 

TRANSCRIPTS: \n
{context}
'''

IDENTIFY_TOPICS_PROMPT = ''' Identify and return a combined list from the above lists containing unique heading, summary and evidence. Combine evidence from different objects if necessary. Return the topics in a JSON format.
For example: 
~
TRANSCRIPT - 1: 
\"[{ 
    ""heading"" : ""Operational Coordination"",
    ""summary"" : ""Effective management of patient diets highlights the importance of a holistic approach to patient care, requiring coordination between different disciplines such as kitchen operations and medical care."",
    ""evidence"" : ""Because...the strategy will involve multiple disciplines. Because even kitchen is involved in the diet, and you make sure the nurse can identify those with medications early..."" 
},

{
        \"heading\": \"Communication\",
        \"summary\": \"Effective communication is crucial in healthcare, enabling doctors to train and work together efficiently. The speaker highlights the importance of clear communication, sharing personal experiences of struggling with poor communication skills in the past.\",
        \"evidence\": \"I was asked, I didn't even know if I could even ask people to focus on it unless you were thinking, because I was so interested in the point where I put in there to call, call computer, you know, computers, there's no more in the phone and say, oh, you know, I'm not a participant.\"
    }]
\"

TRANSCRIPT - 2: 

\"[{ 
    ""heading"" : ""Operational Coordination"",
    ""summary"" : ""Effective management of patient diets highlights the importance of a holistic approach to patient care, requiring operational coordination skills."",
    ""evidence"" : ""A lot of it is...because...okay, so the difficulty is in identifying the problem, in identifying the strategy and because the strategy will involve multiple disciplines."" 
}]\"

OUTPUT: 
[{
    "heading": "Operational Coordination",
    "summary": "Effective management of patient diets requires a holistic approach to patient care that emphasizes the importance of cross-disciplinary coordination. This involves integrating kitchen operations, medical care, and nursing staff to ensure that dietary needs align with patient health requirements, particularly for those with medications. Strong operational coordination skills are essential to navigate the complexities of aligning multiple departments, addressing challenges, and ensuring efficient patient care outcomes.",
    "evidence": "Because... the strategy will involve multiple disciplines, including kitchen staff, to ensure patient diets are carefully managed. Even the kitchen is involved in the diet, and the process ensures that nurses can identify patients who are on medications early. A lot of it is challenging because... okay, so the difficulty is in identifying the problem and strategy, especially since it requires the cooperation of multiple disciplines."
}]
~

The below transcripts are for the same interview between 2 speakers. All the COMMON HEADINGS from all the transcripts must be included in the final response.
DO NOT USE THE EXAMPLE FOR ANSWERING. ONLY USE THE CONTEXT. Do not answer with anything other than the JSON. It MUST be a complete JSON. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format JSON response. Do not use information from the EXAMPLE only the CONTEXT.
\n 
{context}
'''

FORMAT_SUFFIX = '''DO NOT USE THE EXAMPLE FOR ANSWERING. ONLY USE THE CONTEXT. Do not answer with anything other than the JSON. It MUST be a complete JSON. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format JSON response. Do not use information from the EXAMPLE only the CONTEXT.'''

COMBINE_SUMMARY_PROMPT = '''The above summaries are for the same transcript. 
1. Use the summaries from the above to generate a combined summary. 
2. Identify all the common topics observed across each transcript.
3. Combine the evidence from different objects if necessary as a string. 
4. Regenerate the summary if necessary to include new information.
5. return as a json format. for example:

EXAMPLE RESPONSE:
~
{{'summary' : 'Practical Skills:

Point-of-Care Ultrasound (POCUS): One of the key highlights was learning ultrasound techniques, such as the FAST scan (Focused Assessment with Sonography for Trauma), an essential diagnostic tool in emergency situations.
Observation of Surgical Procedures: The speaker had opportunities to observe surgeries in the operating theatre (OT), expanding their practical understanding of surgical procedures.
Emergency Room Experience: Through shifts in the emergency department, the speaker gained insights into how acute medical cases are handled and learned more about the role of physicians in emergency care.

Transdisciplinary Practice:

Interaction Between Disciplines: The speaker observed instances where surgeons were involved in patient care after initial emergency assessment, particularly for cases requiring surgical interventions like chest tube insertion. This provided insight into how emergency and surgical disciplines can collaborate for patient care.
Limited Transdisciplinary Exposure: Although the posting included both GS and EM, the speaker noted that the experiences were mostly separated rather than fully integrated, with fewer opportunities to observe interdisciplinary collaboration compared to other postings (such as palliative care and surgery).'}}
~

Do not answer with anything other than the JSON. It MUST be a complete JSON. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format response.Do not use information from the EXAMPLE only the CONTEXT.
'''

SUMMARY_PROMPT_1 = '''{context} \n Write a summary of the above context highlighting the  skills used and evidence from the text supporting the skills.
Return in a list of json objects as given in the example below. 
~
[{{ 
    \"heading\" : \"Operational Coordination\",
    \"summary\" : \"Operational coordination skills are essential, particularly in integrating non-clinical aspects such as kitchen operations with medical care. Effective management of patient diets, for instance, highlights the importance of a holistic approach to patient care. This skill ensures that all aspects of healthcare are harmonized to support the overall well-being of patients\", 
    \"evidence\" : \"A lot of it is, uh, I think the difficulty is…because…okay, so the difficulty is in identifying the problem, in identifying the strategy and because the strategy will involve multiple disciplines.
 Mm.
 Because we also went to kitchen. Because—
 Okay.
 —even kitchen is involved in the diet,
 Yeah.
 —and you make sure the nurse can identify those with medications early, so those with…who uh need insulin before meals, we have to ask kitchen to go and pack the diet, and then what time the diet comes up from the kitchen, because it cannot set all the diet up at one time, it must be…
 Mm.
 So some wards will have the diet late, some wards will have the diet early, so sometimes that causes issues…so the—there are all these things la so that’s the reason why—
 Yes. (laughs)
 —it became a very big massive…and then the thing is that there are also constraints… \"}}]

~
Do not answer with anything other than the list of dictionaries. It MUST be a complete list. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format response.'''


SUMMARY_PROMPT_2 = '''{context} \n List important topics in the following text and write a summary with evidence from the text supporting the skills.
Return in a list of json objects as given in the example below. 
~
[{{
        \"heading\": \"Communication\",
        \"summary\": \"Effective communication is crucial in healthcare, enabling doctors to train and work together efficiently. The speaker highlights the importance of clear communication, sharing personal experiences of struggling with poor communication skills in the past.\",
        \"evidence\": \"I was asked, I didn't even know if I could even ask people to focus on it unless you were thinking, because I was so interested in the point where I put in there to call, call computer, you know, computers, there's no more in the phone and say, oh, you know, I'm not a participant.\"
    }}]
 
~
Do not answer with anything other than the list of dictionaries. It MUST be a complete list. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format response.'''


SUMMARY_PROMPT_3 = '''{context} \n "identify key points in the following texts and write a summary with evidence from the text supporting the skills.
Return in a list of json objects as given in the example below. 
~
[{{
        \"heading\": \"Teamwork\",
        \"summary\": \"The speaker emphasizes the importance of teamwork in healthcare, highlighting the need for doctors to work together seamlessly.\",
        \"evidence\": \"Because you've got to do this, things, you actually think that when you're actually the type of study thing is open...\"
    }},
    {{
        \"heading\": \"Adaptability\",
        \"summary\": \"The speaker emphasizes the importance of adaptability in healthcare, highlighting the need for doctors to be flexible and responsive to changing situations.\",
        \"evidence\": \"So some wards will have the diet late, some wards will have the diet early, so sometimes that causes issues...\"
    }}]
 

~
Do not answer with anything other than the list of dictionaries. It MUST be a complete list. Do not answer with "Here is the summary" or "The summary is" or anything similar. Just provide the format response.'''

hallucination_prompt = '''
Check if there is hallucination in the given TEXT in comparison with the CONTEXT. 
for example: 
~
CONTEXT :
 '0.00 17.90 SPEAKER_01  Okay. Great. Then I will start my record. Uhh…okay. Maybe you first…uhhh, you can start by just telling me a bit more about… No which were the electives that you chose during the latte posting, and what kind of teaching activities were you exposed to during that time?\n',

 TEXT : 
 [{{ 
    \"heading\" : \"Operational Coordination\",
    \"summary\" : \"Operational coordination skills are essential, particularly in integrating non-clinical aspects such as kitchen operations with medical care. Effective management of patient diets, for instance, highlights the importance of a holistic approach to patient care. This skill ensures that all aspects of healthcare are harmonized to support the overall well-being of patients\", 
    \"evidence\" : \"A lot of it is, uh, I think the difficulty is…because…okay, so the difficulty is in identifying the problem, in identifying the strategy and because the strategy will involve multiple disciplines.
 Mm.
 Because we also went to kitchen. Because—
 Okay.
 —even kitchen is involved in the diet,
 Yeah.
 —and you make sure the nurse can identify those with medications early, so those with…who uh need insulin before meals, we have to ask kitchen to go and pack the diet, and then what time the diet comes up from the kitchen, because it cannot set all the diet up at one time, it must be…
 Mm.
 So some wards will have the diet late, some wards will have the diet early, so sometimes that causes issues…so the—there are all these things la so that’s the reason why—
 Yes. (laughs)
 —it became a very big massive…and then the thing is that there are also constraints… \" 
    
}}]

REASON: 
There is hallucination beacause the text is not related to the context. It mentions kitchen when it is not provided in the context.

RESPONSE: 
YES 
~
Do not answer with anything other than YES or NO. Do not answer with "Here is the answer" or "The answer is" or anything similar. Just provide YES or NO.
CONTEXT: 
{context}

TEXT: 
{text}
'''

institutions = { "NUHS" : "National University Health System", "NHG": "National Healthcare Group", "TTSH": "Tan Tock Seng Hospital", "SGH": "Singapore General Hospital"}
positions = {'MO' : "Medical Officer" , "Registrar" : "Registrar", "Consultant" : "Consultant"}
terms = ["endocrine" , "anesthesia", "clinicians" , "MO rostering" ]

i = [f"{key}-{value}" for key, value in institutions.items()]
p = [f"{key}-{value}" for key, value in positions.items()]
k = "Keywords\n" + " ".join(p)
i = "Institutions\n" + " ".join(i)
t = "Terms\n" + " ".join(terms)

KEYWORD_WHISPER_PROMPT =  i + " \n" + k + "\n" + t


JSON_PROMPT = ''' The generated content is not in a completed {format} format. Complete the {format} format and return the completed {format} format by adding the required delimiters '}}' or ']]' or any other necessary.
For example: 
INPUT: 
''
"[{{{{ 
    \\"heading\\" : \\"Interdisciplinary Collaboration\\",
    \\"summary\\" : \\"Effective communication and collaboration between different disciplines, such as medical care and kitchen operations, are essential in healthcare settings.\\",
    \\"evidence\\" : \\"Because we also went to kitchen. Because—even kitchen is involved in the diet, Yeah.\\"
}}}},{{{{
    \\"heading\\" : \\"Problem-Solving\\",
    \\"summary\\" : \\"The ability to identify problems, strategies, and constraints, as well as think critically about how to address them, is crucial.\\",
    \\"evidence\\" : \\"A lot of it is, uh, I think the difficulty is…because…okay, so the difficulty is in identifying the problem, in identifying the strategy...\\"
}}}},{{{{
    \\"heading\\" : \\"Holistic Approach\\",
    \\"summary\\" : \\"A comprehensive approach to patient care that considers multiple aspects, including nutrition and dietary needs, is necessary.\\",
    \\"evidence\\" : \\"Because we also went to kitchen. Because—even kitchen is involved in the diet...\\\\"
}}}}] ''
OUTPUT:
'' 
"[{{{{ 
    \\"heading\\" : \\"Interdisciplinary Collaboration\\",
    \\"summary\\" : \\"Effective communication and collaboration between different disciplines, such as medical care and kitchen operations, are essential in healthcare settings.\\",
    \\"evidence\\" : \\"Because we also went to kitchen. Because—even kitchen is involved in the diet, Yeah.\\"
}}}},{{{{
    \\"heading\\" : \\"Problem-Solving\\",
    \\"summary\\" : \\"The ability to identify problems, strategies, and constraints, as well as think critically about how to address them, is crucial.\\",
    \\"evidence\\" : \\"A lot of it is, uh, I think the difficulty is…because…okay, so the difficulty is in identifying the problem, in identifying the strategy...\\"
}}}},{{{{
    \\"heading\\" : \\"Holistic Approach\\",
    \\"summary\\" : \\"A comprehensive approach to patient care that considers multiple aspects, including nutrition and dietary needs, is necessary.\\",
    \\"evidence\\" : \\"Because we also went to kitchen. Because—even kitchen is involved in the diet...\\\\"
}}}}] '' 

EXPLANATION: 
The above content was missing '}}]' at the end of the content. The content was not in a completed list of JSON objects format.

Do not answer with anything other than the completed {format} format. Do not answer with "Here is the answer" or "The answer is" or anything similar. Just provide the completed {format} format.
INPUT: 
{context}
'''

REFLECTION_PROMPT = '''transcript: {transcript} \n BACKGROUND: {background}\n TOPIC SUMMARIES: {context} \n Write a reflection on the above context highlighting the key points and insights gained from the text. focus on the following points:

1. Contextual Reading: Carefully read the provided background and topic summaries, absorbing the key themes, ideas, and patterns.  
2. Bias Identification: Pay close attention to the interviewees potential personal biases, including beliefs, experiences, and assumptions, which could affect the interpretation of the data.  
3. Emerging Themes Analysis: Look for patterns, themes, and recurring concepts across the text, noting their significance to the analysis.  Highlight themes that may be interconnected. 
4. Meaning Interpretation: Move beyond literal interpretations by analyzing the deeper meanings, motivations, and emotions underlying participants' words.  
5. Reflection Structure: Use a concise third-person narrative throughout. Focus on summarizing the key insights gained without introducing phrases like 'here is' or 'this is.'  
6. Expected Output: Return the reflection as a single string. Ensure the text provides a coherent and analytical overview. 

REFLECTION \n
'''


CONCLUSION_PROMPT = '''BACKGROUND: {background}\n TOPIC SUMMARIES: {context} \n\n REFLECTION: {reflection} \n\n Write a conclusion on the above context highlighting the key points and insights gained from the text. Return as a string format.'''

SPEAKER_ID_PROMPT = '''{context} \n Identify which SPEAKER from SPEAKER_00 and SPEAKER_01 is INTERVIEWER and INTERVIEWEE in the above context return as a json file. Do not answer with anything other than the json text \n example of returned answer \n {{ "SPEAKER_01" : "INTERVIEWER", "SPEAKER_00" : "INTERVIEWEE"}} \n ANSWER \n'''
