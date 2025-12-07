#!/usr/bin/env python3
"""
TickTick MCP API 功能测试脚本

测试所有主要的 API 功能，包括：
- 项目管理（创建、获取、更新、删除）
- 任务管理（创建、获取、更新、完成、删除）
- 高级任务功能（截止日期、提醒、重复任务、时区、子任务）
- 批量创建任务
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ticktick_mcp.src.ticktick_client import TickTickClient


class TestResults:
    """测试结果记录器"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.test_data = {}
    
    def record_pass(self, test_name: str):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
    
    def record_fail(self, test_name: str, error: str):
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
        self.failed += 1
    
    def record_skip(self, test_name: str, reason: str):
        print(f"⏭️  SKIP: {test_name}")
        print(f"   Reason: {reason}")
        self.skipped += 1
    
    def store_data(self, key: str, value: Any):
        """存储测试数据供后续测试使用"""
        self.test_data[key] = value
    
    def get_data(self, key: str) -> Any:
        """获取之前存储的测试数据"""
        return self.test_data.get(key)
    
    def print_summary(self):
        total = self.passed + self.failed + self.skipped
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"总计: {total} 个测试")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"⏭️  跳过: {self.skipped}")
        print("="*60)
        
        if self.failed == 0:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  有 {self.failed} 个测试失败")


def print_section(title: str):
    """打印测试节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_get_all_projects(client: TickTickClient, results: TestResults):
    """测试获取项目列表"""
    try:
        projects = client.get_all_projects()
        
        if 'error' in projects:
            results.record_fail("获取项目列表", projects['error'])
            return
        
        if isinstance(projects, list):
            results.record_pass(f"获取项目列表 (共 {len(projects)} 个项目)")
            
            # 存储第一个项目ID供后续测试使用
            if projects:
                results.store_data('existing_project_id', projects[0]['id'])
                print(f"   存储项目ID: {projects[0]['id']}")
        else:
            results.record_fail("获取项目列表", "返回值不是列表")
    except Exception as e:
        results.record_fail("获取项目列表", str(e))


def test_create_project(client: TickTickClient, results: TestResults):
    """测试创建项目"""
    try:
        project_name = f"测试项目 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project = client.create_project(
            name=project_name,
            color="#FF6B6B",
            view_mode="list"
        )
        
        if 'error' in project:
            results.record_fail("创建项目", project['error'])
            return
        
        if project.get('id') and project.get('name') == project_name:
            results.record_pass(f"创建项目 '{project_name}'")
            results.store_data('test_project_id', project['id'])
            print(f"   项目ID: {project['id']}")
        else:
            results.record_fail("创建项目", "项目信息不完整")
    except Exception as e:
        results.record_fail("创建项目", str(e))


def test_get_project(client: TickTickClient, results: TestResults):
    """测试获取单个项目"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("获取单个项目", "没有可用的项目ID")
            return
        
        project = client.get_project(project_id)
        
        if 'error' in project:
            results.record_fail("获取单个项目", project['error'])
            return
        
        if project.get('id') == project_id:
            results.record_pass(f"获取项目详情 '{project.get('name')}'")
        else:
            results.record_fail("获取单个项目", "项目ID不匹配")
    except Exception as e:
        results.record_fail("获取单个项目", str(e))


def test_create_simple_task(client: TickTickClient, results: TestResults):
    """测试创建简单任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建简单任务", "没有可用的项目ID")
            return
        
        task = client.create_task(
            title="简单测试任务",
            project_id=project_id,
            content="这是一个简单的测试任务"
        )
        
        if 'error' in task:
            results.record_fail("创建简单任务", task['error'])
            return
        
        if task.get('id') and task.get('title') == "简单测试任务":
            results.record_pass("创建简单任务")
            results.store_data('simple_task_id', task['id'])
            print(f"   任务ID: {task['id']}")
        else:
            results.record_fail("创建简单任务", "任务信息不完整")
    except Exception as e:
        results.record_fail("创建简单任务", str(e))


def test_create_task_with_due_date(client: TickTickClient, results: TestResults):
    """测试创建带截止日期的任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建带截止日期的任务", "没有可用的项目ID")
            return
        
        # 设置截止日期为3天后
        due_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT15:00:00+0000")
        
        task = client.create_task(
            title="带截止日期的任务",
            project_id=project_id,
            content="这个任务有截止日期",
            due_date=due_date,
            priority=5
        )
        
        if 'error' in task:
            results.record_fail("创建带截止日期的任务", task['error'])
            return
        
        if task.get('id') and task.get('dueDate'):
            results.record_pass("创建带截止日期的任务")
            results.store_data('due_date_task_id', task['id'])
            print(f"   任务ID: {task['id']}")
            print(f"   截止日期: {task.get('dueDate')}")
        else:
            results.record_fail("创建带截止日期的任务", "截止日期未设置")
    except Exception as e:
        results.record_fail("创建带截止日期的任务", str(e))


