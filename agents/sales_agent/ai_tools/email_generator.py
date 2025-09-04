"""
Email Generator for the sales agent system.

This module provides AI-powered email generation capabilities,
including personalized cold emails, follow-up emails, and email templates.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base_ai_tool import BaseAITool
from .gemini_tool import GeminiTool
from ..scrapers.base_scraper import LeadData

logger = logging.getLogger(__name__)


class EmailGenerator:
    """
    AI-powered email generator for creating personalized sales emails.
    
    This class provides capabilities for:
    - Personalized cold email generation
    - Follow-up email creation
    - Email template customization
    - A/B testing variations
    """
    
    def __init__(self, ai_tool: Optional[BaseAITool] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email generator.
        
        Args:
            ai_tool: AI tool instance to use (default: GeminiTool)
            config: Configuration dictionary
        """
        self.config = config or {}
        self.ai_tool = ai_tool or GeminiTool(self.config)
        self.is_initialized = False
        
        # Email templates and styles
        self.email_templates = {
            'cold_outreach': self._get_cold_outreach_template(),
            'follow_up': self._get_follow_up_template(),
            'introduction': self._get_introduction_template(),
            'value_proposition': self._get_value_proposition_template()
        }
    
    def initialize(self) -> bool:
        """
        Initialize the email generator.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not self.ai_tool.is_initialized:
                if not self.ai_tool.initialize():
                    logger.error("Failed to initialize AI tool for email generator")
                    return False
            
            self.is_initialized = True
            logger.info("Email generator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize email generator: {e}")
            return False
    
    def generate_cold_email(self, lead: LeadData, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a personalized cold email for a lead.
        
        Args:
            lead: LeadData object containing lead information
            context: Optional context dictionary containing:
                - product_service: Description of product/service being offered
                - company_info: Information about your company
                - value_proposition: Key value proposition
                - call_to_action: Desired action from the lead
                - tone: Email tone (professional, casual, friendly)
        
        Returns:
            Dict containing:
                - subject: Email subject line
                - body: Email body content
                - personalization_notes: Notes about personalization used
                - suggested_follow_up: Suggested follow-up actions
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize email generator")
        
        try:
            # Build email generation prompt
            email_prompt = self._build_cold_email_prompt(lead, context)
            
            # Generate email content
            email_content = self.ai_tool.generate(
                email_prompt,
                system_instruction="You are an expert sales copywriter. Create compelling, personalized cold emails that build rapport and drive action."
            )
            
            # Parse and structure the email
            email_result = self._parse_email_content(email_content, lead, context)
            
            logger.info(f"Successfully generated cold email for {lead.company}")
            return email_result
            
        except Exception as e:
            logger.error(f"Error generating cold email: {e}")
            raise
    
    def generate_bulk_emails(self, leads: List[LeadData], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate personalized emails for multiple leads.
        
        Args:
            leads: List of LeadData objects
            context: Optional context dictionary (same as generate_cold_email)
        
        Returns:
            List of email dictionaries (same format as generate_cold_email)
        """
        emails = []
        
        for lead in leads:
            try:
                email = self.generate_cold_email(lead, context)
                emails.append(email)
            except Exception as e:
                logger.error(f"Failed to generate email for {lead.company}: {e}")
                # Add a fallback email
                emails.append(self._create_fallback_email(lead, context))
        
        return emails
    
    def generate_follow_up_email(self, lead: LeadData, previous_email: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a follow-up email for a lead.
        
        Args:
            lead: LeadData object
            previous_email: Previous email sent to the lead (optional)
            context: Optional context dictionary
        
        Returns:
            Dict containing follow-up email content
        """
        try:
            # Build follow-up prompt
            follow_up_prompt = self._build_follow_up_prompt(lead, previous_email, context)
            
            # Generate follow-up content
            follow_up_content = self.ai_tool.generate(
                follow_up_prompt,
                system_instruction="You are an expert sales professional. Create effective follow-up emails that re-engage prospects without being pushy."
            )
            
            # Parse and structure the follow-up
            follow_up_result = self._parse_email_content(follow_up_content, lead, context)
            follow_up_result['email_type'] = 'follow_up'
            
            return follow_up_result
            
        except Exception as e:
            logger.error(f"Error generating follow-up email: {e}")
            raise
    
    def _build_cold_email_prompt(self, lead: LeadData, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the cold email generation prompt."""
        context = context or {}
        
        prompt = f"""
        Create a personalized cold email for the following lead:

        LEAD INFORMATION:
        - Company: {lead.company}
        - Contact Name: {lead.name}
        - Title: {lead.title or 'Not specified'}
        - Industry: {lead.industry or 'Not specified'}
        - Location: {lead.location or 'Not specified'}
        - Company Description: {lead.description or 'No description available'}

        CONTEXT:
        - Product/Service: {context.get('product_service', 'Our solution')}
        - Your Company: {context.get('company_info', 'Our company')}
        - Value Proposition: {context.get('value_proposition', 'We help businesses grow')}
        - Desired Action: {context.get('call_to_action', 'Schedule a meeting')}
        - Tone: {context.get('tone', 'professional')}

        Please create:
        1. A compelling subject line (under 50 characters)
        2. A personalized email body (150-300 words)
        3. Clear call-to-action
        4. Professional closing

        The email should:
        - Be personalized based on the lead's information
        - Build rapport and trust
        - Clearly communicate value
        - Include a specific call-to-action
        - Be professional yet engaging
        - Avoid being too salesy or pushy

        Format the response as:
        SUBJECT: [subject line]
        BODY: [email body]
        PERSONALIZATION: [notes about personalization used]
        FOLLOW_UP: [suggested follow-up actions]
        """
        return prompt
    
    def _build_follow_up_prompt(self, lead: LeadData, previous_email: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the follow-up email generation prompt."""
        context = context or {}
        
        previous_info = ""
        if previous_email:
            previous_info = f"""
            PREVIOUS EMAIL SENT:
            Subject: {previous_email.get('subject', 'N/A')}
            Date Sent: {previous_email.get('sent_date', 'N/A')}
            Response: {previous_email.get('response', 'No response')}
            """
        
        prompt = f"""
        Create a follow-up email for the following lead:

        LEAD INFORMATION:
        - Company: {lead.company}
        - Contact Name: {lead.name}
        - Title: {lead.title or 'Not specified'}
        - Industry: {lead.industry or 'Not specified'}

        {previous_info}

        CONTEXT:
        - Product/Service: {context.get('product_service', 'Our solution')}
        - Your Company: {context.get('company_info', 'Our company')}
        - Value Proposition: {context.get('value_proposition', 'We help businesses grow')}

        Create a follow-up email that:
        - References the previous contact (if any)
        - Provides additional value or information
        - Is not pushy or aggressive
        - Offers a different angle or benefit
        - Includes a clear but soft call-to-action
        - Maintains professional tone

        Format the response as:
        SUBJECT: [subject line]
        BODY: [email body]
        STRATEGY: [follow-up strategy used]
        NEXT_STEPS: [suggested next actions]
        """
        return prompt
    
    def _parse_email_content(self, email_content: str, lead: LeadData, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse AI-generated email content into structured format."""
        lines = email_content.split('\n')
        
        subject = ""
        body = ""
        personalization_notes = ""
        follow_up_suggestions = ""
        
        current_section = None
        body_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('SUBJECT:'):
                subject = line.replace('SUBJECT:', '').strip()
                current_section = 'subject'
            elif line.startswith('BODY:'):
                current_section = 'body'
                body_start = line.replace('BODY:', '').strip()
                if body_start:
                    body_lines.append(body_start)
            elif line.startswith('PERSONALIZATION:'):
                personalization_notes = line.replace('PERSONALIZATION:', '').strip()
                current_section = 'personalization'
            elif line.startswith('FOLLOW_UP:'):
                follow_up_suggestions = line.replace('FOLLOW_UP:', '').strip()
                current_section = 'follow_up'
            elif line.startswith('STRATEGY:'):
                follow_up_suggestions = line.replace('STRATEGY:', '').strip()
                current_section = 'strategy'
            elif line.startswith('NEXT_STEPS:'):
                follow_up_suggestions = line.replace('NEXT_STEPS:', '').strip()
                current_section = 'next_steps'
            elif current_section == 'body' and line:
                body_lines.append(line)
            elif current_section in ['personalization', 'follow_up', 'strategy', 'next_steps'] and line:
                if current_section == 'personalization':
                    personalization_notes += f" {line}"
                else:
                    follow_up_suggestions += f" {line}"
        
        body = '\n'.join(body_lines).strip()
        
        # Fallback if parsing failed
        if not subject or not body:
            subject = f"Quick question about {lead.company}"
            body = email_content
            personalization_notes = "Generated using AI with lead information"
            follow_up_suggestions = "Follow up in 3-5 business days if no response"
        
        return {
            'subject': subject,
            'body': body,
            'personalization_notes': personalization_notes,
            'suggested_follow_up': follow_up_suggestions,
            'email_type': 'cold_outreach',
            'generated_at': datetime.now().isoformat(),
            'lead_company': lead.company,
            'lead_name': lead.name
        }
    
    def _create_fallback_email(self, lead: LeadData, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a fallback email if generation fails."""
        context = context or {}
        
        return {
            'subject': f"Quick question about {lead.company}",
            'body': f"""Hi {lead.name or 'there'},

I hope this email finds you well. I came across {lead.company} and was impressed by your work in the {lead.industry or 'industry'}.

I wanted to reach out because {context.get('value_proposition', 'we help companies like yours achieve their goals')}.

Would you be open to a brief conversation about how we might be able to help {lead.company}?

Best regards,
[Your Name]
[Your Company]""",
            'personalization_notes': 'Fallback template used due to generation error',
            'suggested_follow_up': 'Follow up in 3-5 business days if no response',
            'email_type': 'cold_outreach',
            'generated_at': datetime.now().isoformat(),
            'lead_company': lead.company,
            'lead_name': lead.name
        }
    
    def _get_cold_outreach_template(self) -> str:
        """Get cold outreach email template."""
        return """
        Hi [NAME],
        
        I hope this email finds you well. I came across [COMPANY] and was impressed by [SPECIFIC_DETAIL].
        
        I wanted to reach out because [VALUE_PROPOSITION].
        
        [SPECIFIC_BENEFIT] could be particularly valuable for [COMPANY] given [RELEVANT_CONTEXT].
        
        Would you be open to a brief conversation about how we might be able to help [COMPANY] [SPECIFIC_OUTCOME]?
        
        Best regards,
        [YOUR_NAME]
        """
    
    def _get_follow_up_template(self) -> str:
        """Get follow-up email template."""
        return """
        Hi [NAME],
        
        I wanted to follow up on my previous email about [TOPIC].
        
        I thought you might find this [VALUE_ADD] interesting: [SPECIFIC_INFORMATION].
        
        [ADDITIONAL_CONTEXT_OR_BENEFIT]
        
        Would you be available for a quick call this week to discuss how this might apply to [COMPANY]?
        
        Best regards,
        [YOUR_NAME]
        """
    
    def _get_introduction_template(self) -> str:
        """Get introduction email template."""
        return """
        Hi [NAME],
        
        I hope you're doing well. I wanted to introduce myself and [COMPANY].
        
        We specialize in [SPECIALIZATION] and have helped companies like [SIMILAR_COMPANIES] achieve [SPECIFIC_RESULTS].
        
        I'd love to learn more about [COMPANY] and see if there might be a way we could help.
        
        Would you be interested in a brief conversation?
        
        Best regards,
        [YOUR_NAME]
        """
    
    def _get_value_proposition_template(self) -> str:
        """Get value proposition email template."""
        return """
        Hi [NAME],
        
        I noticed that [COMPANY] is [RELEVANT_ACTIVITY]. That's impressive!
        
        I wanted to reach out because we've helped similar companies in [INDUSTRY] achieve [SPECIFIC_RESULTS] through [SOLUTION].
        
        Specifically, we've helped companies:
        - [BENEFIT_1]
        - [BENEFIT_2]
        - [BENEFIT_3]
        
        Would you be interested in learning more about how this might apply to [COMPANY]?
        
        Best regards,
        [YOUR_NAME]
        """
