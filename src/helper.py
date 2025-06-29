import os
import shutil
import time
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings


def safe_remove_directory(path):
    """Safely remove a directory with retry logic for Windows"""
    if not os.path.exists(path):
        return True
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # On Windows, we need to handle read-only files
            def on_error(func, path, exc_info):
                if os.path.exists(path):
                    os.chmod(path, 0o777)
                    func(path)
            
            shutil.rmtree(path, onerror=on_error)
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}: Permission error, retrying in 1 second...")
                time.sleep(1)
            else:
                print(f"Failed to remove directory after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            print(f"Error removing directory: {e}")
            return False
    return False


#clone any github repositories 
def repo_ingestion(repo_url):
    repo_path = "repo/"
    
    # Safely remove existing repository
    if os.path.exists(repo_path):
        print("Cleaning up existing repository...")
        if not safe_remove_directory(repo_path):
            print("Warning: Could not clean up existing repository, continuing anyway...")
    
    # Create fresh directory
    os.makedirs(repo_path, exist_ok=True)
    
    try:
        print(f"Cloning repository: {repo_url}")
        Repo.clone_from(repo_url, to_path=repo_path)
        print("Repository cloned successfully!")
        return True
    except Exception as e:
        print(f"Error cloning repository: {e}")
        # Clean up partial clone
        safe_remove_directory(repo_path)
        return False


#Loading repositories as documents
def load_repo(repo_path):
    # Define supported file extensions with safer parsing
    supported_extensions = {
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
        ".sql": Language.SQL,
        ".sh": Language.BASH,
        ".md": Language.MARKDOWN,
        ".txt": Language.MARKDOWN,
        ".json": Language.JSON,
        ".xml": Language.XML,
        ".yaml": Language.YAML,
        ".yml": Language.YAML,
        ".toml": Language.TOML,
        ".ini": Language.INI,
        ".cfg": Language.INI,
        ".conf": Language.INI,
    }
    
    # CSS and other files that might cause parsing issues
    simple_extensions = [".css", ".scss", ".sass", ".less", ".log", ".lock", ".gitignore", ".gitattributes"]
    
    documents = []
    
    # Load documents for each supported file type with language parser
    for ext, language in supported_extensions.items():
        try:
            loader = GenericLoader.from_filesystem(
                repo_path,
                glob="**/*",
                suffixes=[ext],
                parser=LanguageParser(language=language, parser_threshold=500)
            )
            docs = loader.load()
            documents.extend(docs)
            if docs:
                print(f"Loaded {len(docs)} {ext} files")
        except Exception as e:
            print(f"Error loading {ext} files: {e}")
            continue
    
    # Load simple text files without language parser
    for ext in simple_extensions:
        try:
            loader = GenericLoader.from_filesystem(
                repo_path,
                glob="**/*",
                suffixes=[ext]
            )
            docs = loader.load()
            documents.extend(docs)
            if docs:
                print(f"Loaded {len(docs)} {ext} files (as text)")
        except Exception as e:
            print(f"Error loading {ext} files: {e}")
            continue
    
    # Also load any other text files that might not have specific extensions
    try:
        text_loader = GenericLoader.from_filesystem(
            repo_path,
            glob="**/*",
            suffixes=[".txt", ".md", ".log", ".cfg", ".conf", ".ini"]
        )
        text_docs = text_loader.load()
        documents.extend(text_docs)
        if text_docs:
            print(f"Loaded {len(text_docs)} additional text files")
    except Exception as e:
        print(f"Error loading text files: {e}")
    
    print(f"Total documents loaded: {len(documents)}")
    return documents


#Creating text chunks 
def text_splitter(documents):
    # Use a more generic text splitter that works for all languages
    documents_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    text_chunks = documents_splitter.split_documents(documents)
    print(f"Created {len(text_chunks)} text chunks")
    return text_chunks


#loading embeddings model
def load_embedding():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return embeddings
