# 🔌 Agents Builder API Usage Guide

Complete guide for using the Deep Agents Builder API programmatically.

## Base URL

```
http://localhost:8000
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

⚠️ **IMPORTANT**: Currently, the API does not require authentication (development mode only). 

**For production environments:**
- **DO NOT** deploy without authentication
- Implement API key authentication, OAuth 2.0, or JWT tokens
- Use HTTPS for all API communications
- Implement rate limiting to prevent abuse
- Consider IP whitelisting for sensitive deployments

## API Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
# Output: {"status": "healthy"}
```

**cURL Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. List Available Tools

Get information about built-in tools available to agents.

**Endpoint:** `GET /tools`

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/tools")
tools = response.json()["tools"]

for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

**cURL Example:**
```bash
curl http://localhost:8000/tools
```

---

### 3. Create an Agent

Create a new deep agent with custom configuration.

**Endpoint:** `POST /agents/create`

**Request Body:**
```json
{
  "name": "research-agent",
  "description": "An agent for conducting research",
  "system_prompt": "You are an expert researcher. Conduct thorough research and provide detailed analysis.",
  "model": "anthropic:claude-sonnet-4-20250514",
  "use_longterm_memory": false,
  "debug": false,
  "tools": [],
  "subagents": []
}
```

**Python Example:**
```python
import requests

agent_config = {
    "name": "research-agent",
    "description": "An agent for conducting research",
    "system_prompt": "You are an expert researcher. Conduct thorough research and provide detailed analysis.",
    "model": "anthropic:claude-sonnet-4-20250514",
    "use_longterm_memory": False,
    "debug": True,
    "tools": [],
    "subagents": []
}

response = requests.post(
    "http://localhost:8000/agents/create",
    json=agent_config
)

if response.status_code == 200:
    print("Agent created:", response.json())
else:
    print("Error:", response.json())
```

**JavaScript Example:**
```javascript
const agentConfig = {
  name: "research-agent",
  description: "An agent for conducting research",
  system_prompt: "You are an expert researcher. Conduct thorough research and provide detailed analysis.",
  model: "anthropic:claude-sonnet-4-20250514",
  use_longterm_memory: false,
  debug: true,
  tools: [],
  subagents: []
};

fetch('http://localhost:8000/agents/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(agentConfig)
})
  .then(response => response.json())
  .then(data => console.log('Agent created:', data))
  .catch(error => console.error('Error:', error));
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "research-agent",
    "description": "An agent for conducting research",
    "system_prompt": "You are an expert researcher.",
    "debug": true
  }'
```

---

### 4. Create an Agent with Subagents

Create an agent with specialized subagents.

**Python Example:**
```python
import requests

agent_config = {
    "name": "advanced-research-agent",
    "description": "Advanced research agent with subagents",
    "system_prompt": "You are a research coordinator. Delegate specific research tasks to subagents.",
    "model": "anthropic:claude-sonnet-4-20250514",
    "subagents": [
        {
            "name": "data-researcher",
            "description": "Specializes in data research",
            "system_prompt": "You are a data research specialist. Find and analyze data."
        },
        {
            "name": "literature-reviewer",
            "description": "Specializes in literature review",
            "system_prompt": "You are a literature review specialist. Review academic papers and summarize findings."
        }
    ]
}

response = requests.post(
    "http://localhost:8000/agents/create",
    json=agent_config
)
print(response.json())
```

---

### 5. List All Agents

Get a list of all created agents.

**Endpoint:** `GET /agents`

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/agents")
agents_data = response.json()

print(f"Total agents: {agents_data['count']}")
for agent in agents_data['agents']:
    print(f"- {agent['name']}: {agent['description']}")
    print(f"  Model: {agent['model']}")
    print(f"  Executions: {agent['execution_count']}")
```

**cURL Example:**
```bash
curl http://localhost:8000/agents
```

---

### 6. Get Agent Details

Get detailed information about a specific agent.

**Endpoint:** `GET /agents/{agent_name}`

**Python Example:**
```python
import requests

agent_name = "research-agent"
response = requests.get(f"http://localhost:8000/agents/{agent_name}")

if response.status_code == 200:
    agent = response.json()
    print(f"Agent: {agent['name']}")
    print(f"Config: {agent['config']}")
else:
    print("Agent not found")
