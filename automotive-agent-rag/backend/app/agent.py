from typing import List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

from . import config
from . import vector_store
from .db_mongo import get_repository

PROVIDERS = {
    "groq": {
        "label": "Groq LLaMA (Ultra Fast)",
        "models": [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "allam-2-7b",
            "meta-llama/llama-4-scout-17b-16e-instruct",
        ],
        "default_model": "openai/gpt-oss-120b",
        "env_key": "GROQ_API_KEY",
    },
    "gemini": {
        "label": "Google Gemini",
        "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        "default_model": "gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
    },
    "openai": {
        "label": "OpenAI",
        "models": ["gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
}


def get_provider_status() -> dict:
    return {
        key: {
            **{k: v for k, v in info.items() if k != "env_key"},
            "available": bool(_api_key_for(key)),
        }
        for key, info in PROVIDERS.items()
    }


def _api_key_for(provider: str) -> str:
    return {
        "groq": config.GROQ_API_KEY,
        "gemini": config.GEMINI_API_KEY,
        "openai": config.OPENAI_API_KEY,
    }.get(provider, "")


def get_llm(provider: str, model_name: Optional[str]):
    provider = provider.lower()
    info = PROVIDERS.get(provider)
    if info is None:
        raise ValueError(f"Unknown provider '{provider}'.")

    api_key = _api_key_for(provider)
    if not api_key:
        raise ValueError(f"The API key for '{provider}' is not configured in the server's .env file.")
    model_name = model_name or info["default_model"]

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0, max_retries=3)
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=model_name, api_key=api_key, temperature=0, max_retries=3)

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=model_name, api_key=api_key, temperature=0, max_tokens=600, max_retries=3)


def clean_agent_output(output) -> str:
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


def _make_availability_tool():
    repo = get_repository()

    @tool
    def check_car_availability(brand_q: str, model_q: str, year_q: str) -> str:
        """Check if a specific car brand, model, and year is registered in the dealership's knowledge base."""
        try:
            match = repo.find_manual(brand_q, model_q, year_q)
            if match:
                return f"Available: The {brand_q} {model_q} ({year_q}) manual is indexed in the knowledge base."
            available = [f"{m['brand']} {m['model']} ({m['year']})" for m in repo.list_manuals()]
            return (
                f"Not available: The {brand_q} {model_q} ({year_q}) was not found in the database. "
                f"Available models in system: {', '.join(available) if available else 'None'}."
            )
        except Exception as e:  # noqa: BLE001
            return f"Error checking availability: {str(e)}"

    return check_car_availability


def _make_retriever_tool(evidence_sink: list):
    retriever = vector_store.get_retriever(k=4)

    @tool
    def knowledge_base_retriever(query: str) -> str:
        """Search for specific technical procedures, troubleshooting steps, and manual instructions."""
        if retriever is None:
            return "The knowledge base currently contains no indexed vehicle manuals. Inform the customer to index a manual PDF first."
        docs = retriever.invoke(query)
        for doc in docs:
            evidence_sink.append(doc)
        if not docs:
            return "No relevant manual sections were found for this query."
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    return knowledge_base_retriever


def run_chat(
    message: str,
    provider: str,
    model_name: Optional[str],
    brand: str,
    vehicle_model: str,
    year: str,
) -> Tuple[str, List[dict]]:
    llm = get_llm(provider, model_name)

    evidence_sink: list = []
    tools = [_make_availability_tool(), _make_retriever_tool(evidence_sink)]

    system_prompt = f"""You are a professional customer service agent at a car dealership assisting vehicle owners.
The customer's vehicle is: {brand} {vehicle_model} ({year}).

Follow these exact steps:
1. First, check if the {brand} {vehicle_model} {year} is available in the knowledge base using the `check_car_availability` tool.
2. If available:
   - Use `knowledge_base_retriever` to find the exact manual instructions and troubleshooting steps for the user's issue.
   - Provide a helpful, clear, and structured step-by-step response addressing their question.
3. If not available:
   - Politely inform the customer that technical data for {brand} {vehicle_model} {year} is not in the system yet, and ask them to specify an available model or upload the corresponding manual.
"""

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt_template)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

    input_query = (
        f"Customer issue: '{message}'. "
        f"Please check availability for {brand} {vehicle_model} {year} and provide the solution if available."
    )

    response = agent_executor.invoke({"input": input_query})
    raw_output = response.get("output", "I processed your request, but could not retrieve a final answer.")
    answer = clean_agent_output(raw_output)

    evidence = []
    seen = set()
    for doc in evidence_sink:
        key = (doc.metadata.get("manual_id"), doc.metadata.get("page"), doc.page_content)
        if key in seen:
            continue
        seen.add(key)
        evidence.append(
            {
                "content": doc.page_content,
                "page": doc.metadata.get("page"),
                "brand": doc.metadata.get("brand"),
                "model": doc.metadata.get("model"),
                "year": doc.metadata.get("year"),
                "manual_id": doc.metadata.get("manual_id"),
                "source_filename": doc.metadata.get("source"),
            }
        )

    return answer, evidence
