# 🧭 NeuroNavigator

**Your AI-Powered Autonomous Agent Team for Travel & Research**

NeuroNavigator is an advanced multi-agent system designed to plan, research, budget, and execute complex missions autonomously. Built with a modular orchestrator pattern and a premium Streamlit UI, it leverages LLMs (Groq, OpenAI, or local Ollama) to turn high-level goals into actionable plans.

![App Screenshot](https://via.placeholder.com/800x400?text=NeuroNavigator+Dashboard) *Replace with actual screenshot*

## ✨ Features

- **🧠 Multi-Agent Orchestration**:
  - **Planner**: Breaks down goals into strategic steps.
  - **Researcher**: Gathers real-time insights and sources.
  - **Finance**: Estimates budgets using live APIs (Amadeus, Booking.com, Numbeo).
  - **Execution**: Generates day-by-day itineraries.
- **💻 Premium UI**: Dark-themed, responsive dashboard built with Streamlit and Altair.
- **🔌 Model Agnostic**: seamless switching between **Groq**, **OpenAI**, and **Local Ollama** models.
- **🛠️ Extensible Tools**: Modular tool system for Search, Weather, Flights, and Stocks.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (optional, for local inference)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Twilight-13/Neuro_Navigator.git
    cd Neuro_Navigator
    ```

2.  **Install Dependencies**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configuration**
    Copy `.env.example` (or create `.env`) and add your keys:
    ```env
    # Choose Provider: groq, openai, or ollama
    LLM_PROVIDER=ollama
    OLLAMA_MODEL=mistral

    # API Keys (Required for specific tools)
    SERPAPI_API_KEY=...
    AMADEUS_CLIENT_ID=...
    AMADEUS_CLIENT_SECRET=...
    RAPIDAPI_KEY=...
    ```

4.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

## 🏗️ Architecture

- **`orchestrator.py`**: The brain of the operation. Manages the async workflow of agents.
- **`config.py`**: Centralized configuration management and LLM factory.
- **`agents/`**: Specialized agent definitions using LangChain.
- **`tools/`**: Interface wrappers for external APIs.

## 🤝 Contributing

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
