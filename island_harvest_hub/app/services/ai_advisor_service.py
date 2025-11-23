"""
AI Business Advisor Service

Uses Claude API to provide intelligent business insights and recommendations

"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import requests


class AIAdvisorService:
    """Service for AI-powered business insights using Claude API"""
    
    def __init__(self):
        # Try to get API key from environment first
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        
        # If not in environment, try Streamlit secrets (for Streamlit Cloud)
        if not self.api_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets'):
                    # Try dictionary access
                    if 'ANTHROPIC_API_KEY' in st.secrets:
                        api_key_value = st.secrets['ANTHROPIC_API_KEY']
                        # Handle both string and object types
                        if api_key_value:
                            self.api_key = str(api_key_value).strip()
                            # Also set in environment for consistency
                            os.environ['ANTHROPIC_API_KEY'] = self.api_key
                    # Try attribute access as fallback
                    elif hasattr(st.secrets, 'ANTHROPIC_API_KEY'):
                        api_key_value = getattr(st.secrets, 'ANTHROPIC_API_KEY', '')
                        if api_key_value:
                            self.api_key = str(api_key_value).strip()
                            os.environ['ANTHROPIC_API_KEY'] = self.api_key
            except Exception as e:
                # Silently fail - secrets might not be available
                pass
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"
        
    def _make_api_call(self, prompt: str, system_context: str = "") -> str:
        """Make a call to Claude API"""
        
        if not self.api_key:
            return "⚠️ API key not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        data = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": messages
        }
        
        if system_context:
            data["system"] = system_context
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['content'][0]['text']
            
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"❌ Error connecting to AI service: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def get_business_insights(self, business_data: Dict[str, Any], question: str) -> str:
        """Get AI insights about the business"""
        
        system_context = f"""You are an expert business advisor for Bornfidis businesses, 
a portfolio of companies owned by Brian Miller including farm-to-table distribution, 
agriculture, private chef services, and sustainable sportswear.



You provide clear, actionable insights based on business data. Be concise but thorough.

Always format your responses with clear sections and bullet points where appropriate.

"""
        
        # Format business data for the prompt
        data_summary = json.dumps(business_data, indent=2)
        
        prompt = f"""Based on the following business data:



{data_summary}



Question: {question}



Please provide a clear, actionable answer with specific recommendations where appropriate."""

        return self._make_api_call(prompt, system_context)
    
    def get_daily_priorities(self, business_data: Dict[str, Any], business_name: str) -> str:
        """Get AI-powered daily priorities"""
        
        system_context = """You are a business operations advisor. Analyze the data and 
suggest 3-5 specific priorities for today. Be practical and action-oriented."""
        
        data_summary = json.dumps(business_data, indent=2)
        
        prompt = f"""Based on this business data for {business_name}:



{data_summary}



What are the top 3-5 priorities I should focus on today? 
Format as a numbered list with clear action items."""

        return self._make_api_call(prompt, system_context)
    
    def predict_revenue(self, historical_data: Dict[str, Any], business_name: str) -> str:
        """Predict future revenue based on historical data"""
        
        system_context = """You are a financial analyst. Analyze historical data and 
provide revenue predictions with reasoning."""
        
        data_summary = json.dumps(historical_data, indent=2)
        
        prompt = f"""Based on this historical data for {business_name}:



{data_summary}



Predict the revenue for next month and explain your reasoning. 
Include best-case, likely, and worst-case scenarios."""

        return self._make_api_call(prompt, system_context)
    
    def analyze_customer_trends(self, customer_data: Dict[str, Any]) -> str:
        """Analyze customer satisfaction and trends"""
        
        system_context = """You are a customer success analyst. Identify trends, 
issues, and opportunities in customer data."""
        
        data_summary = json.dumps(customer_data, indent=2)
        
        prompt = f"""Analyze this customer data:



{data_summary}



Identify:

1. Key satisfaction trends

2. Customers at risk

3. Opportunities for growth

4. Specific action items"""

        return self._make_api_call(prompt, system_context)
    
    def compare_businesses(self, business_comparison: Dict[str, Any]) -> str:
        """Compare performance across businesses"""
        
        system_context = """You are a portfolio analyst. Compare business performance 
and provide strategic recommendations."""
        
        data_summary = json.dumps(business_comparison, indent=2)
        
        prompt = f"""Compare these businesses:



{data_summary}



Provide:

1. Performance ranking

2. Key strengths of each business

3. Areas needing attention

4. Strategic recommendations"""

        return self._make_api_call(prompt, system_context)
    
    def generate_marketing_content(self, business_context: str, content_type: str) -> str:
        """Generate marketing content"""
        
        system_context = """You are a marketing copywriter for Bornfidis businesses. 
Create compelling, authentic content that reflects the brand values: 
Faith, Regeneration, Innovation, Service."""
        
        prompt = f"""Create {content_type} for:



{business_context}



Make it engaging, authentic, and aligned with the Bornfidis brand values."""

        return self._make_api_call(prompt, system_context)

