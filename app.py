import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import time
import os


st.set_page_config(
    page_title="Gemini 3: Omni-Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
    }
    .reportview-container {
        background: #0E1117;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Gemini 3: Omni-Analyst")
st.markdown("### The Multimodal Reasoning Engine")



with st.sidebar:
    st.header("System Settings")
    
    if "GEMINI_API_KEY" in st.secrets:
        st.success("✅ API Key Loaded from Secrets")
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # If no secret found (e.g. for the user), ask for it
        api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    
    mode = st.radio("Select Mode:", ["⚡ Fast Analysis", "🕵️ Sherlock (Deep Reasoning)"])
    enable_audio = st.toggle("Enable Audio Report", value=True)
    
    st.info("ℹ️ **Sherlock Mode** forces the model to think step-by-step before answering. Best for complex problems.")


if not api_key:
    st.warning("🔒 Please enter your API Key in the sidebar to activate the Neural Engine.")
    st.stop()


genai.configure(api_key=api_key)


tab1, tab2 = st.tabs(["📷 Image Analysis", "🎥 Video Analysis (Beta)"])


with tab1:
    uploaded_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        col1, col2 = st.columns([1, 1])
        with col1:
            image = Image.open(uploaded_img)
            st.image(image, caption="Input Data", use_column_width=True)
        
        with col2:
            st.markdown("### 🔍 Analysis Options")
            user_prompt = st.text_area("Specific Question (Optional):", placeholder="e.g., Is this wiring safe? What breed is this?")
            
            if st.button("🚀 Analyze Image"):
                with st.spinner("Processing Multimodal Data..."):
                    try:
                        
                        model_name = 'gemini-3-flash-preview' # Using your preview model
                        model = genai.GenerativeModel(model_name)
                        
                        
                        if mode == "🕵️ Sherlock (Deep Reasoning)":
                            final_prompt = f"Perform a deep reasoning analysis. First, list your OBSERVATIONS. Second, perform a SAFETY CHECK. Third, answer this user question: {user_prompt}. Finally, provide a CONCLUSION."
                        else:
                            final_prompt = f"Analyze this image. User question: {user_prompt}"

                        
                        response = model.generate_content([final_prompt, image])
                        
                       
                        st.success("Analysis Complete")
                        
                        
                        if mode == "🕵️ Sherlock (Deep Reasoning)":
                            with st.expander("🧠 View Reasoning Logic (Chain-of-Thought)", expanded=True):
                                st.write(response.text)
                        else:
                            st.write(response.text)
                            
                    
                        if enable_audio:
                            tts = gTTS(text=response.text[:200] + "...", lang='en') 
                            tts.save("report.mp3")
                            st.audio("report.mp3")
                            
                    except Exception as e:
                        st.error(f"Error: {e}")


with tab2:
    st.info("📝 Note: Video analysis works best with short clips (< 1 minute).")
    uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mov"])
    
    if uploaded_video:
        st.video(uploaded_video)
        
        if st.button("🎬 Analyze Video"):
            with st.spinner("Uploading video to Gemini Cloud (This may take a moment)..."):
                try:
                    
                    with open("temp_video.mp4", "wb") as f:
                        f.write(uploaded_video.read())
                    
       
                    video_file = genai.upload_file(path="temp_video.mp4")
                    
              
                    while video_file.state.name == "PROCESSING":
                        time.sleep(2)
                        video_file = genai.get_file(video_file.name)

                    if video_file.state.name == "FAILED":
                        st.error("Video processing failed.")
                    else:
                        st.success("Video Processed! Generating Insights...")
                        model = genai.GenerativeModel('gemini-1.5-pro-latest') # Pro is better for video
                        
                        prompt = "Watch this video carefully. Describe the action, the setting, and any key events effectively."
                        response = model.generate_content([prompt, video_file])
                        
                        st.markdown("### 🎬 Video Insights")
                        st.write(response.text)
                        
                except Exception as e:
                    st.error(f"Error: {e}")