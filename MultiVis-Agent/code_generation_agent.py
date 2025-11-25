import os
import json
import re
import pandas as pd
from typing import Dict, Tuple, List
import altair as alt
import io
import matplotlib.pyplot as plt
import traceback
import base64
from contextlib import redirect_stdout, redirect_stderr

# 导入基类
from .utils.Agent import Agent


class CodeGenerationAgent(Agent):
    """代码生成智能体（Code Generation Agent）
    
    负责基于SQL查询结果和用户查询生成Altair可视化代码或修改已有代码。
    提供两个主要接口：
    1. generate_visualization_code: 生成全新可视化代码
    2. modify_visualization_code: 根据用户查询修改已有代码
    
    该智能体主要依赖LLM的代码生成能力和Altair可视化库的知识。
    """
    
    def __init__(self, model_type: str = "qwen-max-2025-01-25@qwen-vl-max-2025-01-25", agent_name: str = "code_generation_agent", agent_id: str = 0, use_log: bool = False):
        """初始化代码生成智能体
        
        Args:
            model_type: 使用的模型种类，格式为text_model@img_model，默认为qwen-max-2025-01-25@qwen-vl-max-2025-01-25
            agent_name: 智能体名称
            agent_id: 智能体ID
        """
        system_prompt = """You are a professional data visualization expert specializing in Altair. Your task is to generate and modify high-quality visualization code that is executable, efficient, and visually appealing.

## Core Responsibilities
1. Generate complete, executable Altair visualization code from user queries and SQL queries
2. Modify existing visualization code according to user queries
3. Ensure code quality, executability, and aesthetic design

## Output Requirements
- Provide complete, executable Python scripts with all necessary imports
- Include appropriate SQL query integration and data processing
- Focus only on implementing explicitly requested features (avoid adding unrequested elements)
- Do not set width and height for charts unless specifically requested

## Technical Guidelines
- Handle data transformation appropriately for visualization
- Design interactive elements when specified
- Apply proper visual encoding principles
- When using exec_altair_code:
  * Thoroughly analyze any error messages
  * Make comprehensive corrections before retrying
  * Never retry without significant improvements to the code

## Note
- When users provide reference images/reference code/code for iteration, you MUST generate visualization code that has similar visual components, appearance, and structure to those references. This is a strict requirement.
- Even when users don't explicitly restate all visualization requirements, maintain visual similarity to the provided references while incorporating any new specified requirements.
- When users don't provide reference images/reference code/code for iteration, generate entirely new visualization code based on their requirements
"""

        super().__init__(model_type=model_type, system_prompt=system_prompt, agent_name=agent_name, agent_id=agent_id, use_log=use_log)
        
        # 注册代码执行工具
        self._register_code_tools()
        
        self._log("代码生成智能体初始化完成")
    
    def _register_code_tools(self):
        """注册代码相关工具"""
        # 1. 执行代码工具
        self.register_tool(
            tool_name="exec_altair_code",
            tool_func=self._exec_altair_code,
            tool_description="Execute Python code implemented with Altair library and capture output or errors",
            tool_parameters={
                "code_string": {
                    "type": "string",
                    "description": "Python code with Altair library to execute"
                }
            },
            required=["code_string"]
        )
        
        # 2. 获取代码示例列表工具
        self.register_tool(
            tool_name="get_code_example_list",
            tool_func=self._get_code_example_list,
            tool_description="Get a list of available chart categories and types from the example directory",
            tool_parameters={},
            required=[]
        )
        
        # 3. 获取特定代码示例工具
        self.register_tool(
            tool_name="get_code_example",
            tool_func=self._get_code_example,
            tool_description="Get specific example code based on chart category and type",
            tool_parameters={
                "chart_category": {
                    "type": "string",
                    "description": "The category of the chart (e.g., 'Bar Charts', 'Line Charts')"
                },
                "chart_type": {
                    "type": "string",
                    "description": "The specific type of chart within the category (e.g., 'stacked_bar_chart', 'line_chart_with_confidence_interval')"
                }
            },
            required=["chart_category", "chart_type"]
        )
             
        self._log("代码工具注册完成")
    
    def _get_code_example_list(self) -> dict:
        """获取代码示例列表
        
        从./chart_example目录中获取所有图表类别和类型的列表
        
        Returns:
            dict: 包含图表类别和类型的字典
        """
        result = {}
        example_dir = "./chart_example"
        
        try:
            # 检查目录是否存在
            if not os.path.exists(example_dir) or not os.path.isdir(example_dir):
                return {"status": "fail", "info": f"Example directory {example_dir} not found"}
            
            # 获取所有类别（子目录）
            categories = [d for d in os.listdir(example_dir) if os.path.isdir(os.path.join(example_dir, d))]
            
            # 对于每个类别，获取所有类型（文件）
            for category in categories:
                category_path = os.path.join(example_dir, category)
                # 获取该类别下的所有Python文件
                chart_types = [
                    f.replace('.py', '') for f in os.listdir(category_path) 
                    if os.path.isfile(os.path.join(category_path, f)) and f.endswith('.py')
                ]
                result[category] = chart_types
            
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "fail", "info": f"Error getting code example list: {str(e)}"}
    
    def _get_code_example(self, chart_category: str, chart_type: str) -> dict:
        """获取特定代码示例
        
        根据图表类别和类型获取特定的代码示例
        
        Args:
            chart_category: 图表类别（例如"Bar Charts"）
            chart_type: 图表类型（例如"stacked_bar_chart"）
            
        Returns:
            dict: 包含代码示例的字典
        """
        example_dir = "./chart_example"
        
        try:
            # 构建文件路径
            file_path = os.path.join(example_dir, chart_category, f"{chart_type}.py")
            
            # 检查文件是否存在
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return {"status": "fail", "info": f"Example file not found: {file_path}"}
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            return {"status": "success", "data": code_content}
        except Exception as e:
            return {"status": "fail", "info": f"Error getting code example: {str(e)}"}
    
    def _exec_altair_code(self, code_string) -> dict:
        
        _exec_altair_code_result = self._execute_altair_code(code_string, "./test_tmp/test.png")
        
        # Format the return value according to the required format
        result = _exec_altair_code_result
        
        return result

    def _execute_altair_code(self, code_string: str, output_path: str) -> dict:
        """执行Altair代码并保存图像
        
        Args:
            code_string: 要执行的Altair代码
            output_path: 输出图像的保存路径
            
        Returns:
            dict: 执行结果，包含状态和信息
        """
        self._log(f"执行Altair代码并保存到: {output_path}")
        
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 创建命名空间，包含常用库
        namespace = {
            'alt': alt,
            'pd': pd,
            'np': __import__('numpy'),
            'sqlite3': __import__('sqlite3'),
            'io': __import__('io'),
            'os': __import__('os')
        }
        
        # 捕获标准输出和错误
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # 确保代码最终没有显示图表，而是保存图表
            lines = code_string.split('\n')
            lines = [line for line in lines if ".to_json()" not in line and "print(" not in line and "exit(" not in line]
            modified_code = '\n'.join(lines).replace("exit()", "")
            
            # 识别最后一个图表变量
            last_chart_var = None
            
            # 寻找所有可能的图表变量赋值语句
            chart_assignments = re.findall(r'(\w+)\s*=\s*alt\.Chart', modified_code)
            chart_assignments += re.findall(r'(\w+)\s*=\s*\(.*?\)\.resolve_scale', modified_code)
            chart_assignments += re.findall(r'(\w+)\s*=.*?(?:chart|Chart)', modified_code)
            
            # 如果找到了图表变量，使用最后一个
            if chart_assignments:
                last_chart_var = chart_assignments[-1]
            
            # 检查代码最后是否直接引用了一个变量（可能是图表）
            last_line_match = re.search(r'^\s*(\w+)\s*$', modified_code.split('\n')[-1].strip())
            if last_line_match:
                last_chart_var = last_line_match.group(1)
            
            # 添加保存语句，如果找到了最后的图表变量
            if last_chart_var and ".save('" not in modified_code and "alt.save(" not in modified_code:
                save_code = f"\n\n# 保存图表\n{last_chart_var}.save('{output_path}')\n"
                modified_code += save_code
                self._log(f"添加保存命令：{save_code}")
            
            # 执行代码
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(modified_code, namespace)
            
            # 检查图表是否被保存
            if not os.path.exists(output_path):
                # 如果没有保存，尝试找到chart对象并手动保存
                for var_name, var_value in namespace.items():
                    if isinstance(var_value, alt.TopLevelMixin):
                        self._log(f"找到图表对象：{var_name}")
                        var_value.save(output_path)
                        break
            
            # 再次检查
            if os.path.exists(output_path):
                self._log("成功执行Altair代码并保存图像")
                return {
                    "status": "success",
                    "info": "Chart Image Successfully Saved"
                }
            else:
                error_msg = "Execution successful but image not saved"
                self._log(error_msg)
                return {
                    "status": "fail",
                    "info": error_msg
                }
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            self._log(f"执行Altair代码失败: {error_msg}")
            return {
                "status": "fail",
                "info": error_msg + "\n" + stdout_capture.getvalue() + stderr_capture.getvalue()
            }
    
    def _execute_matplotlib_code(self, code_string: str, output_path: str) -> dict:
        """执行Matplotlib代码并保存图像
        
        Args:
            code_string: 要执行的Matplotlib代码
            output_path: 输出图像的保存路径
            
        Returns:
            dict: 执行结果，包含状态和信息
        """
        self._log(f"执行Matplotlib代码并保存到: {output_path}")
        
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 创建命名空间，包含常用库
        namespace = {
            'pd': pd,
            'plt': plt,
            'np': __import__('numpy')
        }
        
        # 捕获标准输出和错误
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # 清除之前的所有图形，避免状态污染
            plt.close('all')
            
            # 确保代码最终保存图表
            modified_code = code_string

            # 移除plt.show()调用，避免阻塞或显示窗口
            modified_code = modified_code.replace("plt.show()", "")
            
            # 如果代码中没有保存图表的命令，添加一个
            if "plt.savefig(" not in modified_code:
                modified_code += f"\n\n# 保存图表\nplt.savefig('{output_path}', bbox_inches='tight')\n"
            
            # 执行代码
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(modified_code, namespace)
            
            # 确保所有图形都已保存
            plt.savefig(output_path, bbox_inches='tight')
            
            # 清理：关闭所有图形
            plt.close('all')
            
            # 检查图表是否被保存
            if os.path.exists(output_path):
                self._log("成功执行Matplotlib代码并保存图像")
                return {
                    "status": "success",
                    "info": "Chart Image Successfully Saved"
                }
            else:
                error_msg = "Execution successful but image not saved"
                self._log(error_msg)
                return {
                    "status": "fail",
                    "info": error_msg
                }
            
        except Exception as e:
            # 确保清理所有图形，即使出现异常
            plt.close('all')
            
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            self._log(f"执行Matplotlib代码失败: {error_msg}")
            return {
                "status": "fail",
                "info": error_msg + "\n" + stdout_capture.getvalue() + stderr_capture.getvalue()
            }

    def generate_visualization_code(self, db_path: str, user_query: str, sql_query: str, reference_path: str = None, existing_code_path: str = None) -> Tuple[bool, str]:
        """生成全新可视化代码
        
        Args:
            db_path: 数据库文件路径
            user_query: 用户查询
            sql_query: SQL查询语句
            reference_path: (可选)参考图像或参考代码的文件路径(.png或.py文件)
            existing_code_path: (可选)已有代码的文件路径
            
        Returns:
            Tuple[bool, str]: 状态（成功/失败）和Python/Altair代码字符串
        """
        self._log(f"开始生成可视化代码，数据库: {db_path}")
        
        # 准备参考素材和图像URL
        reference_code = None
        reference_type = None
        img_sources = [] # [(url, description), ...]
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        if reference_path:
            if reference_path.lower().endswith(('.py')):
                reference_type = "code"
                try:
                    with open(reference_path, 'r', encoding='utf-8') as f:
                        reference_code = f.read()
                    self._log(f"成功加载参考代码: {reference_path}")
                    
                    # 执行参考代码并生成图像
                    temp_img_path = os.path.join(temp_dir, f"ref_code_vis_{self.agent_id}.png")
                    
                    # 根据代码内容判断使用哪种执行方法
                    if "import matplotlib" in reference_code or "from matplotlib" in reference_code:
                        exec_result = self._execute_matplotlib_code(reference_code, temp_img_path)
                    else:
                        # 默认使用Altair执行
                        exec_result = self._execute_altair_code(reference_code, temp_img_path)
                        
                    if exec_result["status"] == "success" and os.path.exists(temp_img_path):
                        # 转换图片为data URL格式
                        try:
                            img_url = self._img_to_img_url(temp_img_path)
                            img_sources.append((img_url, "Visualization generated from the Reference Code:"))
                            self._log(f"成功生成参考代码的图像: {temp_img_path}")
                        except Exception as e:
                            self._log(f"转换参考代码图像为URL失败: {str(e)}")
                    else:
                        self._log(f"执行参考代码生成图像失败: {exec_result.get('info', '未知错误')}")
                        
                except Exception as e:
                    self._log(f"加载参考代码失败: {str(e)}")
                    return False, {"error": f"Failed to load reference code: {str(e)}"}
            elif reference_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                reference_type = "image"
                try:
                    # 转换图片为data URL格式
                    img_url = self._img_to_img_url(reference_path)
                    img_sources.append((img_url, "Reference Image provided by user:"))
                    self._log(f"成功加载参考图像: {reference_path}")
                except Exception as e:
                    self._log(f"加载参考图像失败: {str(e)}")
                    return False, {"error": f"Failed to load reference image: {str(e)}"}
            else:
                self._log(f"不支持的参考文件格式: {reference_path}")
                return False, {"error": f"Unsupported reference file format: {reference_path}"}
        
        existing_code = None
        if existing_code_path:
            try:
                with open(existing_code_path, 'r', encoding='utf-8') as f:
                    existing_code = f.read()
                self._log(f"成功加载已有代码: {existing_code_path}")
                
                # 执行已有代码并生成图像
                temp_img_path = os.path.join(temp_dir, f"existing_code_vis_{self.agent_id}.png")
                
                # 根据代码内容判断使用哪种执行方法
                if "import matplotlib" in existing_code or "from matplotlib" in existing_code:
                    exec_result = self._execute_matplotlib_code(existing_code, temp_img_path)
                else:
                    # 默认使用Altair执行
                    exec_result = self._execute_altair_code(existing_code, temp_img_path)
                    
                if exec_result["status"] == "success" and os.path.exists(temp_img_path):
                    # 转换图片为data URL格式
                    try:
                        img_url = self._img_to_img_url(temp_img_path)
                        img_sources.append((img_url, "Visualization generated from the Existing Code:"))
                        self._log(f"成功生成已有代码的图像: {temp_img_path}")
                    except Exception as e:
                        self._log(f"转换已有代码图像为URL失败: {str(e)}")
                else:
                    self._log(f"执行已有代码生成图像失败: {exec_result.get('info', '未知错误')}")
            except Exception as e:
                self._log(f"加载已有代码失败: {str(e)}")
                return False, {"error": f"Failed to load existing code: {str(e)}"}
        
        # 构建提示词
        prompt = f"""
## Visualization Task
Generate Python visualization code using the Altair library based on the following:

### User Query
```plaintext
{user_query}
```

### SQL Query
```sql
{sql_query.strip()}
```

### Database Path
{db_path}

## IMPORTANT REQUIREMENTS
- When reference code or images are provided, you MUST generate visualization code that produces visuals with similar components, appearance, and structure to those references. This is a strict requirement.
- Maintain visual similarity to any provided references while incorporating new requirements.
- Your code must be complete, executable, and generate high-quality visualizations.
"""

        # 如果有参考代码，添加到提示词中
        if reference_code:
            prompt += f"""
### Reference Code
```python
{reference_code}
```
**Instruction:** Use this code as a primary reference. If a visualization generated from this code is provided below, use both the code and its visual output to guide your implementation.
"""

        # 如果有已有代码，添加到提示词中
        if existing_code:
            prompt += f"""
### Existing Code
```python
{existing_code}
```
**Instruction:** Consider this existing code. If a visualization generated from this code is provided below, use both the code and its visual output when modifying or generating new code.
"""

        prompt += """
### Output Format
<Final_Answer>
```python
[generated_code]
```
</Final_Answer>
"""
        # Build the user messages list with image context
        user_content_list = []
        user_content_list.append({"type": "text", "text": "<Question>\n" + prompt + "\n</Question>"})

        if img_sources:
            self._log(f"Adding {len(img_sources)} image(s) to the prompt context for Code Generation.")
            for img_url, description in img_sources:
                # Add text description before the image
                user_content_list.append({"type": "text", "text": f"\n--- IMAGE CONTEXT ---\n{description}\n(Image follows)"})
                # Add the image URL
                user_content_list.append({"type": "image_url", "image_url": {"url": img_url}})
        
        # 创建预迭代以减小api请求降低成本
        user_messages = [
            {"role": "user", "content": user_content_list},
            {"role": "assistant", "content": f"""<Thought>
Before I can generate any visualization code, I need to follow the MANDATORY REFERENCE CODE REQUIREMENT to get an appropriate example code. This is a strict requirement - I must never generate visualization code from scratch.

First, I'll use the get_code_example_list tool to see what chart categories and types are available. After analyzing the available examples, I can select the most appropriate one based on the user's requirements.

By exploring the example library first, I can:
1. Understand what chart types are available
2. Select the most appropriate reference for the user's needs
3. Ensure I'm following the mandatory requirement to base my code on an existing example
4. Make more informed decisions about the visualization approach

I'll start by getting the full list of chart categories and types.
</Thought>

<Action>
{json.dumps({"tool_name": "get_code_example_list", "parameters": {}}, ensure_ascii=False)}
</Action>
"""},
            {"role": "user", "content": f"""<Observation>
{json.dumps({"tool_name": "get_code_example_list", "result": self._get_code_example_list()}, ensure_ascii=False)}
</Observation>
"""}
        ]

        # 使用ReAct模式进行交互，包含图像URL
        self._log("启动ReAct模式进行可视化代码生成")
        result, used_tool = self.chat_ReAct(
            user_messages=user_messages,
            # temperature=0.2,
            max_iterations=10
        )
        
        self._log(f"ReAct模式生成完成，使用工具: {'是' if used_tool else '否'}")
        self._log(f"原始代码生成结果: {result}")
        
        # 尝试提取Python代码
        code_pattern = r'```(?:python)?\s*(import[\s\S]*?)```'
        match = re.search(code_pattern, result, re.DOTALL)
        
        if match:
            code = match.group(1).strip()
            self._log("成功从文本中提取Python代码")
            return True, code
        else:
            # 如果没有找到Python代码，尝试使用整个结果
            if result.strip().startswith("import"):
                self._log("使用原始结果作为Python代码")
                return True, result.strip()
            else:
                self._log("警告：无法提取Python代码")
                return False, {"error": "无法提取Python代码", "raw_result": result}

    def _img_to_img_url(self, img_path: str) -> str:
        """将图片转换为image_url
        
        支持jpg、png、jpeg格式
        
        Args:
            img_path: 图片文件路径
            
        Returns:
            str: 图片的data URL
            
        Raises:
            ValueError: 如果图片不存在或格式不支持
        """
        if not os.path.exists(img_path):
            self._log(f"图片文件不存在: {img_path}")
            raise ValueError(f"图片文件不存在: {img_path}")
            
        # 获取文件扩展名并确定mime type
        ext = os.path.splitext(img_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        
        if ext not in mime_types:
            self._log(f"不支持的图片格式: {ext}，仅支持 {', '.join(mime_types.keys())}")
            raise ValueError(f"不支持的图片格式: {ext}，仅支持 {', '.join(mime_types.keys())}")
        
        try:
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            # 检查编码字符串是否为空或太短
            if not encoded_string or len(encoded_string) < 10:
                error_msg = f"图片编码为空或太短: {img_path}, 长度: {len(encoded_string) if encoded_string else 0}"
                self._log(error_msg)
                raise ValueError(error_msg)
                
            return f"data:{mime_types[ext]};base64,{encoded_string}"
        except Exception as e:
            error_msg = f"读取图片文件失败: {str(e)}"
            self._log(error_msg)
            raise ValueError(error_msg)

    def modify_visualization_code(self, existing_code: str, recommendations: List[Dict] = None) -> Tuple[bool, str]:
        """根据需求修改已有代码
        
        Args:
            existing_code: 现有的代码字符串
            recommendations: 来自ValidationEvaluationAgent的代码修改建议列表
               - description: Detailed description of the issue and what needs to be fixed
               - priority: high|medium|low
               - component: data_processing|visualization_library|visualization_implementation
               - rationale: Explanation of why this change is necessary and how it addresses the issue
            
        Returns:
            Tuple[bool, str]: 状态（成功/失败）和修改后的Python/Altair代码字符串
        """
        self._log("开始修改可视化代码")

        if ".py" in existing_code:
            self._log("existing_code不能是文件路径")
            return False, {"error": "existing_code cannot be a file path"}
        
        # 如果没有建议，直接返回现有代码
        if not recommendations:
            self._log("没有代码修改建议，返回现有代码")
            return True, existing_code

        # 处理建议格式
        normalized_recommendations = []
        for rec in recommendations or []:
            # 创建一个新字典，避免修改原始对象
            normalized_rec = rec.copy() if isinstance(rec, dict) else {"description": str(rec)}
            normalized_recommendations.append(normalized_rec)
            
        self._log(f"修改建议数量: {len(normalized_recommendations)}")

        # 构建提示词
        prompt = f"""
## Visualization Code Modification Task

### Current Code
```python
{existing_code}
```

### Modification Recommendations
"""
        
        # 对建议按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        sorted_recs = sorted(
            normalized_recommendations, 
            key=lambda x: priority_order.get(x.get("priority", "medium").lower(), 1)
        )
        
        for i, rec in enumerate(sorted_recs, 1):
            if isinstance(rec, str):
                prompt += f"**#{i}**: {rec}\n"
            else:
                desc = rec.get("description", "Issue")
                priority = rec.get("priority", "medium").upper()
                component = rec.get("component", "")
                rationale = rec.get("rationale", "")
                
                prompt += f"**#{i} ({priority})**: {desc}\n"
                if component:
                    prompt += f"_Component: {component}_\n"
                if rationale:
                    prompt += f"_Rationale: {rationale}_\n\n"

        # 添加简洁的输出格式要求
        prompt += """
## Your Task
1. Apply the recommended modifications to the code
2. Maintain all essential functionality of the original code
3. Implement each recommendation carefully, considering the component and rationale provided
4. After modifications, test the code using the exec_altair_code tool
   - This tool only verifies if the code executes without errors
   - It cannot show you the actual visualization output
5. Fix any execution errors found during testing
6. Return only the complete, working code

## Follow these guidelines:
- Make targeted changes based specifically on the recommendations
- Do not introduce new features or functionality unless explicitly requested
- Preserve the overall structure of the visualization
- Do not remove any existing functionality unless specifically instructed
- Ensure all changes are compatible with the Altair library
- Verify code execution before submitting

## Output Format
<Final_Answer>
```python
[your modified code]
```
</Final_Answer>
"""

        # 创建预迭代以检查现有代码是否可执行
        user_messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": f"""<Thought>
