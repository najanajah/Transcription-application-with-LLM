hallucination_prompt = '''
You are an expert evaluator. You have been given the task of evaluating the following 2 texts based on to find HALLUCINATION.
HALLUCINATION is defined as a text that is either factually incorrect, nonsensical, or disconnected from the GROUND TRUTH.
You have to compare the 2 texts and evaluate with one is better with respect to HALLUCINATION i.e. which TEXT has LESS hallucination. Respond with TEXT 1 or TEXT 2. 
You must provide your reasoning for the evaluation as well. If they are both comparable return TIE and provide an explanation. 
FORMAT YOUR RESPONSE AS FOLLOWS: 1|Reason for answer.

GROUND TRUTH: 
{transcript}

TEXT 1:
{text1}

TEXT 2:
{text2}

Evaluation:

'''
Comp_prompt = '''
You are an expert evaluator. You have been given the task of evaluating the following 2 texts based on the given METRIC.
You have to compare the 2 texts and evaluate with one is better according to the METRIC and TASK. Respond with TEXT 1 or TEXT 2. 
You must provide your reasoning for the evaluation as well. If they are both comparable return TIE and provide an explanation. 

TASK: 
{task}

METRIC: 
COMPREHENSIVENESS: How much detail does the generated feature provide to cover all aspects of the task?

TEXT 1:
{text1}

TEXT 2:
{text2}

Evaluation:

'''


diver_prompt = '''
You are an expert evaluator. You have been given the task of evaluating the following 2 texts based on the given METRIC.
You have to compare the 2 texts and evaluate with one is better according to the METRIC and TASK. Respond with TEXT 1 or TEXT 2. 
You must provide your reasoning for the evaluation as well. If they are both comparable return TIE and provide an explanation. 

TASK: 
{task}

METRIC: 
DIVERSITY: How varied and rich is the generated feature in providing different per-
spectives on the task?

TEXT 1:
{text1}

TEXT 2:
{text2}

Evaluation:

'''

direct_prompt = '''
You are an expert evaluator. You have been given the task of evaluating the following 2 texts based on the given METRIC.
You have to compare the 2 texts and evaluate with one is better according to the METRIC and TASK. Respond with TEXT 1 or TEXT 2. 
You must provide your reasoning for the evaluation as well. If they are both comparable return TIE and provide an explanation. 

TASK: 
{task}

METRIC: 
DIRECTNESS: How specifically and clearly is the task addressed?

TEXT 1:
{text1}

TEXT 2:
{text2}

Evaluation:

'''