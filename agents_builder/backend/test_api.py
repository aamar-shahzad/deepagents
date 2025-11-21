"""
Simple tests for the Agents Builder API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Deep Agents Builder API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_tools():
    """Test list tools endpoint"""
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    
    # Check that built-in tools are present
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "write_todos" in tool_names
    assert "ls" in tool_names
    assert "read_file" in tool_names


def test_list_agents_empty():
    """Test listing agents when none exist"""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "count" in data


def test_create_agent():
    """Test creating a new agent"""
    agent_config = {
        "name": "test-agent",
        "system_prompt": "You are a test agent",
        "tools": [],
        "subagents": [],
        "use_longterm_memory": False
    }
    
    response = client.post("/agents/create", json=agent_config)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "test-agent" in data["message"]


def test_create_duplicate_agent():
    """Test creating an agent with duplicate name"""
    agent_config = {
        "name": "test-agent",
        "system_prompt": "You are a test agent",
        "tools": [],
        "subagents": []
    }
    
    # First creation should succeed
    client.post("/agents/create", json=agent_config)
    
    # Second creation should fail
    response = client.post("/agents/create", json=agent_config)
    assert response.status_code == 400


def test_get_agent():
    """Test getting agent details"""
    # Create agent first
    agent_config = {
        "name": "get-test-agent",
        "system_prompt": "You are a get test agent",
        "tools": []
    }
    client.post("/agents/create", json=agent_config)
    
    # Get agent
    response = client.get("/agents/get-test-agent")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "get-test-agent"
    assert "config" in data


def test_get_nonexistent_agent():
    """Test getting a nonexistent agent"""
    response = client.get("/agents/nonexistent")
    assert response.status_code == 404


def test_delete_agent():
    """Test deleting an agent"""
    # Create agent first
    agent_config = {
        "name": "delete-test-agent",
        "system_prompt": "You are a delete test agent",
        "tools": []
    }
    client.post("/agents/create", json=agent_config)
    
    # Delete agent
    response = client.delete("/agents/delete-test-agent")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify deletion
    response = client.get("/agents/delete-test-agent")
    assert response.status_code == 404


def test_delete_nonexistent_agent():
    """Test deleting a nonexistent agent"""
    response = client.delete("/agents/nonexistent")
    assert response.status_code == 404


def test_create_agent_with_subagents():
    """Test creating an agent with subagents"""
    agent_config = {
        "name": "agent-with-subagents",
        "system_prompt": "You are a main agent",
        "tools": [],
        "subagents": [
            {
                "name": "sub1",
                "description": "First subagent",
                "system_prompt": "You are a subagent",
                "tools": []
            }
        ]
    }
    
    response = client.post("/agents/create", json=agent_config)
    assert response.status_code == 200
    
    # Verify subagent is included
    response = client.get("/agents/agent-with-subagents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["config"]["subagents"]) == 1


def test_update_agent():
    """Test updating an existing agent"""
    # First create an agent
    agent_config = {
        "name": "update-test-agent",
        "description": "Original description",
        "system_prompt": "Original prompt",
        "debug": False
    }
    client.post("/agents/create", json=agent_config)
    
    # Update the agent
    updated_config = {
        "name": "update-test-agent",
        "description": "Updated description",
        "system_prompt": "Updated prompt",
        "debug": True
    }
    
    response = client.put("/agents/update-test-agent", json=updated_config)
    assert response.status_code == 200
    
    # Verify the update
    response = client.get("/agents/update-test-agent")
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["description"] == "Updated description"
    assert data["config"]["system_prompt"] == "Updated prompt"
    assert data["config"]["debug"] is True


def test_execution_history():
    """Test execution history tracking"""
    # Create an agent
    agent_config = {
        "name": "history-test-agent",
        "system_prompt": "You are a test agent"
    }
    client.post("/agents/create", json=agent_config)
    
    # Get initial history (should be empty)
    response = client.get("/agents/history-test-agent/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 0
    
    # Note: Actual execution test would require the agent to work
    # which needs proper API keys, so we skip that part


def test_agent_with_description_and_debug():
    """Test creating agent with description and debug mode"""
    agent_config = {
        "name": "feature-test-agent",
        "description": "An agent with all features",
        "system_prompt": "You are a feature-rich agent",
        "debug": True,
        "use_longterm_memory": False
    }
    
    response = client.post("/agents/create", json=agent_config)
    assert response.status_code == 200
    
    # Verify the features are saved
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    
    # Find our agent
    agent = next((a for a in data["agents"] if a["name"] == "feature-test-agent"), None)
    assert agent is not None
    assert agent["description"] == "An agent with all features"
    assert agent["debug"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
