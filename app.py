import gradio as gr
import requests
import json
from typing import Generator
import time

def query_rag(message: str, history: list) -> Generator[tuple, None, None]:
    """
    调用RAG接口并流式返回结果
    """
    url = "http://localhost:8992/rag/query"
    payload = {"query": message}
    
    # 添加用户消息
    new_history = history + [{"role": "user", "content": message}]
    
    # 显示加载骨架屏
    loading_message = "⏳ 正在思考中..."
    yield new_history + [{"role": "assistant", "content": loading_message}], ""
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 获取模型回答
        answer = result.get("response", "抱歉，没有获取到回答。")
        
        # 流式输出效果
        assistant_message = ""
        for char in answer:
            assistant_message += char
            yield new_history + [{"role": "assistant", "content": assistant_message}], ""
            time.sleep(0.01)
        
        # 构建溯源信息HTML（使用radio按钮 + 正确的HTML结构）
        sources = result.get("sources", [])
        sources_html = ""
        if sources:
            import random
            unique_id = random.randint(10000, 99999)
            
            sources_html = f'''
            <div class="sources-wrapper-{unique_id}">
            '''
            
            # 先放置所有radio input（隐藏的）
            for idx in range(len(sources)):
                checked = "checked" if idx == 0 else ""
                sources_html += f'<input type="radio" name="source-radio-{unique_id}" id="radio-{unique_id}-{idx}" class="source-radio" {checked}>'
            
            sources_html += f'''
                <div class="sources-container">
                    <div class="sources-header">📚 参考来源</div>
                    <div class="sources-tags-wrapper">
            '''
            
            # 添加标签label
            for idx in range(len(sources)):
                sources_html += f'<label for="radio-{unique_id}-{idx}" class="source-tag">[{idx + 1}]</label>'
            
            sources_html += '</div><div class="source-display-area">'
            
            # 添加所有内容块
            for idx, source in enumerate(sources):
                metadata = source.get("metadata", {})
                page_content = source.get("page_content", "")
                
                file_name = metadata.get("file_name", "未知文件")
                source_location = metadata.get("source_location", "未知位置")
                
                sources_html += f'''
                <div class="source-content source-content-{idx}">
                    <div class="source-meta">
                        <strong>📄 {file_name}</strong> · {source_location}
                    </div>
                    <div class="source-text">{page_content}</div>
                </div>
                '''
            
            sources_html += '</div></div></div>'
            
            # 使用CSS控制显示
            sources_html += f'''
            <style>
            .sources-wrapper-{unique_id} .source-radio {{
                display: none;
            }}
            
            .sources-wrapper-{unique_id} .source-content {{
                display: none;
            }}
            '''
            
            # 为每个radio生成对应的显示规则 - 带紫色主题
            for idx in range(len(sources)):
                sources_html += f'''
            .sources-wrapper-{unique_id} #radio-{unique_id}-{idx}:checked ~ .sources-container .source-content-{idx} {{
                display: block !important;
                animation: slideDown 0.3s ease-out;
            }}
            
            .sources-wrapper-{unique_id} #radio-{unique_id}-{idx}:checked ~ .sources-container .sources-tags-wrapper label[for="radio-{unique_id}-{idx}"] {{
                background: linear-gradient(135deg, #5b47d2 0%, #7b64e8 100%) !important;
                color: white !important;
                border-color: #5b47d2 !important;
                box-shadow: 0 4px 16px rgba(91, 71, 210, 0.4) !important;
                transform: scale(1.05) !important;
                font-weight: 600 !important;
            }}
                '''
            
            sources_html += '''
            </style>
            '''
        
        yield new_history + [{"role": "assistant", "content": answer}], sources_html
            
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 请求失败：{str(e)}\n\n请确保后端服务运行在 http://localhost:8992"
        yield new_history + [{"role": "assistant", "content": error_msg}], ""
    except Exception as e:
        error_msg = f"❌ 发生错误：{str(e)}"
        yield new_history + [{"role": "assistant", "content": error_msg}], ""