I need to modify the visualization code according to the provided recommendations. Before making any changes, I should first check if the existing code can be executed without errors using the exec_altair_code tool.

This tool will only verify if the code runs without errors - it won't show me the actual visualization output. But this check is still important to ensure I'm starting with working code before applying modifications.
</Thought>

<Action>
{json.dumps({"tool_name": "exec_altair_code", "parameters": {"code_string": existing_code}}, ensure_ascii=False)}
</Action>
"""},
            {"role": "user", "content": f"""<Observation>
{json.dumps({"tool_name": "exec_altair_code", "result": self._exec_altair_code(existing_code)}, ensure_ascii=False)}
</Observation>
"""}
        ]

        # 使用ReAct模式进行交互
        self._log("启动ReAct模式进行代码修改")
        result, used_tool = self.chat_ReAct(
            user_messages=user_messages,
            # temperature=0.2,
            max_iterations=10
        )
        
        self._log(f"ReAct模式修改完成，使用工具: {'是' if used_tool else '否'}")
        self._log(f"原始代码修改结果: {result}")
        
        # 尝试提取最终代码 - 优化提取逻辑
        # 1. 首先尝试提取Python代码块
        code_pattern = r'```(?:python)?\s*(import[\s\S]*?)```'
        match = re.search(code_pattern, result, re.DOTALL)
        
        if match:
            code = match.group(1).strip()
            self._log("成功从代码块中提取修改后的Python代码")
            return True, code
        
        # 2. 尝试查找以import开头的内容块
        import_pattern = r'(?:^|\n)(import[\s\S]*?)(?:$|\n\n)'
        match = re.search(import_pattern, result, re.DOTALL)
        if match:
            code = match.group(1).strip()
            self._log("成功从文本中提取以import开头的Python代码块")
            return True, code
            
        # 3. 最后检查整个结果是否就是Python代码
        if result.strip().startswith("import"):
            self._log("使用整个响应作为修改后的Python代码")
            return True, result.strip()
        else:
            self._log("警告：无法提取修改后的Python代码")
            return False, {"error": "无法提取修改后的Python代码", "raw_result": result}


if __name__ == "__main__":
    # 测试代码生成智能体
    import sys
    import os
    
    # 创建日志目录
    os.makedirs("./logs", exist_ok=True)
    
    # 初始化代码生成智能体
    code_agent = CodeGenerationAgent(model_type="gemini-2.0-flash@gemini-2.0-flash", agent_id=20, use_log=True)
    
    code_agent._log("\n===== 测试 CodeGenerationAgent =====")
    
    user_query = "Can you create an interactive scatter plot showing the relationship between students' ages and how many activities they participate in? I'd like to see each student represented as a circle, with different colors for each major so I can spot any patterns across different fields of study."
    db_path = "./database/activity_1.sqlite"
    # reference_path = "./vis_bench/code/matplotlib/Advanced Calculations___calculate_residuals.py"
    sql_query = "SELECT S.Age, COUNT(P.actid) AS num_activities, S.Major FROM Student AS S JOIN Participates_in AS P ON S.StuID = P.stuid GROUP BY S.StuID;"
    
    
    code_agent._log("\n测试生成可视化代码 (使用参考图像):")
    status_with_ref, code_with_ref = code_agent.generate_visualization_code(
        db_path, user_query, sql_query
    )
    if status_with_ref:
        code_agent._log(f"使用参考图像生成的可视化代码:\n{code_with_ref}")
    else:
        code_agent._log(f"使用参考图像生成可视化代码失败: {code_with_ref}")

# #     code = """

