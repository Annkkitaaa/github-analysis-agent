# GitHub Activity Analysis Agent

A low-code AI-powered tool for analyzing GitHub repository activity, with a focus on blockchain projects. This project demonstrates the application of AI/automation to solve real-world problems in blockchain research and development.

## Project Overview

This tool helps blockchain researchers and developers track, analyze, and summarize developments across multiple blockchain projects. It:

1. Collects GitHub activity data (commits, issues, PRs, releases)
2. Analyzes patterns and trends using AI
3. Generates insightful summaries and reports
4. Provides a query interface for exploring repository data

## Key Features

- **Automated Data Collection**: Fetches repository activity using the GitHub API
- **AI-Powered Analysis**: Uses LLMs to identify key developments and trends
- **Multi-Repository Comparison**: Compares activity across different blockchain projects
- **Interactive Dashboard**: Visual interface for exploring repository data
- **Natural Language Querying**: Ask questions about repositories in plain English
- **RAG-Enhanced Responses**: Uses Retrieval-Augmented Generation for accurate insights

## Technology Stack

- **Python**: Core programming language
- **Streamlit**: Interactive web dashboard
- **LangChain**: Orchestrating AI components
- **OpenAI API**: LLM for analysis and insights
- **ChromaDB**: Vector database for RAG implementation
- **Plotly**: Data visualization
- **GitHub API**: Data collection

## Getting Started

### Prerequisites

- Python 3.8+
- GitHub API token
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/github-analysis-agent.git
   cd github-analysis-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API credentials:
   ```
   GITHUB_TOKEN=your_github_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   REPOS=ethereum/go-ethereum,starkware-libs/starknet-sdk
   ```

### Running the Application

Run the Streamlit dashboard:
```bash
streamlit run src/app.py
```

Or use the command-line interface:
```bash
python src/main.py
```

## Project Structure

```
github-analysis-agent/
├── data/               # Stored repository data and reports
├── src/
│   ├── api/            # GitHub API client
│   ├── agents/         # LLM agent implementations
│   ├── db/             # Vector database functionality
│   ├── utils/          # Data processing utilities
│   ├── app.py          # Streamlit dashboard
│   └── main.py         # CLI application
├── .env                # Environment variables
└── README.md           # Project documentation
```

## Usage Examples

### Tracking Development Activity

Monitor commit activity across multiple blockchain repositories to identify active areas of development and emerging patterns.

### Comparing Project Approaches

Compare how different blockchain projects approach similar technical challenges, based on their repository activity.

### Identifying Cross-Project Trends

Discover trends that span multiple blockchain projects to get early insights into industry direction.

### Answering Research Questions

Use the query engine to ask specific questions about repository activity:
- "What are the most active areas of development in the Ethereum codebase?"
- "How has the focus on ZK-proofs evolved across projects?"
- "Which contributors are working across multiple projects?"

## Extending the Project

The modular design makes it easy to extend:

1. Add more data sources (Discord, forums, etc.)
2. Implement additional analysis agents
3. Create custom visualizations
4. Add project-specific metrics and insights

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Uses the [GitHub API](https://docs.github.com/en/rest)
- Dashboard created with [Streamlit](https://streamlit.io/)