import os

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from article_to_podcast.openai_utils import generate_podcast_from_article
from article_to_podcast.models import GeneratePodcastRequest
from article_to_podcast.firebase_utils import get_all_podcasts, get_podcasts_by_press_id


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://prtimes-hackathon-fe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  

@app.get("/")
def read_root():
    return {"Hello": "RI-HAQ"}


@app.get("/podcasts")
async def get_podcasts():
    try:
        podcasts = get_all_podcasts()
        return JSONResponse(content=podcasts, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/podcasts/{press_id}")
async def get_podcasts_by_press_id_endpoint(press_id: int):
    try:
        podcasts = get_podcasts_by_press_id(press_id)
        return JSONResponse(content=podcasts, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

@app.post("/podcasts")
async def generate_podcasts(request: GeneratePodcastRequest):
    try:
        new_podcast = generate_podcast_from_article(request.article, request.press_id)
        return JSONResponse(content=new_podcast, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