# # import pandas as pd
# # import altair as alt
# # import sqlite3

# # # Connect to database
# # conn = sqlite3.connect('./database/baseball_1.sqlite')

# # # Execute SQL query to get data
# # sql_query = '''
# # SELECT year, team_id, SUM(hr) AS total_hr FROM batting GROUP BY year, team_id
# # '''
# # df = pd.read_sql_query(sql_query, conn)

# # # Calculate average home runs per team and year
# # ddf = df.groupby('year')['total_hr'].mean().reset_index()
# # ddf.rename(columns={'total_hr': 'avg_hr'}, inplace=True)

# # # Calculate confidence interval (example, replace with actual calculation)
# # ddf['upper'] = ddf['avg_hr'] + ddf['avg_hr'].std()  # Example: 1 standard deviation above average
# # ddf['lower'] = ddf['avg_hr'] - ddf['avg_hr'].std()  # Example: 1 standard deviation below average

# # # Create visualization
# # chart = alt.Chart(ddf).mark_line(point=False).encode(
# #     x=alt.X('year:T', axis=alt.Axis(title='Year')),
# #     y=alt.Y('avg_hr:Q', axis=alt.Axis(title='Average Home Runs per Team'))
# # ).properties(
# #     title='Average Team Home Runs per Year with 95% Confidence Interval'
# # )

