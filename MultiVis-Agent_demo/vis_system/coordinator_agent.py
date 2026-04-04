import os
import re
from typing import Dict, List, Tuple
import json
from datetime import datetime

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
    
    def __init__(self, model_type: str = "gemini-2.0-flash@gemini-2.0-flash", agent_name: str = "coordinator_agent", agent_id: str = None, use_log: bool = False):
        """初始化协调器智能体
        
        Args:
            model_type: 使用的模型种类，格式为text_model@img_model，默认为gemini-2.0-flash@gemini-2.0-flash
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
    
    def _execute_visualization_code(self, code: str, iteration: int) -> str:
        """执行可视化代码并生成图表
        
        Args:
            code: 可视化代码
            iteration: 当前迭代次数
            
        Returns:
            str: 图表文件路径，如果失败则返回None
        """
        if not code.strip():
            return None
            
        # 为每次迭代生成唯一的图表文件名
        chart_filename = f"generated_chart_iter_{iteration}.png"
        chart_path = f"./test_tmp/{chart_filename}"
        
        # 确保目录存在
        os.makedirs("./test_tmp", exist_ok=True)
        
        try:
            # 使用代码生成智能体的执行方法
            # 打印代码前几行，用于调试
            self._log(f"代码前100个字符: {code[:100]}")
            
            # 更宽松的检测条件
            is_matplotlib = 'matplotlib' in code or 'plt.' in code
            is_altair = 'altair' in code or 'alt.' in code or 'Chart(' in code
            
            self._log(f"代码类型检测: matplotlib={is_matplotlib}, altair={is_altair}")
            
            if is_matplotlib:
                result = self._code_agent._execute_matplotlib_code(code, chart_path)
                # Matplotlib不支持交互式JSON格式
                self.chart_json_path = None
            elif is_altair:
                self._log("检测到Altair代码，使用_execute_altair_code方法")
                result = self._code_agent._execute_altair_code(code, chart_path)
                # 获取JSON路径
                if result.get('status') == 'success':
                    if 'json_path' in result:
                        self.chart_json_path = result['json_path']
                        self._log(f"获取到Altair JSON路径: {self.chart_json_path}")
                        
                        # 确认JSON文件是否存在
                        if os.path.exists(self.chart_json_path):
                            self._log(f"确认JSON文件存在: {self.chart_json_path}")
                        else:
                            self._log(f"警告：JSON路径存在但文件不存在: {self.chart_json_path}")
                            
                            # 尝试推断JSON路径
                            json_path = chart_path.replace('.png', '.vega.json')
                            if os.path.exists(json_path):
                                self.chart_json_path = json_path
                                self._log(f"找到推断的JSON路径: {self.chart_json_path}")
                            else:
                                self._log(f"推断的JSON路径也不存在: {json_path}")
                    else:
                        self._log("结果中没有json_path字段")
                        
                        # 尝试推断JSON路径
                        json_path = chart_path.replace('.png', '.vega.json')
                        if os.path.exists(json_path):
                            self.chart_json_path = json_path
                            self._log(f"找到推断的JSON路径: {self.chart_json_path}")
                        else:
                            self.chart_json_path = None
                            self._log(f"推断的JSON路径不存在: {json_path}")
                else:
                    self.chart_json_path = None
                    self._log("Altair代码执行失败，无法获取JSON路径")
            else:
                # 默认尝试matplotlib
                result = self._code_agent._execute_matplotlib_code(code, chart_path)
                self.chart_json_path = None
            
            if result.get('status') == 'success' and os.path.exists(chart_path):
                # 同时更新当前的chart_path（为了最终结果也使用最新的图表）
                self.chart_path = chart_path
                self._log(f"成功设置chart_path: {self.chart_path}")
                
                # 同时设置标准的generated_chart.png路径，用于历史记录备份
                standard_chart_path = "./test_tmp/generated_chart.png"
                try:
                    import shutil
                    shutil.copy2(chart_path, standard_chart_path)
                    self._log(f"已复制图表到标准路径: {standard_chart_path}")
                except Exception as e:
                    self._log(f"复制图表到标准路径失败: {e}")
                
                return chart_path
            else:
                self._log(f"执行可视化代码失败: {result.get('info', 'Unknown error')}")
                return None
                
        except Exception as e:
            self._log(f"执行可视化代码异常: {str(e)}")
            return None
    
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

    def _format_iteration_process(self, final_code: str) -> str:
        """格式化迭代过程，只显示最新的迭代代码
        
        Args:
            final_code: 最终生成的代码
            
        Returns:
            str: 最新迭代的代码，如果没有迭代记录则返回最终代码
        """
        if not hasattr(self, 'iteration_trace') or not self.iteration_trace:
            return final_code
        
        # 找到最后一个有代码的迭代，只返回那个代码
        for step in reversed(self.iteration_trace):
            if step.get('code'):
                return step['code']
        
        # 如果没有找到迭代中的代码，返回最终代码
        return final_code

    def _format_evaluation_result(self) -> str:
        """Format evaluation result as readable text
        
        Returns:
            str: Formatted evaluation result
        """
        if not hasattr(self, 'evaluation_result') or not self.evaluation_result:
            return "No evaluation result available"
        
        result = self.evaluation_result
        formatted_text = "=== Visualization Evaluation Results ===\n\n"
        
        # Basic information
        if 'evaluation_summary' in result:
            formatted_text += f"📋 Summary: {result['evaluation_summary']}\n\n"
        elif 'analysis_summary' in result:
            formatted_text += f"📋 Summary: {result['analysis_summary']}\n\n"
        
        # 检查数据格式并显示评估状态
        if 'matches_requirements' in result:
            # 传统格式 - 有完整的评估结果
            matches_req = result.get('matches_requirements', False)
            status_emoji = "✅" if matches_req else "❌"
            formatted_text += f"{status_emoji} Evaluation Status: {'Passed' if matches_req else 'Failed'}\n\n"
        else:
            # Recommendations格式 - 评估失败的情况，使用evaluation_passed属性
            status_emoji = "✅" if getattr(self, 'evaluation_passed', False) else "❌"
            formatted_text += f"{status_emoji} Evaluation Status: {'Passed' if getattr(self, 'evaluation_passed', False) else 'Failed'}\n\n"
        
        # Quality scores
        if 'quality_scores' in result:
            scores = result['quality_scores']
            formatted_text += "📊 Quality Scores:\n"
            if 'visual_clarity' in scores:
                formatted_text += f"  • Visual Clarity: {scores['visual_clarity']}/10\n"
            if 'design_aesthetics' in scores:
                formatted_text += f"  • Design Aesthetics: {scores['design_aesthetics']}/10\n"
            if 'code_quality_impression' in scores:
                formatted_text += f"  • Code Quality: {scores['code_quality_impression']}/10\n"
            formatted_text += "\n"
        
        # Validation checks
        if 'validation_checks' in result:
            checks = result['validation_checks']
            formatted_text += "🔍 Validation Checks:\n"
            for check_name, check_result in checks.items():
                check_emoji = "✅" if check_result is True else "❌" if check_result is False else "⚪"
                check_display = check_name.replace('_', ' ').title()
                formatted_text += f"  {check_emoji} {check_display}: {check_result}\n"
            formatted_text += "\n"
        
        # Explicit requirements analysis
        if 'explicit_requirements_analysis' in result:
            requirements = result['explicit_requirements_analysis']
            if requirements:
                formatted_text += "📝 User Requirements Analysis:\n"
                for req in requirements:
                    req_emoji = "✅" if req.get('is_met', False) else "❌"
                    formatted_text += f"  {req_emoji} \"{req.get('requirement_quote', '')}\"\n"
                    if 'evidence' in req:
                        formatted_text += f"     Evidence: {req['evidence']}\n"
                formatted_text += "\n"
        
        # Improvement recommendations
        if 'recommendations_for_improvement' in result:
            recommendations = result['recommendations_for_improvement']
            if recommendations:
                formatted_text += "💡 Improvement Recommendations:\n"
                for rec in recommendations:
                    priority = rec.get('priority', 'medium')
                    priority_emoji = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    formatted_text += f"  {priority_emoji} {rec.get('description', '')}\n"
                formatted_text += "\n"
        
        # Failure reasons (if any)
        matches_req = result.get('matches_requirements', False)
        if not matches_req and 'failure_reasons' in result:
            reasons = result['failure_reasons']
            if reasons:
                formatted_text += "⚠️ Failure Reasons:\n"
                for reason in reasons:
                    formatted_text += f"  • {reason}\n"
        
        # 处理recommendations格式的数据（当评估失败时validation_agent返回的格式）
        if 'recommendations' in result and result['recommendations']:
            formatted_text += "🔧 Code Improvement Recommendations:\n"
            for rec in result['recommendations']:
                priority = rec.get('priority', 'medium')
                priority_emoji = "🔴" if priority == 'critical' else "🟠" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                description = rec.get('recommendation_description', rec.get('description', ''))
                component = rec.get('component', '')
                formatted_text += f"  {priority_emoji} [{priority.upper()}] {description}\n"
                if component:
                    formatted_text += f"     Component: {component}\n"
            formatted_text += "\n"
        
        # 显示detailed_analysis信息（如果有）
        if 'detailed_analysis' in result and result['detailed_analysis']:
            formatted_text += "🔍 Detailed Analysis:\n"
            for analysis in result['detailed_analysis']:
                issue_desc = analysis.get('issue_description', '')
                root_cause = analysis.get('root_cause_explanation', '')
                if issue_desc:
                    formatted_text += f"  • Issue: {issue_desc}\n"
                if root_cause:
                    formatted_text += f"    Cause: {root_cause}\n"
            formatted_text += "\n"
        
        return formatted_text

    def process(
        self,
        db_name: str,
        nl_query: str,
        ref_code: str = None,
        mod_code: str = None,
        ref_image_path: str = None,
        max_iterations: int = 10
    ) -> dict:
        """
        Web接口专用：统一处理并返回所有可视化相关结果
        """
        # 参考代码和图片都可能是reference_path
        reference_path = ref_image_path or None
        if ref_code:
            # 保存参考代码到临时文件
            reference_path = f"temp_ref_code_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
            with open(reference_path, "w", encoding="utf-8") as f:
                f.write(ref_code)
        existing_code_path = None
        if mod_code:
            existing_code_path = f"temp_mod_code_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
            with open(existing_code_path, "w", encoding="utf-8") as f:
                f.write(mod_code)
        if db_name.endswith('.sqlite') or db_name.endswith('.db'):
            db_path = f"./database/{db_name}"
        else:
            db_path = f"./database/{db_name}.sqlite"

        # 调用主流程
        status, vis_code = self.process_task(
            user_query=nl_query,
            db_path=db_path,
            reference_path=reference_path,
            existing_code_path=existing_code_path,
            max_iterations=max_iterations
        )

        # 执行最终的可视化代码生成图表
        chart_img = None
        chart_json = None
        
        if status and vis_code:
            self._log("开始执行最终可视化代码生成图表")
            chart_path = self._execute_visualization_code(vis_code, 1)  # 使用迭代1作为最终值
            
            if chart_path:
                self._log(f"最终图表生成成功，路径: {chart_path}")
            else:
                self._log("最终图表生成失败")
        
        self._log(f"检查chart_path: hasattr={hasattr(self, 'chart_path')}, chart_path={getattr(self, 'chart_path', 'None')}")
        if hasattr(self, 'chart_path') and self.chart_path:
            self._log(f"chart_path存在, 路径: {self.chart_path}, 文件存在: {os.path.exists(self.chart_path)}")
            if os.path.exists(self.chart_path):
                # 返回静态文件URL，确保路径格式正确
                # 移除前缀 "./" 并确保使用正斜杠
                normalized_path = self.chart_path.replace('\\', '/').lstrip('./')
                chart_img = '/' + normalized_path
                self._log(f"设置chart_img为: {chart_img}")
            else:
                self._log(f"chart_path文件不存在: {self.chart_path}")
        else:
            self._log("没有chart_path或chart_path为空")
            
        # 处理JSON格式图表
        self._log(f"检查chart_json_path: hasattr={hasattr(self, 'chart_json_path')}, chart_json_path={getattr(self, 'chart_json_path', 'None')}")
        
        # 首先检查是否有明确设置的JSON路径
        if hasattr(self, 'chart_json_path') and self.chart_json_path:
            self._log(f"chart_json_path存在, 路径: {self.chart_json_path}, 文件存在: {os.path.exists(self.chart_json_path)}")
            if os.path.exists(self.chart_json_path):
                # 返回JSON文件URL，确保路径格式正确
                normalized_json_path = self.chart_json_path.replace('\\', '/').lstrip('./')
                chart_json = '/' + normalized_json_path
                self._log(f"设置chart_json为: {chart_json}")
            else:
                self._log(f"chart_json_path文件不存在: {self.chart_json_path}")
        else:
            self._log("没有chart_json_path或chart_json_path为空")
        
        # 如果没有找到chart_json，尝试从chart_path推断
        if not chart_json and hasattr(self, 'chart_path') and self.chart_path:
            # 尝试多种可能的JSON文件名格式
            possible_json_paths = [
                self.chart_path.replace('.png', '.vega.json'),
                self.chart_path.replace('.png', '.json'),
                os.path.join(os.path.dirname(self.chart_path), 'generated_chart.vega.json')
            ]
            
            for json_path in possible_json_paths:
                self._log(f"尝试推断JSON路径: {json_path}")
                if os.path.exists(json_path):
                    normalized_json_path = json_path.replace('\\', '/').lstrip('./')
                    chart_json = '/' + normalized_json_path
                    self._log(f"从chart_path推断设置chart_json为: {chart_json}")
                    break
                    
        # 最后一次尝试：直接检查test_tmp目录中的JSON文件
        if not chart_json:
            default_json_path = "./test_tmp/generated_chart.vega.json"
            self._log(f"尝试使用默认JSON路径: {default_json_path}")
            if os.path.exists(default_json_path):
                normalized_json_path = default_json_path.replace('\\', '/').lstrip('./')
                chart_json = '/' + normalized_json_path
                self._log(f"使用默认JSON路径设置chart_json为: {chart_json}")

        # 评估结果 - 格式化为可读文本
        eval_result = self._format_evaluation_result() if hasattr(self, 'evaluation_result') and self.evaluation_result else None

        # SQL及其迭代过程
        sql_iter = self.sql_query if hasattr(self, 'sql_query') else None

        # 可视化代码及其迭代过程 - 收集迭代历史
        vis_code_iter = self._format_iteration_process(vis_code)

        return {
            'vis_code': vis_code,
            'vis_code_iter': vis_code_iter,
            'chart_img': chart_img,
            'chart_json': chart_json,
            'sql': sql_iter,
            'sql_iter': sql_iter,
            'eval_result': eval_result
        }


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
