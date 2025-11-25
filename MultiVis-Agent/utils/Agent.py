# Standard library imports
import json
import demjson3
import os
from typing import Tuple, Callable, Dict, Any, List

# Third-party imports
import urllib3
import openai
import httpx
import time

# Local imports
from .ToolManager import ToolManager
from .Config import Config

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Agent:
    """LLM处理器
    
    负责处理与语言模型的交互，包括提示词的处理和响应的解析
    """
    
    def __init__(self, model_type: str = "qwen-max-2025-01-25@qwen-vl-max-2025-01-25", system_prompt: str = "", agent_name: str = "llm_processor", agent_id: str = 0, use_log: bool = False):
        """初始化LLM处理器
        
        Args:
            model_type: 使用的模型种类，格式为text_model@img_model，默认为qwen-max-2025-01-25@qwen-vl-max-2025-01-25
            system_prompt: 系统提示词，默认为空
            agent_name: 智能体名称，默认为"llm_processor"
            agent_id: 智能体ID，默认为None
        """
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.model_type = None
        self.client = None
        self.text_client = None
        self.img_client = None
        self.img_model = None
        self.text_model = None
        self.model_choice = None
        self.log_folder = f"./logs/{agent_name}/{agent_id}.log"
        self.history = []
        self.tool_manager = ToolManager()  # 初始化空的工具管理器
        self.update_history = False
        self.system_prompt = ""
        self.config = Config()
        self.use_log = use_log
        self.last_error_msg = None  # 新增：记录最后一次错误信息

        # 初始化配置
        self.set_model(model_type)
        self.set_system_prompt(system_prompt)

        # 初始化日志目录
        os.makedirs(os.path.dirname(self.log_folder), exist_ok=True)


    
    #--------------------------------------------------------------------------
    # Configuration Methods
    #--------------------------------------------------------------------------
    
    def set_model(self, model_type: str = "qwen-max-2025-01-25@qwen-vl-max-2025-01-25"):
        """设置使用的模型类型
        
        Args:
            model_type: 模型类型，格式为text_model@img_model，默认为qwen-max-2025-01-25@qwen-vl-max-2025-01-25
            
        Raises:
            ValueError: 当指定了不支持的模型类型时抛出
        """
        text_model, img_model = model_type.split("@")

        self.text_client = self.get_model_client(text_model)
        self.img_client = self.get_model_client(img_model)
        self.text_model = text_model
        self.img_model = img_model
        
        self._log(f"初始化模型: {model_type}")
    
    def get_model_client(self, model_name: str = "qwen-max-2025-01-25") -> openai.Client:
        for model_type, config in self.config.MODEL_CONFIGS.items():
            if model_type.lower() in model_name.lower():
                client = openai.Client(
                    api_key=config["api_key"],
                    base_url=config["base_url"],
                    http_client=httpx.Client(verify=False)  # 禁用SSL验证
                )
                return client
        raise ValueError(f"Unsupported model: {model_name}")

    def set_system_prompt(self, system_prompt: str):
        """设置系统提示词
        
        Args:
            system_prompt: 系统提示词
        """
        self.system_prompt = system_prompt
        
        if self.history:
            self.history[0] = {"role": "system", "content": system_prompt}
        else:
            self.history = [{"role": "system", "content": system_prompt}]
            
        # self._log(f"设置系统提示: {system_prompt}")    

    def chat_status(self, status: bool):
        """设置是否更新对话历史
        
        Args:
            status: 是否更新对话历史
        """
        self.update_history = status
        self._log(f"设置对话历史更新状态: {status}")

    #--------------------------------------------------------------------------
    # Tool Management Methods
    #--------------------------------------------------------------------------
    
    def register_tool(self, tool_name: str, tool_func: Callable, tool_description: str, tool_parameters: dict, required: list[str] = []):
        """注册工具
        
        Args:
            tool_name: 工具名称
            tool_func: 工具函数
            tool_description: 工具描述
            tool_parameters: 工具参数
            required: 工具参数是否必填，默认为全部参数
        """
        if required == []:
            required = [k for k, v in tool_parameters.items()]

        self.tool_manager.register_tool(tool_name, tool_func, tool_description, tool_parameters, required)
        self._log(f"注册工具: {tool_name}")

    #--------------------------------------------------------------------------
    # Core Chat Methods
    #--------------------------------------------------------------------------
    
    def _prepare_messages(self, prompt: str, user_messages: list = None, img_urls: List[str] = None, use_history: bool = True) -> List[Dict[str, Any]]:
        """准备发送给模型的消息
        
        Args:
            prompt: 用户输入的提示词
            user_messages: 用户消息列表
            img_urls: 图片URL列表
            use_history: 是否使用对话历史
            
        Returns:
            List[Dict[str, Any]]: 准备好的消息列表
        """
        if user_messages and prompt:
            raise ValueError("user_messages和prompt不能同时存在")
        
        if user_messages:
            if use_history:
                messages = self.history + user_messages
            else:
                messages = [{"role": "system", "content": self.system_prompt}] + user_messages
        else:
            if img_urls:
                # 构建多模态内容
                user_content = [{"type": "text", "text": prompt}]
                for img_url in img_urls or []:
                    user_content.append({"type": "image_url", "image_url": {"url": img_url}})
                    
                if use_history:
                    messages = self.history + [{"role": "user", "content": user_content}]
                else:
                    messages = [{"role": "system", "content": self.system_prompt}, 
                                {"role": "user", "content": user_content}]
            else:
                # 纯文本内容
                if use_history:
                    messages = self.history + [{"role": "user", "content": prompt}]
                else:
                    messages = [{"role": "system", "content": self.system_prompt}, 
                                {"role": "user", "content": prompt}]
                
        return messages
    
    def _parse_tool_calls_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中解析工具调用
        
        解析工具调用，支持格式:
        1. <Action>...</Action>
        
        Args:
            text: 包含工具调用的文本
            
        Returns:
            List[Dict[str, Any]]: 解析出的工具调用列表
        """
        tool_calls = []
        
        self._log(f"\n[解析工具调用] 开始解析文本中的工具调用")
        
        # 确保输入文本不为None
        if text is None:
            error_msg = "输入文本为None"
            self._log(f"[解析工具调用] {error_msg}，返回空工具调用列表")
            # 添加错误信息到返回结果
            tool_calls.append({
                "id": "call_error",
                "function": {
                    "name": "parse_error",
                    "arguments": json.dumps({"error": error_msg})
                }
            })
            return tool_calls
        
        # 解析 <Action> 标签
        if "<Action>" in text and "</Action>" in text:
            try:
                start_tag = "<Action>"
                end_tag = "</Action>"
                
                start_pos = text.find(start_tag) + len(start_tag)
                end_pos = text.find(end_tag)
                
                if end_pos > start_pos:
                    content = text[start_pos:end_pos].strip()
                    content = content.replace("```json", "").replace("```", "").strip()
                    
                    # 解析每一行可能的工具调用
                    for line in content.strip().split('\n'):
                        line = line.strip()
                        if line and line.startswith("{") and line.endswith("}"):
                            try:
                                tool_call_result = self._parse_single_tool_call(line)
                                if tool_call_result:
                                    tool_calls.append(tool_call_result)
                            except json.JSONDecodeError as e:
                                error_msg = f"JSON解析错误: {str(e)}, 行内容: {line}"
                                self._log(f"[错误] {error_msg}")
                                # 添加错误信息到返回结果
                                tool_calls.append({
                                    "id": f"call_error_{len(tool_calls)}",
                                    "function": {
                                        "name": "json_parse_error",
                                        "arguments": json.dumps({
                                            "error": str(e),
                                            "original_input": line
                                        })
                                    }
                                })
                    # 如果没有解析到工具调用但确实有<Action>标签，则尝试将content整个进行解析
                    if not tool_calls:
                        try:
                            tool_call_result = self._parse_single_tool_call(content)
                            if tool_call_result:
                                tool_calls.append(tool_call_result)
                        except Exception as e:
                            error_msg = f"整体解析Action内容失败: {str(e)}"
                            self._log(f"[错误] {error_msg}")
                            # 添加工具解析错误的详细信息
                            tool_calls.append({
                                "id": "call_error_parse",
                                "function": {
                                    "name": "json_parse_error",
                                    "arguments": json.dumps({
                                        "error": str(e),
                                        "original_content": content[:100] + "..." if len(content) > 100 else content
                                    })
                                }
                            })

            except Exception as e:
                error_msg = f"Action标签工具调用解析错误: {str(e)}"
                self._log(f"[错误] {error_msg}")
                # 添加通用错误信息到返回结果
                tool_calls.append({
                    "id": "call_error_general",
                    "function": {
                        "name": "parse_error",
                        "arguments": json.dumps({
                            "error": error_msg,
                            "original_text": text[:100] + "..." if len(text) > 100 else text
                        })
                    }
                })
        elif "<Action>" in text:
            error_msg = "发现起始标签<Action>但缺少结束标签</Action>"
            self._log(f"[解析工具调用] 警告: {error_msg}")
            # 添加错误信息到返回结果
            tool_calls.append({
                "id": "call_error_tags",
                "function": {
                    "name": "incomplete_action_tags",
                    "arguments": json.dumps({
                        "error": error_msg,
                        "original_text": text[:100] + "..." if len(text) > 100 else text
                    })
                }
            })
        
        # 强制至少返回一个解析信息，即使是错误
        if not tool_calls and "<Action>" in text:
            # 使用最近保存的错误信息，如果有的话
            if self.last_error_msg:
                error_msg = self.last_error_msg
            else:
                error_msg = "工具调用解析失败，但未能捕获具体错误"
                
            self._log(f"[解析工具调用] {error_msg}")
            tool_calls.append({
                "id": "call_error_unknown",
                "function": {
                    "name": "parse_error",
                    "arguments": json.dumps({
                        "error": error_msg,
                        "original_text": text[:100] + "..." if len(text) > 100 else text
                    })
                }
            })
        
        self._log(f"[解析工具调用] 从文本中解析出 {len(tool_calls)} 个工具调用")
        return tool_calls
    
    def _parse_single_tool_call(self, tool_call_text: str) -> Dict[str, Any]:
        """解析单个工具调用
        
        Args:
            tool_call_text: 包含单个工具调用的文本
            
        Returns:
            Dict[str, Any]: 解析出的工具调用，如果解析失败则返回带有错误信息的工具调用
        """
        try:
            tool_call_text = tool_call_text.replace("```json", "").replace("```", "").strip()
            tool_call = demjson3.decode(tool_call_text)
            if isinstance(tool_call, dict):
                if "tool_name" in tool_call and "parameters" in tool_call:
                    # 验证工具调用格式
                    if not isinstance(tool_call["parameters"], dict):
                        error_msg = f"Tool parameters are not a dictionary type: {tool_call['parameters']}"
                        # 返回错误信息
                        return {
                            "id": f"call_error",
                            "function": {
                                "name": tool_call["tool_name"] + "_error",
                                "arguments": json.dumps({
                                    "error": error_msg,
                                    "original_input": tool_call_text
                                })
                            }
                        }
                        
                    # 构建一个标准格式的工具调用对象
                    validated_tool_call = {
                        "id": f"call",
                        "function": {
                            "name": tool_call["tool_name"],
                            "arguments": json.dumps(tool_call["parameters"])
                        }
                    }
                    
                    return validated_tool_call
                else:
                    error_msg = f"Missing tool_name or parameters: {tool_call}"
                    self._log(f"[解析工具调用] 跳过无效工具调用: {error_msg}")
                    # 返回错误信息
                    return {
                        "id": f"call_error",
                        "function": {
                            "name": "invalid_tool_call",
                            "arguments": json.dumps({
                                "error": error_msg,
                                "original_input": tool_call_text
                            })
                        }
                    }
            else:
                error_msg = f"Non-dictionary tool call: {tool_call}"
                self._log(f"[解析工具调用] 跳过非字典工具调用: {error_msg}")
                # 返回错误信息
                return {
                    "id": f"call_error",
                    "function": {
                        "name": "invalid_tool_format",
                        "arguments": json.dumps({
                            "error": error_msg,
                            "original_input": tool_call_text
                        })
                    }
                }
        except Exception as e:
            error_msg = f"Tool call parsing error: {str(e)}"
            self._log(f"[解析工具调用] {error_msg}")
            self.last_error_msg = error_msg  # 记录最后一次错误信息
            # 修改：返回包含错误信息的工具调用对象，而不是返回None
            return {
                "id": f"call_error_exception",
                "function": {
                    "name": "parse_error",
                    "arguments": json.dumps({
                        "error": error_msg,
                        "original_input": tool_call_text[:100] + "..." if len(tool_call_text) > 100 else tool_call_text
                    })
                }
            }
    
    def _update_conversation_history(self, prompt: str, response: str, img_urls: List[str] = None):
        """更新对话历史
        
        Args:
            prompt: 用户输入
            response: 模型响应
            img_urls: 图片URL列表
        """
        if not self.update_history:
            return
            
        if img_urls:
            user_content = [{"type": "text", "text": prompt}]
            for img_url in img_urls:
                user_content.append({"type": "image_url", "image_url": {"url": img_url}})
            
            self.history.extend([
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": response}
            ])
        else:
            self.history.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ])
            
        self._log("更新对话历史")

    def call_llm(self, messages: List[Dict[str, Any]], client: openai.Client, model: str, **kwargs):
        """调用LLM
        
        Args:
            messages: 消息列表
            **kwargs: 传递给模型的其他参数
        """
        response = None
        while not response:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
            except Exception as e:
                self._log(f"调用LLM失败: {str(e)}")
                print(f"调用LLM失败: {str(e)}")
                time.sleep(1)
        return response
    
    def chat(self, prompt: str, user_messages: list = None, img_urls: List[str] = None, use_history: bool = True, **kwargs) -> str:
        """
        与模型进行对话，不使用工具
        
        Args:
            prompt: 用户输入的提示词
            user_messages: 用户消息列表
            img_urls: 图片URL列表，如果提供则进行多模态对话
            reasoning: 是否使用推理模式
            use_history: 是否使用对话历史
            **kwargs: 传递给模型的其他参数
            
        Returns:
            str: 模型回复
        """

        if user_messages and prompt:
            raise ValueError("user_messages和prompt不能同时存在")

        try:
            self._log(f"\n=== 新对话开始 ===")
            if prompt:
                self._log(f"用户输入: {prompt}")
            if user_messages:
                self._log("用户输入：\n")
                for message in user_messages:
                    if message['role'] == 'user':
                        user_content = message['content']
                        if isinstance(user_content, str):
                            self._log(f"{user_content}")
                        elif isinstance(user_content, list):
                            for item in user_content:
                                if item['type'] == 'text':
                                    self._log(f"{item['text']}")
                    elif message['role'] == 'assistant':
                        self._log(f"模型回复: \n{message['content']}")
            # 准备消息
            messages = self._prepare_messages(prompt, user_messages, img_urls, use_history)
            
            # 选择模型
            selected_client = self.img_client if img_urls else self.text_client
            selected_model = self.img_model if img_urls else self.text_model
            self._log(f"使用模型: {selected_model}")

            # 开始与模型的对话循环
            while True:
                self._log(f"发送消息到模型...")
                # response = selected_client.chat.completions.create(
                #     model=selected_model,
                #     messages=messages,
                #     **kwargs
                # )
                response = self.call_llm(messages, selected_client, selected_model, **kwargs)
            
                assistant_message = response.choices[0].message
                self._log(f"模型回复: {assistant_message.content}")

                self._log("无需使用工具")
                content = assistant_message.content or ""
                    
                # 更新对话历史
                self._update_conversation_history(prompt, content, img_urls)
                self._log("=== 对话结束 ===\n")
                return content
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._log(f"发生错误: {error_msg}")
            self._log("=== 对话异常结束 ===\n")
            return error_msg

    def generate_response(self, prompt: str = None, user_messages: list = None, img_urls: list = None, **kwargs) -> str:
        """与模型进行单轮对话，不使用工具
        
        Args:
            prompt: 用户输入的提示词
            user_messages: 用户消息列表
            img_url: 图片URL，如果提供则进行多模态对话
            reasoning: 是否使用推理模式
            **kwargs: 传递给模型的其他参数
            
        Returns:
            str: 模型回复
        """

        if user_messages and prompt:
            raise ValueError("user_messages和prompt不能同时存在")
        elif not user_messages and not prompt:
            raise ValueError("user_messages和prompt不能同时为空")
        
        # 禁用历史更新以确保单轮对话
        original_update_status = self.update_history
        self.update_history = False
        
        try:
            result = self.chat(
                prompt=prompt,
                user_messages=user_messages,
                img_urls=img_urls,
                use_history=False,
                **kwargs
            )
            return result
        finally:
            # 恢复原始历史更新状态
            self.update_history = original_update_status

    def chat_ReAct(self, question: str = None, img_urls: List[str] = None, user_messages: List[Dict[str, Any]] = None, **kwargs) -> Tuple[str, bool]:
        """
        让Agent采用ReAct模式进行对话，支持并行工具调用
        
        Args:
            question: 用户输入的问题
            img_urls: 图片URL列表
            reasoning: 是否使用推理模式
            use_history: 是否使用对话历史
            **kwargs: 传递给模型的其他参数
            
        Returns:
            Tuple[str, bool]: (模型回复, 是否使用了工具)
        """
        if not question and not user_messages:
            raise ValueError("问题或消息不能同时为空")
        if user_messages and img_urls:
            raise ValueError("当提供user_messages时，img_urls必须为空")

        try:
            # 记录会话开始信息
            self._log("\n" + "="*80)
            self._log("REACT模式对话会话开始")
            self._log("="*80)
            
            # 记录基本参数信息
            self._log("\n[会话参数]")
            self._log(f"问题: {question}")
            self._log(f"额外参数: {kwargs}")
            
            # 获取工具信息
            tools = self.tool_manager.get_tools()
            tool_functions = self.tool_manager.get_tool_functions()
            
            # 记录可用工具信息
            self._log("\n[可用工具]")
            available_tools = list(tool_functions.keys())
            tool_names_str = ", ".join(available_tools) if available_tools else "无可用工具"
            self._log(f"工具列表: {tool_names_str}")
            self._log(f"工具数量: {len(available_tools)}")
                
            # 构建ReAct系统提示词
            react_system_prompt = self._build_react_system_prompt()
            self._log("\n[ReAct System Prompt]")
            self._log(react_system_prompt)
            
            # 确定使用的模型
            selected_client = self.img_client if img_urls else self.text_client
            selected_model = self.img_model if img_urls else self.text_model

            if not user_messages:
                # 初始问题
                prompt = f"""<Question>
{question}
</Question>
"""

                # 构建消息 - 只有系统提示和用户初始问题
                if img_urls:
                    messages = [
                        {"role": "system", "content": react_system_prompt},
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                    for img_url in img_urls:
                        messages[1]["content"].append({"type": "image_url", "image_url": {"url": img_url}})
                else:
                    messages = [
                        {"role": "system", "content": react_system_prompt},
                        {"role": "user", "content": prompt}
                    ]
            else:
                messages = [{"role": "system", "content": react_system_prompt}] + user_messages
                for message in user_messages:
                    if isinstance(message['content'], str):
                        if message['role'] == 'user':
                            self._log(f"[发送到模型的消息]:\n{message['content']}\n")
                        else:
                            self._log(f"[模型响应]:\n{message['content']}\n")
                    if isinstance(message['content'], list):
                        if message['role'] == 'user':
                            for item in message['content']:
                                if item['type'] == 'image_url':
                                    selected_client = self.img_client
                                    selected_model = self.img_model
                                else:
                                    self._log(f"[发送到模型的消息]:\n{item['text']}\n")
                        else:
                            self._log(f"[模型响应]:\n{message['content']}\n")
                                

            
            self._log("\n[模型配置]")
            self._log(f"使用模型: {selected_model}")
            
            # ReAct对话迭代
            max_iterations = kwargs.pop("max_iterations", 8)
            final_answer, used_tool = self._run_react_iterations(
                messages=messages,
                client=selected_client,
                model=selected_model,
                tools=tools,
                tool_functions=tool_functions,
                max_iterations=max_iterations,
                **kwargs
            )
            
            # 更新对话历史
            if self.update_history:
                self._update_conversation_history(question, final_answer, img_urls)
            
            return final_answer, used_tool
            
        except Exception as e:
            error_msg = f"Error in ReAct chat: {str(e)}"
            self._log(f"\n[会话异常结束] {error_msg}")
            self._log("="*80 + "\n")
            return error_msg, False
    
    def _format_conversation_history(self) -> str:
        """将对话历史格式化为文本
        
        Returns:
            str: 格式化后的对话历史
        """
        conversation = ""
        for message in self.history:
            if message['role'] == "system":
                continue
                
            if isinstance(message['content'], str):
                conversation += f"{message['role'].upper()}: {message['content']}\n"
            elif isinstance(message["content"], list):
                conversation += f"{message['role'].upper()}: "
                for content in message['content']:
                    if content['type'] == "text":
                        conversation += f"{content['text']} "
                    elif content['type'] == "image_url":
                        conversation += f"[IMG_URL] "
                conversation += "\n"
                
        return conversation
    
    def _build_react_system_prompt(self) -> str:
        """构建ReAct模式的系统提示词
        
        Returns:
            str: ReAct系统提示词
        """
        return f"""{self.system_prompt}

<available_tools>
{self.tool_manager.get_tools_prompt()}
</available_tools>

<format_instructions>
You must follow the ReAct (Reasoning + Acting) format strictly:

1. <Question>
   The initial user question or request that needs to be addressed.
   </Question>

2. <Thought>
   Analyze the question thoroughly and plan your approach step by step.
   Consider what information you need and which tools might help.
   </Thought>

3. <Action>
   Call tools with VALID JSON format on a single line:
   {{"tool_name": "exact_tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}
   </Action>

4. <Observation>
   The result returned by the tool after execution.
   This will be provided to you automatically after each Action.
   Format: {{"tool_name": "called_tool_name", "result": "tool_result_data"}}
   </Observation>

5. <Final_Answer>
   Provide a clear, concise answer to the original question using information gathered.
   </Final_Answer>

IMPORTANT:
- Each response must contain EXACTLY ONE block type (Thought, Action, or Final_Answer)
- Never mix multiple block types in one response
- Action blocks must contain valid, parseable JSON with no line breaks in the JSON object
- Use Final_Answer ONLY when you have all needed information
- You will RECEIVE Question and Observation blocks but should not GENERATE them
</format_instructions>

<tool_usage_rules>
- Each tool call must be on its own line within an Action block
- Tool calls must use valid JSON format: {{"tool_name": "name", "parameters": {{"param1": "value1"}}}}
- Never guess or simulate tool outputs
- Tools can be called multiple times if needed
- Wait for actual observations before proceeding
</tool_usage_rules>

<error_handling>
If a tool call fails:
1. Analyze why it might have failed
2. Try reformulating your request or use a different approach
3. If all attempts fail, provide your best answer with the information available
</error_handling>
"""
    
    def _run_react_iterations(self, messages: List[Dict[str, Any]], client: openai.Client, model: str, tools: List[Dict[str, Any]], 
                              tool_functions: Dict[str, Callable], max_iterations: int = 8, **kwargs) -> Tuple[str, bool]:
        """运行ReAct模式的迭代对话
        
        Args:
            messages: 消息列表
            model: 使用的模型
            tools: 工具列表
            tool_functions: 工具函数字典
            max_iterations: 最大迭代次数
            **kwargs: 其他参数
            
        Returns:
            Tuple[str, bool]: (最终答案, 是否使用了工具)
        """
        final_answer = None
        used_tool = False
        current_iteration = 0
        last_valid_response = None
        
        # 存储完整的ReAct过程记录
        react_trace = [messages[1]["content"] if isinstance(messages[1]["content"], str) 
                      else messages[1]["content"][0]["text"]]
        
        while final_answer is None and current_iteration < max_iterations:
            current_iteration += 1
            self._log(f"\n[ReAct迭代 {current_iteration}/{max_iterations}]")
            
            try:
                # 记录发送给模型的消息
                self._log("\n[发送到模型的消息]")
                if isinstance(messages[-1]['content'], str):
                    self._log(f"{messages[-1]['content']}")
                elif isinstance(messages[-1]['content'], list):
                    for item in messages[-1]['content']:
                        if item['type'] == 'text':
                            self._log(f"{item['text']}")
                
                # 提取共用参数
                # temperature = kwargs.pop("temperature", 0.2)
                
                # response = client.chat.completions.create(
                #     model=model,
                #     messages=messages,
                #     temperature=temperature,
                #     **kwargs
                # )
                response = self.call_llm(messages, client, model, **kwargs)
            
                assistant_message = response.choices[0].message
                assistant_content = assistant_message.content or ""
                self._log("\n[模型响应]")
                self._log(assistant_content or '[无文本内容]')
                
                # 将模型回复添加到对话记录中
                if "<Action>" in assistant_content and "</Action>" in assistant_content:
                    assistant_content = assistant_content.split("</Action>")[0].strip() + "\n</Action>"

                react_trace.append(assistant_content)
                
                if "<Final_Answer>" in assistant_content and "</Final_Answer>" not in assistant_content:
                    assistant_content += "\n</Final_Answer>"

                # 检查是否含有Final_Answer标签
                if assistant_content and "<Final_Answer>" in assistant_content and "</Final_Answer>" in assistant_content:
                    start_tag = "<Final_Answer>"
                    end_tag = "</Final_Answer>"
                    start_pos = assistant_content.find(start_tag) + len(start_tag)
                    end_pos = assistant_content.find(end_tag)
                    if end_pos > start_pos:
                        final_answer = assistant_content[start_pos:end_pos].strip()
                        self._log("\n[检测到Final_Answer标签]")
                        self._log(final_answer)
                        break

                # 解析工具调用
                if "<Action>" in assistant_content and "</Action>" not in assistant_content:
                    assistant_content += "\n</Action>"
                if "</Action>" in assistant_content and "\n</Action>" not in assistant_content:
                    assistant_content = assistant_content.replace("</Action>", "\n</Action>")
                tool_calls = self._parse_tool_calls_from_text(assistant_content)
                
                # 如果有工具调用，则处理它们
                if tool_calls:
                    self._log("\n[检测到工具调用]")
                    self._log(f"工具调用数量: {len(tool_calls)}")
                    used_tool = True
                    
                    # 将清理后的内容添加到对话中
                    messages.append({"role": "assistant", "content": assistant_content})
                    
                    # 处理每个工具调用
                    tool_results = []
                    error_messages = []
                    
                    for i, tool_call in enumerate(tool_calls):
                        # 检查是否是错误解析的工具调用
                        if "function" in tool_call and tool_call["function"]["name"] in ["parse_error", "json_parse_error", "incomplete_action_tags"]:
                            try:
                                error_info = json.loads(tool_call["function"]["arguments"])
                                error_detail = f"Error: {error_info.get('error', 'Unknown error')}"
                                self._log(f"\n[工具调用解析错误] {error_detail}")
                                error_messages.append(error_detail)
                                continue
                            except Exception as e:
                                self._log(f"\n[错误信息解析失败] {str(e)}")
                                error_messages.append(f"Error occurred while parsing your tool call")
                                continue
                        
                        # 添加检查确保tool_call和tool_call["function"]都不是None
                        if not tool_call or "function" not in tool_call or not tool_call["function"]:
                            error_msg = f"Error: Invalid tool call format at index {i}"
                            self._log(f"\n[错误] {error_msg}")
                            tool_results.append(f"error: {error_msg}")
                            continue
                            
                        # 检查必要的键是否存在
                        if "name" not in tool_call["function"] or "arguments" not in tool_call["function"]:
                            error_msg = f"Error: Missing required fields in tool call at index {i}"
                            self._log(f"\n[错误] {error_msg}")
                            tool_results.append(f"error: {error_msg}")
                            continue
                        
                        function_name = tool_call["function"]["name"]
                        
                        try:
                            function_args = demjson3.decode(tool_call["function"]["arguments"])
                        except json.JSONDecodeError as e:
                            error_msg = f"Error parsing arguments for tool '{function_name}': {str(e)}"
                            self._log(f"\n[错误] {error_msg}")
                            tool_results.append(f"{function_name}: {error_msg}")
                            continue
                            
                        self._log(f"\n[工具调用 {i+1}/{len(tool_calls)}]")
                        self._log(f"工具名称: {function_name}")
                        self._log(f"工具参数: {function_args}")
                        
                        # 检查工具是否存在
                        if function_name not in tool_functions:
                            error_msg = f"Error: Tool '{function_name}' not found"
                            self._log(f"\n[错误] {error_msg}")
                            tool_results.append(f"{function_name}: {error_msg}")
                            continue
                        
                        # 实际执行工具调用
                        # self._log(f"\n[开始执行工具调用] {function_name}")
                        try:
                            tool_func = tool_functions[function_name]
                            tool_response = tool_func(**function_args)
                            result = f"{function_name}: {tool_response}"
                            tool_results.append(result)
                            # self._log(f"\n[工具返回结果] {tool_response}")
                        except Exception as e:
                            error_msg = f"Error executing tool {function_name}: {str(e)}"
                            
                            # 检查是否是参数错误，如果是，添加参数提示
                            if "got an unexpected keyword argument" in str(e):
                                # 获取该工具的正确参数列表
                                tool_info = None
                                for tool in tools:
                                    if tool.get("name") == function_name:
                                        tool_info = tool
                                        break
                                
                                if tool_info and "parameters" in tool_info:
                                    # 从工具定义中获取正确的参数列表
                                    correct_params = []
                                    if "properties" in tool_info["parameters"]:
                                        correct_params = list(tool_info["parameters"]["properties"].keys())
                                    
                                    # 获取错误的参数名称
                                    import re
                                    wrong_param = re.search(r"'([^']*)'", str(e))
                                    wrong_param = wrong_param.group(1) if wrong_param else "unknown"
                                    
                                    # 获取当前提供的参数
                                    provided_params = list(function_args.keys())
                                    
                                    # 构建参数提示
                                    param_hint = f"\nParameter Error: '{wrong_param}' is not a valid parameter\n"
                                    param_hint += f"Tool '{function_name}' accepts these parameters: {', '.join(correct_params)}\n"
                                    param_hint += f"You provided these parameters: {', '.join(provided_params)}"
                                    
                                    error_msg += param_hint
                            
                            tool_results.append(f"{function_name}: {error_msg}")
                            self._log(f"\n[工具执行错误] {error_msg}")
                    
                    # 记录并行工具调用的综合结果
                    self._log("\n[并行工具调用完成]")
                    self._log("工具调用结果:")
                    for result in tool_results:
                        self._log(f"- {result}")
                    
                    # 增加新格式的工具调用结果
                    observation_json = []
                    for i, result in enumerate(tool_results):
                        parts = result.split(': ', 1)
                        if len(parts) == 2:
                            tool_name = parts[0]
                            result_value = parts[1]
                            observation_json.append({
                                "tool_name": tool_name,
                                "result": result_value
                            })
                    
                    # 添加解析错误信息到观察结果中
                    if error_messages:
                        for error_msg in error_messages:
                            observation_json.append({
                                "tool_name": "parse_error",
                                "result": error_msg
                            })
                    
                    # 如果没有有效的结果但有last_error_msg，添加它
                    if not observation_json and self.last_error_msg:
                        observation_json.append({
                            "tool_name": "parse_error",
                            "result": self.last_error_msg
                        })
                    
                    # 更新响应格式为XML风格
                    observation_xml = """<Observation>\n"""
                    for obs in observation_json:
                        observation_xml += json.dumps(obs, ensure_ascii=False) + "\n"
                    observation_xml += "</Observation>"
                    
                    react_trace.append(observation_xml)
                    
                    # 将Observation作为用户消息添加到对话中，推动下一轮对话
                    messages.append({
                        "role": "user", 
                        "content": observation_xml
                    })
                else:
                    self._log("\n[No tool call detected]")
                    # Add the cleaned content to the conversation
                    messages.append({"role": "assistant", "content": assistant_content})
                    
                    # If approaching the maximum number of iterations, prompt for a final answer
                    if current_iteration > max_iterations / 2:
                        messages.append({
                            "role": "user", 
                            "content": "You need to provide a final answer now. Format your response exactly as follows:\n\n<Thought>\nYour final thoughts summarizing what you've learned and your conclusion.\n</Thought>\n\n<Final_Answer>\nYour direct answer to the original question.\n</Final_Answer>\n\nNote: If you previously attempted to use a tool but it wasn't processed correctly, please focus on providing your final answer based on information you already have."
                        })
                    else:
                        # If we detected an attempt to use tools but failed to parse properly, provide specific feedback
                        if "<Action>" in assistant_content:
                            # 尝试获取解析错误信息
                            parsing_error = self.last_error_msg or "JSON Format Parsing Error"
                                
                            error_feedback = f"""<Observation>
{{"tool_name": "parse_error", "result": "{parsing_error}"}}
</Observation>

Please check your JSON format, ensure:
1. JSON objects don't contain line breaks
2. Special characters in strings are properly escaped
3. All quotes are correctly paired
4. Format should be: {{"tool_name": "name", "parameters": {{"param1": "value1"}}}}

Please retry with the correct format:

<Thought>
Rethink the next steps
</Thought>

<Action>
{{"tool_name": "tool_name_here", "parameters": {{"param1": "value1"}}}}
</Action>
"""
                            messages.append({
                                "role": "user",
                                "content": error_feedback
                            })
                        else:
                            messages.append({
                                "role": "user", 
                                "content": "Please continue your reasoning process using the exact format below:\n\n<Thought>\nYour reasoning about the current situation and what to do next.\n</Thought>\n\nIf you need to use a tool:\n<Action>\n{{\"tool_name\": \"tool_name_here\", \"parameters\": {{\"param1\": \"value1\"}}}}\n</Action>\n\nOr if you have enough information to answer:\n<Final_Answer>\nYour direct answer to the original question.\n</Final_Answer>\n\nNote: If you previously attempted to use a tool but it wasn't processed correctly, please reformat your request using the exact format above."
                            })
            
            except Exception as e:
                error_msg = f"Model API call failed: {str(e)}"
                self._log(f"\n[API调用错误] {error_msg}")
                # 尝试使用备用模型
                if current_iteration == 1:
                    backup_model = kwargs.get("backup_model", 
                                           self.text_model)  # 使用text_model作为备用
                    self._log(f"\n[尝试使用备用模型] {backup_model}")
                    model = backup_model
                    continue
                return f"Model API call failed: {str(e)}", False
        
        # 如果达到最大迭代次数还没有找到Final Answer
        if final_answer is None:
            self._log("\n[达到最大迭代次数]")
            self._log("未找到Final Answer，尝试从最后有效回复构建答案")
            
            # 使用最后一次有效回复构建答案
            if last_valid_response:
                if "Thought:" in last_valid_response:
                    thoughts = last_valid_response.split("Thought:")
                    final_thought = thoughts[-1].strip()
                    # 清理掉可能包含的其他关键字
                    for keyword in ["Action:", "Observation:"]:
                        if keyword in final_thought:
                            final_thought = final_thought.split(keyword)[0].strip()
                    final_answer = f"{final_thought}"
                else:
                    final_answer = last_valid_response
            else:
                final_answer = "Unable to reach a clear conclusion. Please try asking again or provide more information."
        
        # # 记录完整的ReAct过程到日志
        # self._log("\n[完整ReAct过程]")
        # for step in react_trace:
        #     self._log("-" * 40)
        #     self._log(step)
        
        self._log("\n" + "="*80)
        self._log("REACT模式对话会话结束")
        self._log("="*80 + "\n")
        
        return final_answer, used_tool

    #--------------------------------------------------------------------------
    # History Management Methods
    #--------------------------------------------------------------------------
    
    def log_history(self):
        """将对话历史输出到日志"""
        self._log("\n[对话历史]")
        for message in self.history:
            role = message['role']
            content = message['content']
            if isinstance(content, str):
                self._log(f"{role}: {content}")
            elif isinstance(content, list):
                content_str = ""
                for item in content:
                    if item['type'] == 'text':
                        content_str += f"{item['text']} "
                    elif item['type'] == 'image_url':
                        content_str += "[IMAGE] "
                self._log(f"{role}: {content_str.strip()}")

    def clear_history(self):
        """清空对话历史"""
        system_prompt = self.system_prompt
        self.history = [{"role": "system", "content": system_prompt}]
        self._log("已清空对话历史")

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    
    def _log(self, message: str):
        """记录日志
        
        Args:
            message: 日志消息
        """
        if self.use_log:
            os.makedirs(os.path.dirname(self.log_folder), exist_ok=True)
            if os.path.exists(self.log_folder):
                with open(self.log_folder, "a", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            else:
                with open(self.log_folder, "w", encoding="utf-8") as f:
                    f.write(f"{message}\n")


if __name__ == "__main__":    
    agent = Agent(use_log=True)
    
    # 注册一些测试工具
    agent.register_tool(
        tool_name="calculate",
        tool_func=lambda expression: eval(expression),
        tool_description="计算数学表达式",
        tool_parameters={"expression": {"type": "string", "description": "要计算的数学表达式"}},
        required=["expression"]
    )
    
    agent.register_tool(
        tool_name="get_current_time",
        tool_func=lambda: __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tool_description="获取当前时间",
        tool_parameters={},
        required=[]
    )
    
    # 设置系统提示词
    agent.set_system_prompt("你是一个有用的助手，可以回答问题和使用工具。")
    
    # 测试ReAct聊天功能
    print("开始测试ReAct模式聊天...")
    question = "计算123+456是多少，然后告诉我当前的时间"
    
    # 启用对话历史更新
    agent.chat_status(True)
    
    # 执行ReAct聊天
    answer, used_tool = agent.chat_ReAct(question)
    
    print("\n===测试结果===")
    print(f"问题: {question}")
    print(f"回答: {answer}")
    print(f"是否使用了工具: {used_tool}")
    
    # 如果想查看完整的对话历史
    print("\n===对话历史===")
    agent.log_history()