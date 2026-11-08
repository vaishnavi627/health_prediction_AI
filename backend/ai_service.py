import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_health_remarks(glucose,haemoglobin,cholesterol):
     prompt = f"""
    Review these blood test values for an educational health-risk
    information application.

    Glucose: {glucose}
    Haemoglobin: {haemoglobin}
    Cholesterol: {cholesterol}

    Provide:
    1. Observations about the supplied values.
    2. Possible health risks that may warrant further evaluation.
    3. A recommendation to consult a healthcare professional.

    Do not diagnose diseases.
    Do not claim certainty.
    Do not invent missing patient information.
    Mention that interpretation depends on units, reference ranges,
    fasting status and clinical context.

    Keep the response concise and easy to understand.
    """
     response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role":"system",
            "content":"You provide cautious, educational information about blood test values. You are not a doctor."
        }, {
            "role":"user",
            "content":prompt
        }],
        temperature=0.2,
        max_completion_tokens=800
    )

     if not response.choices or not response.choices[0].message.content:
         raise RuntimeError("The AI service returned no response content")

     return response.choices[0].message.content.strip()
