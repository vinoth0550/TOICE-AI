


# phase 2  16/03/2026 ofz

# gemini_service.py

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types       


###
import time 
from AI_usage_tracker import track_ai_usage
import time
###

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


    ##


    ###

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
"task_summary":"",
"suggestions": []
}}


RULES:

- STRICT JSON only.
- Do NOT include markdown.
- Do NOT include extra keys.
- Do NOT return empty arrays.
- Do NOT return null values in any feilds.
- Omit any user key if they have no tasks.
- todo will be in array data type only. 
- task_summary must be a single paragraph (no \\n, **, #, /,/etc,..).
- suggestions must contain at least 2 improvements.

Conversation:
{text_input}
"""

###

    start_time = time.time()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    latency = time.time() - start_time

    track_ai_usage(
        endpoint="task_prd",
        response=response,
        latency=latency
    )





    try:
        return json.loads(response.text)
    except:
        return {"error": "Invalid JSON", "raw": response.text}
###





# 3rd api

def generate_task_report(task_prd: dict, chats: list):

    prompt = f"""
You are a senior delivery manager.

Below is the ORIGINAL TASK PRD (source of truth):

{task_prd}

Below are ALL TASK CHAT MESSAGES (chronological):

{chats}

Based on this:

1. Compare PRD to_do with chats.
2. Identify completed tasks.
3. Identify in-progress tasks.
4. Identify newly created tasks from chats.
5. Provide 2-5 actionable suggestions.
6. provide task summary atleast 1 to 3 line based on the key highlights and upcomming tasks. don't return null.
7. if the key highlights satisfied all the to_do's from the prd just wrote a upcommings task From the prd all to-do's are satisfied. no upcomming tasks are pending. rather than returning null value.

Return STRICT JSON only:

{{
"key_highlights": [],
"upcoming_tasks": [],
"task_summary":"",
"suggestions": []

}}

RULES:

- STRICT JSON only.
- Do NOT include markdown.
- Do NOT include extra keys.
- Do NOT return empty arrays.
- Do NOT return null value in any feilds.
- Omit any user key if they have no tasks.
- task summary must be in atleats 1 to 2 line 
- task_summary must be a single paragraph (no \\n, **, #, /,/etc,..).
- suggestions must contain at least 2 improvements.
- task_summary must be 1 to 5 line paragraph summarizing task progress.
"""




    start_time = time.time()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    latency = time.time() - start_time

    track_ai_usage(
        endpoint="task_report",
        response=response,
        latency=latency
    )

    try:
        return json.loads(response.text)
    except:
        return {"error": "Invalid JSON", "raw": response.text}


# 3rd api





# TRANSCRIBE AUDIO





# def transcribe_audio(audio_bytes: bytes):

#     start_time = time.time()

#     response = client.models.generate_content(
#         model=AUDIO_MODEL,
#         contents=[
#             types.Part.from_bytes(
#                 data=audio_bytes,
#                 mime_type="audio/wav"
#             ),
#             "Transcribe this audio clearly."
#         ],
#         config=types.GenerateContentConfig(
#             temperature=0
#         )
#     )

#     latency = time.time() - start_time

#     track_ai_usage(
#         endpoint="audio_transcription",
#         response=response,
#         latency=latency
#     )

#     return response.text


## bfix

def transcribe_audio(audio_bytes: bytes):

    start_time = time.time()

    response = client.models.generate_content(
        model=AUDIO_MODEL,
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav"
            ),
            # """
            # If the audio contains silence, noise, or no understandable speech,
            # return exactly this word and nothing else:

            # EMPTY_AUDIO
            # """
            """
            Transcribe the audio exactly.

            If the audio contains:
            - silence
            - background noise
            - music
            - unclear speech
            - non-understandable audio

            Return exactly this:

            EMPTY_AUDIO

            Do NOT guess words.
            Do NOT hallucinate sentences.
            DO NOT process the if the audio contain no audioble clear coice and words.
            Only return real spoken words.
            """


        ],
        config=types.GenerateContentConfig(
            temperature=0
        )
    )

    latency = time.time() - start_time

    track_ai_usage(
        endpoint="audio_transcription",
        response=response,
        latency=latency
    )

    return response.text


## bfix