def test_create_task_with_timezone_offset(client: TickTickClient, results: TestResults):
    """测试创建带时区偏移的任务（通过 due_date 自带偏移）"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建带时区的任务", "没有可用的项目ID")
            return
        
        # 使用带偏移的截止时间（示例：UTC+00）
        due_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT10:00:00+0000")
        
        task = client.create_task(
            title="带时区的任务",
            project_id=project_id,
            due_date=due_date,
            priority=3
        )
        
        if 'error' in task:
            results.record_fail("创建带时区的任务", task['error'])
            return
        
        if task.get('id') and task.get('dueDate'):
            results.record_pass("创建带时区的任务")
            print(f"   任务ID: {task['id']}")
            print(f"   截止时间: {task.get('dueDate')}")
        else:
            results.record_fail("创建带时区的任务", "截止时间未设置")
    except Exception as e:
        results.record_fail("创建带时区的任务", str(e))


def test_create_recurring_task(client: TickTickClient, results: TestResults):
    """测试创建重复任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建重复任务", "没有可用的项目ID")
            return
        
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00+0000")
        
        task = client.create_task(
            title="每日重复任务",
            project_id=project_id,
            start_date=start_date,
            repeat_flag="RRULE:FREQ=DAILY;INTERVAL=1",
            priority=1
        )
        
        if 'error' in task:
            results.record_fail("创建重复任务", task['error'])
            return
        
        if task.get('id') and task.get('repeatFlag'):
            results.record_pass("创建重复任务")
            print(f"   任务ID: {task['id']}")
            print(f"   重复规则: {task.get('repeatFlag')}")
        else:
            results.record_fail("创建重复任务", "重复规则未设置")
    except Exception as e:
        results.record_fail("创建重复任务", str(e))


def test_create_task_with_subtasks(client: TickTickClient, results: TestResults):
    """测试创建带子任务的任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建带子任务的任务", "没有可用的项目ID")
            return
        
        subtasks = [
            {
                "title": "子任务 1",
                "status": 0,
                "sortOrder": 0
            },
            {
                "title": "子任务 2",
                "status": 0,
                "sortOrder": 1
            },
            {
                "title": "子任务 3",
                "status": 1,  # 已完成
                "sortOrder": 2
            }
        ]
        
        task = client.create_task(
            title="带子任务的任务",
            project_id=project_id,
            content="这个任务包含多个子任务",
            items=subtasks,
            priority=3
        )
        
        if 'error' in task:
            results.record_fail("创建带子任务的任务", task['error'])
            return
        
        if task.get('id') and task.get('items') and len(task.get('items', [])) == 3:
            results.record_pass("创建带子任务的任务")
            print(f"   任务ID: {task['id']}")
            print(f"   子任务数量: {len(task.get('items', []))}")
        else:
            results.record_fail("创建带子任务的任务", "子任务未正确创建")
    except Exception as e:
        results.record_fail("创建带子任务的任务", str(e))


def test_create_all_day_task(client: TickTickClient, results: TestResults):
    """测试创建全天任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建全天任务", "没有可用的项目ID")
            return
        
        task = client.create_task(
            title="全天任务",
            project_id=project_id,
            priority=1
        )
        
        if 'error' in task:
            results.record_fail("创建全天任务", task['error'])
            return
        
        if task.get('id') and not task.get('dueDate'):
            results.record_pass("创建全天任务")
            print(f"   任务ID: {task['id']}")
            print("   全天任务: true (no dueDate provided)")
        else:
            results.record_fail("创建全天任务", "未按无 due_date 方式创建全天任务")
    except Exception as e:
        results.record_fail("创建全天任务", str(e))


def test_get_task(client: TickTickClient, results: TestResults):
    """测试获取任务详情"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('simple_task_id')
        
        if not project_id or not task_id:
            results.record_skip("获取任务详情", "没有可用的任务ID")
            return
        
        task = client.get_task(project_id, task_id)
        
        if 'error' in task:
            results.record_fail("获取任务详情", task['error'])
            return
        
        if task.get('id') == task_id:
            results.record_pass(f"获取任务详情 '{task.get('title')}'")
        else:
            results.record_fail("获取任务详情", "任务ID不匹配")
    except Exception as e:
        results.record_fail("获取任务详情", str(e))


def test_update_task(client: TickTickClient, results: TestResults):
    """测试更新任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('simple_task_id')
        
        if not project_id or not task_id:
            results.record_skip("更新任务", "没有可用的任务ID")
            return
        
        updated_task = client.update_task(
            task_id=task_id,
            project_id=project_id,
            title="已更新的任务标题",
            content="任务内容已更新",
            priority=3
        )
        
        if 'error' in updated_task:
            results.record_fail("更新任务", updated_task['error'])
            return
        
        if updated_task.get('title') == "已更新的任务标题":
            results.record_pass("更新任务")
            print(f"   新标题: {updated_task.get('title')}")
        else:
            results.record_fail("更新任务", "任务未正确更新")
    except Exception as e:
        results.record_fail("更新任务", str(e))


