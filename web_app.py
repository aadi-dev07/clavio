from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
from datetime import datetime
from agents import GitHubAgent, AnalysisAgent, PRDAgent
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Multi-Agent System Dashboard", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize agents
github_agent = GitHubAgent()
analysis_agent = AnalysisAgent()
prd_agent = PRDAgent()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/github-report/{days}")
async def get_github_report(days: int = 1):
    """API endpoint for GitHub reports"""
    try:
        report = await github_agent.generate_daily_report(days)
        commits = await github_agent.get_daily_commits(days)
        prs = await github_agent.get_pull_requests("open")
        repo_stats = await github_agent.get_repository_stats()
        
        return {
            "status": "success",
            "report": report,
            "commits": commits,
            "pull_requests": prs,
            "repository_stats": repo_stats,
            "days": days,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

@app.get("/api/analysis")
async def get_product_analysis():
    """API endpoint for product analysis"""
    try:
        result = await analysis_agent.analyze_product_requirements()
        
        return {
            "status": "success",
            "analysis": {
                "goals": result.goals,
                "constraints": result.constraints,
                "edge_cases": result.edge_cases,
                "follow_up_questions": result.follow_up_questions,
                "impact_analysis": result.impact_analysis,
                "recommendations": result.recommendations
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

@app.post("/api/prd-generation")
async def generate_prd(request: Request):
    """API endpoint for PRD generation"""
    try:
        # First get analysis results
        analysis_result = await analysis_agent.analyze_product_requirements()
        
        # Generate PRD and Gherkin scenarios
        documentation = await prd_agent.generate_complete_documentation(analysis_result)
        
        return {
            "status": "success",
            "documentation": {
                "prd": documentation["prd"],
                "gherkin": documentation["gherkin"]
            },
            "analysis_summary": {
                "goals_count": len(analysis_result.goals),
                "constraints_count": len(analysis_result.constraints),
                "recommendations_count": len(analysis_result.recommendations)
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

@app.get("/api/complete-workflow/{days}")
async def complete_workflow(days: int = 1):
    """API endpoint for complete workflow"""
    try:
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        # Step 1: GitHub Report
        github_report = await github_agent.generate_daily_report(days)
        commits = await github_agent.get_daily_commits(days)
        results["github"] = {
            "report": github_report,
            "commits_count": len(commits),
            "commits": commits[:5]  # Show only first 5 for summary
        }
        
        # Step 2: Analysis
        analysis_result = await analysis_agent.analyze_product_requirements()
        results["analysis"] = {
            "goals": analysis_result.goals,
            "constraints": analysis_result.constraints,
            "edge_cases": analysis_result.edge_cases,
            "recommendations": analysis_result.recommendations,
            "impact_analysis": analysis_result.impact_analysis
        }
        
        # Step 3: PRD Generation
        documentation = await prd_agent.generate_complete_documentation(analysis_result)
        results["documentation"] = {
            "prd_preview": documentation["prd"][:500] + "...",
            "gherkin_preview": documentation["gherkin"][:300] + "...",
            "full_prd": documentation["prd"],
            "full_gherkin": documentation["gherkin"]
        }
        
        results["status"] = "completed"
        return results
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/github", response_class=HTMLResponse)
async def github_page(request: Request):
    """GitHub reports page"""
    return templates.TemplateResponse("github.html", {"request": request})

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """Product analysis page"""
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.get("/prd", response_class=HTMLResponse)
async def prd_page(request: Request):
    """PRD generation page"""
    return templates.TemplateResponse("prd.html", {"request": request})

@app.get("/workflow", response_class=HTMLResponse)
async def workflow_page(request: Request):
    """Complete workflow page"""
    return templates.TemplateResponse("workflow.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
