import os
import sys
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from api.github_api import GitHubAPI
from utils.data_processor import DataProcessor
from agents.llm_agent import LLMAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

def load_config():
    """Load configuration from .env file."""
    load_dotenv()
    
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    repos_str = os.getenv('REPOS', 'ethereum/go-ethereum')
    repos = [repo.strip() for repo in repos_str.split(',')]
    
    if not github_token:
        logging.error("GITHUB_TOKEN is not set in .env file")
        sys.exit(1)
    
    if not openai_api_key:
        logging.error("OPENAI_API_KEY is not set in .env file")
        sys.exit(1)
    
    return {
        'github_token': github_token,
        'openai_api_key': openai_api_key,
        'repos': repos
    }

def collect_github_data(github_token: str, repos: List[str], days: int = 7) -> List[Dict[str, Any]]:
    """Collect data from GitHub for the specified repositories."""
    github_api = GitHubAPI(github_token)
    data_processor = DataProcessor()
    
    all_repo_data = []
    
    for repo in repos:
        try:
            logging.info(f"Collecting data for {repo}")
            repo_data = github_api.process_repo_data(repo, days)
            
            # Save data to disk
            data_processor.save_repo_data(repo_data)
            
            all_repo_data.append(repo_data)
            
        except Exception as e:
            logging.error(f"Error collecting data for {repo}: {str(e)}")
    
    return all_repo_data

def generate_reports(openai_api_key: str, repo_data_list: List[Dict[str, Any]]):
    """Generate analysis reports for the collected data."""
    llm_agent = LLMAgent(openai_api_key)
    data_processor = DataProcessor()
    
    # Generate individual repository summaries
    for repo_data in repo_data_list:
        repo_name = repo_data['repo_name']
        logging.info(f"Generating summary for {repo_name}")
        
        # Generate basic stats and activity summary
        basic_summary = data_processor.generate_repo_summary_text(repo_data)
        
        # Generate LLM-enhanced summary
        llm_summary = llm_agent.generate_activity_summary(repo_data)
        
        # Identify key developments
        key_developments = llm_agent.identify_key_developments(repo_data)
        
        # Combine reports
        full_report = f"{basic_summary}\n\n## AI-Generated Activity Summary\n\n{llm_summary}\n\n"
        full_report += "## Key Developments\n\n"
        for development in key_developments:
            full_report += f"{development}\n\n"
        
        # Save report to disk
        timestamp = repo_data.get('collection_date', '').split('T')[0]
        report_filename = f"report_{repo_name.replace('/', '_')}_{timestamp}.md"
        with open(os.path.join('data', report_filename), 'w') as f:
            f.write(full_report)
        
        logging.info(f"Report saved to data/{report_filename}")
    
    # Generate comparative analysis if multiple repositories
    if len(repo_data_list) > 1:
        logging.info("Generating comparative analysis")
        comparison = llm_agent.compare_repositories(repo_data_list)
        
        # Save comparison report
        comparison_filename = f"comparison_report_{timestamp}.md"
        with open(os.path.join('data', comparison_filename), 'w') as f:
            f.write(f"# Comparative Analysis of Repositories\n\n{comparison}")
        
        logging.info(f"Comparison report saved to data/{comparison_filename}")
    
    # Setup vector database for querying
    logging.info("Setting up vector database for querying")
    vectordb = llm_agent.setup_vector_db(repo_data_list)
    
    return {
        'vectordb': vectordb,
        'llm_agent': llm_agent
    }

def main():
    """Main function to run the GitHub analysis agent."""
    config = load_config()
    
    # Check if data collection is needed or if we should use existing data
    use_existing = input("Use existing data? (y/n): ").lower() == 'y'
    
    if use_existing:
        # Load existing data
        data_processor = DataProcessor()
        data_files = data_processor.get_latest_data_files()
        
        if not data_files:
            logging.warning("No existing data files found. Will collect new data.")
            use_existing = False
        else:
            # Load the data files
            repo_data_list = []
            for file in data_files:
                repo_data = data_processor.load_data_file(file)
                repo_data_list.append(repo_data)
            
            logging.info(f"Loaded {len(repo_data_list)} existing data files")
    
    if not use_existing:
        # Collect new data
        days = int(input("How many days of history to collect? (default: 7): ") or 7)
        repo_data_list = collect_github_data(
            config['github_token'],
            config['repos'],
            days
        )
    
    # Generate reports and setup for querying
    result = generate_reports(config['openai_api_key'], repo_data_list)
    
    # Interactive query mode
    print("\nEnter queries about the repositories (type 'exit' to quit):")
    while True:
        query = input("\nQuery: ")
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        answer = result['llm_agent'].query_repositories(result['vectordb'], query)
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()