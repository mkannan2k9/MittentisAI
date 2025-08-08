# MittentisAI

***

AI-powered blog that publishes original short stories daily in nine genres, with AI-generated cover images.  Available at: https://mittentisai.pythonanywhere.com/

**Owner:** Kannan Murugapandian  
**License:** MIT

***

## Features

- Publishes 9 AI-written short stories everyday, each in a different genre:
  - Mystery
  - Romance
  - Fantasy
  - Science Fiction
  - Horror
  - Historical Fiction
  - Dystopian
  - Shakespearean
  - Flash Fiction
- Every story is titled by AI and stored for web display.
- Each daily "Horror" story generates an AI illustration as a blog cover image (landscape, max 512x512).
- All web pages are rendered using Jinja2 templates (templates folder).
- Uses Google Gemini API for story, title, and image generation.

***

## Requirements

- Python 3.8+
- pip packages:
  - Flask
  - google-genai (Google AI SDK)
  - Pillow
  - requests
  - gTTS
  - markdown
- Google Gemini API Key (for text and image generation)

***

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/[your-username]/ai-story-blog.git
   cd ai-story-blog
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not provided, install dependencies manually:
   ```bash
   pip install Flask google-genai Pillow requests gTTS markdown
   ```

3. **Add your API key:**
   - Open `flask_app.py`
   - Replace `'API_KEY'` with your actual Google Gemini API key everywhere it appears.

4. **Ensure you have a `templates` directory** in your project folder (containing `index.html` and `article.html`).

***

## Usage

1. **Run the application:**
   ```bash
   python flask_app.py
   ```
2. **Open your browser and visit:**
   ```
   http://localhost:5000/
   ```

- Use `/` to view the homepage with all genres.
- Visit `/article/` (where `` is 1–9) to read the full text in each genre.
- `GET /generate_image` to get the current generated cover image.
- Use `/trigger/mittentis/` (GET) endpoint to trigger a new daily set of stories (typically you may call this with a cron job or manually for development/testing).

***

## File Structure

```
flask_app.py             # Main Flask app
templates/
    index.html           # Homepage template
    article.html         # Story page template
static/
    generated_image.png  # Generated cover image
```

***

## Customization

- To change genres, modify the calls in `/trigger/mittentis/`.
- To adjust length, prompt, or formatting, edit the prompt strings, markdown settings, or Flask routes as needed.

***

## License

MIT License

Copyright (c) 2025 Kannan Murugapandian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

***

## Acknowledgements

- [Google Gemini API](https://ai.google.dev/)
- [Flask](https://flask.palletsprojects.com/)
- [gTTS: Google Text-to-Speech](https://pypi.org/project/gTTS/)
- [Pillow](https://pillow.readthedocs.io/)

***

**For questions or support, contact Kannan Murugapandian.**

***
