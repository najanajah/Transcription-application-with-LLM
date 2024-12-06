
# Transcription Application With LLM Intergration 

**Description**  

This project is created as a part of Final Year Project at NTU to create an intuitive transcription software utilizing LLMs for information extraction. Exploration of transcript improvement and optimisation is further explored in the `.\LLM-integration-exploration` directory. Please reference the `README.md` in the respective repository. 

---

## Table of Contents

- [Transcription Application With LLM Intergration](#transcription-application-with-llm-intergration)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contact](#contact)



---

## Features

The software implements 3 main functionalities: 
- Transcribe 
- Browse 
- Edit 

---

## Installation

Step-by-step instructions to set up the project locally:

1. Clone the repository:  
   `git clone https://github.com/najanajah/Transcription-application-with-LLM.git`
2. Navigate to the project directory:  
   `cd Transcription-application-with-LLM`
3. Install dependencies (compatible with `python 3.11.4`):  
   `pip install -r requirements.txt` 
4. Additional setup instructions.
    - Please ensure [Ollama](https://ollama.com/download) is setup up and the server is running on the device. Ensure you have pulled the `llama3:instruct` model. 
    - [Streamlit](https://streamlit.io/) may have to be installed separately to run the program. 
    - Ensure [`SQLite`](https://www.sqlite.org/download.html) is also successfully installed.  
5. Create the database by running `python database\create_db.py`
6. Create a credentials.json file and add the Huggingface token in the following format.
   ` 
   { 
    "HUGGINGFACE_TOKEN" : token_here
    }
   `
   
---

## Usage

Instructions on how to run and use the project:
- For disabling debug mode (No LLM generation) change the value in config.json from true to false. 
- Command to start the project:  
  `streamlit run Transcribe.py`

---


## Contact
- Email: najah001@e.ntu.edu.sg  
