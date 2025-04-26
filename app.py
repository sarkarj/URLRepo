import logging
import sqlite3
import requests
import json
from urllib.parse import urlparse
from flask import Flask, render_template, request, flash, redirect
from newspaper import Article
from flask_limiter import Limiter
from decouple import config
from werkzeug.exceptions import BadRequest

# Configuration
app = Flask(__name__)
app.secret_key = config('SECRET_KEY')  # Stored in .env
GEMINI_API_KEY = config('GEMINI_API_KEY')  # Stored in .env

limiter = Limiter(app)

# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',  # Append mode
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Initialize Database 
def init_db():
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS web_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    category TEXT,
                    keyword TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html', records=retrieve_all_records())

@limiter.limit("5 per second")
@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url', '').strip()

    if not is_valid_url(url):
        flash("Invalid URL. Please enter a valid HTTPS web URL.", "error")
        return redirect('/')

    if is_duplicate_url(url):
        flash("Duplicate URL. This URL already exists.", "warning")
    else:
        result = fetch_and_analyze(url)
        if isinstance(result, str):
            flash(result, "error")

    return redirect('/')

@app.route('/delete', methods=['GET'])
def delete():
    url = request.args.get('url')
    if not url:
        flash("Failed to delete bookmark: URL is missing", "error")
        return redirect('/')

    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM web_data WHERE url = ?', (url,))
            conn.commit()
        flash("Bookmark deleted successfully", "success")
    except sqlite3.Error as e:
        logging.error(f"Delete failed for URL {url}: {e}")
        flash("Failed to delete bookmark", "error")

    return redirect('/')

# Utility Functions
def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme == 'https' and bool(parsed.netloc)
    except Exception as e:
        logging.warning(f"URL validation failed: {e}")
        return False

def is_duplicate_url(url):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM web_data WHERE url = ?', (url,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logging.error(f"Duplicate check failed: {e}")
        return False

def fetch_and_analyze(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        content = article.text[:6000]  # Gemini input cap

        category, keyword = call_gemini(content)

        if save_to_database(url, category, keyword):
            return "Success"
        else:
            return "Error while saving to the database."

    except Exception as e:
        logging.error(f"Article fetch failed for {url}: {e}")
        return "An error occurred while processing the URL."

def call_gemini(content):
    try:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}

        prompt = f"""
Task 1: Summarize the following content precisely and professionally in no more than 200 words.
Task 2: Extract critical keywords (topic, themes, names, places) as a comma-separated list, no more than 50 words.

Content:
{content}
        """

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        response.raise_for_status()

        result = response.json()
        parts = result['candidates'][0]['content']['parts'][0]['text']

        if "Task 2:" in parts:
            summary, keywords = parts.split("Task 2:")
            return summary.replace("Task 1:", "").strip(), keywords.strip()
        else:
            return parts.strip(), ""

    except requests.exceptions.RequestException as e:
        logging.error(f"Gemini API request failed: {e}")
        return "Error calling Gemini", str(e)
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f"Invalid Gemini API response: {e}")
        return "Error processing Gemini response", str(e)

def save_to_database(url, category, keyword):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO web_data (url, category, keyword) VALUES (?, ?, ?)',
                (url, category, keyword)
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        logging.warning(f"Duplicate insertion blocked for URL: {url}")
        return False
    except sqlite3.Error as e:
        logging.error(f"Database insertion error: {e}")
        return False

def retrieve_all_records():
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT url, category, keyword FROM web_data ORDER BY id DESC')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Record fetch error: {e}")
        return []

# Run App
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8085)
