import base64
import datetime
import hmac
import html as htmllib
import json
import os
import sys
import tempfile
import threading
import time
from io import BytesIO

import bleach
import markdown
from flask import Flask, abort, render_template, request, send_file
from google import genai
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORIES_FILE = os.path.join(DATA_DIR, "stories.json")
IMAGE_FILE = os.path.join(DATA_DIR, "featured.png")


def load_env(path):
    """Minimal .env reader so secrets never live in the source code."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env(os.path.join(BASE_DIR, ".env"))

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
TRIGGER_KEY = os.environ.get("TRIGGER_KEY", "")
UPLOAD_KEY = os.environ.get("UPLOAD_KEY", "")
TEXT_MODEL = os.environ.get("TEXT_MODEL", "gemini-3.5-flash-lite")
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gemini-3.1-flash-lite-image")

GENRES = [
    "Mystery", "Romance", "Fantasy", "Science Fiction", "Horror",
    "Historical Fiction", "Dystopian", "Flash Fiction", "Shakespearean",
]
FEATURED = 5
STORY_DELAY_SECONDS = 6

ALLOWED_TAGS = ["p", "br", "em", "strong", "i", "b", "blockquote", "hr", "ul", "ol", "li"]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

_file_lock = threading.Lock()
_job_locks = {"stories": threading.Lock(), "image": threading.Lock()}
_client = None


# ---------- helpers ----------

def get_client():
    global _client
    if _client is None:
        if not GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not set (add it to the .env file).")
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return default


def write_json(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def clean_html(raw):
    return bleach.clean(raw or "", tags=ALLOWED_TAGS, attributes={}, strip=True)


def excerpt(raw_html, limit):
    text = bleach.clean(raw_html or "", tags=[], strip=True)
    text = " ".join(htmllib.unescape(text).split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:-") + "\u2026"


def clean_title(title, fallback):
    title = " ".join((title or "").replace('"', "").split())
    if title.lower().startswith("title:"):
        title = title[6:].strip()
    return title[:120] or fallback


def load_stories():
    return read_json(STORIES_FILE, {"stories": {}}).get("stories", {})


def save_stories(stories):
    with _file_lock:
        write_json(STORIES_FILE, {"stories": stories})


def start_job(name, fn, *args):
    lock = _job_locks[name]
    if not lock.acquire(blocking=False):
        return False

    def runner():
        try:
            fn(*args)
        except Exception:
            app.logger.exception("Job %s failed", name)
        finally:
            lock.release()

    threading.Thread(target=runner, daemon=True).start()
    return True


def authorised(supplied, expected):
    if not expected or not supplied:
        return False
    return hmac.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8"))


@app.after_request
def security_headers(resp):
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; "
        "form-action 'self'; base-uri 'none'"
    )
    return resp


# ---------- Gemini (Interactions API) ----------

def ask(prompt, schema=None, retries=3):
    """One text call. Returns text, or None after all retries fail."""
    for attempt in range(retries):
        try:
            kwargs = {"model": TEXT_MODEL, "input": prompt, "store": False}
            if schema:
                kwargs["response_format"] = {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": schema,
                }
            interaction = get_client().interactions.create(**kwargs)
            text = (interaction.output_text or "").strip()
            if text:
                return text
        except Exception as e:
            app.logger.warning("Gemini attempt %s failed: %s", attempt + 1, e)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(30 * (attempt + 1))
            else:
                time.sleep(2)
    return None


def ask_json(prompt, schema, retries=3):
    raw = ask(prompt, schema, retries)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        app.logger.warning("Model returned invalid JSON")
        return None
    return data if isinstance(data, dict) else None


def generate_featured_image(headline):
    prompt = (
        "A cinematic, landscape-oriented illustration for a short story titled: "
        + headline[:150]
        + ". Evocative lighting, strong composition, detailed texture. "
        "No text, no lettering, no watermarks."
    )
    interaction = get_client().interactions.create(
        model=IMAGE_MODEL,
        input=prompt,
        store=False,
        response_format={"type": "image", "aspect_ratio": "16:9"},
    )
    block = interaction.output_image
    if block is None or not block.data:
        raise RuntimeError("The image model returned no image.")
    image = Image.open(BytesIO(base64.b64decode(block.data))).convert("RGB")
    image.thumbnail((1280, 1280))
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".png")
    os.close(fd)
    image.save(tmp, "PNG", optimize=True)
    os.replace(tmp, IMAGE_FILE)
    app.logger.info("Featured image saved.")


def refresh_image():
    story = load_stories().get(str(FEATURED))
    if not story:
        return
    try:
        generate_featured_image(story["title"])
    except Exception as e:
        # Keep the previous image; the stories are already saved.
        app.logger.warning("Image generation failed: %s", e)


# ---------- stories ----------

STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "A 3-6 word title, no quotation marks."},
        "story": {"type": "string", "description": "The story in Markdown paragraphs, no title heading."},
    },
    "required": ["title", "story"],
}


def write_story(genre, avoid_titles):
    prompt = (
        "ROLE: You are a master short story writer specialising in " + genre + ".\n"
        "TASK: Write a complete, high-quality, original short story of at most 800 words.\n"
        "GUIDELINES: Start in medias res. Show, don't tell. Limit the number of characters. "
        "Do not put a title or introduction inside the story text.\n"
    )
    if genre == "Shakespearean":
        prompt += "STYLE: Use Early Modern English.\n"
    if avoid_titles:
        prompt += "The title must be new. Do not reuse these titles: " + "; ".join(avoid_titles) + ".\n"
    prompt += "Return JSON with the fields title and story."

    data = ask_json(prompt, STORY_SCHEMA)
    if not data:
        return None
    story = (data.get("story") or "").strip()
    if len(story.split()) < 80:
        return None
    return {
        "title": clean_title(data.get("title"), genre + " Story"),
        "html": clean_html(markdown.markdown(story)),
    }


def run_stories():
    app.logger.info("Starting story batch.")
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    stories = load_stories()
    avoid = [s.get("title", "") for s in stories.values() if s.get("title")]
    made = 0

    for idx, genre in enumerate(GENRES, start=1):
        story = write_story(genre, avoid)
        if not story:
            app.logger.error("Failed to generate %s; stopping the batch.", genre)
            break
        story["date"] = today
        stories[str(idx)] = story
        avoid.append(story["title"])
        made += 1
        app.logger.info("Generated %s", genre)
        if idx < len(GENRES):
            time.sleep(STORY_DELAY_SECONDS)

    if made:
        save_stories(stories)
        if str(FEATURED) in stories and stories[str(FEATURED)].get("date") == today:
            refresh_image()
    return made


def store_payload(payload):
    """Accepts the legacy {h1..h9, c1..c9, date} format."""
    stories = load_stories()
    date = str(payload.get("date") or datetime.datetime.now().strftime("%Y/%m/%d"))[:20]
    saved = 0
    for n in range(1, len(GENRES) + 1):
        title = payload.get("h" + str(n))
        body = payload.get("c" + str(n))
        if isinstance(title, str) and isinstance(body, str) and title.strip() and body.strip():
            stories[str(n)] = {
                "title": clean_title(title, GENRES[n - 1] + " Story"),
                "html": clean_html(body),
                "date": date,
            }
            saved += 1
    if saved:
        save_stories(stories)
    return saved


# ---------- routes ----------

@app.route("/")
def home():
    stories = load_stories()
    items = []
    for n in range(1, len(GENRES) + 1):
        story = stories.get(str(n))
        if story:
            items.append({
                "n": n,
                "genre": GENRES[n - 1],
                "title": story.get("title", "Untitled"),
                "excerpt": excerpt(story.get("html"), 260 if n == FEATURED else 170),
            })
    featured = next((i for i in items if i["n"] == FEATURED), None)
    others = [i for i in items if i["n"] != FEATURED]
    edition = max((s.get("date", "") for s in stories.values()), default="")
    has_image = os.path.exists(IMAGE_FILE)
    version = int(os.path.getmtime(IMAGE_FILE)) if has_image else 0
    return render_template("index.html", featured=featured, others=others,
                           edition=edition, has_image=has_image, version=version)


@app.route("/article/<int:number>")
def article(number):
    stories = load_stories()
    story = stories.get(str(number))
    if not story or not 1 <= number <= len(GENRES):
        abort(404)
    available = sorted(int(k) for k in stories if k.isdigit())
    pos = available.index(number)
    prev_n = available[pos - 1] if pos > 0 else None
    next_n = available[pos + 1] if pos < len(available) - 1 else None

    def link(n):
        return {"n": n, "title": stories[str(n)].get("title", "Untitled")} if n else None

    return render_template(
        "article.html",
        title=story.get("title", "Untitled"),
        body=clean_html(story.get("html")),
        date=story.get("date", ""),
        genre=GENRES[number - 1],
        prev_story=link(prev_n),
        next_story=link(next_n),
    )


@app.route("/generate_image")
def thumbnail():
    if not os.path.exists(IMAGE_FILE):
        abort(404)
    return send_file(IMAGE_FILE, mimetype="image/png", max_age=3600)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/upload/<key>", methods=["POST"])
def upload(key):
    if not authorised(key, UPLOAD_KEY):
        return "Forbidden", 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return "Invalid JSON", 400
    saved = store_payload(payload)
    if saved:
        start_job("image", refresh_image)
    return "Saved " + str(saved) + " stories", 200


@app.route("/trigger/mittentis/")
def trigger_stories():
    supplied = request.headers.get("X-Trigger-Key") or request.args.get("key") or ""
    if not authorised(supplied, TRIGGER_KEY):
        return "Forbidden", 403
    if not start_job("stories", run_stories):
        return "A story job is already running.", 409
    return "Story job started.", 202


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stories":
        print("Stories generated:", run_stories())
    else:
        app.run(host="127.0.0.1", port=5000)
