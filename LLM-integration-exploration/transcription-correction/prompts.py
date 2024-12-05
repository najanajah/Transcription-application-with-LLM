diarization_prompt = '''
You are a helpful speech-to-text medical transcription assistant correcting a transcript containing {topics} including other general medical concepts and topics. Your current task is
to diarize a conversation with no speaker labels. You will use your advanced
understanding of medical terminology, dialogue structure, and conversational
context to diarize the text accurately. Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone,
sentiment, and vocabulary.
2. Sentence Splitting: Actively split sentences into separate statements when there’s
a change in speaker. Look for cues like pauses, speech direction changes, thought
conclusions, questions, and answers.
3. Reasoning: Consider whether the language is inquistive (suggesting an interviewer) or expresses personal experiences/emotions (suggesting the interviewee).
4. Look-Around Strategy: Analyze the five sentences before and after the current
one to understand the conversation flow. Questions may be followed by answers,
and concerns by reassurance.
5. Label with Justification: Assign a label ’INTERVIEWER’ or ’INTERVIEWEE’ to each sentence,
providing a brief justification based on your analysis. Ensure each justification
pertains to only one person.
6. Consistent Attribution: Maintain a thorough approach throughout the transcript,
treating each sentence with equal attention to detail.
7. Extremely Granular Attribution: Break down the conversation into the smallest
parts (question, answer, utterance) for clarity. Each clause should be precisely
attributed to either the ’INTERVIEWER’ or the ’INTERVIEWEE’, with no overlap in speaker identity.
8. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
9. Return as a list of JSON. Examples #1:
    Example #1: 
    Transcript: 
    What I asked was what was the electives?


    Expected enumerated output structure:
    {{ "Sentence": "What I asked was what was the electives?", "Justification": "The speaker is the INTERVIEWER, as they are asking a question.", "Label": "INTERVIEWER" }} 
    

Here is the transcript: 

Transcript:
{transcript}

Expected enumerated output structure:
{{ "Sentence": [reference sentence], "Justification": [justification], "Label": [label: INTERVIEWEE or INTWERVIEWER] }}
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''
diarization_prompt_list= '''
You are a helpful speech-to-text medical transcription assistant. Your current task is
to diarize a conversation with no speaker labels. You will use your advanced
understanding of medical terminology, dialogue structure, and conversational
context to diarize the text accurately. Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone,
sentiment, and vocabulary.
2. Sentence Splitting: Actively split sentences into separate statements when there’s
a change in speaker. Look for cues like pauses, speech direction changes, thought
conclusions, questions, and answers.
3. Reasoning: Consider whether the language is inquistive (suggesting an interviewer) or expresses personal experiences/emotions (suggesting the interviewee).
4. Look-Around Strategy: Analyze the five sentences before and after the current
one to understand the conversation flow. Questions may be followed by answers,
and concerns by reassurance.
5. Label with Justification: Assign a label ’INTERVIEWER’ or ’INTERVIEWEE’ to each sentence,
providing a brief justification based on your analysis. Ensure each justification
pertains to only one person.
6. Consistent Attribution: Maintain a thorough approach throughout the transcript,
treating each sentence with equal attention to detail.
7. Extremely Granular Attribution: Break down the conversation into the smallest
parts (question, answer, utterance) for clarity. Each clause should be precisely
attributed to either the ’INTERVIEWER’ or the ’INTERVIEWEE’, with no overlap in speaker identity.
8. Correction: You may make slight corrections to the text to ensure proper grammar and punctuation. Do NOT add or remove words from the existing text. Replacements are allowed. 
9. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
10. Return as a list of JSON. Examples #1:
    Example #1: 
    Transcript: 
    'What I asked was what was the electives?'
    'For me it was General Surgery'


    Expected enumerated output structure:
    [{{ "Sentence": "What I asked was what was the electives?", "Justification": "The speaker is the INTERVIEWER, as they are asking a question.", "Label": "INTERVIEWER" }} , 
    {{"Sentence": "For me it was General Surgery", "Justification": "The speaker is the INTERVIEWEE, as they are providing personal information.", "Label": "INTERVIEWEE"}}]

Here is the transcript: 

Transcript:
{transcript}

Expected enumerated output structure:
[{{ "Sentence": [reference sentence], "Justification": [justification], "Label": [label: INTERVIEWEE or INTWERVIEWER] }}]
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''