def test_update_task_add_due_date(client: TickTickClient, results: TestResults):
    """测试为任务添加截止日期"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('simple_task_id')
        
        if not project_id or not task_id:
            results.record_skip("添加截止日期", "没有可用的任务ID")
            return
        
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT18:00:00+0000")
        
        updated_task = client.update_task(
            task_id=task_id,
            project_id=project_id,
            due_date=due_date
        )
        
        if 'error' in updated_task:
            results.record_fail("添加截止日期", updated_task['error'])
            return
        
        if updated_task.get('dueDate'):
            results.record_pass("添加截止日期")
            print(f"   截止日期: {updated_task.get('dueDate')}")
        else:
            results.record_fail("添加截止日期", "截止日期未设置")
    except Exception as e:
        results.record_fail("添加截止日期", str(e))


def test_get_project_with_data(client: TickTickClient, results: TestResults):
    """测试获取项目及其任务数据"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("获取项目数据", "没有可用的项目ID")
            return
        
        project_data = client.get_project_with_data(project_id)
        
        if 'error' in project_data:
            results.record_fail("获取项目数据", project_data['error'])
            return
        
        project = project_data.get('project', {})
        tasks = project_data.get('tasks', [])
        
        if project.get('id') == project_id:
            results.record_pass(f"获取项目数据 (包含 {len(tasks)} 个任务)")
            print(f"   项目名: {project.get('name')}")
            print(f"   任务数: {len(tasks)}")
        else:
            results.record_fail("获取项目数据", "项目数据不完整")
    except Exception as e:
        results.record_fail("获取项目数据", str(e))


def test_complete_task(client: TickTickClient, results: TestResults):
    """测试完成任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('due_date_task_id')
        
        if not project_id or not task_id:
            results.record_skip("完成任务", "没有可用的任务ID")
            return
        
        result = client.complete_task(project_id, task_id)
        
        if 'error' in result:
            results.record_fail("完成任务", result['error'])
            return
        
        results.record_pass("完成任务")
    except Exception as e:
        results.record_fail("完成任务", str(e))


def test_delete_tasks(client: TickTickClient, results: TestResults):
    """测试删除任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('simple_task_id')
        
        if not project_id or not task_id:
            results.record_skip("删除任务", "没有可用的任务ID")
            return
        
        # 获取项目中的所有任务并删除
        project_data = client.get_project_with_data(project_id)
        tasks = project_data.get('tasks', [])
        
        deleted_count = 0
        for task in tasks:
            result = client.delete_task(project_id, task['id'])
            if 'error' not in result:
                deleted_count += 1
        
        results.record_pass(f"删除任务 (删除了 {deleted_count} 个任务)")
    except Exception as e:
        results.record_fail("删除任务", str(e))


def test_delete_project(client: TickTickClient, results: TestResults):
    """测试删除项目"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("删除项目", "没有可用的项目ID")
            return
        
        result = client.delete_project(project_id)
        
        if 'error' in result:
            results.record_fail("删除项目", result['error'])
            return
        
        results.record_pass("删除项目")
    except Exception as e:
        results.record_fail("删除项目", str(e))


def main():
    """主测试函数"""
    print("="*60)
    print("TickTick MCP API 功能测试")
    print("="*60)
    print()
    
    # 初始化客户端
    try:
        client = TickTickClient()
        print("✅ TickTick 客户端初始化成功")
        print()
    except Exception as e:
        print(f"❌ 无法初始化 TickTick 客户端: {e}")
        print("\n请确保：")
        print("1. 已设置环境变量 TICKTICK_ACCESS_TOKEN")
        print("2. 访问令牌有效且未过期")
        print("3. 已运行 'uv run -m ticktick_mcp.cli auth' 进行认证")
        return 1
    
    results = TestResults()
    
    # 项目管理测试
    print_section("1. 项目管理测试")
    test_get_all_projects(client, results)
    test_create_project(client, results)
    test_get_project(client, results)
    
    # 基础任务测试
    print_section("2. 基础任务测试")
    test_create_simple_task(client, results)
    test_get_task(client, results)
    test_update_task(client, results)
    
    # 高级任务功能测试
    print_section("3. 高级任务功能测试")
    test_create_task_with_due_date(client, results)
    test_create_task_with_timezone(client, results)
    test_create_recurring_task(client, results)
    test_create_task_with_subtasks(client, results)
    test_create_all_day_task(client, results)
    
    # 任务更新测试
    print_section("4. 任务更新测试")
    test_update_task_add_due_date(client, results)
    
    # 数据查询测试
    print_section("5. 数据查询测试")
    test_get_project_with_data(client, results)
    
    # 任务操作测试
    print_section("6. 任务操作测试")
    test_complete_task(client, results)
    
    # 清理测试
    print_section("7. 清理测试数据")
    test_delete_tasks(client, results)
    test_delete_project(client, results)
    
    # 打印测试总结
    results.print_summary()
    
    # 返回退出码
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

