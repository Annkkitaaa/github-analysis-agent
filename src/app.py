import os
import sys
import logging
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.github_api import GitHubAPI
from utils.data_processor import DataProcessor
from agents.llm_agent import LLMAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Load environment variables
load_dotenv()

# Initialize session state if not already done
if 'repo_data' not in st.session_state:
    st.session_state.repo_data = None
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'llm_agent' not in st.session_state:
    st.session_state.llm_agent = None
if 'reports_generated' not in st.session_state:
    st.session_state.reports_generated = False

# Set up the page
st.set_page_config(
    page_title="GitHub Activity Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for configuration
with st.sidebar:
    st.title("GitHub Analysis Agent")
    st.markdown("Analyze GitHub repositories for blockchain projects")
    
    # Configuration inputs
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token:
        github_token = st.text_input("GitHub Token", type="password")
        if not github_token:
            st.warning("Please provide a GitHub token to continue.")
    
    if not openai_api_key:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if not openai_api_key:
            st.warning("Please provide an OpenAI API key to continue.")
    
    # Repository input
    default_repos = os.getenv('REPOS', 'ethereum/go-ethereum')
    repos_input = st.text_area(
        "Repositories to analyze (one per line)",
        value=default_repos.replace(',', '\n')
    )
    repositories = [repo.strip() for repo in repos_input.split('\n') if repo.strip()]
    
    # Time period selector
    time_period = st.slider(
        "Days of history to analyze",
        min_value=1,
        max_value=30,
        value=7
    )
    
    # Data collection button
    if st.button("Collect GitHub Data"):
        if github_token and repositories:
            with st.spinner("Collecting data from GitHub..."):
                try:
                    github_api = GitHubAPI(github_token)
                    data_processor = DataProcessor()
                    
                    all_repo_data = []
                    for repo in repositories:
                        st.write(f"Collecting data for {repo}...")
                        repo_data = github_api.process_repo_data(repo, time_period)
                        data_processor.save_repo_data(repo_data)
                        all_repo_data.append(repo_data)
                    
                    st.session_state.repo_data = all_repo_data
                    st.success(f"Data collected successfully for {len(all_repo_data)} repositories!")
                    
                    # Initialize LLM agent
                    if openai_api_key:
                        st.session_state.llm_agent = LLMAgent(openai_api_key)
                except Exception as e:
                    st.error(f"Error collecting data: {str(e)}")
        else:
            st.error("GitHub token and repositories are required")

    # Load existing data
    if st.button("Load Latest Data"):
        data_processor = DataProcessor()
        data_files = data_processor.get_latest_data_files()
        
        if not data_files:
            st.warning("No existing data files found.")
        else:
            with st.spinner("Loading data files..."):
                # Load the data files
                repo_data_list = []
                for file in data_files:
                    repo_data = data_processor.load_data_file(file)
                    repo_data_list.append(repo_data)
                
                st.session_state.repo_data = repo_data_list
                st.success(f"Loaded {len(repo_data_list)} existing data files")
                
                # Initialize LLM agent
                if openai_api_key:
                    st.session_state.llm_agent = LLMAgent(openai_api_key)

    # Generate reports button
    if st.session_state.repo_data and st.session_state.llm_agent and st.button("Generate Analysis Reports"):
        with st.spinner("Generating reports..."):
            try:
                llm_agent = st.session_state.llm_agent
                data_processor = DataProcessor()
                
                # Generate individual repository summaries
                for repo_data in st.session_state.repo_data:
                    repo_name = repo_data['repo_name']
                    st.write(f"Generating summary for {repo_name}...")
                    
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
                
                # Generate comparative analysis if multiple repositories
                if len(st.session_state.repo_data) > 1:
                    st.write("Generating comparative analysis...")
                    comparison = llm_agent.compare_repositories(st.session_state.repo_data)
                    
                    # Save comparison report
                    timestamp = datetime.now().strftime('%Y-%m-%d')
                    comparison_filename = f"comparison_report_{timestamp}.md"
                    with open(os.path.join('data', comparison_filename), 'w') as f:
                        f.write(f"# Comparative Analysis of Repositories\n\n{comparison}")
                
                # Setup vector database for querying
                st.write("Setting up vector database for querying...")
                vectordb = llm_agent.setup_vector_db(st.session_state.repo_data)
                st.session_state.vector_db = vectordb
                
                st.session_state.reports_generated = True
                st.success("Reports generated successfully!")
            except Exception as e:
                st.error(f"Error generating reports: {str(e)}")

# Main content area
st.title("GitHub Activity Analysis Agent")

if not st.session_state.repo_data:
    st.info("Please collect GitHub data using the sidebar controls to get started.")
else:
    # Create tabs for different views
    tabs = st.tabs(["Repository Overview", "Activity Analysis", "AI Insights", "Query Engine"])
    
    # Tab 1: Repository Overview
    with tabs[0]:
        st.header("Repository Overview")
        
        # Select repository
        repo_names = [repo['repo_name'] for repo in st.session_state.repo_data]
        selected_repo = st.selectbox("Select Repository", repo_names)
        
        # Get the selected repository data
        repo_data = next((repo for repo in st.session_state.repo_data if repo['repo_name'] == selected_repo), None)
        
        if repo_data:
            # Display repository information
            st.subheader("Repository Information")
            repo_info = repo_data['repo_info']
            
            # Create two columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stars", f"{repo_info['stars']:,}")
            with col2:
                st.metric("Forks", f"{repo_info['forks']:,}")
            with col3:
                st.metric("Open Issues", f"{repo_info['open_issues']:,}")
            
            st.write(f"**Description:** {repo_info['description']}")
            st.write(f"**URL:** [{repo_info['url']}]({repo_info['url']})")
            
            # Activity Summary
            st.subheader("Activity Summary")
            
            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Commits", len(repo_data.get('commits', [])))
            with col2:
                st.metric("Issues", len(repo_data.get('issues', [])))
            with col3:
                st.metric("Pull Requests", len(repo_data.get('pull_requests', [])))
            with col4:
                st.metric("Releases", len(repo_data.get('releases', [])))
            
            # Contributors
            if repo_data.get('commits'):
                st.subheader("Top Contributors")
                
                # Extract contributor data
                data_processor = DataProcessor()
                contributor_df = data_processor.extract_contributor_stats(repo_data)
                
                # Display top contributors bar chart
                if not contributor_df.empty:
                    top_n = min(10, len(contributor_df))
                    fig = px.bar(
                        contributor_df.head(top_n),
                        x='Contributor',
                        y='Commits',
                        title=f"Top {top_n} Contributors by Commits",
                        color='Commits',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent Activity
            if repo_data.get('commits'):
                st.subheader("Recent Activity")
                
                # Create daily commit activity chart
                data_processor = DataProcessor()
                daily_activity = data_processor.generate_commit_activity_by_day(repo_data)
                
                if not daily_activity.empty:
                    fig = px.line(
                        daily_activity,
                        x='Date',
                        y='Count',
                        title="Daily Commit Activity",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Activity Analysis
    with tabs[1]:
        st.header("Activity Analysis")
        
        # Select repository
        repo_names = [repo['repo_name'] for repo in st.session_state.repo_data]
        selected_repo = st.selectbox("Select Repository", repo_names, key="activity_repo_select")
        
        # Get the selected repository data
        repo_data = next((repo for repo in st.session_state.repo_data if repo['repo_name'] == selected_repo), None)
        
        if repo_data:
            # Create tabs for different activity types
            activity_tabs = st.tabs(["Commits", "Issues", "Pull Requests", "Releases"])
            
            # Commits tab
            with activity_tabs[0]:
                st.subheader("Recent Commits")
                
                if repo_data.get('commits'):
                    # Create a DataFrame for display
                    commits = repo_data['commits']
                    commit_df = pd.DataFrame([
                        {
                            'SHA': commit['sha'][:7],
                            'Author': commit['author'],
                            'Message': commit['message'],
                            'Date': commit.get('date', ''),
                            'URL': commit.get('url', '')
                        }
                        for commit in commits
                    ])
                    
                    # Display the data
                    st.dataframe(
                        commit_df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Link")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No commits found for the selected time period.")
            
            # Issues tab
            with activity_tabs[1]:
                st.subheader("Recent Issues")
                
                if repo_data.get('issues'):
                    # Process issues with DataProcessor
                    data_processor = DataProcessor()
                    issue_df = data_processor.extract_issue_stats(repo_data)
                    
                    # Display the data
                    st.dataframe(
                        issue_df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Link")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No issues found for the selected time period.")
            
            # Pull Requests tab
            with activity_tabs[2]:
                st.subheader("Recent Pull Requests")
                
                if repo_data.get('pull_requests'):
                    # Process PRs with DataProcessor
                    data_processor = DataProcessor()
                    pr_df = data_processor.extract_pr_stats(repo_data)
                    
                    # Display the data
                    st.dataframe(
                        pr_df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Link")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No pull requests found for the selected time period.")
            
            # Releases tab
            with activity_tabs[3]:
                st.subheader("Recent Releases")
                
                if repo_data.get('releases'):
                    # Create a DataFrame for display
                    releases = repo_data['releases']
                    release_df = pd.DataFrame([
                        {
                            'Tag': release['tag_name'],
                            'Name': release['name'],
                            'Published': release.get('published_at', ''),
                            'Author': release.get('author', ''),
                            'URL': release.get('url', '')
                        }
                        for release in releases
                    ])
                    
                    # Display the data
                    st.dataframe(
                        release_df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Link")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No releases found for the selected time period.")
    
    # Tab 3: AI Insights
    with tabs[2]:
        st.header("AI-Generated Insights")
        
        if not st.session_state.reports_generated:
            st.warning("Please generate analysis reports first using the button in the sidebar.")
        else:
            # Select repository
            repo_names = [repo['repo_name'] for repo in st.session_state.repo_data]
            selected_repo = st.selectbox("Select Repository", repo_names, key="insights_repo_select")
            
            # Get the selected repository data
            repo_data = next((repo for repo in st.session_state.repo_data if repo['repo_name'] == selected_repo), None)
            
            if repo_data and st.session_state.llm_agent:
                # Generate insights if not already cached
                with st.spinner("Generating insights..."):
                    llm_summary = st.session_state.llm_agent.generate_activity_summary(repo_data)
                    key_developments = st.session_state.llm_agent.identify_key_developments(repo_data)
                
                # Display the AI-generated summary
                st.subheader("Activity Summary")
                st.markdown(llm_summary)
                
                # Display key developments
                st.subheader("Key Developments")
                for development in key_developments:
                    st.markdown(development)
                
                # Display comparative analysis if multiple repositories
                if len(st.session_state.repo_data) > 1:
                    st.subheader("Comparative Analysis")
                    with st.spinner("Generating comparison..."):
                        comparison = st.session_state.llm_agent.compare_repositories(st.session_state.repo_data)
                    st.markdown(comparison)
    
    # Tab 4: Query Engine
    with tabs[3]:
        st.header("Repository Query Engine")
        
        if not st.session_state.vector_db:
            if st.session_state.reports_generated:
                st.warning("Vector database not initialized. Please refresh the page.")
            else:
                st.warning("Please generate analysis reports first to initialize the query engine.")
        else:
            st.write("Ask questions about the repositories to get insights from the data.")
            
            query = st.text_input("Enter your question:")
            
            if query and st.button("Submit Query"):
                with st.spinner("Generating answer..."):
                    answer = st.session_state.llm_agent.query_repositories(st.session_state.vector_db, query)
                
                st.subheader("Answer")
                st.markdown(answer)

# Run the app with the command:
# streamlit run src/app.py