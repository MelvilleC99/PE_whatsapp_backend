"""
Templates for formatting insight messages
"""
from typing import Dict
from datetime import datetime
from loguru import logger

from src.utils.formatters import format_currency


class InsightsTemplate:
    """Format insights into WhatsApp messages"""
    
    @staticmethod
    def format_insights_message(insights: dict, user_name: str) -> str:
        """
        Format insights into a WhatsApp message
        
        Args:
            insights: Dictionary of insight data
            user_name: Name of the user
            
        Returns:
            Formatted message string
        """
        # Customize your header here
        message = f"🏡 *Your Weekly Property Report*\n"
        message += f"Hello {user_name}! 👋\n\n"
        message += f"Here's your performance summary:\n\n"
        
        # Add insights dynamically based on your metrics
        if "leads" in insights:
            message += f"📈 *New Leads:* {insights['leads']}\n"
        
        if "most_active_portal" in insights:
            message += f"🌐 *Top Portal:* {insights['most_active_portal']}\n"
        
        if "new_offers" in insights:
            message += f"💼 *New Offers:* {insights['new_offers']}\n"
        
        if "sales" in insights:
            message += f"🏠 *Sales Closed:* {insights['sales']}\n"
        
        if "revenue" in insights:
            try:
                # Try to format as currency if it's a number
                revenue_val = float(insights['revenue'])
                message += f"💰 *Revenue:* {format_currency(revenue_val)}\n"
            except (ValueError, TypeError):
                # If not a number, just display as-is
                message += f"💰 *Revenue:* {insights['revenue']}\n"
        
        if "commission" in insights:
            try:
                # Try to format as currency if it's a number
                commission_val = float(insights['commission'])
                message += f"🎯 *Commission:* {format_currency(commission_val)}\n"
            except (ValueError, TypeError):
                # If not a number, just display as-is
                message += f"🎯 *Commission:* {insights['commission']}\n"
        
        # Legacy fields (for backward compatibility)
        if "sales_change" in insights:
            emoji = "📈" if "+" in str(insights["sales_change"]) else "📉"
            message += f"{emoji} *Sales Change:* {insights['sales_change']}\n"
        
        if "active_listings" in insights:
            message += f"🏘️ *Active Listings:* {insights['active_listings']}\n"
        
        if "avg_price" in insights:
            message += f"💵 *Average Price:* {insights['avg_price']}\n"
        
        if "sales_velocity" in insights:
            message += f"⚡ *Sales Velocity:* {insights['sales_velocity']}\n"
        
        # Add footer
        message += f"\n━━━━━━━━━━━━━━━━━\n"
        message += f"📅 {datetime.now().strftime('%d %B %Y')}\n"
        message += f"\n💡 _Reply 'insights' anytime for your latest report_"
        
        return message
    
    @staticmethod
    def format_welcome_message(user_name: str) -> str:
        """
        Format a welcome message for new users
        
        Args:
            user_name: Name of the user
            
        Returns:
            Formatted welcome message
        """
        message = f"👋 Welcome {user_name}!\n\n"
        message += f"I'm your Property Insights Assistant. I'll send you weekly reports on your business performance.\n\n"
        message += f"*Commands you can use:*\n"
        message += f"• `insights` - Get your latest report\n"
        message += f"• `help` - See all commands\n"
        message += f"• `stop` - Pause insights\n\n"
        message += f"You'll receive your first weekly report soon! 📊"
        
        return message
    
    @staticmethod
    def format_help_message() -> str:
        """
        Format a help message with available commands
        
        Returns:
            Formatted help message
        """
        message = f"🤖 *Available Commands*\n\n"
        message += f"• `insights` - Get your latest insights report\n"
        message += f"• `help` - Show this help message\n"
        message += f"• `stop` - Stop receiving weekly insights\n"
        message += f"• `start` - Resume receiving weekly insights\n\n"
        message += f"_Just send any of these commands and I'll help you!_"
        
        return message
    
    @staticmethod
    def format_stop_message() -> str:
        """Format a message when user stops insights"""
        return "✋ You've stopped receiving weekly insights. Send 'start' anytime to resume!"
    
    @staticmethod
    def format_start_message() -> str:
        """Format a message when user resumes insights"""
        return "✅ You're back! You'll start receiving weekly insights again. Send 'insights' for your latest report!"


# Backwards compatible function wrapper
def format_insight_message(insights: dict, user_name: str) -> str:
    """
    Backwards compatible wrapper for InsightsTemplate.format_insights_message
    
    Args:
        insights: Dictionary of insight data
        user_name: Name of the user
        
    Returns:
        Formatted message string
    """
    return InsightsTemplate.format_insights_message(insights, user_name)
