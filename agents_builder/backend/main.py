"""Agents Builder Backend API

A FastAPI application for creating and managing deep agents.
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from deepagents import create_deep_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Deep Agents Builder API",
    description="API for creating and managing deep agents",
    version="1.0.0"
)

# Configure CORS
# WARNING: For production, replace "*" with specific allowed origins
# Example: allow_origins=["https://yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only - allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for agents
# WARNING: This is NOT persistent and NOT thread-safe for production use.
# For production, use a proper database (PostgreSQL, MongoDB, etc.)
# Data will be lost when the server restarts.
agents_store: dict[str, Any] = {}

# Execution history storage
execution_history: dict[str, list[dict[str, Any]]] = {}


class ToolConfig(BaseModel):
    """Configuration for a tool"""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class SubAgentConfig(BaseModel):
    """Configuration for a subagent"""
    name: str
    description: str
    system_prompt: str
    tools: list[str] = Field(default_factory=list)


class AgentConfig(BaseModel):
    """Configuration for creating a deep agent"""
    name: str
    description: str = ""
    system_prompt: str
    tools: list[str] = Field(default_factory=list)
    subagents: list[SubAgentConfig] = Field(default_factory=list)
    model: str | None = None
    use_longterm_memory: bool = False
    debug: bool = False


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent"""
    agent_name: str
    message: str


