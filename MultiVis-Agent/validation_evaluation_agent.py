import os
import json
import demjson3
import re
import traceback
import base64
from typing import Dict, Tuple
import io
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt

# 导入基类
from .utils.Agent import Agent


class ValidationEvaluationAgent(Agent):
    """验证评估智能体（Validation & Evaluation Agent）
    
    负责验证生成的可视化是否符合用户需求。
    提供主要接口：
    evaluate_visualization: 验证可视化是否符合需求
    
    该智能体依赖LLM的评估能力、可视化库的执行能力和图像比较能力。
    """
    
    def __init__(self, model_type: str = "qwen-max-2025-01-25@qwen-vl-max-2025-01-25", agent_name: str = "validation_evaluation_agent", agent_id: str = 0, use_log: bool = False):
        """初始化验证评估智能体
        
        Args:
            model_type: 使用的模型种类，格式为text_model@img_model，默认为qwen-max-2025-01-25@qwen-vl-max-2025-01-25
            log_folder: 日志文件路径
        """
        system_prompt = """You are a specialized data visualization validator who rigorously evaluates visualization code against both technical standards and user requirements."""

        super().__init__(model_type=model_type, system_prompt=system_prompt, agent_name=agent_name, agent_id=agent_id, use_log=use_log)
        
        self._log("验证评估智能体初始化完成")

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
                modified_code += f"\n\n# 清理旧图形以防万一\nplt.close('all')\n# 保存图表\nplt.savefig('{output_path}', bbox_inches='tight')\n"
            else:
                # If savefig exists, ensure close is called before it, handle potential multiple savefig calls? (Simplest: add close before the final implicit save)
                # For simplicity, we'll still add the explicit savefig call preceded by close, potentially causing double save if already present. A better approach would parse the code.
                modified_code += f"\n\n# 确保清理并保存\nplt.close('all')\nplt.savefig('{output_path}', bbox_inches='tight')\n"
            
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
    
    def evaluate_visualization(self, user_query: str, code: str, reference_path: str = None, existing_code_path: str = None, force_failure: bool = False) -> Tuple[bool, Dict]:
        """验证可视化是否符合用户需求
        
        Args:
            user_query: 用户的原始查询文本
            code: 可视化代码字符串
            reference_path: (可选)参考图像或参考代码的文件路径(.png/.jpg/.jpeg或.py文件)
            existing_code_path: (可选)已有代码路径（迭代场景）
            force_failure: (可选)是否强制评估不通过，默认为False
            
        Returns:
            Tuple[bool, Dict]: 状态（成功/失败）和验证结果
                               如果通过验证，返回(True, {})
                               如果未通过验证，返回(False, {'python_recommendations': [{'description': '问题描述', 'modification_content': '修改建议', 'priority': '优先级', 'component': '组件'}, ...], ...})
                               如果执行失败，返回(False, {'error': '错误信息'})
        """
        self._log(f"开始验证可视化，场景: {'有参考图像' if reference_path and reference_path.lower().endswith(('.png', '.jpg', '.jpeg')) else '有参考代码' if reference_path and reference_path.lower().endswith('.py') else '有迭代代码' if existing_code_path else '基础输入'}, force_failure: {force_failure}")
        
        temp_dir = "./test_tmp/"
        os.makedirs(temp_dir, exist_ok=True)

        code = code.strip()

        # 设置生成图像的路径
        generated_path = os.path.join(temp_dir, f"generated_vis_{self.agent_id}.png")
        reference_output_path = os.path.join(temp_dir, f"ref_vis_{self.agent_id}.png")
        existing_output_path = os.path.join(temp_dir, f"existing_vis_{self.agent_id}.png")

        # List to hold image sources (url, description)
        img_sources = []

        # 执行可视化代码并保存图像
        if "matplotlib" in code:
            exec_info = self._execute_matplotlib_code(code, generated_path)
        else:
            exec_info = self._execute_altair_code(code, generated_path) # Default to Altair
        
        if exec_info["status"] == "fail":
            self._log(f"可视化代码执行失败: {exec_info['info']}")
            return False, {"error": "code execution failed", "details": exec_info["info"]}
        
        # 转换生成的图像为URL
        try:
            generated_img_url = self._img_to_img_url(generated_path)
            img_sources.append((generated_img_url, "Generated Visualization (from the code being evaluated):"))
            self._log("生成的可视化图像已转换为URL并添加标签")
        except Exception as e:
            self._log(f"转换生成的图像为URL失败: {str(e)}")
            return False, {"error": f"failed to convert generated image to URL: {str(e)}"}
        
        # 处理参考资料（如果有）
        reference_code = None
        reference_type = None
        if reference_path:
            if reference_path.lower().endswith(('.py')):
                # 处理参考代码
                reference_type = "code"
                try:
                    reference_code = open(reference_path, 'r', encoding='utf-8').read()
                    self._log("成功读取参考代码")
                    
                    # 执行参考代码生成参考图像
                    if "matplotlib" in reference_code:
                        exec_info = self._execute_matplotlib_code(reference_code, reference_output_path)
                    else:
                        exec_info = self._execute_altair_code(reference_code, reference_output_path)
                    
                    if exec_info["status"] == "success":
                        ref_code_img_url = self._img_to_img_url(reference_output_path)
                        img_sources.append((ref_code_img_url, "Visualization generated from the Reference Code:"))
                        self._log("参考代码执行成功并生成图像URL")
                    else:
                        self._log(f"参考代码执行失败: {exec_info['info']}")
                        # Don't fail evaluation, just proceed without the reference image
                except Exception as e:
                    self._log(f"处理参考代码失败: {str(e)}")
                    # Don't fail evaluation, just proceed without the reference image
            elif reference_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                # 处理参考图像
                reference_type = "image"
                try:
                    if os.path.exists(reference_path):
                        ref_img_url = self._img_to_img_url(reference_path)
                        img_sources.append((ref_img_url, "Reference Image provided by user:"))
                        self._log("成功转换参考图像为URL")
                    else:
                        self._log(f"参考图像不存在: {reference_path}")
                        # Don't fail evaluation
                except Exception as e:
                    self._log(f"处理参考图像失败: {str(e)}")
                    # Don't fail evaluation
            else:
                self._log(f"不支持的参考资料类型: {reference_path}")
                # Don't fail evaluation
        
        # 处理迭代场景的已有代码（如果有）
        existing_code = None
        if existing_code_path:
            try:
                if os.path.exists(existing_code_path):
                    # 读取已有代码内容
                    existing_code = open(existing_code_path, 'r', encoding='utf-8').read()
                    self._log("成功读取已有代码")
                    
                    # 尝试执行已有代码生成图像
                    if "matplotlib" in existing_code:
                        exec_info = self._execute_matplotlib_code(existing_code, existing_output_path)
                    else:
                        exec_info = self._execute_altair_code(existing_code, existing_output_path)
                    
                    if exec_info["status"] == "success":
                        existing_code_img_url = self._img_to_img_url(existing_output_path)
                        img_sources.append((existing_code_img_url, "Visualization generated from the Previous/Existing Code:"))
                        self._log("已有代码执行成功并生成图像URL")
                    else:
                        self._log(f"已有代码执行失败，但继续进行评估: {exec_info['info']}")
                else:
                    self._log(f"已有代码文件不存在: {existing_code_path}")
                    # Don't fail evaluation
            except Exception as e:
                self._log(f"处理已有代码失败: {str(e)}")
                # Don't fail evaluation
        
        # 构建评估提示词
        prompt = self._build_evaluation_prompt(
            user_query=user_query,
            code=code,
            reference_path=reference_path,
            reference_type=reference_type, # Pass determined type
            reference_code=reference_code,
            existing_code_path=existing_code_path,
            existing_code=existing_code,
            force_failure=force_failure
        )

        # 准备图像URL列表和用户内容，用于LLM多模态评估
        user_content_list = []
        user_content_list.append({"type": "text", "text": prompt})
        
        if img_sources:
            self._log(f"Adding {len(img_sources)} image(s) to the evaluation prompt context.")
            # Sort sources to try and ensure generated is first, reference/existing second
            img_sources.sort(key=lambda x: "Generated" not in x[1]) 
            
            # 过滤掉无效的图像URL
            valid_img_sources = []
            for img_url, description in img_sources:
                # 检查URL是否以data:开头且包含base64内容
                if img_url.startswith("data:") and ";base64," in img_url:
                    # 检查base64内容是否非空
                    parts = img_url.split(";base64,")
                    if len(parts) == 2 and len(parts[1]) > 100:  # 确保有足够长的base64内容
                        valid_img_sources.append((img_url, description))
                        self._log(f"有效图像URL: {description}")
                    else:
                        self._log(f"跳过无效图像URL (内容太短): {description}")
                else:
                    self._log(f"跳过无效图像URL (格式错误): {description}")
            
            # 使用过滤后的有效图像URL
            for img_url, description in valid_img_sources:
                user_content_list.append({"type": "text", "text": f"\n--- IMAGE CONTEXT ---\n{description}\n(Image follows)"})
                user_content_list.append({"type": "image_url", "image_url": {"url": img_url}})
            
            self._log(f"添加了 {len(valid_img_sources)}/{len(img_sources)} 个有效图像URL")
        else:
            self._log("No image context available for evaluation.")

        user_messages = [{"role": "user", "content": user_content_list}]

        # 使用LLM进行评估
        self._log("开始使用LLM进行可视化评估")
        
        result = self.generate_response(
            user_messages=user_messages, # Pass the structured list
            # temperature=0.2
        )
        
        self._log(f"LLM评估完成，正在处理结果")
        
        # 从结果中提取评估结果
        try:            
            # 提取JSON格式的评估结果
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, result, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                evaluation_result = demjson3.decode(json_str)
                self._log("成功从代码块中提取JSON评估结果")
            else:
                # 尝试直接解析整个文本
                try:
                    evaluation_result = demjson3.decode(result.strip())
                    self._log("直接解析文本为JSON评估结果")
                except Exception as e:
                    self._log(f"无法解析评估结果为JSON: {str(e)}")
                    return False, {"error": f"failed to parse evaluation result: {str(e)}", "raw_result": result}
            
            # 检查标准合规结果
            matches_requirements = evaluation_result.get("matches_requirements", False) # Check boolean flag
            
            # 如果强制失败，则覆盖评估结果
            if force_failure and matches_requirements:
                self._log("由于force_failure=True，覆盖评估结果为'不通过'")
                matches_requirements = False
                evaluation_result["matches_requirements"] = False
                evaluation_result["automatic_failure_triggered"] = True
                if "failure_reasons" not in evaluation_result:
                    evaluation_result["failure_reasons"] = []
                evaluation_result["failure_reasons"].append("Forced failure mode activated")
            
            # 如果符合要求，返回简洁的成功结果
            if matches_requirements:
                self._log("评估通过，返回空结果")
                return True, {}
            
            # 如果不符合要求，执行深入分析并返回详细结果
            self._log("评估未通过，开始深入分析问题原因")
            optimization_plan = self._analyze_issues(user_query, code, evaluation_result, img_sources)
            
            return False, optimization_plan
            
        except Exception as e:
            self._log(f"从LLM结果中提取评估结果失败: {str(e)}")
            return False, {"error": f"Failed to extract evaluation result from LLM response: {str(e)}", "raw_result": result}

    def _analyze_issues(self, user_query: str, code: str, evaluation_result: Dict, img_sources) -> Dict:
        """分析问题并提供改进建议
        
        Args:
            user_query: 用户查询
            code: 可视化代码
            evaluation_result: 执行评估的结果
            img_sources: 图像URL和描述的列表
            
        Returns:
            Dict: 含有问题分析和建议的字典
        """
        self._log("开始分析问题并提供改进建议")
        
        # 构建分析提示词
        analysis_prompt_text = self._build_analysis_prompt(user_query, code, evaluation_result)
        
        # Reconstruct user_content for analysis, adding the analysis prompt text
        analysis_user_content = []
        # Add the analysis prompt text first
        analysis_user_content.append({"type": "text", "text": analysis_prompt_text})
        
        # 过滤掉无效的图像URL
        valid_img_sources = []
        for img_url, description in img_sources:
            # 检查URL是否以data:开头且包含base64内容
            if img_url.startswith("data:") and ";base64," in img_url:
                # 检查base64内容是否非空
                parts = img_url.split(";base64,")
                if len(parts) == 2 and len(parts[1]) > 100:  # 确保有足够长的base64内容
                    valid_img_sources.append((img_url, description))
                    self._log(f"分析中使用有效图像URL: {description}")
                else:
                    self._log(f"分析中跳过无效图像URL (内容太短): {description}")
            else:
                self._log(f"分析中跳过无效图像URL (格式错误): {description}")
        
        # Append valid images from img_sources
        for img_url, description in valid_img_sources:
            analysis_user_content.append({"type": "text", "text": f"\n--- IMAGE FOR ANALYSIS ---\n{description}\n(Image follows)"})
            analysis_user_content.append({"type": "image_url", "image_url": {"url": img_url}})
        
        self._log(f"分析中添加了 {len(valid_img_sources)}/{len(img_sources)} 个有效图像URL")
        self._log("生成分析提示词完成")

        user_messages = [{"role": "user", "content": analysis_user_content}]
        
        # 生成分析响应
        recommendations_text = self.generate_response(
            user_messages=user_messages, # Use reconstructed list
            # temperature=0.2
        )
        
        self._log("分析响应生成完成")
        
        # 解析改进建议
        try:
            # 解析JSON格式的改进建议
            recommendations_json_pattern = r'```json\s*(.*?)\s*```'
            recommendations_json_match = re.search(recommendations_json_pattern, recommendations_text, re.DOTALL)
            
            recommendations = {} # Default empty dict
            if recommendations_json_match:
                self._log("发现JSON格式的改进建议")
                recommendations_json = recommendations_json_match.group(1).strip()
                recommendations = demjson3.decode(recommendations_json)
            else:
                self._log("未找到JSON格式的改进建议, attempting to parse whole response")
                try:
                    recommendations = demjson3.decode(recommendations_text.strip())
                except Exception as parse_err:
                    self._log(f"Failed to parse whole response as JSON: {parse_err}")
                    # Fallback or error handling needed here - perhaps return error or empty recommendations
                    recommendations = {"recommendations": [], "error": "Failed to parse recommendations"}

        except Exception as e:
            self._log(f"解析改进建议失败: {str(e)}")
            recommendations = {"recommendations": [], "error": f"Failed to parse recommendations: {str(e)}"}

        self._log(f"问题分析和建议生成完成，建议数量: {len(recommendations.get('recommendations', []))}个")
        
        # Ensure the key exists, even if empty
        if 'recommendations' not in recommendations:
            recommendations['recommendations'] = []
        
        return recommendations

    def _build_analysis_prompt(self, user_query: str, code: str, evaluation_result: Dict) -> str:
        """Builds the prompt for issue analysis and recommendation generation.

        Args:
            user_query: The user's original request.
            code: The generated visualization code.
            evaluation_result: The result dictionary from the initial evaluation.

        Returns:
            The prompt string for the analysis LLM call.
        """

        prompt = f"""# Task: Analyze Visualization Issues and Generate Fix Recommendations

You are an expert visualization analyst. Your goal is to deeply analyze why a generated visualization failed evaluation and provide specific, actionable recommendations for fixing the code.

## Input Context

### 1. Initial Evaluation Failures
The visualization code below was evaluated and failed for the following reasons:
```json
{json.dumps(evaluation_result, indent=2, ensure_ascii=False)}
```
*   **Review Carefully**: Pay close attention to `failure_reasons`, `unmet_requirements`, and `validation_results.issues`.

### 2. Generated Visualization Code (Problematic Code)
```python
{code}
```

### 3. Original User Request
```
{user_query}
```

### 4. IMAGE CONTEXT (Provided Separately After This Text Block)
- Visualizations (Generated, Reference, Previous) relevant to this analysis will follow this text.
- **Crucially, check the text label before each image** to understand its role (e.g., "Generated Visualization", "Reference Image").
- **Visual inspection is critical**, especially for issues noted in the evaluation.

## Analysis and Recommendation Generation Process

Follow these steps rigorously:

### Step 1: Root Cause Analysis for EACH Failure Reason
- For every issue listed in `failure_reasons` and `validation_results.issues`:
    - Pinpoint the exact lines or logic in the **Generated Visualization Code** causing the issue.
    - Explain *why* it's incorrect or fails to meet requirements.
    - Consider:
        - **Blank/Empty Visualization:** Is data missing? Is filtering wrong? Is a rendering call missing? (HIGHEST PRIORITY TO FIX)
        - **Reference Inconsistency:** What specific visual elements (chart type, axes, colors, marks, layout) differ from the reference? Why?
        - **Unmet User Requirements:** Which explicit user request (use quotes) was missed or implemented incorrectly? How does the code fall short?
        - **Technical Errors:** Are there Python errors, library misuse (e.g., incorrect Altair encodings O/T/Q/N), or data processing flaws (pandas)?
        - **Visual/Design Flaws:** Are elements overlapping, illegible, or poorly designed?

### Step 2: Develop Actionable Recommendations
- For each identified root cause, formulate a precise recommendation.
- Recommendations should ideally suggest specific code modifications or alternative approaches.
- Prioritize fixes based on severity (e.g., blank charts are critical).

## Required Output Format

Generate ONLY a JSON object adhering to the following structure. Do not include explanations outside the JSON structure.

```json
{{
  "analysis_summary": "A brief (1-2 sentence) overall summary of the main problems identified.",
  "detailed_analysis": [
    {{
      "issue_description": "Clear description of a specific problem identified during evaluation (e.g., 'X-axis labels overlap', 'Chart type mismatch: expected bar, got line', 'User request for larger points not met'). Link directly to evaluation findings.",
      "root_cause_explanation": "Detailed explanation of *why* this happened in the code (e.g., 'Missing label rotation configuration in Altair axis object', 'alt.Chart(...).mark_line() was used instead of mark_bar()', 'mark_point() size parameter was not modified').",
      "code_location_hint": "Optional: Specific function call or line number range where the issue likely resides (e.g., 'alt.X() configuration', 'around line 25')."
    }}
  ],
  "recommendations": [
    {{
      "recommendation_description": "Specific, actionable step to fix one of the analyzed issues (e.g., 'Rotate x-axis labels by -45 degrees using labelAngle=-45.', 'Change mark_line() to mark_bar().', 'Add size=100 to mark_point()').",
      "priority": "critical | high | medium | low",
      "target_issue_description": "The 'issue_description' from 'detailed_analysis' that this recommendation addresses.",
      "component": "data_processing | visualization_library_config | visualization_logic | code_structure"
    }}
  ]
}}
```

**Ensure the output is a single, valid JSON object starting with `{{` and ending with `}}`.**
"""
        return prompt

    def _build_evaluation_prompt(self, user_query: str, code: str,
                                reference_path=None, reference_type=None, reference_code=None,
                                existing_code_path=None, existing_code=None, force_failure: bool = False):
        """Builds the prompt for the initial visualization evaluation.

        Args:
            user_query: User's query text.
            code: Code to be evaluated.
            reference_path: Path to reference material.
            reference_type: Type of reference ('image' or 'code').
            reference_code: Content of reference code if applicable.
            existing_code_path: Path to existing code (iteration context).
            existing_code: Content of existing code if applicable.
            force_failure: If True, instructs the LLM to guarantee a failure evaluation.

        Returns:
            The prompt string for the evaluation LLM call.
        """

        # --- Build dynamic sections ---
        force_failure_section = ""
        if force_failure:
            force_failure_section = """
## ⚠️ CRITICAL: FORCE FAILURE MODE ACTIVATED ⚠️
- **MANDATORY**: This evaluation MUST RESULT IN FAILURE (`matches_requirements: false`).
- Identify and document sufficient issues (major or minor) to justify failure.
- Focus on deviations from reference, unmet user requests, technical flaws, or poor design choices.
- Provide specific failure reasons and recommendations, even if based on subtle issues.
"""

        reference_section = "\n## 3. Reference & Context"
        ref_provided = False
        if reference_type == "image":
            reference_section += """
- **Context**: User provided a Reference Image.
- **Image Label**: 'Reference Image provided by user:' (appears after this text).
- **⚠️ HIGHEST PRIORITY**: Generated visualization MUST visually match this reference image unless the user explicitly requested a change.
"""
            ref_provided = True
        elif reference_type == "code":
            ref_code_content = reference_code if reference_code else '# Reference code could not be loaded'
            reference_section += f"""
- **Context**: User provided Reference Code.
```python
{ref_code_content}
```
- **Image Label**: 'Visualization generated from the Reference Code:' (may appear after this text).
- **⚠️ HIGHEST PRIORITY**: Generated visualization MUST visually match the visualization produced by the reference code unless the user explicitly requested a change.
"""
            ref_provided = True
        elif existing_code_path:
            exist_code_content = existing_code if existing_code else '# Previous code could not be loaded'
            reference_section += f"""
- **Context**: This is an iteration; previous code exists.
```python
{exist_code_content}
```
- **Image Label**: 'Visualization generated from the Previous/Existing Code:' (may appear after this text).
- **⚠️ HIGHEST PRIORITY**: Generated visualization MUST visually match the visualization from the previous code unless the user explicitly requested a change.
"""
            ref_provided = True
        else:
            reference_section += """
- **Context**: No reference or previous code provided. Evaluate solely against the user request and general quality standards.
"""

        if ref_provided:
             reference_section += """
- **Reference Matching Rule**: Chart type, axes, colors, marks, titles, legends, and overall layout MUST match the reference unless an **explicit user request** justifies the difference.
"""

        # --- Combine into the final prompt ---
        prompt = f"""# Task: Evaluate Visualization Code

## 1. Visualization Code To Be Evaluated
```python
{code}
```

## 2. IMAGE CONTEXT (Provided Separately After This Text Block)
- Visualizations (Generated, Reference, Previous) relevant to this evaluation will follow this text.
- **Crucially, check the text label before each image** to understand its role (e.g., 'Generated Visualization', 'Reference Image').
- **Carefully examine all provided images before proceeding.**
{force_failure_section}
{reference_section}

## 4. User Request
```
{user_query}
```
- **Analyze Carefully**: Identify all **explicit** instructions, constraints, and desired changes.
- **Use Quotes**: When referencing user requirements in your analysis, use direct quotes.

# Evaluation Criteria & Methodology
Evaluate the 'Code To Be Evaluated' based *only* on the provided context (Reference, User Request, Images).

## A. Core Requirements & Automatic Failure Conditions:
  1. **Reference Consistency (if reference provided)**: Any deviation from the reference *not explicitly requested* by the user. -> FAILURE
  2. **Explicit User Requirements**: ALL explicitly stated user requests MUST be met precisely. Use direct quotes from the user request as evidence. -> FAILURE if any unmet.
  3. **Technical Execution**: Code must run without errors and use appropriate libraries (pandas for data, expected viz library like Altair). -> FAILURE if errors or wrong libraries.
  4. **Non-Blank Output**: The generated visualization MUST NOT be blank or empty (must show data marks, axes, etc.). -> CRITICAL FAILURE
  5. **Completeness**: Essential plot elements (axes, labels, data marks appropriate to chart type) must be present. -> FAILURE if missing.
  # 6. **Visual Quality**: Absence of major visual defects (e.g., widespread overlapping elements, illegible text). -> FAILURE if major defects.

## B. Evaluation Process:
  - **Step 1: Analyze Reference**: If provided, deeply understand the reference visualization's type, elements, and data representation.
  - **Step 2: Analyze User Request**: Extract a checklist of *explicit* requirements using quotes.
  - **Step 3: Analyze Generated Code & Visualization**: Check code quality, library usage, and visually inspect the generated image. **Verify it's not blank.**
  - **Step 4: Compare & Verify**: Systematically compare the generated viz/code against the reference (if any) and the explicit user requirements checklist.
  - **Step 5: Apply Failure Conditions**: Check if any automatic failure conditions are met.
  - **Step 6: Determine Outcome**: Decide `matches_requirements` (true/false). If `force_failure` is active, this MUST be false.

# Required Output Format
Generate ONLY a JSON object adhering to the following structure. Do not include explanations outside the JSON structure.
```json
{{
  "evaluation_summary": "Brief textual summary (1-2 sentences) of the overall evaluation outcome and key findings.",
  "matches_requirements": true | false,
  "automatic_failure_triggered": true | false,
  "failure_reasons": [
    "Specific reason for failure 1 (e.g., 'Reference consistency failed: Chart type mismatch')",
    "Specific reason for failure 2 (e.g., 'Unmet user requirement: X-axis labels not rotated as requested')"
  ],
  "validation_checks": {{
    "reference_consistency_met": true | false | "not_applicable",
    "all_explicit_user_requirements_met": true | false,
    "used_expected_libraries": true | false,
    "is_visualization_blank": true | false,
    "has_essential_elements": true | false
  }},
  "explicit_requirements_analysis": [
    {{
      "requirement_quote": "Direct quote of an explicit user requirement.",
      "is_met": true | false,
      "evidence": "Brief explanation or evidence from code/visualization supporting the met/unmet status."
    }}
  ],
  "recommendations_for_improvement": [
    {{
      "description": "Brief description of a suggested improvement if evaluation failed (focus on *what* needs fixing).",
      "priority": "high | medium | low",
      "component": "reference_matching | user_requirement | technical_issue | visual_quality"
    }}
  ],
  "quality_scores": {{
    "visual_clarity": "1-10 (Clarity of data presentation)",
    "design_aesthetics": "1-10 (Visual appeal)",
    "code_quality_impression": "1-10 (Apparent code structure/readability)"
  }}
}}
```
**Ensure the output is a single, valid JSON object starting with `{{` and ending with `}}`.**
"""

        self._log("Evaluation prompt constructed.")
        return prompt


