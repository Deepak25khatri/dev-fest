from google.adk.tools import FunctionTool
# Gmail tool
gmail_list_tool = FunctionTool.from_defaults(
    name="gmail_list_snippets",
    description="Return recent email snippets",
    func=lambda: list_messages_snippets(5)  # import function or wrap
)
# Calendar tool
calendar_create_tool = FunctionTool.from_defaults(
    name="calendar_create_event_with_meet",
    description="Create calendar event and return Meet link",
    func=lambda title, start, end, attendees=None, desc=None: create_event_with_meet(title, start, end, attendees, desc)
)
# Drive tool
drive_search_tool = FunctionTool.from_defaults(
    name="drive_search_files",
    description="Search drive files by query",
    func=lambda q: search_files(q)
)
