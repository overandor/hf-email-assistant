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
    } else if (toolName === 'reply') {
        content = `
            <h2 class="tool-title">↩️ Email Reply Generator</h2>
            <div class="form-group">
                <label>Original Email</label>
                <textarea id="reply-original" rows="8" placeholder="Paste original email..."></textarea>
            </div>
            <div class="form-group">
                <label>Reply Tone</label>
                <select id="reply-tone">
                    <option value="Professional">Professional</option>
                    <option value="Friendly">Friendly</option>
                    <option value="Formal">Formal</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateReply()">Generate Reply</button>
            <div class="form-group">
                <label>Generated Reply</label>
                <textarea id="reply-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'subject') {
        content = `
            <h2 class="tool-title">📧 Subject Line Generator</h2>
            <div class="form-group">
                <label>Email Content</label>
                <textarea id="subject-content" rows="6" placeholder="Paste email content..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Number of Variants</label>
                    <input type="number" id="subject-num" value="5" min="1" max="10">
                </div>
                <div class="form-group">
                    <label>Style</label>
                    <select id="subject-style">
                        <option value="Professional">Professional</option>
                        <option value="Creative">Creative</option>
                        <option value="Urgent">Urgent</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateSubjectLines()">Generate Subject Lines</button>
            <div class="form-group">
                <label>Generated Subject Lines</label>
                <textarea id="subject-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'edit') {
        content = `
            <h2 class="tool-title">✏️ Email Editor</h2>
            <div class="form-group">
                <label>Original Email</label>
                <textarea id="edit-original" rows="8" placeholder="Paste email to edit..."></textarea>
            </div>
            <div class="form-group">
                <label>Edit Instruction</label>
                <input type="text" id="edit-instruction" placeholder="e.g., Make it more concise">
            </div>
            <div class="form-group">
                <label>Preserve Tone</label>
                <input type="checkbox" id="edit-preserve" checked>
            </div>
            <button class="btn btn-primary" onclick="editEmail()">Edit Email</button>
            <div class="form-group">
                <label>Edited Email</label>
                <textarea id="edit-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'categorize') {
        content = `
            <h2 class="tool-title">🏷️ Email Categorization</h2>
            <div class="form-group">
                <label>Email Content</label>
                <textarea id="categorize-content" rows="6" placeholder="Paste email..."></textarea>
            </div>
            <div class="form-group">
                <label>Categories (comma separated)</label>
                <input type="text" id="categorize-categories" placeholder="Work, Personal, Promotion, Urgent">
            </div>
            <button class="btn btn-primary" onclick="categorizeEmail()">Categorize</button>
            <div class="form-group">
                <label>Category Scores</label>
                <textarea id="categorize-result" rows="6" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'outreach') {
        content = `
            <h2 class="tool-title">🎯 Outreach Email Generator</h2>
            <div class="form-group">
                <label>Company Name</label>
                <input type="text" id="outreach-company" placeholder="e.g., Acme Corp">
            </div>
            <div class="form-group">
                <label>Industry</label>
                <input type="text" id="outreach-industry" placeholder="e.g., SaaS">
            </div>
            <div class="form-group">
                <label>Target Role</label>
                <input type="text" id="outreach-role" placeholder="e.g., CTO">
            </div>
            <div class="form-group">
                <label>Pain Points (comma separated)</label>
                <input type="text" id="outreach-pain" placeholder="scaling, cost, efficiency">
            </div>
            <div class="form-group">
                <label>Value Proposition</label>
                <input type="text" id="outreach-value" placeholder="Our platform scales efficiently">
            </div>
            <button class="btn btn-primary" onclick="generateOutreachEmail()">Generate Outreach Email</button>
            <div class="form-group">
                <label>Generated Email</label>
                <textarea id="outreach-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'followup') {
        content = `
            <h2 class="tool-title">📞 Follow-up Email Generator</h2>
            <div class="form-group">
                <label>Previous Email</label>
                <textarea id="followup-previous" rows="6" placeholder="Paste previous email..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Response Status</label>
                    <select id="followup-status">
                        <option value="No Response">No Response</option>
                        <option value="Positive">Positive</option>
                        <option value="Negative">Negative</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Days Since Contact</label>
                    <input type="number" id="followup-days" value="7">
                </div>
            </div>
            <div class="form-group">
                <label>Next Action</label>
                <input type="text" id="followup-action" placeholder="Schedule Call">
            </div>
            <button class="btn btn-primary" onclick="generateFollowUp()">Generate Follow-up</button>
            <div class="form-group">
                <label>Generated Follow-up</label>
                <textarea id="followup-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'cold') {
        content = `
            <h2 class="tool-title">❄️ Cold Email Generator</h2>
            <div class="form-group">
                <label>Prospect Name</label>
                <input type="text" id="cold-name" placeholder="John Smith">
            </div>
            <div class="form-group">
                <label>Company</label>
                <input type="text" id="cold-company" placeholder="Acme Corp">
            </div>
            <div class="form-group">
                <label>Role</label>
                <input type="text" id="cold-role" placeholder="CTO">
            </div>
            <div class="form-group">
                <label>Personalization Data</label>
                <textarea id="cold-personalization" rows="3" placeholder="Recent funding, new product launch..."></textarea>
            </div>
            <div class="form-group">
                <label>Call to Action Type</label>
                <select id="cold-cta">
                    <option value="Demo Request">Demo Request</option>
                    <option value="Meeting">Meeting</option>
                    <option value="Trial">Trial</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateColdEmail()">Generate Cold Email</button>
            <div class="form-group">
                <label>Generated Cold Email</label>
                <textarea id="cold-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'leadfit') {
        content = `
            <h2 class="tool-title">🎯 Lead Fit Analysis</h2>
            <div class="form-group">
                <label>Lead Info (JSON)</label>
                <textarea id="leadfit-info" rows="4" placeholder='{"company_size": "100-500", "industry": "SaaS"}'></textarea>
            </div>
            <div class="form-group">
                <label>Ideal Customer Profile (JSON)</label>
                <textarea id="leadfit-ideal" rows="4" placeholder='{"company_size": "100-500", "industry": "SaaS"}'></textarea>
            </div>
            <button class="btn btn-primary" onclick="analyzeLeadFit()">Analyze Fit</button>
            <div class="form-group">
                <label>Fit Scores</label>
                <textarea id="leadfit-result" rows="6" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'sequence') {
        content = `
            <h2 class="tool-title">📋 Outreach Sequence Generator</h2>
            <div class="form-group">
                <label>Lead Info (JSON)</label>
                <textarea id="sequence-info" rows="4" placeholder='{"name": "John", "company": "Acme"}'></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Sequence Length</label>
                    <input type="number" id="sequence-length" value="5" min="3" max="10">
                </div>
                <div class="form-group">
                    <label>Sequence Type</label>
                    <select id="sequence-type">
                        <option value="Standard">Standard</option>
                        <option value="Aggressive">Aggressive</option>
                        <option value="Passive">Passive</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateOutreachSequence()">Generate Sequence</button>
            <div class="form-group">
                <label>Generated Sequence</label>
                <textarea id="sequence-result" rows="12" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'keypoints') {
        content = `
            <h2 class="tool-title">🔑 Key Points Extractor</h2>
            <div class="form-group">
                <label>Text</label>
                <textarea id="keypoints-text" rows="8" placeholder="Paste text to analyze..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Number of Points</label>
                    <input type="number" id="keypoints-num" value="5" min="3" max="10">
                </div>
                <div class="form-group">
                    <label>Format</label>
                    <select id="keypoints-format">
                        <option value="Bullet Points">Bullet Points</option>
                        <option value="Numbered List">Numbered List</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="extractKeyPoints()">Extract Key Points</button>
            <div class="form-group">
                <label>Key Points</label>
                <textarea id="keypoints-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'sentimenttrend') {
        content = `
            <h2 class="tool-title">📈 Sentiment Trend Analysis</h2>
            <div class="form-group">
                <label>Texts (one per line)</label>
                <textarea id="sentimenttrend-texts" rows="8" placeholder="Enter multiple texts, one per line..."></textarea>
            </div>
            <div class="form-group">
                <label>Time Labels (optional, comma separated)</label>
                <input type="text" id="sentimenttrend-labels" placeholder="Day 1, Day 2, Day 3">
            </div>
            <button class="btn btn-primary" onclick="analyzeSentimentTrend()">Analyze Trend</button>
            <div class="form-group">
                <label>Trend Analysis</label>
                <textarea id="sentimenttrend-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'compare') {
        content = `
            <h2 class="tool-title">⚖️ Text Comparison</h2>
            <div class="form-group">
                <label>Text 1</label>
                <textarea id="compare-text1" rows="6" placeholder="First text..."></textarea>
            </div>
            <div class="form-group">
                <label>Text 2</label>
                <textarea id="compare-text2" rows="6" placeholder="Second text..."></textarea>
            </div>
            <div class="form-group">
                <label>Comparison Type</label>
                <select id="compare-type">
                    <option value="Similarity">Similarity</option>
                    <option value="Differences">Differences</option>
                    <option value="Style">Style</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="compareTexts()">Compare</button>
            <div class="form-group">
                <label>Comparison Result</label>
                <textarea id="compare-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'insights') {
        content = `
            <h2 class="tool-title">💡 Insights Generator</h2>
            <div class="form-group">
                <label>Data/Text</label>
                <textarea id="insights-data" rows="8" placeholder="Paste data or text..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Insight Type</label>
                    <select id="insights-type">
                        <option value="Business">Business</option>
                        <option value="Technical">Technical</option>
                        <option value="Strategic">Strategic</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Context</label>
                    <input type="text" id="insights-context" placeholder="Additional context...">
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateInsights()">Generate Insights</button>
            <div class="form-group">
                <label>Generated Insights</label>
                <textarea id="insights-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'classify') {
        content = `
            <h2 class="tool-title">📂 Content Classification</h2>
            <div class="form-group">
                <label>Text</label>
                <textarea id="classify-text" rows="6" placeholder="Paste text to classify..."></textarea>
            </div>
            <div class="form-group">
                <label>Categories (comma separated)</label>
                <input type="text" id="classify-categories" placeholder="Tech, Business, Health, Finance">
            </div>
            <div class="form-group">
                <label>Multi-label</label>
                <input type="checkbox" id="classify-multi">
            </div>
            <button class="btn btn-primary" onclick="classifyContent()">Classify</button>
            <div class="form-group">
                <label>Classification Scores</label>
                <textarea id="classify-result" rows="6" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'hashtags') {
        content = `
            <h2 class="tool-title">#️⃣ Hashtag Generator</h2>
            <div class="form-group">
                <label>Content</label>
                <textarea id="hashtags-content" rows="6" placeholder="Paste content..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Number of Hashtags</label>
                    <input type="number" id="hashtags-num" value="10" min="5" max="30">
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <select id="hashtags-type">
                        <option value="Relevant">Relevant</option>
                        <option value="Trending">Trending</option>
                        <option value="Niche">Niche</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateHashtags()">Generate Hashtags</button>
            <div class="form-group">
                <label>Generated Hashtags</label>
                <textarea id="hashtags-result" rows="6" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'headlines') {
        content = `
            <h2 class="tool-title">📰 Headline Generator</h2>
            <div class="form-group">
                <label>Content</label>
                <textarea id="headlines-content" rows="6" placeholder="Paste content..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Number of Headlines</label>
                    <input type="number" id="headlines-num" value="5" min="3" max="10">
                </div>
                <div class="form-group">
                    <label>Style</label>
                    <select id="headlines-style">
                        <option value="Clickbait">Clickbait</option>
                        <option value="Professional">Professional</option>
                        <option value="Question">Question</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateHeadlines()">Generate Headlines</button>
            <div class="form-group">
                <label>Generated Headlines</label>
                <textarea id="headlines-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'rewrite') {
        content = `
            <h2 class="tool-title">🔄 Text Rewriter</h2>
            <div class="form-group">
                <label>Original Text</label>
                <textarea id="rewrite-original" rows="8" placeholder="Paste text to rewrite..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Rewrite Style</label>
                    <select id="rewrite-style">
                        <option value="Simplified">Simplified</option>
                        <option value="Formal">Formal</option>
                        <option value="Casual">Casual</option>
                        <option value="Technical">Technical</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Target Audience</label>
                    <input type="text" id="rewrite-audience" placeholder="General">
                </div>
            </div>
            <button class="btn btn-primary" onclick="rewriteText()">Rewrite</button>
            <div class="form-group">
                <label>Rewritten Text</label>
                <textarea id="rewrite-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'cta') {
        content = `
            <h2 class="tool-title">👆 Call to Action Generator</h2>
            <div class="form-group">
                <label>Context</label>
                <textarea id="cta-context" rows="4" placeholder="Describe the context..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Action Type</label>
                    <select id="cta-type">
                        <option value="Sign Up">Sign Up</option>
                        <option value="Buy Now">Buy Now</option>
                        <option value="Learn More">Learn More</option>
                        <option value="Contact">Contact</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Urgency Level</label>
                    <select id="cta-urgency">
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateCTA()">Generate CTA</button>
            <div class="form-group">
                <label>Generated CTA</label>
                <textarea id="cta-result" rows="4" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'meta') {
        content = `
            <h2 class="tool-title">🔍 Meta Description Generator</h2>
            <div class="form-group">
                <label>Page Content</label>
                <textarea id="meta-content" rows="6" placeholder="Paste page content..."></textarea>
            </div>
            <div class="result-row">
                <div class="form-group">
                    <label>Max Length</label>
                    <input type="number" id="meta-length" value="160" min="50" max="300">
                </div>
                <div class="form-group">
                    <label>SEO Focus</label>
                    <input type="checkbox" id="meta-seo" checked>
                </div>
            </div>
            <button class="btn btn-primary" onclick="generateMetaDescription()">Generate Meta Description</button>
            <div class="form-group">
                <label>Meta Description</label>
                <textarea id="meta-result" rows="4" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'sales') {
        content = `
            <h2 class="tool-title">💰 Sales Pitch Generator</h2>
            <div class="form-group">
                <label>Product</label>
                <input type="text" id="sales-product" placeholder="Product name">
            </div>
            <div class="form-group">
                <label>Target Audience</label>
                <input type="text" id="sales-audience" placeholder="e.g., CTOs at mid-size companies">
            </div>
            <div class="form-group">
                <label>Key Benefits (comma separated)</label>
                <input type="text" id="sales-benefits" placeholder="efficiency, cost savings, scalability">
            </div>
            <div class="form-group">
                <label>Differentiators (comma separated)</label>
                <input type="text" id="sales-differentiators" placeholder="AI-powered, real-time, secure">
            </div>
            <div class="form-group">
                <label>Pitch Length</label>
                <select id="sales-length">
                    <option value="Short">Short</option>
                    <option value="Medium">Medium</option>
                    <option value="Long">Long</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateSalesPitch()">Generate Sales Pitch</button>
            <div class="form-group">
                <label>Sales Pitch</label>
                <textarea id="sales-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'pricing') {
        content = `
            <h2 class="tool-title">💲 Pricing Strategy Generator</h2>
            <div class="form-group">
                <label>Product</label>
                <input type="text" id="pricing-product" placeholder="Product name">
            </div>
            <div class="form-group">
                <label>Market Position</label>
                <select id="pricing-position">
                    <option value="Premium">Premium</option>
                    <option value="Mid-tier">Mid-tier</option>
                    <option value="Budget">Budget</option>
                </select>
            </div>
            <div class="form-group">
                <label>Competitor Prices (comma separated)</label>
                <input type="text" id="pricing-competitors" placeholder="99, 149, 199">
            </div>
            <div class="form-group">
                <label>Value Proposition</label>
                <input type="text" id="pricing-value" placeholder="Unique value proposition">
            </div>
            <button class="btn btn-primary" onclick="generatePricingStrategy()">Generate Pricing Strategy</button>
            <div class="form-group">
                <label>Pricing Strategy</label>
                <textarea id="pricing-result" rows="8" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'marketing') {
        content = `
            <h2 class="tool-title">📢 Marketing Copy Generator</h2>
            <div class="form-group">
                <label>Product</label>
                <input type="text" id="marketing-product" placeholder="Product name">
            </div>
            <div class="form-group">
                <label>Channel</label>
                <select id="marketing-channel">
                    <option value="Email">Email</option>
                    <option value="Social">Social Media</option>
                    <option value="Ad">Advertisement</option>
                    <option value="Landing Page">Landing Page</option>
                </select>
            </div>
            <div class="form-group">
                <label>Target Audience</label>
                <input type="text" id="marketing-audience" placeholder="Target audience">
            </div>
            <div class="form-group">
                <label>Campaign Goal</label>
                <input type="text" id="marketing-goal" placeholder="e.g., Demo signups">
            </div>
            <div class="form-group">
                <label>Copy Length</label>
                <select id="marketing-length">
                    <option value="Short">Short</option>
                    <option value="Medium">Medium</option>
                    <option value="Long">Long</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateMarketingCopy()">Generate Marketing Copy</button>
            <div class="form-group">
                <label>Marketing Copy</label>
                <textarea id="marketing-result" rows="10" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'competitor') {
        content = `
            <h2 class="tool-title">🏢 Competitor Analysis</h2>
            <div class="form-group">
                <label>Competitor Name</label>
                <input type="text" id="competitor-name" placeholder="Competitor company name">
            </div>
            <div class="form-group">
                <label>Analysis Type</label>
                <select id="competitor-type">
                    <option value="Comprehensive">Comprehensive</option>
                    <option value="Pricing">Pricing</option>
                    <option value="Features">Features</option>
                    <option value="Marketing">Marketing</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="analyzeCompetitor()">Analyze Competitor</button>
            <div class="form-group">
                <label>Competitor Analysis</label>
                <textarea id="competitor-result" rows="12" readonly></textarea>
            </div>
        `;
    } else if (toolName === 'testimonials') {
        content = `
            <h2 class="tool-title">⭐ Testimonial Generator</h2>
            <div class="form-group">
                <label>Product</label>
                <input type="text" id="testimonials-product" placeholder="Product name">
            </div>
            <div class="form-group">
                <label>Customer Type</label>
                <select id="testimonials-type">
                    <option value="Enterprise">Enterprise</option>
                    <option value="SMB">SMB</option>
                    <option value="Individual">Individual</option>
                </select>
            </div>
            <div class="form-group">
                <label>Number of Testimonials</label>
                <input type="number" id="testimonials-num" value="5" min="3" max="10">
            </div>
            <div class="form-group">
                <label>Testimonial Style</label>
                <select id="testimonials-style">
                    <option value="Authentic">Authentic</option>
                    <option value="Professional">Professional</option>
                    <option value="Casual">Casual</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateTestimonials()">Generate Testimonials</button>
            <div class="form-group">
                <label>Generated Testimonials</label>
                <textarea id="testimonials-result" rows="12" readonly></textarea>
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

// New API call functions for all 29 LLM functionalities
async function generateReply() {
    const originalEmail = document.getElementById('reply-original').value;
    const replyTone = document.getElementById('reply-tone').value;
    
    if (!originalEmail) {
        alert('Please provide original email');
        return;
    }
    
    const result = await callAPI('/api/generate-reply', {
        original_email: originalEmail,
        reply_tone: replyTone
    });
    
    document.getElementById('reply-result').value = result.reply;
}

async function generateSubjectLines() {
    const emailContent = document.getElementById('subject-content').value;
    const numVariants = document.getElementById('subject-num').value;
    const style = document.getElementById('subject-style').value;
    
    if (!emailContent) {
        alert('Please provide email content');
        return;
    }
    
    const result = await callAPI('/api/generate-subject-lines', {
        email_content: emailContent,
        num_variants: parseInt(numVariants),
        style: style
    });
    
    document.getElementById('subject-result').value = result.subject_lines.join('\n');
}

async function editEmail() {
    const originalEmail = document.getElementById('edit-original').value;
    const editInstruction = document.getElementById('edit-instruction').value;
    const preserveTone = document.getElementById('edit-preserve').checked;
    
    if (!originalEmail || !editInstruction) {
        alert('Please provide original email and edit instruction');
        return;
    }
    
    const result = await callAPI('/api/edit-email', {
        original_email: originalEmail,
        edit_instruction: editInstruction,
        preserve_tone: preserveTone
    });
    
    document.getElementById('edit-result').value = result.edited_email;
}

async function categorizeEmail() {
    const emailContent = document.getElementById('categorize-content').value;
    const categoriesText = document.getElementById('categorize-categories').value;
    const categories = categoriesText.split(',').map(c => c.trim());
    
    if (!emailContent) {
        alert('Please provide email content');
        return;
    }
    
    const result = await callAPI('/api/categorize-email', {
        email_content: emailContent,
        categories: categories
    });
    
    const categoryText = Object.entries(result.categories)
        .map(([cat, score]) => `${cat}: ${(score * 100).toFixed(1)}%`)
        .join('\n');
    document.getElementById('categorize-result').value = categoryText;
}

async function generateOutreachEmail() {
    const companyName = document.getElementById('outreach-company').value;
    const industry = document.getElementById('outreach-industry').value;
    const targetRole = document.getElementById('outreach-role').value;
    const painPointsText = document.getElementById('outreach-pain').value;
    const painPoints = painPointsText.split(',').map(p => p.trim());
    const valueProposition = document.getElementById('outreach-value').value;
    const tone = 'Professional';
    
    if (!companyName || !industry) {
        alert('Please provide company name and industry');
        return;
    }
    
    const result = await callAPI('/api/generate-outreach-email', {
        company_name: companyName,
        industry: industry,
        target_role: targetRole,
        pain_points: painPoints,
        value_proposition: valueProposition,
        tone: tone
    });
    
    document.getElementById('outreach-result').value = result.email;
}

async function generateFollowUp() {
    const previousEmail = document.getElementById('followup-previous').value;
    const responseStatus = document.getElementById('followup-status').value;
    const daysSinceContact = document.getElementById('followup-days').value;
    const nextAction = document.getElementById('followup-action').value;
    
    if (!previousEmail) {
        alert('Please provide previous email');
        return;
    }
    
    const result = await callAPI('/api/generate-follow-up', {
        previous_email: previousEmail,
        response_status: responseStatus,
        days_since_contact: parseInt(daysSinceContact),
        next_action: nextAction
    });
    
    document.getElementById('followup-result').value = result.follow_up;
}

async function generateColdEmail() {
    const name = document.getElementById('cold-name').value;
    const company = document.getElementById('cold-company').value;
    const role = document.getElementById('cold-role').value;
    const personalization = document.getElementById('cold-personalization').value;
    const ctaType = document.getElementById('cold-cta').value;
    
    const prospectInfo = { name, company, role };
    const personalizationData = { personalization };
    
    if (!name || !company) {
        alert('Please provide prospect name and company');
        return;
    }
    
    const result = await callAPI('/api/generate-cold-email', {
        prospect_info: prospectInfo,
        personalization_data: personalizationData,
        cta_type: ctaType
    });
    
    document.getElementById('cold-result').value = result.cold_email;
}

async function analyzeLeadFit() {
    const leadInfoText = document.getElementById('leadfit-info').value;
    const idealProfileText = document.getElementById('leadfit-ideal').value;
    
    try {
        const leadInfo = JSON.parse(leadInfoText);
        const idealProfile = JSON.parse(idealProfileText);
        
        const result = await callAPI('/api/analyze-lead-fit', {
            lead_info: leadInfo,
            ideal_customer_profile: idealProfile
        });
        
        const fitText = Object.entries(result.fit_scores)
            .map(([metric, score]) => `${metric}: ${(score * 100).toFixed(1)}%`)
            .join('\n');
        document.getElementById('leadfit-result').value = fitText;
    } catch (e) {
        alert('Invalid JSON format');
    }
}

async function generateOutreachSequence() {
    const leadInfoText = document.getElementById('sequence-info').value;
    const sequenceLength = document.getElementById('sequence-length').value;
    const sequenceType = document.getElementById('sequence-type').value;
    
    try {
        const leadInfo = JSON.parse(leadInfoText);
        
        const result = await callAPI('/api/generate-outreach-sequence', {
            lead_info: leadInfo,
            sequence_length: parseInt(sequenceLength),
            sequence_type: sequenceType
        });
        
        const sequenceText = result.sequence.map((touch, i) => 
            `Touch ${i + 1}: ${touch.channel} - ${touch.message}`
        ).join('\n\n');
        document.getElementById('sequence-result').value = sequenceText;
    } catch (e) {
        alert('Invalid JSON format');
    }
}

async function extractKeyPoints() {
    const text = document.getElementById('keypoints-text').value;
    const numPoints = document.getElementById('keypoints-num').value;
    const summaryType = document.getElementById('keypoints-format').value;
    
    if (!text) {
        alert('Please provide text');
        return;
    }
    
    const result = await callAPI('/api/extract-key-points', {
        text: text,
        num_points: parseInt(numPoints),
        summary_type: summaryType
    });
    
    document.getElementById('keypoints-result').value = result.key_points.join('\n');
}

async function analyzeSentimentTrend() {
    const textsText = document.getElementById('sentimenttrend-texts').value;
    const labelsText = document.getElementById('sentimenttrend-labels').value;
    
    const texts = textsText.split('\n').filter(t => t.trim());
    const timeLabels = labelsText ? labelsText.split(',').map(l => l.trim()) : null;
    
    if (!texts.length) {
        alert('Please provide texts');
        return;
    }
    
    const result = await callAPI('/api/analyze-sentiment-trend', {
        texts: texts,
        time_labels: timeLabels
    });
    
    const trendText = `Labels: ${result.trends.labels.join(', ')}\nPositive: ${result.trends.positive.join(', ')}\nNegative: ${result.trends.negative.join(', ')}`;
    document.getElementById('sentimenttrend-result').value = trendText;
}

async function compareTexts() {
    const text1 = document.getElementById('compare-text1').value;
    const text2 = document.getElementById('compare-text2').value;
    const comparisonType = document.getElementById('compare-type').value;
    
    if (!text1 || !text2) {
        alert('Please provide both texts');
        return;
    }
    
    const result = await callAPI('/api/compare-texts', {
        text1: text1,
        text2: text2,
        comparison_type: comparisonType
    });
    
    document.getElementById('compare-result').value = result.comparison.analysis;
}

async function generateInsights() {
    const data = document.getElementById('insights-data').value;
    const insightType = document.getElementById('insights-type').value;
    const context = document.getElementById('insights-context').value;
    
    if (!data) {
        alert('Please provide data');
        return;
    }
    
    const result = await callAPI('/api/generate-insights', {
        data: data,
        insight_type: insightType,
        context: context
    });
    
    document.getElementById('insights-result').value = result.insights.join('\n');
}

async function classifyContent() {
    const text = document.getElementById('classify-text').value;
    const categoriesText = document.getElementById('classify-categories').value;
    const multiLabel = document.getElementById('classify-multi').checked;
    const categories = categoriesText.split(',').map(c => c.trim());
    
    if (!text || !categories.length) {
        alert('Please provide text and categories');
        return;
    }
    
    const result = await callAPI('/api/classify-content', {
        text: text,
        categories: categories,
        multi_label: multiLabel
    });
    
    const classText = Object.entries(result.classification)
        .map(([cat, score]) => `${cat}: ${(score * 100).toFixed(1)}%`)
        .join('\n');
    document.getElementById('classify-result').value = classText;
}

async function generateHashtags() {
    const content = document.getElementById('hashtags-content').value;
    const numHashtags = document.getElementById('hashtags-num').value;
    const hashtagType = document.getElementById('hashtags-type').value;
    
    if (!content) {
        alert('Please provide content');
        return;
    }
    
    const result = await callAPI('/api/generate-hashtags', {
        content: content,
        num_hashtags: parseInt(numHashtags),
        hashtag_type: hashtagType
    });
    
    document.getElementById('hashtags-result').value = result.hashtags.join(' ');
}

async function generateHeadlines() {
    const content = document.getElementById('headlines-content').value;
    const numVariants = document.getElementById('headlines-num').value;
    const headlineStyle = document.getElementById('headlines-style').value;
    
    if (!content) {
        alert('Please provide content');
        return;
    }
    
    const result = await callAPI('/api/generate-headlines', {
        content: content,
        num_variants: parseInt(numVariants),
        headline_style: headlineStyle
    });
    
    document.getElementById('headlines-result').value = result.headlines.join('\n');
}

async function rewriteText() {
    const originalText = document.getElementById('rewrite-original').value;
    const rewriteStyle = document.getElementById('rewrite-style').value;
    const targetAudience = document.getElementById('rewrite-audience').value;
    
    if (!originalText) {
        alert('Please provide original text');
        return;
    }
    
    const result = await callAPI('/api/rewrite-text', {
        original_text: originalText,
        rewrite_style: rewriteStyle,
        target_audience: targetAudience
    });
    
    document.getElementById('rewrite-result').value = result.rewritten_text;
}

async function generateCTA() {
    const context = document.getElementById('cta-context').value;
    const actionType = document.getElementById('cta-type').value;
    const urgencyLevel = document.getElementById('cta-urgency').value;
    
    if (!context) {
        alert('Please provide context');
        return;
    }
    
    const result = await callAPI('/api/generate-cta', {
        context: context,
        action_type: actionType,
        urgency_level: urgencyLevel
    });
    
    document.getElementById('cta-result').value = result.cta;
}

async function generateMetaDescription() {
    const content = document.getElementById('meta-content').value;
    const maxLength = document.getElementById('meta-length').value;
    const seoFocus = document.getElementById('meta-seo').checked;
    
    if (!content) {
        alert('Please provide content');
        return;
    }
    
    const result = await callAPI('/api/generate-meta-description', {
        content: content,
        max_length: parseInt(maxLength),
        seo_focus: seoFocus
    });
    
    document.getElementById('meta-result').value = result.meta_description;
}

async function generateSalesPitch() {
    const product = document.getElementById('sales-product').value;
    const targetAudience = document.getElementById('sales-audience').value;
    const benefitsText = document.getElementById('sales-benefits').value;
    const differentiatorsText = document.getElementById('sales-differentiators').value;
    const pitchLength = document.getElementById('sales-length').value;
    
    const keyBenefits = benefitsText.split(',').map(b => b.trim());
    const differentiators = differentiatorsText.split(',').map(d => d.trim());
    
    if (!product || !targetAudience) {
        alert('Please provide product and target audience');
        return;
    }
    
    const result = await callAPI('/api/generate-sales-pitch', {
        product: product,
        target_audience: targetAudience,
        key_benefits: keyBenefits,
        differentiators: differentiators,
        pitch_length: pitchLength
    });
    
    document.getElementById('sales-result').value = result.sales_pitch;
}

async function generatePricingStrategy() {
    const product = document.getElementById('pricing-product').value;
    const marketPosition = document.getElementById('pricing-position').value;
    const competitorsText = document.getElementById('pricing-competitors').value;
    const valueProposition = document.getElementById('pricing-value').value;
    
    const competitorPrices = competitorsText.split(',').map(p => parseInt(p.trim()));
    
    if (!product) {
        alert('Please provide product');
        return;
    }
    
    const result = await callAPI('/api/generate-pricing-strategy', {
        product: product,
        market_position: marketPosition,
        competitor_prices: competitorPrices,
        value_proposition: valueProposition
    });
    
    document.getElementById('pricing-result').value = result.pricing_strategy.strategy;
}

async function generateMarketingCopy() {
    const product = document.getElementById('marketing-product').value;
    const channel = document.getElementById('marketing-channel').value;
    const targetAudience = document.getElementById('marketing-audience').value;
    const campaignGoal = document.getElementById('marketing-goal').value;
    const copyLength = document.getElementById('marketing-length').value;
    
    if (!product || !targetAudience) {
        alert('Please provide product and target audience');
        return;
    }
    
    const result = await callAPI('/api/generate-marketing-copy', {
        product: product,
        channel: channel,
        target_audience: targetAudience,
        campaign_goal: campaignGoal,
        copy_length: copyLength
    });
    
    document.getElementById('marketing-result').value = result.marketing_copy;
}

async function analyzeCompetitor() {
    const competitorName = document.getElementById('competitor-name').value;
    const analysisType = document.getElementById('competitor-type').value;
    
    if (!competitorName) {
        alert('Please provide competitor name');
        return;
    }
    
    const result = await callAPI('/api/analyze-competitor', {
        competitor_name: competitorName,
        analysis_type: analysisType
    });
    
    document.getElementById('competitor-result').value = result.competitor_analysis.analysis;
}

async function generateTestimonials() {
    const product = document.getElementById('testimonials-product').value;
    const customerType = document.getElementById('testimonials-type').value;
    const numTestimonials = document.getElementById('testimonials-num').value;
    const testimonialStyle = document.getElementById('testimonials-style').value;
    
    if (!product) {
        alert('Please provide product');
        return;
    }
    
    const result = await callAPI('/api/generate-testimonials', {
        product: product,
        customer_type: customerType,
        num_testimonials: parseInt(numTestimonials),
        testimonial_style: testimonialStyle
    });
    
    document.getElementById('testimonials-result').value = result.testimonials.join('\n\n');
}
