
from pypdf import PdfReader

def parse_resume(file_path):
    try :
        reader=PdfReader(file_path)
        text=""
        for page in reader.pages:
            text+=page.extract_text()
        print(text)
        return text
    except Exception as e:
        print(e)

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_interview_questions(resume_text):
    system_prompt = """
    You are an expert technical interviewer. 
    I will provide you with a candidate's resume. 
    Your task is to generate 5 technical interview questions based specifically on the skills and projects mentioned in the resume.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Here is the candidate's resume:\n\n{resume_text}",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content



def main():
    resume_path = "path/to/your/resume.pdf" 
    resume_content = parse_resume(resume_path)
    if resume_content:
        print("Resume parsed successfully!")
        

        print("Generating questions...")
        questions = generate_interview_questions(resume_content)
        
        print("\nGenerated Questions:\n")
        print(questions)
    else:
        print("Failed to parse resume.")
if __name__ == "__main__":
    main()