import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. Page Configuration (Optimized for Mobile/Tablet Screens)
st.set_page_config(page_title="Sopala AI: Ghanaian Teacher Assistant", page_icon="🇬🇭", layout="centered")

# --- INTEGRATED MOODLEBOX SIDEBAR COMPONENT ---
with st.sidebar:
    st.image("https://icons8.com", width=60)
    st.markdown("## 🍓 MoodleBox Offline Hub")
    st.info("Use this tracking checklist to deploy your online resources offline in the classroom.")
    
    st.markdown("### 📋 Classroom Workflow Checklist")
    st.checkbox("Step 1: Generate resource online.", value=False)
    st.checkbox("Step 2: Click the 'Download Text File' button below.", value=False)
    st.checkbox("Step 3: Connect phone to school 'MoodleBox' Wi-Fi.", value=False)
    st.checkbox("Step 4: Go to http://moodlebox.home completely data-free.", value=False)
    st.checkbox("Step 5: Upload the text file to your Moodle Course block.", value=False)
    
    st.markdown("---")
    st.markdown("### 🛠️ Local Server Access Parameters")
    st.caption("Default Admin Username: **moodlebox**")
    st.caption("Default Admin Password: **MoodleBox4$**")
    st.caption("Default Wifi  Password: **moodlebox**")

# --- MAIN APP USER INTERFACE ---
st.title("🇬🇭 Sopala AI")
st.subheader("Context-Aware Lesson Planner & Teaching Assistant")
st.caption("Powered by Gemini 3.5 Flash-Lite & Grounded in GES Curriculum Standards")


# 2. Secure Developer API Key Field
api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

# 3. Retrieval-Augmented Generation (RAG) Local PDF Parser
def load_local_knowledge():
    combined_text = ""
    folder_path = "knowledge_base"
    
    # Custom pipeline fallback: scans subfolders AND the main directory if files are loose
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(folder_path, filename))
                    for page in reader.pages:
                        combined_text += page.extract_text() + "\n"
                except Exception as e:
                    pass
                    
    # Secondary pipeline check if PDFs were uploaded loosely outside the folder
    for filename in os.listdir("."):
        if filename.endswith(".pdf"):
            try:
                reader = PdfReader(filename)
                for page in reader.pages:
                    combined_text += page.extract_text() + "\n"
            except Exception as e:
                pass
                
    return combined_text[:30000] # Throttled baseline context parameter size

with st.spinner("Loading local curriculum guidelines..."):
    local_curriculum_context = load_local_knowledge()

# 4. Interactive Teacher Parameter Inputs Form
st.markdown("### Step 1: Lesson Details")
col1, col2 = st.columns(2)
with col1:
        subject = st.selectbox("Subject", [
        "Natural Science (Primary)", 
        "Mathematics (Primary)", 
        "English Language (Primary)", 
        "Our World Our People (OWOP)", 
        "Religious & Moral Education (RME - Primary)", 
        "Dagbani Literacy (Primary)",
        "Mathematics (JHS)", 
        "English Language (JHS)", 
        "Science (JHS)", 
        "Social Studies (JHS)", 
        "Religious and Moral Education (RME - JHS)", 
        "Ghanaian Language (JHS)", 
        "Career Technology (JHS)", 
        "Creative Art and Design (JHS)", 
        "Computing (JHS)"
    ])

with col2:
    class_level = st.selectbox("Class Level", ["KG 1", "KG 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6", "JHS 1", "JHS 2", "JHS 3"])

topic = st.text_input("What specific topic are you teaching today?", placeholder="e.g., Sources of Water")

st.markdown("### Step 2: Custom Instructions")
output_type = st.radio("What do you want the AI to generate?", ["Complete GES Lesson Plan Outline", "Low-Resource Classroom Activities (Using local materials)", "Dagbani Reading Passage & Vocabulary Drill"])

# 5. Core Processing & Prompt Engineering Engine
if st.button("Generate Resource ✨"):
    if not api_key:
        st.error("Please enter your Google API Key above to proceed.")
    elif not topic:
        st.error("Please enter a topic.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash-lite')

        
        prompt = f"""
        You are an expert curriculum designer for the Ghana Education Service (GES) specializing in Basic Education in Northern Ghana.
        Your task is to create a highly accurate, structured educational resource based on the parameters requested.

        CONSTRAINTS & LOCALIZED NORTHERN GHANA CONTEXT:
        - Only suggest classroom experiments, teaching aids, and learning materials that utilize cheap, locally available resources found in Tamale or surrounding rural northern schools (e.g., empty plastic bottles, cardboard scrap, local plants, pebbles, local clay). Do not assume access to standard laboratory equipment, commercial kits, or reliable grid electricity.
        - Ensure all pedagogical structures and headings align exactly with the standard GES template (Rationale, Indicators, Core Competencies, Phase 1: Starter/Warm-up, Phase 2: Main Activity/Teacher-Learner Activities, Phase 3: Plenary/Reflection).
        
        REFERENCE CURRICULUM GROUNDING DATA:
        Use the following text extracted from official curriculum guidelines and organization context books to ground your generation:
        {local_curriculum_context}

        REQUEST PARAMETERS:
        Subject: {subject}
        Class Level: {class_level}
        Topic: {topic}
        Requested Resource Format: {output_type}

        Please deliver a highly professional, practical output. If generating a reading passage or vocabulary drill in Dagbani, ensure strict adherence to proper orthography and grammatical rules.
        """
        
        with st.spinner("Sopala AI is structuring your request..."):
            try:
                response = model.generate_content(prompt)
                st.markdown("### 📝 Generated Resource")
                st.write(response.text)
                st.download_button("Download Text File", response.text, file_name=f"{topic.replace(' ', '_')}_resource.txt")
            except Exception as e:
                st.error(f"An error occurred: {e}")


