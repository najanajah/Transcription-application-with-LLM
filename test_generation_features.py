from FeatureExtractor.FeatureExtractor import replace_speaker_id_with_label, generate_background, generate_summary, generate_reflection, generate_conclusion

'''
This script is used to test the generation features of the FeatureExtractor module on the GPU resources.
Set DEBUG = False in .\config.json to test. 
The script will test the following functions:
    replace_speaker_id_with_label()
    generate_background()
    generate_summary()
    generate_reflection()
    generate_conclusion()
'''

TRANSCRIPT = '''SPEAKER_00: Hello, how are you? 
SPEAKER_01: I am fine, thank you.
SPEAKER_00: What is your name?
SPEAKER_01: My name is John.'''    

if __name__ == "__main__":
    try: 
        funtion = "speaker_id"
        context = replace_speaker_id_with_label(TRANSCRIPT)
        print("Speaker labels replaced successfully \n\n" , context)

        function = "background"
        background = generate_background(context)
        print("Background generated successfully \n\n" , background)

        function = "summary"
        summary = generate_summary(context)
        print("Summary generated successfully \n\n" , summary)

        function = "reflection"
        reflection = generate_reflection(TRANSCRIPT, context, background)
        print("Reflection generated successfully \n\n" , reflection)

        function = "conclusion"
        conclusion = generate_conclusion(context, background, reflection)
        print("Conclusion generated successfully \n\n" , conclusion)
    except Exception as e:
        print(f"Error occured during {function} : ", e)