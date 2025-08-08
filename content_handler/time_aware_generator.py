"""
Time-Aware Content Generator
Ensures all time references in content are accurate and current
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TimeAwareGenerator:
    """
    Time-aware content generator that ensures accurate time references
    """
    
    def __init__(self):
        """Initialize the time-aware generator."""
        self.current_time = datetime.now(timezone.utc)
        self.current_date = self.current_time.date()
        self.current_weekday = self.current_time.strftime("%A")
        self.current_month = self.current_time.strftime("%B")
        self.current_year = self.current_time.year
        
        # Time-sensitive content patterns to avoid
        self.time_sensitive_patterns = {
            "new_year": {
                "patterns": ["happy new year", "new year"],
                "valid_months": [1],  # January only
                "valid_days": [1]     # January 1st only
            },
            "christmas": {
                "patterns": ["merry christmas", "christmas", "holiday season"],
                "valid_months": [12],  # December only
                "valid_days": list(range(20, 26))  # Dec 20-25
            },
            "weekend": {
                "patterns": ["happy friday", "happy weekend", "friday", "saturday", "sunday"],
                "valid_weekdays": ["Friday", "Saturday", "Sunday"]
            },
            "monday": {
                "patterns": ["happy monday", "monday motivation", "start of the week"],
                "valid_weekdays": ["Monday"]
            },
            "midweek": {
                "patterns": ["hump day", "wednesday", "midweek"],
                "valid_weekdays": ["Wednesday"]
            },
            "end_of_week": {
                "patterns": ["end of the week", "friday", "weekend"],
                "valid_weekdays": ["Friday"]
            }
        }
    
    def validate_time_references(self, content: str) -> Dict:
        """
        Validate time references in content for accuracy.
        
        Args:
            content: Content to validate
            
        Returns:
            Dict with validation results and corrections
        """
        issues = []
        corrections = []
        is_valid = True
        
        content_lower = content.lower()
        
        # Check each time-sensitive pattern
        for category, rules in self.time_sensitive_patterns.items():
            for pattern in rules["patterns"]:
                if pattern in content_lower:
                    if not self._is_time_appropriate(category, rules):
                        issues.append(f"Inappropriate {category} reference: '{pattern}'")
                        corrections.append(self._get_appropriate_replacement(category, pattern))
                        is_valid = False
        
        # Check for specific date references
        date_issues = self._check_date_references(content)
        issues.extend(date_issues["issues"])
        corrections.extend(date_issues["corrections"])
        
        if date_issues["issues"]:
            is_valid = False
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "corrections": corrections,
            "current_time": self.current_time.isoformat(),
            "current_weekday": self.current_weekday,
            "current_month": self.current_month,
            "current_year": self.current_year
        }
    
    def _is_time_appropriate(self, category: str, rules: Dict) -> bool:
        """Check if a time reference is appropriate for the current time."""
        if "valid_months" in rules:
            if self.current_time.month not in rules["valid_months"]:
                return False
        
        if "valid_days" in rules:
            if self.current_time.day not in rules["valid_days"]:
                return False
        
        if "valid_weekdays" in rules:
            if self.current_weekday not in rules["valid_weekdays"]:
                return False
        
        return True
    
    def _get_appropriate_replacement(self, category: str, pattern: str) -> str:
        """Get an appropriate replacement for inappropriate time references."""
        replacements = {
            "new_year": "great year ahead",
            "christmas": "this season",
            "weekend": "today",
            "monday": "today",
            "midweek": "today",
            "end_of_week": "today"
        }
        
        return replacements.get(category, "today")
    
    def _check_date_references(self, content: str) -> Dict:
        """Check for specific date references that might be outdated."""
        issues = []
        corrections = []
        
        # Check for year references (check multiple years)
        for year in range(2020, self.current_year):
            year_str = str(year)
            if year_str in content:
                issues.append(f"Outdated year reference: '{year_str}'")
                corrections.append(str(self.current_year))
        
        # Check for month references
        month_patterns = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        
        for month_name, month_num in month_patterns.items():
            if month_name in content.lower():
                # If referencing a past month in a way that suggests it's current
                if month_num < self.current_time.month:
                    issues.append(f"Outdated month reference: '{month_name}'")
                    corrections.append(self.current_month.lower())
        
        return {
            "issues": issues,
            "corrections": corrections
        }
    
    def correct_time_references(self, content: str) -> str:
        """
        Correct time references in content to be accurate.
        
        Args:
            content: Content to correct
            
        Returns:
            Corrected content
        """
        validation = self.validate_time_references(content)
        
        if validation["is_valid"]:
            return content
        
        corrected_content = content
        
        # Apply corrections
        for issue, correction in zip(validation["issues"], validation["corrections"]):
            # Handle year corrections
            if "year reference" in issue.lower():
                # Extract the year from the issue message
                import re
                year_match = re.search(r"'(\d{4})'", issue)
                if year_match:
                    old_year = year_match.group(1)
                    corrected_content = corrected_content.replace(old_year, correction)
            
            # Handle other corrections
            elif "new year" in issue.lower():
                corrected_content = corrected_content.replace("happy new year", "great year ahead")
                corrected_content = corrected_content.replace("Happy New Year", "Great year ahead")
            elif "christmas" in issue.lower():
                corrected_content = corrected_content.replace("merry christmas", "this season")
                corrected_content = corrected_content.replace("Merry Christmas", "This season")
            elif "friday" in issue.lower():
                corrected_content = corrected_content.replace("happy friday", "today")
                corrected_content = corrected_content.replace("Happy Friday", "Today")
            elif "monday" in issue.lower():
                corrected_content = corrected_content.replace("happy monday", "today")
                corrected_content = corrected_content.replace("Happy Monday", "Today")
        
        return corrected_content
    
    def add_time_context(self, content: str) -> str:
        """
        Add appropriate time context to content.
        
        Args:
            content: Content to add context to
            
        Returns:
            Content with time context
        """
        # Add current time context if appropriate
        if "today" in content.lower() or "this week" in content.lower():
            # Content already has time context
            return content
        
        # Add appropriate time context based on current time
        if self.current_weekday == "Monday":
            context = "As we start this new week"
        elif self.current_weekday == "Friday":
            context = "As we wrap up this week"
        elif self.current_weekday in ["Saturday", "Sunday"]:
            context = "This weekend"
        else:
            context = "Today"
        
        # Add context if it makes sense
        if not content.startswith(context):
            return f"{context}, {content.lower()}"
        
        return content
    
    def get_time_aware_prompt_addition(self) -> str:
        """
        Get time-aware prompt addition for content generation.
        
        Returns:
            String to add to prompts for time awareness
        """
        return f"""