```

**cURL Example:**
```bash
curl http://localhost:8000/agents/research-agent
```

---

### 7. Execute an Agent

Run an agent with a specific message/task.

**Endpoint:** `POST /agents/{agent_name}/execute`

**Request Body:**
```json
{
  "message": "Research the history of artificial intelligence"
}
```

**Python Example:**
```python
import requests

agent_name = "research-agent"
message = "Research the history of artificial intelligence"

response = requests.post(
    f"http://localhost:8000/agents/{agent_name}/execute",
    json={"message": message}
)

if response.status_code == 200:
    result = response.json()
    print(f"Status: {result['status']}")
    print(f"Response: {result['response']}")
    print(f"Execution time: {result['execution_time']}s")
else:
    print("Error:", response.json())
```

**Async Python Example:**
```python
import asyncio
import aiohttp

async def execute_agent(agent_name: str, message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://localhost:8000/agents/{agent_name}/execute",
            json={"message": message}
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                error = await response.json()
                raise Exception(error['detail'])

# Usage
async def main():
    result = await execute_agent("research-agent", "Research AI history")
    print(result['response'])

asyncio.run(main())
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/agents/research-agent/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Research the history of artificial intelligence"}'
```

---

### 8. Get Execution History

Get the execution history for an agent.

**Endpoint:** `GET /agents/{agent_name}/history?limit=10`

**Query Parameters:**
- `limit` (optional): Number of executions to return (default: 10)

**Python Example:**
```python
import requests

agent_name = "research-agent"
response = requests.get(
    f"http://localhost:8000/agents/{agent_name}/history",
    params={"limit": 5}
)

if response.status_code == 200:
    history = response.json()
    print(f"Total executions: {history['total']}")
    
    for execution in history['history']:
        print(f"\nTimestamp: {execution['timestamp']}")
        print(f"Message: {execution['message']}")
        print(f"Status: {execution['status']}")
        print(f"Execution time: {execution['execution_time']}s")
```

**cURL Example:**
```bash
curl "http://localhost:8000/agents/research-agent/history?limit=5"
```

---

### 9. Update an Agent

Update an existing agent's configuration.

**Endpoint:** `PUT /agents/{agent_name}`

**Request Body:** Same as create agent

**Python Example:**
```python
import requests

agent_name = "research-agent"
updated_config = {
    "name": "research-agent",  # Name must match
    "description": "Updated description",
    "system_prompt": "You are an expert researcher with updated instructions.",
    "debug": False,
    "use_longterm_memory": True
}

response = requests.put(
    f"http://localhost:8000/agents/{agent_name}",
    json=updated_config
)

if response.status_code == 200:
    print("Agent updated:", response.json())
else:
    print("Error:", response.json())
```

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/agents/research-agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "research-agent",
    "description": "Updated description",
    "system_prompt": "Updated prompt",
    "debug": false
  }'
```

---

### 10. Delete an Agent

Delete an agent and its execution history.

**Endpoint:** `DELETE /agents/{agent_name}`

**Python Example:**
```python
import requests

agent_name = "research-agent"
response = requests.delete(f"http://localhost:8000/agents/{agent_name}")

if response.status_code == 200:
    print("Agent deleted:", response.json())
else:
    print("Error:", response.json())
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/agents/research-agent
```

---

## Complete Python SDK Example

Here's a complete Python class for interacting with the API:

```python
import requests
from typing import Optional, Dict, List, Any


class DeepAgentsClient:
    """Client for interacting with Deep Agents Builder API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, str]:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        response = self.session.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()["tools"]
    
    def create_agent(
        self,
        name: str,
        system_prompt: str,
        description: str = "",
        model: Optional[str] = None,
        debug: bool = False,
        use_longterm_memory: bool = False,
        subagents: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Create a new agent"""
        config = {
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "model": model,
            "debug": debug,
            "use_longterm_memory": use_longterm_memory,
            "tools": [],
            "subagents": subagents or []
        }
        
        response = self.session.post(
            f"{self.base_url}/agents/create",
            json=config
        )
        response.raise_for_status()
        return response.json()
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        response = self.session.get(f"{self.base_url}/agents")
        response.raise_for_status()
        return response.json()["agents"]
    
    def get_agent(self, name: str) -> Dict[str, Any]:
        """Get agent details"""
        response = self.session.get(f"{self.base_url}/agents/{name}")
        response.raise_for_status()
        return response.json()
    
    def execute_agent(self, name: str, message: str) -> Dict[str, Any]:
        """Execute an agent"""
        response = self.session.post(
            f"{self.base_url}/agents/{name}/execute",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    
    def get_history(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history"""
        response = self.session.get(
            f"{self.base_url}/agents/{name}/history",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()["history"]
    
    def update_agent(
        self,
        name: str,
        system_prompt: str,
        description: str = "",
        model: Optional[str] = None,
        debug: bool = False,
        use_longterm_memory: bool = False
    ) -> Dict[str, Any]:
        """Update an existing agent"""
        config = {
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "model": model,
            "debug": debug,
            "use_longterm_memory": use_longterm_memory,
            "tools": [],
            "subagents": []
        }
        
        response = self.session.put(
            f"{self.base_url}/agents/{name}",
            json=config
        )
        response.raise_for_status()
        return response.json()
    
    def delete_agent(self, name: str) -> Dict[str, Any]:
        """Delete an agent"""
        response = self.session.delete(f"{self.base_url}/agents/{name}")
        response.raise_for_status()
        return response.json()


# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = DeepAgentsClient()
    
    # Check health
    print(client.health_check())
    
    # Create an agent
    agent = client.create_agent(
        name="research-agent",
        description="An agent for research tasks",
        system_prompt="You are an expert researcher.",
        debug=True
    )
    print(f"Created agent: {agent}")
    
    # Execute the agent
    result = client.execute_agent(
        name="research-agent",
        message="What is machine learning?"
    )
    print(f"Response: {result['response']}")
    
    # Get history
    history = client.get_history("research-agent", limit=5)
    print(f"Execution history: {len(history)} executions")
    
    # Update agent
    updated = client.update_agent(
        name="research-agent",
        system_prompt="You are an expert AI researcher.",
        description="Updated research agent"
    )
    print(f"Updated: {updated}")
    
    # List all agents
    agents = client.list_agents()
    print(f"Total agents: {len(agents)}")
    
    # Delete agent
    # client.delete_agent("research-agent")
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (e.g., invalid input, agent already exists)
- `404`: Not found (e.g., agent doesn't exist)
- `500`: Internal server error

**Python Error Handling Example:**
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/agents/create",
        json={"name": "test-agent", "system_prompt": "Test"}
    )
    response.raise_for_status()
    print(response.json())
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print(f"Bad request: {e.response.json()['detail']}")
    elif e.response.status_code == 404:
        print("Agent not found")
    elif e.response.status_code == 500:
        print(f"Server error: {e.response.json()['detail']}")
    else:
        print(f"Error: {e}")
        
except requests.exceptions.ConnectionError:
    print("Could not connect to API. Is the server running?")
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, implement rate limiting to prevent abuse.

---

## Best Practices

1. **Always check the health endpoint** before making other API calls
2. **Handle errors gracefully** with proper try-catch blocks
3. **Use meaningful agent names** for easy identification
4. **Keep execution history** for debugging and analysis
5. **Set appropriate timeouts** for long-running agent executions
6. **Use environment variables** for API URLs and keys
7. **Implement retry logic** for transient failures

---

## Environment Variables

For production use, set these environment variables:

```bash
# API Configuration
AGENTS_API_URL=http://localhost:8000

# LLM API Keys (required by deepagents)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
```

---

## Advanced Usage

### Parallel Agent Execution

```python
import concurrent.futures
import requests

def execute_agent(agent_name: str, message: str):
    response = requests.post(
        f"http://localhost:8000/agents/{agent_name}/execute",
        json={"message": message}
    )
    return response.json()

# Execute multiple agents in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(execute_agent, "agent1", "Task 1"),
        executor.submit(execute_agent, "agent2", "Task 2"),
        executor.submit(execute_agent, "agent3", "Task 3")
    ]
    
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        print(result['response'])
```

### Streaming Responses (Future Enhancement)

Currently, agent execution returns complete responses. For streaming support, this would need to be implemented using Server-Sent Events (SSE) or WebSockets.

---

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the execution history for debugging
3. Enable debug mode for detailed logs
4. Check server logs for backend errors

---

## License

This API is part of the Deep Agents Builder project and follows the same MIT license as the deepagents library.
