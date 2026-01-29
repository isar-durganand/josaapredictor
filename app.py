"""
JoSAA College Predictor - Enhanced Flask Application
Multi-page architecture with stunning UI and advanced filtering features.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    print("WARNING: GEMINI_API_KEY not found in .env file")
    model = None

app = Flask(__name__)

# Data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cutoff-data-2025')
MARKS_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marks-rank-percentile', 'marks-rank-percentile.csv')

# Dictionary to store DataFrames for each round
data_frames = {}
marks_df = None

def load_data():
    """Load all 6 round CSV files into memory and marks data."""
    global data_frames, marks_df

    for round_num in range(1, 7):
        file_path = os.path.join(DATA_DIR, f'josaa_cutoff_data_2025_round{round_num}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Clean the Closing Rank column - remove 'P' suffix for PwD ranks and convert to numeric
            df['Closing Rank Numeric'] = df['Closing Rank'].astype(str).str.replace('P', '', regex=False)
            df['Closing Rank Numeric'] = pd.to_numeric(df['Closing Rank Numeric'], errors='coerce')
            df['Opening Rank Numeric'] = df['Opening Rank'].astype(str).str.replace('P', '', regex=False)
            df['Opening Rank Numeric'] = pd.to_numeric(df['Opening Rank Numeric'], errors='coerce')
            data_frames[round_num] = df
            print(f"Loaded Round {round_num}: {len(df)} records")

    if os.path.exists(MARKS_DATA_FILE):
        marks_df = pd.read_csv(MARKS_DATA_FILE)
        print("Loaded Marks vs Rank data")


def get_institute_type(institute_name):
    """Determine the institute type from its name."""
    name = institute_name.upper()
    
    # Check for IIT first (most specific)
    if name.startswith('IIT') or 'INDIAN INSTITUTE OF TECHNOLOGY' in name:
        return 'IIT'
    
    # Check for IIIT (before NIT to avoid 'IIIT' matching 'NIT')
    if 'IIIT' in name or 'INDIAN INSTITUTE OF INFORMATION TECHNOLOGY' in name:
        return 'IIIT'
    
    # Check for NIT - matches "NIT ", "NIT,", starts with "NIT", or full name
    # This catches: "NIT Agartala", "Malaviya NIT Jaipur", "Dr. B R Ambedkar NIT, Jalandhar"
    if ('NIT ' in name or 'NIT,' in name or name.startswith('NIT') or 
        'NATIONAL INSTITUTE OF TECHNOLOGY' in name):
        return 'NIT'
    
    return 'GFTI'

def get_probability(user_rank, closing_rank):
    """Calculate admission probability based on rank difference."""
    if closing_rank is None or pd.isna(closing_rank):
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
    for df in data_frames.values():
        all_categories.update(df['Seat Type'].unique().tolist())
    return sorted(list(all_categories))

def get_unique_quotas():
    """Get unique quotas from all data."""
    all_quotas = set()
    for df in data_frames.values():
        all_quotas.update(df['Quota'].unique().tolist())
    return sorted(list(all_quotas))

def get_unique_programs():
    """Get unique program names from all data."""
    all_programs = set()
    for df in data_frames.values():
        all_programs.update(df['Academic Program Name'].unique().tolist())
    return sorted(list(all_programs))

def get_stats():
    """Get statistics for the landing page."""
    total_records = sum(len(df) for df in data_frames.values())
    unique_institutes = set()
    unique_programs = set()
    for df in data_frames.values():
        unique_institutes.update(df['Institute'].unique().tolist())
        unique_programs.update(df['Academic Program Name'].unique().tolist())
    
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

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest."""
    return app.send_static_file('manifest.json')

