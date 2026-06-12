import os

class Config:
    def __init__(self):
        self.db_folder = "./tmp/db"
        self.image_folder = "./tmp/image"
        self.code_folder = "./tmp/code"
        proxy_api_key = os.environ.get("MULTIVIS_PROXY_API_KEY", "")

        self.MODEL_CONFIGS = {
            "qwen": {
                "api_key": os.environ.get("QWEN_API_KEY", ""),
                "base_url": os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            },
            "llama": {
                "api_key": os.environ.get("LLAMA_API_KEY", ""),
                "base_url": os.environ.get("LLAMA_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            },
            "deepseek": {
                "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
                "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            },
            "gpt": {
                "api_key": proxy_api_key,
                "base_url": os.environ.get("MULTIVIS_PROXY_BASE_URL", "https://api.openai-proxy.org/v1"),
            },
            "claude": {
                "api_key": proxy_api_key,
                "base_url": os.environ.get("MULTIVIS_PROXY_BASE_URL", "https://api.openai-proxy.org/v1"),
            },
            "doubao": {
                "api_key": os.environ.get("DOUBAO_API_KEY", ""),
                "base_url": os.environ.get("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/")
            },
            "kimi": {
                "api_key": os.environ.get("KIMI_API_KEY", ""),
                "base_url": os.environ.get("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
            },
            "moonshot": {
                "api_key": os.environ.get("MOONSHOT_API_KEY", ""),
                "base_url": os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
            },
            "gemini": {
                "api_key": proxy_api_key,
                "base_url": os.environ.get("MULTIVIS_PROXY_BASE_URL", "https://api.openai-proxy.org/v1"),
            },
        }
