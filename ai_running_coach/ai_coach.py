import json
import time
from datetime import datetime
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, FREE_AI_MODEL,
    FALLBACK_TO_RULES
)
from data_analyzer import SimpleAnalyzer


class FreeAICoach:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.analyzer = SimpleAnalyzer()
        
    def get_daily_recommendation(self, activities, context):
        if not activities:
            return self._default_recommendation(context)
        
        try:
            prompt = self._build_efficient_prompt(activities, context)
            
            response = self.client.chat.completions.create(
                model=FREE_AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a concise running coach. Analyze patterns and give ONE recommendation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200,
                extra_headers={
                    "HTTP-Referer": "https://github.com/ai-running-coach",
                    "X-Title": "AI Running Coach"
                }
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                recommendation = json.loads(content)
                recommendation["ai_used"] = True
                recommendation["model"] = FREE_AI_MODEL
                return recommendation
            except json.JSONDecodeError:
                if FALLBACK_TO_RULES:
                    return self._fallback_to_rules(activities, context)
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"⚠️  AI API error: {str(e)}")
            if FALLBACK_TO_RULES:
                return self._fallback_to_rules(activities, context)
            return self._default_recommendation(context)
    
    def _build_efficient_prompt(self, activities, context):
        recent_runs = activities[:10]
        
        runs_summary = []
        for run in recent_runs:
            runs_summary.append(
                f"{run['weekday'][:3]} {run['start_time']} - {run['duration_minutes']}min, {run['distance_km']}km"
            )
        
        prompt = f"""Recent runs (newest first):
{chr(10).join(runs_summary)}

Today: {context['today']} {context['time_now']}
Last run: {context['last_run_days_ago']} days ago

REQUIRED OUTPUT (JSON only):
{{
  "time": "HH:MM",
  "duration": minutes,
  "intensity": "easy/moderate/hard",
  "insight": "data-driven pattern observation",
  "motivation": "brief encouragement"
}}"""
        
        return prompt
    
    def _fallback_to_rules(self, activities, context):
        patterns = self.analyzer.analyze_time_patterns(activities)
        avg_duration = self.analyzer.calculate_avg_duration(activities)
        weekly_pattern = self.analyzer.detect_weekly_pattern(activities)
        
        recommendation = self.analyzer.generate_rule_based_recommendation(
            {
                "time_patterns": patterns,
                "avg_duration": avg_duration,
                "weekly_pattern": weekly_pattern
            },
            context
        )
        
        recommendation["ai_used"] = False
        recommendation["model"] = "rule-based"
        return recommendation
    
    def _default_recommendation(self, context):
        current_hour = int(context['time_now'].split(':')[0])
        
        if current_hour < 12:
            time = "7:00 AM"
        elif current_hour < 17:
            time = "6:00 PM"
        else:
            time = "tomorrow 7:00 AM"
        
        return {
            "time": time,
            "duration": 30,
            "intensity": "moderate",
            "insight": "Start with a comfortable 30-minute run",
            "motivation": "Every journey begins with a single step!",
            "ai_used": False,
            "model": "default"
        }
    
    def _parse_text_response(self, text):
        recommendation = {
            "time": "6:00 PM",
            "duration": 30,
            "intensity": "moderate",
            "insight": text[:100],
            "motivation": "Keep pushing forward!",
            "ai_used": True,
            "model": FREE_AI_MODEL
        }
        
        if "morning" in text.lower():
            recommendation["time"] = "7:00 AM"
        elif "evening" in text.lower():
            recommendation["time"] = "6:00 PM"
        
        return recommendation
    
    def analyze_weekly_patterns(self, activities):
        if not activities:
            return {"insights": ["No activity data available"], "ai_used": False}
        
        try:
            weekly_data = self._prepare_weekly_summary(activities)
            
            prompt = f"""Analyze this runner's weekly patterns:
{weekly_data}

Provide 3 specific insights about their training patterns, consistency, and areas for improvement.
Format: JSON array of strings under "insights" key."""
            
            response = self.client.chat.completions.create(
                model=FREE_AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a running coach analyzing training patterns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150,
                extra_headers={
                    "HTTP-Referer": "https://github.com/ai-running-coach",
                    "X-Title": "AI Running Coach"
                }
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(content)
                result["ai_used"] = True
                return result
            except:
                return {
                    "insights": [content[:200]],
                    "ai_used": True
                }
                
        except Exception as e:
            print(f"⚠️  Weekly analysis error: {str(e)}")
            return self.analyzer.generate_weekly_insights(activities)
    
    def _prepare_weekly_summary(self, activities):
        by_day = {}
        for run in activities:
            day = run['weekday']
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(f"{run['duration_minutes']}min/{run['distance_km']}km")
        
        summary = []
        for day, runs in by_day.items():
            summary.append(f"{day}: {', '.join(runs[:3])}")
        
        return "\n".join(summary)