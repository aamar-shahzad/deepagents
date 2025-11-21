/**
 * Deep Agents Builder - Frontend Application
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';

let currentAgent = null;
let subagentCounter = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadAgents();
    setupFormHandler();
});

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Load and display all agents
 */
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE_URL}/agents`);
        if (!response.ok) {
            throw new Error('Failed to load agents');
        }
        
        const data = await response.json();
        displayAgents(data.agents);
    } catch (error) {
        console.error('Error loading agents:', error);
        showToast('Failed to load agents. Make sure the backend is running.', 'error');
    }
}

/**
 * Display agents in the list
 */
function displayAgents(agents) {
    const agentsList = document.getElementById('agents-list');
    
    if (!agents || agents.length === 0) {
        agentsList.innerHTML = '<p class="empty-state">No agents created yet. Create your first agent!</p>';
        return;
    }
    
    agentsList.innerHTML = agents.map(agent => {
        const badges = [];
        if (agent.debug) badges.push('<span class="badge debug">DEBUG</span>');
        if (agent.use_longterm_memory) badges.push('<span class="badge memory">MEMORY</span>');
        
        const description = agent.description ? `<p style="font-style: italic; font-size: 0.85rem;">${agent.description}</p>` : '';
        
        return `
        <div class="agent-card">
            <h4>${agent.name}${badges.join('')}</h4>
            ${description}
            <p>${agent.system_prompt}</p>
            <div class="meta">
                Model: ${agent.model || 'Claude Sonnet 4.5'} | 
                Subagents: ${agent.num_subagents || 0} | 
                Executions: ${agent.execution_count || 0}
            </div>
            <div class="agent-actions">
                <button class="btn btn-success" onclick="selectAgent('${agent.name}')">
                    Execute
                </button>
                <button class="btn btn-secondary" onclick="editAgent('${agent.name}')">
                    Edit
                </button>
                <button class="btn btn-danger" onclick="deleteAgent('${agent.name}')">
                    Delete
                </button>
            </div>
        </div>
    `;
    }).join('');
}

/**
 * Setup form submission handler
 */
function setupFormHandler() {
    const form = document.getElementById('agent-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await createOrUpdateAgent();
    });
}

/**
 * Create or update an agent
 */
async function createOrUpdateAgent() {
    const formData = new FormData(document.getElementById('agent-form'));
    const isEditMode = document.getElementById('edit-mode').value === 'true';
    const originalName = document.getElementById('original-name').value;
    
    // Build the agent configuration
    const config = {
        name: formData.get('name'),
        description: formData.get('description') || '',
        system_prompt: formData.get('system_prompt'),
        model: formData.get('model') || null,
        use_longterm_memory: document.getElementById('use-memory').checked,
        debug: document.getElementById('debug-mode').checked,
        tools: [], // Built-in tools are always available
        subagents: []
    };
    
    // Collect subagents
    const subagentItems = document.querySelectorAll('.subagent-item');
    subagentItems.forEach(item => {
        const name = item.querySelector('[name="subagent_name"]').value;
        const description = item.querySelector('[name="subagent_description"]').value;
        const prompt = item.querySelector('[name="subagent_prompt"]').value;
        
        if (name && description && prompt) {
            config.subagents.push({
                name: name,
                description: description,
                system_prompt: prompt,
                tools: []
            });
        }
    });
    
    try {
        const url = isEditMode 
            ? `${API_BASE_URL}/agents/${originalName}`
            : `${API_BASE_URL}/agents/create`;
        
        const method = isEditMode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `Failed to ${isEditMode ? 'update' : 'create'} agent`);
        }
        
        const result = await response.json();
        showToast(`Agent "${config.name}" ${isEditMode ? 'updated' : 'created'} successfully!`, 'success');
        
        // Reset form and reload agents
        cancelEdit();
        loadAgents();
        
    } catch (error) {
        console.error(`Error ${isEditMode ? 'updating' : 'creating'} agent:`, error);
        showToast(error.message, 'error');
    }
}

/**
 * Edit an existing agent
 */
async function editAgent(agentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/agents/${agentName}`);
        if (!response.ok) {
            throw new Error('Failed to load agent details');
        }
        
        const data = await response.json();
        const config = data.config;
        
        // Populate form with agent data
        document.getElementById('agent-name').value = config.name;
        document.getElementById('agent-name').readOnly = true; // Can't change name
        document.getElementById('agent-description').value = config.description || '';
        document.getElementById('system-prompt').value = config.system_prompt;
        document.getElementById('model-select').value = config.model || '';
        document.getElementById('use-memory').checked = config.use_longterm_memory || false;
        document.getElementById('debug-mode').checked = config.debug || false;
        
        // Clear and populate subagents
        document.getElementById('subagents-container').innerHTML = '';
        subagentCounter = 0;
        
        if (config.subagents && config.subagents.length > 0) {
            config.subagents.forEach(subagent => {
                addSubagent();
                const container = document.getElementById(`subagent-${subagentCounter}`);
                if (container) {
                    const nameInput = container.querySelector('[name="subagent_name"]');
                    const descInput = container.querySelector('[name="subagent_description"]');
                    const promptInput = container.querySelector('[name="subagent_prompt"]');
                    
                    if (nameInput) nameInput.value = subagent.name;
                    if (descInput) descInput.value = subagent.description;
                    if (promptInput) promptInput.value = subagent.system_prompt;
                }
            });
        }
        
        // Set edit mode
        document.getElementById('edit-mode').value = 'true';
        document.getElementById('original-name').value = agentName;
        document.getElementById('submit-btn').textContent = 'Update Agent';
        document.getElementById('cancel-btn').style.display = 'inline-block';
        
        // Scroll to form
        document.querySelector('.config-panel').scrollIntoView({ behavior: 'smooth' });
        
        showToast(`Editing agent: ${agentName}`, 'info');
        
    } catch (error) {
        console.error('Error loading agent for edit:', error);
        showToast(error.message, 'error');
    }
}