punctuation_prompt = '''You are a helpful speech-to-text medical transcription assistant. Your current task is to correct punctuation in a medical transcription. 
You will use your advanced understanding of medical terminology, dialogue structure, and conversational context to punctuate the text accurately. Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone, sentiment, and vocabulary.
2. Punctuation Correction: Add or remove punctuation marks where necessary to ensure the text is grammatically correct.
3. Reasoning: Consider the context of the conversation to determine the appropriate punctuation marks. Look for cues like pauses, speech direction changes, thought conclusions, questions, and answers.
4. Look-Around Strategy: Analyze the five sentences before and after the current one to understand the conversation flow. Questions may be followed by answers, and concerns by reassurance.
5. Consistent Punctuation: Maintain a consistent approach throughout the transcript, ensuring that punctuation marks are used correctly and consistently.
6. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
7. Return as a list of JSON. Examples #1:
Example #1:
Transcript:
What I asked was what was the electives


Expected output:
[{{"Punctuated_Sentence": "What I asked was what was the electives?", "Justification": "The sentence is a question, so it should end with a question mark."}}]



Here is the transcript:
{transcript}
Expected output:
[{{"Punctuated_Sentence": [reference sentence], "Justification": [justification]}}]
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.

'''

correction_prompt_few_shot_no_vocab = '''You are a helpful speech-to-text medical transcription assistant correcting audio by Singaporean speakers. 
Your current task is to correct any errors in a medical transcription with a specific focus on proper-nouns that may have been transcribed in correctly.
You will use your advanced understanding of medical terminology, dialogue structure, and conversational context to correct the text accurately. 

Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone, sentiment, and vocabulary. Take one speaker's dialogue at a time and make sure every sentence is included in the final output.
2. Error Correction: Identify and correct any errors in the text, focusing on proper nouns and medical terminology.
3. Reasoning: Consider the context of the conversation to determine the appropriate corrections. Look for cues like changes in meaning to correct words that may have been misheard or misinterpreted.
4. Look-Around Strategy: Analyze the five sentences before and after the current one to understand the conversation flow. Questions may be followed by answers, and concerns by reassurance. Institutions may be talked about on multiple occasions.
5. Consistent Correction: Maintain a consistent approach throughout the transcript, ensuring that errors are corrected accurately and consistently.Do not over-correct for example do not expand abbreviations unnecessarily.
6. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
7. Return as a list of JSON. Examples #1-2:
Example #1:
Transcript:
INTERVIEWEE: Uh, I think maybe it la, yeah. 
Expected output:
[{{"Corrected Sentence": "INTERVIEWEE: Uh, I think maybe 8, yeah. ", "Justification": "it is corrected to 8 based on the surrounding context and by similarity of the words pronounciation"}}]


Example #2:
Transcript:
INTERVIEWER: and then what did you do?
INTERVIEWEE: Then I did NSTCA in new region.

Expected output:
[{{"Corrected Sentence": "INTERVIEWER: and then what did you do?", "Justification": "no corrections needed."}} , 
{{"Corrected Sentence": "INTERVIEWEE: Then I did Anaesthesia in NUH", "Justification": "From the vocabulary, NSTCA is corrected to Anaesthesia and new region is corrected to NUH since they could be mistaken for each other."}}]


Here is the transcript:
{transcript}

Expected output:
[{{"Corrected Sentence": "corrected sentence", "Justification": "justification"}}]
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''

correction_prompt_few_shot = '''You are a helpful speech-to-text medical transcription assistant correcting audio by Singaporean speakers. 
Your current task is to correct any errors in a medical transcription with a specific focus on proper-nouns that may have been transcribed in correctly.
You will use your advanced understanding of medical terminology, dialogue structure, and conversational context to correct the text accurately. 
You may use the terms under Vocabulary for reference. 
Vocabulary: 
{vocabulary}

Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone, sentiment, and vocabulary. Take one speaker's dialogue at a time and make sure every sentence is included in the final output.
2. Error Correction: Identify and correct any errors in the text, focusing on proper nouns and medical terminology.
3. Reasoning: Consider the context of the conversation to determine the appropriate corrections. Look for cues like changes in meaning to correct words that may have been misheard or misinterpreted.
4. Look-Around Strategy: Analyze the five sentences before and after the current one to understand the conversation flow. Questions may be followed by answers, and concerns by reassurance. Institutions may be talked about on multiple occasions.
5. Consistent Correction: Maintain a consistent approach throughout the transcript, ensuring that errors are corrected accurately and consistently.Do not over-correct for example do not expand abbreviations unnecessarily.
6. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
7. Return as a list of JSON. Examples #1-2:
Example #1:
Transcript:
INTERVIEWEE: Uh, I think maybe it la, yeah. 
Expected output:
[{{"Corrected Sentence": "INTERVIEWEE: Uh, I think maybe 8, yeah. ", "Justification": "it is corrected to 8 based on the surrounding context and by similarity of the words pronounciation"}}]


