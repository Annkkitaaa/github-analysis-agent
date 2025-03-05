import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.rate_limit_remaining = 5000
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make a request to the GitHub API with rate limit handling."""
        if self.rate_limit_remaining < 10:
            logging.warning("Rate limit low, waiting for reset...")
            time.sleep(60)
        
        response = requests.get(url, headers=self.headers, params=params)
        
        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 5000))
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403 and 'rate limit' in response.json().get('message', '').lower():
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            sleep_time = max(reset_time - time.time(), 0) + 10
            logging.warning(f"Rate limit exceeded. Waiting for {sleep_time} seconds")
            time.sleep(sleep_time)
            return self._make_request(url, params)
        else:
            logging.error(f"Error in API request: {response.status_code} - {response.text}")
            response.raise_for_status()
    
    def get_commits(self, repo: str, days: int = 7) -> List[Dict]:
        """Get commits for a repository in the last X days."""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {"since": since_date}
        
        commits = []
        page = 1
        
        while True:
            params["page"] = page
            data = self._make_request(url, params)
            
            if not data:
                break
                
            commits.extend(data)
            page += 1
            
            if len(data) < 30:  # GitHub API page size
                break
        
        return commits
    
    def get_issues(self, repo: str, days: int = 7, state: str = "all") -> List[Dict]:
        """Get issues for a repository in the last X days."""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{repo}/issues"
        params = {"since": since_date, "state": state}
        
        issues = []
        page = 1
        
        while True:
            params["page"] = page
            data = self._make_request(url, params)
            
            if not data:
                break
                
            issues.extend(data)
            page += 1
            
            if len(data) < 30:  # GitHub API page size
                break
        
        return issues
    
    def get_pull_requests(self, repo: str, days: int = 7, state: str = "all") -> List[Dict]:
        """Get pull requests for a repository in the last X days."""
        # In GitHub API, PRs are a subset of issues, but need additional filtering
        issues = self.get_issues(repo, days, state)
        pull_requests = [issue for issue in issues if 'pull_request' in issue]
        return pull_requests
    
    def get_releases(self, repo: str, days: int = 7) -> List[Dict]:
        """Get releases for a repository in the last X days."""
        url = f"{self.base_url}/repos/{repo}/releases"
        
        releases = []
        page = 1
        
        while True:
            params = {"page": page}
            data = self._make_request(url, params)
            
            if not data:
                break
            
            # Filter by date
            since_date = (datetime.now() - timedelta(days=days))
            recent_releases = [
                release for release in data 
                if datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ') > since_date
            ]
            
            releases.extend(recent_releases)
            page += 1
            
            if len(data) < 30 or len(recent_releases) < len(data):  # Stop if we've hit older releases
                break
        
        return releases
    
    def get_repository_info(self, repo: str) -> Dict:
        """Get basic information about a repository."""
        url = f"{self.base_url}/repos/{repo}"
        return self._make_request(url)

    def process_repo_data(self, repo: str, days: int = 7) -> Dict[str, Any]:
        """Process all relevant data for a repository into a structured format."""
        logging.info(f"Fetching data for {repo} over the past {days} days")
        
        try:
            repo_info = self.get_repository_info(repo)
            commits = self.get_commits(repo, days)
            issues = self.get_issues(repo, days)
            pull_requests = [pr for pr in issues if 'pull_request' in pr]
            issues = [issue for issue in issues if 'pull_request' not in issue]
            releases = self.get_releases(repo, days)
            
            # Process commits data
            commit_data = []
            for commit in commits:
                author = commit.get('author', {})
                commit_info = commit.get('commit', {})
                
                commit_data.append({
                    'sha': commit.get('sha', ''),
                    'author': author.get('login', 'Unknown') if author else commit_info.get('author', {}).get('name', 'Unknown'),
                    'date': commit_info.get('author', {}).get('date', ''),
                    'message': commit_info.get('message', '').split('\n')[0],  # Just get the first line
                    'url': commit.get('html_url', '')
                })
            
            # Process issues data
            issue_data = []
            for issue in issues:
                issue_data.append({
                    'number': issue.get('number', ''),
                    'title': issue.get('title', ''),
                    'state': issue.get('state', ''),
                    'created_at': issue.get('created_at', ''),
                    'updated_at': issue.get('updated_at', ''),
                    'author': issue.get('user', {}).get('login', 'Unknown'),
                    'labels': [label.get('name', '') for label in issue.get('labels', [])],
                    'url': issue.get('html_url', '')
                })
            
            # Process pull requests data
            pr_data = []
            for pr in pull_requests:
                pr_data.append({
                    'number': pr.get('number', ''),
                    'title': pr.get('title', ''),
                    'state': pr.get('state', ''),
                    'created_at': pr.get('created_at', ''),
                    'updated_at': pr.get('updated_at', ''),
                    'author': pr.get('user', {}).get('login', 'Unknown'),
                    'labels': [label.get('name', '') for label in pr.get('labels', [])],
                    'url': pr.get('html_url', '')
                })
            
            # Process releases data
            release_data = []
            for release in releases:
                release_data.append({
                    'tag_name': release.get('tag_name', ''),
                    'name': release.get('name', ''),
                    'published_at': release.get('published_at', ''),
                    'author': release.get('author', {}).get('login', 'Unknown'),
                    'url': release.get('html_url', '')
                })
            
            return {
                'repo_name': repo,
                'repo_info': {
                    'full_name': repo_info.get('full_name', ''),
                    'description': repo_info.get('description', ''),
                    'stars': repo_info.get('stargazers_count', 0),
                    'forks': repo_info.get('forks_count', 0),
                    'open_issues': repo_info.get('open_issues_count', 0),
                    'url': repo_info.get('html_url', '')
                },
                'commits': commit_data,
                'issues': issue_data,
                'pull_requests': pr_data,
                'releases': release_data,
                'time_period': f"{days} days",
                'collection_date': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error processing repo {repo}: {str(e)}")
            raise