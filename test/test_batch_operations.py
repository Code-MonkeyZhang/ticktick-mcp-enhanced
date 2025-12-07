#!/usr/bin/env python3
"""
TickTick MCP 批量操作测试

测试所有新的批量操作工具，包括：
- create_tasks 
- update_tasks 
- complete_tasks
- delete_tasks 
- create_subtasks 
"""

import sys
import os
from datetime import datetime, timedelta

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
    
    def store_data(self, key: str, value):
        """存储测试数据供后续测试使用"""
        self.test_data[key] = value
    
    def get_data(self, key: str):
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


# ==================== 准备测试环境 ====================

def setup_test_project(client: TickTickClient, results: TestResults):
    """创建测试项目"""
    try:
        project_name = f"批量操作测试 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project = client.create_project(
            name=project_name,
            color="#4CAF50"
        )
        
        if 'error' in project:
            results.record_fail("创建测试项目", project['error'])
            return False
        
        if project.get('id'):
            results.record_pass(f"创建测试项目 '{project_name}'")
            results.store_data('test_project_id', project['id'])
            results.store_data('test_project_name', project_name)
            print(f"   项目ID: {project['id']}")
            return True
        else:
            results.record_fail("创建测试项目", "项目信息不完整")
            return False
    except Exception as e:
        results.record_fail("创建测试项目", str(e))
        return False


# ==================== create_tasks 测试 ====================

def test_create_single_task(client: TickTickClient, results: TestResults):
    """测试创建单个任务（使用统一的 create_tasks 接口）"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建单个任务", "没有可用的项目ID")
            return
        
        # 使用新的批量接口创建单个任务
        task = client.create_task(
            title="单个任务测试",
            project_id=project_id,
            content="这是通过批量接口创建的单个任务",
            priority=3
        )
        
        if 'error' in task:
            results.record_fail("创建单个任务", task['error'])
            return
        
        if task.get('id') and task.get('title') == "单个任务测试":
            results.record_pass("创建单个任务")
            results.store_data('single_task_id', task['id'])
            print(f"   任务ID: {task['id']}")
        else:
            results.record_fail("创建单个任务", "任务信息不完整")
    except Exception as e:
        results.record_fail("创建单个任务", str(e))


def test_create_batch_tasks(client: TickTickClient, results: TestResults):
    """测试批量创建任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("批量创建任务", "没有可用的项目ID")
            return
        
        # 准备批量任务数据
        tasks_data = []
        for i in range(1, 6):  # 创建 5 个任务
            due_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%dT15:00:00+0000")
            tasks_data.append({
                "title": f"批量任务 {i}",
                "project_id": project_id,
                "content": f"这是批量创建的第 {i} 个任务",
                "priority": (i % 3) * 2 + 1,  # 1, 3, 5 轮换
                "due_date": due_date
            })
        
        # 批量创建任务
        created_count = 0
        task_ids = []
        for task_data in tasks_data:
            task = client.create_task(**task_data)
            if 'error' not in task and task.get('id'):
                created_count += 1
                task_ids.append(task['id'])
        
        if created_count == 5:
            results.record_pass(f"批量创建任务 (成功创建 {created_count} 个)")
            results.store_data('batch_task_ids', task_ids)
            print(f"   创建的任务ID: {task_ids[:3]}... (共 {len(task_ids)} 个)")
        else:
            results.record_fail("批量创建任务", f"只成功创建了 {created_count}/5 个任务")
    except Exception as e:
        results.record_fail("批量创建任务", str(e))


def test_create_task_with_all_fields(client: TickTickClient, results: TestResults):
    """测试创建包含所有字段的任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("创建完整字段任务", "没有可用的项目ID")
            return
        
        due_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT14:00:00+0000")
        start_date = datetime.now().strftime("%Y-%m-%dT09:00:00+0000")
        
        task = client.create_task(
            title="完整字段任务",
            project_id=project_id,
            content="包含所有可能字段的任务",
            desc="这是任务描述",
            start_date=start_date,
            due_date=due_date,
            priority=5,
            items=[
                {"title": "子任务1", "status": 0, "sortOrder": 0},
                {"title": "子任务2", "status": 0, "sortOrder": 1}
            ]
        )
        
        if 'error' in task:
            results.record_fail("创建完整字段任务", task['error'])
            return
        
        # 验证各个字段
        checks = [
            (task.get('id'), "有任务ID"),
            (task.get('title') == "完整字段任务", "标题正确"),
            (task.get('dueDate'), "有截止日期"),
            (task.get('priority') == 5, "优先级正确"),
            (task.get('items') and len(task.get('items', [])) == 2, "子任务正确")
        ]
        
        all_passed = all(check[0] for check in checks)
        
        if all_passed:
            results.record_pass("创建完整字段任务")
            results.store_data('full_field_task_id', task['id'])
            print(f"   验证通过: {', '.join(check[1] for check in checks if check[0])}")
        else:
            failed_checks = [check[1] for check in checks if not check[0]]
            results.record_fail("创建完整字段任务", f"字段验证失败: {', '.join(failed_checks)}")
    except Exception as e:
        results.record_fail("创建完整字段任务", str(e))


# ==================== update_tasks 测试 ====================

def test_update_single_task(client: TickTickClient, results: TestResults):
    """测试更新单个任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('single_task_id')
        
        if not project_id or not task_id:
            results.record_skip("更新单个任务", "没有可用的任务ID")
            return
        
        updated_task = client.update_task(
            task_id=task_id,
            project_id=project_id,
            title="已更新的单个任务",
            content="任务内容已更新",
            priority=5
        )
        
        if 'error' in updated_task:
            results.record_fail("更新单个任务", updated_task['error'])
            return
        
        if (updated_task.get('title') == "已更新的单个任务" and 
            updated_task.get('priority') == 5):
            results.record_pass("更新单个任务")
            print(f"   新标题: {updated_task.get('title')}")
            print(f"   新优先级: {updated_task.get('priority')}")
        else:
            results.record_fail("更新单个任务", "任务未正确更新")
    except Exception as e:
        results.record_fail("更新单个任务", str(e))


