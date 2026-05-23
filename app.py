from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import re
import os
import requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Import custom modules
from models import ModelManager, functionality_1_generate_text, functionality_2_analyze_sentiment, functionality_3_summarize_text, functionality_4_translate_text, functionality_5_answer_question
from email_tools import functionality_6_generate_reply, functionality_7_generate_subject_lines, functionality_8_edit_email, functionality_9_categorize_email
from outreach_tools import functionality_10_generate_outreach_email, functionality_11_generate_follow_up, functionality_12_generate_cold_email, functionality_13_analyze_lead_fit, functionality_14_generate_outreach_sequence
from analysis_tools import functionality_15_extract_key_points, functionality_16_analyze_sentiment_trend, functionality_17_compare_texts, functionality_18_generate_insights, functionality_19_classify_content
from utils import functionality_20_generate_hashtags, functionality_21_generate_headlines, functionality_22_rewrite_text, functionality_23_generate_call_to_action, functionality_24_generate_meta_description
from terminal import functionality_25_generate_sales_pitch, functionality_26_generate_pricing_strategy, functionality_27_generate_marketing_copy, functionality_28_analyze_competitor, functionality_29_generate_testimonials, TerminalInterface, AITestingFramework
from bash_terminal import BashTerminal, session_manager

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')

# Hugging Face Configuration
HF_TOKEN = os.getenv('HUGGING_FACE_TOKEN', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Initialize Model Manager
print("Loading models...")
model_manager = ModelManager()
print("Models loaded!")

def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())

@app.route('/')
def index():
    return render_template('index.html', authenticated='credentials' in session)

@app.route('/auth/login')
def auth_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return jsonify({'error': 'Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env'}), 500
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/userinfo.email']
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/auth/callback')
def auth_callback():
    state = session.get('state')
    if not state:
        return redirect(url_for('index'))
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/userinfo.email']
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500

@app.route('/auth/logout')
def auth_logout():
    session.pop('credentials', None)
    return redirect(url_for('index'))

@app.route('/auth/status')
def auth_status():
    return jsonify({'authenticated': 'credentials' in session})

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send email via Gmail API."""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated. Please login with Google.'}), 401
    
    data = request.json
    to = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    
    if not to or not subject or not body:
        return jsonify({'error': 'Missing required fields: to, subject, body'}), 400
    
    try:
        creds = Credentials(**session['credentials'])
        service = build('gmail', 'v1', credentials=creds)
        
        message = f"From: me\nTo: {to}\nSubject: {subject}\n\n{body}"
        import base64
        encoded_message = base64.urlsafe_b64encode(message.encode()).decode()
        
        sent = service.users().messages().send(userId='me', body={'raw': encoded_message}).execute()
        return jsonify({'success': True, 'message_id': sent.get('id')})
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@app.route('/api/compose', methods=['POST'])
def compose_email():
    """Generate email using Hugging Face model."""
    data = request.json
    topic = data.get('topic', '')
    tone = data.get('tone', 'Professional')
    recipient = data.get('recipient', '')
    key_points = data.get('key_points', '')
    
    if not topic or not key_points:
        return jsonify({'error': 'Please provide both a topic and key points.'}), 400
    
    try:
        result = functionality_1_generate_text(
            f"Subject: {topic}\n\nTo: {recipient}\n\nTone: {tone}\n\nKey points: {key_points}\n\nEmail:",
            max_length=400
        )
        email_body = result[0].split("Email:")[-1].strip()
        return jsonify({'email': email_body if email_body else "Could not generate email. Please try again."})
    except Exception as e:
        return jsonify({'error': f"Error generating email: {str(e)}"}), 500

@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of email text."""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Please provide text to analyze'}), 400
    
    try:
        result = functionality_2_analyze_sentiment(text)
        label = max(result, key=result.get)
        score = result[label]
        sentiment = "Positive" if label == "POSITIVE" else "Negative"
        return jsonify({'sentiment': sentiment, 'confidence': score})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_email():
    """Summarize long email text."""
    data = request.json
    text = data.get('text', '')
    
    if not text or len(text) < 100:
        return jsonify({'error': 'Please provide a longer email to summarize (min 100 characters).'}), 400
    
    try:
        result = summarizer(text, max_length=150, min_length=30)
        return jsonify({'summary': result[0]['summary_text']})
    except Exception as e:
        return jsonify({'error': f"Error summarizing: {str(e)}"}), 500