# 自定义CSS样式
custom_css = """
/* 全局容器样式 */
.gradio-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
}

/* 隐藏页脚 */
footer {
    display: none !important;
}

/* 聊天容器样式 */
.chatbot-container {
    border-radius: 16px;
    overflow: hidden;
}

/* 发送按钮样式 */
button[variant="primary"] {
    min-width: 90px !important;
    height: 40px !important;
    border-radius: 20px !important;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

button[variant="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
}

button[variant="primary"]:active {
    transform: translateY(0) scale(0.98) !important;
}

/* 清空按钮样式 */
.clear-button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border-radius: 12px !important;
}

.clear-button:hover {
    transform: scale(1.05) !important;
}

.clear-button:active {
    transform: scale(0.95) !important;
}

/* 示例卡片悬浮效果 */
.examples-container button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border-radius: 12px !important;
}

.examples-container button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

/* 溯源信息容器样式 */
.sources-container {
    margin-top: 16px;
    padding: 20px;
    background: var(--background-fill-secondary);
    border-radius: 16px;
    border: 1px solid var(--border-color-primary);
}

.sources-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--body-text-color);
}

/* 标签容器 - 横向排列 */
.sources-tags-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border-color-primary);
}

/* 溯源标签样式 */
.source-tag {
    padding: 8px 16px;
    background: var(--neutral-200);
    color: var(--neutral-600);
    border: 2px solid transparent;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    outline: none;
    user-select: none;
}

.source-tag:hover {
    transform: translateY(-2px) scale(1.05);
    background: var(--neutral-300);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 激活状态的标签 */
.source-tag.active {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    border-color: #2563eb;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4) !important;
    transform: scale(1.08) !important;
}

.source-tag.active:hover {
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
}

.source-tag:active {
    transform: scale(0.95) !important;
}

/* 内容显示区域 */
.source-display-area {
    position: relative;
    min-height: 150px;
}

.source-content {
    padding: 20px;
    background: var(--background-fill-primary);
    border-radius: 12px;
    border: 1px solid var(--border-color-primary);
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.source-meta {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color-primary);
    font-size: 14px;
    color: var(--body-text-color);
}

.source-text {
    line-height: 1.8;
    color: var(--body-text-color);
    font-size: 14px;
    white-space: pre-wrap;
}

/* 加载骨架屏动画 */
@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

/* 暗色模式适配 */
.dark .sources-container {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
}

.dark .source-content {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.1);
}

.dark .source-tag {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
}

.dark .source-tag:hover {
    background: rgba(255, 255, 255, 0.15);
}

.dark .source-tag.active {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
}

/* 主题切换按钮样式 */
.theme-toggle {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.theme-toggle:hover {
    transform: rotate(15deg) scale(1.1) !important;
}

.theme-toggle:active {
    transform: rotate(15deg) scale(0.95) !important;
}

/* 输入框区域优化 */
.input-box-wrapper {
    position: sticky;
    bottom: 0;
    padding: 20px 0;
    background: linear-gradient(to top, var(--background-fill-primary) 80%, transparent);
    z-index: 100;
}

.input-box-inner {
    background: var(--background-fill-secondary);
    border-radius: 24px;
    padding: 6px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-box-inner:focus-within {
    box-shadow: 0 12px 32px rgba(37, 99, 235, 0.2), 0 4px 12px rgba(37, 99, 235, 0.15);
    transform: translateY(-2px);
}

.dark .input-box-inner {
    background: rgba(255, 255, 255, 0.05);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2);
}
"""

# 创建Gradio界面
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.purple,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    ).set(
        body_background_fill="*neutral_50",
        body_text_color="*neutral_900",
        button_primary_background_fill="#5b47d2",
        button_primary_background_fill_hover="#4a38b8",
        input_border_color="*neutral_200",
        block_border_width="1px",
    ),
    title="RAG 智能问答系统",
    css=custom_css
) as demo:
    
    # 标题和主题切换
    with gr.Row():
        with gr.Column(scale=10):
            gr.Markdown(
                """
                <div style="text-align: center;">
                
                # 🤖 RAG 智能问答系统
                
                基于检索增强生成技术的智能问答助手
                
                </div>
                """
            )
        with gr.Column(scale=1, min_width=100):
            theme_btn = gr.Button("🌓 切换主题", elem_classes="theme-toggle", size="sm")
    
    # 聊天界面
    chatbot = gr.Chatbot(
        height=500,
        show_label=False,
        avatar_images=("./pic/dog.png", "./pic/squirrel.png"),
        type="messages",
        elem_classes="chatbot-container",
        show_copy_button=True
    )
    
    # 溯源信息显示区域
    sources_display = gr.HTML(label="", visible=True)
    
    # 输入框区域
    with gr.Row(elem_classes="input-box-wrapper"):
        msg = gr.Textbox(
            placeholder="💭 请输入您的问题...",
            show_label=False,
            scale=9,
            container=False,
            lines=1
        )
        submit_btn = gr.Button("发送 ✨", variant="primary", scale=1)
    
    with gr.Row():
        clear_btn = gr.Button("🗑️ 清空对话", size="sm", elem_classes="clear-button")
    
    # 示例问题
    with gr.Row(elem_classes="examples-container"):
        gr.Examples(
            examples=[
                "Agent在2025年发展趋势如何？",
                "介绍一下Agentcpm-gui框架",
                "WebArena是什么？",
                "当前Agent技术面临哪些挑战？",
            ],
            inputs=msg,
            label="💡 快速开始"
        )
    
    gr.Markdown(
        """
        ---
        
        <div class="features-card">
        
        **✨ 功能特性**
        
        🎯 **智能检索** · 基于向量数据库的精准检索  
        📚 **溯源透明** · 点击标签切换查看参考来源  
        🌓 **主题切换** · 支持浅色/深色模式  
        ⚡ **流式输出** · 实时显示AI思考过程
        
        </div>
        """,
        elem_classes="features-section"
    )
    
    # 主题切换逻辑
    theme_btn.click(
        fn=None,
        js="""
        () => {
            document.body.classList.toggle('dark');
            const isDark = document.body.classList.contains('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        }
        """
    )
    
    # 事件绑定
    msg.submit(
        fn=query_rag,
        inputs=[msg, chatbot],
        outputs=[chatbot, sources_display],
    ).then(
        lambda: gr.update(value=""),
        outputs=[msg]
    )
    
    submit_btn.click(
        fn=query_rag,
        inputs=[msg, chatbot],
        outputs=[chatbot, sources_display],
    ).then(
        lambda: gr.update(value=""),
        outputs=[msg]
    )
    
    clear_btn.click(
        fn=lambda: (None, ""),
        outputs=[chatbot, sources_display]
    )
    
    # 页面加载时恢复主题
    demo.load(
        fn=None,
        js="""
        () => {
            const theme = localStorage.getItem('theme');
            if (theme === 'dark') {
                document.body.classList.add('dark');
            }
        }
        """
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )