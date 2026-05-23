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

# Email Tools endpoints
@app.route('/api/generate-reply', methods=['POST'])
def generate_reply():
    """Generate email reply."""
    data = request.json
    original_email = data.get('original_email', '')
    reply_tone = data.get('reply_tone', 'Professional')
    
    if not original_email:
        return jsonify({'error': 'Original email required'}), 400
    
    try:
        result = functionality_6_generate_reply(original_email, reply_tone)
        return jsonify({'reply': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-subject-lines', methods=['POST'])
def generate_subject_lines():
    """Generate subject lines."""
    data = request.json
    email_content = data.get('email_content', '')
    num_variants = data.get('num_variants', 5)
    style = data.get('style', 'Professional')
    
    if not email_content:
        return jsonify({'error': 'Email content required'}), 400
    
    try:
        result = functionality_7_generate_subject_lines(email_content, num_variants, style)
        return jsonify({'subject_lines': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-email', methods=['POST'])
def edit_email():
    """Edit email."""
    data = request.json
    original_email = data.get('original_email', '')
    edit_instruction = data.get('edit_instruction', '')
    preserve_tone = data.get('preserve_tone', True)
    
    if not original_email or not edit_instruction:
        return jsonify({'error': 'Original email and edit instruction required'}), 400
    
    try:
        result = functionality_8_edit_email(original_email, edit_instruction, preserve_tone)
        return jsonify({'edited_email': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categorize-email', methods=['POST'])
def categorize_email():
    """Categorize email."""
    data = request.json
    email_content = data.get('email_content', '')
    categories = data.get('categories', None)
    
    if not email_content:
        return jsonify({'error': 'Email content required'}), 400
    
    try:
        result = functionality_9_categorize_email(email_content, categories)
        return jsonify({'categories': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Outreach Tools endpoints
@app.route('/api/generate-outreach-email', methods=['POST'])
def generate_outreach_email():
    """Generate outreach email."""
    data = request.json
    company_name = data.get('company_name', '')
    industry = data.get('industry', '')
    target_role = data.get('target_role', '')
    pain_points = data.get('pain_points', [])
    value_proposition = data.get('value_proposition', '')
    tone = data.get('tone', 'Professional')
    
    if not company_name or not industry:
        return jsonify({'error': 'Company name and industry required'}), 400
    
    try:
        result = functionality_10_generate_outreach_email(
            company_name, industry, target_role, pain_points, value_proposition, tone
        )
        return jsonify({'email': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-follow-up', methods=['POST'])
def generate_follow_up():
    """Generate follow-up email."""
    data = request.json
    previous_email = data.get('previous_email', '')
    response_status = data.get('response_status', 'No Response')
    days_since_contact = data.get('days_since_contact', 7)
    next_action = data.get('next_action', 'Schedule Call')
    
    if not previous_email:
        return jsonify({'error': 'Previous email required'}), 400
    
    try:
        result = functionality_11_generate_follow_up(previous_email, response_status, days_since_contact, next_action)
        return jsonify({'follow_up': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-cold-email', methods=['POST'])
def generate_cold_email():
    """Generate cold email."""
    data = request.json
    prospect_info = data.get('prospect_info', {})
    personalization_data = data.get('personalization_data', {})
    cta_type = data.get('cta_type', 'Demo Request')
    
    if not prospect_info:
        return jsonify({'error': 'Prospect info required'}), 400
    
    try:
        result = functionality_12_generate_cold_email(prospect_info, personalization_data, cta_type)
        return jsonify({'cold_email': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-lead-fit', methods=['POST'])
def analyze_lead_fit():
    """Analyze lead fit."""
    data = request.json
    lead_info = data.get('lead_info', {})
    ideal_customer_profile = data.get('ideal_customer_profile', {})
    
    if not lead_info:
        return jsonify({'error': 'Lead info required'}), 400
    
    try:
        result = functionality_13_analyze_lead_fit(lead_info, ideal_customer_profile)
        return jsonify({'fit_scores': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-outreach-sequence', methods=['POST'])
def generate_outreach_sequence():
    """Generate outreach sequence."""
    data = request.json
    lead_info = data.get('lead_info', {})
    sequence_length = data.get('sequence_length', 5)
    sequence_type = data.get('sequence_type', 'Standard')
    
    if not lead_info:
        return jsonify({'error': 'Lead info required'}), 400
    
    try:
        result = functionality_14_generate_outreach_sequence(lead_info, sequence_length, sequence_type)
        return jsonify({'sequence': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analysis Tools endpoints
@app.route('/api/extract-key-points', methods=['POST'])
def extract_key_points():
    """Extract key points."""
    data = request.json
    text = data.get('text', '')
    num_points = data.get('num_points', 5)
    summary_type = data.get('summary_type', 'Bullet Points')
    
    if not text:
        return jsonify({'error': 'Text required'}), 400
    
    try:
        result = functionality_15_extract_key_points(text, num_points, summary_type)
        return jsonify({'key_points': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-sentiment-trend', methods=['POST'])
def analyze_sentiment_trend():
    """Analyze sentiment trend."""
    data = request.json
    texts = data.get('texts', [])
    time_labels = data.get('time_labels', None)
    
    if not texts:
        return jsonify({'error': 'Texts required'}), 400
    
    try:
        result = functionality_16_analyze_sentiment_trend(texts, time_labels)
        return jsonify({'trends': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-texts', methods=['POST'])
def compare_texts():
    """Compare texts."""
    data = request.json
    text1 = data.get('text1', '')
    text2 = data.get('text2', '')
    comparison_type = data.get('comparison_type', 'Similarity')
    
    if not text1 or not text2:
        return jsonify({'error': 'Both texts required'}), 400
    
    try:
        result = functionality_17_compare_texts(text1, text2, comparison_type)
        return jsonify({'comparison': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-insights', methods=['POST'])
def generate_insights():
    """Generate insights."""
    data = request.json
    data_text = data.get('data', '')
    insight_type = data.get('insight_type', 'Business')
    context = data.get('context', '')
    
    if not data_text:
        return jsonify({'error': 'Data required'}), 400
    
    try:
        result = functionality_18_generate_insights(data_text, insight_type, context)
        return jsonify({'insights': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classify-content', methods=['POST'])
def classify_content():
    """Classify content."""
    data = request.json
    text = data.get('text', '')
    categories = data.get('categories', [])
    multi_label = data.get('multi_label', False)
    
    if not text or not categories:
        return jsonify({'error': 'Text and categories required'}), 400
    
    try:
        result = functionality_19_classify_content(text, categories, multi_label)
        return jsonify({'classification': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Utils endpoints
@app.route('/api/generate-hashtags', methods=['POST'])
def generate_hashtags():
    """Generate hashtags."""
    data = request.json
    content = data.get('content', '')
    num_hashtags = data.get('num_hashtags', 10)
    hashtag_type = data.get('hashtag_type', 'Relevant')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        result = functionality_20_generate_hashtags(content, num_hashtags, hashtag_type)
        return jsonify({'hashtags': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-headlines', methods=['POST'])
def generate_headlines():
    """Generate headlines."""
    data = request.json
    content = data.get('content', '')
    num_variants = data.get('num_variants', 5)
    headline_style = data.get('headline_style', 'Clickbait')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        result = functionality_21_generate_headlines(content, num_variants, headline_style)
        return jsonify({'headlines': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rewrite-text', methods=['POST'])
def rewrite_text():
    """Rewrite text."""
    data = request.json
    original_text = data.get('original_text', '')
    rewrite_style = data.get('rewrite_style', 'Simplified')
    target_audience = data.get('target_audience', 'General')
    
    if not original_text:
        return jsonify({'error': 'Original text required'}), 400
    
    try:
        result = functionality_22_rewrite_text(original_text, rewrite_style, target_audience)
        return jsonify({'rewritten_text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-cta', methods=['POST'])
def generate_cta():
    """Generate call to action."""
    data = request.json
    context = data.get('context', '')
    action_type = data.get('action_type', 'Sign Up')
    urgency_level = data.get('urgency_level', 'Medium')
    
    if not context:
        return jsonify({'error': 'Context required'}), 400
    
    try:
        result = functionality_23_generate_call_to_action(context, action_type, urgency_level)
        return jsonify({'cta': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-meta-description', methods=['POST'])
def generate_meta_description():
    """Generate meta description."""
    data = request.json
    content = data.get('content', '')
    max_length = data.get('max_length', 160)
    seo_focus = data.get('seo_focus', True)
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        result = functionality_24_generate_meta_description(content, max_length, seo_focus)
        return jsonify({'meta_description': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Terminal/Sales endpoints
@app.route('/api/generate-sales-pitch', methods=['POST'])
def generate_sales_pitch():
    """Generate sales pitch."""
    data = request.json
    product = data.get('product', '')
    target_audience = data.get('target_audience', '')
    key_benefits = data.get('key_benefits', [])
    differentiators = data.get('differentiators', [])
    pitch_length = data.get('pitch_length', 'Medium')
    
    if not product or not target_audience:
        return jsonify({'error': 'Product and target audience required'}), 400
    
    try:
        result = functionality_25_generate_sales_pitch(product, target_audience, key_benefits, differentiators, pitch_length)
        return jsonify({'sales_pitch': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pricing-strategy', methods=['POST'])
def generate_pricing_strategy():
    """Generate pricing strategy."""
    data = request.json
    product = data.get('product', '')
    market_position = data.get('market_position', 'Mid-tier')
    competitor_prices = data.get('competitor_prices', [])
    value_proposition = data.get('value_proposition', '')
    
    if not product:
        return jsonify({'error': 'Product required'}), 400
    
    try:
        result = functionality_26_generate_pricing_strategy(product, market_position, competitor_prices, value_proposition)
        return jsonify({'pricing_strategy': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-marketing-copy', methods=['POST'])
def generate_marketing_copy():
    """Generate marketing copy."""
    data = request.json
    product = data.get('product', '')
    channel = data.get('channel', 'Email')
    target_audience = data.get('target_audience', '')
    campaign_goal = data.get('campaign_goal', '')
    copy_length = data.get('copy_length', 'Medium')
    
    if not product or not target_audience:
        return jsonify({'error': 'Product and target audience required'}), 400
    
    try:
        result = functionality_27_generate_marketing_copy(product, channel, target_audience, campaign_goal, copy_length)
        return jsonify({'marketing_copy': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-competitor', methods=['POST'])
def analyze_competitor():
    """Analyze competitor."""
    data = request.json
    competitor_name = data.get('competitor_name', '')
    analysis_type = data.get('analysis_type', 'Comprehensive')
    
    if not competitor_name:
        return jsonify({'error': 'Competitor name required'}), 400
    
    try:
        result = functionality_28_analyze_competitor(competitor_name, analysis_type)
        return jsonify({'competitor_analysis': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-testimonials', methods=['POST'])
def generate_testimonials():
    """Generate testimonials."""
    data = request.json
    product = data.get('product', '')
    customer_type = data.get('customer_type', 'Enterprise')
    num_testimonials = data.get('num_testimonials', 5)
    testimonial_style = data.get('testimonial_style', 'Authentic')
    
    if not product:
        return jsonify({'error': 'Product required'}), 400
    
    try:
        result = functionality_29_generate_testimonials(product, customer_type, num_testimonials, testimonial_style)
        return jsonify({'testimonials': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
