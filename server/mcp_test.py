"""测试MCP Web搜索功能"""
import config
from loguru import logger
from mcp_manager import mcp_manager

def test_web_search():
    """测试Web搜索"""
    
    # 初始化MCP
    logger.info("正在初始化MCP服务...")
    if not mcp_manager.initialize():
        logger.error("MCP初始化失败")
        return
    
    # 测试查询
    test_queries = [
        "MIT位于哪个州？",
        "今天的天气",
        "RAG技术是什么"
    ]
    
    for query in test_queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"测试查询: {query}")
        logger.info(f"{'='*60}")
        
        result = mcp_manager.web_search(query)
        
        if result:
            logger.info(f"✅ 搜索成功")
            logger.info(f"结果类型: {type(result)}")
            logger.info(f"结果长度: {len(str(result))}")
            logger.info(f"结果内容(前500字符):\n{str(result)[:500]}")
            
            # 如果是字典，打印所有键
            if isinstance(result, dict):
                logger.info(f"字典键: {list(result.keys())}")
        else:
            logger.error(f"❌ 搜索失败")

if __name__ == "__main__":
    # 确保启用Web搜索
    config.ENABLE_WEB_SEARCH = True
    
    # 设置日志级别为DEBUG以查看详细信息
    logger.remove()
    logger.add(lambda msg: print(msg), level="DEBUG")
    
    test_web_search()