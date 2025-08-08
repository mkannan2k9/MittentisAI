from flask import *
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import requests
from gtts import gTTS
from google import genai
import time
import markdown
import datetime

app = Flask(__name__)

class DataStore:
    """Class to store data in static variables."""
    data = {}

@app.route('/upload/<key>', methods=['POST'])
def upload(key):
    if key == "hello":
        client = genai.Client(api_key='API_KEY')
        print("Key is hello")
        # Extract data from the JSON request
        h1 = request.get_json().get('h1')
        c1 = request.get_json().get('c1')
        h2 = request.get_json().get('h2')
        c2 = request.get_json().get('c2')
        h3 = request.get_json().get('h3')
        c3 = request.get_json().get('c3')
        h4 = request.get_json().get('h4')
        c4 = request.get_json().get('c4')
        h5 = request.get_json().get('h5')
        c5 = request.get_json().get('c5')
        h6 = request.get_json().get('h6')
        c6 = request.get_json().get('c6')
        h7 = request.get_json().get('h7')
        c7 = request.get_json().get('c7')
        h8 = request.get_json().get('h8')
        c8 = request.get_json().get('c8')
        h9 = request.get_json().get('h9')
        c9 = request.get_json().get('c9')
        date = request.get_json().get('date')

        # Store the data in the DataStore class
        DataStore.data = {
            "h1": h1, "c1": c1,
            "h2": h2, "c2": c2,
            "h3": h3, "c3": c3,
            "h4": h4, "c4": c4,
            "h5": h5, "c5": c5,
            "h6": h6, "c6": c6,
            "h7": h7, "c7": c7,
            "h8": h8, "c8": c8,
            "h9": h9, "c9": c9,
            "date": date,
        }
        contents = "Generate me an image which is suitable for a short story titled: " + DataStore.data.get("h5","Sample Heading") + ". The size of the image MUST NOT exceed 512x512. The orientation must be landscape (not potrait)."
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                try:
                    image = Image.open(BytesIO(part.inline_data.data))
                    # Ensure image is saved in the correct static folder path
                    static_folder = os.path.join(app.root_path, 'static')
                    if not os.path.exists(static_folder):
                        os.makedirs(static_folder)  # Create static folder if it doesn't exist
                    image.save(os.path.join(static_folder, 'generated_image.png'))  # Save the image to the static folder
                    print("Image saved successfully")
                except Exception as e:
                    print(f"Error saving image: {e}")
            else:
                print("No image data found")
        return "Data saved successfully"
    return "Bad API key"

@app.route('/')
def home():
    heading1 = DataStore.data.get("h1", "Sample heading")
    content1 = DataStore.data.get("c1", "Sample Description")
    heading2 = DataStore.data.get("h2", "Sample heading")
    content2 = DataStore.data.get("c2", "Sample Description")
    heading3 = DataStore.data.get("h3", "Sample heading")
    content3 = DataStore.data.get("c3", "Sample Description")
    heading4 = DataStore.data.get("h4", "Sample heading")
    content4 = DataStore.data.get("c4", "Sample Description")
    heading5 = DataStore.data.get("h5", "Sample heading")
    content5 = DataStore.data.get("c5", "Sample Description")
    heading6 = DataStore.data.get("h6", "Sample heading")
    content6 = DataStore.data.get("c6", "Sample Description")
    heading7 = DataStore.data.get("h7", "Sample heading")
    content7 = DataStore.data.get("c7", "Sample Description")
    heading8 = DataStore.data.get("h8", "Sample heading")
    content8 = DataStore.data.get("c8", "Sample Description")
    heading9 = DataStore.data.get("h9", "Sample heading")
    content9 = DataStore.data.get("c9", "Sample Description")
    return render_template("index.html",
    h1 = heading1, d1 = content1.replace("<p>","").replace("</p>","")[:100],
    h2 = heading2, d2 = content2.replace("<p>","").replace("</p>","")[:100],
    h3 = heading3, d3 = content3.replace("<p>","").replace("</p>","")[:100],
    h4 = heading4, d4 = content4.replace("<p>","").replace("</p>","")[:100],
    h5 = heading5, d5 = content5.replace("<p>","").replace("</p>","")[:200],
    h6 = heading6, d6 = content6.replace("<p>","").replace("</p>","")[:100],
    h7 = heading7, d7 = content7.replace("<p>","").replace("</p>","")[:100],
    h8 = heading8, d8 = content8.replace("<p>","").replace("</p>","")[:100],
    h9 = heading9, d9 = content9.replace("<p>","").replace("</p>","")[:100])