@app.route('/api/abtest', methods=['POST'])
def ab_test_email():
    """Generate two email variants for A/B testing."""
    data = request.json
    topic = data.get('topic', '')
    recipient = data.get('recipient', '')
    key_points = data.get('key_points', '')
    
    if not topic or not key_points:
        return jsonify({'error': 'Please provide topic and key points'}), 400
    
    prompt_a = f"Subject: {topic}\n\nTo: {recipient}\n\nVariant A: Professional tone\n\nKey points: {key_points}\n\nEmail:"
    prompt_b = f"Subject: {topic}\n\nTo: {recipient}\n\nVariant B: Conversational tone\n\nKey points: {key_points}\n\nEmail:"
    
    try:
        result_a = composer(prompt_a, max_length=350, num_return_sequences=1, temperature=0.8)
        result_b = composer(prompt_b, max_length=350, num_return_sequences=1, temperature=0.8)
        
        email_a = result_a[0]['generated_text'].split("Email:")[-1].strip()
        email_b = result_b[0]['generated_text'].split("Email:")[-1].strip()
        
        return jsonify({
            'variant_a': email_a or "Could not generate variant A",
            'variant_b': email_b or "Could not generate variant B"
        })
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/api/improve', methods=['POST'])
def improve_tone():
    """Improve or change the tone of existing email text."""
    data = request.json
    text = data.get('text', '')
    target_tone = data.get('target_tone', 'More Professional')
    
    if not text:
        return jsonify({'error': 'Please provide email text to improve.'}), 400
    
    prompt = f"Original email:\n{text}\n\nRewrite with {target_tone} tone:\n"
    
    try:
        result = composer(prompt, max_length=400, num_return_sequences=1, temperature=0.6)
        improved = result[0]['generated_text'].split("Rewrite with")[-1].split(":")[-1].strip()
        return jsonify({'improved': improved if improved else "Could not improve tone. Please try again."})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/api/research-lead', methods=['POST'])
def research_lead():
    """Research a lead and generate outreach email."""
    data = request.json
    company = data.get('company', '')
    industry = data.get('industry', '')
    role = data.get('role', '')
    pain_points = data.get('pain_points', '')
    
    if not company or not industry:
        return jsonify({'error': 'Please provide company and industry.'}), 400
    
    prompt = f"Research {company} in {industry} industry. Target role: {role}. Pain points: {pain_points}. Generate personalized outreach email with:\n1. Personalized opening\n2. Value proposition\n3. Call to action\n\nEmail:"
    
    try:
        result = composer(prompt, max_length=500, num_return_sequences=1, temperature=0.7)
        email = result[0]['generated_text'].split("Email:")[-1].strip()
        return jsonify({'email': email if email else "Could not generate outreach email."})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/api/batch-outreach', methods=['POST'])
def batch_outreach():
    """Generate outreach emails for multiple leads."""
    data = request.json
    leads = data.get('leads', [])
    template = data.get('template', '')
    
    if not leads:
        return jsonify({'error': 'Please provide leads list.'}), 400
    
    emails = []
    for lead in leads:
        company = lead.get('company', '')
        name = lead.get('name', '')
        prompt = f"Generate outreach email to {name} at {company}. Template: {template}\n\nEmail:"
        
        try:
            result = composer(prompt, max_length=400, num_return_sequences=1, temperature=0.7)
            email = result[0]['generated_text'].split("Email:")[-1].strip()
            emails.append({
                'lead': lead,
                'email': email if email else "Could not generate email"
            })
        except Exception as e:
            emails.append({
                'lead': lead,
                'email': f"Error: {str(e)}"
            })
    
    return jsonify({'emails': emails})

@app.route('/api/analyze-lead', methods=['POST'])
def analyze_lead():
    """Analyze lead information for outreach strategy."""
    data = request.json
    lead_info = data.get('lead_info', '')
    
    if not lead_info:
        return jsonify({'error': 'Please provide lead information.'}), 400
    
    prompt = f"Analyze this lead for outreach strategy: {lead_info}\n\nProvide:\n1. Best contact approach\n2. Key talking points\n3. Potential objections\n4. Recommended follow-up timing\n\nAnalysis:"
    
    try:
        result = composer(prompt, max_length=400, num_return_sequences=1, temperature=0.6)
        analysis = result[0]['generated_text'].split("Analysis:")[-1].strip()
        return jsonify({'analysis': analysis if analysis else "Could not generate analysis."})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/api/appraise-repo', methods=['POST'])
