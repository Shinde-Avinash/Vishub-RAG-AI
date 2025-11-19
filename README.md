# 🤖 Vishub RAG AI Helper

This project implements a Retrieval-Augmented Generation (RAG) system using Flask for the frontend and **Ollama** for running the Large Language Model (LLM) and handling embeddings. The system allows users to upload documents, which are then processed and used as the knowledge base for the chatbot.

## ✨ Features
<img width="1350" height="593" alt="image" src="https://github.com/user-attachments/assets/2c0b6547-2a55-40f4-8ed8-e7be296f2675" />

* **Dark Mode UI:** Modern, responsive chat interface built with Flask and Bootstrap.
* **Vishub RAG AI:** Leverages a local vector database to provide context-aware answers based on uploaded documents.
* **Ollama Integration:** Uses Ollama for running the LLM (e.g., `llama2`, `mistral`) and generating necessary text embeddings (e.g., `nomic-embed-text`).
* **Markdown Rendering:** Formats AI responses cleanly using Markdown.

## 🚀 Setup and Installation

### Prerequisites

You must have the following installed on your system:

1.  **Python 3.x**
2.  **Ollama:** Download and install Ollama from the official website. Ensure the Ollama service is running.

### Step 1: Clone the Repository

```bash
git clone <your-repo-link>
cd <your-project-directory>