class AgentResponse(BaseModel):
    """Response from agent execution"""
    agent_name: str
    response: str
    status: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Deep Agents Builder API",
        "version": "1.0.0",
        "endpoints": {
            "/agents": "List all agents",
            "/agents/create": "Create a new agent",
            "/agents/{name}": "Get agent details",
            "/agents/{name}": "Update an agent (PUT)",
            "/agents/{name}/execute": "Execute an agent",
            "/agents/{name}/history": "Get execution history",
            "/tools": "List available tools",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/tools")
async def list_tools():
    """List available built-in tools"""
    return {
        "tools": [
            {
                "name": "write_todos",
                "description": "Planning tool for breaking down tasks",
                "category": "planning",
                "builtin": True
            },
            {
                "name": "ls",
                "description": "List files in filesystem",
                "category": "filesystem",
                "builtin": True
            },
            {
                "name": "read_file",
                "description": "Read file contents",
                "category": "filesystem",
                "builtin": True
            },
            {
                "name": "write_file",
                "description": "Write to a file",
                "category": "filesystem",
                "builtin": True
            },
            {
                "name": "edit_file",
                "description": "Edit an existing file",
                "category": "filesystem",
                "builtin": True
            },
            {
                "name": "task",
                "description": "Spawn a subagent for a task",
                "category": "subagents",
                "builtin": True
            }
        ]
    }


@app.post("/agents/create")
async def create_agent(config: AgentConfig):
    """Create a new deep agent"""
    try:
        logger.info(f"Creating agent: {config.name}")

        # Check if agent already exists
        if config.name in agents_store:
            raise HTTPException(status_code=400, detail="Agent already exists")

        # Create the agent
        agent_config = {
            "system_prompt": config.system_prompt,
        }

        if config.model:
            agent_config["model"] = config.model

        if config.use_longterm_memory:
            agent_config["use_longterm_memory"] = True
        
        if config.debug:
            agent_config["debug"] = True

        # Create subagents if specified
        if config.subagents:
            subagents = []
            for subagent in config.subagents:
                subagents.append({
                    "name": subagent.name,
                    "description": subagent.description,
                    "system_prompt": subagent.system_prompt,
                    "tools": []  # Tools would need to be resolved
                })
            agent_config["subagents"] = subagents

        # Create the agent (note: tools need to be actual function objects)
        agent = create_deep_agent(**agent_config)

        # Store agent configuration
        agents_store[config.name] = {
            "config": config.model_dump(),
            "agent": agent,
            "created_at": None  # Could add timestamp
        }

        logger.info(f"Agent created successfully: {config.name}")

        return {
            "status": "success",
            "message": f"Agent '{config.name}' created successfully",
            "agent": {
                "name": config.name,
                "system_prompt": config.system_prompt[:100] + "..." if len(config.system_prompt) > 100 else config.system_prompt
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List all created agents"""
    agents = []
    for name, data in agents_store.items():
        config = data["config"]
        agents.append({
            "name": name,
            "description": config.get("description", ""),
            "system_prompt": config["system_prompt"][:100] + "..."
                           if len(config["system_prompt"]) > 100
                           else config["system_prompt"],
            "num_subagents": len(config.get("subagents", [])),
            "model": config.get("model", "claude-sonnet-4-5-20250929"),
            "debug": config.get("debug", False),
            "use_longterm_memory": config.get("use_longterm_memory", False),
            "execution_count": len(execution_history.get(name, []))
        })

    return {"agents": agents, "count": len(agents)}


@app.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get details of a specific agent"""
    if agent_name not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")

    data = agents_store[agent_name]
    return {
        "name": agent_name,
        "config": data["config"]
    }


@app.post("/agents/{agent_name}/execute")
async def execute_agent(agent_name: str, request: dict[str, str]):
    """Execute an agent with a message"""
    import datetime
    
    try:
        if agent_name not in agents_store:
            raise HTTPException(status_code=404, detail="Agent not found")

        message = request.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        logger.info(f"Executing agent: {agent_name}")
        agent = agents_store[agent_name]["agent"]
        
        start_time = datetime.datetime.now()

        # Execute the agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": message}]
        })
        
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Extract the response
        response_content = ""
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                response_content = last_message.content
            elif isinstance(last_message, dict):
                response_content = last_message.get("content", str(last_message))
            else:
                response_content = str(last_message)
        
        # Save to execution history
        if agent_name not in execution_history:
            execution_history[agent_name] = []
        
        execution_history[agent_name].append({
            "timestamp": start_time.isoformat(),
            "message": message,
            "response": response_content,
            "execution_time": execution_time,
            "status": "success"
        })

        return {
            "status": "success",
            "agent_name": agent_name,
            "response": response_content,
            "execution_time": execution_time
        }

    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {e!s}")
        
        # Save failed execution to history
        if agent_name in agents_store:
            if agent_name not in execution_history:
                execution_history[agent_name] = []
            
            # Use the message variable that was already extracted
            error_message = message if 'message' in locals() else request.get("message", "")
            
            execution_history[agent_name].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "message": error_message,
                "response": str(e),
                "execution_time": 0,
                "status": "error"
            })
        
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/agents/{agent_name}")
async def update_agent(agent_name: str, config: AgentConfig):
    """Update an existing agent"""
    try:
        if agent_name not in agents_store:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Verify the name matches
        if config.name != agent_name:
            raise HTTPException(status_code=400, detail="Agent name cannot be changed")
        
        logger.info(f"Updating agent: {agent_name}")
        
        # Create the updated agent with new configuration
        agent_config = {
            "system_prompt": config.system_prompt,
        }
        
        if config.model:
            agent_config["model"] = config.model
        
        if config.use_longterm_memory:
            agent_config["use_longterm_memory"] = True
        
        if config.debug:
            agent_config["debug"] = True
        
        # Create subagents if specified
        if config.subagents:
            subagents = []
            for subagent in config.subagents:
                subagents.append({
                    "name": subagent.name,
                    "description": subagent.description,
                    "system_prompt": subagent.system_prompt,
                    "tools": []
                })
            agent_config["subagents"] = subagents
        
        # Recreate the agent
        agent = create_deep_agent(**agent_config)
        
        # Update stored configuration
        agents_store[agent_name]["config"] = config.model_dump()
        agents_store[agent_name]["agent"] = agent
        
        logger.info(f"Agent updated successfully: {agent_name}")
        
        return {
            "status": "success",
            "message": f"Agent '{agent_name}' updated successfully",
            "agent": {
                "name": config.name,
                "description": config.description
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_name}/history")
async def get_execution_history(agent_name: str, limit: int = 10):
    """Get execution history for an agent"""
    if agent_name not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    history = execution_history.get(agent_name, [])
    # Return most recent executions first
    return {
        "agent_name": agent_name,
        "history": history[-limit:][::-1],
        "total": len(history)
    }


@app.delete("/agents/{agent_name}")
async def delete_agent(agent_name: str):
    """Delete an agent"""
    if agent_name not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")

    del agents_store[agent_name]
    
    # Also delete execution history
    if agent_name in execution_history:
        del execution_history[agent_name]

    return {
        "status": "success",
        "message": f"Agent '{agent_name}' deleted successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
