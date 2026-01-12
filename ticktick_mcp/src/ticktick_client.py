import os
import requests
import logging
from typing import Dict, List, Any, Optional, Union
from .auth import TickTickAuth

logger = logging.getLogger(__name__)


class TickTickClient:
    """
    Client for the TickTick API using OAuth2 authentication.
    Wraps TickTickAuth to handle token lifecycle.
    """

    def __init__(self):
        self.auth = TickTickAuth()

    @property
    def headers(self):
        """Get current headers from auth module."""
        headers = self.auth.get_headers()
        headers.update(
            {
                "Content-Type": "application/json",
                "Accept-Encoding": None,
                "User-Agent": "curl/8.7.1",
            }
        )
        return headers

    @property
    def base_url(self):
        return self.auth.get_base_url()

    def _make_request(self, method: str, endpoint: str, data=None) -> Dict:
        """
        Makes a request to the TickTick API.
        """
        if not self.auth.is_authenticated():
            return {
                "error": "Not authenticated. Please use 'start_authentication' tool."
            }

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, json=data)

            if response.status_code == 401:
                logger.info(
                    "Access token expired. Attempting to refresh is not implemented in this version (needs refresh token flow)."
                )
                return {
                    "error": "Access token expired or invalid. Please re-authenticate using 'start_authentication'."
                }

            response.raise_for_status()

            if response.status_code == 204 or not response.text:
                return {}

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}

    def get_all_projects(self) -> List[Dict]:
        return self._make_request("GET", "/project")

    def get_project(self, project_id: str) -> Dict:
        return self._make_request("GET", f"/project/{project_id}")

    def get_project_with_data(self, project_id: str) -> Dict:
        return self._make_request("GET", f"/project/{project_id}/data")

    def create_project(
        self,
        name: str,
        color: str = "#F18181",
        view_mode: str = "list",
        kind: str = "TASK",
    ) -> Dict:
        data = {"name": name, "color": color, "viewMode": view_mode, "kind": kind}
        return self._make_request("POST", "/project", data)

    def update_project(
        self,
        project_id: str,
        name: str = None,
        color: str = None,
        view_mode: str = None,
        kind: str = None,
    ) -> Dict:
        data = {}
        if name:
            data["name"] = name
        if color:
            data["color"] = color
        if view_mode:
            data["viewMode"] = view_mode
        if kind:
            data["kind"] = kind
        return self._make_request("POST", f"/project/{project_id}", data)

    def delete_project(self, project_id: str) -> Dict:
        return self._make_request("DELETE", f"/project/{project_id}")

    def get_task(self, project_id: str, task_id: str) -> Dict:
        return self._make_request("GET", f"/project/{project_id}/task/{task_id}")

    def create_task(
        self,
        title: str,
        project_id: str,
        content: str = None,
        desc: str = None,
        start_date: str = None,
        due_date: str = None,
        priority: Union[int, str] = 0,
        repeat_flag: str = None,
        items: List[Dict] = None,
        time_zone: str = None,
    ) -> Dict:
        from .utils.validators import normalize_priority

        data = {"title": title, "projectId": project_id}
        if content:
            data["content"] = content
        if desc:
            data["desc"] = desc
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
        if time_zone:
            data["timeZone"] = time_zone
        if priority is not None:
            data["priority"] = normalize_priority(priority) if priority else 0
        if repeat_flag:
            data["repeatFlag"] = repeat_flag
        if items:
            data["items"] = items
        return self._make_request("POST", "/task", data)

    def update_task(
        self,
        task_id: str,
        project_id: str,
        title: str = None,
        content: str = None,
        desc: str = None,
        priority: Union[int, str] = None,
        start_date: str = None,
        due_date: str = None,
        repeat_flag: str = None,
        items: List[Dict] = None,
        time_zone: str = None,
    ) -> Dict:
        from .utils.validators import normalize_priority

        data = {"id": task_id, "projectId": project_id}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if desc:
            data["desc"] = desc
        if priority is not None:
            p = normalize_priority(priority)
            if p is not None:
                data["priority"] = p
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
        if time_zone:
            data["timeZone"] = time_zone
        if repeat_flag:
            data["repeatFlag"] = repeat_flag
        if items is not None:
            data["items"] = items
        return self._make_request("POST", f"/task/{task_id}", data)

    def complete_task(self, project_id: str, task_id: str) -> Dict:
        return self._make_request(
            "POST", f"/project/{project_id}/task/{task_id}/complete"
        )

    def delete_task(self, project_id: str, task_id: str) -> Dict:
        return self._make_request("DELETE", f"/project/{project_id}/task/{task_id}")

    def create_subtask(
        self,
        subtask_title: str,
        parent_task_id: str,
        project_id: str,
        content: str = None,
        priority: Union[int, str] = 0,
    ) -> Dict:
        from .utils.validators import normalize_priority

        data = {
            "title": subtask_title,
            "projectId": project_id,
            "parentId": parent_task_id,
        }
        if content:
            data["content"] = content
        if priority is not None:
            data["priority"] = normalize_priority(priority) if priority else 0
        return self._make_request("POST", "/task", data)
