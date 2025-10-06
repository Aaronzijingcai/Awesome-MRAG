import json
from typing import Optional

import config
from loguru import logger
from mcpstore import MCPStore


class MCPManager:
    """MCP服务管理器"""
    
    def __init__(self):
        self.store = None
        self.web_search_tool = None
        
    def initialize(self):
        """初始化MCP服务"""
        try:
            with open(config.MCP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
            
            self.store = MCPStore.setup_store()
            
            for server in mcp_config.get("servers", []):
                if not server.get("enabled", True):
                    continue
                
                headers = server.get("headers", {})
                if "Authorization" in headers:
                    headers["Authorization"] = headers["Authorization"].replace(
                        "YOUR_DASHSCOPE_API_KEY", config.DASHSCOPE_API_KEY
                    )
                
                self.store.for_store().add_service({
                    "name": server["name"],
                    "url": server["url"],
                    "transport": server["transport"],
                    "headers": headers
                })
                
                self.store.for_store().wait_service(server["name"])
                logger.info(f"✅ MCP服务 {server['name']} 已就绪")
            
            # 获取Web搜索工具
            tools = self.store.for_store().for_langchain().list_tools()
            for tool in tools:
                if "bailian_web_search" in tool.name.lower():
                    self.web_search_tool = tool
                    logger.info(f"找到Web搜索工具: {tool.name}")
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"初始化MCP服务失败: {e}")
            return False
    
    def web_search(self, query: str) -> Optional[str]:
        """执行Web搜索"""
        if not self.web_search_tool:
            return None
        
        try:
            result = self.web_search_tool.invoke({
                "query": query,
                "count": 5,
                "ctx": ""
            })
            logger.info(f"Web搜索成功: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Web搜索失败: {e}")
            return None


# 全局MCP管理器实例
MCP_Service = MCPManager()