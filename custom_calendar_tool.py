# custom_calendar_tool.py
"""
Custom Calendar Tool for Schedule-Agent.
Provides comprehensive Google Calendar operations as Google ADK Function Tools.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from google.adk.tools import FunctionTool
from simple_google_auth import get_google_service

def _get_calendar_service():
    """Get Calendar service instance."""
    return get_google_service('calendar', 'v3')

def get_today_events() -> str:
    """Get today's calendar events."""
    try:
        service = _get_calendar_service()
        
        # Get today's date range
        today = datetime.now().date()
        time_min = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return "📅 No events scheduled for today."
        
        # Format output
        output = f"📅 **Today's Events ({len(events)}):**\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            attendees = event.get('attendees', [])
            
            output += f"{i}. **{summary}**\n"
            output += f"   Time: {start}\n"
            if attendees:
                attendee_emails = [a.get('email', '') for a in attendees[:3]]
                output += f"   Attendees: {', '.join(attendee_emails)}\n"
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving today's events: {str(e)}"

def get_week_events() -> str:
    """Get this week's calendar events."""
    try:
        service = _get_calendar_service()
        
        # Get week's date range
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        time_min = datetime.combine(week_start, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(week_end, datetime.max.time()).isoformat() + 'Z'
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return "📅 No events scheduled for this week."
        
        # Format output
        output = f"📅 **This Week's Events ({len(events)}):**\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            attendees = event.get('attendees', [])
            
            output += f"{i}. **{summary}**\n"
            output += f"   Time: {start}\n"
            if attendees:
                attendee_emails = [a.get('email', '') for a in attendees[:3]]
                output += f"   Attendees: {', '.join(attendee_emails)}\n"
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error retrieving week's events: {str(e)}"

def create_event(title: str, start_time: str, end_time: str, 
                attendees: Optional[List[str]] = None, 
                description: Optional[str] = None) -> str:
    """Create a new calendar event."""
    try:
        service = _get_calendar_service()
        
        # Prepare event
        event = {
            'summary': title,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        
        if description:
            event['description'] = description
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Create event
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        event_id = created_event.get('id', 'Unknown')
        event_link = created_event.get('htmlLink', 'No link')
        
        return f"✅ Event created successfully!\nEvent ID: {event_id}\nTitle: {title}\nStart: {start_time}\nEnd: {end_time}\nLink: {event_link}"
        
    except Exception as e:
        return f"❌ Error creating event: {str(e)}"

def delete_event(event_id: str) -> str:
    """Delete a calendar event."""
    try:
        service = _get_calendar_service()
        
        # Delete event
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        return f"✅ Event {event_id} deleted successfully!"
        
    except Exception as e:
        return f"❌ Error deleting event: {str(e)}"

def search_events(query: str, max_results: int = 20) -> str:
    """Search for calendar events."""
    try:
        service = _get_calendar_service()
        
        if not query or not query.strip():
            return "❌ Search query cannot be empty"
        
        # Search events
        events_result = service.events().list(
            calendarId='primary',
            q=query.strip(),
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No events found for query: '{query}'"
        
        # Format output
        output = f"�� Found {len(events)} events for '{query}':\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            attendees = event.get('attendees', [])
            
            output += f"{i}. **{summary}**\n"
            output += f"   Time: {start}\n"
            if attendees:
                attendee_emails = [a.get('email', '') for a in attendees[:3]]
                output += f"   Attendees: {', '.join(attendee_emails)}\n"
            output += "\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error searching events: {str(e)}"

def get_free_time_slots(date: str, duration_minutes: int = 60) -> str:
    """Get available time slots for a specific date."""
    try:
        service = _get_calendar_service()
        
        # Get date range
        target_date = datetime.fromisoformat(date).date()
        time_min = datetime.combine(target_date, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(target_date, datetime.max.time()).isoformat() + 'Z'
        
        # Get events for the day
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Find free time slots
        free_slots = []
        current_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        
        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
        
        for event in sorted_events:
            event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            if event_start > current_time:
                # Check if there's enough time before this event
                time_diff = (event_start - current_time).total_seconds() / 60
                if time_diff >= duration_minutes:
                    free_slots.append({
                        'start': current_time.strftime('%H:%M'),
                        'end': event_start.strftime('%H:%M'),
                        'duration': int(time_diff)
                    })
            current_time = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        
        # Check for free time after last event
        if current_time < end_time:
            time_diff = (end_time - current_time).total_seconds() / 60
            if time_diff >= duration_minutes:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M'),
                    'duration': int(time_diff)
                })
        
        if not free_slots:
            return f"❌ No free time slots of {duration_minutes} minutes found for {date}"
        
        # Format output
        output = f"⏰ **Free time slots for {date} (minimum {duration_minutes} minutes):**\n\n"
        for i, slot in enumerate(free_slots, 1):
            output += f"{i}. {slot['start']} - {slot['end']} ({slot['duration']} minutes)\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error finding free time slots: {str(e)}"

# Create Google ADK Function Tools
calendar_tools = [
    FunctionTool.from_defaults(
        name="get_today_events",
        description="Get today's calendar events",
        func=get_today_events
    ),
    FunctionTool.from_defaults(
        name="get_week_events",
        description="Get this week's calendar events",
        func=get_week_events
    ),
    FunctionTool.from_defaults(
        name="create_event",
        description="Create a new calendar event",
        func=create_event
    ),
    FunctionTool.from_defaults(
        name="delete_event",
        description="Delete a calendar event by event ID",
        func=delete_event
    ),
    FunctionTool.from_defaults(
        name="search_events",
        description="Search for calendar events by query",
        func=search_events
    ),
    FunctionTool.from_defaults(
        name="get_free_time_slots",
        description="Get available time slots for a specific date",
        func=get_free_time_slots
    )
]