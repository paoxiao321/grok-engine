import streamlit as st
import requests
import time
import base64

# --- 1. 网页全局设置（宽屏模式，适合多窗口） ---
st.set_page_config(page_title="Grok 视频工厂", page_icon="🎬", layout="wide")

st.title("🎬 Grok 专业视频生成工作台")

# --- 2. 左侧边栏：安全填写 API Key ---
with st.sidebar:
    st.header("⚙️ 全局设置")
    api_key = st.text_input("🔑 请输入你的 Grok API Key:", type="password")
    st.info("💡 你的 Key 仅在本次网页运行时有效，刷新页面后会自动清除，绝对安全，不会泄露给任何人。")

# --- 3. 核心功能：发送请求并循环查询进度的函数 ---
def process_video_task(api_key, prompt, image_bytes, duration, aspect_ratio):
    """
    这是一个通用的异步视频生成请求逻辑：先提交任务，再循环查进度。
    ⚠️ 注意：下面的 URL 和字段名需要根据你的具体 API 文档进行微调！
    """
    submit_url = "https://api.x.ai/v1/video/generate"  # 1. 提交任务的接口地址
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 组合发送给 API 的数据
    payload = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio
    }
    
    # 如果上传了图片，转换成 Base64 编码发给 API
    if image_bytes:
        payload["image_base64"] = base64.b64encode(image_bytes).decode('utf-8')
        
    try:
        # 第一步：向接口提交生成任务
        response = requests.post(submit_url, headers=headers, json=payload)
        if response.status_code != 200:
            return None, f"接口拒绝访问 (错误码 {response.status_code}): {response.text}"
            
        task_data = response.json()
        task_id = task_data.get("task_id") # 获取任务流水号
        
        if not task_id:
            # 如果接口直接返回了视频链接（不需要排队等待），直接在这里返回
            if task_data.get("video_url"):
                return task_data.get("video_url"), None
            return None, f"未能获取到任务ID，接口返回内容: {task_data}"
            
        # 第二步：带着任务流水号，每隔 5 秒去查询一次有没有做完
        status_url = f"https://api.x.ai/v1/video/status/{task_id}" # 2. 查询进度的接口地址
        
        for _ in range(60): # 最多等 60 次 * 5 秒 = 5 分钟
            time.sleep(5) # 暂停 5 秒再查，防止被接口封号
            
            res = requests.get(status_url, headers=headers)
            if res.status_code != 200:
                continue
                
            status_data = res.json()
            status = status_data.get("status") # 获取当前状态
            
            if status == "completed" or status == "success":
                video_url = status_data.get("video_url") # 成功！提取视频链接
                return video_url, None
            elif status == "failed" or status == "error":
                return None, "生成失败，可能是提示词违规或服务器繁忙。"
                
        return None, "生成超时（超过5分钟未完成），请稍后再试。"
        
    except Exception as e:
        return None, f"代码运行发生错误: {str(e)}"

# --- 4. 构建多窗口用户界面 ---
# 创建 3 个并行的工作区标签页
tabs = st.tabs(["🖥️ 任务窗口 1", "🖥️ 任务窗口 2", "🖥️ 任务窗口 3"])

# 为每个标签页生成相同的操作界面，但数据互相独立
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"任务 {i+1} 设置区")
        
        # 使用表单锁定输入，只有点击提交按钮才会运行
        with st.form(f"video_form_{i}"):
            # 输入提示词
            prompt = st.text_area("✍️ 提示词 (Prompt)", height=100, placeholder="描述你想生成的视频画面...", key=f"prompt_{i}")
            
            # 上传参考图
            uploaded_file = st.file_uploader("🖼️ 上传参考图 (选填，支持 JPG/PNG)", type=['jpg', 'png', 'jpeg'], key=f"image_{i}")
            
            # 高级参数设置 (分成两列显示)
            col1, col2 = st.columns(2)
            with col1:
                duration = st.slider("⏱️ 视频时长 (秒)", min_value=2, max_value=10, value=5, key=f"duration_{i}")
            with col2:
                aspect = st.selectbox("📏 画面比例", ["16:9 (横屏)", "9:16 (竖屏)", "1:1 (正方形)"], key=f"aspect_{i}")
            
            # 提交按钮
            submit_btn = st.form_submit_button("🚀 开始生成任务", type="primary")

        # --- 5. 点击生成按钮后的执行逻辑 ---
        if submit_btn:
            if not api_key:
                st.error("❌ 请先在左侧边栏输入你的 API Key！")
            elif not prompt:
                st.warning("⚠️ 提示词不能为空！请告诉 Grok 你想画什么。")
            else:
                # 显示加载动画
                with st.spinner(f"任务 {i+1} 正在向 Grok 服务器排队并渲染中，请耐心等待（约需几分钟）..."):
                    # 如果有图片，转成字节流
                    img_bytes = uploaded_file.getvalue() if uploaded_file else None
                    
                    # 剥离比例里的文字，只留 16:9
                    clean_aspect = aspect.split(" ")[0] 
                    
                    # 调用上面的核心函数
                    video_url, error_msg = process_video_task(api_key, prompt, img_bytes, duration, clean_aspect)
                    
                    # 展示结果
                    if video_url:
                        st.success("✅ 视频生成成功！")
                        st.video(video_url)
                    else:
                        st.error(f"❌ 任务失败: {error_msg}")
