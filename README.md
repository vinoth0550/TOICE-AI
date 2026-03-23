
## TOICE-AI(PHASE-2) USER MANUAL AND ERROR LOGS OF TASK_PRD_ROUTER AND TASK_REPORT_ROUTER API'S


# TASK_PRD_ROUTER API'S FLOW OF USE AND WORKS :

REQUIRED INPUT FEILD'S :

1. task_id       =  REQUIRES A UNIQUE TASK ID.
2. group_id      =  REQUIRES A UNIQUE GROUP ID.
3. sender_id     =  REQUIRES A SENDER ID OR SENDER NAME.
4. to            =  REQUIRES A NAME OR ID TO WHOM THE TASK ASSIGNEE.
5. file          =  REQUIRES A VALID AUDIO FILE ENDS WITH .WAV, .MP3, .OGG FORMATS [NOTE:"IF THE UPLOADING FILES OR IN RATHER THAN THIS IT WILL OMIT"]
6. type          =  REQUIRES A TYPE OF THE TASK LIKE (BUGFIX/HIGH/LOW...)
7. priority      =  REQUIRES A PRIORITY OF THIS TASK (HIGH/MEDIUM/LOW)
8. eta           =  REQUIRES A TASK EXPECTED COMPLETION DATE 


THESE 8 FEILDS ARE REQUIRED IF ANYONE MISS IT WILL NOT PROCESS THROWS A ERROR LIKE THIS BELOW


# IF ANY ONE MISS THIS BELOW ERROR:

STATUS CODE : 400 BAD REQUEST

{
    "status": "error",
    "message": "group_id field are required"
}

# IF MISS MORE THAN 1 FEILDS THIS BELOW ERROR WITH MISSING FEILD NAME'S:

STATUS CODE : 400 BAD REQUEST

{
    "status": "error",
    "message": "group_id, sender_id, priority field are required"
}




# OUTPUT RESPONSE :

{
    "status": "true",
    "message": "Task Report Generated Successfully",
    "data": {
        "group_id": "00001",
        "task_id": "00002",
        "sender_id": "praveen",
        "to": "FRONTEND TEAM , BACKEND TEAM, AI TEAM  ",
        "priority": "HIGH",
        "task_date": "19/03/2026",
        "to_do": [
            "Daniel to integrate a speech-to-text API for audio transcription.",
            "Daniel to set up a backend service for storing meeting transcripts, summaries, and tasks.",
            "Daniel to develop the process for passing transcripts to an LLM to extract structured information.",
            "Priya to design the dashboard interface for the AI meeting notes assistant.",
            "Ahmed to experiment with prompt engineering for extracting action items and decisions from transcripts.",
            "The team to aim for a prototype within two weeks for internal testing."
        ],
        "type": "standard git flow",
        "task_summary": "The team discussed the development of an AI meeting notes assistant, aiming to automate note-taking, action item summarization, and decision tracking. The initial focus for the Minimum Viable Product (MVP) includes recording meeting audio, generating transcripts, and creating short summaries with action items. Key technical and user experience considerations were discussed, with a goal to have a prototype ready for internal testing within two weeks.",
        "suggestions": [
            "Implement speaker identification to accurately attribute statements, addressing challenges with multiple speakers and overlapping conversations.",
            "Incorporate topic segmentation to break down meetings into discussion segments, generating more readable and focused summaries for each section.",
            "Design the system to allow users to easily edit AI-generated notes before sharing, ensuring accuracy and user control over the final output."
        ],
        "eta": "06/03/2026"
    }
}



# FLOW OF WORK :

STEP 1 : CHECK FEILDS TO ENSURE 8 FEILDS ARE THERE OR NOT IF YES.

STEP 2 : IT WILL CHECK THE AUDIO AND DOWNLOAD INTO THE UPLOADS FOLDER AND IT WILL TRANSCRIPT THE DOWNLOADED AUDIO AND CHECK WHETHER AUDIO HAS VALID CONTENT OR NOT.
         IF THE AUDIO HAS NOISE OR UNAUDIOBLE SPEECH IT WILL THROW THE BELOW ERROR. OTHERWISE CONTINUE STEP 3.


STATUS CODE : 200

{
    "status": "true",
    "data": {
        "message": "upload a valid audioble audio file."
    }
}
       
STEP 3 : IF THE UPLOADED AUDIO IS VALID IT WILL TRANSCRIPT AND USING THE PROMPT IT WILL RETURN A STRUCTURED VALID JSON RESPONSE.LIKE THIS BELOW 



STATUS CODE : 200

