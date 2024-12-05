import streamlit as st
import pandas as pd 
from database.model import get_all_id_and_filename, get_transcription, update_transcription, get_audio_file_name, get_report, update_features, update_report, get_feature, regenerate_report_col
from Utils.utils import make_text_readable_in_markdown
from docx import Document
import PyPDF2
import os 
from evaluate import load
from Utils.utils import clean_transcript_for_wer

'''
Streamlit page for Edit transcriptions

This page allows the user to edit the transcriptions, background, summary, reflection and conclusion of the transcriptions.

'''

st.set_page_config(page_title="Transcription Application", page_icon=":microphone:", layout="wide", initial_sidebar_state="expanded")
st.title("Edit transcriptions")


ALL_TRANSCRIPTIONS_TUPLE = get_all_id_and_filename()
ALL_TRANSCRIPTIONS_LIST = [f"{pair[0]}: {pair[1]}" for pair in ALL_TRANSCRIPTIONS_TUPLE]

option = st.selectbox("Select a transcription to view", ALL_TRANSCRIPTIONS_LIST)
regen_text = ":blue[Regenerate the background using LLMs using the button below or manually edit the text in the text area]"

if option:
    st.markdown(f"### Selected transcription: {option}")
    id = int(option.split(":")[0])
    transcription = get_transcription(id)[0][0]
    try :
        audio_file_name = get_audio_file_name(id)[0][0]
        audio_path = os.path.join(os.getcwd(), "file_db", "audio", audio_file_name)    
        st.audio(audio_path, format='audio/mp3')
    except Exception as e:
        st.write(":red[No audio file found]")
    
    ENTRIES = ["Transcription", "Background","Summary",  "Reflection", "Conclusion"]
    # option_2 = st.selectbox("Select entry to edit",ENTRIES )
    option_2 = st.radio("", ENTRIES, horizontal=True)
    if option_2 == "Transcription":
        st.markdown (":blue[Edit the transcription in the left column and upload a file to compare the transcription in the right column.]")
        st.markdown(":blue[Updating the transcript will **regenerate** the features and report.]")
        left_column, right_column = st.columns(2)
        markdown_transcription = make_text_readable_in_markdown(transcription, id)
        with left_column:
            edited_transcription = st.text_area("Edit Transcription" , value=transcription, height=700)
            

        with right_column:
            uploaded_transcription = None
            st.write("Reference Transcription:")
            with st.form("my-form", clear_on_submit=True):
                file = st.file_uploader("Upload a file", type=["docx", "txt", "pdf"] , accept_multiple_files=False) 
                submit = st.form_submit_button("upload") 
                if submit:
                    if file is not None:
                        if file.type == "application/pdf":
                            pdf_reader = PyPDF2.PdfReader(file)
                            pdf_text = []

                            for page in pdf_reader.pages:
                                pdf_text.append(page.extract_text())
                            uploaded_transcription = "\n\n".join(pdf_text)
                        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                            doc = Document(file)
                            uploaded_transcription = "\n\n".join([para.text for para in doc.paragraphs])
                        elif file.type == "text/plain":
                            uploaded_transcription = file.read().decode("utf-8")
                            uploaded_transcription = uploaded_transcription.replace("\n", "\n\n")
                        
                    st.write(uploaded_transcription)
                else: 
                    st.write("Upload a file to compare transcription")
            # try: 
            
                
            # except Exception as e:
            #     st.write("No file uploaded yet")
        
        update = st.button("Update Transcription") 
        if update: 
            keywords, background, summary, reflection, conclusion = update_transcription(id,edited_transcription )
            print(uploaded_transcription)
            if uploaded_transcription is not None: 
                wer_metric = load("wer")
                wer = wer_metric.compute(references=[clean_transcript_for_wer(uploaded_transcription)], predictions=[clean_transcript_for_wer(edited_transcription)])
                if wer < 0.1: colour = "green"
                elif wer < 0.3: colour = "orange"
                else : colour = "red"
                st.markdown(f"### Word Error Rate: <span style='color:{colour}'>{wer}</span>", unsafe_allow_html=True)
            st.success("Transcription updated successfully and new features and report generated")
    elif option_2=="Background": 
            st.write(regen_text)
            if st.button("Regenerate Background"): 
                 new_feature = regenerate_report_col(id, "Background")
                 st.success("Background regenerated successfully!")
            left_column, right_column = st.columns(2)
            markdown_transcription = make_text_readable_in_markdown(transcription, id)
            with right_column:
                st.markdown("### Transcription")
                st.write(markdown_transcription)
            
            with left_column: 
                background = get_report(id, "Background")[0][0]
                edited_background = st.text_area("Edit Background", value=background, height=300)
                update = st.button("Update Background")
                if update: 
                    update_report(id, "Background", edited_background)
                    st.success("Background updated successfully")
    elif option_2=="Summary":
            st.write(regen_text)
            if st.button("Regenerate Summary"): 
                 new_feature = regenerate_report_col(id, "Summary")
                 st.success("Summary regenerated successfully!")
            left_column, right_column = st.columns(2)
            markdown_transcription = make_text_readable_in_markdown(transcription, id)
            with right_column:
                st.markdown("### Transcription")
                st.write(markdown_transcription)
            
            with left_column:
                summary = get_report(id, "Summary")[0][0]
                edited_summary = st.text_area("Edit Summary", value=summary, height=300)
                update = st.button("Update Summary")
                if update: 
                    update_report(id, "Summary", edited_summary)
                    st.success("Summary updated successfully")

    elif option_2=="Reflection":
            st.write(regen_text)
            if st.button("Regenerate Reflection"): 
                 new_feature = regenerate_report_col(id, "Reflection")
                 st.success("Reflection regenerated successfully!")
            left_column, right_column = st.columns(2)
            markdown_transcription = make_text_readable_in_markdown(transcription, id)
            with right_column:
                st.markdown("### Transcription")
                st.write(markdown_transcription)
            with left_column:
                reflection = get_report(id, "Reflection")[0][0]
                edited_reflection = st.text_area("Edit Reflection", value=reflection, height=300)
                update = st.button("Update Reflection")
                if update: 
                    update_report(id, "Reflection", edited_reflection)
                    st.success("Reflection updated successfully")
    elif option_2=="Conclusion":
            st.write(regen_text)
            if st.button("Regenerate Conclusion"): 
                 new_feature = regenerate_report_col(id, "Conclusion")
                 st.success("Conclusion regenerated successfully!")
            left_column, right_column = st.columns(2)
            markdown_transcription = make_text_readable_in_markdown(transcription, id)
            with right_column:
                st.markdown("### Transcription")
                st.write(markdown_transcription)

            with left_column:
                conclusion = get_report(id, "Conclusion")[0][0]
                edited_conclusion = st.text_area("Edit Conclusion", value=conclusion, height=300)
                update = st.button("Update Conclusion")
                if update: 
                    update_report(id, "Conclusion", edited_conclusion)
                    st.success("Conclusion updated successfully")
                

                