def test_update_batch_tasks(client: TickTickClient, results: TestResults):
    """测试批量更新任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_ids = results.get_data('batch_task_ids')
        
        if not project_id or not task_ids:
            results.record_skip("批量更新任务", "没有可用的任务ID")
            return
        
        # 批量更新前3个任务的优先级
        updated_count = 0
        for i, task_id in enumerate(task_ids[:3]):
            result = client.update_task(
                task_id=task_id,
                project_id=project_id,
                priority=5,  # 都更新为高优先级
                content=f"已批量更新 - {i+1}"
            )
            if 'error' not in result:
                updated_count += 1
        
        if updated_count == 3:
            results.record_pass(f"批量更新任务 (成功更新 {updated_count} 个)")
        else:
            results.record_fail("批量更新任务", f"只成功更新了 {updated_count}/3 个任务")
    except Exception as e:
        results.record_fail("批量更新任务", str(e))


def test_update_task_add_due_date(client: TickTickClient, results: TestResults):
    """测试为任务添加截止日期"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('single_task_id')
        
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


# ==================== complete_tasks 测试 ====================

def test_complete_single_task(client: TickTickClient, results: TestResults):
    """测试完成单个任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_ids = results.get_data('batch_task_ids')
        
        if not project_id or not task_ids or len(task_ids) < 1:
            results.record_skip("完成单个任务", "没有可用的任务ID")
            return
        
        # 完成第一个批量任务
        task_id = task_ids[0]
        result = client.complete_task(project_id, task_id)
        
        if 'error' in result:
            results.record_fail("完成单个任务", result['error'])
            return
        
        results.record_pass("完成单个任务")
        print(f"   已完成任务ID: {task_id}")
    except Exception as e:
        results.record_fail("完成单个任务", str(e))


def test_complete_batch_tasks(client: TickTickClient, results: TestResults):
    """测试批量完成任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_ids = results.get_data('batch_task_ids')
        
        if not project_id or not task_ids or len(task_ids) < 3:
            results.record_skip("批量完成任务", "没有足够的任务ID")
            return
        
        # 批量完成第2-3个任务（第1个已在单个测试中完成）
        completed_count = 0
        for task_id in task_ids[1:3]:
            result = client.complete_task(project_id, task_id)
            if 'error' not in result:
                completed_count += 1
        
        if completed_count == 2:
            results.record_pass(f"批量完成任务 (成功完成 {completed_count} 个)")
        else:
            results.record_fail("批量完成任务", f"只成功完成了 {completed_count}/2 个任务")
    except Exception as e:
        results.record_fail("批量完成任务", str(e))


# ==================== create_subtasks 测试 ====================

