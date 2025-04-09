# import pip
# pip.main(['install', 'groq', 'streamlit_markmap'])

import streamlit as st
from groq import Groq
from streamlit_markmap import markmap

# Set up the app
st.title("🧠 Text to Mindmap with Groq")
st.caption("Using deepseek-r1-distill-llama-70b model")

# API key handling
if "api_key" not in st.session_state:
    st.session_state.api_key = None

# Try to get API key from secrets first
api_key = st.secrets.get("GROQ_API_KEY", None)

# If not in secrets, check if it's already in session state
if not api_key and st.session_state.api_key:
    api_key = st.session_state.api_key

# If still no API key, prompt user to enter one
if not api_key:
    user_api_key = st.text_input("Enter your Groq API Key:", type="password")
    if user_api_key:
        api_key = user_api_key
        st.session_state.api_key = api_key

# Initialize Groq client if API key is available
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
        st.success("Connected to Groq API successfully!")
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {str(e)}")

# Text processing function
def generate_mindmap_content(text):
    if not client:
        st.error("Groq client not initialized. Please provide a valid API key.")
        return None
        
    system_prompt = """Convert this text into a hierarchical markdown list for a mindmap.
    Use exactly 3 levels maximum with this format:
    
    # Main Concept
    - Primary Topic
      - Secondary Detail
      - Another Detail
    - Another Primary Topic
    """
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.6,
            max_tokens=4096,
            top_p=0.95,
            stream=False  # Disable streaming for this implementation
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# Main app interface
with st.form("mindmap_form"):
    input_text = st.text_area("Enter text to convert to mindmap:", height=200)
    submitted = st.form_submit_button("Generate Mindmap")

if submitted and input_text:
    if not client:
        st.error("Please provide a valid Groq API key first.")
    else:
        with st.spinner("Generating mindmap structure..."):
            markdown_output = generate_mindmap_content(input_text)
            
            if markdown_output:
                st.subheader("Interactive Mindmap")
                # Configure markmap with white background
                markmap(markdown_output, 
                        height=500,
                        config={
                            
                            "background": "#ffffff"
                        })
                
                with st.expander("View Raw Markdown"):
                    st.code(markdown_output, language="markdown")

# Sidebar with model info
with st.sidebar:
    st.markdown("### Model Configuration")
    st.code("""Model: deepseek-r1-distill-llama-70b
Temperature: 0.6
Max Tokens: 4096
Top-P: 0.95""")
    
    st.markdown("### Tips")
    st.markdown("- Keep input text under 2000 words")
    st.markdown("- Use clear, structured content")
    st.markdown("- Refresh if timeout occurs")
