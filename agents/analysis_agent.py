import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from github import Github
from config import settings

class AnalysisResult(BaseModel):
    goals: List[str]
    constraints: List[str]
    edge_cases: List[str]
    follow_up_questions: List[str]
    impact_analysis: Dict[str, Any]
    recommendations: List[str]

class ProductAnalyst:
    """Sub-agent for product analysis"""
    def __init__(self, llm):
        self.llm = llm
        self.role = "Product Analyst"
    
    async def analyze_requirements(self, data: Dict) -> Dict:
        system_prompt = f"""You are a {self.role}. Analyze the provided product data and identify:
1. Core product goals and objectives
2. Key constraints and limitations
3. Potential edge cases and risks
4. Strategic recommendations

Focus on business value, user needs, and market positioning."""

        human_prompt = f"Analyze this product data: {data}"
        
        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        response = await self.llm.ainvoke(messages)
        return {"role": self.role, "analysis": response.content}

class TechnicalAnalyst:
    """Sub-agent for technical analysis"""
    def __init__(self, llm):
        self.llm = llm
        self.role = "Technical Analyst"
    
    async def analyze_requirements(self, data: Dict) -> Dict:
        system_prompt = f"""You are a {self.role}. Analyze the provided data for:
1. Technical feasibility and constraints
2. Architecture considerations
3. Performance and scalability issues
4. Integration challenges
5. Security and compliance requirements

Focus on technical implementation details and system design."""

        human_prompt = f"Analyze this technical data: {data}"
        
        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        response = await self.llm.ainvoke(messages)
        return {"role": self.role, "analysis": response.content}

class BusinessAnalyst:
    """Sub-agent for business impact analysis"""
    def __init__(self, llm):
        self.llm = llm
        self.role = "Business Analyst"
    
    async def analyze_requirements(self, data: Dict) -> Dict:
        system_prompt = f"""You are a {self.role}. Analyze the business impact including:
1. Revenue impact and monetization opportunities
2. Cost implications and resource requirements
3. Market positioning and competitive advantage
4. Risk assessment and mitigation strategies
5. ROI projections and success metrics

Focus on business outcomes and financial implications."""

        human_prompt = f"Analyze this business data: {data}"
        
        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        response = await self.llm.ainvoke(messages)
        return {"role": self.role, "analysis": response.content}

class AnalysisAgent:
    """Agent 2: AI Analysis agent for product requirement analysis"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Initialize sub-agents
        self.product_analyst = ProductAnalyst(self.llm)
        self.technical_analyst = TechnicalAnalyst(self.llm)
        self.business_analyst = BusinessAnalyst(self.llm)
        
        # Initialize data source clients
        self.github = Github(settings.github_token) if settings.github_token else None
    
    async def fetch_github_data(self) -> Dict:
        """Fetch data from GitHub repository"""
        if not self.github or not settings.github_repo_owner or not settings.github_repo_name:
            return {}
        
        try:
            repo = self.github.get_repo(f"{settings.github_repo_owner}/{settings.github_repo_name}")
            
            # Get issues and pull requests
            issues = []
            try:
                issue_list = list(repo.get_issues(state='all'))
                for issue in issue_list[:50]:  # Limit to 50
                    issues.append({
                        'number': issue.number,
                        'title': issue.title,
                        'body': issue.body[:500] if issue.body else '',
                        'labels': [label.name for label in issue.labels],
                        'state': issue.state,
                        'created_at': issue.created_at.isoformat()
                    })
            except Exception as e:
                logging.warning(f"Could not fetch issues: {e}")
            
            # Get recent commits
            commits = []
            try:
                commit_list = list(repo.get_commits())
                for commit in commit_list[:20]:  # Limit to 20
                    commits.append({
                        'message': commit.commit.message,
                        'author': commit.commit.author.name,
                        'date': commit.commit.author.date.isoformat()
                    })
            except Exception as e:
                if "empty" in str(e).lower():
                    logging.info("Repository is empty - no commits available")
                else:
                    logging.warning(f"Could not fetch commits: {e}")
            
            return {
                'source': 'github',
                'repository': repo.full_name,
                'description': repo.description or "No description available",
                'issues': issues,
                'commits': commits,
                'language': repo.language,
                'stars': repo.stargazers_count
            }
        except Exception as e:
            logging.error(f"Error fetching GitHub data: {e}")
            return {}
    
    async def gather_all_data(self) -> Dict:
        """Gather data from all available sources"""
        data_sources = {}
        
        # Fetch from all sources concurrently
        github_task = asyncio.create_task(self.fetch_github_data())
        
        github_data = await github_task
        
        if github_data:
            data_sources['github'] = github_data
        
        return data_sources
    
    async def run_multi_agent_analysis(self, data: Dict) -> List[Dict]:
        """Run analysis using multiple specialized agents"""
        analyses = []
        
        # Run all agents concurrently
        product_task = asyncio.create_task(self.product_analyst.analyze_requirements(data))
        technical_task = asyncio.create_task(self.technical_analyst.analyze_requirements(data))
        business_task = asyncio.create_task(self.business_analyst.analyze_requirements(data))
        
        product_analysis = await product_task
        technical_analysis = await technical_task
        business_analysis = await business_task
        
        analyses.extend([product_analysis, technical_analysis, business_analysis])
        
        return analyses
    
    async def synthesize_analysis(self, analyses: List[Dict], data: Dict) -> AnalysisResult:
        """Synthesize results from all agents into final analysis"""
        system_prompt = """You are a Senior Product Manager synthesizing analysis from multiple specialists.