/**
 * Cancel edit mode
 */
function cancelEdit() {
    document.getElementById('agent-form').reset();
    document.getElementById('subagents-container').innerHTML = '';
    subagentCounter = 0;
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('original-name').value = '';
    document.getElementById('agent-name').readOnly = false;
    document.getElementById('submit-btn').textContent = 'Create Agent';
    document.getElementById('cancel-btn').style.display = 'none';
}

/**
 * Add a subagent form
 */
function addSubagent() {
    subagentCounter++;
    const container = document.getElementById('subagents-container');
    
    const subagentHTML = `
        <div class="subagent-item" id="subagent-${subagentCounter}">
            <div class="subagent-header">
                <h4>Subagent ${subagentCounter}</h4>
                <button type="button" class="btn btn-danger" onclick="removeSubagent(${subagentCounter})">
                    Remove
                </button>
            </div>
            <div class="form-group">
                <label>Name</label>
                <input 
                    type="text" 
                    name="subagent_name" 
                    placeholder="research-agent"
                    required
                >
            </div>
            <div class="form-group">
                <label>Description</label>
                <input 
                    type="text" 
                    name="subagent_description" 
                    placeholder="Used to research specific topics"
                    required
                >
            </div>
            <div class="form-group">
                <label>System Prompt</label>
                <textarea 
                    name="subagent_prompt" 
                    rows="3"
                    placeholder="You are a dedicated researcher..."
                    required
                ></textarea>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', subagentHTML);
}

/**
 * Remove a subagent form
 */
function removeSubagent(id) {
    const element = document.getElementById(`subagent-${id}`);
    if (element) {
        element.remove();
    }
}

/**
 * Select an agent for execution
 */
function selectAgent(agentName) {
    currentAgent = agentName;
    document.getElementById('current-agent-name').textContent = agentName;
    document.getElementById('execution-panel').style.display = 'block';
    document.getElementById('execution-result').innerHTML = '';
    document.getElementById('user-message').value = '';
}

/**
 * Execute the selected agent
 */
async function executeAgent() {
    if (!currentAgent) {
        showToast('No agent selected', 'error');
        return;
    }
    
    const message = document.getElementById('user-message').value.trim();
    if (!message) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    const resultDiv = document.getElementById('execution-result');
    resultDiv.innerHTML = '<div class="loading">⏳ Executing agent... This may take a moment.</div>';
    resultDiv.className = 'execution-result loading';
    
    try {
        const response = await fetch(`${API_BASE_URL}/agents/${currentAgent}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to execute agent');
        }
        
        const result = await response.json();
        
        resultDiv.innerHTML = `
            <strong>Agent Response:</strong><br><br>
            ${result.response || 'No response from agent'}
        `;
        resultDiv.className = 'execution-result success';
        
        showToast('Agent executed successfully!', 'success');
        
    } catch (error) {
        console.error('Error executing agent:', error);
        resultDiv.innerHTML = `
            <strong>Error:</strong><br><br>
            ${error.message}
        `;
        resultDiv.className = 'execution-result error';
        showToast(error.message, 'error');
    }
}

/**
 * Delete an agent
 */
async function deleteAgent(agentName) {
    if (!confirm(`Are you sure you want to delete agent "${agentName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/agents/${agentName}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete agent');
        }
        
        showToast(`Agent "${agentName}" deleted successfully`, 'success');
        
        // If this was the current agent, hide execution panel
        if (currentAgent === agentName) {
            currentAgent = null;
            document.getElementById('execution-panel').style.display = 'none';
        }
        
        loadAgents();
        
    } catch (error) {
        console.error('Error deleting agent:', error);
        showToast(error.message, 'error');
    }
}

/**
 * Load execution history for the current agent
 */
async function loadExecutionHistory() {
    if (!currentAgent) {
        showToast('No agent selected', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/agents/${currentAgent}/history?limit=10`);
        if (!response.ok) {
            throw new Error('Failed to load execution history');
        }
        
        const data = await response.json();
        const historyList = document.getElementById('history-list');
        
        if (!data.history || data.history.length === 0) {
            historyList.innerHTML = '<p class="empty-state" style="padding: 1rem;">No execution history yet.</p>';
            return;
        }
        
        historyList.innerHTML = data.history.map(item => {
            const date = new Date(item.timestamp).toLocaleString();
            const statusClass = item.status === 'error' ? 'error' : '';
            const executionTime = item.execution_time ? `${item.execution_time.toFixed(2)}s` : 'N/A';
            
            // Escape HTML to prevent XSS
            const escapeHtml = (text) => {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            };
            
            const safeMessage = escapeHtml(item.message);
            const safeResponse = escapeHtml(item.response.substring(0, 200));
            const ellipsis = item.response.length > 200 ? '...' : '';
            
            return `
                <div class="history-item ${statusClass}">
                    <div class="timestamp">🕐 ${date}</div>
                    <div class="message"><strong>Message:</strong> ${safeMessage}</div>
                    <div class="response"><strong>Response:</strong> ${safeResponse}${ellipsis}</div>
                    <div class="execution-time">⏱️ Execution time: ${executionTime}</div>
                </div>
            `;
        }).join('');
        
        showToast(`Loaded ${data.history.length} execution(s)`, 'success');
        
    } catch (error) {
        console.error('Error loading execution history:', error);
        showToast(error.message, 'error');
    }
}

/**
 * Check backend health
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('Backend is healthy');
        }
    } catch (error) {
        console.warn('Backend health check failed:', error);
    }
}

// Check backend health on load
checkBackendHealth();
