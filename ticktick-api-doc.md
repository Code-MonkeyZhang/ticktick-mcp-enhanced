# TickTick Open API

## Introduction

Welcome to the TickTick Open API documentation. TickTick is a powerful task management application that allows users to easily manage and organize their daily tasks, deadlines, and projects. With TickTick Open API, developers can integrate TickTick's powerful task management features into their own applications and create a seamless user experience.

## Getting Started
To get started using the TickTick Open API, you will need to register your application and obtain a client ID and client secret. You can register your application by visiting the [TickTick Developer Center](https://developer.ticktick.com/manage). Once registered, you will receive a client ID and client secret which you will use to authenticate your requests.

## Authorization
### Get Access Token
In order to call TickTick's Open API, it is necessary to obtain an access token for the corresponding user. TickTick uses the OAuth2 protocol to obtain the access token.

#### First Step
Redirect the user to the TickTick authorization page, https://ticktick.com/oauth/authorize. The required parameters are as follows:

| Name | Description |
| ------ |----------------------------------------------------------------------------------------------|
| client_id | Application unique id |
| scope | Spaces-separated permission scope. The currently available scopes are tasks:write tasks:read |
| state | Passed to redirect url as is |
| redirect_uri | User-configured redirect url |
| response_type | Fixed as code |

Example:
https://ticktick.com/oauth/authorize?scope=scope&client_id=client_id&state=state&redirect_uri=redirect_uri&response_type=code



#### Second Step
After the user grants access, TickTick will redirect the user back to your application's `redirect_uri` with an authorization code as a query parameter.

| Name | Description |
| ------ | ------ |
| code | Authorization code for subsequent access tokens |
| state | state parameter passed in the first step |


#### Third Step

To exchange the authorization code for an access token, make a POST request to `https://ticktick.com/oauth/token` with the following parameters(Content-Type: application/x-www-form-urlencoded):

| Name | Description |
| ------ | ------ |
| client_id | The username is located in the **HEADER** using the **Basic Auth** authentication method |
| client_secret | The password is located in the **HEADER** using the **Basic Auth** authentication method |
| code | The code obtained in the second step |
| grant_type | grant type, now only authorization_code |
| scope | spaces-separated permission scope. The currently available scopes are tasks: write, tasks: read |
| redirect_uri | user-configured redirect url |

Access_token for openapi request authentication in the request response
```
 {
...
"access_token": "access token value"
...
}
```


#### Request OpenAPI
Set **Authorization** in the header, the value is **Bearer** `access token value`
```
Authorization: Bearer e*****b
```


## API Reference
The TickTick Open API provides a RESTful interface for accessing and managing user tasks, lists, and other related resources. The API is based on the standard HTTP protocol and supports JSON data formats.

### Task
#### Get Task By Project ID And Task ID
```
GET /open/v1/project/{projectId}/task/{taskId}
```

##### Parameters
| Type     | Name                     | Description        | Schema |
| -------- | ------------------------ | ------------------ | ------ |
| **Path** | **projectId** *required* | Project identifier | string |
| **Path** | **taskId** *required*    | Task identifier    | string |

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|[Task](openapi.md#Task)|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example

###### Request
```  http
GET /open/v1/project/{{projectId}}/task/{{taskId}} HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

###### Response
```json
{
"id" : "63b7bebb91c0a5474805fcd4",
"isAllDay" : true,
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"timeZone" : "America/Los_Angeles",
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
	"id" : "6435074647fd2e6387145f20",
	"status" : 0,
	"title" : "Item Title",
	"sortOrder" : 12345,
	"startDate" : "2019-11-13T03:00:00+0000",
	"isAllDay" : false,
	"timeZone" : "America/Los_Angeles",
	"completedTime" : "2019-11-13T03:00:00+0000"
	} ]
}
```


#### Create Task
```
POST /open/v1/task
```

##### Parameters
| **Type** | **Name**       | **Description**                                                                                          | **Schema**   |
| -------- | ------------------- | -------------------------------------------------------------------------------------------------------- | ------- |
| **Body** | title   *required*  | Task title                                                                                               | string  |
| **Body** | content             | Task content                                                                                             | string  |
| **Body** | desc                | Description of checklist                                                                                 | string  |
| **Body** | isAllDay            | All day                                                                                                  | boolean |
| **Body** | startDate           | Start date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"` | date    |
| **Body** | dueDate             | Due date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"`   | date    |
| **Body** | timeZone            | The time zone in which the time is specified                                                             | String  |
| **Body** | reminders           | Lists of reminders specific to the task                                                                  | list    |
| **Body** | repeatFlag          | Recurring rules of task                                                                                  | string  |
| **Body** | priority            | The priority of task, default is "0"                                                                     | integer |
| **Body** | sortOrder           | The order of task                                                                                        | integer |
| **Body** | items               | The list of subtasks                                                                                     | list    |
| **Body** | items.title         | Subtask title                                                                                            | string  |
| **Body** | items.startDate     | Start date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format                                                 | date    |
| **Body** | items.isAllDay      | All day                                                                                                  | boolean |
| **Body** | items.sortOrder     | The order of subtask                                                                                     | integer |
| **Body** | items.timeZone      | The time zone in which the Start time is specified                                                       | string  |
| **Body** | items.status        | The completion status of subtask                                                                         | integer |
| **Body** | items.completedTime | Completed time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"`      | date    |

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|[Task](openapi.md#Definitions#Task)|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|


##### Example
###### Request
```http
POST /open/v1/task HTTP/1.1
Host: api.ticktick.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
	...
    "title":"Task Title",
    "projectId":"6226ff9877acee87727f6bca"
    ...
}
```

###### Response
```json
{
"id" : "63b7bebb91c0a5474805fcd4",
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"isAllDay" : true,
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"timeZone" : "America/Los_Angeles",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
	"id" : "6435074647fd2e6387145f20",
	"status" : 1,
	"title" : "Subtask Title",
	"sortOrder" : 12345,
	"startDate" : "2019-11-13T03:00:00+0000",
	"isAllDay" : false,
	"timeZone" : "America/Los_Angeles",
	"completedTime" : "2019-11-13T03:00:00+0000"
	} ]
}
```


<a name="updateusingput"></a>
#### Update Task
```
POST /open/v1/task/{taskId}
```

##### Parameters
| **Type** | **Name**            | **Description**                                                                                          | **Schema**   |
| -------- | ------------------------ | -------------------------------------------------------------------------------------------------------- | ------- |
| **Path** | **taskId** *required*    | Task identifier                                                                                          | string  |
| **Body** | id     *required*        | Task id.                                                                                                 | string  |
| **Body** | projectId     *required* | Project id.                                                                                              | string  |
| **Body** | title                    | Task title                                                                                               | string  |
| **Body** | content                  | Task content                                                                                             | string  |
| **Body** | desc                     | Description of checklist                                                                                 | string  |
| **Body** | isAllDay                 | All day                                                                                                  | boolean |
| **Body** | startDate                | Start date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"` | date    |
| **Body** | dueDate                  | Due date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"`   | date    |
| **Body** | timeZone                 | The time zone in which the time is specified                                                             | String  |
| **Body** | reminders                | Lists of reminders specific to the task                                                                  | list    |
| **Body** | repeatFlag               | Recurring rules of task                                                                                  | string  |
| **Body** | priority                 | The priority of task, default is "normal"                                                                | integer |
| **Body** | sortOrder                | The order of task                                                                                        | integer |
| **Body** | items                    | The list of subtasks                                                                                     | list    |
| **Body** | items.title              | Subtask title                                                                                            | string  |
| **Body** | items.startDate          | Start date and time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format                                                 | date    |
| **Body** | items.isAllDay           | All day                                                                                                  | boolean |
| **Body** | items.sortOrder          | The order of subtask                                                                                     | integer |
| **Body** | items.timeZone           | The time zone in which the Start time is specified                                                       | string  |
| **Body** | items.status             | The completion status of subtask                                                                         | integer |
| **Body** | items.completedTime      | Completed time in `"yyyy-MM-dd'T'HH:mm:ssZ"` format <br> **Example** : `"2019-11-13T03:00:00+0000"`      | date    |

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|[Task](openapi.md#Definitions#Task)|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example

###### Request
```http
POST /open/v1/task/{{taskId}} HTTP/1.1
Host: api.ticktick.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
    "id": "{{taskId}}",
    "projectId": "{{projectId}}",
    "title": "Task Title",
    "priority": 1,
    ...
}
```

###### Response
```json
{
"id" : "63b7bebb91c0a5474805fcd4",
"projectId" : "6226ff9877acee87727f6bca",
"title" : "Task Title",
"content" : "Task Content",
"desc" : "Task Description",
"isAllDay" : true,
"startDate" : "2019-11-13T03:00:00+0000",
"dueDate" : "2019-11-14T03:00:00+0000",
"timeZone" : "America/Los_Angeles",
"reminders" : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ],
"repeatFlag" : "RRULE:FREQ=DAILY;INTERVAL=1",
"priority" : 1,
"status" : 0,
"completedTime" : "2019-11-13T03:00:00+0000",
"sortOrder" : 12345,
"items" : [ {
	"id" : "6435074647fd2e6387145f20",
	"status" : 1,
	"title" : "Item Title",
	"sortOrder" : 12345,
	"startDate" : "2019-11-13T03:00:00+0000",
	"isAllDay" : false,
	"timeZone" : "America/Los_Angeles",
	"completedTime" : "2019-11-13T03:00:00+0000"
	} ]
}
```


<a name="completeusingpost"></a>
#### Complete Task
```
POST /open/v1/project/{projectId}/task/{taskId}/complete
```


##### Parameters

|Type|Name|Description|Schema|
|---|---|---|---|
|**Path**|**projectId** *required*|Project identifier|string|
|**Path**|**taskId** *required*|Task identifier|string|


##### Responses

|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|No Content|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example
###### Request
```http
POST /open/v1/project/{{projectId}}/task/{{taskId}}/complete HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

#### Delete Task
```
DELETE /open/v1/project/{projectId}/task/{taskId}
```

##### Parameters
| Type     | Name                     | Description        | Schema |
| -------- | ------------------------ | ------------------ | ------ |
| **Path** | **projectId** *required* | Project identifier | string |
| **Path** | **taskId** *required*    | Task identifier    | string |


##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|No Content|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|


##### Example

###### Request
```http
DELETE /open/v1/project/{{projectId}}/task/{{taskId}} HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

### Project
#### Get User Project
```
GET /open/v1/project
```

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|< [Project](openapi.md#Definitions#Project) > array|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example
###### Request
```http
GET /open/v1/project HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

###### Response
```json
[{
"id": "6226ff9877acee87727f6bca",
"name": "project name",
"color": "#F18181",
"closed": false,
"groupId": "6436176a47fd2e05f26ef56e",
"viewMode": "list",
"permission": "write",
"kind": "TASK"
}]
```

#### Get Project By ID
```
GET /open/v1/project/{projectId}
```

##### Parameters
| Type     | Name                   | Description        | Schema |
| -------- | ---------------------- | ------------------ | ------ |
| **Path** | **project** *required* | Project identifier | string |

##### Responses
| HTTP Code | Description  | Schema                  |
| --------- | ------------ | ----------------------- |
| **200**   | OK           | [Project](openapi.md#Definitions#Project)|
| **401**   | Unauthorized | No Content              |
| **403**   | Forbidden    | No Content              |
| **404**   | Not Found    | No Content              |

##### Example

###### Request path
```http
GET /open/v1/project/{{projectId}} HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

###### Response
```json
{
	"id": "6226ff9877acee87727f6bca",
	"name": "project name",
	"color": "#F18181",
	"closed": false,
	"groupId": "6436176a47fd2e05f26ef56e",
	"viewMode": "list",
	"kind": "TASK"
}
```


#### Get Project With Data

```
GET /open/v1/project/{projectId}/data
```

##### Parameters
|Type|Name|Description|Schema|
|---|---|---|---|
|**Path**|**projectId** *required*|Project identifier|string|

##### Responses

| HTTP Code | Description  | Schema                  |
| --------- | ------------ | ----------------------- |
| **200**   | OK           | [ProjectData](openapi.md#Definitions#ProjectData) |
| **401**   | Unauthorized | No Content              |
| **403**   | Forbidden    | No Content              |
| **404**   | Not Found    | No Content              |

##### Example
###### Request
```http
GET /open/v1/project/{{projectId}}/data HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```

###### Response
```json
{
"project": {
	"id": "6226ff9877acee87727f6bca",
	"name": "project name",
	"color": "#F18181",
	"closed": false,
	"groupId": "6436176a47fd2e05f26ef56e",
	"viewMode": "list",
	"kind": "TASK"
},
"tasks": [{
	"id": "6247ee29630c800f064fd145",
	"isAllDay": true,
	"projectId": "6226ff9877acee87727f6bca",
	"title": "Task Title",
	"content": "Task Content",
	"desc": "Task Description",
	"timeZone": "America/Los_Angeles",
	"repeatFlag": "RRULE:FREQ=DAILY;INTERVAL=1",
	"startDate": "2019-11-13T03:00:00+0000",
	"dueDate": "2019-11-14T03:00:00+0000",
	"reminders": [
		"TRIGGER:P0DT9H0M0S",
		"TRIGGER:PT0S"
	],
	"priority": 1,
	"status": 0,
	"completedTime": "2019-11-13T03:00:00+0000",
	"sortOrder": 12345,
	"items": [{
		"id": "6435074647fd2e6387145f20",
		"status": 0,
		"title": "Subtask Title",
		"sortOrder": 12345,
		"startDate": "2019-11-13T03:00:00+0000",
		"isAllDay": false,
		"timeZone": "America/Los_Angeles",
		"completedTime": "2019-11-13T03:00:00+0000"
	}]
}],
"columns": [{
	"id": "6226ff9e76e5fc39f2862d1b",
	"projectId": "6226ff9877acee87727f6bca",
	"name": "Column Name",
	"sortOrder": 0
}]
}
```

#### Create Project

```
POST /open/v1/project
```

##### Parameters
| **Type** | **Name**         | **Description**                         | **Schema**           |
| -------- | ---------------- | --------------------------------------- | --------------- |
| **Body** | name  *required* | name of the project                     | string          |
| **Body** | color            | color of project, eg. "#F18181"         | string          |
| **Body** | sortOrder        | sort order value of the project         | integer (int64) |
| **Body** | viewMode         | view mode, "list", "kanban", "timeline" | string          |
| **Body** | kind             | project kind, "TASK", "NOTE"            | string          |

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|[Project](openapi.md#Definitions#Project)|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example
###### Request
```http
POST /open/v1/project HTTP/1.1
Host: api.ticktick.com
Content-Type: application/json
Authorization: Bearer {{token}}
{
    "name": "project name",
    "color": "#F18181",
    "viewMode": "list",
    "kind": "task"
}
```

###### Response
```json
{
"id": "6226ff9877acee87727f6bca",
"name": "project name",
"color": "#F18181",
"sortOrder": 0,
"viewMode": "list",
"kind": "TASK"
}
```

#### Update Project
```
POST /open/v1/project/{projectId}
```

##### Parameters
| **Type** | **Parameter**        | **Description**                         | Schema          |
| -------- | -------------------- | --------------------------------------- | --------------- |
| **Path** | projectId *required* | project identifier                      | string          |
| **Body** | name                 | name of the project                     | string          |
| **Body** | color                | color of the project                    | string          |
| **Body** | sortOrder            | sort order value, default 0             | integer (int64) |
| **Body** | viewMode             | view mode, "list", "kanban", "timeline" | string          |
| **Body** | kind                 | project kind, "TASK", "NOTE"            | string          |

##### Responses
|HTTP Code|Description|Schema|
|---|---|---|
|**200**|OK|[Project](openapi.md#Definitions#Project)|
|**201**|Created|No Content|
|**401**|Unauthorized|No Content|
|**403**|Forbidden|No Content|
|**404**|Not Found|No Content|

##### Example
###### Request
```http
POST /open/v1/project/{{projectId}} HTTP/1.1
Host: api.ticktick.com
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "name": "Project Name",
    "color": "#F18181",
    "viewMode": "list",
    "kind": "TASK"
}
```

###### Response
```json
{
"id": "6226ff9877acee87727f6bca",
"name": "Project Name",
"color": "#F18181",
"sortOrder": 0,
"viewMode": "list",
"kind": "TASK"
}
```

#### Delete Project
```
DELETE /open/v1/project/{projectId}
```

##### Parameters
| Type | Name                     | Description        | Schema |
| ---- | ------------------------ | ------------------ | ------ |
| Path | **projectId** *required* | Project identifier | string       |

##### Responses
| HTTP Code | Description  | Schema     |
| --------- | ------------ | ---------- |
| **200**   | OK           | No Content |
| **401**   | Unauthorized | No Content |
| **403**   | Forbidden    | No Content |
| **404**   | Not Found    | No Content |

##### Example
###### Request
```http
DELETE /open/v1/project/{{projectId}} HTTP/1.1
Host: api.ticktick.com
Authorization: Bearer {{token}}
```


## Definitions

### ChecklistItem

|Name|Description|Schema|
|---|---|---|
|**id**|Subtask identifier|string|
|**title**|Subtask title|string|
|**status**|The completion status of subtask <br> **Value** : Normal: `0`, Completed: `1`|integer (int32)|
|**completedTime**|Subtask completed time in `"yyyy-MM-dd'T'HH:mm:ssZ"` <br> **Example** : `"2019-11-13T03:00:00+0000"`|string (date-time)|
|**isAllDay**|All day|boolean|
|**sortOrder**|Subtask sort order <br> **Example** : `234444`|integer (int64)|
|**startDate**|Subtask start date time in `"yyyy-MM-dd'T'HH:mm:ssZ"` <br> **Example** : `"2019-11-13T03:00:00+0000"`|string (date-time)|
|**timeZone**|Subtask timezone <br> **Example** : `"America/Los_Angeles"`|string|


### Task

| Name              | Description                                                                                        | Schema                                              |
| ----------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **id**            | Task identifier                                                                                    | string                                              |
| **projectId**     | Task project id                                                                                    | string                                              |
| **title**         | Task title                                                                                         | string                                              |
| **isAllDay**      | All day                                                                                            | boolean                                             |
| **completedTime** | Task completed time in ``"yyyy-MM-dd'T'HH:mm:ssZ"``<br> **Example** : `"2019-11-13T03:00:00+0000"` | string (date-time)                                  |
| **content**       | Task content                                                                                       | string                                              |
| **desc**          | Task description of checklist                                                                      | string                                              |
| **dueDate**       | Task due date time in `"yyyy-MM-dd'T'HH:mm:ssZ"`<br> **Example** : `"2019-11-13T03:00:00+0000"`    | string (date-time)                                  |
| **items**         | Subtasks of Task                                                                                   | < [ChecklistItem](openapi.md#checklistitem) > array |
| **priority**      | Task priority <br> **Value** : None:`0`, Low:`1`, Medium:`3`, High`5`                              | integer (int32)                                     |
| **reminders**     | List of reminder triggers<br> **Example** : `[ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ]`             | < string > array                                    |
| **repeatFlag**    | Recurring rules of task <br> **Example** : `"RRULE:FREQ=DAILY;INTERVAL=1"`                         | string                                              |
| **sortOrder**     | Task sort order <br> **Example** : `12345`                                                         | integer (int64)                                     |
| **startDate**     | Start date time in `"yyyy-MM-dd'T'HH:mm:ssZ"`<br> **Example** : `"2019-11-13T03:00:00+0000"`       | string (date-time)                                  |
| **status**        | Task completion status <br> **Value** : Normal: `0`, Completed: `2`                                | integer (int32)                                     |
| **timeZone**      | Task timezone <br> **Example** : `"America/Los_Angeles"`                                           | string                                              |


### Project
| Name           | Description                             | Schema          |
| -------------- | --------------------------------------- | --------------- |
| **id**         | Project identifier                      | string          |
| **name**       | Project name                            | string          |
| **color**      | Project color                           | string          |
| **sortOrder**  | Order value                             | integer (int64) |
| **closed**     | Projcet closed                          | boolean         |
| **groupId**    | Project group identifier                | string          |
| **viewMode**   | view mode, "list", "kanban", "timeline" | string          |
| **permission** | "read", "write" or "comment"            | string          |
| **kind**       | "TASK" or "NOTE"                        | string          |


### Column
| Name      | Description        | Schema          |
| --------- | ------------------ | --------------- |
| id        | Column identifier  | string          |
| projectId | Project identifier | string          |
| name      | Column name        | string          |
| sortOrder | Order value        | integer (int64) |


### ProjectData
| Name    | Description                | Schema             |
| ------- | -------------------------- | ------------------ |
| project | Project info               | [Project](openapi.md#Definitions#Project)        |
| tasks   | Undone tasks under project | <[Task](openapi.md#Definitions#Task)> array   |
| columns | Columns under project      | <[Column](openapi.md#Definitions#Column)> array |


## Feedback and Support

If you have any questions or feedback regarding the TickTick Open API documentation, please contact us at [support@ticktick.com](mailto:support@ticktick.com). We appreciate your input and will work to address any concerns or issues as quickly as possible. Thank you for choosing TickTick!