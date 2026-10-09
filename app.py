import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

# 1. Page Configuration (Optimized for Mobile/Tablet Screens)
st.set_page_config(page_title="RLS Teacher Hub: Ghanaian Teacher Assistant", page_icon="🇬🇭", layout="centered")

# --- INTEGRATED MOODLEBOX SIDEBAR COMPONENT ---
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown("## 🍓 MoodleBox Offline Hub")
    st.info("Use this tracking checklist to deploy your online resources offline in the classroom.")
    
    st.checkbox("Step 1: Paste API Key & choose task.", value=False)
    st.checkbox("Step 2: Choose layout style format.", value=False)
    st.checkbox("Step 3: Click the 'Download Word Document' button below.", value=False)
    st.checkbox("Step 4: Connect phone to school 'MoodleBox' Wi-Fi.", value=False)
    st.checkbox("Step 5: Go to http://moodlebox.home data-free.", value=False)
    st.checkbox("Step 6: Upload the Word file to your Moodle Course block.", value=False)
    
    st.markdown("---")
    st.markdown("### 🛠️ Local Server Access Parameters")
    st.caption("Default Admin Username: **admin**")
    st.caption("Default Admin Password: **MoodleBox4$**")
    st.caption("Framework maintained by **Rural Literacy Solutions (RLS)**")

# --- MAIN APP USER INTERFACE ---
st.title("🇬🇭 RLS Teacher Hub")
st.subheader("Context-Aware Lesson Planner & Teaching Assistant")
st.caption("Powered by RLS Teacher Hub Core Engine & Grounded in GES Curriculum Standards")

# 2. Secure Developer API Key Field
api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

# 3. Retrieval-Augmented Generation (RAG) Local PDF Parser with Caching Fix
@st.cache_resource
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
                    
    for filename in os.listdir("."):
        if filename.endswith(".pdf"):
            try:
                reader = PdfReader(filename)
                for page in reader.pages:
                    combined_text += page.extract_text() + "\n"
            except Exception as e:
                pass
                
    return combined_text[:30000]

with st.spinner("Loading local curriculum guidelines..."):
    local_curriculum_context = load_local_knowledge()

# --- STEP 1: CHOOSE TARGET OUTPUT ---
st.markdown("### Step 1: What do you want to create today?")
output_type = st.radio("Select an option:", [
    "Complete GES Lesson Plan Outline", 
    "Low-Resource Classroom Activities (Using local materials)", 
    "Dagbani Reading Passage & Vocabulary Drill",
    "Brand-New Dagbani Story (Based on uploaded storybook characters & vocabulary levels)"
])

st.markdown("---")
st.markdown("### Step 2: Resource Parameters")

# --- SMART CONDITIONAL INTERFACE LOGIC ---
if output_type == "Brand-New Dagbani Story (Based on uploaded storybook characters & vocabulary levels)":
    subject = "Dagbani Literacy (Primary)"
    st.success("📝 **Story Mode Active:** The app will automatically ground this creation in your uploaded Dagbani children's books.")
    
    col1, col2 = st.columns(2)
    with col1:
        class_level = st.selectbox("Reading Level / Class", ["KG 1", "KG 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6"])
    with col2:
        topic = st.text_input("Describe your story idea or moral lesson:", placeholder="e.g., A story about Sana helping her mother pick shea nuts near Tamale")
    layout_style = "Standard Text Block Layout"
else:
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Subject", [
            "Natural Science (Primary)", "Mathematics (Primary)", "English Language (Primary)", 
            "Our World Our People (OWOP)", "Religious & Moral Education (RME - Primary)", "Dagbani Literacy (Primary)",
            "Mathematics (JHS)", "English Language (JHS)", "Science (JHS)", "Social Studies (JHS)", 
            "Religious and Moral Education (RME - JHS)", "Ghanaian Language (JHS)", "Career Technology (JHS)", 
            "Creative Art and Design (JHS)", "Computing (JHS)"
        ])
    with col2:
        class_level = st.selectbox("Class Level", ["KG 1", "KG 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6", "JHS 1", "JHS 2", "JHS 3"])
        
    topic = st.text_input("What specific curriculum topic are you teaching today?", placeholder="e.g., Sources of Water, Photosynthesis, Fractions")
    
    st.markdown("### Step 3: Select Document Layout Format")
    layout_style = st.radio("Choose layout template style:", ["Standard Text Block Layout", "Official NaCCA Standard Table Template Grid"])


