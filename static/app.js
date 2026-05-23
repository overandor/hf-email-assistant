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

// Appraise Repo
async function appraiseRepo() {
    const repoUrl = document.getElementById('appraise-url').value;
    
    if (!repoUrl) {
        alert('Please provide a GitHub repository URL.');
        return;
    }
    
    const result = await callAPI('/api/appraise-repo', {
        repo_url: repoUrl
    });
    
    document.getElementById('appraise-stars').value = result.stars;
    document.getElementById('appraise-forks').value = result.forks;
    document.getElementById('appraise-engagement').value = result.engagement_score;
    document.getElementById('appraise-value').value = result.value_score;
    document.getElementById('appraise-result').value = result.ai_appraisal;
}

// Terminal functionality
let terminalSessionId = null;

async function createTerminalSession() {
    const result = await callAPI('/api/terminal/create-session', {});
    if (result.success) {
        terminalSessionId = result.session_id;
        document.getElementById('terminal-session-id').value = result.session_id;
        document.getElementById('terminal-working-dir').value = result.working_directory;
        appendTerminalOutput(`Session created: ${result.session_id}`);
        appendTerminalOutput(`Working directory: ${result.working_directory}`);
    }
}

async function executeTerminalCommand() {
    const command = document.getElementById('terminal-command').value;
    if (!command) return;
    
    if (!terminalSessionId) {
        await createTerminalSession();
    }
    
    appendTerminalOutput(`$ ${command}`);
    
    const result = await callAPI('/api/terminal/execute', {
        session_id: terminalSessionId,
        command: command
    });
    
    if (result.success) {
        appendTerminalOutput(result.stdout);
        if (result.stderr) {
            appendTerminalOutput(`Error: ${result.stderr}`);
        }
    } else {
        appendTerminalOutput(`Error: ${result.error}`);
    }
    
    document.getElementById('terminal-command').value = '';
}

async function listTerminalDirectory() {
    const path = document.getElementById('terminal-path').value;
    
    if (!terminalSessionId) {
        await createTerminalSession();
    }
    
    const result = await callAPI('/api/terminal/list-directory', {
        session_id: terminalSessionId,
        path: path || null
    });
    
    if (result.success) {
        appendTerminalOutput(result.stdout);
    } else {
        appendTerminalOutput(`Error: ${result.error}`);
    }
}

async function changeTerminalDirectory() {
    const path = document.getElementById('terminal-cd-path').value;
    if (!path) return;
    
    if (!terminalSessionId) {
        await createTerminalSession();
    }
    
    const result = await callAPI('/api/terminal/change-directory', {
        session_id: terminalSessionId,
        path: path
    });
    
    if (result.success) {
        document.getElementById('terminal-working-dir').value = result.working_directory;
        appendTerminalOutput(`Changed to: ${result.working_directory}`);
    } else {
        appendTerminalOutput(`Error: ${result.error}`);
    }
}

async function runTerminalTests() {
    const testType = document.getElementById('terminal-test-type').value;
    
    if (!terminalSessionId) {
        await createTerminalSession();
    }
    
    appendTerminalOutput(`Running ${testType} tests...`);
    
    const result = await callAPI('/api/terminal/run-tests', {
        session_id: terminalSessionId,
        test_type: testType
    });
    
    if (result.success) {
        appendTerminalOutput(result.stdout);
    } else {
        appendTerminalOutput(`Error: ${result.error}`);
    }
}

async function deployTerminal() {
    const environment = document.getElementById('terminal-env').value;
    const platform = document.getElementById('terminal-platform').value;
    
    if (!terminalSessionId) {
        await createTerminalSession();
    }
    
    appendTerminalOutput(`Deploying to ${platform} (${environment})...`);
    
    const result = await callAPI('/api/terminal/deploy', {
        session_id: terminalSessionId,
        environment: environment,
        platform: platform
    });
    
    if (result.success) {
        appendTerminalOutput('Deployment successful!');
    } else {
        appendTerminalOutput(`Error: ${result.error}`);
    }
}

function appendTerminalOutput(text) {
    const output = document.getElementById('terminal-output');
    output.value += text + '\n';
    output.scrollTop = output.scrollHeight;
}

function clearTerminalOutput() {
    document.getElementById('terminal-output').value = '';
}

// Dashboard tool panel
function openTool(toolName) {
    const toolPanel = document.getElementById('tool-panel');
    const toolContent = document.getElementById('tool-content');
    
    toolPanel.classList.remove('hidden');
    
    let content = '';
    
    if (toolName === 'terminal') {
        content = `
            <h2 class="tool-title">💻 Bash Terminal</h2>
            <div class="result-row">
                <div class="form-group">
                    <label>Session ID</label>
                    <input type="text" id="terminal-session-id" readonly>
                </div>
                <div class="form-group">
                    <label>Working Directory</label>
                    <input type="text" id="terminal-working-dir" readonly>
                </div>
            </div>
            <div class="form-group">
                <label>Terminal Output</label>
                <textarea id="terminal-output" rows="15" readonly style="font-family: monospace; background: #1e1e1e; color: #00ff00;"></textarea>
            </div>
            <div class="form-group">
                <label>Command</label>
                <input type="text" id="terminal-command" placeholder="Enter bash command..." onkeypress="if(event.key === 'Enter') executeTerminalCommand()">
            </div>
            <div class="result-row">
                <button class="btn btn-primary" onclick="executeTerminalCommand()">Execute</button>
                <button class="btn" onclick="clearTerminalOutput()">Clear</button>
            </div>
            <hr style="margin: 20px 0;">
            <h3>Quick Actions</h3>
            <div class="result-row">
                <div class="form-group">
                    <label>List Directory</label>
                    <input type="text" id="terminal-path" placeholder="Path (optional)">
                </div>
                <button class="btn" onclick="listTerminalDirectory()">List</button>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Change Directory</label>
                    <input type="text" id="terminal-cd-path" placeholder="Path">
                </div>
                <button class="btn" onclick="changeTerminalDirectory()">CD</button>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Run Tests</label>
                    <select id="terminal-test-type">
                        <option value="all">All Tests</option>
                        <option value="unit">Unit Tests</option>
                        <option value="integration">Integration Tests</option>
                    </select>
                </div>
                <button class="btn" onclick="runTerminalTests()">Run Tests</button>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Deploy</label>
                    <select id="terminal-env">
                        <option value="production">Production</option>
                        <option value="staging">Staging</option>
                    </select>
                    <select id="terminal-platform">
                        <option value="huggingface">Hugging Face</option>
                        <option value="github">GitHub</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="deployTerminal()">Deploy</button>
            </div>
        `;
    }
    
    toolContent.innerHTML = content;
    
    if (toolName === 'terminal') {
        createTerminalSession();
    }
}

function closeTool() {
    const toolPanel = document.getElementById('tool-panel');
    toolPanel.classList.add('hidden');
}
