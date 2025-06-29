# 🤖 CodeOracle - Simple Code Analysis Agent

A simple, powerful code analysis agent that can analyze any GitHub repository and answer questions about the codebase. Built with Streamlit for a clean, easy-to-use interface.

## ✨ Features

- **Simple UI**: Clean Streamlit interface - no complex setup
- **Multi-language Support**: Analyzes Python, JavaScript, TypeScript, Java, C++, C#, PHP, Ruby, Go, Rust, and more
- **Dynamic Repository Ingestion**: Paste any GitHub repository URL and get instant analysis
- **Intelligent Chat**: Ask questions about the codebase and get detailed, contextual answers
- **Memory Management**: Maintains conversation context for better Q&A experience

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd CodeOracle
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and go to `http://localhost:8501`

## 🎯 How to Use

1. **Enter a GitHub repository URL** in the sidebar
2. **Click "Process Repository"** to analyze the codebase
3. **Start asking questions** about the code!

### Example Questions

- "What is the main function of this application?"
- "How does the authentication system work?"
- "Show me the database schema"
- "Explain the API endpoints"
- "What are the main dependencies?"
- "How is the project structured?"

## 🔧 Technical Details

### Supported File Types

- **Programming Languages**: Python, JavaScript, TypeScript, Java, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala
- **Web Technologies**: HTML, CSS, SQL
- **Configuration**: JSON, XML, YAML, TOML, INI
- **Documentation**: Markdown, Text files
- **Scripts**: Bash, Shell scripts

### Architecture

- **Repository Processing**: Dynamic cloning and analysis of GitHub repositories
- **Document Processing**: Multi-language file parsing and chunking
- **Vector Database**: ChromaDB for efficient similarity search
- **AI Integration**: Google Gemini for intelligent code analysis
- **UI**: Streamlit for simple, responsive interface

## 🔑 Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key to your `.env` file

**Important Notes:**
- Make sure your API key has access to Gemini models
- The app will automatically try different model versions: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-pro`
- If you encounter model errors, check that your API key is valid and has the necessary permissions

## 🛠️ Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
```

**2. "Google API key not found"**
- Make sure your `.env` file exists in the root directory
- Verify the API key is correct
- Restart the Streamlit app

**3. "Repository cloning failed"**
- Check your internet connection
- Verify the GitHub repository URL is correct
- Make sure the repository is public or you have access

**4. "No files found" error**
- The repository might not contain supported file types
- Check the repository structure

## 📁 Project Structure

```
CodeOracle/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── src/                   # Helper functions
│   ├── __init__.py
│   └── helper.py         # Repository processing functions
├── db/                   # Vector database (created automatically)
├── repo/                 # Cloned repositories (created automatically)
└── README.md             # This file
```

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Cloud Deployment
You can deploy this Streamlit app to:
- **Streamlit Cloud**: Connect your GitHub repo
- **Heroku**: Add a `setup.sh` and `Procfile`
- **Railway**: Direct deployment from GitHub

## 🎉 Success!

Once everything is working, you should be able to:
- ✅ Paste any GitHub repository URL
- ✅ See the repository being processed
- ✅ Ask questions about the codebase
- ✅ Get intelligent, contextual answers
- ✅ Enjoy the simple, clean interface

Happy coding! 🚀