CURRENT TIME CONTEXT:
- Current Date: {self.current_time.strftime('%B %d, %Y')}
- Current Day: {self.current_weekday}
- Current Month: {self.current_month}
- Current Year: {self.current_year}

TIME ACCURACY REQUIREMENTS:
- DO NOT mention "Happy New Year" unless it's January 1st
- DO NOT mention "Merry Christmas" unless it's December 20-25
- DO NOT mention "Happy Friday" unless it's actually Friday
- DO NOT mention "Monday motivation" unless it's actually Monday
- DO NOT mention "Hump day" unless it's Wednesday
- Use accurate time references based on current date
- If mentioning days, ensure they match the current day
- If mentioning months, ensure they're current or relevant
- If mentioning years, use {self.current_year}

APPROPRIATE TIME REFERENCES FOR TODAY:
- Day: {self.current_weekday}
- Month: {self.current_month}
- Year: {self.current_year}
- Context: {self._get_current_context()}
"""
    
    def _get_current_context(self) -> str:
        """Get current time context for content."""
        if self.current_weekday == "Monday":
            return "start of the week"
        elif self.current_weekday == "Friday":
            return "end of the week"
        elif self.current_weekday in ["Saturday", "Sunday"]:
            return "weekend"
        else:
            return "midweek"
    
    def get_status(self) -> Dict:
        """Get component status."""
        return {
            "status": "operational",
            "component": "time_aware_generator",
            "current_time": self.current_time.isoformat(),
            "current_weekday": self.current_weekday,
            "current_month": self.current_month,
            "current_year": self.current_year,
            "timestamp": self.current_time.isoformat()
        }


# Test function
def test_time_aware_generator():
    """Test the time-aware generator functionality."""
    generator = TimeAwareGenerator()
    
    print("🧪 Testing Time-Aware Generator")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "Happy New Year! Let's make this year amazing!",
        "Happy Friday everyone!",
        "Monday motivation coming at you!",
        "I had a great meeting yesterday",
        "This week has been challenging"
    ]
    
    for i, test_content in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_content}")
        print("-" * 40)
        
        validation = generator.validate_time_references(test_content)
        print(f"Valid: {validation['is_valid']}")
        
        if not validation['is_valid']:
            print("Issues:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        corrected = generator.correct_time_references(test_content)
        print(f"Corrected: {corrected}")
    
    print(f"\n⏰ Current Time Context:")
    print(f"  Date: {generator.current_time.strftime('%B %d, %Y')}")
    print(f"  Day: {generator.current_weekday}")
    print(f"  Month: {generator.current_month}")
    print(f"  Year: {generator.current_year}")


if __name__ == "__main__":
    test_time_aware_generator() 