@app.route('/article/<number>')
def article(number):
    try:
        n = int(number)
    except ValueError:
        abort(404)
    if((n <= 0 or n >= 10)):
        abort(404)
    heading1 = DataStore.data.get("h1", "Sample heading")
    content1 = DataStore.data.get("c1", "Sample Description")
    heading2 = DataStore.data.get("h2", "Sample heading")
    content2 = DataStore.data.get("c2", "Sample Description")
    heading3 = DataStore.data.get("h3", "Sample heading")
    content3 = DataStore.data.get("c3", "Sample Description")
    heading4 = DataStore.data.get("h4", "Sample heading")
    content4 = DataStore.data.get("c4", "Sample Description")
    heading5 = DataStore.data.get("h5", "Sample heading")
    content5 = DataStore.data.get("c5", "Sample Description")
    heading6 = DataStore.data.get("h6", "Sample heading")
    content6 = DataStore.data.get("c6", "Sample Description")
    heading7 = DataStore.data.get("h7", "Sample heading")
    content7 = DataStore.data.get("c7", "Sample Description")
    heading8 = DataStore.data.get("h8", "Sample heading")
    content8 = DataStore.data.get("c8", "Sample Description")
    heading9 = DataStore.data.get("h9", "Sample heading")
    content9 = DataStore.data.get("c9", "Sample Description")
    date = DataStore.data.get("date", "Not given")
    if(n==1):
        return render_template("article.html", h=heading1, c=content1, date=date)
    elif(n==2):
        return render_template("article.html", h=heading2, c=content2, date=date)
    elif(n==3):
        return render_template("article.html", h=heading3, c=content3, date=date)
    elif(n==4):
        return render_template("article.html", h=heading4, c=content4, date=date)
    elif(n==5):
        return render_template("article.html", h=heading5, c=content5, date=date)
    elif(n==6):
        return render_template("article.html", h=heading6, c=content6, date=date)
    elif(n==7):
        return render_template("article.html", h=heading7, c=content7, date=date)
    elif(n==8):
        return render_template("article.html", h=heading8, c=content8, date=date)
    elif(n==9):
        return render_template("article.html", h=heading9, c=content9, date=date)
    else:
        return "Invalid input"

@app.route('/generate_image')
def thumbnail():
    # Serve the image from the static folder
    return send_file("static/generated_image.png", mimetype='image/png')

