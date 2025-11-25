import os
import re
from typing import Dict, List, Tuple
import json

# 导入基类和其他智能体
from .utils.Agent import Agent
from .database_query_agent import DatabaseQueryAgent
from .code_generation_agent import CodeGenerationAgent
from .validation_evaluation_agent import ValidationEvaluationAgent


class CoordinatorAgent(Agent):
    """协调器智能体（Coordinator Agent）
    
    作为整个系统的核心控制单元，负责解析任务类型，协调各专业智能体的工作，并确保信息的正确流动。
    
    核心责任：
    1. 确定任务类型（A/B/C/D）
    2. 根据任务类型设计执行路径
    3. 调用各专业智能体并传递必要信息
    4. 管理任务状态和中间结果
    5. 实施错误恢复和重试策略
    6. 收集最终结果并整合输出
    """
    
    def __init__(self, model_type: str = "qwen-max-2025-01-25@qwen-vl-max-2025-01-25", agent_name: str = "coordinator_agent", agent_id: str = None, use_log: bool = False):
        """初始化协调器智能体
        
        Args:
            model_type: 使用的模型种类，格式为text_model@img_model，默认为qwen-max-2025-01-25@qwen-vl-max-2025-01-25
            agent_name: 智能体名称
            agent_id: 智能体ID
            use_log: 是否使用日志
        """
        system_prompt = """You are a visualization system coordinator that efficiently orchestrates specialized agents to create high-quality data visualizations. Your task is to analyze requirements, coordinate data preparation, generate visualization code, and ensure quality through validation and iteration.

## Task Types
- Type A: Natural language query + database → visualization
- Type B: Natural language query + database + reference images → visualization matching image style
- Type C: Natural language query + database + reference code → visualization based on code patterns
- Type D: Natural language query + database + existing visualization code → improved visualization

## Core Workflow
1. Determine task type and requirements
2. Generate SQL to extract required data
3. Generate visualization code
4. Validate results and iterate until requirements are met

## Tool Usage Guidelines
- generate_sql_from_query: Creates SQL to extract data
- generate_visualization_code: Creates visualization code
- modify_visualization_code: Fixes code issues (ONLY after evaluate_visualization)
- evaluate_visualization: Validates visualization and provides improvement recommendations

## CRITICAL WORKFLOW RULES
1. ALWAYS generate SQL first, then visualization code
2. ALWAYS evaluate visualization before making modifications
3. ONLY use modification tools with recommendations from evaluate_visualization
4. Re-evaluate after each modification
5. Continue until requirements are met or max iterations reached

When complete, provide the final visualization code that meets all requirements.
"""

        super().__init__(model_type=model_type, system_prompt=system_prompt, agent_name=agent_name, agent_id=agent_id, use_log=use_log)
        
        # 初始化任务状态和中间结果存储
        self.user_query = None
        self.db_path = None
        self.reference_path = None
        self.existing_code = None
        self.existing_code_path = None
        self.task_type = None
        self.sql_query = None
        self.visualization_code = None
        self.evaluation_result = None
        
        # 评估结果详细信息
        self.evaluation_passed = False
        self.sql_recommendations = []
        self.recommendations = []
        
        # 初始化各专业智能体实例(用于注册工具)
        self._db_agent = DatabaseQueryAgent(model_type=model_type, agent_id=agent_id, use_log=use_log)
        self._code_agent = CodeGenerationAgent(model_type=model_type, agent_id=agent_id, use_log=use_log)
        self._validation_agent = ValidationEvaluationAgent(model_type=model_type, agent_id=agent_id, use_log=use_log)

        # 任务类型描述
        self.task_descriptions = {
            "A": "Basic visualization from natural language query and database",
            "B": "Visualization matching reference image style",
            "C": "Visualization based on reference code patterns",
            "D": "Improvement of existing visualization code"
        }
        
        # 注册各专业智能体工具
        self._register_agent_tools()

        self.chat_status(False)
        
        self._log("协调器智能体初始化完成")
    
    def _register_agent_tools(self):
        """注册各专业智能体工具"""
        # 1. 数据库与查询智能体工具
        self.register_tool(
            tool_name="generate_sql_from_query",
            tool_func=self._generate_sql_from_query_tool,
            tool_description="Generate SQL query based on user query and database schema",
            tool_parameters={},
            required=[]
        )
        
        # 2. 代码生成智能体工具
        self.register_tool(
            tool_name="generate_visualization_code",
            tool_func=self._generate_visualization_code_tool,
            tool_description="Generate visualization code based on user query, database, and SQL query",
            tool_parameters={},
            required=[]
        )
        
        self.register_tool(
            tool_name="modify_visualization_code",
            tool_func=self._modify_visualization_code_tool,
            tool_description="Modify visualization code based on evaluation recommendations (ONLY use after evaluate_visualization)",
            tool_parameters={},
            required=[]
        )
        
        # 3. 验证评估智能体工具
        self.register_tool(
            tool_name="evaluate_visualization",
            tool_func=self._evaluate_visualization_tool,
            tool_description="Evaluate if visualization meets requirements and provide improvement suggestions",
            tool_parameters={},
            required=[]
        )
        
        self._log("智能体工具注册完成")
    
    def _generate_sql_from_query_tool(self) -> Dict:
        """生成SQL查询工具
        
        Returns:
            Dict: 操作状态和简要说明
        """
        self._log(f"调用生成SQL查询工具")
        
        if not self.user_query or not self.db_path:
            self._log("生成SQL查询失败：缺少用户查询或数据库路径")
            return {"status": False, "message": "Missing user query or database path"}
        
        status, result = self._db_agent.generate_sql_from_query(self.db_path, self.user_query)
        
        if not status:
            self._log("生成SQL查询失败")
            return {"status": False, "message": "Failed to generate SQL query"}
        
        # 将结果保存到实例属性
        self.sql_query = result
        
        self._log("生成SQL查询成功")
        return {"status": True, "message": "SQL query generated successfully"}

    def _generate_visualization_code_tool(self) -> Dict:
        """生成可视化代码工具
        
        Returns:
            Dict: 操作状态和简要说明
        """
        self._log("调用生成可视化代码工具")
        
        # 验证先决条件
        if not self.db_path:
            return {"status": False, "message": "Database path not specified"}
        if not self.user_query:
            return {"status": False, "message": "User query is empty"}
        if not self.sql_query:
            return {"status": False, "message": "SQL query not generated yet"}
            
        status, result = self._code_agent.generate_visualization_code(
            self.db_path, 
            self.user_query, 
            self.sql_query, 
            self.reference_path,
            self.existing_code_path
        )
        
        if not status:
            self._log("生成可视化代码失败")
            return {"status": False, "message": "Failed to generate visualization code"}
        
        # 保存生成的可视化代码
        self.visualization_code = result
        
        self._log("生成可视化代码成功")
        return {"status": True, "message": "Visualization code generated successfully"}
    
    def _modify_visualization_code_tool(self) -> Dict:
        """修改可视化代码工具
        
        Returns:
            Dict: 操作状态和简要说明
        """
        self._log("调用修改可视化代码工具")
        
        # 验证先决条件
        if not self.visualization_code:
            return {"status": False, "message": "No visualization code to modify"}
            
        if not self.evaluation_result:
            error_msg = "Must call evaluate_visualization before using modify_visualization_code"
            self._log(error_msg)
            return {"status": False, "message": error_msg}
        
        if not self.recommendations:
            self._log("无Python代码修改建议，无需修改可视化代码")
            return {"status": True, "message": "No code modifications needed"}
        
        status, result = self._code_agent.modify_visualization_code(
            self.visualization_code,
            self.recommendations
        )
        
        if not status:
            self._log("修改可视化代码失败")
            return {"status": False, "message": "Failed to modify visualization code"}
        
        # 更新可视化代码
        self.visualization_code = result
        
        self._log("修改可视化代码成功")
        return {"status": True, "message": "Visualization code modified successfully"}
    
    def _evaluate_visualization_tool(self) -> Dict:
        """验证可视化工具
        
        Returns:
            Dict: 验证结果字典，包含评估是否通过(True/False)和改进建议及下一步操作指南。
        """
        self._log("调用验证可视化工具")
        
        # 验证先决条件
        if not self.user_query:
            return {"evaluation_success": False, "message": "User query is empty"}
        if not self.visualization_code:
            return {"evaluation_success": False, "message": "No visualization code to evaluate"}
            
        status, result = self._validation_agent.evaluate_visualization(
            self.user_query,
            self.visualization_code,
            reference_path=self.reference_path,
            existing_code_path=self.existing_code_path,
            force_failure=self.force_failure
        )
        
        # 保存评估结果
        self.evaluation_result = result
        self.force_failure = False
        
        # 更新评估详细信息
        self.evaluation_passed = status
        self.recommendations = result.get("recommendations", [])
        
        # 根据评估结果决定下一步操作
        if status:
            # 当评估通过时，指导Agent输出最终结果
            return {
                "evaluation_success": True,
                "message": "The visualization successfully meets all requirements. You should now output the final answer in the following format:\n<Final_Answer>\nMission Complete. The visualization successfully meets all requirements.\n</Final_Answer>",
                "passed": True,
                "complete": True
            }
        else:
            # 评估未通过，提供明确的下一步指南
            recommendations_count = len(self.recommendations)
            
            if recommendations_count > 0:
                next_action = "modify_visualization_code"
                message = f"Evaluation failed with {recommendations_count} code issues. Next step: Call modify_visualization_code to fix code problems, then call evaluate_visualization again."
            else:
                self._log(f"评估未通过，但建议为空：{result}")
                if self.task_type != "D":
                    next_action = "unknown"
                    message = "Evaluation failed but no specific recommendations available. Consider revising the entire approach."
                else:
                    next_action = "evaluate_visualization"
                    message = "Evaluation failed but no specific recommendations available. Consider trying again."

            return {
                "evaluation_success": True,
                "message": message,
                "passed": False,
                "next_action": next_action,
                "modification_count": recommendations_count
            }
    
    def process_item(self, item: dict) -> dict:
        """处理数据集中的item
        
        Args:
            item: 数据集中的项目
            
        Returns:
            dict: 处理结果
        """
        user_query = item['NLQ']
        db_path = f"./database/{item['db_id']}.sqlite"
        reference_path = None
        existing_code_path = None

        # 根据任务类型设置相应参数
        if item['type'] == 'type_A':
            # 基础任务，无需额外参数
            pass
        elif item['type'] == 'type_B':
            # 图像参考任务
            reference_path = item['reference_path']
        elif 'type_C' in item['type']:
            # 代码参考任务
            reference_path = item['reference_path']
        elif item['type'] == 'type_D':
            # 迭代改进任务
            existing_code_path = item['original_code_path']

        # 记录任务信息
        self._log(f"处理数据集项：类型={item['type']}, 查询={user_query[:50]}...")
        
        # 处理任务 - 直接调用process_task，确保参数传递正确
        # 注意：process_task方法参数列表为(user_query, db_path, reference_path, existing_code_path, max_iterations)
        status, result = self.process_task(
            user_query=user_query, 
            db_path=db_path, 
            reference_path=reference_path,
            existing_code_path=existing_code_path
        )

        # 构建和返回结果项
        result_item = {
            'type': item['type'],
            'NLQ': user_query,
            'db_id': item['db_id'],
            'chart_category': item.get('chart_category', ''),
            'chart_type': item.get('chart_type', ''),
            'label': item.get('code', ''),
            'prediction': result,
            'status': status
        }

        return result_item
    
    def _reset_state(self):
        """重置智能体状态"""
        self.user_query = None
        self.db_path = None
        self.reference_path = None
        self.existing_code = None
        self.existing_code_path = None
        self.task_type = None
        self.sql_query = None
        self.visualization_code = None
        self.evaluation_result = None
        self.force_failure = False
        
        # 重置评估结果
        self.evaluation_passed = False
        self.sql_recommendations = []
        self.recommendations = []

    def process_task(self, 
                    user_query: str, 
                    db_path: str, 
                    reference_path: str = None,
                    existing_code_path: str = None,
                    max_iterations: int = 10) -> Tuple[bool, str]:
        """处理可视化任务的主流程
        
        Args:
            user_query: 用户查询
            db_path: 数据库路径
            reference_path: 参考图像或代码路径（可选）
            existing_code: 已有的可视化代码（可选）
            existing_code_path: 已有的可视化代码路径（可选）
            max_iterations: 最大迭代次数
            
        Returns:
            Tuple[bool, str]: 状态（成功/失败）和可视化代码
        """
        self._log(f"开始处理可视化任务")
        
        # 重置状态并保存初始参数
        self._reset_state()
        self.user_query = user_query
        self.db_path = db_path
        self.reference_path = reference_path
        self.existing_code_path = existing_code_path

        if existing_code_path:
            try:
                with open(existing_code_path, 'r', encoding='utf-8') as f:
                    self.visualization_code = f.read()
                    # self.force_failure = True
                    self._log(f"成功加载已有代码: {existing_code_path}")

            except Exception as e:
                 self._log(f"加载已有代码失败 {existing_code_path}: {e}. Continuing without pre-loaded code.")
                 self.visualization_code = None # Ensure it's None if loading failed
        
        # 确定任务类型
        self.task_type = self._determine_task_type(user_query, db_path, reference_path, existing_code_path)
        
        # 构建初始提示词
        initial_prompt = self._build_task_prompt(max_iterations)
        
        # ----- Pre-iteration Step -----
        user_messages = [{"role": "user", "content": initial_prompt}]
        
        # Determine the first action based on task type
        # if self.task_type == "D":
        if False:
            first_action_tool_name = "evaluate_visualization"
            first_action_thought = "The task is type D (Improvement), so I need to evaluate the existing visualization first."
            first_action_func = self._evaluate_visualization_tool
            first_action_params = {} # No params needed for this tool wrapper
        else:
            first_action_tool_name = "generate_sql_from_query"
            # first_action_thought = "The task is not type D, so I need to generate the SQL query first."
            first_action_thought = "I need to generate the SQL query first."
            first_action_func = self._generate_sql_from_query_tool
            first_action_params = {} # No params needed for this tool wrapper

        # Construct the first assistant message (thought + action)
        first_action_json = json.dumps({"tool_name": first_action_tool_name, "parameters": first_action_params}, ensure_ascii=False)
        assistant_content = f"<Thought>\n{first_action_thought}\n</Thought>\n<Action>\n{first_action_json}\n</Action>"
        user_messages.append({"role": "assistant", "content": assistant_content})
        
        # Simulate the first observation
        self._log(f"Executing pre-iteration step: {first_action_tool_name}")
        try:
            # Ensure necessary attributes are set before calling the tool function
            # For generate_sql_from_query: user_query, db_path must be set
            # For evaluate_visualization: user_query, visualization_code must be set (loaded above for type D)
            first_observation_result = first_action_func()
            self._log(f"Pre-iteration result: {first_observation_result}")
        except Exception as e:
            self._log(f"Error during pre-iteration execution of {first_action_tool_name}: {e}")
            first_observation_result = {"status": False, "message": f"Error during pre-iteration: {e}"}

        observation_content = f"<Observation>\n{json.dumps({'tool_name': first_action_tool_name, 'result': first_observation_result}, ensure_ascii=False)}\n</Observation>"
        user_messages.append({"role": "user", "content": observation_content})
        # ----- End Pre-iteration Step -----

        # 启动ReAct处理模式
        self._log(f"开始ReAct处理模式，任务类型：{self.task_type}, 使用预迭代历史.")
        
        # 使用ReAct模式执行任务，传入预迭代消息
        result, used_tool = self.chat_ReAct(
            user_messages=user_messages, # Use the pre-populated message list
            # temperature=0.2,
            max_iterations=max_iterations,
        )
        
        self._log(f"ReAct模式处理完成，使用工具: {'是' if used_tool else '否'}")
        
        # 返回结果
        if self.visualization_code:
            self._log("任务处理成功")
            return True, self.visualization_code
        else:
            self._log("任务处理失败：未生成可视化代码")
            return False, "Failed to generate visualization code"
    
    def _build_task_prompt(self, max_iterations: int) -> str:
        """构建任务提示词
        
        Args:
            max_iterations: 最大迭代次数
            
        Returns:
            str: 任务提示词
        """
        # 获取任务类型描述
        task_type_desc = self.task_descriptions.get(self.task_type, "Unknown")
        
        # 基本信息
        prompt = f"""# Visualization Task Type {self.task_type}

## Task Information
- Type: {self.task_type} ({task_type_desc})
- Query: "{self.user_query}"
- Database: "{self.db_path}"
"""

        # 添加参考信息
        if self.reference_path:
            prompt += f"- Reference: \"{self.reference_path}\"\n"
        
        if self.existing_code and self.existing_code_path:
            prompt += f"""- Existing Code: "{self.existing_code_path}"
```python
{self.existing_code[:500]}... (truncated)
```
"""
        
        # 为不同任务类型提供不同的工作流程指导
        # if self.task_type == "D":  # 对于改进现有可视化代码的任务
        if False:  # 对于改进现有可视化代码的任务
            prompt += f"""
## ReAct Workflow for Type D (Improvement)
1. Evaluate existing visualization with evaluate_visualization
2. If evaluation fails:
   - Use modify_visualization_code to implement recommended changes
3. Re-evaluate after EACH modification
4. Continue until requirements met or max {max_iterations} iterations reached

IMPORTANT:
- ALWAYS evaluate visualization after every modification

Start the workflow by calling evaluate_visualization first.
"""
        else:  # 对于其他类型的任务，保持原有流程
            prompt += f"""
## ReAct Workflow
1. Generate SQL query with generate_sql_from_query
2. Generate visualization code with generate_visualization_code
3. Evaluate with evaluate_visualization
4. If evaluation fails:
   - If SQL recommendations provided, use modify_sql_query FIRST
   - After SQL is fixed or if no SQL recommendations, use modify_visualization_code for Python recommendations
5. Re-evaluate after EACH modification
6. Continue until requirements met or max {max_iterations} iterations reached

IMPORTANT:
- ALWAYS evaluate visualization after every modification
- ALWAYS fix SQL issues before code issues
- If both SQL and Python recommendations exist, handle SQL first, then Python

Start the workflow by calling generate_sql_from_query first.
"""
        
        return prompt
    
    def _determine_task_type(self, 
                           user_query: str, 
                           db_path: str, 
                           reference_path: str = None, 
                           existing_code_path: str = None) -> str:
        """确定任务类型
        
        Args:
            user_query: 用户查询
            db_path: 数据库路径
            reference_path: 参考图像或代码路径（可选）
            existing_code_path: 已有的可视化代码路径（可选）
            
        Returns:
            str: 任务类型 ('A', 'B', 'C', 'D')
        """
        self._log("开始确定任务类型")
        
        # 检查输入确定任务类型
        if existing_code_path:
            task_type = "D"  # 迭代任务
        elif reference_path:
            # 检查参考文件类型
            if reference_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                task_type = "B"  # 图像参考
            elif reference_path.lower().endswith(('.py', '.ipynb')):
                task_type = "C"  # 代码参考
            else:
                task_type = "A"  # 默认为基础任务
                self._log(f"警告：无法识别参考文件类型 {reference_path}，默认为A类任务")
        else:
            task_type = "A"  # 基础任务
        
        self._log(f"任务类型确定为：{task_type}")
        return task_type


if __name__ == "__main__":
    # 测试协调器智能体
    import sys
    import os
    
    # 创建日志目录
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./test_tmp", exist_ok=True)
    
    # 初始化协调器智能体
    coordinator = CoordinatorAgent(model_type="gemini-2.0-flash@gemini-2.0-flash", agent_id=233, use_log=True)
    
    print("\n===== 测试 CoordinatorAgent =====")
    
    user_query = """Can you create an interactive scatter plot showing the relationship between how many days wrestlers held their titles and how long they lasted in elimination matches? I'd like to see each wrestler represented as a circle, with the x-axis showing days held and the y-axis showing elimination time in seconds. Please color-code the circles based on which team each wrestler belonged to."""
    db_path = "./database/wrestler.sqlite"
    # reference_path = "./vis_bench/code/matplotlib/Advanced Calculations___calculate_residuals.py"
    # existing_code_path = "./vis_bench/vis_modify/Advanced Calculations___calculate_residuals___activity_1.py"

    status, result = coordinator.process_task(user_query, db_path)

    coordinator._log(f"最终可视化代码:\n{result}")
    
    print("\n===== 测试完成 =====") 