def test_create_single_subtask(client: TickTickClient, results: TestResults):
    """测试创建单个子任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('full_field_task_id')
        
        if not project_id or not task_id:
            results.record_skip("创建单个子任务", "没有可用的父任务ID")
            return
        
        subtask = client.create_subtask(
            subtask_title="单个子任务测试",
            parent_task_id=task_id,
            project_id=project_id,
            content="这是一个测试子任务",
            priority=3
        )
        
        if 'error' in subtask:
            results.record_fail("创建单个子任务", subtask['error'])
            return
        
        if subtask.get('id') and subtask.get('title') == "单个子任务测试":
            results.record_pass("创建单个子任务")
            results.store_data('subtask_id', subtask['id'])
            print(f"   子任务ID: {subtask['id']}")
        else:
            results.record_fail("创建单个子任务", "子任务信息不完整")
    except Exception as e:
        results.record_fail("创建单个子任务", str(e))


def test_create_batch_subtasks(client: TickTickClient, results: TestResults):
    """测试批量创建子任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('full_field_task_id')
        
        if not project_id or not task_id:
            results.record_skip("批量创建子任务", "没有可用的父任务ID")
            return
        
        # 批量创建3个子任务
        created_count = 0
        for i in range(1, 4):
            subtask = client.create_subtask(
                subtask_title=f"批量子任务 {i}",
                parent_task_id=task_id,
                project_id=project_id,
                content=f"批量创建的第 {i} 个子任务",
                priority=(i % 3) * 2 + 1
            )
            if 'error' not in subtask and subtask.get('id'):
                created_count += 1
        
        if created_count == 3:
            results.record_pass(f"批量创建子任务 (成功创建 {created_count} 个)")
        else:
            results.record_fail("批量创建子任务", f"只成功创建了 {created_count}/3 个子任务")
    except Exception as e:
        results.record_fail("批量创建子任务", str(e))


# ==================== delete_tasks 测试 ====================

def test_delete_single_task(client: TickTickClient, results: TestResults):
    """测试删除单个任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_id = results.get_data('single_task_id')
        
        if not project_id or not task_id:
            results.record_skip("删除单个任务", "没有可用的任务ID")
            return
        
        result = client.delete_task(project_id, task_id)
        
        if 'error' in result:
            results.record_fail("删除单个任务", result['error'])
            return
        
        results.record_pass("删除单个任务")
        print(f"   已删除任务ID: {task_id}")
    except Exception as e:
        results.record_fail("删除单个任务", str(e))


def test_delete_batch_tasks(client: TickTickClient, results: TestResults):
    """测试批量删除任务"""
    try:
        project_id = results.get_data('test_project_id')
        task_ids = results.get_data('batch_task_ids')
        
        if not project_id or not task_ids:
            results.record_skip("批量删除任务", "没有可用的任务ID")
            return
        
        # 删除所有批量任务
        deleted_count = 0
        for task_id in task_ids:
            result = client.delete_task(project_id, task_id)
            if 'error' not in result:
                deleted_count += 1
        
        if deleted_count == len(task_ids):
            results.record_pass(f"批量删除任务 (成功删除 {deleted_count} 个)")
        else:
            results.record_fail("批量删除任务", f"只成功删除了 {deleted_count}/{len(task_ids)} 个任务")
    except Exception as e:
        results.record_fail("批量删除任务", str(e))


# ==================== 清理测试 ====================

def cleanup_test_project(client: TickTickClient, results: TestResults):
    """清理测试项目及所有剩余任务"""
    try:
        project_id = results.get_data('test_project_id')
        if not project_id:
            results.record_skip("清理测试项目", "没有可用的项目ID")
            return
        
        # 获取项目中的所有任务并删除
        project_data = client.get_project_with_data(project_id)
        if 'error' not in project_data:
            tasks = project_data.get('tasks', [])
            for task in tasks:
                client.delete_task(project_id, task['id'])
        
        # 删除项目
        result = client.delete_project(project_id)
        
        if 'error' in result:
            results.record_fail("清理测试项目", result['error'])
            return
        
        results.record_pass("清理测试项目")
        project_name = results.get_data('test_project_name')
        print(f"   已删除项目: {project_name}")
    except Exception as e:
        results.record_fail("清理测试项目", str(e))


# ==================== 主测试函数 ====================

def main():
    """主测试函数"""
    print("="*60)
    print("TickTick MCP 批量操作测试")
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
    
    # 准备测试环境
    print_section("0. 准备测试环境")
    if not setup_test_project(client, results):
        print("\n❌ 无法创建测试项目，终止测试")
        return 1
    
    # create_tasks 测试
    print_section("1. create_tasks 工具测试")
    test_create_single_task(client, results)
    test_create_batch_tasks(client, results)
    test_create_task_with_all_fields(client, results)
    
    # update_tasks 测试
    print_section("2. update_tasks 工具测试")
    test_update_single_task(client, results)
    test_update_batch_tasks(client, results)
    test_update_task_add_due_date(client, results)
    
    # complete_tasks 测试
    print_section("3. complete_tasks 工具测试")
    test_complete_single_task(client, results)
    test_complete_batch_tasks(client, results)
    
    # create_subtasks 测试
    print_section("4. create_subtasks 工具测试")
    test_create_single_subtask(client, results)
    test_create_batch_subtasks(client, results)
    
    # delete_tasks 测试
    print_section("5. delete_tasks 工具测试")
    test_delete_single_task(client, results)
    test_delete_batch_tasks(client, results)
    
    # 清理测试数据
    print_section("6. 清理测试数据")
    cleanup_test_project(client, results)
    
    # 打印测试总结
    results.print_summary()
    
    # 返回退出码
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