Example #2:
Transcript:
INTERVIEWER: and then what did you do?
INTERVIEWEE: Then I did NSTCA in new region.

Expected output:
[{{"Corrected Sentence": "INTERVIEWER: and then what did you do?", "Justification": "no corrections needed."}} , 
{{"Corrected Sentence": "INTERVIEWEE: Then I did Anaesthesia in NUH", "Justification": "From the vocabulary, NSTCA is corrected to Anaesthesia and new region is corrected to NUH since they could be mistaken for each other."}}]


Here is the transcript:
{transcript}

Expected output:
[{{"Corrected Sentence": "corrected sentence", "Justification": "justification"}}]
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''


correction_prompt_zero = '''You are a helpful speech-to-text medical transcription assistant. 
Your current task is to correct any errors in a medical transcription with a specific focus on proper-nouns that may have been transcribed in correctly.
You will use your advanced understanding of medical terminology, dialogue structure, and conversational context to correct the text accurately. 
You may use the terms under Vocabulary for reference. 
{vocabulary}
Here’s how to approach the task step by step:
1. Contextual Reading: Read each sentence thoroughly, absorbing its content, tone, sentiment, and vocabulary. Take one speaker's dialogue at a time and make sure every sentence is included in the final output.
2. Error Correction: Identify and correct any errors in the text, focusing on proper nouns and medical terminology.
3. Reasoning: Consider the context of the conversation to determine the appropriate corrections. Look for cues like changes in meaning to correct words that may have been misheard or misinterpreted.
4. Look-Around Strategy: Analyze the five sentences before and after the current one to understand the conversation flow. Questions may be followed by answers, and concerns by reassurance. Institutions may be talked about on multiple occasions.
5. Consistent Correction: Maintain a consistent approach throughout the transcript, ensuring that errors are corrected accurately and consistently.
6. Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
7. Return as a list of JSON. 

{transcript}
Expected output:
[{{"Corrected Sentence": [corrected sentence], "Justification": [justification]}}]
Do not answer with anything other than the list of JSON. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''

institutions = { "NUHS" : "National University Health System", "NHG": "National Healthcare Group", "TTSH": "Tan Tock Seng Hospital", "SGH": "Singapore General Hospital"}
positions = {'MO' : "Medical Officer" , "Registrar" : "Registrar", "Consultant" : "Consultant"}
terms = ["endocrine" , "anesthesia", "clinicians" , "MO rostering" , "NS", "National Service", "KPMT", "Lotte Posting"]

i = [f"{key}-{value}" for key, value in institutions.items()]
p = [f"{key}-{value}" for key, value in positions.items()]
k = "Keywords\n" + " ".join(p)
i = "Institutions\n" + " ".join(i)
t = "Terms\n" + " ".join(terms)

KEYWORD_WHISPER_PROMPT =  i + " \n" + k + "\n" + t


json_completion_prompt = '''You are a helpful python syntax corrector. Your current task is to correct any errors in a medical transcription with a specific focus on list of json objects.
You will use your advanced understanding of python syntax to correct the text accurately.
Here’s how to approach the task step by step:
1. Understand the data type: from the input check the intended data type i.e. List of JSON objects
2. Determine the error: Find the error in the input that is causing error when being parsed using json.loads() 
3. Correct the error: Correct the error in the input so that it can be parsed using json.loads(). 

Here is the input:
{input}

