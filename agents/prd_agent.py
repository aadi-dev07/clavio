import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from jinja2 import Template
from config import settings
from .analysis_agent import AnalysisResult

class PRDDocument(BaseModel):
    title: str
    overview: str
    objectives: List[str]
    success_metrics: List[str]
    user_stories: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    constraints: List[str]
    assumptions: List[str]
    risks: List[str]
    timeline: str
    resources: List[str]

class GherkinScenario(BaseModel):
    feature: str
    background: Optional[str]
    scenarios: List[Dict[str, Any]]

class PRDAgent:
    """Agent 3: PRD and Gherkin generator"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.2,  # Lower temperature for more structured output
            convert_system_message_to_human=True
        )
        
        # PRD Template
        self.prd_template = Template("""
# Product Requirements Document

## Product Title
{{ title }}

## Overview
{{ overview }}

## Objectives
{% for objective in objectives %}
- {{ objective }}
{% endfor %}

## Success Metrics
{% for metric in success_metrics %}
- {{ metric }}
{% endfor %}

## User Stories
{% for story in user_stories %}
- {{ story }}
{% endfor %}

## Functional Requirements
{% for req in functional_requirements %}
- {{ req }}
{% endfor %}

## Non-Functional Requirements
{% for req in non_functional_requirements %}
- {{ req }}
{% endfor %}

## Constraints
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}

## Assumptions
{% for assumption in assumptions %}
- {{ assumption }}
{% endfor %}

## Risks and Mitigation
{% for risk in risks %}
- {{ risk }}
{% endfor %}

## Timeline
{{ timeline }}

## Resources Required
{% for resource in resources %}
- {{ resource }}
{% endfor %}

---
*Generated on {{ generation_date }}*
        """)
    
    async def generate_prd(self, analysis_result: AnalysisResult, project_context: Dict = None) -> PRDDocument:
        """Generate a comprehensive PRD based on analysis results"""
        
        system_prompt = """You are a Senior Product Manager creating a comprehensive Product Requirements Document (PRD).

Based on the provided analysis, generate a detailed PRD that includes:
1. Clear product title and overview
2. Specific, measurable objectives
3. Success metrics and KPIs
4. Detailed user stories
5. Functional and non-functional requirements
6. Constraints and assumptions
7. Risk assessment
8. Timeline estimates
9. Resource requirements

Make the PRD actionable, specific, and aligned with business goals."""

        context_info = f"Project Context: {project_context}" if project_context else "No additional context provided."
        
        human_prompt = f"""Create a comprehensive PRD based on this analysis:

GOALS:
{chr(10).join(f'- {goal}' for goal in analysis_result.goals)}

CONSTRAINTS:
{chr(10).join(f'- {constraint}' for constraint in analysis_result.constraints)}

EDGE CASES:
{chr(10).join(f'- {case}' for case in analysis_result.edge_cases)}

FOLLOW-UP QUESTIONS:
{chr(10).join(f'- {question}' for question in analysis_result.follow_up_questions)}

IMPACT ANALYSIS:
{chr(10).join(f'- {key}: {value}' for key, value in analysis_result.impact_analysis.items())}

RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in analysis_result.recommendations)}

{context_info}

