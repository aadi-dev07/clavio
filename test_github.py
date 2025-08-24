import os
from dotenv import load_dotenv
from github import Github
from datetime import datetime, timedelta

load_dotenv()

def test_github_connection():
    """Test GitHub connection and repository access"""
    
    # Get credentials from environment
    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("GITHUB_REPO_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")
    
    print(f"Testing GitHub connection...")
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Token available: {'Yes' if github_token else 'No'}")
    print("-" * 50)
    
    if not github_token:
        print("❌ No GitHub token found!")
        return
    
    try:
        # Initialize GitHub client
        github = Github(github_token)
        
        # Test authentication
        user = github.get_user()
        print(f"✅ Authenticated as: {user.login}")
        
        # Get repository
        repo = github.get_repo(f"{repo_owner}/{repo_name}")
        print(f"✅ Repository found: {repo.full_name}")
        print(f"   Description: {repo.description or 'No description'}")
        print(f"   Language: {repo.language or 'Not specified'}")
        print(f"   Stars: {repo.stargazers_count}")
        print(f"   Forks: {repo.forks_count}")
        print(f"   Default branch: {repo.default_branch}")
        
        # Check if repository is empty
        try:
            # Try to get the default branch
            default_branch = repo.get_branch(repo.default_branch)
            print(f"✅ Default branch '{repo.default_branch}' exists")
            
            # Get total commit count
            commits = list(repo.get_commits())
            print(f"📊 Total commits: {len(commits)}")
            
            if commits:
                print(f"   Latest commit: {commits[0].commit.message[:50]}...")
                print(f"   Author: {commits[0].commit.author.name}")
                print(f"   Date: {commits[0].commit.author.date}")
                
                # Test commits in last 7 days
                since_date = datetime.now() - timedelta(days=7)
                recent_commits = list(repo.get_commits(since=since_date))
                print(f"   Commits in last 7 days: {len(recent_commits)}")
            else:
                print("   No commits found")
                
        except Exception as e:
            if "empty" in str(e).lower() or "409" in str(e):
                print("⚠️  Repository appears to be empty (no commits)")
            else:
                print(f"❌ Error accessing repository content: {e}")
        
        # Test issues
        try:
            issues = list(repo.get_issues(state='all'))
            print(f"📋 Total issues: {len(issues)}")
        except Exception as e:
            print(f"⚠️  Could not fetch issues: {e}")
            
        # Test pull requests
        try:
            prs = list(repo.get_pulls(state='all'))
            print(f"🔄 Total pull requests: {len(prs)}")
        except Exception as e:
            print(f"⚠️  Could not fetch pull requests: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "404" in str(e):
            print("   Repository not found or no access permission")
        elif "401" in str(e):
            print("   Authentication failed - check your token")

if __name__ == "__main__":
    test_github_connection()
