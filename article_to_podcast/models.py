from pydantic import BaseModel
from typing import List, Literal

class GeneratePodcastRequest(BaseModel):
    press_id: int
    uid: str
    article: str

class Script(BaseModel):
    person: Literal["ケイシ", "クアン", "アヤカ"]
    script: str

class Podcast(BaseModel):
    title: str
    scripts: List[Script]
    summary: str
    press_id: int
