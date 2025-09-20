"""
Main Orchestrator Agent for the Personal Assistant (PA) System.
This file defines the root agent and integrates specialized agents
(Gmail, Calendar, Meet, Drive, News) as tools.
"""

from google.adk.agents import Agent
from google.adk.tools import agent_tool

# Import specialized agents
from .gmail_agent import gmail_agent
from .calendar_agent import calendar_agent
from .drive_agent import drive_agent
from .news_agent import news_agent

# Define the main orchestrator agent
root_agent = Agent(
    model="gemini-2.0-flash",  # You could switch to gemini-1.5-pro for heavier synthesis tasks
    name="pa_orchestrator",
    description="Orchestrates Gmail, Calendar, Meet, Drive, and News agents to act as a complete Personal Assistant.",
    
    # Expose specialized agents as tools
    tools=[
        agent_tool.AgentTool(agent=gmail_agent),
        agent_tool.AgentTool(agent=calendar_agent),
        agent_tool.AgentTool(agent=drive_agent),
        agent_tool.AgentTool(agent=news_agent),
    ],

    # Root Orchestrator Instruction
    instruction="""You are a Personal Assistant Orchestrator. 
Your role is to understand the user's request and coordinate specialized agents to fulfill it. 
You do not execute tasks directly; instead, you:
1. Identify which specialized agent(s) are needed.
2. Forward the request to the correct agent(s).
3. Collect their outputs.
4. Present the final response clearly and professionally.

Capabilities include:
- Summarizing, searching, drafting, and organizing Gmail emails.
- Scheduling, rescheduling, and canceling calendar events.
- Creating, attaching, and sharing Google Meet links.
- Searching, summarizing, and organizing Google Drive files.
- Gathering and summarizing recent news or research (finance, weather, sports, tech, etc.).

Rules:
- Always confirm before irreversible actions (sending/deleting emails, sharing/deleting files, overwriting data).
- If details are missing (time, participants, file name, etc.), ask for clarification before proceeding.
- Provide results in a structured, concise, and professional format.
- Use proper error handling and provide helpful error messages.

Final Output:
- Combine results from multiple agents into one cohesive response.
- Present answers in clear sections if multiple tools were used.
- Include relevant metadata (timestamps, IDs, etc.) when appropriate.
"""
)
