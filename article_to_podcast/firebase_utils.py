from firebase_admin import firestore, credentials, initialize_app, storage

from article_to_podcast.models import Podcast, Script

cred = credentials.Certificate("article_to_podcast/prtimes-podcasts-firebase-adminsdk-7j9wl-b5c1035d6c.json")
initialize_app(cred)
db = firestore.client()
bucket = storage.bucket("prtimes-podcasts.firebasestorage.app")


def save_new_podcast(podcast: Podcast, audio_file_path: str):
    try:
        audio_url = upload_audio_to_storage(audio_file_path, f"podcasts/{podcast.title}.mp3")
        print(audio_url)
        doc_ref = db.collection("podcasts")
        
        new_podcast = {
            "title": podcast.title,
            "summary": podcast.summary,
            "press_id": podcast.press_id,
            "audio_url": audio_url,
            "scripts": [{"person": script.person, "script": script.script} for script in podcast.scripts]
        }
        print(new_podcast)
        
        doc_ref.add(new_podcast)
        return new_podcast
    except Exception as e:
        raise RuntimeError(f"Failed to save new podcast: {e}")

def upload_audio_to_storage(file_path: str, destination_blob_name: str) -> str:
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url

def get_all_podcasts():
    try:
        doc_ref = db.collection("podcasts")
        docs = doc_ref.stream()

        podcasts = []
        for doc in docs:
            podcasts.append(doc.to_dict())
        
        return podcasts
    except Exception as e:
        raise RuntimeError(f"Failed to get all podcasts: {e}")

def get_podcasts_by_press_id(press_id: int):
    try:
        doc_ref = db.collection("podcasts")
        query = doc_ref.where("press_id", "==", press_id)
        docs = query.stream()

        podcasts = []
        for doc in docs:
            podcasts.append(doc.to_dict())
        return podcasts
    except Exception as e:
        raise RuntimeError(f"Failed to get podcasts by press_id: {e}")
        