# Clean, error-proof function to safely generate standard Word files
def convert_to_docx(title_text, content_text):
    doc = Document()
    doc.add_heading(title_text, level=1)
    
    for line in content_text.split('\n'):
        if line.strip().startswith("###"):
            doc.add_heading(line.replace("###", "").strip(), level=3)
        elif line.strip().startswith("##"):
            doc.add_heading(line.replace("##", "").strip(), level=2)
        elif line.strip().startswith("#"):
            doc.add_heading(line.replace("#", "").strip(), level=1)
        else:
            doc.add_paragraph(line)
            
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# 5. Core Processing & Prompt Engineering Engine
if st.button("Generate Resource ✨"):
    if not api_key:
        st.error("Please enter your Google API Key above to proceed.")
    elif not topic:
        st.error("Please provide details in the parameter text box.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash-lite')
        
        if layout_style == "Official NaCCA Standard Table Template Grid":
            layout_instruction = """Format the entire lesson plan output as a clean text-based table matrix using markdown borders. Use columns for 'Phase / Duration', 'Learner Activities', and 'Resources / TLMs'. Make sure to include row sections for Phase 1: Starter, Phase 2: Main, and Phase 3: Plenary matching official NaCCA guidelines."""
        else:
            layout_instruction = "Render standard markdown headings and paragraph lists to structure the output content."

        prompt = f"""
        You are an expert curriculum designer for the Ghana Education Service (GES), NaCCA standards tracking boards, and a master storyteller specializing in Dagbani literacy for Basic Education in Northern Ghana.
        Your task is to create a highly accurate, structured educational resource based on the parameters requested.

        LAYOUT RULE REQUIREMENTS:
        {layout_instruction}

        CONSTRAINTS & LOCALIZED NORTHERN GHANA CONTEXT:
        - Only suggest classroom experiments, teaching aids, and learning materials that utilize cheap, locally available resources found in Tamale or surrounding rural northern schools (e.g., empty plastic bottles, cardboard scrap, local plants, pebbles, local clay). Do not assume access to standard laboratory equipment, commercial kits, or reliable grid electricity.
        - Ensure all pedagogical structures and headings align exactly with the standard GES template (Rationale, Indicators, Core Competencies, Phase 1: Starter/Warm-up, Phase 2: Main Activity/Teacher-Learner Activities, Phase 3: Plenary/Reflection).
        
        STRICT DAGBANI STORY GENERATION GUARDRAILS (If requested):
        - If generating a story, strictly use the traditional Northern Ghana setting, culture, and context. Use local naming conventions (e.g., Sana, Iddi, Napari, Amina).
        - Extrapolate characters, style, syntax, and tone directly from the reference storybooks inside the grounding data. Match the vocabulary level to the selected class level (KG vs Primary vs JHS).
        - Ensure absolute linguistic authenticity and adherence to the official Dagbani Orthography. Correctly use specific characters like 'ŋ', 'ɣ', 'ɛ', and 'ɔ'.
        
        REFERENCE CURRICULUM & STORYBOOK GROUNDING DATA:
        Use the following text extracted from official curriculum guidelines and uploaded Dagbani books to ground your generation:
        {local_curriculum_context}

        REQUEST PARAMETERS:
        Subject: {subject}
        Class Level: {class_level}
        Topic/Prompt: {topic}
        Requested Resource Format: {output_type}

        Please deliver a highly professional, practical output. Ensure strict adherence to grammar, cultural logic, and proper spelling parameters.
        """
        
        with st.spinner("RLS Teacher Hub is structuring your request..."):
            try:
                response = model.generate_content(prompt)
                st.markdown("### 📝 Generated Resource Preview")
                st.write(response.text)
                
                docx_file = convert_to_docx(f"RLS Teacher Hub: {topic}", response.text)
                
                st.download_button(
                    label="Download Word Document (.docx) 📄",
                    data=docx_file,
                    file_name=f"{topic.replace(' ', '_')}_resource.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                        
