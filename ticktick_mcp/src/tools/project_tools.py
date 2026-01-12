"""
Project management tools for TickTick MCP.

This module contains MCP tools for managing TickTick projects,
including creating, reading, updating, and deleting projects.
"""

import logging
from typing import Union, List
from mcp.server.fastmcp import FastMCP

from ..config import ensure_client
from ..utils.formatters import format_project, format_task
from ..utils.logging_utils import log_interaction

# Set up logging
logger = logging.getLogger(__name__)


def register_project_tools(mcp: FastMCP):
    """Register all project-related MCP tools."""
    
    @mcp.tool()
    @log_interaction
    async def get_all_projects() -> str:
        """
        Get all projects from TickTick.
        
        Note: This does not include the special "Inbox" project. 
        To get inbox information and tasks, use get_project_info(project_id="inbox").
        """
        try:
            ticktick = ensure_client()
            projects = ticktick.get_all_projects()
            if 'error' in projects:
                return f"Error fetching projects: {projects['error']}"
            
            if not projects:
                return "No projects found."
            
            result = f"Found {len(projects)} projects:\n\n"
            for i, project in enumerate(projects, 1):
                result += f"Project {i}:\n" + format_project(project) + "\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in get_all_projects: {e}")
            return f"Error retrieving projects: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def get_project_info(project_id: str) -> str:
        """
        Get comprehensive information about a project, including its details and all tasks.
        
        This tool provides a complete view of a project in one call, showing both
        the project metadata (name, color, view mode, etc.) and all tasks within it.
        
        Args:
            project_id: ID of the project, or "inbox" to get inbox information
        
        Returns:
            A formatted string containing:
            - Project basic information (name, ID, color, etc.)
            - List of all tasks in the project with their details
        
        Examples:
            - get_project_info("abc123") → Get project info and tasks
            - get_project_info("inbox") → Get inbox info and tasks
        """
        try:
            ticktick = ensure_client()
            project_data = ticktick.get_project_with_data(project_id)
            if 'error' in project_data:
                return f"Error fetching project data: {project_data['error']}"
            
            project = project_data.get('project', {})
            tasks = project_data.get('tasks', [])
            project_name = project.get('name', project_id)
            
            # Format project information
            result = "=" * 60 + "\n"
            result += "📁 PROJECT INFORMATION\n"
            result += "=" * 60 + "\n\n"
            result += format_project(project)
            result += "\n" + "=" * 60 + "\n"
            result += f"📋 TASKS IN '{project_name}' ({len(tasks)} tasks)\n"
            result += "=" * 60 + "\n\n"
            
            # Special message for empty projects
            if project_id.lower() == "inbox" and not tasks:
                result += "Your inbox is empty. 📭 Great job staying organized!\n"
            elif not tasks:
                result += f"No tasks found in this project.\n"
            else:
                # Format tasks
                for i, task in enumerate(tasks, 1):
                    result += f"Task {i}:\n" + format_task(task) + "\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in get_project_info: {e}")
            return f"Error retrieving project information: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def create_project(
        name: str,
        color: str = "#F18181",
        view_mode: str = "list"
    ) -> str:
        """
        Create a new project in TickTick.
        
        Args:
            name: Project name
            color: Color code (hex format) (optional)
            view_mode: View mode - one of list, kanban, or timeline (optional)
        """
        # Validate view_mode
        if view_mode not in ["list", "kanban", "timeline"]:
            return "Invalid view_mode. Must be one of: list, kanban, timeline."
        
        try:
            ticktick = ensure_client()
            project = ticktick.create_project(
                name=name,
                color=color,
                view_mode=view_mode
            )
            
            if 'error' in project:
                return f"Error creating project: {project['error']}"
            
            return f"Project created successfully:\n\n" + format_project(project)
        except Exception as e:
            logger.error(f"Error in create_project: {e}")
            return f"Error creating project: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def delete_projects(projects: Union[str, List[str]]) -> str:
        """
        Delete one or more projects.
        
        Supports both single project and batch deletion. For single project, you can pass
        a project ID string directly. For multiple projects, pass a list of project IDs.
        
        Args:
            projects: Project ID string or list of project ID strings
        
        Examples:
            # Single project
            "abc123"
            
            # Multiple projects
            ["abc123", "def456", "ghi789"]
        """
        # Normalize input - convert single string to list
        if isinstance(projects, str):
            project_list = [projects]
            single_project = True
        elif isinstance(projects, list):
            project_list = projects
            single_project = False
        else:
            return "Invalid input. Projects must be a string or list of strings."
        
        if not project_list:
            return "No projects provided. Please provide at least one project to delete."
        
        # Validate all projects are strings
        validation_errors = []
        for i, project_id in enumerate(project_list):
            if not isinstance(project_id, str):
                validation_errors.append(f"Project {i + 1}: Must be a string (project ID)")
                continue
            
            if not project_id.strip():
                validation_errors.append(f"Project {i + 1}: Project ID cannot be empty")
        
        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)
        
        # Delete projects one by one and collect results
        deleted_projects = []
        failed_projects = []
        
        try:
            ticktick = ensure_client()
            for i, project_id in enumerate(project_list):
                try:
                    result = ticktick.delete_project(project_id)
                    
                    if 'error' in result:
                        failed_projects.append(f"Project {i + 1} (ID: {project_id}): {result['error']}")
                    else:
                        deleted_projects.append((i + 1, project_id))
                        
                except Exception as e:
                    failed_projects.append(f"Project {i + 1} (ID: {project_id}): {str(e)}")
            
            # Format the results
            if single_project:
                if deleted_projects:
                    return f"Project {deleted_projects[0][1]} deleted successfully."
                else:
                    return f"Failed to delete project:\n{failed_projects[0]}"
            else:
                result_message = f"Batch project deletion completed.\n\n"
                result_message += f"Successfully deleted: {len(deleted_projects)} projects\n"
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
            logger.error(f"Error in delete_projects: {e}")
            return f"Error during project deletion: {str(e)}"
