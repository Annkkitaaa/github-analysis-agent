import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.docstore.document import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMAgent:
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.1
        )
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def generate_activity_summary(self, repo_data: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of repository activity."""
        repo_name = repo_data['repo_name']
        time_period = repo_data['time_period']
        
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""You are a technical analyst specialized in blockchain development. 
                Your task is to analyze GitHub repository activity and provide a concise but insightful summary.
                Focus on highlighting important development trends, key changes, and significant discussions.
                Be specific about what you observe in the data, and try to identify patterns that would be
                valuable for a blockchain developer or researcher."""),
                HumanMessage(content="""
                Please analyze the following GitHub repository activity data and provide a concise, insightful summary.
                Focus on key developments, important changes, and significant trends.
                
                Repository: {repo_name}
                Time period: {time_period}
                
                COMMITS:
                {commit_data}
                
                ISSUES:
                {issue_data}
                
                PULL REQUESTS:
                {pr_data}
                
                RELEASES:
                {release_data}
                
                Your summary should be professional, technical, and highlight the most important developments
                that a blockchain developer or researcher would find valuable.
                """)
            ]
        )
        
        # Prepare commit data
        commit_str = "No commits in this period."
        if repo_data.get('commits'):
            commits = repo_data['commits'][:20]  # Limit to 20 most recent commits
            commit_lines = [
                f"- {commit['sha'][:7]} by {commit['author']}: {commit['message']}"
                for commit in commits
            ]
            commit_str = "\n".join(commit_lines)
        
        # Prepare issue data
        issue_str = "No issues in this period."
        if repo_data.get('issues'):
            issues = repo_data['issues'][:10]  # Limit to 10 most recent issues
            issue_lines = [
                f"- #{issue['number']} - {issue['title']} (by {issue['author']}, state: {issue['state']})"
                for issue in issues
            ]
            issue_str = "\n".join(issue_lines)
        
        # Prepare PR data
        pr_str = "No pull requests in this period."
        if repo_data.get('pull_requests'):
            prs = repo_data['pull_requests'][:10]  # Limit to 10 most recent PRs
            pr_lines = [
                f"- #{pr['number']} - {pr['title']} (by {pr['author']}, state: {pr['state']})"
                for pr in prs
            ]
            pr_str = "\n".join(pr_lines)
        
        # Prepare release data
        release_str = "No releases in this period."
        if repo_data.get('releases'):
            releases = repo_data['releases']
            release_lines = [
                f"- {release['tag_name']} - {release['name']} (by {release['author']})"
                for release in releases
            ]
            release_str = "\n".join(release_lines)
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({
            "repo_name": repo_name,
            "time_period": time_period,
            "commit_data": commit_str,
            "issue_data": issue_str,
            "pr_data": pr_str,
            "release_data": release_str
        })
        
        return result['text']
    
    def identify_key_developments(self, repo_data: Dict[str, Any]) -> List[str]:
        """Identify key developments and points of interest in the repository activity."""
        repo_name = repo_data['repo_name']
        
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""You are a blockchain development analyst specializing in identifying 
                significant trends and developments in GitHub repositories. Your task is to analyze repository activity 
                and extract the 3-5 most important developments or points of interest, especially those related
                to blockchain technology, smart contracts, or decentralized systems."""),
                HumanMessage(content="""
                Based on the following GitHub repository activity, identify the 3-5 most important 
                developments or points of interest. Focus on significant code changes, important technical discussions,
                or emerging technical directions.
                
                Repository: {repo_name}
                
                COMMITS:
                {commit_data}
                
                ISSUES:
                {issue_data}
                
                PULL REQUESTS:
                {pr_data}
                
                List each key development as a separate point in this format:
                1. [TITLE OF DEVELOPMENT]: Brief explanation of why this is significant.
                """)
            ]
        )
        
        # Prepare commit data
        commit_str = "No commits in this period."
        if repo_data.get('commits'):
            commits = repo_data['commits'][:30]  # Include more commits for analysis
            commit_lines = [
                f"- {commit['sha'][:7]} by {commit['author']}: {commit['message']}"
                for commit in commits
            ]
            commit_str = "\n".join(commit_lines)
        
        # Prepare issue data
        issue_str = "No issues in this period."
        if repo_data.get('issues'):
            issues = repo_data['issues'][:15]  # Include more issues for analysis
            issue_lines = [
                f"- #{issue['number']} - {issue['title']} (by {issue['author']}, state: {issue['state']})"
                for issue in issues
            ]
            issue_str = "\n".join(issue_lines)
        
        # Prepare PR data
        pr_str = "No pull requests in this period."
        if repo_data.get('pull_requests'):
            prs = repo_data['pull_requests'][:15]  # Include more PRs for analysis
            pr_lines = [
                f"- #{pr['number']} - {pr['title']} (by {pr['author']}, state: {pr['state']})"
                for pr in prs
            ]
            pr_str = "\n".join(pr_lines)
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({
            "repo_name": repo_name,
            "commit_data": commit_str,
            "issue_data": issue_str,
            "pr_data": pr_str
        })
        
        # Split the result into separate points
        developments = result['text'].strip().split('\n\n')
        return [dev.strip() for dev in developments if dev.strip()]
    
    def compare_repositories(self, repo_data_list: List[Dict[str, Any]]) -> str:
        """Compare activity across multiple repositories to identify trends."""
        if len(repo_data_list) < 2:
            return "Need at least two repositories to compare."
        
        repo_summaries = []
        repo_names = []
        
        for repo_data in repo_data_list:
            repo_name = repo_data['repo_name']
            repo_names.append(repo_name)
            
            # Basic stats
            commit_count = len(repo_data.get('commits', []))
            issue_count = len(repo_data.get('issues', []))
            pr_count = len(repo_data.get('pull_requests', []))
            release_count = len(repo_data.get('releases', []))
            
            # Get unique contributors
            contributors = set()
            for commit in repo_data.get('commits', []):
                if 'author' in commit and commit['author']:
                    contributors.add(commit['author'])
            
            summary = f"""
            Repository: {repo_name}
            Activity:
            - Commits: {commit_count}
            - Issues: {issue_count}
            - PRs: {pr_count}
            - Releases: {release_count}
            - Contributors: {len(contributors)}
            """
            
            # Add some recent commit messages
            if repo_data.get('commits'):
                summary += "\nRecent commits:\n"
                for commit in repo_data['commits'][:5]:
                    summary += f"- {commit['message'][:100]}...\n"
            
            repo_summaries.append(summary)
        
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""You are a blockchain development analyst comparing activity across different repositories.
                Your task is to analyze the provided repository summaries and identify interesting patterns, connections, 
                or contrasts between the projects. Focus on technical aspects, development pace, community engagement, 
                and emerging trends that would be relevant to blockchain developers."""),
                HumanMessage(content="""
                Please compare the following blockchain repositories and provide insights on the differences
                and similarities in their recent development activity:
                
                {repo_summaries}
                
                In your analysis, consider:
                1. Which repositories are most active?
                2. Are there any common themes or parallel developments?
                3. How do the community dynamics differ?
                4. Are there technical approaches that one project is taking that others could benefit from?
                
                Provide a concise but insightful comparison that would help a blockchain researcher understand
                the current state and direction of these projects.
                """)
            ]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({
            "repo_summaries": "\n\n".join(repo_summaries)
        })
        
        return result['text']
    
    def setup_vector_db(self, repo_data_list: List[Dict[str, Any]]) -> Chroma:
        """Set up a vector database for RAG with repository data."""
        documents = []
        
        for repo_data in repo_data_list:
            repo_name = repo_data['repo_name']
            
            # Add commit messages
            for commit in repo_data.get('commits', []):
                doc = Document(
                    page_content=f"Commit in {repo_name}: {commit['message']}",
                    metadata={
                        "repo": repo_name,
                        "type": "commit",
                        "author": commit['author'],
                        "date": commit.get('date', ''),
                        "sha": commit.get('sha', '')
                    }
                )
                documents.append(doc)
            
            # Add issues
            for issue in repo_data.get('issues', []):
                doc = Document(
                    page_content=f"Issue in {repo_name}: {issue['title']}",
                    metadata={
                        "repo": repo_name,
                        "type": "issue",
                        "number": issue['number'],
                        "author": issue['author'],
                        "state": issue['state'],
                        "url": issue.get('url', '')
                    }
                )
                documents.append(doc)
            
            # Add pull requests
            for pr in repo_data.get('pull_requests', []):
                doc = Document(
                    page_content=f"Pull request in {repo_name}: {pr['title']}",
                    metadata={
                        "repo": repo_name,
                        "type": "pull_request",
                        "number": pr['number'],
                        "author": pr['author'],
                        "state": pr['state'],
                        "url": pr.get('url', '')
                    }
                )
                documents.append(doc)
        
        # Create vector store
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        return vectordb
    
    def query_repositories(self, vectordb: Chroma, query: str) -> str:
        """Query the repository data using RAG to answer specific questions."""
        retriever = vectordb.as_retriever(search_kwargs={"k": 10})
        
        # Use MultiQuery to generate multiple search queries
        multi_retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=self.llm
        )
        
        # Retrieve relevant documents
        docs = multi_retriever.get_relevant_documents(query)
        
        # Format retrieved context
        context = []
        for i, doc in enumerate(docs):
            context.append(f"{i+1}. {doc.page_content} [Source: {doc.metadata['repo']}, Type: {doc.metadata['type']}]")
        
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""You are a technical assistant specialized in blockchain development.
                Your task is to answer questions about GitHub repository activity based on the provided context."""),
                HumanMessage(content="""
                Based on the following information about blockchain repository activity, please answer this question:
                
                Question: {query}
                
                Context from repositories:
                {context}
                
                Provide a concise but informative answer based only on the provided context.
                """)
            ]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({
            "query": query,
            "context": "\n".join(context)
        })
        
        return result['text']