{
    "status": "true",
    "message": "Task Report Generated Successfully",
    "data": {
        "group_id": "00001",
        "task_id": "00002",
        "sender_id": "praveen",
        "to": "FRONTEND TEAM , BACKEND TEAM, AI TEAM  ",
        "priority": "HIGH",
        "task_date": "19/03/2026",
        "to_do": [
            "Daniel: Integrate a speech-to-text API for audio transcription.",
            "Daniel: Set up a backend service to store meeting transcripts, summaries, and tasks.",
            "Daniel: Build the web dashboard for the MVP to allow users to upload or record meeting audio.",
            "Priya: Design the dashboard interface, focusing on recent meetings and detailed summary pages.",
            "Ahmed: Experiment with prompt engineering for extracting action items and decisions from transcripts.",
            "Sarah: Oversee the development of a prototype within two weeks for internal testing."
        ],
        "type": "standard git flow",
        "task_summary": "The team discussed the development of an AI meeting notes assistant, outlining its core functionality to automate note-taking, summarize action items, and track decisions. Key technical and UX considerations were addressed, including audio transcription, LLM integration, and dashboard design. The minimum viable product (MVP) will focus on recording audio, generating transcripts, and creating short summaries with action items, with a prototype targeted for internal testing within two weeks.",
        "suggestions": [
            "Implement speaker identification to accurately attribute statements, addressing challenges with multiple speakers and overlapping conversations.",
            "Introduce topic segmentation to break down meetings into discussion segments, generating more focused and readable summaries.",
            "Develop user-friendly editing capabilities for AI-generated summaries, allowing organizers to refine notes before sharing with the team.",
            "Explore integrations with external project management tools to automatically create and assign tasks based on identified action items."
        ],
        "eta": "06/03/2026"
    }
}



# TASK_REPORT_ROUTER API'S FLOW OF WORK :

REQUIRED INPUT FEILD'S :

1. task_id       =  REQUIRES A EXISTING TASK PRD'S TASK ID.


STEP 1 : IF THE TASK ID HAS A TASK PRD IN THE TASK-PRDS COLLECTION FROM THE DB IT WILL PROCESS. IF THE TASK ID DON'T IT WILL THROW THE BELOW ERROR.



STATUS CODE : 404

{
    "status": "error",
    "message": "mentioned task id dont have the prd not found"
}

STEP 2 : IF THE TASK ID HAS A TASK PRD IN THE DB IT WILL ANALYSE THE TASK PRD'S FEILD'S SUCH AS "to_do,task_date,eta,to,task_summary" TO GIVE A DETAIL TASKN REPORT BASED ON 
         THIS FEILDS AND TASK CHAT BY FETCHING THE "task_chat_messages" COLLECTION FROM THE DB BASED ON THE MATCHING TASK_ID IT WILL FETCH THE "MsgFrom_id, message, attachments"
         if the attachemts is emty it will leave it if is has object it will fetch the "file_url" and uding .env BASEURL IT WILL PATCH THE FULL LINK AND DOWNLOAD THE AUDIO FILES AND IT WILL TRANSCRIPT AND USING THE API'S SYSTEM PROMPT IT WILL SUMMARIZE THE CONTEXT OF ALL CHAT MESSAGES AND IT WILL CHECK ANOTHER COLLECTION TOO "activities" COLLECTION TO TRACK THE ACTIVITIES INSIDE THE TASK SUCH AS WHO CREATED THE TASK IF SOMEONE ASSIGNES CHANGED THE STATUS OF THE TASK AND IF TASK OR COMPLETED WITHIN IN THE SPECIFIED ETA DURATION.


STEP 3 : IF THAT "task_id" HAS DATAS IN ALL 3 COLLECTION SUCH AS "task_prds,task_chat_messages,activities" IT WILL PRODUCE A JSON RESPONSE LIKE THIS BELOW


STATUS CODE : 200

{
    "status": "true",
    "message": "Task Report Generated Successfully",
    "data": {
        "task_id": "69b2531c38b684580374c4d9",
        "group_id": "69b24d8538b684580374bc4c",
        "assignee": "Abinesh Durai Tsit, me",
        "task_generated_date": "12/03/2026",
        "priority": "High",
        "key_highlights": [
            "Task was created by Avinash.",
            "Task view status changed by Abinesh Durai.",
            "Task view status changed by Vignesh Developer.",
            "Task was reassigned by Vignesh Developer.",
            "Task audio content was listened to by Vignesh Developer."
        ],
        "upcoming_tasks": [
            "Finalize Q3 budget review with the finance department.",
            "Prepare the agenda and materials for the upcoming Project Alpha kickoff meeting.",
            "Follow up on outstanding vendor contracts for the Phase 2 procurement.",
            "Draft the weekly progress report for the executive steering committee."
        ],
        "task_summary": "The task is currently on time. The past week saw significant progress on key deliverables, with Phase 1 milestones successfully met and initial stakeholder engagement completed. We are currently transitioning into the planning stages for Phase 2, focusing on resource allocation and vendor finalization to maintain momentum and adhere to the project timeline.",
        "suggestions": [
            "Implement a more agile feedback loop with key stakeholders to address potential blockers proactively.",
            "Standardize documentation templates across all project phases to improve consistency and reduce onboarding time for new team members.",
            "Conduct a brief post-mortem on Phase 1 to capture lessons learned and apply them to subsequent phases."
        ],
        "eta": "2026-03-12"
    }
}

