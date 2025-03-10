# Victorian Study App

Victorian Study App is an AI-driven web application designed to support personalized learning through interactive chat and quiz features. The platform integrates multiple AI services—including conversational tutoring, quiz generation, and document ingestion—with a modern web interface and persistent data storage.

---

## Project Overview

Victorian Study App offers a comprehensive study companion experience by combining the following core functionalities:

- **User Authentication:**  
  Secure sign-up, login, and logout features manage user sessions and credentials.

- **AI Chatbot:**  
  Interact with "Sir Learnsworth," an AI tutor that answers study-related questions using advanced language models (e.g., GPT-4 via OpenAI) and context retrieved from user-uploaded knowledge bases.

- **Quiz Generation:**  
  Quizzes are generated in two ways:
  - **Knowledge Base-Based Quizzes:**  
    Users can upload PDFs (or DOCX) files that are processed and split into text chunks. A vector store is built for context retrieval, and GPT-4 generates multiple-choice questions.
  - **Conversation-Based Quizzes:**  
    Based on ongoing interactions with the chatbot, a quiz is generated to assess retention and understanding.

- **Document Ingestion and Summarization:**  
  The app processes various document formats (PDFs, DOCX, images) to extract text using libraries such as PyPDF2, pdf2image, pytesseract, and python-docx.

- **Streamlit Interfaces:**  
  Standalone tools using Streamlit provide quick interactive summary and quiz generation via T5-based and LLaMA-based models.

- **Database Persistence:**  
  User details and conversation histories are stored in Azure Cosmos DB, ensuring persistent and scalable data management.

---


Additional standalone Streamlit applications:
- **t5basedquizzgeneration.py:** Uses a Flan-T5 model for PDF summarization and quiz generation.
- **llammabasedquiz-summarygeneration.py:** Leverages an Open LLaMA-based model for generating summaries and quizzes from PDFs.

---

## Technologies and Models Used

- **Backend Framework:**  
  - **Flask:** Web server and REST API endpoints.
  - **Flask-CORS:** Enables Cross-Origin Resource Sharing.
  - **Jinja2:** HTML templating engine.

- **Front-end:**  
  - **HTML5, CSS3, JavaScript:** Building responsive and interactive interfaces.
  - **Streamlit:** Rapid development of AI-based interactive tools.

- **AI and NLP:**  
  - **OpenAI API (GPT-4):** Conversational tutoring, quiz generation, and content summarization.
  - **LangChain:** For document ingestion, vector indexing, and managing conversational retrieval chains.
  - **Transformers (Hugging Face):** T5-based and LLaMA-based models for text generation in Streamlit apps.
  - **PyPDF2, pdf2image, pytesseract, python-docx:** Document processing and text extraction.

- **Vector Stores and Embeddings:**  
  - **FAISS:** Creating vector stores for efficient text retrieval.
  - **OpenAIEmbeddings:** Converting text into embeddings for context-based queries.

- **Database and Persistence:**  
  - **Azure Cosmos DB:** Stores user information and conversation histories.
  - **Cosmos Python SDK:** Managed via `db.py` to initialize containers for "users" and "conversations".

- **Configuration and Environment Management:**  
  - **python-dotenv:** Loads environment variables from a `.env` file.
  - **Custom Config Class:** Located in `config.py` (and `app/config/config.py`) for application settings.

- **Security:**  
  - **Werkzeug Security:** For password hashing and verification.

---

## Installation and Setup

### Prerequisites

- **Python 3.8+**
- **Azure Cosmos DB:**  
  Set up an Azure Cosmos DB account and obtain the database URL and key.
- **Environment Variables:**  
  Create a `.env` file in the project root with the following variables:
  
  ```ini
  SECRET_KEY=your_secret_key
  OPENAI_API_KEY=your_openai_api_key
  COSMOS_DB_URL=your_cosmos_db_url
  COSMOS_DB_KEY=your_cosmos_db_key
  COSMOS_DB_DATABASE=learnsworth


Running the Application
Flask Server
Start the Server:
In the project root, run:
python main.py
Access the Web Interface:

Login/Signup: Visit http://0.0.0.0:8000/login to create an account or log in.
Homepage: Upon login, the homepage (/) will display navigation links for the chatbot and quiz features.
Chatbot: Accessible at /chatbot/chat_ui_page for interacting with Sir Learnsworth.
Quiz: Accessible at /quiz/quiz_ui for quiz configuration and display.
Streamlit Tools
To run the standalone AI tools for PDF summarization and quiz generation:

T5-Based Quiz Generation:
streamlit run t5basedquizzgeneration.py
LLaMA-Based Quiz & Summary Generation:
streamlit run llammabasedquiz-summarygeneration.py


