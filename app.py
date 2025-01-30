from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.utilsDatabase import (
    getAllJobs,
    getAllKeywords,
    getHoursOfData,
    addKeyword,
    getNotAppliedJobs,
    removeKeyword,
    updateJobStatus,
    addToEasyApply,
    getCountForAcceptDeny,
)
import os
import subprocess
import socket
import json


app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class JobPostingModel(BaseModel):
    id: str
    link: str
    title: str
    companyName: str
    location: str
    method: str
    timeStamp: str
    jobType: str
    jobDescription: str
    applied: str

    class Config:
        from_attributes = True


class KeywordModel(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True


class AddKeywordRequest(BaseModel):
    name: str
    type: str


class RemoveKeywordRequest(BaseModel):
    id: int


class ApplyRequestModel(BaseModel):
    jobID: str
    applyMethod: str
    link: str
    useBot: bool


class RejectRequestModel(BaseModel):
    jobID: str


class AddToEasyApplyRequest(BaseModel):
    jobID: int
    status: str

class HoursRequest(BaseModel):
    hours: int

class LinkedInQuestion(BaseModel):
    question: str
    type: str
    required: bool
    options: list[str] | None
    currentAnswer: str | list[str] | None
    verified: bool

class UpdateLinkedInQuestionsRequest(BaseModel):
    questions: list[LinkedInQuestion]

# API Endpoints
@app.get("/")
def helloWorld():
    """Welcome endpoint."""
    return {"message": "Hello Duniya"}


@app.get("/getData", response_model=list[JobPostingModel])
def getData():
    """Fetch all job postings."""
    # records = getAllJobs()
    records = getNotAppliedJobs()
    if not records:
        raise HTTPException(status_code=404, detail="No data found.")
    return records


@app.get("/scrapeNewData")
def scrapeNewData():
    """Trigger the data scraping script via socket listener."""
    try:
        # Replace with your server's IP address on the local network11
        HOST = '0.0.0.0' 
        PORT = 12345
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'run_scraper\n')
            # Wait for response
            response = s.recv(1024)
            return {"success": True, "message": f"Data scraping initiated: {response.decode()}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger scraper: {str(e)}"
        )
    finally:
        s.close()


@app.get("/getCountForAcceptDeny")
def countAcceptDeny():
    """
    Fetch the counts of accepted and rejected job applications.
    """
    try:
        counts = getCountForAcceptDeny()
        return {
            "message": "Counts fetched successfully.",
            "data": counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching counts: {str(e)}")

@app.post("/getHoursOfData", response_model=list[JobPostingModel])
def get_hours_of_data(request: HoursRequest):
    """Fetch job postings from the last specified hours."""
    try:
        print(request.hours)
        timedRecords = getHoursOfData(request.hours)
        if not timedRecords:
            raise HTTPException(status_code=404, detail="No job postings found for the given hours.")
        return timedRecords
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/getKeywords", response_model=list[KeywordModel])
def getKeywords():
    """Fetch all keywords."""
    keywords = getAllKeywords()
    if not keywords:
        raise HTTPException(status_code=404, detail="No keywords found.")
    return keywords


@app.post("/addKeyword")
def addKeywordEndpoint(request: AddKeywordRequest):
    """Add a new keyword."""
    newKeyword = addKeyword(request.name, request.type)
    if newKeyword:
        return {"message": "Keyword added successfully", "id": newKeyword.id}
    raise HTTPException(status_code=500, detail="Failed to add keyword.")


@app.post("/removeKeyword")
def removeKeywordEndpoint(request: RemoveKeywordRequest):
    """Remove a keyword."""
    keyword = removeKeyword(request.id)
    if keyword:
        return {"message": "Keyword removed successfully."}
    raise HTTPException(
        status_code=404, detail=f"No keyword found with ID {request.id}."
    )


@app.post("/applyThis")
def applyJob(request: ApplyRequestModel):
    """Mark a job as applied or add it to Easy Apply."""
    print(request.useBot)
    if request.useBot:
        # If useBot is True, add to Easy Apply
        easyApplyEntry = addToEasyApply(request.jobID, 'PENDING')
        if easyApplyEntry:
            return {
                "message": "Application added to Easy Apply successfully.",
                "jobID": request.jobID,
                "applyMethod": request.applyMethod,
                "link": request.link,
                "useBot": request.useBot,
                "entryID": easyApplyEntry.id,
            }
        raise HTTPException(status_code=500, detail="Failed to add to Easy Apply.")
    else:
        # If useBot is False, just update the job status to "YES"
        job = updateJobStatus(request.jobID, "YES")
        if job:
            return {
                "message": "Application submitted successfully.",
                "jobID": request.jobID,
                "applyMethod": request.applyMethod,
                "link": request.link,
                "useBot": request.useBot,
            }
        raise HTTPException(
            status_code=404, detail=f"No record found with ID {request.jobID}."
        )


@app.post("/rejectThis")
def rejectJob(request: RejectRequestModel):
    """Reject a job posting."""
    job = updateJobStatus(request.jobID, "NEVER")
    if job:
        return {"message": "Rejection recorded successfully.", "jobID": request.jobID}
    raise HTTPException(
        status_code=404, detail=f"No record found with ID {request.jobID}."
    )


@app.get("/getLinkedInQuestions")
def get_linkedin_questions():
    """Fetch LinkedIn questions from JSON file."""
    try:
        file_path = r"/home/robada/Desktop/LinkedIn-Saral-Apply/linkedinQuestions.json"
        with open(file_path, 'r') as file:
            questions_data = json.load(file)
        return {
            "message": "Questions fetched successfully",
            "data": questions_data
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Questions file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Error parsing questions file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading questions file: {str(e)}"
        )


@app.post("/updateLinkedInQuestions")
def update_linkedin_questions(request: UpdateLinkedInQuestionsRequest):
    """Update LinkedIn questions in JSON file."""
    try:
        file_path = r"/home/robada/Desktop/LinkedIn-Saral-Apply/linkedinQuestions.json"
        
        # Convert the questions to a list of dictionaries
        questions_data = [question.model_dump() for question in request.questions]
        
        # Write the updated questions to the file
        with open(file_path, 'w') as file:
            json.dump(questions_data, file, indent=2)
            
        return {
            "message": "Questions updated successfully",
            "data": questions_data
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Questions file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating questions file: {str(e)}"
        )


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
