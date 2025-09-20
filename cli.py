import asyncio
import os
import sys
import time
from dotenv import load_dotenv
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent import root_agent  # The orchestrator agent

load_dotenv()

# Check if using Vertex AI (recommended for Cloud Run)
use_vertex_ai = os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', 'False').lower() == 'true'

if use_vertex_ai:
    print("✅ Using Vertex AI (no API key required)")
else:
    google_api_key = os.environ.get('GOOGLE_API_KEY', '')
    if not google_api_key:
        print("❌ GOOGLE_API_KEY is not set! Please set it in your .env file or set GOOGLE_GENAI_USE_VERTEXAI=True")
        sys.exit(1)
    print("✅ API key is configured.")

async def run_pa_task(task, runner, session_service):
    session = session_service.create_session(app_name="schedule_agent_pa", user_id="cli_user")
    content = types.Content(role="user", parts=[types.Part(text=task)])
    print(f"\n📝 Task: {task}")
    print("Processing...")
    result = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id="cli_user",
        new_message=content
    ):
        if hasattr(event, 'is_final_response') and event.is_final_response:
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        result += part.text
    return result

async def main():
    print("\n============================================")
    print("🚀 SCHEDULE AGENT - CLI INTERFACE")
    print("============================================")
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="schedule_agent_pa",
    )
    print("\nAvailable commands:")
    print("  mail <summary|unread|from X>")
    print("  calendar <schedule|cancel|today>")
    print("  meet <create|cancel|list>")
    print("  drive <search X|summarize X>")
    print("  sheets <read X|write X>")
    print("  news <topic>")
    print("  exit")
    while True:
        task = input("\nEnter your command: ").strip()
        if not task or task.lower() == "exit":
            print("👋 Goodbye!")
            break
        try:
            start_time = time.time()
            result = await run_pa_task(task, runner, session_service)
            end_time = time.time()
            print("\n============================================")
            print(f"TASK COMPLETED IN {round(end_time - start_time, 1)} SECONDS")
            print("============================================")
            print(result)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
