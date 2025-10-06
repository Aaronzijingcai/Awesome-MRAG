import json
from typing import Optional

import config
from loguru import logger
from mcpstore import MCPStore


class MCPManager:
    
    def __init__(self):
        self.store = None
        self.web_search_tool = None
        
    def initialize(self):
        try:
            with open(config.MCP_CONFIG_PATH, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
            
            # 1. 初始化MCPStore
            self.store = MCPStore.setup_store()
            
            for server in mcp_config.get("servers", []):
                if not server.get("enabled", True):
                    continue
                
                headers = server.get("headers", {})
                if "Authorization" in headers:
                    headers["Authorization"] = headers["Authorization"].replace(
                        "YOUR_DASHSCOPE_API_KEY", config.DASHSCOPE_API_KEY
                    )
                
                # 2. 将服务添加到Store中
                self.store.for_store().add_service({
                    "name": server["name"],
                    "url": server["url"],
                    "transport": server["transport"],
                    "headers": headers
                })
                
                # 3. 等待服务就绪
                self.store.for_store().wait_service(server["name"])
                logger.info(f"✅ MCP服务 {server['name']} 已就绪")
            
            # 4. 重点关注for_langchain()函数，将之前的服务对象包装成langchain能够使用的tool
            tools = self.store.for_store().for_langchain().list_tools()
            for tool in tools:
                print(tool.name)
                # 5. 指定使用bailian-websearch服务
                if "bailian-websearch" in tool.name.lower():
                    self.web_search_tool = tool
                    logger.info(f"找到Web搜索工具: {tool.name}")
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"初始化MCP服务失败: {e}")
            return False
    
    def web_search(self, query: str) -> Optional[str]:
        if not self.web_search_tool:
            return None
        
        try:
            # 1. bailian官网上指定所需的参数
            result = self.web_search_tool.invoke({
                "query": query,
                "count": 1, # 只检索一个
                "ctx": ""
            })
            logger.info(f"Web搜索成功: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Web搜索失败: {e}")
            return None


MCP_Service = MCPManager()