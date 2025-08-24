import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from github import Github
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from config import settings

class GitHubAgent:
    """Agent 1: GitHub MCP Coordinator for real-time commit reports"""
    
    def __init__(self):
        self.github = Github(settings.github_token) if settings.github_token else None
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        self.repo = None
        self._setup_repo()
        
    def _setup_repo(self):
        """Initialize GitHub repository connection"""
        if self.github and settings.github_repo_owner and settings.github_repo_name:
            try:
                self.repo = self.github.get_repo(f"{settings.github_repo_owner}/{settings.github_repo_name}")
                logging.info(f"Connected to repository: {self.repo.full_name}")
            except Exception as e:
                logging.error(f"Failed to connect to repository: {e}")
    
    async def get_daily_commits(self, days_back: int = 1) -> List[Dict]:
        """Fetch commits from the last N days"""
        if not self.repo:
            return []
        
        since_date = datetime.now() - timedelta(days=days_back)
        commits = []
        
        try:
            # Get all commits first, then filter by date
            all_commits = list(self.repo.get_commits())
            
            if not all_commits:
                logging.info("No commits found in repository")
                return []
            
            # Filter commits by date
            for commit in all_commits:
                commit_date = commit.commit.author.date
                if commit_date >= since_date:
                    commit_data = {
                        'sha': commit.sha[:8],
                        'message': commit.commit.message,
                        'author': commit.commit.author.name,
                        'date': commit.commit.author.date.isoformat(),
                        'url': commit.html_url,
                        'files_changed': len(commit.files) if commit.files else 0,
                        'additions': commit.stats.additions if commit.stats else 0,
                        'deletions': commit.stats.deletions if commit.stats else 0,
                        'total_changes': commit.stats.total if commit.stats else 0
                    }
                    commits.append(commit_data)
                    
            logging.info(f"Found {len(commits)} commits in the last {days_back} day(s)")
                
        except Exception as e:
            if "empty" in str(e).lower():
                logging.info("Repository is empty - no commits available")
                return []
            else:
                logging.error(f"Error fetching commits: {e}")
            
        return commits
    
    async def get_pull_requests(self, state: str = "open") -> List[Dict]:
        """Fetch pull requests"""
        if not self.repo:
            return []
        
        prs = []
        try:
            for pr in self.repo.get_pulls(state=state):
                pr_data = {
                    'number': pr.number,
                    'title': pr.title,
                    'author': pr.user.login,
                    'created_at': pr.created_at.isoformat(),
                    'state': pr.state,
                    'url': pr.html_url,
                    'additions': pr.additions,
                    'deletions': pr.deletions,
                    'changed_files': pr.changed_files
                }
                prs.append(pr_data)
        except Exception as e:
            logging.error(f"Error fetching pull requests: {e}")
            
        return prs
    
    async def get_repository_stats(self) -> Dict:
        """Get repository statistics"""
        if not self.repo:
            return {}
        
        try:
            stats = {
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'description': self.repo.description,
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count,
                'open_issues': self.repo.open_issues_count,
                'language': self.repo.language,
                'size': self.repo.size,
                'created_at': self.repo.created_at.isoformat(),
                'updated_at': self.repo.updated_at.isoformat(),
                'default_branch': self.repo.default_branch
            }
            return stats
        except Exception as e:
            logging.error(f"Error fetching repository stats: {e}")
            return {}
    
    async def generate_daily_report(self, days_back: int = 1) -> str:
        """Generate AI-powered daily commit report"""
        commits = await self.get_daily_commits(days_back)
        prs = await self.get_pull_requests("open")
        repo_stats = await self.get_repository_stats()
        
        if not commits and not prs:
            return "No activity found for the specified period."
        
        system_prompt = """You are a GitHub activity analyst. Generate a comprehensive daily report based on the provided repository data. 

Include:
1. Executive Summary
2. Commit Activity Analysis
3. Pull Request Status
4. Developer Contributions
5. Code Quality Insights
6. Recommendations

Format the report professionally with clear sections and actionable insights."""

        human_prompt = f"""Generate a daily GitHub activity report for the following data:

Repository: {repo_stats.get('full_name', 'Unknown')}
Period: Last {days_back} day(s)

Commits ({len(commits)}):
{self._format_commits_for_prompt(commits)}

Pull Requests ({len(prs)}):
{self._format_prs_for_prompt(prs)}

Repository Stats:
- Stars: {repo_stats.get('stars', 0)}
- Forks: {repo_stats.get('forks', 0)}
- Open Issues: {repo_stats.get('open_issues', 0)}
- Primary Language: {repo_stats.get('language', 'Unknown')}
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error generating AI report: {e}")
            return self._generate_fallback_report(commits, prs, repo_stats)
    
    def _format_commits_for_prompt(self, commits: List[Dict]) -> str:
        """Format commits data for AI prompt"""
        if not commits:
            return "No commits found."
        
        formatted = []
        for commit in commits[:10]:  # Limit to 10 most recent
            formatted.append(f"- {commit['sha']}: {commit['message'][:100]}... by {commit['author']} (+{commit['additions']}/-{commit['deletions']})")
        
        return "\n".join(formatted)
    
    def _format_prs_for_prompt(self, prs: List[Dict]) -> str:
        """Format pull requests data for AI prompt"""
        if not prs:
            return "No open pull requests."
        
        formatted = []
        for pr in prs[:5]:  # Limit to 5 most recent
            formatted.append(f"- #{pr['number']}: {pr['title']} by {pr['author']} ({pr['state']})")
        
        return "\n".join(formatted)
    
    def _generate_fallback_report(self, commits: List[Dict], prs: List[Dict], repo_stats: Dict) -> str:
        """Generate a basic report if AI fails"""
        report = f"# GitHub Activity Report\n\n"
        report += f"**Repository:** {repo_stats.get('full_name', 'Unknown')}\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"## Commit Summary\n"
        report += f"- Total commits: {len(commits)}\n"
        if commits:
            total_additions = sum(c['additions'] for c in commits)
            total_deletions = sum(c['deletions'] for c in commits)
            report += f"- Lines added: {total_additions}\n"
            report += f"- Lines deleted: {total_deletions}\n"
        
        report += f"\n## Pull Requests\n"
        report += f"- Open PRs: {len(prs)}\n"
        
        return report

    async def schedule_daily_reports(self):
        """Schedule daily report generation"""
        while True:
            try:
                report = await self.generate_daily_report()
                logging.info("Daily report generated successfully")
                print(f"\n{'='*50}")
                print("DAILY GITHUB REPORT")
                print(f"{'='*50}")
                print(report)
                print(f"{'='*50}\n")
            except Exception as e:
                logging.error(f"Error in scheduled report: {e}")
            
            # Wait for next report (24 hours by default)
            await asyncio.sleep(settings.report_schedule_hours * 3600)
