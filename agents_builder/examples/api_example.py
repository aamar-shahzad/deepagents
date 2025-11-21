"""
Example: Using the Deep Agents Builder API Programmatically

This script demonstrates how to interact with the Agents Builder API
to create, manage, and execute agents programmatically.

Prerequisites:
1. Start the backend server: python agents_builder/backend/main.py
2. Set ANTHROPIC_API_KEY environment variable
3. Run this script: python agents_builder/examples/api_example.py
"""

import requests
import time
from typing import Dict, Any


class AgentsClient:
    """Simple client for interacting with Agents Builder API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def create_agent(self, name: str, system_prompt: str, **kwargs) -> Dict[str, Any]:
        """Create a new agent"""
        config = {
            "name": name,
            "system_prompt": system_prompt,
            "description": kwargs.get("description", ""),
            "debug": kwargs.get("debug", False),
            "use_longterm_memory": kwargs.get("use_longterm_memory", False),
            "tools": [],
            "subagents": kwargs.get("subagents", [])
        }
        
        # Only include model if provided
        if kwargs.get("model"):
            config["model"] = kwargs.get("model")
        
        response = requests.post(f"{self.base_url}/agents/create", json=config)
        response.raise_for_status()
        return response.json()
    
    def execute_agent(self, name: str, message: str) -> Dict[str, Any]:
        """Execute an agent with a message"""
        response = requests.post(
            f"{self.base_url}/agents/{name}/execute",
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    
    def list_agents(self) -> list:
        """List all agents"""
        response = requests.get(f"{self.base_url}/agents")
        response.raise_for_status()
        return response.json()["agents"]
    
    def get_history(self, name: str, limit: int = 5) -> list:
        """Get execution history for an agent"""
        response = requests.get(
            f"{self.base_url}/agents/{name}/history",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()["history"]
    
    def delete_agent(self, name: str) -> Dict[str, Any]:
        """Delete an agent"""
        response = requests.delete(f"{self.base_url}/agents/{name}")
        response.raise_for_status()
        return response.json()


def main():
    """Main example function"""
    print("🧠🤖 Deep Agents Builder API Example\n")
    
    # Initialize client
    client = AgentsClient()
    
    # Example 1: Create a simple agent
    print("1️⃣ Creating a research agent...")
    try:
        result = client.create_agent(
            name="api-research-agent",
            description="An agent created via API for research tasks",
            system_prompt="You are an expert researcher. Provide concise, accurate answers based on your knowledge.",
            debug=True
        )
        print(f"✅ Agent created: {result['message']}\n")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("⚠️  Agent already exists, using existing agent\n")
        else:
            raise
    
    # Example 2: Execute the agent
    print("2️⃣ Executing the agent...")
    result = client.execute_agent(
        name="api-research-agent",
        message="What are the key benefits of using AI agents?"
    )
    print(f"✅ Agent response:")
    print(f"   {result['response'][:200]}...")
    print(f"   Execution time: {result['execution_time']:.2f}s\n")
    
    # Example 3: Execute with another query
    print("3️⃣ Executing another query...")
    result = client.execute_agent(
        name="api-research-agent",
        message="Explain machine learning in simple terms."
    )
    print(f"✅ Agent response:")
    print(f"   {result['response'][:200]}...")
    print(f"   Execution time: {result['execution_time']:.2f}s\n")
    
    # Example 4: Get execution history
    print("4️⃣ Getting execution history...")
    history = client.get_history("api-research-agent", limit=5)
    print(f"✅ Found {len(history)} executions:")
    for i, execution in enumerate(history, 1):
        print(f"   {i}. [{execution['status']}] {execution['message'][:50]}...")
    print()
    
    # Example 5: List all agents
    print("5️⃣ Listing all agents...")
    agents = client.list_agents()
    print(f"✅ Total agents: {len(agents)}")
    for agent in agents:
        print(f"   - {agent['name']}: {agent['execution_count']} executions")
    print()
    
    # Example 6: Create an agent with subagents
    print("6️⃣ Creating an agent with subagents...")
    try:
        result = client.create_agent(
            name="coordinator-agent",
            description="A coordinator agent that delegates to specialists",
            system_prompt="You are a coordinator. Delegate specific tasks to your subagents.",
            subagents=[
                {
                    "name": "researcher",
                    "description": "Research specialist",
                    "system_prompt": "You are a research specialist. Conduct thorough research.",
                    "tools": []
                },
                {
                    "name": "analyzer",
                    "description": "Data analysis specialist",
                    "system_prompt": "You are a data analyst. Analyze and interpret data.",
                    "tools": []
                }
            ]
        )
        print(f"✅ Coordinator agent created with 2 subagents\n")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("⚠️  Coordinator agent already exists\n")
        else:
            raise
    
    print("✨ Example completed successfully!")
    print("\n💡 Tips:")
    print("   - View API docs at: http://localhost:8000/docs")
    print("   - Check API_USAGE.md for comprehensive documentation")
    print("   - Use the web UI at: http://localhost:8080")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print("   Make sure the backend server is running:")
        print("   python agents_builder/backend/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