@app.route('/rank-predictor')
def rank_predictor():
    """JEE Main Rank & Percentile Predictor page."""
    # Data for the table
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
            round_num = int(round_num)
            if round_num not in data_frames:
                return jsonify({'error': f'Data for Round {round_num} not available', 'results': []})
            rounds_to_process = [round_num]
        
        all_results = []
        
        for rnd in rounds_to_process:
            df = data_frames[rnd].copy()
            df['Round'] = rnd
            
            # Filter by category (seat type)
            if category != 'ALL':
                df = df[df['Seat Type'] == category]
            
            # Filter by gender
            if gender != 'ALL':
                df = df[df['Gender'].str.contains(gender, case=False, na=False)]
            
            # Filter by quota
            if quota != 'ALL':
                df = df[df['Quota'] == quota]
            
            # Filter by program
            if program != 'ALL':
                df = df[df['Academic Program Name'] == program]
            
            # Filter by institute type
            if institute_type != 'ALL':
                df['Institute Type'] = df['Institute'].apply(get_institute_type)
                df = df[df['Institute Type'] == institute_type]
            
            # Filter where user rank <= closing rank
            df = df[df['Closing Rank Numeric'] >= user_rank]
            
            # Add probability indicator
            df['Probability'] = df['Closing Rank Numeric'].apply(lambda x: get_probability(user_rank, x))
            
            all_results.append(df)
        
        # Combine all results
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            
            # If "All Rounds" selected, keep only the best round for each unique combination
            if round_num == 'ALL':
                # Group by Institute, Program, Quota, Seat Type, Gender and keep the one with highest closing rank
                combined_df = combined_df.sort_values('Closing Rank Numeric', ascending=False)
                combined_df = combined_df.drop_duplicates(
                    subset=['Institute', 'Academic Program Name', 'Quota', 'Seat Type', 'Gender'],
                    keep='first'
                )
            
            # Sort by closing rank (highest first = best chance)
            combined_df = combined_df.sort_values('Closing Rank Numeric', ascending=False)
        else:
            combined_df = pd.DataFrame()
        
        # Prepare results
        results = []
        for _, row in combined_df.iterrows():
            result = {
                'institute': row['Institute'],
                'program': row['Academic Program Name'],
                'quota': row['Quota'],
                'seat_type': row['Seat Type'],
                'gender': row['Gender'],
                'opening_rank': row['Opening Rank'],
                'closing_rank': row['Closing Rank'],
                'probability': row['Probability']
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
    """Handle chat requests with Gemini AI."""
    if not model:
        return jsonify({'response': "AI service is not configured. Please set GEMINI_API_KEY."})

    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', []) # Expect list of {role: 'user'/'model', parts: [text]}

    if not user_message:
        return jsonify({'response': "Please say something!"})

    try:
        # Construct History Context
        history_context = ""
        if history:
            history_context = "Conversation History:\n"
            for msg in history[-5:]:
                role = "User" if msg['role'] == 'user' else "Assistant"
                text = msg['parts'][0] if isinstance(msg['parts'], list) else msg['parts']
                history_context += f"{role}: {text}\n"

        # OPTIMIZATION: Single Prompt for Classification + General Chat
        # If user asks for data -> Return JSON.
        # If user chats generally -> Return simple text answer directly.
        
        system_instruction = """
        You are an intelligent assistant for a College Predictor app.
        
        Analyze the user's query and history.
        
        Scenario 1: DATA QUERY (Cutoffs, Ranks, Predictions)
        If the user asks for cutoffs, rank predictions, or college chances, return a JSON object with the intent and entities. 
        CRITICAL: If a prediction query lacks Rank (or Marks/Percentile) AND Category, return intent "missing_info".
        
        Scenario 2: GENERAL CHAT
        If the user inputs a greeting, asks general questions, or follows up conversationally without needing data, DIRECTLY answer the user in natural language (text). Do NOT return JSON.
        
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
        }
        """
        
        full_prompt = f"{system_instruction}\n{history_context}\nUser Query: {user_message}"
        response = model.generate_content(full_prompt)
        text_response = response.text.strip()
        
        # Check if response is JSON (starts with { and ends with })
        # We use a simple check; if it fails, we treat it as a general text response (1 call!)
        json_pattern =r'\{.*\}'
        match = re.search(json_pattern, text_response, re.DOTALL)
        
        if match:
            # It's a JSON intent! Process it.
            json_str = match.group()
            try:
                parsed_intent = json.loads(json_str)
            except json.JSONDecodeError:
                # Failed to parse JSON, treated as text answer
                return jsonify({'response': text_response.replace('```json', '').replace('```', '')})

            intent = parsed_intent.get('intent')
            entities = parsed_intent.get('entities', {})
            context_data = ""

            if intent == 'missing_info':
                # Optimization: Generate asking question locally or ask Gemini again?
                # Faster to ask Gemini to generate the specific question based on missing fields involves another call.
                # To save calls, we can try to return a template, OR just do the 2nd call.
                # Let's do 2nd call for high quality natural language.
                pass 
                
            elif intent == 'cutoff':
                round_num = entities.get('round') if entities.get('round') else 6
                if round_num not in data_frames: round_num = 6
                df = data_frames[round_num]
                
                filtered_df = df.copy()
                if entities.get('institute'):
                    filtered_df = filtered_df[filtered_df['Institute'].str.contains(entities['institute'], case=False, na=False)]
                if entities.get('program'):
                    filtered_df = filtered_df[filtered_df['Academic Program Name'].str.contains(entities['program'], case=False, na=False)]
                if entities.get('category'):
                    cat_map = {'OPEN': 'OPEN', 'GEN': 'OPEN', 'OBC': 'OBC-NCL', 'SC': 'SC', 'ST': 'ST', 'EWS': 'EWS'}
                    search_cat = cat_map.get(entities['category'].upper(), entities['category'])
                    filtered_df = filtered_df[filtered_df['Seat Type'].str.contains(search_cat, case=False, na=False)]
                if entities.get('rank'):
                     rank = int(entities['rank'])
                     filtered_df = filtered_df[filtered_df['Closing Rank Numeric'] >= rank]
                     filtered_df = filtered_df.sort_values('Closing Rank Numeric')
                
                results = filtered_df.head(10).to_dict('records')
                if not results:
                    context_data = "No matching cutoff data found."
                else:
                    context_data = "Matches (Round 6):\n" + "\n".join([f"- {r['Institute']}, {r['Academic Program Name']}, {r['Seat Type']}, Closing Rank: {r['Closing Rank']}" for r in results])

            elif intent == 'rank_predict':
                if marks_df is not None:
                    context_data = "Reference Data:\n" + marks_df.to_string()
                else:
                    context_data = "Rank data unavailable."

            # Second Call: Generate Answer with Context
            final_prompt = f"""
            System: User asked: "{user_message}".
            Context found:
            {context_data}
            
            Task: Answer the user naturally based on the context. If 'missing_info', ask for missing details.
            """
            final_resp = model.generate_content(final_prompt)
            return jsonify({'response': final_resp.text})
            
        else:
            # It's NOT JSON. It's a direct general answer.
            # We saved a whole API call!
            return jsonify({'response': text_response})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'response': "I encountered an error. Please try again."})


if __name__ == '__main__':
    print("Loading JoSAA 2025 Cutoff Data...")
    load_data()
    print(f"Data loaded successfully! Total rounds available: {len(data_frames)}")
    app.run(debug=True, port=5000)
