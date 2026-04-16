import streamlit as st
import requests

# --- 清新马里奥风格 UI ---
st.set_page_config(page_title="🍄 超级马里奥视频工厂", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&display=swap');
    body { font-family: 'Ma Shan Zheng', cursive; background-color: #87CEEB !important; }
    .stApp { background-color: #87CEEB !important; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 2px 2px #E74C3C; text-align: center; }
    .stButton>button { background-color: #FF6B6B !important; color: white !important; border-radius: 20px !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🍄 超级马里奥视频工厂")

# --- 侧边栏 ---
with st.sidebar:
    st.subheader("⚙️ 投币设置")
    api_key = st.text_input("🔑 ToAPIs Key:", type="password")

# --- 主界面 ---
tab1, tab2 = st.tabs(["🚀 生成视频", "🔍 领取视频"])

with tab1:
    with st.form("gen_form"):
        prompt = st.text_area("✍️ 告诉马里奥你想看什么画面:")
        img_urls = st.text_area("🖼️ 图片链接 (最多7个,换行分隔):")
        duration = st.slider("⏱️ 时长(秒):", 6, 30, 6)
        submitted = st.form_submit_button("🚀 投币出发！")

    if submitted and api_key:
        img_list = [u.strip() for u in img_urls.split('\n') if u.strip()]
        res = requests.post("https://toapis.com/v1/videos/generations",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "grok-imagine-1.0-video", "prompt": prompt, "image_urls": img_list[:7], "duration": duration})
        st.success(f"✅ 任务 ID 已获取: {res.json().get('id')}")

with tab2:
    check_id = st.text_input("请输入任务 ID:")
    if st.button("🔍 检查进度"):
        res = requests.get(f"https://toapis.com/v1/videos/generations/{check_id}", 
                           headers={"Authorization": f"Bearer {api_key}"})
        data = res.json()
        status = data.get("status")
        st.write(f"当前状态: {status}")
        
        if status == "completed":
            v_url = data.get("video_url")
            st.video(v_url)
            # 下载按钮
            st.markdown(f'<a href="{v_url}" download="mario_video.mp4"><button style="background:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:10px;">💾 点击下载视频</button></a>', unsafe_allow_html=True)
        elif status == "failed":
            st.error("❌ 任务失败，请检查提示词或图片链接。")
        else:
            st.warning("⏳ 还在努力采蘑菇中，请稍后再查！")
