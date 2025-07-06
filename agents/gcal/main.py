#!/usr/bin/env python3
"""
GCalA - Calendar Operations Agent
Handles calendar operations via MCP server integration
Following clean architecture patterns from EXAMPLE_PY.md
"""

from agents.base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, to_greeter, BASE_INSTRUCTIONS
from livekit.agents import function_tool
from livekit.plugins import groq
from typing import Annotated
from pydantic import Field

class GCalA(BaseAgent):
    """Google Calendar agent that handles calendar operations"""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Alfred's Calendar agent John. Handle calendar operations briefly. "
                "Schedule meetings, create events, query schedules.\n" +
                BASE_INSTRUCTIONS
            ),
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["gcal"]),
            tools=[to_greeter],
        )

    async def schedule_meeting_internal(
        self,
        person: str,
        duration: int = 30,
        timeframe: str = "today",
        context: RunContext_T = None,
    ) -> str:
        """Internal method to schedule a meeting"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Calendar operations
        # For now, return Batman-themed stub response
        if not userdata.scheduled_meetings:
            userdata.scheduled_meetings = []

        meeting_details = f"{duration}-minute meeting with {person} {timeframe}"
        userdata.scheduled_meetings.append(meeting_details)

        # Batman narrative for demo scenario
        if person.lower() == "sarah":
            return f"Meeting with Sarah scheduled for {timeframe} morning, sir."

        return f"Meeting with {person} scheduled for {timeframe}."

    async def create_calendar_event_internal(
        self,
        activity: str,
        time: str = "",
        date: str = "today",
        context: RunContext_T = None,
    ) -> str:
        """Internal method to create calendar event"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Calendar operations
        # For now, return Batman-themed stub response
        if not userdata.calendar_events:
            userdata.calendar_events = []

        event_details = f"{activity} at {time} on {date}" if time else f"{activity} on {date}"
        userdata.calendar_events.append(event_details)

        return f"Event added: {event_details}."

    async def query_todays_schedule_internal(self, context: RunContext_T) -> str:
        """Internal method to query today's schedule"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Calendar operations
        # For now, return Batman-themed stub response matching demo scenario
        todays_events = [
            "9:00 AM - Wayne Enterprises board standup",
            "2:00 PM - Client call with Gotham City contractors"
        ]

        if not userdata.meeting_times:
            userdata.meeting_times = []
        userdata.meeting_times.extend(todays_events)

        return f"Today: 9am standup, 2pm client call."

    async def query_tomorrows_schedule_internal(self, context: RunContext_T) -> str:
        """Internal method to query tomorrow's schedule"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Calendar operations
        # For now, return Batman-themed stub response
        tomorrows_events = [
            "10:00 AM - Wayne Foundation charity meeting",
            "1:00 PM - Lunch with Commissioner Gordon",
            "3:30 PM - R&D sync with Lucius Fox"
        ]

        if not userdata.meeting_times:
            userdata.meeting_times = []
        userdata.meeting_times.extend(tomorrows_events)

        return f"Tomorrow: 10am charity meeting, 1pm lunch with Gordon, 3:30pm R&D sync."

    async def set_reminder_internal(
        self,
        reminder_text: str,
        time: str = "",
        context: RunContext_T = None,
    ) -> str:
        """Internal method to set a reminder"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Calendar operations
        # For now, return Batman-themed stub response
        if not userdata.calendar_events:
            userdata.calendar_events = []

        reminder_details = f"Reminder: {reminder_text}" + (f" at {time}" if time else "")
        userdata.calendar_events.append(reminder_details)

        return f"Reminder set: {reminder_details}."

    @function_tool()
    async def schedule_meeting(
        self,
        person: Annotated[str, Field(description="Person to meet with")],
        duration: Annotated[int, Field(description="Meeting duration in minutes")] = 30,
        timeframe: Annotated[str, Field(description="When to schedule (today, tomorrow, etc.)")] = "today",
        context: RunContext_T = None,
    ) -> str:
        """Schedule a meeting with someone.
        Confirm the person, duration, and timeframe before scheduling."""
        agent = context.session.current_agent
        if isinstance(agent, GCalA):
            return await agent.schedule_meeting_internal(person, duration, timeframe, context)
        else:
            userdata = context.userdata
            if not userdata.scheduled_meetings:
                userdata.scheduled_meetings = []
            meeting_details = f"{duration}-minute meeting with {person} {timeframe}"
            userdata.scheduled_meetings.append(meeting_details)
            return f"Meeting with {person} scheduled for {timeframe}."

    @function_tool()
    async def create_calendar_event(
        self,
        activity: Annotated[str, Field(description="Activity or event description")],
        time: Annotated[str, Field(description="Time for the event")] = "",
        date: Annotated[str, Field(description="Date for the event")] = "today",
        context: RunContext_T = None,
    ) -> str:
        """Create a calendar event or reminder.
        Confirm the activity, time, and date before creating."""
        agent = context.session.current_agent
        if isinstance(agent, GCalA):
            return await agent.create_calendar_event_internal(activity, time, date, context)
        else:
            userdata = context.userdata
            if not userdata.calendar_events:
                userdata.calendar_events = []
            event_details = f"{activity} at {time} on {date}" if time else f"{activity} on {date}"
            userdata.calendar_events.append(event_details)
            return f"Event added: {event_details}."

    @function_tool()
    async def query_todays_schedule(self, context: RunContext_T) -> str:
        """Query today's schedule and return scheduled start times.
        This will show all events scheduled for today."""
        agent = context.session.current_agent
        if isinstance(agent, GCalA):
            return await agent.query_todays_schedule_internal(context)
        else:
            userdata = context.userdata
            todays_events = [
                "9:00 AM - Wayne Enterprises board standup",
                "2:00 PM - Client call with Gotham City contractors"
            ]
            if not userdata.meeting_times:
                userdata.meeting_times = []
            userdata.meeting_times.extend(todays_events)
            return f"Today: 9am standup, 2pm client call."

    @function_tool()
    async def query_tomorrows_schedule(self, context: RunContext_T) -> str:
        """Query tomorrow's schedule and return scheduled events.
        This will show all events scheduled for tomorrow."""
        agent = context.session.current_agent
        if isinstance(agent, GCalA):
            return await agent.query_tomorrows_schedule_internal(context)
        else:
            userdata = context.userdata
            tomorrows_events = [
                "10:00 AM - Wayne Foundation charity meeting",
                "1:00 PM - Lunch with Commissioner Gordon",
                "3:30 PM - R&D sync with Lucius Fox"
            ]
            if not userdata.meeting_times:
                userdata.meeting_times = []
            userdata.meeting_times.extend(tomorrows_events)
            return f"Tomorrow: 10am charity meeting, 1pm lunch with Gordon, 3:30pm R&D sync."

    @function_tool()
    async def set_reminder(
        self,
        reminder_text: Annotated[str, Field(description="What to be reminded about")],
        time: Annotated[str, Field(description="When to be reminded")] = "",
        context: RunContext_T = None,
    ) -> str:
        """Set a reminder for something.
        Confirm the reminder text and time before setting."""
        agent = context.session.current_agent
        if isinstance(agent, GCalA):
            return await agent.set_reminder_internal(reminder_text, time, context)
        else:
            userdata = context.userdata
            if not userdata.calendar_events:
                userdata.calendar_events = []
            reminder_details = f"Reminder: {reminder_text}" + (f" at {time}" if time else "")
            userdata.calendar_events.append(reminder_details)
            return f"Reminder set: {reminder_details}."
