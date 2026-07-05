import logging

import requests
from typing import Dict, List, Optional, Union
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

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data=None,
        params: Optional[Dict] = None,
    ) -> Dict:
        """
        Makes a request to the TickTick API.

        Args:
            method: HTTP method (GET, POST, DELETE, ...).
            endpoint: API path starting with "/".
            data: JSON body payload. May be a list for endpoints that accept arrays.
            params: URL query string parameters (used by GET endpoints such as habit checkins).
        """
        if not self.auth.is_configured():
            return {"error": "Not configured. Please use the 'login' tool."}

        if not self.auth.is_authenticated():
            return {"error": "Not authenticated. Please use the 'login' tool."}

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method, url, headers=self.headers, json=data, params=params
            )

            if response.status_code == 401:
                return {
                    "error": "Access token expired or invalid. Please use the 'login' tool to re-authenticate."
                }

            response.raise_for_status()

            if response.status_code == 204 or not response.text:
                return {}

            return response.json()
        except requests.exceptions.RequestException as e:
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
        reminders: List[str] = None,
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
        if reminders is not None:
            data["reminders"] = reminders
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
        reminders: List[str] = None,
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
        if reminders is not None:
            data["reminders"] = reminders
        return self._make_request("POST", f"/task/{task_id}", data)

    def complete_task(self, project_id: str, task_id: str) -> Dict:
        return self._make_request(
            "POST", f"/project/{project_id}/task/{task_id}/complete"
        )

    def delete_task(self, project_id: str, task_id: str) -> Dict:
        return self._make_request("DELETE", f"/project/{project_id}/task/{task_id}")

    def move_task(
        self,
        task_id: str,
        from_project_id: str,
        to_project_id: str,
    ) -> Union[Dict, List]:
        """Move a task from one project to another.

        The API accepts an array of move operations; this wrapper handles one task per call.
        """
        moves = [
            {
                "fromProjectId": from_project_id,
                "toProjectId": to_project_id,
                "taskId": task_id,
            }
        ]
        logger.info(
            f"Moving task {task_id} from {from_project_id} to {to_project_id}"
        )
        return self._make_request("POST", "/task/move", data=moves)

    def get_completed_tasks(
        self,
        project_ids: List[str] = None,
        start_date: str = None,
        end_date: str = None,
    ) -> List[Dict]:
        """List tasks completed within the given projects and time range.

        All filters are optional; at least one is recommended to narrow results.
        Dates must already be in TickTick API format (timezone offset without colon).
        """
        data = {}
        if project_ids:
            data["projectIds"] = project_ids
        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date
        logger.info(f"Querying completed tasks with filters: {data}")
        return self._make_request("POST", "/task/completed", data=data)

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

    # ------------------------------------------------------------------
    # Habit API
    # ------------------------------------------------------------------

    def get_all_habits(self) -> List[Dict]:
        return self._make_request("GET", "/habit")

    def get_habit(self, habit_id: str) -> Dict:
        return self._make_request("GET", f"/habit/{habit_id}")

    def create_habit(self, data: Dict) -> Dict:
        logger.info(f"Creating habit: {data.get('name')}")
        return self._make_request("POST", "/habit", data=data)

    def update_habit(self, habit_id: str, data: Dict) -> Dict:
        logger.info(f"Updating habit {habit_id}: {list(data.keys())}")
        return self._make_request("POST", f"/habit/{habit_id}", data=data)

    def checkin_habit(
        self,
        habit_id: str,
        stamp: int,
        value: float = 1.0,
        goal: float = 1.0,
        status: Optional[int] = None,
    ) -> Dict:
        """Create or update a habit check-in for a given date stamp."""
        data = {"stamp": stamp, "value": value, "goal": goal}
        if status is not None:
            data["status"] = status
        logger.info(f"Check-in habit {habit_id} for stamp {stamp}")
        return self._make_request("POST", f"/habit/{habit_id}/checkin", data=data)

    def get_habit_checkins(
        self,
        habit_ids: List[str],
        from_stamp: int,
        to_stamp: int,
    ) -> List[Dict]:
        """Fetch habit check-in records within a date-stamp range.

        habit_ids, from and to are sent as URL query parameters per the API spec.
        """
        params = {
            "habitIds": ",".join(habit_ids),
            "from": from_stamp,
            "to": to_stamp,
        }
        logger.info(f"Querying habit check-ins: {params}")
        return self._make_request(
            "GET", "/habit/checkins", params=params
        )
