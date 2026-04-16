import streamlit as st
import requests
import time

st.set_page_config(page_title="MARIO VIDEO FACTORY", layout="wide")

# --- 像素清新风格 ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #87CEEB 70%, #4CAF50 100%); }
    h1 { color: #FFD700; text-shadow: 3px 3px #000; }
    .stButton>button { background-color: #2ECC71 !important; color: white !important; border-radius: 10px !important; }
    .video-box { border: 5px solid #2C3E50; border-radius: 15px; padding: 10px; background: #fff; }
    </style>
""", unsafe_allow_html=True)

st.title("🍄 超级马里奥视频工厂")

api_key = st.sidebar.text_input("🔑 ToAPIs Key:", type="password")

# 任务列表初始化
if 'tasks' not in st.session_state:
    st.session_state.tasks = [{"id": None, "status": "idle", "url": None} for _ in range(10)]

tabs = st.tabs([f"管道 {i+1}" for i in range(10)])

for i, tab in enumerate(tabs):
    with tab:
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.form(f"f_{i}"):
                prompt = st.text_area("✍️ 描述:", key=f"p_{i}")
                img_url = st.text_input("🖼️ 图片链接:", key=f"img_{i}")
                ratio = st.selectbox("📏 比例:", ["16:9", "9:16", "1:1", "3:2", "2:3"], key=f"r_{i}")
                qual = st.selectbox("💎 质量:", ["480p", "720p"], key=f"q_{i}")
                if st.form_submit_button("🚀 发射！"):
                    res = requests.post("https://toapis.com/v1/videos/generations",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": "grok-imagine-1.0-video", "prompt": prompt, "image_urls": [img_url] if img_url else [], 
                              "aspect_ratio": ratio, "quality": qual})
                    if "id" in res.json():
                        st.session_state.tasks[i] = {"id": res.json()['id'], "status": "queued", "url": None}
        
        with col2:
            st.markdown('<div class="video-box">', unsafe_allow_html=True)
            t = st.session_state.tasks[i]
            if t["id"]:
                if t["status"] != "completed":
                    st.info(f"状态: {t['status']} ...采蘑菇中")
                    # 自动查询逻辑
                    res = requests.get(f"https://toapis.com/v1/videos/generations/{t['id']}", headers={"Authorization": f"Bearer {api_key}"})
                    data = res.json()
                    t["status"] = data.get("status")
                    if t["status"] == "completed": t["url"] = data.get("video_url")
                else:
                    st.video(t["url"])
                    st.markdown(f'<a href="{t["url"]}" download="mario.mp4">📥 下载视频</a>', unsafe_allow_html=True)
            else:
                st.write("等待发射...")
            st.markdown('</div>', unsafe_allow_html=True)

# 自动刷新页面保持状态
if st.button("🔄 刷新任务状态"): st.rerun()
