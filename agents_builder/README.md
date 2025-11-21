# 🧠🤖 Deep Agents Builder UI

A full-stack web application for creating and managing deep agents using the `deepagents` library.

## Features

- **Visual Agent Builder**: Create deep agents through an intuitive web interface
- **Agent Management**: List, execute, and delete agents
- **Subagent Configuration**: Add specialized subagents to your main agents
- **Real-time Execution**: Run agents and see results in the browser
- **Built-in Tools**: Automatic access to planning, filesystem, and subagent tools

## Architecture

The application consists of two main components:

### Backend (FastAPI)
- RESTful API for agent management
- Endpoints for creating, listing, executing, and deleting agents
- In-memory storage (can be extended to use a database)
- CORS enabled for local development

### Frontend (HTML/CSS/JavaScript)
- Modern, responsive web interface
- Agent configuration forms
- Real-time agent execution
- Toast notifications for user feedback

## Installation

### Prerequisites

- Python 3.11+
- pip or uv package manager

### Backend Setup

1. Navigate to the backend directory:
```bash
cd agents_builder/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install ../../  # Install the deepagents package
```

3. Set up environment variables (if needed):
```bash
export ANTHROPIC_API_KEY="your-api-key"  # Required for default model
```

4. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd agents_builder/frontend
```

2. Open the application:
   - Simply open `index.html` in a web browser, or
   - Serve it with a simple HTTP server:
   ```bash
   python -m http.server 8080
   ```
   Then visit `http://localhost:8080`

## Usage

### Creating an Agent

1. Fill in the agent configuration form:
   - **Agent Name**: Unique identifier for your agent
   - **Model**: Choose the LLM model (or use default)
   - **System Prompt**: Define the agent's role and instructions
   - **Long-term Memory**: Enable if you want persistent memory

2. (Optional) Add subagents:
   - Click "Add Subagent"
   - Configure name, description, and prompt for each subagent

3. Click "Create Agent"

### Executing an Agent

1. Click the "Execute" button on any agent card
2. Enter your message/task in the text area
3. Click "Run Agent"
4. View the results in the execution panel

### Managing Agents

- **View All Agents**: See all created agents in the right panel
- **Delete Agent**: Click the "Delete" button on any agent card

## API Endpoints

### GET /
Root endpoint with API information

### GET /health
Health check endpoint

### GET /tools
List available built-in tools

### POST /agents/create
Create a new agent
```json
{
  "name": "my-agent",
  "system_prompt": "You are an expert...",
  "model": "openai:gpt-4o",
  "use_longterm_memory": false,
  "tools": [],
  "subagents": []
}
```

### GET /agents
List all agents

### GET /agents/{agent_name}
Get details of a specific agent

### POST /agents/{agent_name}/execute
Execute an agent
```json
{
  "message": "What is LangGraph?"
}
```

### DELETE /agents/{agent_name}
Delete an agent

## Built-in Tools

All agents automatically have access to:

- **Planning Tools**: `write_todos` for task decomposition
- **Filesystem Tools**: `ls`, `read_file`, `write_file`, `edit_file`
- **Subagent Tools**: `task` for spawning subagents

## Example Agent Configurations

### Research Agent
```json
{
  "name": "research-agent",
  "system_prompt": "You are an expert researcher. Your job is to conduct thorough research and write detailed reports. Use the filesystem to save your findings and the planning tool to organize your work.",
  "model": "anthropic:claude-sonnet-4-20250514"
}
```

### Code Review Agent
```json
{
  "name": "code-reviewer",
  "system_prompt": "You are a senior code reviewer. Analyze code for bugs, performance issues, and best practices. Provide constructive feedback.",
  "model": "openai:gpt-4o"
}
```

## Development

### Backend Development

The backend uses FastAPI with the following structure:
- `main.py`: Main application file with all endpoints
- `requirements.txt`: Python dependencies

To add new endpoints, modify `main.py` and follow the existing patterns.

### Frontend Development

The frontend is a vanilla JavaScript application:
- `index.html`: Main HTML structure
- `styles.css`: Styling (CSS variables for easy theming)
- `app.js`: JavaScript logic

To customize the UI, modify the CSS variables in `styles.css` or add new features in `app.js`.

## Production Considerations

For production deployment:

1. **Backend**:
   - Use a proper database instead of in-memory storage
   - Add authentication and authorization
   - Configure CORS for specific origins
   - Use environment variables for configuration
   - Deploy with Gunicorn/Uvicorn behind a reverse proxy

2. **Frontend**:
   - Build with a proper bundler (Webpack, Vite)
   - Minify assets
   - Use environment variables for API URL
   - Deploy to CDN or static hosting

3. **Security**:
   - Add rate limiting
   - Validate all inputs
   - Sanitize outputs
   - Use HTTPS
   - Implement proper API key management

## Troubleshooting

### Backend not connecting
- Ensure the backend is running on port 8000
- Check that all dependencies are installed
- Verify API keys are set in environment variables

### CORS errors
- Make sure CORS is enabled in the backend
- Check that the frontend is accessing the correct API URL

### Agent execution fails
- Verify that the API keys for the selected model are set
- Check the backend logs for detailed error messages
- Ensure the system prompt is valid

## License

This project is part of the deepagents package and follows the same MIT license.

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.
