from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from transformers import pipeline
import re
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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

# Initialize Hugging Face pipelines (free inference, no API key needed)
print("Loading models...")
composer = pipeline("text-generation", model="gpt2", max_length=500)
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
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
    
    prompt = f"Subject: {topic}\n\nTo: {recipient}\n\nTone: {tone}\n\nKey points: {key_points}\n\nEmail:"
    
    try:
        result = composer(prompt, max_length=400, num_return_sequences=1, temperature=0.7)
        generated = result[0]['generated_text']
        email_body = generated.split("Email:")[-1].strip()
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
        result = sentiment_analyzer(text[:512])
        label = result[0]['label']
        score = result[0]['score']
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

if __name__ == "__main__":
    port = int(os.getenv('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
