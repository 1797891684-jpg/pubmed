import streamlit as st
import pandas as pd
from openai import OpenAI

# ==================== 1. BioRender 风格主题配置 ====================
st.set_page_config(
    page_title="AI纳米医学文献速览", 
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 注入 BioRender 经典美学：细胞蓝 (#005A9C)、高光绿 (#00A86B)、无边界卡片微阴影
biorender_theme = """
            <style>
            /* 全局字体与底色优化 */
            html, body, [data-testid="stAppViewContainer"] {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #F8FAFC !important;
            }
            
            /* 侧边栏 BioRender 深邃科技蓝 */
            [data-testid="stSidebar"] {
                background-color: #0F172A !important;
                color: #FFFFFF !important;
            }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
                color: #F1F5F9 !important;
            }
            
            /* 主标题高级感：渐变纳米色 */
            .main-title {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-weight: 800;
                background: linear-gradient(135deg, #0284C7 0%, #0D9488 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5rem;
                margin-bottom: 0.2rem;
            }
            
            /* BioRender 风格科研卡片 (阴影与圆角) */
            div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
                background: #FFFFFF;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                border: 1px solid #E2E8F0;
                margin-bottom: 1rem;
            }
            
            /* 隐藏烦人的 Streamlit 官方脚标 */
            footer, [data-testid="stFooter"], header, [data-testid="stHeader"] {
                display: none !important;
                visibility: hidden !important;
            }
            </style>
            """
st.markdown(biorender_theme, unsafe_allow_html=True)

# ==================== 2. 侧边栏：配置中心 ====================
with st.sidebar:
    st.markdown("### 🔑 BioRender AI Engine")
    st.caption("基于交叉学科大模型驱动的科研提效看板")
    
    user_key = st.text_input("输入国产大模型 API Key", type="password", help="可在智谱AI、DeepSeek等平台免费申请")
    provider = st.selectbox("选择大模型驱动核心", ["智谱 AI (GLM)", "DeepSeek", "通义千问"])

    st.markdown("---")
    st.markdown("### 📢 纳米医学交流群")
    
    # 占位符图片（后续直接换成你的真实群二维码）
    st.image("https://via.placeholder.com/200", caption="长按扫码，加入 AI 纳米交叉学科群")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.85rem;'>
    💡 <b>小红书 ID</b>：你的小红书号 <br>
    🎁 <b>独家福利</b>：进群调取端到端物化性质预测、HA/LNP 模拟教程及纳米材料大模型 Prompt 模板！
    </div>
    """, unsafe_allow_html=True)

# ==================== 3. 主界面看板 ====================
# 用自定义 HTML 渲染炫酷的 BioRender 风格标题
st.markdown('<p class="main-title">🧬 AI 纳米医学文献推文生成器</p>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1rem; margin-top:-10px;'>End-to-End Workflow: 从 PubMed 高维文献特征到多渠道学术传播文案的一键提炼平台。</p>", unsafe_allow_html=True)
st.markdown("---")

# 数据看板卡片
with st.container():
    st.markdown("#### 📋 待处理纳米载体文献列表 (Current Batch)")
    demo_data = {
        "Title": ["Automated Design of Hyaluronic Acid Nanoparticles via Deep Learning",
                  "Lipid Nanoparticles for mRNA Delivery: An End-to-End Prediction Workflow"],
        "Journal": ["Advanced Materials", "Journal of Controlled Release"],
        "Date": ["2026-05-20", "2026-05-24"],
        "Abstract": ["Here we report a machine learning framework to optimize HA nanoparticles...",
                     "This study establishes an end-to-end workflow linking material features to biological fate..."],
        "DOI": ["10.1002/adma.2026001", "10.1016/j.jconrel.2026.002"]
    }
    df_literature = pd.DataFrame(demo_data)
    st.dataframe(df_literature, width="stretch")

# 转换数据为大模型输入的文本格式
papers_text = ""
for index, row in df_literature.iterrows():
    papers_text += f"文献 {index + 1}:\n标题: {row['Title']}\n期刊: {row['Journal']} (Online: {row['Date']})\n摘要: {row['Abstract']}\nDOI: {row['DOI']}\n{'-' * 20}\n"

# ==================== 4. AI 生成看板 ====================
st.markdown("#### 🤖 AI 推文生成控制台")

# 按钮放在卡片容器内部
with st.container():
    if st.button("🚀 启动大模型提炼文案", type="primary"):
        if not user_key:
            st.error("❌ 请先在左侧边栏输入您的 API Key！")
        else:
            if provider == "智谱 AI (GLM)":
                base_url = "https://open.bigmodel.cn/api/paas/v4"
                model_name = "glm-4-flash"  
            elif provider == "DeepSeek":
                base_url = "https://api.deepseek.com/v1"
                model_name = "deepseek-chat"
            elif provider == "通义千问":
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                model_name = "qwen-plus"

            prompt = f"你现在是一位生物医药与AI交叉领域的资深学术博主。请根据以下英文文献摘要，写一篇微信公众号推文草稿...\n{papers_text}"

            try:
                client = OpenAI(api_key=user_key, base_url=base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )

                output_container = st.empty()
                full_response = ""

                for chunk in response:
                    delta = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                    full_response += delta
                    output_container.markdown(full_response + "▌")  

                tail_text = f"\n\n---\n*💡 本文由 [AI科研速览助手] 自动化生成。欢迎关注小红书 ID: [你的小红书号]，解锁更多科研提效神器！*"
                final_article = full_response + tail_text
                output_container.markdown(final_article)  

                st.session_state["generated_content"] = final_article

            except Exception as e:
                st.error(f"❌ 呼叫大模型失败，请检查Key或网络。错误信息: {e}")

# ==================== 5. 输出结果组件 ====================
if "generated_content" in st.session_state:
    with st.container():
        st.success("✨ 文案提炼完成 (Biological Fate Copilot Successfully Processed)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 下载符合期刊风格的 Markdown",
                data=st.session_state["generated_content"],
                file_name="BioMed_Weekly_Review.md",
                mime="text/markdown",
                width="stretch"
            )
        with col2:
            st.info("💡 提示：双击上方文本框，即可直接复制全文内容。")

# 免责声明
st.markdown("""
<p style='color: #94A3B8; font-size: 0.8rem; text-align: center; margin-top: 50px;'>
⚠️ Security & Disclaimer: 本工具仅作为交叉学科内容提炼辅助，数据源自第三方大模型。发布前请根据 DOI 核对原始物化性质描述。
</p>
""", unsafe_allow_html=True)
