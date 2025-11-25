from typing import Dict, List, Any, Callable
from datetime import datetime
import json


class ToolManager:
    """工具管理器
    
    负责管理和组织LLM可以使用的各种工具，包括工具的注册、配置和执行。
    """
    
    def __init__(self):
        """初始化工具管理器"""
        self.tools: List[Dict[str, Any]] = []  # 工具配置列表
        self.tool_functions: Dict[str, Callable] = {}  # 工具函数映射
        
    def register_tool(self, 
                     name: str,
                     func: Callable,
                     description: str,
                     parameters: Dict[str, Any],
                     required: list[str] = []) -> None:
        """注册一个新工具
        
        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            parameters: 工具参数配置
            required: 工具参数是否必填，默认为全部参数
        """
        if required == []:
            required = [k for k, v in parameters.items()]

        # 创建工具配置
        tool_config = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }
        
        # 注册工具配置和函数
        self.tools.append(tool_config)
        self.tool_functions[name] = func
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具配置"""
        return self.tools
        
    def get_tools_prompt(self) -> List[Dict[str, Any]]:
        """获取所有工具配置
        
        Returns:
            工具配置列表
        """
        tools_str = ""
        for tool in self.tools:
            tools_str += f"{json.dumps(tool['function'], ensure_ascii=False)}\n"
        return tools_str.strip()
    
    def get_tool_functions(self) -> Dict[str, Callable]:
        """获取所有工具函数
        
        Returns:
            工具函数映射
        """
        return self.tool_functions
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """执行指定的工具
        
        Args:
            name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
            
        Raises:
            ValueError: 工具不存在时抛出
        """
        if name not in self.tool_functions:
            raise ValueError(f"Tool {name} not found")
        
        return self.tool_functions[name](**kwargs)
    
    def get_tool_description(self, name: str = "all") -> str:
        """获取工具的描述
        
        Args:
            name: 工具名称
        """
        if name == "all":
            return "\n".join([self.tools[i]["function"]["description"] for i in range(len(self.tools))])
        else:
            for i in range(len(self.tools)):
                if self.tools[i]["function"]["name"] == name:
                    return self.tools[i]["function"]["description"]
            return f"Tool {name} not found"
    
    def get_tool_parameters(self, name: str) -> dict:
        """获取工具的参数定义
        
        Args:
            name: 工具名称
            
        Returns:
            dict: 工具参数定义，如果工具不存在则返回空字典
        """
        for tool in self.tools:
            if tool["function"]["name"] == name:
                return tool["function"]["parameters"]["properties"]
        return {}
        


if __name__ == "__main__":
    # 测试工具管理器
    manager = ToolManager()
    
    # 注册一个测试工具
    def test_tool(message: str) -> str:
        return f"Test tool received: {message}"
    
    def test_tool_2(message: str) -> str:
        return f"Test tool 2 received: {message}"

    manager.register_tool(
        name="test_tool",
        func=test_tool,
        description="A test tool that echoes the input message",
        parameters={
            "message": {
                "type": "string",
                "description": "Message to echo"
            }
        }
    )

    manager.register_tool(
        name="test_tool_2",
        func=test_tool_2,
        description="A test tool that echoes the input message",
        parameters={
            "message": {
                "type": "string",
                "description": "Message to echo"
            }
        }
    )
    
    # 打印工具配置
    print("工具配置:")
    print(manager.get_tools())
    
    # 测试工具执行
    print("\n测试工具执行:")
    result = manager.execute_tool("test_tool", message="Hello, World!")
    print(f"测试结果: {result}") 

    # 测试获取工具描述
    print("\n测试获取工具描述:")
    description = manager.get_tool_description()
    print(f"工具描述: {description}")

