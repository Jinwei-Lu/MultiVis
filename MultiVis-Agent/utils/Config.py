import os

class Config:
    def __init__(self):
        self.db_folder = "./tmp/db"
        self.image_folder = "./tmp/image"
        self.code_folder = "./tmp/code"

        self.MODEL_CONFIGS = {
            "qwen": {
                "api_key": "xxx",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "llama": {
                "api_key": "xxx",
                "base_url": "xxx"
            },
            "deepseek": {
                "api_key": "xxx",
                "base_url": "https://api.deepseek.com"
            },
            "gpt": {
                "api_key": "xxx",
                "base_url": "xxx",
            },
            "claude": {
                "api_key": "xxx",
                "base_url": "xxx",
            },
            "doubao": {
                "api_key": "xxx",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3/"
            },
            "kimi": {
                "api_key": "xxx",
                "base_url": "https://api.moonshot.cn/v1"
            },
            "moonshot": {
                "api_key": "xxx",
                "base_url": "https://api.moonshot.cn/v1"
            },
            "gemini": {
                "api_key": "xxx",
                "base_url": "xxx",
            },
        }

