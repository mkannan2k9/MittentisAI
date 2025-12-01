import os
import time
import datetime
import markdown
import requests
from io import BytesIO
from flask import Flask, request, render_template, abort, send_file
from PIL import Image
from gtts import gTTS
from google import genai
from google.genai import types
import json

GOOGLE_API_KEY = "GOOGLE_API_KEY"
PODBEAN_CLIENT_ID = "PODBEAN_CLIENT_ID"
PODBEAN_CLIENT_SECRET = "PODBEAN_CLIENT_SECRET"

TEXT_MODEL = "gemini-2.5-flash-lite"
IMAGE_MODEL = "imagen-3.0-generate-002"

app = Flask(__name__)
client = genai.Client(api_key=GOOGLE_API_KEY)

class DataStore:
    """Simple in-memory storage. Note: Data is lost if the server restarts."""
    data = {}

@app.route('/upload/<key>', methods=['POST'])
def upload(key):
    if key != "hello":
        return "Bad API key", 403

    print("Authenticated upload request received.")
    payload = request.get_json()

    DataStore.data = {k: payload.get(k) for k in payload if k.startswith(('h', 'c'))}
    DataStore.data['date'] = payload.get('date')

    # Image Generation
    headline_for_image = DataStore.data.get("h5", "Abstract Concept")
    image_prompt = (
        f"A cinematic, landscape-oriented illustration suitable for a short story titled: '{headline_for_image}'. "
        "High contrast, evocative lighting, detailed texture."
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=image_prompt,
        config=types.GenerateContentConfig(response_modalities=['Image'])
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            image = image.resize((512, 512))

            static_folder = os.path.join(app.root_path, 'static')
            os.makedirs(static_folder, exist_ok=True)
            image.save(os.path.join(static_folder, 'generated_image.png'))
            print("Image generated and saved successfully.")
            break

    return "Data saved successfully"

@app.route('/')
def home():
    template_args = {}
    for i in range(1, 10):
        h_key = f"h{i}"
        c_key = f"c{i}"

        heading = DataStore.data.get(h_key, "Sample Heading")
        content = DataStore.data.get(c_key, "Sample Description")

        clean_content = content.replace("<p>", "").replace("</p>", "")

        template_args[h_key] = heading
        limit = 200 if i == 5 else 100
        template_args[f"d{i}"] = clean_content[:limit]

    return render_template("index.html", **template_args)

@app.route('/article/<int:number>')
def article(number):
    if not (1 <= number <= 9):
        abort(404)

    heading = DataStore.data.get(f"h{number}", "Sample Heading")
    content = DataStore.data.get(f"c{number}", "Sample Description")
    date = DataStore.data.get("date", "Not given")

    return render_template("article.html", h=heading, c=content, date=date)

@app.route('/generate_image')
def thumbnail():
    return send_file("static/generated_image.png", mimetype='image/png')

#Trigger Functions

def generate_with_retry(model, prompt, retries=3):
    """Helper to handle API flakiness."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            if response.text:
                return response.text
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(1)
    return None

def generate_simple(model, prompt):
    """Helper that makes a direct call. No retries, no catching."""
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text

@app.route('/trigger/<SET A TRIGGER>')
def trigger_podcast():
    topics_file = os.path.join(os.path.dirname(__file__), 'topicsandsubjects.txt')
    seen_topics = set()

    if os.path.exists(topics_file):
        with open(topics_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("Topic:"):
                    t = line.partition(":")[2].strip().lower()
                    seen_topics.add(t)

    topic = None
    subject = None

    for attempt in range(5):
        print(f"Generating topic... (Attempt {attempt + 1})")

        topic_prompt = f"""
        Generate a unique educational topic and subject.
        Output strictly in JSON format like this:
        {{"topic": "The French Revolution", "subject": "History"}}
        """

        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=topic_prompt,
            config=types.GenerateContentConfig(
                temperature=1.0,
                response_mime_type='application/json'  # <--- MAGIC FIX
            )
        )

        data = json.loads(response.text)
        temp_topic = data.get("topic")
        temp_subject = data.get("subject")

        if temp_topic and temp_subject:
            if temp_topic.lower() not in seen_topics:
                topic = temp_topic
                subject = temp_subject

               with open(topics_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\nTopic: {topic}\nSubject: {subject}")
                break
            else:
                print(f"Duplicate: {temp_topic}")
        else:
            print("JSON missing keys")

    if not topic:
        return "Failed to generate unique topic."

    print(f"Selected Topic: {topic}")

    lesson_prompt = f"""
    Write a podcast script.
    Topic: {topic} | Subject: {subject}
    Style: Storytelling, Grade 6 level, 300 words. Plain text only.
    """
    lesson_text = generate_simple(TEXT_MODEL, lesson_prompt)

    clean_text = lesson_text.replace("**", "").replace("##", "")
    tts_obj = gTTS(text=clean_text, lang='en', slow=False)
    tts_obj.save("welcome.mp3")

    meta_prompt = f"""
    Write a title and description.
    Topic: {topic}
    Output strictly in JSON format like this:
    {{"title": "The Title Here", "description": "The description here."}}
    """

    
    meta_resp = client.models.generate_content(
        model=TEXT_MODEL,
        contents=meta_prompt,
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    meta_data = json.loads(meta_resp.text)

    ep_title = meta_data.get("title", f"{topic} Episode")
    ep_desc = meta_data.get("description", "Listen now.")

    
    MODE = "PROD"
    if MODE == "PROD":
        token_resp = requests.post(
            "https://api.podbean.com/v1/oauth/token",
            data={"grant_type": "client_credentials", "client_id": PODBEAN_CLIENT_ID, "client_secret": PODBEAN_CLIENT_SECRET}
        )
        access_token = token_resp.json()["access_token"]

        file_size = os.path.getsize("welcome.mp3")
        auth_resp = requests.get(
            "https://api.podbean.com/v1/files/uploadAuthorize",
            params={'access_token': access_token, 'filename': 'welcome.mp3', 'filesize': file_size, 'content_type': 'audio/mpeg'}
        )
        auth_data = auth_resp.json()

        with open("welcome.mp3", "rb") as f:
            requests.put(auth_data["presigned_url"], data=f, headers={'Content-Type': 'audio/mpeg'})

        requests.post(
            "https://api.podbean.com/v1/episodes",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": ep_title, "content": ep_desc, "status": "publish", "type": "public", "media_key": auth_data["file_key"]
            }
        )

    return "ok"

@app.route("/trigger/<SET A TRIGGER>/")
def mitt():
    """Generates 9 stories of different genres and uploads them to the main app."""
    genres = [
        "Mystery", "Romance", "Fantasy", "Science Fiction", "Horror",
        "Historical Fiction", "Dystopian", "Flash Fiction", "Shakespearean"
    ]

    results = {}
    current_date = datetime.datetime.now().strftime("%Y/%m/%d")

    for idx, genre in enumerate(genres, start=1):
        prompt_story = (
            f"ROLE: You are a master short story writer specializing in {genre}.\n"
            "TASK: Write a complete, high-quality short story (max 800 words).\n\n"
            "GUIDELINES:\n"
            "1. Start in medias res (action-oriented opening).\n"
            "2. Focus on sensory details (Show, Don't Tell).\n"
            "3. Limit characters to 2-3 max.\n"
            "4. NO Introduction text, NO 'Title:' header. Just the story text.\n"
            "5. End with a resonant, impactful closing line.\n"
        )

        if genre == "Shakespearean":
            prompt_story += "6. STYLE: Use Early Modern English (thee/thou), iambic rhythm where possible.\n"

        story_text = generate_with_retry(TEXT_MODEL, prompt_story)

        if not story_text:
            story_text = "Story generation failed."

        rendered_story = markdown.markdown(story_text)

        prompt_title = f"Generate a short, captivating 3-5 word title for this story. OUTPUT TITLE ONLY:\n\n{story_text[:500]}..."
        title_text = generate_with_retry(TEXT_MODEL, prompt_title)
        clean_title = title_text.strip().replace('"', '').replace("Title:", "")

        results[f"h{idx}"] = clean_title
        results[f"c{idx}"] = rendered_story

        print(f"Generated {genre}")
        time.sleep(2)

    results["date"] = current_date

    try:
        requests.post('https://mittentisai.pythonanywhere.com/upload/<SET A TRIGGER>', json=results)
    except Exception as e:
        print(f"Failed to post results to self: {e}")

    return "ok"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
