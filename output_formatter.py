import asyncio
import logging
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import settings
import json
import re
from datetime import datetime

class OutputFormatter:
    """AI-powered output formatter to minimize verbose text and present key information"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.1,  # Low temperature for consistent formatting
            convert_system_message_to_human=True
        )
    
    async def format_github_report(self, report_data: Dict) -> str:
        """Format GitHub report with minimal, key information"""
        system_prompt = """You are an expert at extracting and presenting key information concisely.
        
Transform the verbose GitHub report into a clean, minimal format with:
- 📊 **Executive Summary** (2-3 lines max)
- 🔥 **Key Highlights** (3-5 bullet points)
- 📈 **Metrics** (important numbers only)
- ⚠️ **Action Items** (if any critical issues)

Use emojis, bold text, and clear structure. Keep it under 200 words total."""

        human_prompt = f"""Minimize this GitHub report data:
        
Report: {report_data.get('report', '')}
Commits: {len(report_data.get('commits', []))} commits
PRs: {len(report_data.get('pull_requests', []))} pull requests
Repository: {report_data.get('repository_stats', {}).get('full_name', 'Unknown')}

Extract only the most important information and format it cleanly."""

        try:
            messages = [HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error formatting GitHub report: {e}")
            return self._fallback_github_format(report_data)
    
    async def format_analysis_result(self, analysis_data: Dict) -> str:
        """Format analysis results with key insights only"""
        system_prompt = """Extract and present only the most critical analysis insights.
        
Format as:
- 🎯 **Key Goals** (top 3 only)
- ⚠️ **Critical Constraints** (top 3 only)  
- 💡 **Top Recommendations** (top 3 only)
- 📊 **Impact Summary** (one line each for growth, revenue, UX)

Use bullet points, emojis, and keep under 150 words total."""

        analysis = analysis_data.get('analysis_result') or analysis_data.get('analysis', {})
        
        # Handle both object attributes and dictionary keys
        if hasattr(analysis, 'goals'):
            goals = analysis.goals
            constraints = analysis.constraints
            recommendations = analysis.recommendations
            impact = analysis.impact_analysis
        else:
            goals = analysis.get('goals', [])
            constraints = analysis.get('constraints', [])
            recommendations = analysis.get('recommendations', [])
            impact = analysis.get('impact_analysis', {})
        
        human_prompt = f"""Minimize this analysis data:
        
Goals: {goals}
Constraints: {constraints}
Recommendations: {recommendations}
Impact: {impact}

Show only the most important items."""

        try:
            messages = [HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error formatting analysis: {e}")
            return self._fallback_analysis_format(analysis_data)
    
    async def format_prd_result(self, prd_data: Dict) -> str:
        """Format PRD generation results with summary only"""
        system_prompt = """Summarize PRD generation results concisely.
        
Format as:
- 📋 **PRD Status** (completion status)
- 🧪 **Test Scenarios** (number generated)
- 📄 **Document Summary** (2-3 key points from PRD)
- ✅ **Next Steps** (immediate actions)

Keep under 100 words total."""

        documentation = prd_data.get('documentation', {})
        
        human_prompt = f"""Summarize this PRD generation:
        
Status: {prd_data.get('status', 'unknown')}
PRD Length: {len(str(documentation.get('prd', ''))) if documentation else 0} characters
Gherkin Length: {len(str(documentation.get('gherkin', ''))) if documentation else 0} characters
Analysis Summary: {prd_data.get('analysis_summary', {})}

Provide a brief, actionable summary."""

        try:
            messages = [HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error formatting PRD: {e}")
            return self._fallback_prd_format(prd_data)
    
    async def format_complete_workflow(self, workflow_data: Dict) -> str:
        """Format complete workflow results with executive summary"""
        system_prompt = """Create an executive summary of the complete workflow.
        
Format as:
- 🚀 **Workflow Status** (overall completion)
- 📊 **Key Metrics** (commits, goals, docs generated)
- 🎯 **Main Outcomes** (top 3 achievements)
- 🔄 **Next Actions** (immediate next steps)

Keep under 120 words total. Focus on business value."""

        human_prompt = f"""Summarize this complete workflow:
        
Status: {workflow_data.get('status', 'unknown')}
GitHub: {len(workflow_data.get('github', {}).get('commits', []))} commits analyzed
Analysis: {len(workflow_data.get('analysis', {}).get('goals', []))} goals identified
Documentation: {'Generated' if workflow_data.get('documentation') else 'Not generated'}
Timestamp: {workflow_data.get('timestamp', '')}

Provide an executive summary focusing on value delivered."""

        try:
            messages = [HumanMessage(content=f"{system_prompt}\n\n{human_prompt}")]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error formatting workflow: {e}")
            return self._fallback_workflow_format(workflow_data)
    
    def _fallback_github_format(self, data: Dict) -> str:
        """Fallback GitHub formatting if AI fails"""
        commits = len(data.get('commits', []))
        prs = len(data.get('pull_requests', []))
        repo = data.get('repository_stats', {}).get('full_name', 'Unknown')
        
        return f"""📊 **GitHub Summary**
• **Repository:** {repo}
• **Activity:** {commits} commits, {prs} PRs
• **Status:** {'Active' if commits > 0 else 'Quiet'}"""
    
    def _fallback_analysis_format(self, data: Dict) -> str:
        """Fallback analysis formatting if AI fails"""
        analysis = data.get('analysis_result') or data.get('analysis', {})
        goals_count = len(getattr(analysis, 'goals', analysis.get('goals', [])))
        
        return f"""🎯 **Analysis Summary**
• **Goals Identified:** {goals_count}
• **Status:** {'Completed' if data.get('status') == 'success' else 'Partial'}
• **Action Required:** Review recommendations"""
    
    def _fallback_prd_format(self, data: Dict) -> str:
        """Fallback PRD formatting if AI fails"""
        status = data.get('status', 'unknown')
        
        return f"""📋 **PRD Summary**
• **Status:** {status.title()}
• **Documents:** {'Generated' if status == 'success' else 'Pending'}
• **Next:** Review and approve documentation"""
    
    def _fallback_workflow_format(self, data: Dict) -> str:
        """Fallback workflow formatting if AI fails"""
        status = data.get('status', 'unknown')
        
        return f"""🚀 **Workflow Summary**
• **Status:** {status.title()}
• **Completion:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
• **Action:** Review results and proceed"""

# Utility functions for easy integration
async def format_output(output_type: str, data: Dict) -> str:
    """Main function to format any output type"""
    formatter = OutputFormatter()
    
    if output_type == 'github':
        return await formatter.format_github_report(data)
    elif output_type == 'analysis':
        return await formatter.format_analysis_result(data)
    elif output_type == 'prd':
        return await formatter.format_prd_result(data)
    elif output_type == 'workflow':
        return await formatter.format_complete_workflow(data)
    else:
        return "❌ **Unknown output type**"

def create_section_header(title: str, emoji: str = "📋") -> str:
    """Create consistent section headers"""
    return f"\n{emoji} **{title.upper()}**\n{'─' * (len(title) + 4)}"

def format_bullet_list(items: List[str], max_items: int = 5) -> str:
    """Format items as clean bullet list"""
    if not items:
        return "• No items available"
    
    formatted_items = []
    for i, item in enumerate(items[:max_items]):
        # Clean up the item text
        clean_item = re.sub(r'^[-•*]\s*', '', item.strip())
        formatted_items.append(f"• {clean_item}")
    
    if len(items) > max_items:
        formatted_items.append(f"• ... and {len(items) - max_items} more")
    
    return '\n'.join(formatted_items)
