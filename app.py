import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="Sopala AI: Ghanaian Teacher Assistant", page_icon="🇬🇭", layout="centered")
st.title("🇬🇭 Sopala AI")
st.subheader("Context-Aware Lesson Planner & Teaching Assistant")
st.caption("Powered by Gemini 1.5 Flash & Grounded in GES Curriculum Standards")

api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

def load_local_knowledge():
    combined_text = ""
    folder_path = "knowledge_base"
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(folder_path, filename))
                    for page in reader.pages:
                        combined_text += page.extract_text() + "\n"
                except Exception as e:
                    pass
    return combined_text[:30000]

with st.spinner("Loading local curriculum guidelines..."):
    local_curriculum_context = load_local_knowledge()

st.markdown("### Step 1: Lesson Details")
col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("Subject", ["Natural Science", "Mathematics", "English Language", "Our World Our People (OWOP)", "Religious & Moral Education (RME)", "Dagbani Literacy"])
with col2:
    class_level = st.selectbox("Class Level", ["KG 1", "KG 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6", "JHS 1", "JHS 2", "JHS 3"])

topic = st.text_input("What specific topic are you teaching today?", placeholder="e.g., Sources of Water")

st.markdown("### Step 2: Custom Instructions")
output_type = st.radio("What do you want the AI to generate?", ["Complete GES Lesson Plan Outline", "Low-Resource Classroom Activities (Using local materials)", "Dagbani Reading Passage & Vocabulary Drill"])

if st.button("Generate Resource ✨"):
    if not api_key:
        st.error("Please enter your Google API Key above to proceed.")
    elif not topic:
        st.error("Please enter a topic.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert curriculum designer for the Ghana Education Service (GES) specializing in Basic Education in Northern Ghana.
        
        CONSTRAINTS & CONTEXT FOR NORTHERN GHANA:
        - Only suggest classroom experiments and teaching aids that utilize cheap, locally available resources found in Tamale or rural northern schools (e.g., plastic bottles, cardboard, local plants, pebbles, clay). Do not assume access to laboratory equipment or reliable electricity.
        - Ensure pedagogical terms align with the GES standard structures (Rationale, Indicators, Core Competencies, Teacher-Learner Activities).
        
        REFERENCE CURRICULUM DATA:
        {local_curriculum_context}

        REQUEST DETAILS:
        Subject: {subject}
        Class Level: {class_level}
        Topic: {topic}
        Requested Resource Format: {output_type}
        """
        
        with st.spinner("Sopala AI is structuring your request..."):
            try:
                response = model.generate_content(prompt)
                st.markdown("### 📝 Generated Resource")
                st.write(response.text)
                st.download_button("Download Text File", response.text, file_name=f"{topic.replace(' ', '_')}_resource.txt")
            except Exception as e:
                st.error(f"An error occurred: {e}")