Expected output:
Do not answer with anything other than the corrected input. Do not answer with "Here is the answer" or "The answer is" or anything similar.
'''

vocab_audio_1 = ["Lotte Posting" , "emergency", "ultrasound", "GS", "general surgery", "Emergency room" , "clinics" , "OT", "EM" ,"Physicians", "chest tube" , "surgeons" ]
vocab_audio_2 = ["endocrine", "anesthesia", "clinicians" , "MO rostering" , "Diabetes" ,"NS - National Service", "National Service", "KPMT", "SAF", "KTPH", 
"LKC",
"Duke",
"Yong Loo Lin",
"HSTP", 
"MOH",
"MO – Medical Officer ",
"HO – House Officer",
"RHS – Regional Health System ",
"HOD – Head of Department ",
"OT – Over Time ",
"SAF – Singapore Armed Forces ",
"M&M - Morbidity and Mortality",
"JC – Junior College",
"Hypoglycaemia", 
"Singapore Healthcare Improvement Project ", 
"insulin",
"Army"
]
keywords_audio1 = "  ".join(vocab_audio_1)
keywords_audio2 = "  ".join(vocab_audio_2)

all_keywords = " ".join(vocab_audio_1 + vocab_audio_2)


zero_shot_correction = '''
You are a helpful speech-to-text transcription assistant. Your task is to review and
correct transcription errors, focusing on accuracy and context. Consider diverse
speaker accents. Identify the role of each speaker, either an INTERVIEWE or INTERVIEWW, based
on tone, sentiment, and diction. Label them accordingly in the transcript. Ensure
the enhanced text mirrors the original spoken content without adding new material.
Your goal is to create a transcript that is accurate and contextually consistent,
which will improve semantic clarity and reduce word error rates.
Do not answer with anything other than the transcript. Do not answer with "Here is the answer" or "The answer is" or anything similar.
Return the corrected transcript only. 
You can use the vocabulary for reference when making corrections. 
{vocabulary}

Ensure the stucture remains the same do not make any changes i.e. 
INTERVIEWEE: spoken_sentence

{transcript}
'''


initial_prompt = '''
So if I was asking you, you know, like(inaudible) how many
out of 10, would you do this posting again? I mean, what,
what kind of rating would you give (inaudible) this post-
ing? (inaudible) I think maybe 8, yeah. Okay. Why, why 8?
(inaudible), 8 because(inaudible) it was mostly like, (laugh-
ing), it was a good experience and ,Uh, - I think I learned
quite a lot. (inaudible), yeah. And can maybe like, (inaudi-
ble), yeah, just, I guess maybe because of the fact that it
was, (inaudible), mainly, it is almost like two different post-
ings. like, GS, and emergency. So, yeah, I think that’s like
all of these points. Yeah. Okay. So the, the being 2, like dif-
ferent postings, that’s a good thing in your opinion, right?
(inaudible), was that, yeah, is that a good thing or a bad
thing in your opinion? (inaudible), I think, (laughs), it was,
I mean, there’s nothing bad, like, maybe, I think we were
being better. But I think it was, like, a few more opportuni-
ties to see some sort of like, (inaudible), interaction. Okay.
Yeah. But otherwise I mean, I mean, I think it’s, it’s okay.
Okay. Okay. Thanks. Thanks. I’ve actually ran to the, the
end of my questions. Do you have anything, um, else that
you would like to highlight or to tell me about, Umm... your
experiences during the posting when you were an MO? (in-
audible), no, nothing else in particular. I think it was quite
a good experience. Okay. Okay. Great. Thank you very
much for your time then.
(laughs) Alright, so now—now we’ll start, okay? Ahh just
a couple of (chair dragging) questions ah. . . How long have
you been working in Tan Tock Seng? I guess that’s—s –
so if you talk about am I being employed in Tan Tock Seng
is just— Umm I guess from the time you were an MO or
the—you did your— S—So I did my HO— —residency
here? —here. Ahh, okay. So, 2004, I was here. . . ahh. . . for
a while, then I did anaesthesia in NUH. Ahh. So in two
thousand—So I did two postings of my House Officer train-
ing here, then I went to NUH do anaesthesia, then I went to
do army. Ahh, okay. Then I did two years of pathology in
NUH. Ahhh, okay. Oka—(laughs a bit) So it’s a bit long,
then I decided that I would come back to Tan Tock Seng. . .
Mm, and did your. . . To do internal medicine. So then
I did most of my internal medicine training here,— Mm.
I did In fact all my internal medicine training here, plus
uhhh then my endocrine training. So, my endocrine train-
ing largely here except six months in KTPH. Okay. So I’ve
been. . . working here and there. . . mmm. . . maybe about. . . 8
years, around there, — Mm. —around there. So I’ve grad-
uated about 12 years.
Mm. Two years was in army, two years was in pathology,
and half a year was anaesthesia—so around seven plus eight
years la. So you’ve been in the same endocrine department
for. . . Uh, since 2012. . . September, something like that, so
about. . . .eh. . . 4 years plus la. Ahh I see, okay. Except for a
six month period when I went KTPH (mumbling). So, you
very probably identify yourself pretty much as a Tan Tock
Seng person la. Yeah yes.
'''