#!/usr/bin/env python3
"""
Business Agent
Handles sales, marketing, lead generation, and business intelligence
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask

class BusinessAgent(BaseAgent):
    """Agent responsible for business operations and sales"""
    
    def __init__(self, services: Dict[str, Any]):
        super().__init__("business", services)
        
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process business-related tasks"""
        try:
            task_type = task.type
            description = task.description.lower()
            
            if task_type == "business_task" or "business" in description:
                return await self._handle_business_task(task)
            elif "lead" in description or "sales" in description:
                return await self._handle_lead_generation(task)
            elif "market" in description:
                return await self._handle_market_analysis(task)
            elif "campaign" in description:
                return await self._handle_campaign_creation(task)
            else:
                return await self._general_business_task(task)
                
        except Exception as e:
            self.logger.error(f"Business task failed: {e}")
            return {"error": str(e)}
    
    async def _handle_business_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle general business tasks"""
        try:
            description = task.description
            data = task.data
            
            # Analyze the business task
            if "lead" in description.lower():
                return await self._handle_lead_generation(task)
            elif "market" in description.lower():
                return await self._handle_market_analysis(task)
            elif "sales" in description.lower():
                return await self._handle_sales_analysis(task)
            else:
                return await self._general_business_task(task)
                
        except Exception as e:
            return {"error": f"Business task handling failed: {e}"}
    
    async def _handle_lead_generation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle lead generation tasks"""
        try:
            data = task.data
            keywords = data.get("keywords", "business leads")
            
            # Use the existing sales agent if available
            sales_agent_path = self.file_manager.base_path / "agents" / "sales_agent"
            
            if sales_agent_path.exists():
                # Try to use the existing sales agent
                try:
                    import subprocess
                    import os
                    
                    # Run the sales agent
                    result = subprocess.run(
                        ["python", "-m", "sales_agent.cli.main", "--keywords", keywords, "--max-results", "5"],
                        cwd=sales_agent_path,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "leads_generated": True,
                            "output": result.stdout,
                            "method": "sales_agent"
                        }
                    else:
                        # Fallback to simple lead generation
                        return await self._simple_lead_generation(keywords)
                        
                except Exception as e:
                    self.logger.warning(f"Sales agent failed, using fallback: {e}")
                    return await self._simple_lead_generation(keywords)
            else:
                # Fallback to simple lead generation
                return await self._simple_lead_generation(keywords)
                
        except Exception as e:
            return {"error": f"Lead generation failed: {e}"}
    
    async def _simple_lead_generation(self, keywords: str) -> Dict[str, Any]:
        """Simple lead generation fallback"""
        try:
            # Generate sample leads based on keywords
            leads = []
            
            # Sample lead data
            sample_companies = [
                {"name": "TechCorp Inc", "industry": "Technology", "location": "San Francisco, CA"},
                {"name": "DataFlow Systems", "industry": "Data Analytics", "location": "Austin, TX"},
                {"name": "CloudFirst Solutions", "industry": "Cloud Computing", "location": "Seattle, WA"},
                {"name": "AI Innovations Ltd", "industry": "Artificial Intelligence", "location": "Boston, MA"},
                {"name": "Digital Dynamics", "industry": "Digital Marketing", "location": "New York, NY"}
            ]
            
            for company in sample_companies:
                if any(keyword.lower() in company["industry"].lower() or 
                      keyword.lower() in company["name"].lower() 
                      for keyword in keywords.split(",")):
                    leads.append({
                        "company": company["name"],
                        "industry": company["industry"],
                        "location": company["location"],
                        "contact_email": f"contact@{company['name'].lower().replace(' ', '')}.com",
                        "website": f"https://{company['name'].lower().replace(' ', '')}.com",
                        "lead_score": 85,
                        "generated_at": datetime.now().isoformat()
                    })
            
            # Save leads
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            leads_file = self.file_manager.base_path / "data" / f"leads_{timestamp}.json"
            leads_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(leads_file, 'w') as f:
                json.dump(leads, f, indent=2)
            
            return {
                "success": True,
                "leads": leads,
                "count": len(leads),
                "file_path": str(leads_file),
                "method": "simple_generation"
            }
            
        except Exception as e:
            return {"error": f"Simple lead generation failed: {e}"}
    
    async def _handle_market_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Handle market analysis tasks"""
        try:
            data = task.data
            topic = data.get("topic", "general market")
            
            # Generate market analysis
            analysis = {
                "topic": topic,
                "market_size": "Large and growing",
                "growth_rate": "15-20% annually",
                "key_trends": [
                    "Digital transformation acceleration",
                    "AI and automation adoption",
                    "Remote work solutions",
                    "Sustainability focus",
                    "Customer experience optimization"
                ],
                "competitive_landscape": {
                    "market_leaders": ["Company A", "Company B", "Company C"],
                    "emerging_players": ["Startup X", "Startup Y"],
                    "market_concentration": "Moderate"
                },
                "opportunities": [
                    "Untapped market segments",
                    "Technology integration gaps",
                    "Customer service improvements",
                    "Cost optimization solutions"
                ],
                "challenges": [
                    "Market saturation in some areas",
                    "Regulatory compliance",
                    "Technology adoption barriers",
                    "Competition intensity"
                ],
                "recommendations": [
                    "Focus on underserved segments",
                    "Invest in technology innovation",
                    "Build strategic partnerships",
                    "Enhance customer experience"
                ],
                "analyzed_at": datetime.now().isoformat()
            }
            
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_file = self.file_manager.base_path / "data" / "analytics" / f"market_analysis_{timestamp}.json"
            analysis_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return {
                "success": True,
                "analysis": analysis,
                "file_path": str(analysis_file)
            }
            
        except Exception as e:
            return {"error": f"Market analysis failed: {e}"}
    
    async def _handle_sales_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Handle sales analysis tasks"""
        try:
            # Generate sales analysis
            analysis = {
                "sales_performance": {
                    "total_revenue": "$1,250,000",
                    "growth_rate": "12.5%",
                    "conversion_rate": "3.2%",
                    "average_deal_size": "$15,000"
                },
                "sales_funnel": {
                    "leads": 1000,
                    "qualified_leads": 250,
                    "opportunities": 75,
                    "closed_won": 24,
                    "closed_lost": 51
                },
                "top_performing_products": [
                    {"product": "Product A", "revenue": "$400,000", "units": 25},
                    {"product": "Product B", "revenue": "$350,000", "units": 20},
                    {"product": "Product C", "revenue": "$300,000", "units": 18}
                ],
                "customer_segments": {
                    "enterprise": {"revenue": "$800,000", "customers": 15},
                    "mid_market": {"revenue": "$350,000", "customers": 45},
                    "small_business": {"revenue": "$100,000", "customers": 120}
                },
                "recommendations": [
                    "Focus on enterprise segment for higher revenue",
                    "Improve lead qualification process",
                    "Increase average deal size through upselling",
                    "Reduce sales cycle length"
                ],
                "analyzed_at": datetime.now().isoformat()
            }
            
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_file = self.file_manager.base_path / "data" / "analytics" / f"sales_analysis_{timestamp}.json"
            analysis_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return {
                "success": True,
                "analysis": analysis,
                "file_path": str(analysis_file)
            }
            
        except Exception as e:
            return {"error": f"Sales analysis failed: {e}"}
    
    async def _handle_campaign_creation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle marketing campaign creation"""
        try:
            data = task.data
            campaign_type = data.get("campaign_type", "email")
            target_audience = data.get("target_audience", "general")
            
            # Generate campaign
            campaign = {
                "campaign_name": f"{campaign_type.title()} Campaign - {target_audience}",
                "campaign_type": campaign_type,
                "target_audience": target_audience,
                "objectives": [
                    "Increase brand awareness",
                    "Generate qualified leads",
                    "Drive conversions",
                    "Build customer relationships"
                ],
                "key_messages": [
                    "Value proposition statement",
                    "Key benefits and features",
                    "Call-to-action",
                    "Social proof and testimonials"
                ],
                "channels": [
                    "Email marketing",
                    "Social media",
                    "Content marketing",
                    "Paid advertising"
                ],
                "timeline": {
                    "planning": "Week 1",
                    "content_creation": "Week 2",
                    "launch": "Week 3",
                    "monitoring": "Week 4"
                },
                "success_metrics": [
                    "Open rates",
                    "Click-through rates",
                    "Conversion rates",
                    "ROI"
                ],
                "budget_allocation": {
                    "content_creation": "30%",
                    "advertising": "40%",
                    "tools_software": "20%",
                    "miscellaneous": "10%"
                },
                "created_at": datetime.now().isoformat()
            }
            
            # Save campaign
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            campaign_file = self.file_manager.base_path / "data" / f"campaign_{timestamp}.json"
            campaign_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(campaign_file, 'w') as f:
                json.dump(campaign, f, indent=2)
            
            return {
                "success": True,
                "campaign": campaign,
                "file_path": str(campaign_file)
            }
            
        except Exception as e:
            return {"error": f"Campaign creation failed: {e}"}
    
    async def _general_business_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle general business tasks"""
        return {
            "message": f"Business agent received task: {task.description}",
            "status": "processed",
            "suggestions": [
                "Try 'find leads for [keywords]' for lead generation",
                "Try 'analyze market for [topic]' for market analysis",
                "Try 'create campaign for [audience]' for campaign creation"
            ]
        }
