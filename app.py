import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from io import BytesIO

# 1. Page Configuration (Optimized for Mobile/Tablet Screens)
st.set_page_config(page_title="RLS Teacher Hub: Ghanaian Teacher Assistant", page_icon="🇬🇭", layout="centered")

# --- INTEGRATED MOODLEBOX SIDEBAR COMPONENT ---
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown("## 🍓 MoodleBox Offline Hub")
    st.info("Use this tracking checklist to deploy your online resources offline in the classroom.")
    
    st.checkbox("Step 1: Paste API Key & choose task.", value=False)
    st.checkbox("Step 2: Choose layout layout style format.", value=False)
    st.checkbox("Step 3: Click the 'Download Word Document' button below.", value=False)
    st.checkbox("Step 4: Connect phone to school 'MoodleBox' Wi-Fi.", value=False)
    st.checkbox("Step 5: Go to http://moodlebox.home data-free.", value=False)
    st.checkbox("Step 6: Upload the Word file to your Moodle Course block.", value=False)
    
    st.markdown("---")
    st.markdown("### 🛠️ Local Server Access Parameters")
    st.caption("Default Admin Username: **admin**")
    st.caption("Default Admin Password: **MoodleBox2018!**")
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
    
    # 🌟 NEW DOCUMENT TEMPLATE SELECTOR RADIO BUTTONS
    st.markdown("### Step 3: Select Document Layout Format")
    layout_style = st.radio("Choose layout template style:", ["Standard Text Block Layout", "Official NaCCA Standard Table Template Grid"])


# Helper function to inject light grey header cell backgrounds to match NaCCA layout styles
def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

# Function to safely turn plain AI text into a beautifully styled Word Document (.docx)
def convert_to_docx(title_text, content_text, layout_style, meta_dict=None):
    doc = Document()
    
    # Configure 1-inch uniform margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    if layout_style == "Official NaCCA Standard Table Template Grid" and meta_dict:
        # 1. Page Header Block
        p_head = doc.add_paragraph()
        r_head = p_head.add_run("NATIONAL COUNCIL FOR CURRICULUM & ASSESSMENT (NaCCA)\nDAILY LESSON TRACKING MATRIX")
        r_head.bold = True
        r_head.font.size = Pt(12)
        p_head.alignment = 1 # Centered
        
        # 2. Section A Metadata Block Grid Table
        table_meta = doc.add_table(rows=5, cols=4)
        table_meta.autofit = False
        table_meta.columns[0].width = Inches(1.8)
        table_meta.columns[1].width = Inches(1.7)
        table_meta.columns[2].width = Inches(1.5)
        table_meta.columns[3].width = Inches(1.5)
        
        # Add thin borders to the tables
        tblPr = table_meta._tbl.tblPr
        tblBorders = parse_xml(r'<w:tblBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/></w:tblBorders>' % nsdecls('w'))
        tblPr.append(tblBorders)

        # Row 1 entries
        table_meta.cell(0, 0).text = "Date: [ As Planned ]"
        table_meta.cell(0, 1).text = "Period: [ 1 & 2 ]"
        table_meta.cell(0, 2).text = "Subject:"
        table_meta.cell(0, 3).text = meta_dict.get('subject', '')
        
        # Row 2 entries
        table_meta.cell(1, 0).text = "Duration: 40-60 Mins"
        table_meta.cell(1, 1).text = "Class Size: [ 40 ]"
        table_meta.cell(1, 2).text = "Class:"
        table_meta.cell(1, 3).text = meta_dict.get('class_level', '')
        
        # Row 3 entries
        table_meta.cell(2, 0).text = "Strand:"
        cell_strand = table_meta.cell(2, 1)
        cell_strand.text = f"As defined in {meta_dict.get('subject', '')} syllabus framework."
        table_meta.cell(2, 2).text = "Sub-Strand:"
        table_meta.cell(2, 3).text = meta_dict.get('topic', '')
        # Merge cell 1 across columns if necessary or leave structured
        
        # Row 4 entries
        table_meta.cell(3, 0).text = "Content Standard:"
        table_meta.cell(3, 1).text = "Grounded via RLS Core Specifications."
        table_meta.cell(3, 2).text = "Indicator:"
        table_meta.cell(3, 3).text = f"Lesson 1 of 1"
        
        # Row 5 entries
        table_meta.cell(4, 0).text = "Key Words:"
        table_meta.cell(4, 1).text = "Included below."
        table_meta.cell(4, 2).text = "Core Competencies:"
        table_meta.cell(4, 3).text = "Personal Dev, Critical Thinking"

        for row in table_meta.rows:
            for i in:
                set_cell_background(row.cells[i], "F2F2F2")

        doc.add_paragraph("\n") # Line spacing spacer

        # 3. Main Delivery Tracking Activities Grid Table Layout
        table_main = doc.add_table(rows=1, cols=3)
        table_main.autofit = False
        table_main.columns[0].width = Inches(1.8)
        table_main.columns[1].width = Inches(3.2)
        table_main.columns[2].width = Inches(1.5)
        
        # Apply structured table border element tags
        tblPr_m = table_main._tbl.tblPr
        tblPr_m.append(parse_xml(r'<w:tblBorders %s><w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/><w:insideV w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tblBorders>' % nsdecls('w')))
        
        hdr_cells = table_main.rows[0].cells
        hdr_cells[0].text = "Phase / Duration"
        hdr_cells[1].text = "Learner Activities / Core Delivery"
