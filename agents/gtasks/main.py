#!/usr/bin/env python3
"""
GTasksA - Google Tasks Management Agent
Handles task operations via MCP server integration
Following clean architecture patterns from EXAMPLE_PY.md
"""

from agents.base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, to_greeter, BASE_INSTRUCTIONS
from livekit.agents import function_tool, FunctionTool
from livekit.plugins import groq
from typing import Annotated
from pydantic import Field

class GTasksA(BaseAgent):
    """Google Tasks agent that handles task management operations"""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Alfred's Tasks helper Bill. Handle task operations briefly.\n" +
                "Create tasks, set deadlines, track progress.\n" +
                BASE_INSTRUCTIONS
            ),
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["gtasks"]),
            tools=[to_greeter],
        )

    async def create_task_internal(
        self,
        task_description: str,
        deadline: str = "",
        priority: str = "normal",
        context: RunContext_T = None,
    ) -> str:
        """Internal method to create a task"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Tasks operations
        # For now, return Batman-themed stub response
        if not userdata.created_tasks:
            userdata.created_tasks = []
        if not userdata.task_descriptions:
            userdata.task_descriptions = []
        if not userdata.task_deadlines:
            userdata.task_deadlines = []

        task_details = f"{task_description}"
        if deadline:
            task_details += f" (due: {deadline})"
        if priority != "normal":
            task_details += f" [{priority} priority]"

        userdata.created_tasks.append(task_details)
        userdata.task_descriptions.append(task_description)
        if deadline:
            userdata.task_deadlines.append(deadline)

        # Batman narrative for demo scenario
        if "groceries" in task_description.lower() or "buy" in task_description.lower():
            return f"Task created: Buy groceries tomorrow, sir."

        return f"Task created: {task_details}."

    async def create_todo_internal(
        self,
        todo_description: str,
        context: RunContext_T = None,
    ) -> str:
        """Internal method to create a todo"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Tasks operations
        # For now, return Batman-themed stub response
        if not userdata.created_tasks:
            userdata.created_tasks = []
        if not userdata.task_descriptions:
            userdata.task_descriptions = []

        userdata.created_tasks.append(f"TODO: {todo_description}")
        userdata.task_descriptions.append(todo_description)

        return f"Todo added: {todo_description}."

    async def set_project_deadline_internal(
        self,
        project_name: str,
        deadline: str,
        context: RunContext_T = None,
    ) -> str:
        """Internal method to set project deadline"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Tasks operations
        # For now, return Batman-themed stub response
        if not userdata.created_tasks:
            userdata.created_tasks = []
        if not userdata.task_deadlines:
            userdata.task_deadlines = []

        project_task = f"Project: {project_name} (deadline: {deadline})"
        userdata.created_tasks.append(project_task)
        userdata.task_deadlines.append(deadline)

        return f"Deadline set: {project_name} due {deadline}."

    async def track_progress_internal(
        self,
        task_name: str,
        progress_percentage: int = 0,
        context: RunContext_T = None,
    ) -> str:
        """Internal method to track progress"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Tasks operations
        # For now, return Batman-themed stub response
        progress_update = f"Task '{task_name}' is {progress_percentage}% complete"

        return f"Progress updated: {progress_update}."

    async def list_my_tasks_internal(self, context: RunContext_T) -> str:
        """Internal method to list tasks"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Google Tasks operations
        # For now, return Batman-themed stub response
        my_tasks = [
            "Review quarterly reports (50%)",
            "Charity gala prep (25%)",
            "Security update (not started)",
            "R&D code review (75%)"
        ]

        return f"Current tasks: {', '.join(my_tasks)}."

    @function_tool()
    async def create_task(
        self,
        task_description: Annotated[str, Field(description="Description of the task to create")],
        deadline: Annotated[str, Field(description="Task deadline (optional)")] = "",
        priority: Annotated[str, Field(description="Task priority (low, normal, high)")] = "normal",
        context: RunContext_T = None,
    ) -> str:
        """Create a new task in Google Tasks.
        Confirm the task description, deadline, and priority before creating."""
        return await self.create_task_internal(task_description, deadline, priority, context)

    @function_tool()
    async def create_todo(
        self,
        todo_description: Annotated[str, Field(description="Description of the todo item")],
        context: RunContext_T = None,
    ) -> str:
        """Create a simple todo item.
        Confirm the todo description before creating."""
        return await self.create_todo_internal(todo_description, context)

    @function_tool()
    async def set_project_deadline(
        self,
        project_name: Annotated[str, Field(description="Name of the project")],
        deadline: Annotated[str, Field(description="Project deadline date")],
        context: RunContext_T = None,
    ) -> str:
        """Set a deadline for a project.
        Confirm the project name and deadline before setting."""
        return await self.set_project_deadline_internal(project_name, deadline, context)

    @function_tool()
    async def track_progress(
        self,
        task_name: Annotated[str, Field(description="Name of the task to track")],
        progress_percentage: Annotated[int, Field(description="Progress percentage (0-100)")] = 0,
        context: RunContext_T = None,
    ) -> str:
        """Track progress on a task.
        Confirm the task name and progress percentage before updating."""
        return await self.track_progress_internal(task_name, progress_percentage, context)

    @function_tool()
    async def list_my_tasks(self, context: RunContext_T) -> str:
        """List all tasks assigned to the current user.
        This will show active tasks and their status."""
        return await self.list_my_tasks_internal(context)