@app.route("/trigger/mittentis/")
def mitt():
    x = datetime.datetime.now()

    datee = str(x.strftime("%Y") + "/" + x.strftime("%m") + "/" + x.strftime("%d"))

    client = genai.Client(api_key="API_KEY")
    def send_ai_req(client, short_story, genre):
        prompt = """You are an exceptional short story writer with mastery in the genre of """+genre+""". Your stories captivate readers by seamlessly blending compelling characters, vivid settings, and thought-provoking themes. Below is one of your short stories (the given short story may not be necessary to be of the same genre you are going to write ("""+genre+"""):
        """+short_story+"""
        Your task is to craft another short story in the same genre. Ensure the new story:
        1. Engages the reader immediately by starting in medias res (in the middle of the action) or with a striking hook.
        2. Focuses on one central narrative with limited characters and a concise setting, as is typical for short stories.
        3. Includes literary devices such as imagery, symbolism, foreshadowing, and metaphors to enrich the prose and evoke emotion.
        4. Explores a theme that resonates universally while remaining true to the genre conventions.
        5.Ends with impact, whether through resolution, ambiguity, or an unexpected twist that leaves readers reflecting on the story’s meaning.
        6. Do not give a title to the short story
        7. If the genre you are going to write is Shakespearean, remember to use Shakespeare's signature words and phrases and DO NOT WRITE IN NORMAL ENGLISH, WRITE MUCH OF IT AS SHAKESPEARE WOULD HAVE WRITTEN

        Output Requirements:
        1. Write the story in plain text without headings such as introductions, conclusions, or formatting.
        2. Avoid summarizing or explaining elements of the story; let them unfold naturally within the narrative.
        3. Maintain originality and creativity while adhering to the genre’s expectations.
        4. Analyse the given short story's vocabulary and opening and closing. Try to make your short story like the given one.
        5. The word count must not exceed 1000 words"""
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return(response.text)

    def get_title(client, short_story, genre):
        prompt = """Give a suitable heading for the below short story which is of genre"""+genre+""". The short story: """+short_story + ". Do not give me choices just give me the title of the short story which will suit the best. Do not add introduction and conclusions to your response such as 'Here is a title: '"""
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return(response.text)

    short_story = """A SAMPLE SHORT STORY"""


    ###########################################MYSTERY###########################################

    content = send_ai_req(client, short_story, "Mystery")

    c1 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h1 = get_title(client, content, "Mystery")

    print("Done: ")
    time.sleep(10)
    ##################################END MYSTERY###########################################


    ###########################################ROMANCE###########################################

    content = send_ai_req(client, short_story, "Romance")

    c2 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h2 = get_title(client, content, "Romance")
    print("Done: ")
    time.sleep(10)
    ##################################END ROMANCE###########################################

    ###########################################FANTASY###########################################
    content = send_ai_req(client, short_story, "Fantasy")

    c3 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h3 = get_title(client, content, "Fantasy")
    print("Done")
    time.sleep(10)
    ##################################END FANTASY###########################################

    ##################################SCINCE FICTION###########################################

    content = send_ai_req(client, short_story, "Science Fiction")

    c4 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h4 = get_title(client, content, "Science Fiction")
    print("Done")
    time.sleep(10)
    ##################################END SCINCE FICTION###########################################

    ##################################HORROR###########################################
    content = send_ai_req(client, short_story, "Horror")

    c5 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h5 = get_title(client, content, "Horror")
    print("Done")
    time.sleep(10)
    ##################################END HORROR###########################################

    ##################################HISTORICAL FICTION###########################################
    content = send_ai_req(client, short_story, "Historical Fiction")

    c6 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h6 = get_title(client, content, "Historical Fiction")
    print("Done")
    time.sleep(10)
    ##################################END HISTORICAL FICTION###########################################

    ##################################DYSTOPIAN###########################################

    content = send_ai_req(client, short_story, "Dystopian")

    c7 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h7 = get_title(client, content, "Dystopian")
    print("Done")
    time.sleep(10)
    ##################################END DYSTOPIAN###########################################
    ##################################FLASH FICTION###########################################
    content = send_ai_req(client, short_story, "Flash Fiction")

    c9 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h9 = get_title(client, content, "Flash Fiction")
    ##################################END FLASH FICTION###########################################

    ##################################SHAKESPEREAN###########################################
    short_story = """A DEMO SHAKESPEAREAN SHORT STORY"""
    content = send_ai_req(client, short_story, "Shakespearean")

    c8 = markdown.markdown(content, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.attr_list'
    ])

    h8 = get_title(client, content, "Shakespearean")

    print("Done")
    time.sleep(10)
    ##################################END SHAKESPEAREAN###########################################



    url = 'https://mittentisai.pythonanywhere.com/upload/hello'
    myobj = {'h1': h1, 'c1': c1,
    'h2': h2, 'c2': c2,
    'h3': h3, 'c3': c3,
    'h4': h4, 'c4': c4,
    'h5': h5, 'c5': c5,
    'h6': h6, 'c6': c6,
    'h7': h7, 'c7': c7,
    'h8': h8, 'c8': c8,
    'h9': h9, 'c9': c9,
    'date': datee,}

    x = requests.post(url, json = myobj)
    return "ok"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
