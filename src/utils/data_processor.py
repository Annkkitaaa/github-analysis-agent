import os
import json
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict, Any
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_repo_data(self, repo_data: Dict[str, Any]) -> str:
        """Save repository data to disk."""
        repo_name = repo_data['repo_name'].replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{repo_name}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(repo_data, f, indent=2)
        
        logging.info(f"Saved data for {repo_data['repo_name']} to {filepath}")
        return filepath
    
    def get_latest_data_files(self, days: int = 7) -> List[str]:
        """Get the latest data files for analysis."""
        all_files = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.json'):
                filepath = os.path.join(self.data_dir, file)
                all_files.append(filepath)
        
        return sorted(all_files, key=os.path.getmtime, reverse=True)
    
    def load_data_file(self, filepath: str) -> Dict[str, Any]:
        """Load data from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    
    def extract_contributor_stats(self, repo_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract contributor statistics from repository data."""
        commits = repo_data.get('commits', [])
        
        contributors = {}
        for commit in commits:
            author = commit.get('author', 'Unknown')
            if author not in contributors:
                contributors[author] = 0
            contributors[author] += 1
        
        df = pd.DataFrame(list(contributors.items()), columns=['Contributor', 'Commits'])
        df = df.sort_values('Commits', ascending=False).reset_index(drop=True)
        return df
    
    def extract_issue_stats(self, repo_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract issue statistics from repository data."""
        issues = repo_data.get('issues', [])
        
        # Create DataFrame
        if not issues:
            return pd.DataFrame(columns=['Number', 'Title', 'State', 'Author', 'Created', 'URL'])
            
        df = pd.DataFrame(issues)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Simplify for display
        display_df = df[['number', 'title', 'state', 'author', 'created_at', 'url']].copy()
        display_df.columns = ['Number', 'Title', 'State', 'Author', 'Created', 'URL']
        
        return display_df
    
    def extract_pr_stats(self, repo_data: Dict[str, Any]) -> pd.DataFrame:
        """Extract pull request statistics from repository data."""
        prs = repo_data.get('pull_requests', [])
        
        # Create DataFrame
        if not prs:
            return pd.DataFrame(columns=['Number', 'Title', 'State', 'Author', 'Created', 'URL'])
            
        df = pd.DataFrame(prs)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Simplify for display
        display_df = df[['number', 'title', 'state', 'author', 'created_at', 'url']].copy()
        display_df.columns = ['Number', 'Title', 'State', 'Author', 'Created', 'URL']
        
        return display_df
    
    def generate_repo_summary_text(self, repo_data: Dict[str, Any]) -> str:
        """Generate a text summary of repository activity."""
        repo_name = repo_data['repo_name']
        time_period = repo_data['time_period']
        
        commits = repo_data.get('commits', [])
        issues = repo_data.get('issues', [])
        prs = repo_data.get('pull_requests', [])
        releases = repo_data.get('releases', [])
        
        # Basic statistics
        commit_count = len(commits)
        issue_count = len(issues)
        pr_count = len(prs)
        release_count = len(releases)
        
        # Get unique contributors from commits
        contributors = set(commit.get('author', 'Unknown') for commit in commits)
        contributor_count = len(contributors)
        
        # Generate summary text
        summary = f"# Activity Summary for {repo_name} over the past {time_period}\n\n"
        summary += f"## Overview\n"
        summary += f"- Total commits: {commit_count}\n"
        summary += f"- New issues: {issue_count}\n"
        summary += f"- Pull requests: {pr_count}\n"
        summary += f"- New releases: {release_count}\n"
        summary += f"- Active contributors: {contributor_count}\n\n"
        
        # Add release information if available
        if releases:
            summary += f"## Latest Releases\n"
            for release in releases[:3]:  # Show up to 3 latest releases
                release_date = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                summary += f"- {release['tag_name']} - {release['name']} (released on {release_date})\n"
            summary += "\n"
        
        # Add top contributor information
        if commits:
            contributor_commits = {}
            for commit in commits:
                author = commit.get('author', 'Unknown')
                if author not in contributor_commits:
                    contributor_commits[author] = 0
                contributor_commits[author] += 1
            
            # Sort by number of commits
            top_contributors = sorted(contributor_commits.items(), key=lambda x: x[1], reverse=True)[:5]
            
            summary += f"## Top Contributors\n"
            for contributor, count in top_contributors:
                summary += f"- {contributor}: {count} commits\n"
            summary += "\n"
        
        # Add top discussed issues
        if issues:
            summary += f"## Notable Issues\n"
            for issue in issues[:5]:  # Show up to 5 latest issues
                created_date = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                summary += f"- #{issue['number']} - {issue['title']} (created on {created_date} by {issue['author']})\n"
            summary += "\n"
        
        # Add notable pull requests
        if prs:
            summary += f"## Notable Pull Requests\n"
            for pr in prs[:5]:  # Show up to 5 latest PRs
                created_date = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                summary += f"- #{pr['number']} - {pr['title']} (created on {created_date} by {pr['author']})\n"
            summary += "\n"
        
        return summary
    
    def generate_commit_activity_by_day(self, repo_data: Dict[str, Any]) -> pd.DataFrame:
        """Generate daily commit activity for visualization."""
        commits = repo_data.get('commits', [])
        
        if not commits:
            return pd.DataFrame(columns=['Date', 'Count'])
        
        # Extract dates and convert to datetime
        commit_dates = [commit.get('date', '') for commit in commits]
        date_df = pd.DataFrame({'date': commit_dates})
        date_df['date'] = pd.to_datetime(date_df['date'])
        
        # Group by day and count
        daily_counts = date_df.groupby(date_df['date'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Count']
        
        return daily_counts