# # band = alt.Chart(ddf).mark_area(opacity=0.3).encode(
# #     x='year:T',
# #     y='lower:Q',
# #     y2='upper:Q'
# # )

# # chart = band + chart

# # chart

# # """
#     test_code = """
# import altair as alt
# import pandas as pd
# import sqlite3

# # Database connection and data retrieval
# db_path = './database/activity_1.sqlite'
# conn = sqlite3.connect(db_path)
# query = '''
# SELECT 
#     S.StuID,
#     A.activity_name,
#     S.Age,
#     AVG(S.Age) OVER (PARTITION BY A.activity_name) AS avg_age_by_activity,
#     S.Age - AVG(S.Age) OVER (PARTITION BY A.activity_name) AS age_delta
# FROM 
#     Student AS S
# JOIN 
#     Participates_in AS P ON S.StuID = P.StuID
# JOIN 
#     Activity AS A ON P.actid = A.actid
# '''
# df = pd.read_sql_query(query, conn)
# conn.close()

# # Altair chart
# chart = alt.Chart(df).mark_point().encode(
#     x=alt.X('activity_name:N', title='Activity Name'),
#     y=alt.Y('age_delta:Q', title='Age Delta'),
#     color=alt.Color('age_delta:Q', title='Age Delta')
# ).properties(
#     title='Age Delta vs. Activity'
# )

