import streamlit as st
import google.generativeai as genai
import re
import os

# Configure Gemini client
#genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
genai.configure(api_key="")

# Page setup
st.set_page_config(page_title="AI Code Explainer", page_icon="🚀")
st.title("Real-Time Code Explainer with Gemini")

# Session state management
if "history" not in st.session_state:
    st.session_state.history = []

# UI Components
with st.sidebar:
    st.header("Settings")
    language = st.selectbox("Programming Language", 
                          ["Auto-Detect", "Python", "Java", "C++", "JavaScript", "C#"])
    explanation_mode = st.radio("Explanation Type", 
                              ["Summary", "Detailed Line-by-Line"])

# Main interface
code_input = st.text_area("Paste your code here", height=300, key="code_input")

# System prompt engineering for Gemini
SYSTEM_PROMPT = """You are a senior {language} developer explaining code to beginners.
Provide a {mode} explanation of this code:
{code}
{format_instructions}"""

def generate_explanation(code, language, mode):
    format_instructions = ("Break down each line with: 1. Purpose 2. Key Operations 3. Edge Cases" 
                          if mode == "Detailed Line-by-Line" else 
                          "Provide: 1. Overall Functionality 2. Key Algorithms 3. Complexity Analysis")
    
    if language == "Auto-Detect":
        language = detect_programming_language(code)
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = SYSTEM_PROMPT.format(
        language=language,
        mode=mode.lower(),
        code=code,
        format_instructions=format_instructions
    )
    
    try:
        response = model.generate_content(
            prompt,
            stream=True,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2048
            )
        )
        return response
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

def detect_programming_language(code):
    patterns = {
        "Python": r"(def |print|import numpy|#)",
        "Java": r"(public class|System.out.println|import java.)",
        "C++": r"(#include|using namespace|std::)",
        "JavaScript": r"(function|console.log|=>)",
        "C#": r"(using System|Console.WriteLine|namespace)"
    }
    
    for lang, pattern in patterns.items():
        if re.search(pattern, code):
            return lang
    return "Python"

# Explanation generation
if st.button("Explain Code"):
    if code_input.strip():
        with st.spinner("🧠 Analyzing code with Gemini..."):
            explanation_stream = generate_explanation(
                code_input, language, explanation_mode
            )
            
            if explanation_stream:
                explanation_container = st.empty()
                full_response = ""
                
                for chunk in explanation_stream:
                    if chunk.text:
                        full_response += chunk.text
                        explanation_container.markdown(full_response + "▌")
                
                explanation_container.markdown(full_response)
                st.session_state.history.append({
                    "code": code_input,
                    "explanation": full_response,
                    "language": language
                })

# History display
st.subheader("Explanation History")
for entry in reversed(st.session_state.history):
    with st.expander(f"{entry['language']} code - {len(entry['code'])} chars"):
        st.code(entry["code"], language=entry['language'].lower())
        st.markdown("*Explanation*")
        st.write(entry["explanation"])
