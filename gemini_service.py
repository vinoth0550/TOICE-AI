

# # gemini_service.py

# import os
# import json
# from dotenv import load_dotenv
# from google import genai
# from google.genai import types

# load_dotenv()

# # Create client
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# MODEL_NAME = "models/gemini-2.5-flash"

# AUDIO_MODEL = "models/gemini-2.5-flash"




# def generate_prd(text_input: str):

#     prompt = f"""
# You are a senior product strategist.

# From the below conversation generate a structured PROJECT REPORT.

# Return STRICT JSON only.

# FORMAT:
# {{
# "key_insights": [],
# "team_tasks": {{
#     "<team_name_1>": [],
#     "<team_name_2>": []
# }},
# "project_overview": "",
# "suggestions": []
# }}

# IMPORTANT RULES:

# - DO NOT create fixed teams like development_team, testing_team etc.
# - Dynamically extract team names ONLY if mentioned in the conversation.
# - If tasks are assigned to specific people, group them under a team logically inferred.
# - If no teams are mentioned, create a single group called "general_tasks".
# - Maintain order based on conversation flow.
# - Key insights → 3 to 6 short crisp bullet points.
# - Overview → 3 to 6 paragraphs (single string).
# - Suggestions → 2 to 5 strategic improvements manditaory from the ai side.

# Conversation:
# {text_input}
# """


#     response = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             temperature=0.3,
#             response_mime_type="application/json"
#         )
#     )

#     try:
#         return json.loads(response.text)
#     except Exception:
#         return {
#             "error": "Invalid JSON returned",
#             "raw_output": response.text
#         }




# ###
# def generate_task_prd(text_input: str):

#     prompt = f"""
# You are a senior project manager.

# Generate a structured TASK REPORT.

# Return STRICT JSON only.

# FORMAT:
# {{
# "to_do": {{
#    "<user_name_or_id>": []
# }},
# "task_summary": "",
# "suggestions": []
# }}

# RULES:
# - Group tasks under each mentioned person in the conversation.
# - If only one person mentioned, create one key.
# - task_summary → 2 to 8 lines.
# - suggestions → 2 to 5 improvements.
# - Keep it structured and clean.

# Conversation:
# {text_input}
# """

#     response = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             temperature=0.3,
#             response_mime_type="application/json"
#         )
#     )

#     try:
#         return json.loads(response.text)
#     except:
#         return {"error": "Invalid JSON", "raw": response.text}
# ###



# # TRANSCRIBE AUDIO


# def transcribe_audio(audio_bytes: bytes):

#     response = client.models.generate_content(
#         model=AUDIO_MODEL,
#         contents=[
#             types.Part.from_bytes(
#                 data=audio_bytes,
#                 mime_type="audio/wav"  # change if mp3 etc
#             ),
#             "Transcribe this audio clearly."
#         ],
#         config=types.GenerateContentConfig(
#             temperature=0
#         )
#     )

#     return response.text







# updated code 


# gemini_service.py

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash"

AUDIO_MODEL = "models/gemini-2.5-flash"




def generate_prd(text_input: str):

    prompt = f"""
You are a senior product strategist.

From the below conversation generate a structured PROJECT REPORT.

Return STRICT JSON only.

FORMAT:
{{
"key_insights": [],
"team_tasks": {{
    "<team_name_1>": [],
    "<team_name_2>": []
}},
"project_overview": "",
"suggestions": []
}}

IMPORTANT RULES:


- STRICT JSON only. No explanation text.
- Do NOT include markdown.
- Do NOT include extra keys.
- Do NOT include empty arrays.
- If a team has no tasks, omit that team entirely.
- If no teams exist, create one group called "general_tasks".
- project_overview must be a single paragraph string (no \\n).
- key_insights must contain meaningful content only.
- suggestions must not be empty and (no \\n) ** kind of symbols.


Conversation:
{text_input}
"""


    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    try:
        return json.loads(response.text)
    except Exception:
        return {
            "error": "Invalid JSON returned",
            "raw_output": response.text
        }




###
def generate_task_prd(text_input: str):


    prompt = f"""
You are a senior project manager.

Generate a structured TASK REPORT.

Return STRICT JSON only.

FORMAT:
{{
"to_do":[],
"task_summary": "",
"suggestions": []
}}


RULES:

- STRICT JSON only.
- Do NOT include markdown.
- Do NOT include extra keys.
- Do NOT return empty arrays.
- Omit any user key if they have no tasks.
- task_summary must be a single paragraph (no \\n, **, #, etc,..).
- suggestions must contain at least 2 improvements.

Conversation:
{text_input}
"""

###

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    try:
        return json.loads(response.text)
    except:
        return {"error": "Invalid JSON", "raw": response.text}
###



# TRANSCRIBE AUDIO


def transcribe_audio(audio_bytes: bytes):

    response = client.models.generate_content(
        model=AUDIO_MODEL,
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav"  # change if mp3 etc
            ),
            "Transcribe this audio clearly."
        ],
        config=types.GenerateContentConfig(
            temperature=0
        )
    )

    return response.text

