import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from agents import GitHubAgent, AnalysisAgent, PRDAgent
from config import settings
from output_formatter import format_output, create_section_header

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MultiAgentOrchestrator:
    """Main orchestrator for coordinating all three agents"""
    
    def __init__(self):
        self.github_agent = GitHubAgent()
        self.analysis_agent = AnalysisAgent()
        self.prd_agent = PRDAgent()
        
    async def run_github_report(self, days_back: int = 1) -> str:
        """Run GitHub reporting agent"""
        logging.info("Starting GitHub report generation...")
        try:
            report = await self.github_agent.generate_daily_report(days_back)
            commits = await self.github_agent.get_daily_commits(days_back)
            prs = await self.github_agent.get_pull_requests("open")
            repo_stats = await self.github_agent.get_repository_stats()
            
            # Format the output using AI minimization
            report_data = {
                'report': report,
                'commits': commits,
                'pull_requests': prs,
                'repository_stats': repo_stats
            }
            
            formatted_output = await format_output('github', report_data)
            
            print(create_section_header("GitHub Activity Report", "📊"))
            print(formatted_output)
            print("─" * 50)
            
            return formatted_output
        except Exception as e:
            logging.error(f"Error in GitHub report: {e}")
            return f"❌ **Error generating GitHub report:** {e}"
    
    async def run_product_analysis(self) -> Dict:
        """Run product requirements analysis"""
        logging.info("Starting product requirements analysis...")
        
        # Get user input for product requirements
        print("\n" + "="*60)
        print("PRODUCT REQUIREMENTS INPUT")
        print("="*60)
        
        product_name = input("Enter product/feature name: ").strip()
        if not product_name:
            product_name = "New Product Feature"
            
        product_description = input("Enter product description: ").strip()
        if not product_description:
            product_description = "Product feature to be analyzed"
            
        target_users = input("Enter target users (e.g., developers, end-users): ").strip()
        if not target_users:
            target_users = "General users"
            
        business_goals = input("Enter business goals (comma-separated): ").strip()
        goals_list = [goal.strip() for goal in business_goals.split(",")] if business_goals else ["Improve user experience"]
        
        technical_stack = input("Enter technical stack/technologies: ").strip()
        tech_list = [tech.strip() for tech in technical_stack.split(",")] if technical_stack else ["Web application"]
        
        constraints = input("Enter known constraints (comma-separated): ").strip()
        constraints_list = [constraint.strip() for constraint in constraints.split(",")] if constraints else ["Budget limitations"]
        
        # Create user requirements data
        user_requirements = {
            'user_input': {
                'source': 'user_requirements',
                'product_name': product_name,
                'description': product_description,
                'target_users': target_users,
                'business_goals': goals_list,
                'technical_stack': tech_list,
                'constraints': constraints_list,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            analysis_result = await self.analysis_agent.analyze_product_requirements_with_input(user_requirements)
            
            # Format the output using AI minimization
            analysis_data = {
                'analysis_result': analysis_result,
                'user_input': user_requirements,
                'status': 'success'
            }
            
            formatted_output = await format_output('analysis', analysis_data)
            
            print(create_section_header("Product Analysis Results", "🎯"))
            print(formatted_output)
            print("─" * 50)
            
            return analysis_data
        except Exception as e:
            logging.error(f"Error in product analysis: {e}")
            return {
                'analysis_result': None,
                'status': 'error',
                'error': str(e)
            }
    
    async def run_prd_generation(self, analysis_result, project_context: Dict = None) -> Dict:
        """Run PRD and Gherkin generation"""
        logging.info("Starting PRD and Gherkin generation...")
        try:
            prd_agent = PRDAgent()
            
            # Handle None project_context
            context_data = {}
            if project_context:
                context_data = {
                    'user_requirements': project_context.get('user_requirements', {}),
                    'github_data': project_context.get('github_data', None)
                }
            
            documentation = await prd_agent.generate_complete_documentation(
                analysis_result, 
                project_context=context_data
            )
            
            # Format the output using AI minimization
            prd_data = {
                'documentation': documentation,
                'status': 'success'
            }
            
            formatted_output = await format_output('prd', prd_data)
            
            print(create_section_header("PRD Generation Completed", "📋"))
            print(formatted_output)
            print("─" * 50)
            
            return prd_data
        except Exception as e:
            logging.error(f"Error in PRD generation: {e}")
            return {
                'documentation': None,
                'status': 'error',
                'error': str(e)
            }
    
    async def run_complete_workflow(self, project_context: Dict = None, github_days: int = 1) -> Dict:
        """Run the complete multi-agent workflow"""
        logging.info("Starting complete multi-agent workflow...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'github_report': None,
            'analysis': None,
            'documentation': None,
            'status': 'in_progress'
        }
        
        try:
            # Step 1: Generate GitHub report
            print("🔄 Step 1: Generating GitHub Activity Report...")
            github_report = await self.run_github_report(github_days)
            results['github_report'] = github_report
            
            # Step 2: Run product analysis
            print("🔄 Step 2: Running Product Requirements Analysis...")
            analysis_result = await self.run_product_analysis()
            results['analysis'] = analysis_result
            
            if analysis_result['status'] == 'success':
                # Step 3: Generate PRD and Gherkin scenarios
                print("🔄 Step 3: Generating PRD and Gherkin Documentation...")
                documentation_result = await self.run_prd_generation(
                    analysis_result['analysis_result'], project_context
                )
                results['documentation'] = documentation_result
                
                if documentation_result['status'] == 'success':
                    results['status'] = 'completed'
                    print("✅ Complete workflow finished successfully!")
                else:
                    results['status'] = 'partial_success'
                    print("⚠️ Workflow completed with some errors in documentation generation")
            else:
                results['status'] = 'failed'
                print("❌ Workflow failed during analysis phase")
            
        except Exception as e:
            logging.error(f"Error in complete workflow: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
            print(f"❌ Workflow failed: {e}")
        
        # Format the complete workflow output
        formatted_output = await format_output('workflow', results)
        print(create_section_header("Workflow Summary", "🚀"))
        print(formatted_output)
        print("─" * 50)
        
        return results
    
    async def start_github_monitoring(self):
        """Start continuous GitHub monitoring"""
        print("🚀 Starting GitHub monitoring service...")
        await self.github_agent.schedule_daily_reports()
    
    def save_results_to_files(self, results: Dict, output_dir: str = "output"):
        """Save results to files"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save GitHub report
        if results.get('github_report'):
            with open(f"{output_dir}/github_report_{timestamp}.md", "w", encoding="utf-8") as f:
                f.write(results['github_report'])
        
        # Save analysis results
        if results.get('analysis') and results['analysis']['status'] == 'success':
            analysis = results['analysis']['analysis_result']
            with open(f"{output_dir}/analysis_{timestamp}.md", "w", encoding="utf-8") as f:
                f.write(f"# Product Analysis Results\n\n")
                f.write(f"## Goals\n")
                for goal in analysis.goals:
                    f.write(f"- {goal}\n")
                f.write(f"\n## Constraints\n")
                for constraint in analysis.constraints:
                    f.write(f"- {constraint}\n")
                f.write(f"\n## Edge Cases\n")
                for case in analysis.edge_cases:
                    f.write(f"- {case}\n")
                f.write(f"\n## Follow-up Questions\n")
                for question in analysis.follow_up_questions:
                    f.write(f"- {question}\n")
                f.write(f"\n## Impact Analysis\n")
                for key, value in analysis.impact_analysis.items():
                    f.write(f"- **{key}**: {value}\n")
                f.write(f"\n## Recommendations\n")
                for rec in analysis.recommendations:
                    f.write(f"- {rec}\n")
        
        # Save PRD and Gherkin
        if results.get('documentation') and results['documentation']['status'] == 'success':
            docs = results['documentation']['documentation']
            
            with open(f"{output_dir}/prd_{timestamp}.md", "w", encoding="utf-8") as f:
                f.write(docs['prd'])
            
            with open(f"{output_dir}/gherkin_{timestamp}.feature", "w", encoding="utf-8") as f:
                f.write(docs['gherkin'])
        
        print(f"📁 Results saved to {output_dir}/ directory")

async def main():
    """Main entry point"""
    orchestrator = MultiAgentOrchestrator()
    
    print("🤖 Multi-Agent System Started")
    print("=" * 50)
    print("Available Commands:")
    print("1. GitHub Report Only")
    print("2. Product Analysis Only") 
    print("3. Complete Workflow")
    print("4. Start GitHub Monitoring")
    print("5. Exit")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                days = int(input("Enter number of days to analyze (default 1): ") or "1")
                await orchestrator.run_github_report(days)
                
            elif choice == "2":
                result = await orchestrator.run_product_analysis()
                if result['status'] == 'success':
                    print("Analysis completed successfully!")
                else:
                    print(f"Analysis failed: {result.get('error', 'Unknown error')}")
                    
            elif choice == "3":
                days = int(input("Enter number of days for GitHub analysis (default 1): ") or "1")
                save_files = input("Save results to files? (y/n): ").lower() == 'y'
                
                results = await orchestrator.run_complete_workflow(github_days=days)
                
                if save_files:
                    orchestrator.save_results_to_files(results)
                
                print(f"\nWorkflow Status: {results['status']}")
                
            elif choice == "4":
                print("Starting continuous GitHub monitoring...")
                await orchestrator.start_github_monitoring()
                
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
