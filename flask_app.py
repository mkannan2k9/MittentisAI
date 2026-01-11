import os
import time
import datetime
import markdown
import json
from io import BytesIO
from flask import Flask, request, render_template, abort, send_file
from PIL import Image
from google import genai
from google.genai import types

GOOGLE_API_KEY = "GOOGLE-API-KEY"

TEXT_MODEL = "gemini-2.5-flash-lite" 
IMAGE_MODEL = "gemini-2.5-flash-image"

app = Flask(__name__)
client = genai.Client(api_key=GOOGLE_API_KEY)

class DataStore:
    data = {}

def process_story_upload(payload):
    print("Processing story data...")
    DataStore.data = {k: payload.get(k) for k in payload if k.startswith(('h', 'c'))}
    DataStore.data['date'] = payload.get('date')

    headline_for_image = DataStore.data.get("h5", "Abstract Concept")
    image_prompt = (
        f"A cinematic, landscape-oriented illustration suitable for a short story titled: '{headline_for_image}'. "
        "High contrast, evocative lighting, detailed texture."
    )

    try:
        print(f"Generating image with prompt: {image_prompt[:50]}...")

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_ONLY_HIGH"
                    )
                ]
            )
        )

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image = image.resize((512, 512))
                    static_folder = os.path.join(app.root_path, 'static')
                    os.makedirs(static_folder, exist_ok=True)
                    image.save(os.path.join(static_folder, 'generated_image.png'))
                    print("Image generated and saved successfully.")
                    break
        else:
            print("No image returned from API.")

    except Exception as e:
        print(f"IMAGE GENERATION FAILED: {e}")

    return "Data saved successfully"

@app.route('/upload/<key>', methods=['POST'])
def upload(key):
    if key != "hello":
        return "Bad API key", 403
    payload = request.get_json()
    return process_story_upload(payload)

@app.route('/')
def home():
    template_args = {}
    for i in range(1, 10):
        h_key = f"h{i}"
        c_key = f"c{i}"
        heading = DataStore.data.get(h_key, "Sample Heading")
        content = DataStore.data.get(c_key, "Sample Description")
        clean_content = content.replace("<p>", "").replace("</p>", "") if content else ""
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
    try:
        return send_file("static/generated_image.png", mimetype='image/png')
    except FileNotFoundError:
        return "Image not found. Run triggers first.", 404

def generate_with_retry(model, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            if response.text:
                return response.text
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if "429" in str(e):
                print("Rate limit hit. Sleeping 30s...")
                time.sleep(30)
            else:
                time.sleep(2)
    return None

@app.route("/trigger/mittentis/")
def mitt():
    genres = [
        "Mystery", "Romance", "Fantasy", "Science Fiction", "Horror",
        "Historical Fiction", "Dystopian", "Flash Fiction", "Shakespearean"
    ]

    results = {}
    current_date = datetime.datetime.now().strftime("%Y/%m/%d")

    print("Starting batch generation...")

    for idx, genre in enumerate(genres, start=1):
        prompt_story = (
            f"ROLE: You are a master short story writer specializing in {genre}.\n"
            "TASK: Write a complete, high-quality short story (max 800 words).\n"
            "GUIDELINES: Start in medias res. Show, Don't Tell. Limit characters. No Intro/Title text.\n"
        )

        if genre == "Shakespearean":
            prompt_story += "STYLE: Use Early Modern English.\n"

        story_text = generate_with_retry(TEXT_MODEL, prompt_story)
        
        if not story_text:
            print(f"CRITICAL: Failed to generate {genre}. Aborting batch to save resources.")
            break 

        rendered_story = markdown.markdown(story_text)

        prompt_title = f"Generate a short 3-5 word title for this story. OUTPUT TITLE ONLY:\n\n{story_text[:500]}..."
        title_text = generate_with_retry(TEXT_MODEL, prompt_title)
        
        clean_title = title_text.strip().replace('"', '').replace("Title:", "") if title_text else f"{genre} Story"

        results[f"h{idx}"] = clean_title
        results[f"c{idx}"] = rendered_story

        print(f"Generated {genre}")

        time.sleep(20)

    results["date"] = current_date

    if len(results) > 1:
        try:
            process_story_upload(results)
            return f"Batch finished. Generated {len(results)-1} stories."
        except Exception as e:
            print(f"Failed to process results: {e}")
            return "Batch finished but upload/processing failed."
    else:
        return "Batch failed immediately. No stories generated."

if __name__ == '__main__':
    app.run(host="0.0.0.0")
