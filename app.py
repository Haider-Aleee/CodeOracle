import streamlit as st
import os
import shutil
import time
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="CodeOracle - Code Analysis Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None
if 'current_repo' not in st.session_state:
    st.session_state.current_repo = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def safe_remove_directory(path):
    """Safely remove a directory with retry logic for Windows"""
    if not os.path.exists(path):
        return True
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            def on_error(func, path, exc_info):
                if os.path.exists(path):
                    os.chmod(path, 0o777)
                    func(path)
            
            shutil.rmtree(path, onerror=on_error)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return False
    return False

def clone_repository(repo_url):
    """Clone a GitHub repository"""
    repo_path = "repo/"
    
    # Clean up existing repository
    if os.path.exists(repo_path):
        safe_remove_directory(repo_path)
    
    os.makedirs(repo_path, exist_ok=True)
    
    try:
        with st.spinner("Cloning repository..."):
            Repo.clone_from(repo_url, to_path=repo_path)
        return True
    except Exception as e:
        st.error(f"Error cloning repository: {e}")
        return False

def load_documents(repo_path):
    """Load documents from the repository"""
    # Only the most reliable language parsers
    reliable_extensions = {
        ".py": Language.PYTHON,
        ".js": Language.JS,
        ".jsx": Language.JS,
        ".ts": Language.TS,
        ".tsx": Language.TS,
        ".java": Language.JAVA,
        ".cpp": Language.CPP,
        ".c": Language.C,
        ".cs": Language.CSHARP,
        ".php": Language.PHP,
        ".rb": Language.RUBY,
        ".go": Language.GO,
        ".rs": Language.RUST,
        ".swift": Language.SWIFT,
        ".kt": Language.KOTLIN,
        ".scala": Language.SCALA,
        ".html": Language.HTML,
    }
    
    # All other files as simple text (no language parser)
    simple_extensions = [
        # Documentation
        ".md", ".txt", ".rst", ".adoc",
        # Configuration
        ".json", ".jsonc", ".json5", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        # Styling
        ".css", ".scss", ".sass", ".less", 
        # Database
        ".sql", ".sqlite", ".db",
        # Scripts
        ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
        # Build/Config files
        ".log", ".lock", ".gitignore", ".gitattributes", ".gitmodules", ".gitkeep",
        ".env", ".env.local", ".env.production", ".env.development",
        ".dockerfile", ".dockerignore",
        ".editorconfig", ".eslintrc", ".prettierrc", ".babelrc", ".browserslistrc",
        ".npmrc", ".yarnrc", ".pip", ".requirements", ".setup", ".pyproject",
        ".travis.yml", ".github", ".gitlab-ci.yml", ".azure-pipelines.yml",
        ".vscode", ".idea", ".DS_Store", ".Thumbs.db"
    ]
    
    documents = []
    processed_files = 0
    error_files = 0
    
    # Load files with language parser (only the most reliable ones)
    for ext, language in reliable_extensions.items():
        try:
            loader = GenericLoader.from_filesystem(
                repo_path,
                glob="**/*",
                suffixes=[ext],
                parser=LanguageParser(language=language, parser_threshold=500)
            )
            docs = loader.load()
            documents.extend(docs)
            processed_files += len(docs)
        except Exception as e:
            # Fallback: try loading without language parser
            try:
                loader = GenericLoader.from_filesystem(
                    repo_path,
                    glob="**/*",
                    suffixes=[ext]
                )
                docs = loader.load()
                documents.extend(docs)
                processed_files += len(docs)
                st.info(f"⚠️ Loaded {len(docs)} {ext} files as text (parser failed)")
            except Exception as fallback_error:
                error_files += 1
                continue
    
    # Load simple files without parser (all other files)
    for ext in simple_extensions:
        try:
            loader = GenericLoader.from_filesystem(
                repo_path,
                glob="**/*",
                suffixes=[ext]
            )
            docs = loader.load()
            documents.extend(docs)
            processed_files += len(docs)
        except Exception as e:
            error_files += 1
            continue
    
    if error_files > 0:
        st.warning(f"⚠️ Skipped {error_files} files due to loading issues")
    
    st.success(f"📁 Successfully loaded {len(documents)} documents from {processed_files} files")
    return documents

