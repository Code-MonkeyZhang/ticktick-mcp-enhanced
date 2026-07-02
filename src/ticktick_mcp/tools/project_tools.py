"""
Project management tools for TickTick MCP.

This module contains MCP tools for managing TickTick projects,
including creating, reading, updating, and deleting projects.
"""

import logging
from typing import Union, List
from mcp.server.fastmcp import FastMCP

from ..client_manager import ensure_client
from ..utils.formatters import format_project, format_task
from ..utils.logging_utils import log_interaction
from .prompts import load_prompt

logger = logging.getLogger(__name__)


def register_project_tools(mcp: FastMCP):
    """Register all project-related MCP tools."""

    @mcp.tool(description=load_prompt("get_all_projects"))
    @log_interaction
    async def get_all_projects() -> str:
        try:
            ticktick = ensure_client()
            projects = ticktick.get_all_projects()
            if "error" in projects:
                return f"Error fetching projects: {projects['error']}"

            if not projects:
                return "No projects found."

            result = f"Found {len(projects)} projects:\n\n"
            for i, project in enumerate(projects, 1):
                result += f"Project {i}:\n" + format_project(project) + "\n"

            return result
        except Exception as e:
            # logger.error(f"Error in get_all_projects: {e}")
            return f"Error retrieving projects: {str(e)}"

    @mcp.tool(description=load_prompt("get_project_info"))
    @log_interaction
    async def get_project_info(project_id: str) -> str:
        try:
            ticktick = ensure_client()
            project_data = ticktick.get_project_with_data(project_id)
            if "error" in project_data:
                return f"Error fetching project data: {project_data['error']}"

            project = project_data.get("project", {})
            tasks = project_data.get("tasks", [])
            project_name = project.get("name", project_id)

            result = "=" * 60 + "\n"
            result += "📁 PROJECT INFORMATION\n"
            result += "=" * 60 + "\n\n"
            result += format_project(project)
            result += "\n" + "=" * 60 + "\n"
            result += f"📋 TASKS IN '{project_name}' ({len(tasks)} tasks)\n"
            result += "=" * 60 + "\n\n"

            if project_id.lower() == "inbox" and not tasks:
                result += "Your inbox is empty. 📭 Great job staying organized!\n"
            elif not tasks:
                result += "No tasks found in this project.\n"
            else:
                for i, task in enumerate(tasks, 1):
                    result += f"Task {i}:\n" + format_task(task) + "\n"

            return result
        except Exception as e:
            # logger.error(f"Error in get_project_info: {e}")
            return f"Error retrieving project information: {str(e)}"

    @mcp.tool(description=load_prompt("create_project"))
    @log_interaction
    async def create_project(
        name: str, color: str = "#F18181", view_mode: str = "list"
    ) -> str:
        if view_mode not in ["list", "kanban", "timeline"]:
            return "Invalid view_mode. Must be one of: list, kanban, timeline."

        try:
            ticktick = ensure_client()
            project = ticktick.create_project(
                name=name, color=color, view_mode=view_mode
            )

            if "error" in project:
                return f"Error creating project: {project['error']}"

            return "Project created successfully:\n\n" + format_project(project)
        except Exception as e:
            # logger.error(f"Error in create_project: {e}")
            return f"Error creating project: {str(e)}"

    @mcp.tool(description=load_prompt("delete_projects"))
    @log_interaction
    async def delete_projects(projects: Union[str, List[str]]) -> str:
        if isinstance(projects, str):
            project_list = [projects]
            single_project = True
        elif isinstance(projects, list):
            project_list = projects
            single_project = False
        else:
            return "Invalid input. Projects must be a string or list of strings."

        if not project_list:
            return (
                "No projects provided. Please provide at least one project to delete."
            )

        validation_errors = []
        for i, project_id in enumerate(project_list):
            if not isinstance(project_id, str):
                validation_errors.append(
                    f"Project {i + 1}: Must be a string (project ID)"
                )
                continue

            if not project_id.strip():
                validation_errors.append(f"Project {i + 1}: Project ID cannot be empty")

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        deleted_projects = []
        failed_projects = []

        try:
            ticktick = ensure_client()
            for i, project_id in enumerate(project_list):
                try:
                    result = ticktick.delete_project(project_id)

                    if "error" in result:
                        failed_projects.append(
                            f"Project {i + 1} (ID: {project_id}): {result['error']}"
                        )
                    else:
                        deleted_projects.append((i + 1, project_id))

                except Exception as e:
                    failed_projects.append(
                        f"Project {i + 1} (ID: {project_id}): {str(e)}"
                    )

            if single_project:
                if deleted_projects:
                    return f"Project {deleted_projects[0][1]} deleted successfully."
                else:
                    return f"Failed to delete project:\n{failed_projects[0]}"
            else:
                result_message = "Batch project deletion completed.\n\n"
                result_message += (
                    f"Successfully deleted: {len(deleted_projects)} projects\n"
                )
                result_message += f"Failed: {len(failed_projects)} projects\n\n"

                if deleted_projects:
                    result_message += "✅ Successfully Deleted Projects:\n"
                    for project_num, project_id in deleted_projects:
                        result_message += f"{project_num}. Project ID: {project_id}\n"
                    result_message += "\n"

                if failed_projects:
                    result_message += "❌ Failed Projects:\n"
                    for error in failed_projects:
                        result_message += f"{error}\n"

                return result_message

        except Exception as e:
            # logger.error(f"Error in delete_projects: {e}")
            return f"Error during project deletion: {str(e)}"