Generate a structured PRD with specific sections for objectives, user stories, requirements, etc."""

        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_prd_response(response.content, analysis_result)
        except Exception as e:
            logging.error(f"Error generating PRD: {e}")
            return self._create_fallback_prd(analysis_result)
    
    def _parse_prd_response(self, response: str, analysis_result: AnalysisResult) -> PRDDocument:
        """Parse AI response into structured PRD format"""
        lines = response.split('\n')
        
        title = "Product Requirements Document"
        overview = ""
        objectives = []
        success_metrics = []
        user_stories = []
        functional_requirements = []
        non_functional_requirements = []
        constraints = analysis_result.constraints
        assumptions = []
        risks = []
        timeline = "To be determined based on resource allocation"
        resources = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Extract title
            if line.startswith('# ') and 'title' in line.lower():
                title = line[2:].strip()
                continue
            
            # Identify sections
            if 'overview' in line.lower() and ('##' in line or '#' in line):
                current_section = 'overview'
                continue
            elif 'objective' in line.lower() and ('##' in line or '#' in line):
                current_section = 'objectives'
                continue
            elif 'success' in line.lower() and 'metric' in line.lower():
                current_section = 'success_metrics'
                continue
            elif 'user' in line.lower() and 'stor' in line.lower():
                current_section = 'user_stories'
                continue
            elif 'functional' in line.lower() and 'requirement' in line.lower() and 'non' not in line.lower():
                current_section = 'functional_requirements'
                continue
            elif 'non-functional' in line.lower() or ('non' in line.lower() and 'functional' in line.lower()):
                current_section = 'non_functional_requirements'
                continue
            elif 'assumption' in line.lower():
                current_section = 'assumptions'
                continue
            elif 'risk' in line.lower():
                current_section = 'risks'
                continue
            elif 'timeline' in line.lower():
                current_section = 'timeline'
                continue
            elif 'resource' in line.lower():
                current_section = 'resources'
                continue
            
            # Parse content based on current section
            if current_section == 'overview' and line and not line.startswith('#'):
                overview += line + " "
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                item = line[1:].strip()
                if current_section == 'objectives':
                    objectives.append(item)
                elif current_section == 'success_metrics':
                    success_metrics.append(item)
                elif current_section == 'user_stories':
                    user_stories.append(item)
                elif current_section == 'functional_requirements':
                    functional_requirements.append(item)
                elif current_section == 'non_functional_requirements':
                    non_functional_requirements.append(item)
                elif current_section == 'assumptions':
                    assumptions.append(item)
                elif current_section == 'risks':
                    risks.append(item)
                elif current_section == 'resources':
                    resources.append(item)
            elif current_section == 'timeline' and line and not line.startswith('#'):
                timeline = line
        
        return PRDDocument(
            title=title,
            overview=overview.strip() or "Product overview to be defined",
            objectives=objectives or analysis_result.goals,
            success_metrics=success_metrics or ["User engagement metrics", "Performance benchmarks"],
            user_stories=user_stories or ["As a user, I want to achieve my goals efficiently"],
            functional_requirements=functional_requirements or ["Core functionality implementation"],
            non_functional_requirements=non_functional_requirements or ["Performance", "Security", "Scalability"],
            constraints=constraints,
            assumptions=assumptions or ["Standard development practices"],
            risks=risks or analysis_result.edge_cases,
            timeline=timeline,
            resources=resources or ["Development team", "QA resources", "Infrastructure"]
        )
    
    def _create_fallback_prd(self, analysis_result: AnalysisResult) -> PRDDocument:
        """Create fallback PRD if parsing fails"""
        return PRDDocument(
            title="Product Requirements Document",
            overview="This document outlines the requirements for the proposed product feature.",
            objectives=analysis_result.goals,
            success_metrics=["User adoption rate", "Performance metrics", "Business impact"],
            user_stories=["As a user, I want to accomplish my tasks efficiently"],
            functional_requirements=["Implement core functionality", "Ensure data integrity"],
            non_functional_requirements=["System performance", "Security compliance", "Scalability"],
            constraints=analysis_result.constraints,
            assumptions=["Standard development practices", "Available resources"],
            risks=analysis_result.edge_cases,
            timeline="Development timeline to be determined",
            resources=["Development team", "QA resources", "Infrastructure support"]
        )
    
    async def generate_gherkin_scenarios(self, prd: PRDDocument, analysis_result: AnalysisResult = None) -> List[GherkinScenario]:
        """Generate Gherkin test scenarios based on PRD"""
        
        system_prompt = """You are a QA Engineer creating Gherkin test scenarios for BDD (Behavior-Driven Development).

