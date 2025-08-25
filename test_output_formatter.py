import asyncio
from output_formatter import format_output, create_section_header, format_bullet_list
from datetime import datetime

async def test_output_formatter():
    """Test the output formatter with sample data"""
    
    print("🧪 Testing Output Formatter\n")
    
    # Test GitHub report formatting
    github_data = {
        'report': 'Daily GitHub activity shows 5 commits with significant changes to the authentication system and database migrations. Pull requests are pending review for the new user dashboard feature.',
        'commits': [
            {'sha': 'abc123', 'message': 'Fix authentication bug', 'author': 'John Doe', 'additions': 45, 'deletions': 12},
            {'sha': 'def456', 'message': 'Add user dashboard', 'author': 'Jane Smith', 'additions': 120, 'deletions': 8},
            {'sha': 'ghi789', 'message': 'Update database schema', 'author': 'Bob Wilson', 'additions': 67, 'deletions': 23}
        ],
        'pull_requests': [
            {'number': 42, 'title': 'Feature: New user dashboard', 'author': 'jane_smith', 'state': 'open'},
            {'number': 43, 'title': 'Fix: Authentication issues', 'author': 'john_doe', 'state': 'open'}
        ],
        'repository_stats': {
            'full_name': 'company/awesome-app',
            'stars': 156,
            'forks': 23,
            'open_issues': 8
        }
    }
    
    print("📊 BEFORE (Verbose GitHub Data):")
    print(f"Report: {github_data['report']}")
    print(f"Commits: {len(github_data['commits'])} commits with detailed info")
    print(f"PRs: {len(github_data['pull_requests'])} pull requests")
    print(f"Stats: {github_data['repository_stats']}")
    
    print("\n📊 AFTER (Minimized GitHub Output):")
    github_formatted = await format_output('github', github_data)
    print(github_formatted)
    
    print("\n" + "="*60 + "\n")
    
    # Test Analysis formatting
    analysis_data = {
        'analysis_result': {
            'goals': [
                'Improve user authentication system security',
                'Enhance user dashboard functionality', 
                'Optimize database performance',
                'Implement real-time notifications',
                'Add mobile responsive design'
            ],
            'constraints': [
                'Limited development budget of $50k',
                'Must maintain backward compatibility',
                'Performance cannot degrade more than 5%',
                'Security compliance requirements'
            ],
            'recommendations': [
                'Implement OAuth 2.0 for authentication',
                'Use React for dashboard components',
                'Optimize database queries with indexing',
                'Add comprehensive error handling',
                'Conduct security audit before deployment'
            ],
            'impact_analysis': {
                'growth_potential': 'High - 30% user engagement increase expected',
                'revenue_impact': 'Positive - $200k annual revenue increase',
                'user_experience': 'Significantly improved',
                'technical_debt': 'Reduced by 40%'
            }
        },
        'status': 'success'
    }
    
    print("🎯 BEFORE (Verbose Analysis Data):")
    print(f"Goals: {len(analysis_data['analysis_result']['goals'])} detailed goals")
    print(f"Constraints: {len(analysis_data['analysis_result']['constraints'])} constraints")
    print(f"Recommendations: {len(analysis_data['analysis_result']['recommendations'])} recommendations")
    
    print("\n🎯 AFTER (Minimized Analysis Output):")
    analysis_formatted = await format_output('analysis', analysis_data)
    print(analysis_formatted)
    
    print("\n" + "="*60 + "\n")
    
    # Test utility functions
    print("🛠️ Testing Utility Functions:")
    
    print(create_section_header("Sample Section", "🔧"))
    
    sample_items = [
        "First important item with lots of details",
        "Second critical point that needs attention", 
        "Third recommendation for improvement",
        "Fourth suggestion for optimization",
        "Fifth item that might be less critical",
        "Sixth item that exceeds the limit"
    ]
    
    print("Formatted bullet list (max 4 items):")
    print(format_bullet_list(sample_items, max_items=4))
    
    print("\n✅ Output Formatter Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_output_formatter())
