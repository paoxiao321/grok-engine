import streamlit as st
import requests
import time

# --- 像素风 UI ---
st.set_page_config(page_title="SUPER GROK BROS", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    html, body, [class*="css"] { font-family: 'Press Start 2P', cursive; }
    .stApp { background-color: #5c94fc; }
    button { background-color: #e74c3c !important; color: white !important; border: 4px solid #000 !important; }
    h1 { color: #f1c40f !important; text-shadow: 3px 3px #000; }
    </style>
""", unsafe_allow_html=True)

st.title("🍄 SUPER GROK BROS 视频工厂")

api_key = st.sidebar.text_input("🔑 ToAPIs Key:", type="password")

# --- 10 窗口 ---
tabs = st.tabs([f"🍄 任务 {i+1}" for i in range(10)])

for i, tab in enumerate(tabs):
    with tab:
        with st.form(f"f_{i}"):
            prompt = st.text_area("✍️ 视频描述:", key=f"p_{i}")
            # 这里输入图片链接，换行分隔
            img_urls_text = st.text_area("🖼️ 参考图链接 (一行一个，最多7个):", key=f"img_{i}", help="粘贴公网图片链接，如刚才那个链接")
            
            col1, col2 = st.columns(2)
            duration = col1.number_input("⏱️ 时长(6-30s):", 6, 30, 6, key=f"dur_{i}")
            quality = col2.selectbox("💎 质量:", ["480p", "720p"], key=f"q_{i}")
            submitted = st.form_submit_button("🚀 投币开始！")

        if submitted:
            if not api_key: 
                st.error("请先输入 API Key！")
            else:
                # 转换图片链接为数组
                img_list = [url.strip() for url in img_urls_text.split('\n') if url.strip()]
                
                payload = {
                    "model": "grok-imagine-1.0-video",
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "duration": int(duration),
                    "quality": quality
                }
                if img_list:
                    payload["image_urls"] = img_list[:7] # 最多限制7张

                # 发送请求
                try:
                    res = requests.post(
                        "https://toapis.com/v1/videos/generations",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json=payload
                    )
                    data = res.json()
                    if "id" in data:
                        st.success(f"✅ 任务提交成功！ID: {data['id']}")
                        st.info("正在后台生成，请记录任务ID以备后续查询。")
                    else:
                        st.error(f"❌ 失败: {data}")
                except Exception as e:
                    st.error(f"⚠️ 错误: {e}")
