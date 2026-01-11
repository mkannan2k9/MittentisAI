# MittentisAI



AI-powered blog that publishes original short stories daily in nine genres, with AI-generated cover images.  
**Live Demo:** [https://mittentisai.pythonanywhere.com/](https://mittentisai.pythonanywhere.com/)

**Owner:** Kannan Murugapandian  
**License:** MIT



## Features

- **Daily Content Generation:** Publishes 9 AI-written short stories every day in distinct genres:
  - Mystery, Romance, Fantasy, Science Fiction, Horror, Historical Fiction, Dystopian, Shakespearean, and Flash Fiction.
- **AI-Powered Assets:**
  - **Stories & Titles:** Generated using Google's **Gemini 2.5 Flash-Lite**.
  - **Cover Art:** Each daily edition generates a thematic cover illustration using **Gemini 2.5 Flash Image** (Nano Banana).
- **Automated Workflow:** A single trigger endpoint generates, formats, and publishes all content.
- **Web Interface:** Clean, responsive reading experience built with Flask and Jinja2.



## Requirements

- Python 3.8+
- **Google Gemini API Key** (Required for all generative features)
- Python Packages:
  - `Flask`
  - `google-genai` (Official Google AI SDK)
  - `Pillow` (Image processing)
  - `requests`
  - `gTTS` (Text-to-Speech support)
  - `markdown`



## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mkannan2k9/MittentisAI.git
   cd mittentis-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Or manually:*
   ```bash
   pip install Flask google-genai Pillow requests gTTS markdown
   ```

3. **Configure your API Key:**
   Open `blog_generator.py` (or `flask_app.py`) and locate the `GOOGLE_API_KEY` variable.
   ```python
   # Replace with your actual key
   GOOGLE_API_KEY = "AIzaSy..." 
   ```
   *(Note: For production, it is recommended to use environment variables).*

4. **Verify Directory Structure:**
   Ensure your project folder looks like this:
   ```
   project/
   ├── blog_generator.py    # Main application file
   ├── templates/           
   │   ├── index.html       # Homepage
   │   └── article.html     # Story reader
   └── static/              # Created automatically for images
   ```



## Usage

1. **Run the application:**
   ```bash
   python blog_generator.py
   ```

2. **Open in Browser:**
   Go to `http://localhost:5000/`

3. **Generate Content (The Trigger):**
   To generate a fresh batch of stories and a new cover image, visit the trigger URL in your browser:
   ```
   http://localhost:5000/trigger/mittentis/
   ```
   *Note: This process takes 3-4 minutes as it generates content sequentially to respect API rate limits.*



## Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | GET | Homepage listing all 9 genres and previews. |
| `/article/<id>` | GET | Read a specific story (ID 1-9). |
| `/generate_image` | GET | Returns the current AI-generated cover image. |
| `/trigger/mittentis/` | GET | **Admin only.** Triggers generation of 9 new stories and cover art. |



## Customization

- **Models:** The app is configured to use `gemini-2.5-flash-lite` for text. You can modify `TEXT_MODEL` in the main script to use other Gemini variants.
- **Genres:** Modify the `genres` list in the `mitt()` function to change the types of stories generated.



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



## Acknowledgements

- [Google Gemini API](https://ai.google.dev/)
- [Flask](https://flask.palletsprojects.com/)
- [gTTS](https://pypi.org/project/gTTS/)



**For questions or support, contact Kannan Murugapandian.**
