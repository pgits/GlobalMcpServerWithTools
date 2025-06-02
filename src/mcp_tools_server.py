import os
import json
import logging
import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting MCP Tools Server...")

app = FastAPI(title="MCP Tools Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class DocRequest(BaseModel):
    title: str
    content: Optional[str] = ""

def get_google_creds():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds

@app.post("/create_doc")
async def create_google_doc(doc_request: DocRequest):
    try:
        creds = get_google_creds()
        service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        document = service.documents().create(body={"title": doc_request.title}).execute()

        if doc_request.content:
            requests = [{"insertText": {"location": {"index": 1}, "text": doc_request.content}}]
            service.documents().batchUpdate(
                documentId=document.get("documentId"),
                body={"requests": requests}
            ).execute()

        return {
            "message": "Document created successfully",
            "document_id": document.get("documentId"),
            "title": doc_request.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting server on port 8888...")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="debug")
    logger.info("Server started successfully!")
