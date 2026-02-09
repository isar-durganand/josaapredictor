"""
JoSAA College Predictor - Enhanced Flask Application
Multi-page architecture with stunning UI and advanced filtering features.
Refactored to use built-in csv module for Vercel deployment (no pandas).
Now using OpenRouter API with DeepSeek model for chat.
"""

from flask import Flask, render_template, request, jsonify
import csv
import os
import requests
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-r1-0528:free"

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not found in .env file")

app = Flask(__name__)

# Data directory path - Works for both local and Vercel serverless
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'cutoff-data-2025')
MARKS_DATA_FILE = os.path.join(BASE_DIR, 'marks-rank-percentile', 'marks-rank-percentile.csv')

# Dictionary to store data for each round (list of dicts)
data_frames = {}
marks_data = None


def parse_rank(rank_str):
    """Parse rank string to numeric, handling 'P' suffix for PwD ranks."""
    if rank_str is None:
        return None
    rank_str = str(rank_str).strip().replace('P', '')
    try:
        return int(rank_str)
    except (ValueError, TypeError):
        return None


def load_data():
    """Load all 6 round CSV files into memory and marks data."""
    global data_frames, marks_data

    print(f"Loading data from: {DATA_DIR}")
    print(f"BASE_DIR is: {BASE_DIR}")
    
    for round_num in range(1, 7):
        file_path = os.path.join(DATA_DIR, f'josaa_cutoff_data_2025_round{round_num}.csv')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = []
                for row in reader:
                    # Add numeric versions of ranks
                    row['Closing Rank Numeric'] = parse_rank(row.get('Closing Rank'))
                    row['Opening Rank Numeric'] = parse_rank(row.get('Opening Rank'))
                    records.append(row)
                data_frames[round_num] = records
                print(f"Loaded Round {round_num}: {len(records)} records")
        else:
            print(f"WARNING: File not found: {file_path}")

    if os.path.exists(MARKS_DATA_FILE):
        with open(MARKS_DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            marks_data = list(reader)
            print("Loaded Marks vs Rank data")


def get_institute_type(institute_name):
    """Determine the institute type from its name."""
    name = institute_name.upper()
    
    if name.startswith('IIT') or 'INDIAN INSTITUTE OF TECHNOLOGY' in name:
        return 'IIT'
    
    if 'IIIT' in name or 'INDIAN INSTITUTE OF INFORMATION TECHNOLOGY' in name:
        return 'IIIT'
    
    if ('NIT ' in name or 'NIT,' in name or name.startswith('NIT') or 
        'NATIONAL INSTITUTE OF TECHNOLOGY' in name):
        return 'NIT'
    
    return 'GFTI'


def get_probability(user_rank, closing_rank):
    """Calculate admission probability based on rank difference."""
    if closing_rank is None:
        return 'Unknown'
    
    difference = closing_rank - user_rank
    
    if difference >= 1000:
        return 'Safe'
    elif difference >= 100:
        return 'Moderate'
    else:
        return 'Risky'


def get_unique_categories():
    """Get unique seat types/categories from all data."""
    all_categories = set()
    for records in data_frames.values():
        for row in records:
            if row.get('Seat Type'):
                all_categories.add(row['Seat Type'])
    return sorted(list(all_categories))


def get_unique_quotas():
    """Get unique quotas from all data."""
    all_quotas = set()
    for records in data_frames.values():
        for row in records:
            if row.get('Quota'):
                all_quotas.add(row['Quota'])
    return sorted(list(all_quotas))


def get_unique_programs():
    """Get unique program names from all data."""
    all_programs = set()
    for records in data_frames.values():
        for row in records:
            if row.get('Academic Program Name'):
                all_programs.add(row['Academic Program Name'])
    return sorted(list(all_programs))


def get_stats():
    """Get statistics for the landing page."""
    total_records = sum(len(records) for records in data_frames.values())
    unique_institutes = set()
    unique_programs = set()
    for records in data_frames.values():
        for row in records:
            if row.get('Institute'):
                unique_institutes.add(row['Institute'])
            if row.get('Academic Program Name'):
                unique_programs.add(row['Academic Program Name'])
    
    return {
        'total_records': total_records,
        'unique_institutes': len(unique_institutes),
        'unique_programs': len(unique_programs),
        'rounds': len(data_frames)
    }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page."""
    stats = get_stats()
    return render_template('index.html', stats=stats)


@app.route('/predictor')
def predictor():
    """College predictor tool page."""
    categories = get_unique_categories()
    quotas = get_unique_quotas()
    programs = get_unique_programs()
    return render_template('predictor.html', categories=categories, quotas=quotas, programs=programs)


@app.route('/about')
def about():
    """About page."""
    stats = get_stats()
    return render_template('about.html', stats=stats)


@app.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


@app.route('/cutoffs')
def cutoffs():
    """JEE Main Cutoff Details page."""
    return render_template('cutoffs.html')


@app.route('/privacy')
def privacy():
    """Privacy Policy page - Required for Google AdSense."""
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    """Terms of Service page - Required for Google AdSense."""
    return render_template('terms.html')


@app.route('/sitemap.xml')
def sitemap():
    """Serve XML sitemap for search engines."""
    return app.send_static_file('sitemap.xml')


@app.route('/robots.txt')
def robots():
    """Serve robots.txt for search engines."""
    return app.send_static_file('robots.txt')


# ==================== BLOG ROUTES ====================

def load_institutes():
    """Load institute data from JSON file."""
    institutes_file = os.path.join(BASE_DIR, 'data', 'institutes.json')
    if os.path.exists(institutes_file):
        with open(institutes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('institutes', [])
    return []


@app.route('/blog')
def blog():
    """Blog listing page with all IIT and NIT guides."""
    institutes = load_institutes()
    return render_template('blog.html', institutes=institutes)


@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post for each institute."""
    institutes = load_institutes()
    
    # Find the institute by slug
    institute = None
    for inst in institutes:
        if inst['slug'] == slug:
            institute = inst
            break
    
    if not institute:
        return render_template('404.html'), 404
    
    # Get related institutes (same type, different slug)
    related = [i for i in institutes if i['type'] == institute['type'] and i['slug'] != slug][:3]
    
    return render_template('blog_post.html', institute=institute, related_institutes=related)


@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest."""
    return app.send_static_file('manifest.json')


@app.route('/rank-predictor')
def rank_predictor():
    """JEE Main Rank & Percentile Predictor page."""
    data = [
        {"marks": "281 - 300", "percentile": "99.99989145 - 100", "rank": "1 - 20"},
        {"marks": "271 - 280", "percentile": "99.994681 - 99.997394", "rank": "24 - 80"},
        {"marks": "263 - 270", "percentile": "99.990990 - 99.994029", "rank": "55 - 83"},
        {"marks": "250 - 262", "percentile": "99.977205 - 99.988819", "rank": "85 - 210"},
        {"marks": "241 - 250", "percentile": "99.960163 - 99.975034", "rank": "215 - 367"},
        {"marks": "231 - 240", "percentile": "99.934980 - 99.956364", "rank": "375 - 599"},
        {"marks": "221 - 230", "percentile": "99.901113 - 99.928901", "rank": "610 - 911"},
        {"marks": "211 - 220", "percentile": "99.851616 - 99.893732", "rank": "920 - 1,367"},
        {"marks": "201 - 210", "percentile": "99.795063 - 99.845212", "rank": "1,375 - 1,888"},
        {"marks": "191 - 200", "percentile": "99.710831 - 99.782472", "rank": "1,900 - 2,664"},
        {"marks": "181 - 190", "percentile": "99.597399 - 99.688579", "rank": "2,700 - 3,710"},
        {"marks": "171 - 180", "percentile": "99.456939 - 99.573193", "rank": "3,800 - 5,003"},
        {"marks": "161 - 170", "percentile": "99.272084 - 99.431214", "rank": "5,100 - 6,706"},
        {"marks": "151 - 160", "percentile": "99.028614 - 99.239737", "rank": "6,800 - 8,949"},
        {"marks": "141 - 150", "percentile": "98.732389 - 98.990296", "rank": "9,000 - 11,678"},
        {"marks": "131 - 140", "percentile": "98.317414 - 98.666935", "rank": "11,800 - 15,501"},
        {"marks": "121 - 130", "percentile": "97.811260 - 98.254132", "rank": "15,700 - 20,164"},
        {"marks": "111 - 120", "percentile": "97.142937 - 97.685672", "rank": "20,500 - 26,321"},
        {"marks": "101 - 110", "percentile": "96.204550 - 96.978272", "rank": "26,500 - 34,966"},
        {"marks": "91 - 100", "percentile": "94.998594 - 96.064850", "rank": "35,000 - 46,076"},
        {"marks": "81 - 90", "percentile": "93.471231 - 94.749479", "rank": "46,500 - 60,147"},
        {"marks": "71 - 80", "percentile": "91.072128 - 93.152971", "rank": "61,000 - 82,249"},
        {"marks": "61 - 70", "percentile": "87.512225 - 90.702200", "rank": "83,000 - 1,15,045"},
        {"marks": "51 - 60", "percentile": "82.016062 - 86.907944", "rank": "1,17,000 - 1,65,679"},
        {"marks": "41 - 50", "percentile": "73.287808 - 80.982153", "rank": "1,66,000 - 2,46,089"},
        {"marks": "31 - 40", "percentile": "58.151490 - 71.302052", "rank": "2,64,383 - 3,85,534"},
    ]
    return render_template('rank_predictor.html', data=data)


@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests."""
    try:
        # Get form data
        round_num = request.form.get('round', '6')
        institute_type = request.form.get('institute_type', 'ALL')
        category = request.form.get('category', 'OPEN')
        gender = request.form.get('gender', 'Gender-Neutral')
        quota = request.form.get('quota', 'AI')
        program = request.form.get('program', 'ALL')
        user_rank = int(request.form.get('rank', 0))
        
        if user_rank <= 0:
            return jsonify({'error': 'Please enter a valid rank greater than 0', 'results': []})
        
        # Determine which rounds to process
        if round_num == 'ALL':
            rounds_to_process = list(data_frames.keys())
        else:
            round_num_int = int(round_num)
            if round_num_int not in data_frames:
                return jsonify({'error': f'Data for Round {round_num_int} not available', 'results': []})
            rounds_to_process = [round_num_int]
        
        all_results = []
        
        for rnd in rounds_to_process:
            records = data_frames[rnd]
            
            for row in records:
                # Create a copy for this result
                result_row = dict(row)
                result_row['Round'] = rnd
                
                # Filter by category (seat type)
                if category != 'ALL' and result_row.get('Seat Type') != category:
                    continue
                
                # Filter by gender
                if gender != 'ALL':
                    row_gender = result_row.get('Gender', '')
                    if gender.lower() not in row_gender.lower():
                        continue
                
                # Filter by quota
                if quota != 'ALL' and result_row.get('Quota') != quota:
                    continue
                
                # Filter by program
                if program != 'ALL' and result_row.get('Academic Program Name') != program:
                    continue
                
                # Filter by institute type
                if institute_type != 'ALL':
                    row_inst_type = get_institute_type(result_row.get('Institute', ''))
                    if row_inst_type != institute_type:
                        continue
                
                # Filter where user rank <= closing rank
                closing_rank_num = result_row.get('Closing Rank Numeric')
                if closing_rank_num is None or closing_rank_num < user_rank:
                    continue
                
                # Add probability indicator
                result_row['Probability'] = get_probability(user_rank, closing_rank_num)
                
                all_results.append(result_row)
        
        # If "All Rounds" selected, keep only the best round for each unique combination
        if round_num == 'ALL':
            # Sort by closing rank descending first
            all_results.sort(key=lambda x: x.get('Closing Rank Numeric') or 0, reverse=True)
            
            # Keep only first occurrence of each unique combination
            seen = set()
            unique_results = []
            for row in all_results:
                key = (row.get('Institute'), row.get('Academic Program Name'), 
                       row.get('Quota'), row.get('Seat Type'), row.get('Gender'))
                if key not in seen:
                    seen.add(key)
                    unique_results.append(row)
            all_results = unique_results
        
        # Sort by closing rank (highest first = best chance)
        all_results.sort(key=lambda x: x.get('Closing Rank Numeric') or 0, reverse=True)
        
        # Prepare results
        results = []
        for row in all_results:
            result = {
                'institute': row.get('Institute'),
                'program': row.get('Academic Program Name'),
                'quota': row.get('Quota'),
                'seat_type': row.get('Seat Type'),
                'gender': row.get('Gender'),
                'opening_rank': row.get('Opening Rank'),
                'closing_rank': row.get('Closing Rank'),
                'probability': row.get('Probability')
            }
            if 'Round' in row:
                result['round'] = int(row['Round'])
            results.append(result)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'user_rank': user_rank
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid input. Please enter valid numeric values.', 'results': []})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e), 'results': []})


@app.route('/api/categories')
def api_categories():
    """API endpoint to get all categories."""
    categories = get_unique_categories()
    return jsonify(categories)


@app.route('/api/quotas')
def api_quotas():
    """API endpoint to get all quotas."""
    quotas = get_unique_quotas()
    return jsonify(quotas)


@app.route('/api/programs')
def api_programs():
    """API endpoint to get all program names."""
    programs = get_unique_programs()
    return jsonify(programs)


@app.route('/api/stats')
def api_stats():
    """API endpoint to get statistics."""
    stats = get_stats()
    return jsonify(stats)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with OpenRouter AI (DeepSeek)."""
    if not OPENROUTER_API_KEY:
        return jsonify({'response': "AI service is not configured. Please set OPENROUTER_API_KEY."})

    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])

    if not user_message:
        return jsonify({'response': "Please say something!"})

    def call_openrouter(messages):
        """Call OpenRouter API and return response text."""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://josaacollegepredictor.vercel.app",
            "X-Title": "JoSAA College Predictor"
        }
        payload = {
            "model": MODEL,
            "messages": messages
        }
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return None

    try:
        # Construct messages for OpenRouter
        messages = []
        
        system_instruction = """You are a friendly, helpful assistant for a JoSAA College Predictor app. You help students with JEE counseling, college predictions, cutoff queries, and general guidance.

Analyze the user's query:

Scenario 1: DATA QUERY (Cutoffs, Ranks, Predictions)
If the user asks for cutoffs, rank predictions, or college chances, return a JSON object with the intent and entities. 
CRITICAL: If a prediction query lacks Rank (or Marks/Percentile) AND Category, return intent "missing_info".

Scenario 2: GENERAL CHAT
If the user inputs a greeting, asks general questions, or follows up conversationally without needing data, DIRECTLY answer the user in natural language. Be friendly and encouraging. Do NOT return JSON.

JSON Structure (only for Scenario 1):
{
    "intent": "cutoff" | "rank_predict" | "missing_info",
    "entities": {
        "institute": "string or null",
        "program": "string or null",
        "category": "string or null",
        "rank": "integer or null",
        "marks": "integer or null",
        "percentile": "float or null",
        "round": "integer or null (default 6)"
    },
    "missing_fields": ["rank", "category"] (if intent is missing_info)
}"""

        messages.append({"role": "system", "content": system_instruction})
        
        # Add conversation history (last 5 messages)
        for msg in history[-5:]:
            role = "user" if msg['role'] == 'user' else "assistant"
            text = msg['parts'][0] if isinstance(msg['parts'], list) else msg['parts']
            messages.append({"role": role, "content": text})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        text_response = call_openrouter(messages)
        
        if not text_response:
            return jsonify({'response': "I encountered an error connecting to the AI service. Please try again."})
        
        # Parse response for JSON intent
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text_response, re.DOTALL)
        
        if match:
            json_str = match.group()
            try:
                parsed_intent = json.loads(json_str)
            except json.JSONDecodeError:
                return jsonify({'response': text_response.replace('```json', '').replace('```', '')})

            intent = parsed_intent.get('intent')
            entities = parsed_intent.get('entities', {})
            context_data = ""

            if intent == 'missing_info':
                pass 
                
            elif intent == 'cutoff':
                round_num = entities.get('round') if entities.get('round') else 6
                if round_num not in data_frames:
                    round_num = 6
                records = data_frames.get(round_num, [])
                
                filtered = records[:]
                
                if entities.get('institute'):
                    inst_search = entities['institute'].lower()
                    filtered = [r for r in filtered if inst_search in r.get('Institute', '').lower()]
                
                if entities.get('program'):
                    prog_search = entities['program'].lower()
                    filtered = [r for r in filtered if prog_search in r.get('Academic Program Name', '').lower()]
                
                if entities.get('category'):
                    cat_map = {'OPEN': 'OPEN', 'GEN': 'OPEN', 'OBC': 'OBC-NCL', 'SC': 'SC', 'ST': 'ST', 'EWS': 'EWS'}
                    search_cat = cat_map.get(entities['category'].upper(), entities['category']).lower()
                    filtered = [r for r in filtered if search_cat in r.get('Seat Type', '').lower()]
                
                if entities.get('rank'):
                    rank = int(entities['rank'])
                    filtered = [r for r in filtered if (r.get('Closing Rank Numeric') or 0) >= rank]
                    filtered.sort(key=lambda x: x.get('Closing Rank Numeric') or 0)
                
                results = filtered[:10]
                if not results:
                    context_data = "No matching cutoff data found."
                else:
                    context_data = "Matches (Round 6):\n" + "\n".join([
                        f"- {r.get('Institute')}, {r.get('Academic Program Name')}, {r.get('Seat Type')}, Closing Rank: {r.get('Closing Rank')}" 
                        for r in results
                    ])

            elif intent == 'rank_predict':
                if marks_data:
                    context_data = "Reference Data:\n" + "\n".join([str(row) for row in marks_data[:20]])
                else:
                    context_data = "Rank data unavailable."

            # Get final response with context
            final_messages = [
                {"role": "system", "content": "You are a helpful JoSAA counseling assistant. Answer the user's question based on the provided context. Be friendly and encouraging."},
                {"role": "user", "content": f"User asked: \"{user_message}\"\n\nContext found:\n{context_data}\n\nTask: Answer the user naturally based on the context. If 'missing_info', ask for missing details politely."}
            ]
            final_resp = call_openrouter(final_messages)
            return jsonify({'response': final_resp if final_resp else "I couldn't process that. Please try again."})
            
        else:
            return jsonify({'response': text_response})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'response': "I encountered an error. Please try again."})


# Load data at module level (important for gunicorn/production)
print("Loading JoSAA 2025 Cutoff Data...")
load_data()
print(f"Data loaded successfully! Total rounds available: {len(data_frames)}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