Based on the provided PRD, create comprehensive Gherkin scenarios that cover:
1. Happy path scenarios
2. Edge cases and error handling
3. User acceptance criteria
4. Integration scenarios

Use proper Gherkin syntax:
- Feature: High-level description
- Background: Common setup (if needed)
- Scenario: Specific test case
- Given: Initial context
- When: Action performed
- Then: Expected outcome
- And/But: Additional steps

Create multiple features covering different aspects of the product."""

        human_prompt = f"""Create Gherkin test scenarios for this PRD:

TITLE: {prd.title}
OVERVIEW: {prd.overview}

USER STORIES:
{chr(10).join(f'- {story}' for story in prd.user_stories)}

FUNCTIONAL REQUIREMENTS:
{chr(10).join(f'- {req}' for req in prd.functional_requirements)}

NON-FUNCTIONAL REQUIREMENTS:
{chr(10).join(f'- {req}' for req in prd.non_functional_requirements)}

Generate comprehensive Gherkin scenarios covering main functionality, edge cases, and acceptance criteria."""

        messages = [
            HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_gherkin_response(response.content)
        except Exception as e:
            logging.error(f"Error generating Gherkin scenarios: {e}")
            return self._create_fallback_gherkin(prd, analysis_result)
    
    def _parse_gherkin_response(self, response: str) -> List[GherkinScenario]:
        """Parse AI response into Gherkin scenarios"""
        scenarios = []
        lines = response.split('\n')
        
        current_feature = None
        current_background = None
        current_scenario = None
        current_scenarios = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Feature:'):
                # Save previous feature if exists
                if current_feature and current_scenarios:
                    scenarios.append(GherkinScenario(
                        feature=current_feature,
                        background=current_background,
                        scenarios=current_scenarios
                    ))
                
                # Start new feature
                current_feature = line[8:].strip()
                current_background = None
                current_scenarios = []
                
            elif line.startswith('Background:'):
                current_background = line[11:].strip()
                
            elif line.startswith('Scenario:'):
                # Save previous scenario if exists
                if current_scenario:
                    current_scenarios.append(current_scenario)
                
                # Start new scenario
                current_scenario = {
                    'name': line[9:].strip(),
                    'steps': []
                }
                
            elif line.startswith(('Given ', 'When ', 'Then ', 'And ', 'But ')):
                if current_scenario:
                    current_scenario['steps'].append(line)
        
        # Save last scenario and feature
        if current_scenario:
            current_scenarios.append(current_scenario)
        if current_feature and current_scenarios:
            scenarios.append(GherkinScenario(
                feature=current_feature,
                background=current_background,
                scenarios=current_scenarios
            ))
        
        return scenarios or self._create_fallback_gherkin_scenarios()
    
    def _create_fallback_gherkin(self, prd: PRDDocument, analysis_result: AnalysisResult = None) -> List[GherkinScenario]:
        """Create fallback Gherkin scenarios"""
        return self._create_fallback_gherkin_scenarios(analysis_result)
    
    def _create_fallback_gherkin_scenarios(self, analysis_result: AnalysisResult = None) -> List[GherkinScenario]:
        """Create Gherkin scenarios based on analysis results"""
        if not analysis_result:
            return [
                GherkinScenario(
                    feature="Core Functionality",
                    background="Given the system is properly configured",
                    scenarios=[
                        {
                            'name': "Successful operation",
                            'steps': [
                                "Given I am a valid user",
                                "When I perform the main action",
                                "Then I should see the expected result"
                            ]
                        }
                    ]
                )
            ]
        
        # Generate scenarios based on actual analysis results
        scenarios = []
        
        # Create feature based on goals
        if analysis_result.goals:
            main_goals = analysis_result.goals[:3]  # Use top 3 goals
            goal_scenarios = []
            
            for i, goal in enumerate(main_goals, 1):
                goal_scenarios.append({
                    'name': f"Achieve {goal.lower()}",
                    'steps': [
                        "Given I am an authenticated user",
                        f"When I work towards {goal.lower()}",
                        "Then I should see progress indicators",
                        "And the system should track my achievements"
                    ]
                })
            
            scenarios.append(GherkinScenario(
                feature="Goal Achievement",
                background="Given the application is running and accessible",
                scenarios=goal_scenarios
            ))
        
        # Create scenarios based on constraints
        if analysis_result.constraints:
            constraint_scenarios = []
            
            for constraint in analysis_result.constraints[:2]:  # Use top 2 constraints
                constraint_scenarios.append({
                    'name': f"Handle constraint: {constraint[:50]}...",
                    'steps': [
                        "Given I encounter a system constraint",
                        f"When the system faces: {constraint[:50]}...",
                        "Then appropriate limitations should be communicated",
                        "And alternative solutions should be suggested"
                    ]
                })
            
            scenarios.append(GherkinScenario(
                feature="Constraint Handling",
                background="Given the system has defined operational limits",
                scenarios=constraint_scenarios
            ))
        
        # Create scenarios based on edge cases
        if analysis_result.edge_cases:
            edge_case_scenarios = []
            
            for edge_case in analysis_result.edge_cases[:2]:  # Use top 2 edge cases
                edge_case_scenarios.append({
                    'name': f"Handle edge case: {edge_case[:50]}...",
                    'steps': [
                        "Given I encounter an unusual situation",
                        f"When {edge_case[:50]}...",
                        "Then the system should handle it gracefully",
                        "And provide appropriate user feedback"
                    ]
                })
            
            scenarios.append(GherkinScenario(
                feature="Edge Case Management",
                background="Given the system encounters unexpected scenarios",
                scenarios=edge_case_scenarios
            ))
        
        return scenarios
    
    def format_prd_document(self, prd: PRDDocument) -> str:
        """Format PRD document using template"""
        return self.prd_template.render(
            title=prd.title,
            overview=prd.overview,
            objectives=prd.objectives,
            success_metrics=prd.success_metrics,
            user_stories=prd.user_stories,
            functional_requirements=prd.functional_requirements,
            non_functional_requirements=prd.non_functional_requirements,
            constraints=prd.constraints,
            assumptions=prd.assumptions,
            risks=prd.risks,
            timeline=prd.timeline,
            resources=prd.resources,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def format_gherkin_scenarios(self, scenarios: List[GherkinScenario]) -> str:
        """Format Gherkin scenarios into readable text"""
        formatted = []
        
        for scenario_group in scenarios:
            formatted.append(f"Feature: {scenario_group.feature}")
            
            if scenario_group.background:
                formatted.append(f"  Background: {scenario_group.background}")
            
            for scenario in scenario_group.scenarios:
                formatted.append(f"\n  Scenario: {scenario['name']}")
                for step in scenario['steps']:
                    formatted.append(f"    {step}")
            
            formatted.append("")  # Empty line between features
        
        return "\n".join(formatted)
    
    async def generate_complete_documentation(self, analysis_result: AnalysisResult, project_context: Dict = None) -> Dict[str, str]:
        """Generate both PRD and Gherkin scenarios"""
        logging.info("Generating PRD and Gherkin documentation...")
        
        # Generate PRD
        prd = await self.generate_prd(analysis_result, project_context)
        
        # Generate Gherkin scenarios
        gherkin_scenarios = await self.generate_gherkin_scenarios(prd, analysis_result)
        
        # Format documents
        formatted_prd = self.format_prd_document(prd)
        formatted_gherkin = self.format_gherkin_scenarios(gherkin_scenarios)
        
        logging.info("Documentation generation completed")
        
        return {
            'prd': formatted_prd,
            'gherkin': formatted_gherkin,
            'prd_object': prd,
            'gherkin_object': gherkin_scenarios
        }
