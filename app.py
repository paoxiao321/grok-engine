import streamlit as st
import requests

st.set_page_config(page_title="MARIO VIDEO FACTORY", layout="wide")

# --- 像素清新风格 ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #87CEEB 70%, #4CAF50 100%); }
    h1 { color: #FFD700; text-shadow: 3px 3px #000; text-align: center; }
    .video-container { 
        border: 8px solid #2C3E50; 
        border-radius: 15px; 
        padding: 15px; 
        background: #f0f0f0; 
        min-height: 400px; 
        display: flex; 
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍄 超级马里奥视频工厂")

api_key = st.sidebar.text_input("🔑 ToAPIs Key:", type="password")

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
                duration = st.number_input("⏱️ 时长(秒):", 6, 30, 10, key=f"dur_{i}")
                ratio = st.selectbox("📏 比例:", ["16:9", "9:16", "1:1", "3:2", "2:3"], key=f"r_{i}")
                qual = st.selectbox("💎 质量:", ["480p", "720p"], key=f"q_{i}")
                
                if st.form_submit_button("🚀 发射！"):
                    payload = {
                        "model": "grok-imagine-1.0-video",
                        "prompt": prompt,
                        "image_urls": [img_url] if img_url else [],
                        "aspect_ratio": ratio,
                        "quality": qual,
                        "duration": int(duration)
                    }
                    res = requests.post("https://toapis.com/v1/videos/generations",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json=payload)
                    
                    if "id" in res.json():
                        st.session_state.tasks[i] = {"id": res.json()['id'], "status": "queued", "url": None}
                        st.rerun()
                    else:
                        st.error(f"❌ 错误: {res.text}")
        
        with col2:
            st.markdown("### 📺 视频预览框")
            # 使用容器包裹视频区域
            with st.container(border=True):
                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                
                t = st.session_state.tasks[i]
                if t["id"]:
                    # 查询状态
                    res = requests.get(f"https://toapis.com/v1/videos/generations/{t['id']}", 
                                      headers={"Authorization": f"Bearer {api_key}"})
                    data = res.json()
                    t["status"] = data.get("status", "unknown")
                    
                    if t["status"] == "completed":
                        t["url"] = data.get("video_url")
                        st.video(t["url"])
                        st.markdown(f'<a href="{t["url"]}" download="mario_video.mp4">💾 下载视频</a>', unsafe_allow_html=True)
                    else:
                        # 状态提示强制显示在预览框中心
                        st.warning(f"当前状态: {t['status']} ... 正在采蘑菇 🍄")
                        st.progress(0.5) # 给个加载条
                else:
                    st.write("管道是空的，快去左边发射任务！")
                
                st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔄 刷新所有任务"): st.rerun()