# chart
# """

# #     test_query = "I came across this line chart with a shaded band that shows trends and uncertainty—it looks really professional. Could you create something similar to visualize how the average number of home runs per team has changed over the years, using the batting data from the database? I'd like to see the full history of baseball home runs with a 95% confidence interval band around the average, and make the chart wider to show the long-term trend better."

#     sql_query = """SELECT 
#     A.activity_name,
#     AVG(S.Age) AS Avg_Age
# FROM 
#     Activity AS A
# JOIN 
#     Participates_in AS P ON A.actid = P.actid
# JOIN 
#     Student AS S ON P.stuid = S.StuID
# GROUP BY 
#     A.actid, A.activity_name;"""

#     python_recommendations = [
#     {
#       "description": "Change the color scheme to red-blue using `alt.Scale(scheme='redblue')`.",
#       "modification_type": "code",
#       "priority": "high",
#       "component": "visualization_implementation"
#     },
#     {
#       "description": "Modify the chart title to 'Difference in Average Age by Activity'.",
#       "modification_type": "code",
#       "priority": "medium",
#       "component": "visualization_implementation"
#     }
#   ]

    
#     code_agent._log("\n测试根据评估结果修改可视化代码:")
#     mod_status, modified_code = code_agent.modify_visualization_code(
#         test_code, 
#         # sql_query,
#         python_recommendations=python_recommendations
#     )
#     if mod_status:
#         code_agent._log(f"根据评估结果修改后的可视化代码:\n{modified_code}")
#     else:
#         code_agent._log(f"根据评估结果修改可视化代码失败: {modified_code}")
    
    code_agent._log("\n===== 测试完成 =====") 