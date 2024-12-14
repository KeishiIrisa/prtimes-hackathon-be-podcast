import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from typing import List
from pydub import AudioSegment

from article_to_podcast.models import Podcast, Script
from article_to_podcast.firebase_utils import save_new_podcast

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
    
def generate_podcast_from_article(article: str, press_id: int) -> str:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは、与えられた記事の文章を受け取り、それを元に聞き手の興味をそそるようなポッドキャストの原稿を作成してください。登場人物は司会者のケイシ、登壇者のクアン、アヤカの3人です。それぞれのセリフと名前をscriptに格納すること。原稿は3人が話し合う形式にすること。合計で100文字以内にすること"},
            {"role": "user", "content": article}
        ],
        response_format=Podcast,
    )    
    response = completion.choices[0].message.parsed
 
    scripts = [Script(person=script.person, script=re.sub(r'\n', '', script.script)) for script in response.scripts]    

    audio_file_path = generate_audio_from_scripts(scripts)
    
    podcast = Podcast(
        title=response.title,
        scripts=scripts,
        summary=response.summary,
        press_id=press_id
    )
    
    saved_podcast = save_new_podcast(podcast, audio_file_path)
    return saved_podcast

def generate_audio_from_scripts(scripts: List[Script]):
    audio_files = []
    
    for i, script in enumerate(scripts):
        if script.person == "ケイシ":
            voice = "alloy"
        elif script.person == "クアン":
            voice = "onyx"
        elif script.person == "アヤカ":
            voice = "nova"
        else:
            voice = "alloy"
        
        res = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script.script,
        )
        
        temp_file_path = f"output_{i}.mp3"
        res.stream_to_file(temp_file_path)
        audio_files.append(temp_file_path)
        
    combined = AudioSegment.empty()
    for file in audio_files:
        combined += AudioSegment.from_mp3(file)

    combined_audio_file_path = "whole_podcast.mp3"
    combined.export(combined_audio_file_path, format="mp3")

    for file in audio_files:
        os.remove(file)
    
    return combined_audio_file_path