def create_qa_chain(documents):
    """Create the QA chain from documents"""
    # Create text chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    text_chunks = text_splitter.split_documents(documents)
    
    # Create embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create vector database
    vectordb = Chroma.from_documents(
        text_chunks, 
        embedding=embeddings, 
        persist_directory='./db'
    )
    vectordb.persist()
    
    # Create QA chain with fallback model options
    model_names = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    llm = None
    
    for model_name in model_names:
        try:
            llm = ChatGoogleGenerativeAI(model=model_name)
            # Test the model with a simple query
            llm.invoke("test")
            st.info(f"✅ Using model: {model_name}")
            break
        except Exception as e:
            st.warning(f"⚠️ Model {model_name} not available, trying next...")
            continue
    
    if llm is None:
        raise Exception("No available Gemini models found. Please check your API key and model availability.")
    
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm, 
        retriever=vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 8}), 
        memory=memory
    )
    
    return qa_chain

def process_repository(repo_url):
    """Process a GitHub repository"""
    try:
        # Clone repository
        if not clone_repository(repo_url):
            return False
        
        # Load documents
        with st.spinner("Loading documents..."):
            try:
                documents = load_documents("repo/")
                if not documents:
                    st.error("No supported files found in repository")
                    return False
                st.info(f"Found {len(documents)} files to process")
            except Exception as e:
                st.error(f"Error loading documents: {str(e)}")
                return False
        
        # Create QA chain
        with st.spinner("Creating AI model..."):
            try:
                qa_chain = create_qa_chain(documents)
                st.session_state.qa_chain = qa_chain
                st.session_state.current_repo = repo_url
            except Exception as e:
                st.error(f"Error creating AI model: {str(e)}")
                return False
        
        st.success(f"✅ Repository processed successfully! Found {len(documents)} files.")
        return True
        
    except Exception as e:
        st.error(f"Error processing repository: {str(e)}")
        # Clean up on error
        safe_remove_directory("repo")
        safe_remove_directory("db")
        return False

def clear_repository():
    """Clear the current repository"""
    st.session_state.qa_chain = None
    st.session_state.current_repo = None
    st.session_state.messages = []
    safe_remove_directory("repo")
    safe_remove_directory("db")
    st.success("Repository cleared!")

# Main UI
st.title("🤖 CodeOracle - Code Analysis Agent")
st.markdown("Ask questions about any GitHub repository's codebase!")

# Sidebar for repository input
with st.sidebar:
    st.header("Repository Setup")
    
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repo-name",
        help="Enter the full GitHub repository URL"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Process Repository", type="primary"):
            if repo_url:
                process_repository(repo_url)
            else:
                st.error("Please enter a repository URL")
    
    with col2:
        if st.button("🗑️ Clear"):
            clear_repository()
    
    # Display current repository
    if st.session_state.current_repo:
        st.success(f"📁 Current: {st.session_state.current_repo}")
    
    # API Key check
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY not found in .env file")
    else:
        st.success("✅ API Key configured")

# Main chat area
st.header("💬 Chat with CodeOracle")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the codebase..."):
    if not st.session_state.qa_chain:
        st.error("Please process a repository first!")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.qa_chain({"question": prompt})
                    answer = response['answer']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg and "models" in error_msg:
                        error_msg = "❌ API Model Error: The specified Gemini model is not available. Please check your API key and try again."
                    elif "API" in error_msg or "key" in error_msg.lower():
                        error_msg = "❌ API Error: Please check your Google Gemini API key in the .env file."
                    elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                        error_msg = "❌ API Quota Error: You've reached your API usage limit. Please try again later."
                    else:
                        error_msg = f"❌ Error: {error_msg}"
                    
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Instructions
if not st.session_state.qa_chain:
    st.info("""
    **How to use:**
    1. Enter a GitHub repository URL in the sidebar
    2. Click "Process Repository" to analyze the codebase
    3. Start asking questions about the code!
    
    **Example questions:**
    - "What is the main function of this application?"
    - "How does the authentication system work?"
    - "Show me the database schema"
    - "Explain the API endpoints"
    """)

# Footer
st.markdown("---")
st.markdown("Powered by Google Gemini AI • Built with Streamlit") 