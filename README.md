# GitHub Activity Analysis Agent

![GitHub Activity Analysis Agent](https://img.shields.io/badge/AI-Powered-blue)
![Status](https://img.shields.io/badge/Status-Active-green)

A low-code AI-powered tool for analyzing GitHub repository activity, with a focus on blockchain projects. This project demonstrates the application of AI/automation to solve real-world problems in blockchain research and development.

## 🌟 Project Overview

This tool helps blockchain researchers and developers track, analyze, and summarize developments across multiple blockchain projects. It offers both quantitative metrics and qualitative insights into repository activity, helping identify trends, key developments, and collaboration patterns.

![Screenshot](./docs/screenshot.png)

## ✨ Key Features

### Data Collection & Processing
- **Automated GitHub Data Retrieval**: Fetches repository data including commits, issues, PRs, and releases
- **Historical Data Analysis**: Analyze repository activity over customizable time ranges
- **Multi-Repository Support**: Track and compare multiple blockchain projects simultaneously
- **Data Persistence**: Save repository data locally for offline analysis

### Visualization & Analysis
- **Repository Overview**: Key metrics dashboard showing stars, forks, activity counts
- **Contributor Analysis**: Identify top contributors and collaboration patterns
- **Activity Timelines**: Track development velocity across projects
- **Recent Activity Dashboard**: See the latest commits, issues, and pull requests

### AI-Powered Insights
- **Automated Summaries**: Generate concise, insightful summaries of repository activity
- **Key Development Identification**: AI identifies significant changes and emerging trends
- **Cross-Repository Comparison**: Compare activity patterns across different blockchain projects
- **Natural Language Querying**: Ask questions about repositories in plain English

## 🛠️ Technology Stack

- **Python**: Core programming language
- **Streamlit**: Interactive web dashboard
- **LangChain**: Orchestrates AI components and RAG implementation
- **OpenAI API**: Powers the AI analysis and natural language understanding
- **GitHub API**: Data collection from repositories
- **ChromaDB**: Vector database for RAG implementation
- **Plotly**: Data visualization components

## 🏃‍♂️ Getting Started

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
   REPOS=ethereum/go-ethereum,worldcoin/world-id-contracts
   ```

### Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run src/app.py
```

Or use the command-line interface:
```bash
python src/main.py
```

## 📊 Dashboard Features

### Repository Overview Tab
- Repository information (stars, forks, open issues)
- Activity summary (commits, issues, PRs, releases)
- Top contributors visualization
- Daily commit activity chart

### Activity Analysis Tab
- Detailed views of recent commits
- Issue tracking and visualization
- Pull request analysis
- Release information

### AI Insights Tab
- AI-generated activity summaries
- Key development identification
- Comparative analysis across repositories
- Trend detection

### Query Engine Tab
- Natural language interface to repository data
- RAG-enhanced responses for accurate insights
- Query across multiple repositories

## 💼 Use Cases

### For Blockchain Researchers
- Track development progress across multiple blockchain projects
- Identify emerging trends in blockchain technology
- Compare implementation approaches to similar problems
- Stay updated on protocol changes and upgrades

### For Blockchain Developers
- Monitor activity in dependencies and related projects
- Identify active areas of development to focus contributions
- Study code changes and architectural decisions
- Find cross-project collaboration opportunities

### For Project Managers
- Measure development velocity and contributor activity
- Identify bottlenecks in development workflows
- Track issue resolution and feature development timelines
- Generate activity reports for stakeholders

## 🔍 Example Queries

The Query Engine supports questions like:
- "What are the most active areas of development in the Ethereum codebase?"
- "How has the focus on ZK-proofs evolved across projects?"
- "Which contributors are working across multiple projects?"
- "What are the recent security-related changes?"
- "Summarize the key changes in the last release"

## 🚀 Future Enhancements

- **Additional Data Sources**: Integration with Discord, forums, and documentation repositories
- **Smart Contract Analysis**: Specialized tracking of changes to smart contract code
- **Customizable Metrics**: User-defined KPIs and tracking metrics
- **Notification System**: Alerts for significant developments
- **Export Capabilities**: Report generation in various formats

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Uses the [GitHub API](https://docs.github.com/en/rest)
- Dashboard created with [Streamlit](https://streamlit.io/)
- Inspired by the needs of blockchain researchers and developers
