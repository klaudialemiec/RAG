import streamlit as st

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from scripts.rag import RAG


st.set_page_config(page_title="Streamlit RAG")
st.title("Retrieval-Augmented Generation")


@st.cache_resource
def load_model(google_api_key: str, pinecone_api_key: str, index_name: str) -> RAG:
    """
    Loads and initializes the RAG model.

    Args:
        google_api_key (str): The API key for Google Cloud services.
        pinecone_api_key (str): The API key for Pinecone.
        index_name (str): The name of the index to use.

    Returns:
        RAG: The initialized RAG model.
    """
    embedding = HuggingFaceEmbeddings(model_name=f"sentence-transformers/gtr-t5-base")
    embedding.client.similarity_fn_name = "cosine"
    rag = RAG(
        index_name=index_name,
        embedding_model=embedding,
        google_api_key=google_api_key,
        pinecone_api_key=pinecone_api_key,
    )
    return rag


def show_ui(rag: RAG, welcome_message: str) -> None:
    """
    Displays the user interface for the RAG chatbot.

    Args:
        rag (RAG): The RAG chatbot instance.
        welcome_message (str): The welcome message to display.
    """
    
    # show welcome message
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content=welcome_message),
        ]

    # print existing conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    # handle user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human"):
            st.write(user_query)

        with st.chat_message("AI"):
            response = rag.ask(user_query)
            st.write(response)
            st.session_state.chat_history.append(AIMessage(content=response))


def get_password(secret_key: str, info_link: str = None) -> str:
    """
    Retrieves a password from the user or from the secrets store.

    Args:
        secret_key (str): The key used to retrieve the password from the secrets store.
        info_link (str, optional): A link to additional information about the password. Defaults to None.

    Returns:
        str: The retrieved password.
    """
    if secret_key in st.secrets:
        st.write("Found %s secret" % secret_key)
        secret_value = st.secrets[secret_key]
    else:
        secret_name = secret_key.replace("_", " ").capitalize()
        st.write(f"Please provide your {secret_name}")
        secret_value = st.text_input(
            secret_name, key=f"input_{secret_key}", type="password"
        )
        if secret_value:
            st.session_state[secret_key] = secret_value
        if info_link:
            st.markdown(f"[Get an {secret_name}]({info_link})")
    return secret_value


def run() -> None:
    """
    Runs the Streamlit application.

    This function initializes the necessary API keys and prompts the user for input.
    If all the required information is provided, it loads the RAG model and displays the user interface.
    Otherwise, it stops the execution of the application.
    """
    
    ready = True
    pinecone_api_key = st.session_state.get("PINECONE_API_KEY")
    google_api_key = st.session_state.get("GOOGLE_API_KEY")

    with st.sidebar:
        if not pinecone_api_key:
            pinecone_api_key = get_password(
                "PINECONE_API_KEY",
                info_link="https://docs.pinecone.io/guides/get-started/quickstart",
            )
            ready = False
        if not google_api_key:
            google_api_key = get_password(
                "GOOGLE_API_KEY", info_link="https://aistudio.google.com/app/apikey"
            )
            ready = False

        pinecone_index_input = st.text_input("Please provide Pinecone index name:")
        if not pinecone_index_input:
            ready = False

    if ready:
        rag = load_model(google_api_key, pinecone_api_key, pinecone_index_input)
        show_ui(rag, "Hello! Ask me anything about your data.")
    else:
        st.stop()


run()
