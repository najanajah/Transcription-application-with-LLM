'''
This file contains descriptions of the task used in the LLM evaluator.
'''
SPEAKER_BACKGROUND_PROMPT = ''' Use the provided transcripts to identify the background of the interviewee. Return the background of the speakers in a JSON format. For example:
~
"The speaker participated in a medical posting that spanned two weeks, focusing on both General Surgery (GS) and Emergency Medicine (EM). The primary focus was on enhancing their surgical knowledge and exposure to emergency medicine, specifically through the use of point-of-care ultrasound (POCUS). This was an elective experience aimed at revising existing medical knowledge and gaining hands-on skills."
~
Only provide the requested string format. Do not answer with anything other than the string. Do not answer with "Here is the background" or "The background is" or anything similar. Just provide the format response. ONLY use the information provided after TRANSCRIPTS to generate the background. 
'''


SUMMARY_PROMPT_1 = '''\n Write a summary highlighting the  skills used and evidence from the text supporting the skills.
Return in a list of json objects.
'''

REFLECTION_PROMPT = ''' Write a reflection highlighting the key points and insights gained from the text. focus on the following points:

1. Contextual Reading: Carefully read the provided background and topic summaries, absorbing the key themes, ideas, and patterns.  
2. Bias Identification: Pay close attention to the interviewees potential personal biases, including beliefs, experiences, and assumptions, which could affect the interpretation of the data.  
3. Emerging Themes Analysis: Look for patterns, themes, and recurring concepts across the text, noting their significance to the analysis.  Highlight themes that may be interconnected. 
4. Meaning Interpretation: Move beyond literal interpretations by analyzing the deeper meanings, motivations, and emotions underlying participants' words.  
5. Reflection Structure: Use a concise third-person narrative throughout. Focus on summarizing the key insights gained without introducing phrases like 'here is' or 'this is.'  
6. Expected Output: Return the reflection as a single string. Ensure the text provides a coherent and analytical overview. 

REFLECTION \n
'''

CONCLUSION_PROMPT = '''Write a conclusion on the above context highlighting the key points and insights gained from the text. Return as a string format.'''