def appraise_repo():
    """Appraise a GitHub repository."""
    data = request.json
    repo_url = data.get('repo_url', '')
    
    if not repo_url:
        return jsonify({'error': 'Please provide a GitHub repository URL.'}), 400
    
    # Extract owner and repo from URL
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        return jsonify({'error': 'Invalid GitHub repository URL.'}), 400
    
    owner, repo = match.groups()
    
    try:
        # Fetch repo data from GitHub API
        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        repo_response = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers)
        if repo_response.status_code != 200:
            return jsonify({'error': f'Failed to fetch repository: {repo_response.status_code}'}), 400
        
        repo_data = repo_response.json()
        
        # Fetch additional data
        languages_response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/languages', headers=headers)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        contributors_response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=10', headers=headers)
        contributors = contributors_response.json() if contributors_response.status_code == 200 else []
        
        # Calculate appraisal metrics
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        watchers = repo_data.get('watchers_count', 0)
        open_issues = repo_data.get('open_issues_count', 0)
        size = repo_data.get('size', 0)
        
        # Calculate engagement score
        engagement_score = (stars * 5) + (forks * 3) + (watchers * 2) - (open_issues * 1)
        engagement_score = max(0, engagement_score)
        
        # Calculate activity score based on recent commits
        activity_score = min(100, (len(contributors) * 10) + (open_issues * 2))
        
        # Calculate technical quality score
        tech_score = min(100, (len(languages) * 15) + (size / 1000))
        
        # Calculate overall value score
        value_score = (engagement_score * 0.4) + (activity_score * 0.3) + (tech_score * 0.3)
        
        # Generate AI appraisal
        repo_info = f"""
        Repository: {repo_data.get('full_name')}
        Description: {repo_data.get('description', 'N/A')}
        Stars: {stars}
        Forks: {forks}
        Open Issues: {open_issues}
        Languages: {', '.join(languages.keys())}
        Contributors: {len(contributors)}
        Created: {repo_data.get('created_at')}
        Updated: {repo_data.get('updated_at')}
        """
        
        prompt = f"Appraise this GitHub repository for business value:\n{repo_info}\n\nProvide:\n1. Technical quality assessment\n2. Market potential\n3. Maintenance effort estimate\n4. Recommended use cases\n5. Estimated development cost to replicate\n\nAppraisal:"
        
        result = functionality_1_generate_text(prompt, max_length=500)
        ai_appraisal = result[0].split("Appraisal:")[-1].strip()
        
        return jsonify({
            'repo_name': repo_data.get('full_name'),
            'description': repo_data.get('description'),
            'stars': stars,
            'forks': forks,
            'open_issues': open_issues,
            'languages': languages,
            'contributors_count': len(contributors),
            'engagement_score': round(engagement_score, 2),
            'activity_score': round(activity_score, 2),
            'tech_score': round(tech_score, 2),
            'value_score': round(value_score, 2),
            'ai_appraisal': ai_appraisal if ai_appraisal else "Could not generate AI appraisal."
        })
    except Exception as e:
        return jsonify({'error': f"Error appraising repository: {str(e)}"}), 500

# Terminal endpoints
@app.route('/api/terminal/create-session', methods=['POST'])
def create_terminal_session():
    """Create a new terminal session."""
    data = request.json
    working_dir = data.get('working_dir', None)
    
    try:
        terminal = session_manager.create_session(working_dir=working_dir)
        return jsonify({
            'success': True,
            'session_id': terminal.session_id,
            'working_directory': terminal.working_dir
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/execute', methods=['POST'])
def execute_terminal_command():
    """Execute a command in terminal session."""
    data = request.json
    session_id = data.get('session_id')
    command = data.get('command')
    
    if not session_id or not command:
        return jsonify({'error': 'Session ID and command required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.execute_command(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/change-directory', methods=['POST'])
def terminal_change_directory():
    """Change working directory in terminal session."""
    data = request.json
    session_id = data.get('session_id')
    path = data.get('path')
    
    if not session_id or not path:
        return jsonify({'error': 'Session ID and path required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.change_directory(path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/list-directory', methods=['POST'])
def terminal_list_directory():
    """List directory contents in terminal session."""
    data = request.json
    session_id = data.get('session_id')
    path = data.get('path', None)
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.list_directory(path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/read-file', methods=['POST'])
def terminal_read_file():
    """Read file in terminal session."""
    data = request.json
    session_id = data.get('session_id')
    path = data.get('path')
    max_lines = data.get('max_lines', 100)
    
    if not session_id or not path:
        return jsonify({'error': 'Session ID and path required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.read_file(path, max_lines)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/write-file', methods=['POST'])
def terminal_write_file():
    """Write file in terminal session."""
    data = request.json
    session_id = data.get('session_id')
    path = data.get('path')
    content = data.get('content')
    overwrite = data.get('overwrite', False)
    
    if not session_id or not path or content is None:
        return jsonify({'error': 'Session ID, path, and content required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.write_file(path, content, overwrite)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/system-info', methods=['POST'])
def terminal_system_info():
    """Get system information from terminal session."""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.get_system_info()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/run-tests', methods=['POST'])
def terminal_run_tests():
    """Run tests via terminal session."""
    data = request.json
    session_id = data.get('session_id')
    test_type = data.get('test_type', 'all')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.run_test_suite(test_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terminal/deploy', methods=['POST'])
def terminal_deploy():
    """Deploy application via terminal session."""
    data = request.json
    session_id = data.get('session_id')
    environment = data.get('environment', 'production')
    platform = data.get('platform', 'huggingface')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    try:
        terminal = session_manager.get_session(session_id)
        if not terminal:
            return jsonify({'error': 'Session not found'}), 404
        
        result = terminal.deploy_application(environment, platform)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
