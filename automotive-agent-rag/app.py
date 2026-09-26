import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
import tempfile
import shutil
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from PyPDF2 import PdfReader
from langchain_core.tools import create_retriever_tool, tool
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

# Optional provider imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Constants
DB_DIR = "local_db"
CARS_FILE = "cars_db.json"
SAMPLE_PDF = "sample_volkswagen_taos_2023_manual.pdf"

# Page Configuration
st.set_page_config(
    page_title="Automotive RAG AI Agent",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .vehicle-tag {
        display: inline-block;
        background-color: #EEF2F6;
        color: #1E293B;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 2px 4px 2px 0;
        border: 1px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_resource
def get_embeddings():
    # Local high-speed embeddings (Zero API Key needed for indexing, 100% Free & Reliable)
    return FastEmbedEmbeddings()

def get_stored_cars():
    if not os.path.exists(CARS_FILE):
        return {}
    try:
        with open(CARS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def add_car_to_db(b, m, y):
    cars = get_stored_cars()
    b = str(b).strip()
    m = str(m).strip()
    y = str(y).strip()
    if b not in cars:
        cars[b] = {}
    if m not in cars[b]:
        cars[b][m] = []
    if y not in cars[b][m]:
        cars[b][m].append(y)
    with open(CARS_FILE, "w") as f:
        json.dump(cars, f, indent=2)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n\n"
    return text

def get_llm(provider, api_key, model_name):
    if "gemini" in provider.lower():
        model_name = model_name or "gemini-3.8-flash"
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
            max_retries=3
        )
    elif "groq" in provider.lower():
        # Only these models are active on this Groq account (verified Sep 2026):
        # openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b, allam-2-7b
        model_name = model_name or "openai/gpt-oss-120b"
        return ChatGroq(
            model=model_name,
            api_key=api_key,
            temperature=0,
            max_retries=3
        )
    else:
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0,
            max_tokens=600,
            max_retries=3
        )

def clean_agent_output(output):
    if hasattr(output, "content"):
        output = output.content
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        parts = []
        for item in output:
            if hasattr(item, "content"):
                item = item.content
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        if parts:
            return "\n".join(parts)
    if isinstance(output, dict) and "text" in output:
        return str(output["text"])
    return str(output)

def index_pdf_document(pdf_path, brand_name, model_name, year_val):
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        raise ValueError("Could not extract any readable text from the provided PDF.")
        
    metadata_header = f"Brand: {brand_name}, Model: {model_name}, Year: {year_val}\n\n"
    enhanced_text = metadata_header + text
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(enhanced_text)
    embeddings = get_embeddings()
    metadata = [{"brand": brand_name, "model": model_name, "year": str(year_val)} for _ in chunks]
    
    index_file = os.path.join(DB_DIR, "index.faiss")
    if os.path.exists(index_file):
        knowledge_base = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
        knowledge_base.add_texts(chunks, metadata)
        knowledge_base.save_local(DB_DIR)
    else:
        knowledge_base = FAISS.from_texts(chunks, embeddings, metadata)
        knowledge_base.save_local(DB_DIR)
        
    add_car_to_db(brand_name, model_name, year_val)
    return len(chunks)

# Tools definition
@tool
def check_car_availability(brand_q: str, model_q: str, year_q: str) -> str:
    """Check if a specific car brand, model, and year is registered in the dealership's knowledge base."""
    try:
        stored_cars = get_stored_cars()
        b_clean = str(brand_q).strip().lower()
        m_clean = str(model_q).strip().lower()
        y_clean = str(year_q).strip()

        for b, models in stored_cars.items():
            if b.strip().lower() == b_clean:
                for m, years in models.items():
                    if m.strip().lower() == m_clean:
                        if any(str(y).strip() == y_clean for y in years):
                            return f"Available: The {brand_q} {model_q} ({year_q}) manual is indexed in the knowledge base."
                            
        available_list = []
        for b, models in stored_cars.items():
            for m, years in models.items():
                for y in years:
                    available_list.append(f"{b} {m} ({y})")
                    
        return f"Not available: The {brand_q} {model_q} ({year_q}) was not found in the database. Available models in system: {', '.join(available_list) if available_list else 'None'}."
    except Exception as e:
        return f"Error checking availability: {str(e)}"

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    st.subheader("1. AI Engine & Model")
    provider_options = [
        "Groq LLaMA (Ultra Fast)",
        "Google Gemini",
        "OpenAI"
    ]
    has_groq = bool(os.getenv("GROQ_API_KEY", "").strip())
    has_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())
    default_idx = 0 if has_groq else (1 if has_gemini else 0)

    provider = st.selectbox(
        "AI Provider",
        options=provider_options,
        index=default_idx,
        key="selected_provider"
    )
    
    if "gemini" in provider.lower():
        active_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        gemini_model_choice = st.selectbox(
            "Gemini Model",
            ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "✏️ Enter Custom Model Name..."],
            index=0,
            help="Select the Gemini model variant."
        )
        if gemini_model_choice == "✏️ Enter Custom Model Name...":
            selected_model = st.text_input("Custom Gemini Model ID", value="gemini-2.5-flash")
        else:
            selected_model = gemini_model_choice
    elif "groq" in provider.lower():
        active_api_key = os.getenv("GROQ_API_KEY", "").strip()
        groq_model_choice = st.selectbox(
            "Groq Model",
            [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "qwen/qwen3.8-27b",
                "allam-2-7b",
                "meta-llama/llama-4-scout-17b-16e-instruct",
                "✏️ Enter Custom Model Name..."
            ],
            index=0,
            help="High-speed open-source models hosted on Groq."
        )
        if groq_model_choice == "✏️ Enter Custom Model Name...":
            selected_model = st.text_input("Custom Groq Model ID", value="openai/gpt-oss-120b")
        else:
            selected_model = groq_model_choice
    else:
        active_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        selected_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    
    st.divider()
    
    st.subheader("2. Target Vehicle Details")
    target_brand = st.text_input("Brand", value="Volkswagen")
    target_model = st.text_input("Model", value="Taos")
    target_year = st.text_input("Year", value="2023")
    
    st.divider()
    
    st.subheader("3. Knowledge Base & Manuals")
    st.caption("⚡ *Embeddings run locally (Zero API Key needed for indexing)*")
    uploaded_file = st.file_uploader("Upload PDF Manual", type=["pdf"])
    
    if st.button("📤 Process & Index PDF", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Please select a PDF file first.")
        else:
            with st.spinner("Parsing PDF and building FAISS vector embeddings locally..."):
                try:
                    temp_dir = tempfile.mkdtemp()
                    temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    num_chunks = index_pdf_document(
                        temp_pdf_path,
                        target_brand,
                        target_model,
                        target_year
                    )
                    shutil.rmtree(temp_dir)
                    st.toast(f"✅ Indexed {num_chunks} chunks!")
                    st.success(f"✅ Indexed {num_chunks} chunks for {target_brand} {target_model} ({target_year})!")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {e}")
                    
    # Preloaded Sample PDF Button
    stored_cars_check = get_stored_cars()
    is_taos_loaded = "Volkswagen" in stored_cars_check and "Taos" in stored_cars_check.get("Volkswagen", {})
    
    if is_taos_loaded:
        st.success("✅ **VW Taos 2023 manual is loaded & ready!**")
        btn_label = "🔄 Reload Sample Manual (VW Taos 2023)"
    else:
        btn_label = "⚡ 1-Click Load Sample Manual (VW Taos 2023)"

    if os.path.exists(SAMPLE_PDF):
        if st.button(btn_label, use_container_width=True):
            with st.spinner("Indexing bundled Volkswagen Taos 2023 manual locally..."):
                try:
                    num_chunks = index_pdf_document(
                        SAMPLE_PDF,
                        "Volkswagen",
                        "Taos",
                        "2023"
                    )
                    st.toast("✅ Sample manual loaded successfully!")
                    st.success(f"✅ Loaded sample manual ({num_chunks} chunks indexed)!")
                except Exception as e:
                    st.error(f"❌ Error indexing sample: {e}")

    st.divider()
    
    # Stored cars status
    st.subheader("📚 Registered Vehicles")
    stored_cars = get_stored_cars()
    if stored_cars:
        for b, models in stored_cars.items():
            for m, years in models.items():
                for y in years:
                    st.markdown(f"<span class='vehicle-tag'>🚗 {b} {m} ({y})</span>", unsafe_allow_html=True)
    else:
        st.caption("No vehicles indexed yet. Click the sample manual button above to load one!")

    if os.path.exists(DB_DIR) or os.path.exists(CARS_FILE):
        if st.button("🗑️ Reset Database", use_container_width=True):
            if os.path.exists(DB_DIR):
                shutil.rmtree(DB_DIR)
            if os.path.exists(CARS_FILE):
                os.remove(CARS_FILE)
            st.success("Database cleared!")
            st.rerun()

# Main Header
st.markdown("<div class='main-header'>🚗 Automotive Customer Service Agent (RAG)</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Powered by <b>{provider}</b> + Local FAISS vector search for automotive manuals.</div>", unsafe_allow_html=True)

# Quick Test Prompts
st.markdown("**💡 Sample Questions to Try:**")
col1, col2, col3, col4 = st.columns([1, 1, 1, 0.5])
with col1:
    if st.button("🔔 When will the alarm be triggered?", use_container_width=True):
        st.session_state["preset_prompt"] = "When will the alarm be triggered?"
with col2:
    if st.button("❄️ When is air recirculation turned off?", use_container_width=True):
        st.session_state["preset_prompt"] = "When is the air recirculation mode turned off?"
with col3:
    if st.button("🔥 When should seat heating not be used?", use_container_width=True):
        st.session_state["preset_prompt"] = "When should the seat heating not be turned on?"
with col4:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Chat History initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(clean_agent_output(msg["content"]))

# Prompt handling - Always render chat_input so it stays pinned at the bottom
user_input = st.chat_input("Ask an automotive maintenance or operating question...")

active_prompt = None
if "preset_prompt" in st.session_state and st.session_state["preset_prompt"]:
    active_prompt = st.session_state.pop("preset_prompt")
elif user_input:
    active_prompt = user_input

# Check API key before running agent
if active_prompt:
    if not active_api_key:
        st.error(f"⚙️ **Backend Key Missing**: The API key for `{provider}` is not configured in the server's `.env` file.")
    else:
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Checking manual and analyzing issue..."):
                try:
                    tools = [check_car_availability]
                    index_file = os.path.join(DB_DIR, "index.faiss")
                    
                    if os.path.exists(index_file):
                        embeddings = get_embeddings()
                        knowledge_base = FAISS.load_local(
                            DB_DIR,
                            embeddings,
                            allow_dangerous_deserialization=True
                        )
                        retriever = knowledge_base.as_retriever(search_kwargs={"k": 4})
                        retriever_tool = create_retriever_tool(
                            retriever,
                            "knowledge_base_retriever",
                            "Search for specific technical procedures, troubleshooting steps, and manual instructions."
                        )
                        tools.append(retriever_tool)
                    else:
                        @tool
                        def knowledge_base_retriever(query: str) -> str:
                            """Search for technical manual instructions."""
                            return "The knowledge base currently contains no indexed vehicle manuals. Inform the customer to index a manual PDF first."
                        tools.append(knowledge_base_retriever)
                    
                    llm = get_llm(provider, active_api_key, selected_model)
                    
                    template_system = f"""You are a professional customer service agent at a car dealership assisting vehicle owners.
The customer's vehicle is: {target_brand} {target_model} ({target_year}).

Follow these exact steps:
1. First, check if the {target_brand} {target_model} {target_year} is available in the knowledge base using the `check_car_availability` tool.
2. If available:
   - Use `knowledge_base_retriever` to find the exact manual instructions and troubleshooting steps for the user's issue.
   - Provide a helpful, clear, and structured step-by-step response addressing their question.
3. If not available:
   - Politely inform the customer that technical data for {target_brand} {target_model} {target_year} is not in the system yet, and ask them to specify an available model or upload the corresponding manual.
"""
                    
                    prompt_template = ChatPromptTemplate.from_messages([
                        ("system", template_system),
                        ("user", "{input}"),
                        MessagesPlaceholder(variable_name="agent_scratchpad"),
                    ])
                    
                    agent = create_tool_calling_agent(llm, tools, prompt_template)
                    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)
                    
                    input_query = (
                        f"Customer issue: '{active_prompt}'. "
                        f"Please check availability for {target_brand} {target_model} {target_year} and provide the solution if available."
                    )
                    
                    response = agent_executor.invoke({"input": input_query})

                    raw_output = response.get("output", "I processed your request, but could not retrieve a final answer.")
                    answer = clean_agent_output(raw_output)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    err_msg = str(e)
                    if "API_KEY_INVALID" in err_msg or "incorrect_api_key" in err_msg or "Invalid API Key" in err_msg:
                        st.error("❌ Invalid API key configured in the backend `.env` file.")
                    elif "insufficient_quota" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                        st.warning("⏳ **Rate limit reached.** Please wait a moment or select another AI provider in the sidebar.")
                    else:
                        st.error(f"❌ An error occurred: {e}")
