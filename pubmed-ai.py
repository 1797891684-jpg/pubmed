import streamlit as st
import pandas as pd
from openai import OpenAI

# ==================== 1. 网页基础配置与引流看板 ====================
st.set_page_config(page_title="AI纳米医学文献速览", page_icon="🧬", layout="wide")
# ==================== 网页基础配置与引流看板 ====================
st.set_page_config(page_title="AI纳米医学文献速览", page_icon="🧬", layout="wide")

# 🔥 强行注入 CSS，彻底隐藏 Streamlit 所有官方标识（菜单、页脚、彩虹条）
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}       /* 隐藏右上角主菜单 */
            footer {visibility: hidden;}          /* 隐藏底部 Made with Streamlit */
            header {visibility: hidden;}          /* 隐藏顶部彩虹装饰条 */
            .stDeployButton {display:none;}       /* 隐藏右上角的 Deploy 按钮 */
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 侧边栏：API配置与引流硬广告
with st.sidebar:
    st.title("🔑 助手配置中心")

    # 隐私输入 API Key
    user_key = st.text_input("输入国产大模型 API Key", type="password", help="可在智谱AI、DeepSeek等平台免费申请")
    provider = st.selectbox("选择模型供应商", ["智谱 AI (GLM)", "DeepSeek", "通义千问"])

    st.markdown("---")
    # 🔥 引流钩子：替换为你自己的二维码和ID
    st.subheader("📢 关注作者 / 进科研交流群")
    st.image("https://via.placeholder.com/200", caption="扫码加入 AI 纳米医学交流群")  # 实际开发换成你的微信二维码链接
    st.markdown("""
    * **小红书 ID**：`你的小红书号`
    * **福利**：群内定期分享 AI 搞科研干货、Prompt 模板及纳米载体模拟教程！
    """)

# 主界面
st.title("🧬 AI 纳米医学文献推文生成器")
st.caption("输入 PubMed 抓取的数据，一键大模型精炼，一键导出小红书/公众号爆款文案。")

# ==================== 2. 模拟前端接收到的 PubMed 数据 ====================
# （实际产品中，这里承接你模块1抓取出来的 DataFrame）
st.subheader("📋 待处理文献列表 (示例数据)")
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
st.dataframe(df_literature, use_container_width=True)

# 转换数据为大模型输入的文本格式
papers_text = ""
for index, row in df_literature.iterrows():
    papers_text += f"文献 {index + 1}:\n标题: {row['Title']}\n期刊: {row['Journal']} (Online: {row['Date']})\n摘要: {row['Abstract']}\nDOI: {row['DOI']}\n{'-' * 20}\n"

# ==================== 3. 大模型调用与前端流式返回 ====================
st.subheader("🤖 AI 推文生成看板")

if st.button("🚀 启动大模型提炼文案", type="primary"):
    if not user_key:
        st.error("❌ 请先在左侧边栏输入您的 API Key！")
    else:
        # 根据供应商匹配各自的 base_url 和模型名称
        if provider == "智谱 AI (GLM)":
            base_url = "https://open.bigmodel.cn/api/paas/v4"
            model_name = "glm-4-flash"  # 智谱的高性价比/免费额度模型
        elif provider == "DeepSeek":
            base_url = "https://api.deepseek.com/v1"
            model_name = "deepseek-chat"
        elif provider == "通义千问":
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            model_name = "qwen-plus"

        # 构造 Prompt
        manual_date_range = "2026.05.21-2026.05.24"  # 动态读取
        prompt = f"你现在是一位生物医药与AI交叉领域的资深学术博主。请根据以下英文文献摘要，写一篇微信公众号推文草稿...\n{papers_text}"

        try:
            # 初始化 OpenAI 兼容客户端
            client = OpenAI(api_key=user_key, base_url=base_url)

            # 使用流式传输 (Streaming) 让网页显得极快、不卡顿
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            # 在前端挖一个空位用于实时渲染 Markdown
            output_container = st.empty()
            full_response = ""

            for chunk in response:
                # 兼容不同厂商的 stream 返回格式
                delta = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                full_response += delta
                output_container.markdown(full_response + "▌")  # 模拟光标闪烁

            # 自动强行拼接引流版权小尾巴
            tail_text = f"\n\n---\n*💡 本文由 [AI科研速览助手] 自动化生成。欢迎关注小红书 ID: [你的小红书号]，解锁更多科研提效神器！*"
            final_article = full_response + tail_text
            output_container.markdown(final_article)  # 最终渲染

            # 将生成的内容存入 session_state 供下载按钮读取
            st.session_state["generated_content"] = final_article

        except Exception as e:
            st.error(f"❌ 呼叫大模型失败，请检查Key或网络。错误信息: {e}")

# ==================== 4. 用户复制与下载组件 ====================
if "generated_content" in st.session_state:
    st.success("✨ 文案生成完毕！您可以直接阅读、复制或下载。")

    # 按钮并排布局
    col1, col2 = st.columns(2)
    with col1:
        # 下载按钮：直接把内存里的字符串转为文本文件供浏览器下载
        st.download_button(
            label="📥 下载 Markdown 文件",
            data=st.session_state["generated_content"],
            file_name="WeChat_Weekly_Review.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        st.info("💡 提示：双击上方文本框内容，即可直接 Ctrl+C 复制全文。")

    # 免责声明
    st.markdown("""
    <p style='color: gray; font-size: 0.8rem; text-align: center; margin-top: 50px;'>
    ⚠️ 免责声明：本工具生成的文献速览内容均由第三方大模型自动提炼，仅供学术交流与参考，发布前请核对原始 DOI 文献。
    </p>
    """, unsafe_allow_html=True)