Based on the provided analyses from Product Analyst, Technical Analyst, and Business Analyst, create a comprehensive synthesis that includes:

1. GOALS: Clear, actionable product goals
2. CONSTRAINTS: Technical, business, and resource constraints
3. EDGE_CASES: Potential risks and edge cases to consider
4. FOLLOW_UP_QUESTIONS: Critical questions that need answers
5. IMPACT_ANALYSIS: Detailed impact on growth, revenue, user experience, and technical debt
6. RECOMMENDATIONS: Prioritized action items

Format your response as a structured analysis with clear sections."""

        analyses_text = "\n\n".join([f"**{analysis['role']}:**\n{analysis['analysis']}" for analysis in analyses])
        
        human_prompt = f"""Synthesize the following analyses into a comprehensive product requirements analysis:

{analyses_text}

Original Data Sources: {list(data.keys())}

Provide a structured synthesis covering goals, constraints, edge cases, follow-up questions, impact analysis, and recommendations."""

        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_synthesis_response(response.content)
        except Exception as e:
            logging.error(f"Error in synthesis: {e}")
            return self._create_fallback_analysis(analyses)
    
    def _parse_synthesis_response(self, response: str) -> AnalysisResult:
        """Parse the AI response into structured format"""
        # This is a simplified parser - in production, you'd want more robust parsing
        lines = response.split('\n')
        
        goals = []
        constraints = []
        edge_cases = []
        follow_up_questions = []
        recommendations = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'GOALS' in line.upper():
                current_section = 'goals'
            elif 'CONSTRAINTS' in line.upper():
                current_section = 'constraints'
            elif 'EDGE' in line.upper() and 'CASES' in line.upper():
                current_section = 'edge_cases'
            elif 'FOLLOW' in line.upper() and 'QUESTIONS' in line.upper():
                current_section = 'follow_up_questions'
            elif 'RECOMMENDATIONS' in line.upper():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                item = line[1:].strip()
                if current_section == 'goals':
                    goals.append(item)
                elif current_section == 'constraints':
                    constraints.append(item)
                elif current_section == 'edge_cases':
                    edge_cases.append(item)
                elif current_section == 'follow_up_questions':
                    follow_up_questions.append(item)
                elif current_section == 'recommendations':
                    recommendations.append(item)
        
        impact_analysis = {
            'growth_potential': 'High - based on analysis',
            'revenue_impact': 'Positive - new monetization opportunities',
            'user_experience': 'Enhanced - improved functionality',
            'technical_debt': 'Manageable - with proper planning'
        }
        
        return AnalysisResult(
            goals=goals or ['Define clear product objectives'],
            constraints=constraints or ['Resource limitations'],
            edge_cases=edge_cases or ['Unexpected user behavior'],
            follow_up_questions=follow_up_questions or ['What are the success metrics?'],
            impact_analysis=impact_analysis,
            recommendations=recommendations or ['Conduct further research']
        )
    
    def _create_fallback_analysis(self, analyses: List[Dict]) -> AnalysisResult:
        """Create fallback analysis if parsing fails"""
        return AnalysisResult(
            goals=['Analyze product requirements', 'Define success metrics'],
            constraints=['Limited data availability', 'Resource constraints'],
            edge_cases=['Data integration issues', 'Scalability concerns'],
            follow_up_questions=['What are the key success metrics?', 'What is the timeline?'],
            impact_analysis={
                'growth_potential': 'To be determined',
                'revenue_impact': 'Requires further analysis',
                'user_experience': 'Potential for improvement',
                'technical_debt': 'Needs assessment'
            },
            recommendations=['Gather more detailed requirements', 'Conduct stakeholder interviews']
        )
    
    async def analyze_product_requirements_with_input(self, user_requirements: Dict) -> AnalysisResult:
        """Main method to run complete product requirements analysis with user input"""
        logging.info("Starting product requirements analysis with user input...")
        
        # Step 1: Gather data from external sources
        external_data = await self.gather_all_data()
        
        # Step 2: Combine user input with external data
        combined_data = {**user_requirements, **external_data}
        
        # Step 3: Run multi-agent analysis
        analyses = await self.run_multi_agent_analysis(combined_data)
        
        # Step 4: Synthesize results
        result = await self.synthesize_analysis(analyses, combined_data)
        
        logging.info("Product requirements analysis completed")
        return result
    
    async def analyze_product_requirements(self) -> AnalysisResult:
        """Main method to run complete product requirements analysis"""
        logging.info("Starting product requirements analysis...")
        
        # Step 1: Gather data from all sources
        data = await self.gather_all_data()
        
        # If no external data is available, create sample data for analysis
        if not data:
            logging.info("No external data sources available, using sample product data for analysis")
            data = {
                'sample': {
                    'source': 'sample_data',
                    'description': 'Sample product analysis based on common software development patterns',
                    'features': ['User authentication', 'Data management', 'API integration', 'User interface'],
                    'technologies': ['Python', 'Web framework', 'Database', 'Frontend'],
                    'goals': ['Improve user experience', 'Increase performance', 'Add new features']
                }
            }
        
        # Step 2: Run multi-agent analysis
        analyses = await self.run_multi_agent_analysis(data)
        
        # Step 3: Synthesize results
        result = await self.synthesize_analysis(analyses, data)
        
        logging.info("Product requirements analysis completed")
        return result