if __name__ == "__main__":
    # 测试验证评估智能体
    import sys
    
    # 创建日志目录
    os.makedirs("./logs", exist_ok=True)
    
    # 初始化验证评估智能体
    validation_agent = ValidationEvaluationAgent(model_type="gemini-2.0-flash@gemini-2.0-flash", agent_id=108, use_log=True)
    
    validation_agent._log("\n===== 测试 ValidationEvaluationAgent =====")
    
    # 测试代码
    test_code = """import sqlite3
import pandas as pd
import altair as alt

conn = sqlite3.connect('database/activity_1.sqlite')

query = '''
SELECT 
    A.activity_name,
    AVG(S.Age) AS Avg_Age
FROM 
    Activity AS A
JOIN 
    Participates_in AS P ON A.actid = P.actid
JOIN 
    Student AS S ON P.stuid = S.StuID
GROUP BY 
    A.actid, A.activity_name
'''

df = pd.read_sql_query(query, conn)

conn.close()

overall_avg_age = df['Avg_Age'].mean()

chart = (
    alt.Chart(df)
    .mark_point()
    .transform_calculate(
        Age_Delta="datum.Avg_Age - " + str(overall_avg_age)
    )
    .encode(
        x=alt.X("activity_name:N").title("Activity Name"),
        y=alt.Y("Age_Delta:Q").title("Age Delta (Years)"),
        color=alt.Color("Age_Delta:Q")
        .title("Age Delta")
        .scale(domainMid=0, scheme="redblue"),
    )
    .properties(title="Difference in Average Age by Activity")
)

chart
"""
    
    # 测试查询
    user_query = "The chart is great for showing the age differences, but it's a little hard to read with all the activity names crammed together at the bottom. Could you rotate the x-axis labels to make them easier to read? Also, I think it would be clearer if we added thin grid lines for the y-axis. That would help me quickly see the exact age difference for each activity without having to guess. Finally, could you make the points a bit larger and hollow, but still fill them with the same colors we're using now? That might make the visualization stand out better."
    # reference_path = "./vis_bench/code/matplotlib/Advanced Calculations___calculate_residuals.py"
    existing_code_path = "./vis_bench/vis_modify/Advanced Calculations___calculate_residuals___activity_1.py"

    status, result = validation_agent.evaluate_visualization(user_query, test_code, existing_code_path=existing_code_path, force_failure=True)

    validation_agent._log(f"评估结果: {status}")
    validation_agent._log(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")