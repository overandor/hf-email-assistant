// Tab switching
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;
        
        // Remove active class from all buttons and contents
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    });
});

// Authentication functions
function loginWithGoogle() {
    window.location.href = '/auth/login';
}

function logout() {
    window.location.href = '/auth/logout';
}

// Check auth status on load
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/status');
        const data = await response.json();
        updateAuthUI(data.authenticated);
    } catch (error) {
        console.error('Failed to check auth status:', error);
    }
}

function updateAuthUI(authenticated) {
    const indicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('auth-status');
    
    if (authenticated) {
        indicator.classList.add('authenticated');
        statusText.textContent = 'Authenticated with Gmail';
    } else {
        indicator.classList.remove('authenticated');
        statusText.textContent = 'Not authenticated';
    }
}

// Check auth status on page load
checkAuthStatus();

// API helper function
async function callAPI(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        alert('Error: ' + error.message);
        throw error;
    }
}

// Compose Email
async function composeEmail() {
    const topic = document.getElementById('compose-topic').value;
    const tone = document.getElementById('compose-tone').value;
    const recipient = document.getElementById('compose-recipient').value;
    const keyPoints = document.getElementById('compose-keypoints').value;
    
    if (!topic || !keyPoints) {
        alert('Please provide both a topic and key points.');
        return;
    }
    
    const result = await callAPI('/api/compose', {
        topic,
        tone,
        recipient,
        key_points: keyPoints
    });
    
    document.getElementById('compose-result').value = result.email;
}

// Sentiment Analysis
async function analyzeSentiment() {
    const text = document.getElementById('sentiment-text').value;
    
    if (!text) {
        alert('Please provide text to analyze.');
        return;
    }
    
    const result = await callAPI('/api/sentiment', { text });
    
    document.getElementById('sentiment-result').value = result.sentiment;
    document.getElementById('sentiment-confidence').value = result.confidence.toFixed(4);
}

// Summarize Email
async function summarizeEmail() {
    const text = document.getElementById('summarize-text').value;
    
    if (!text || text.length < 100) {
        alert('Please provide a longer email to summarize (min 100 characters).');
        return;
    }
    
    const result = await callAPI('/api/summarize', { text });
    
    document.getElementById('summarize-result').value = result.summary;
}

// A/B Testing
async function abTestEmail() {
    const topic = document.getElementById('ab-topic').value;
    const recipient = document.getElementById('ab-recipient').value;
    const keyPoints = document.getElementById('ab-keypoints').value;
    
    if (!topic || !keyPoints) {
        alert('Please provide both a topic and key points.');
        return;
    }
    
    const result = await callAPI('/api/abtest', {
        topic,
        recipient,
        key_points: keyPoints
    });
    
    document.getElementById('ab-variant-a').value = result.variant_a;
    document.getElementById('ab-variant-b').value = result.variant_b;
}

// Improve Tone
async function improveTone() {
    const text = document.getElementById('improve-text').value;
    const targetTone = document.getElementById('improve-tone').value;
    
    if (!text) {
        alert('Please provide email text to improve.');
        return;
    }
    
    const result = await callAPI('/api/improve', {
        text,
        target_tone: targetTone
    });
    
    document.getElementById('improve-result').value = result.improved;
}

// Research Lead
async function researchLead() {
    const company = document.getElementById('research-company').value;
    const industry = document.getElementById('research-industry').value;
    const role = document.getElementById('research-role').value;
    const painPoints = document.getElementById('research-pain').value;
    
    if (!company || !industry) {
        alert('Please provide company and industry.');
        return;
    }
    
    const result = await callAPI('/api/research-lead', {
        company,
        industry,
        role,
        pain_points: painPoints
    });
    
    document.getElementById('research-result').value = result.email;
}

// Batch Outreach
async function batchOutreach() {
    const template = document.getElementById('batch-template').value;
    const leadsText = document.getElementById('batch-leads').value;
    
    if (!leadsText) {
        alert('Please provide leads in JSON format.');
        return;
    }
    
    try {
        const leads = JSON.parse(leadsText);
        const result = await callAPI('/api/batch-outreach', {
            leads,
            template
        });
        
        const output = result.emails.map(e => 
            `Lead: ${e.lead.name} at ${e.lead.company}\nEmail: ${e.email}\n---`
        ).join('\n\n');
        
        document.getElementById('batch-result').value = output;
    } catch (error) {
        alert('Invalid JSON format for leads.');
    }
}

// Analyze Lead
async function analyzeLead() {
    const leadInfo = document.getElementById('analyze-info').value;
    
    if (!leadInfo) {
        alert('Please provide lead information.');
        return;
    }
    
    const result = await callAPI('/api/analyze-lead', {
        lead_info: leadInfo
    });
    
    document.getElementById('analyze-result').value = result.analysis;
}
