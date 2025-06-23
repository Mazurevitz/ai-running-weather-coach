#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    CACHE_FILE, PROFILE_FILE, CACHE_DURATION_HOURS,
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, OPENROUTER_API_KEY
)
from strava_client import StravaClient
from ai_coach import FreeAICoach
from data_analyzer import SimpleAnalyzer


class CacheManager:
    @staticmethod
    def load_cache():
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
                expires_at = datetime.fromisoformat(cache.get("expires_at", "2000-01-01"))
                if datetime.now() < expires_at:
                    return cache
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None
    
    @staticmethod
    def save_cache(data):
        cache = {
            **data,
            "timestamp": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=CACHE_DURATION_HOURS)).isoformat()
        }
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    
    @staticmethod
    def clear_cache():
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()


class RunningCoachCLI:
    def __init__(self):
        self.strava = StravaClient()
        self.coach = FreeAICoach()
        self.analyzer = SimpleAnalyzer()
    
    def setup(self):
        print("🏃‍♂️ AI Running Coach Setup")
        print("=" * 50)
        
        if not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET]):
            print("❌ Missing Strava credentials in .env file")
            print("Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET")
            return False
        
        if not OPENROUTER_API_KEY:
            print("⚠️  No OpenRouter API key found - will use rule-based recommendations only")
        
        print("\n📱 Starting Strava OAuth flow...")
        success = self.strava.oauth_flow()
        
        if success:
            print("\n✅ Setup complete! You can now use the coach.")
            return True
        else:
            print("\n❌ Setup failed. Please try again.")
            return False
    
    def get_recommendation(self, use_ai=True):
        print("🏃‍♂️ AI Running Coach Recommendation")
        print("=" * 50)
        
        cache = CacheManager.load_cache()
        
        if cache and "recommendation" in cache:
            activities = cache.get("strava_data", [])
            recommendation = cache["recommendation"]
            data_source = "cached"
            print("📈 Using cached data (saves API calls)")
        else:
            print("🔄 Fetching fresh data from Strava...")
            activities = self.strava.get_athlete_activities()
            
            if activities is None:
                print("❌ Failed to fetch Strava data. Please run --setup again.")
                return
            
            context = self._get_context(activities)
            
            if use_ai and OPENROUTER_API_KEY:
                print("🤖 Getting AI recommendation...")
                recommendation = self.coach.get_daily_recommendation(activities, context)
            else:
                print("📊 Using rule-based analysis...")
                patterns = {
                    "time_patterns": self.analyzer.analyze_time_patterns(activities),
                    "avg_duration": self.analyzer.calculate_avg_duration(activities),
                    "weekly_pattern": self.analyzer.detect_weekly_pattern(activities)
                }
                recommendation = self.analyzer.generate_rule_based_recommendation(patterns, context)
            
            CacheManager.save_cache({
                "strava_data": activities,
                "recommendation": recommendation
            })
            
            data_source = "fresh"
        
        self._display_recommendation(recommendation, activities, data_source)
    
    def analyze_patterns(self):
        print("📊 Weekly Pattern Analysis")
        print("=" * 50)
        
        cache = CacheManager.load_cache()
        
        if cache and "strava_data" in cache:
            activities = cache["strava_data"]
            print("📈 Using cached data")
        else:
            print("🔄 Fetching data from Strava...")
            activities = self.strava.get_athlete_activities()
            
            if activities is None:
                print("❌ Failed to fetch Strava data.")
                return
        
        if OPENROUTER_API_KEY:
            print("🤖 Analyzing with AI...")
            insights = self.coach.analyze_weekly_patterns(activities)
        else:
            insights = self.analyzer.generate_weekly_insights(activities)
        
        metrics = self.analyzer.calculate_performance_metrics(activities)
        
        print(f"\n📈 Performance Summary ({len(activities)} runs analyzed):")
        print(f"   Total Distance: {metrics['total_distance_km']} km")
        print(f"   Total Time: {metrics['total_time_hours']} hours")
        print(f"   Average Pace: {metrics['average_pace_min_per_km']:.1f} min/km")
        print(f"   Average Run: {metrics['average_distance_km']} km in {metrics['average_duration_min']} minutes")
        
        print("\n🧠 Insights:")
        for i, insight in enumerate(insights.get("insights", []), 1):
            print(f"   {i}. {insight}")
        
        if insights.get("ai_used"):
            print(f"\n🤖 Analysis by: {insights.get('model', 'AI')}")
        else:
            print("\n📊 Analysis: Rule-based")
    
    def show_status(self):
        print("📊 AI Running Coach Status")
        print("=" * 50)
        
        strava_connected = bool(self.strava.tokens)
        ai_configured = bool(OPENROUTER_API_KEY)
        
        print(f"✅ Strava Connected: {'Yes' if strava_connected else 'No'}")
        print(f"✅ AI Configured: {'Yes (FREE models)' if ai_configured else 'No (rule-based only)'}")
        
        cache = CacheManager.load_cache()
        if cache:
            expires = datetime.fromisoformat(cache["expires_at"])
            time_left = expires - datetime.now()
            hours_left = int(time_left.total_seconds() / 3600)
            print(f"✅ Cache Valid: Yes (expires in {hours_left} hours)")
        else:
            print(f"❌ Cache Valid: No")
        
        try:
            with open(PROFILE_FILE, "r") as f:
                profile = json.load(f)
                print(f"\n👤 Profile:")
                print(f"   Last Update: {profile.get('last_update', 'Never')}")
                print(f"   Total API Calls Today: {profile.get('api_calls_today', 0)}")
                print(f"   Estimated Monthly Cost: ${profile.get('estimated_cost', 0.00):.2f}")
        except FileNotFoundError:
            print("\n👤 No profile data yet")
    
    def _get_context(self, activities):
        now = datetime.now()
        context = {
            "today": now.strftime("%A"),
            "time_now": now.strftime("%H:%M"),
            "last_run_days_ago": 0
        }
        
        if activities:
            last_run_date = datetime.fromisoformat(activities[0]["date"])
            days_ago = (now.date() - last_run_date.date()).days
            context["last_run_days_ago"] = days_ago
        
        return context
    
    def _display_recommendation(self, recommendation, activities, data_source):
        if activities:
            metrics = self.analyzer.calculate_performance_metrics(activities[:10])
            patterns = self.analyzer.detect_weekly_pattern(activities)
            
            print("\n📊 Quick Analysis:")
            print(f"   - You typically run {', '.join(patterns['favorite_days'][:2])}")
            print(f"   - Average duration: {metrics['average_duration_min']} minutes")
            if patterns["time_patterns"]:
                print(f"   - Best performance: around {patterns['time_patterns']['most_common_time']}")
        
        print("\n🎯 Today's Recommendation:")
        print(f"   ⏰ Time: {recommendation['time']}")
        print(f"   🏃‍♂️ Duration: {recommendation['duration']} minutes")
        print(f"   💪 Intensity: {recommendation['intensity'].capitalize()} pace")
        print(f"   📍 Route: Your usual neighborhood loop")
        
        print(f"\n🧠 AI Insight: \"{recommendation['insight']}\"")
        print(f"\n💬 Motivation: \"{recommendation['motivation']}\"")
        
        if data_source == "cached":
            cache = CacheManager.load_cache()
            expires = datetime.fromisoformat(cache["expires_at"])
            print(f"\n📈 Using cached data (saves API calls) | Next refresh: {expires.strftime('%b %d at %I:%M %p')}")
        
        if recommendation.get("ai_used"):
            print(f"🤖 Powered by: {recommendation.get('model', 'AI')}")
        else:
            print("📊 Analysis: Rule-based (no AI)")
    
    def export_data(self, format="json"):
        cache = CacheManager.load_cache()
        if not cache:
            print("❌ No data to export. Run --recommend first.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"running_data_{timestamp}.{format}"
        
        if format == "json":
            with open(filename, "w") as f:
                json.dump(cache, f, indent=2)
        
        print(f"✅ Data exported to {filename}")


def main():
    parser = argparse.ArgumentParser(description="AI Running Coach - Intelligent recommendations using Strava data")
    parser.add_argument("--setup", action="store_true", help="Initial Strava OAuth setup")
    parser.add_argument("--recommend", action="store_true", help="Get AI recommendation (1 API call)")
    parser.add_argument("--free", action="store_true", help="Use rule-based analysis only (0 API calls)")
    parser.add_argument("--analyze", action="store_true", help="Weekly pattern analysis")
    parser.add_argument("--status", action="store_true", help="Show profile and usage stats")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cached data")
    parser.add_argument("--export", choices=["json"], help="Export data to file")
    
    args = parser.parse_args()
    
    cli = RunningCoachCLI()
    
    if args.setup:
        cli.setup()
    elif args.recommend:
        cli.get_recommendation(use_ai=not args.free)
    elif args.analyze:
        cli.analyze_patterns()
    elif args.status:
        cli.show_status()
    elif args.clear_cache:
        CacheManager.clear_cache()
        print("✅ Cache cleared successfully")
    elif args.export:
        cli.export_data(args.export)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()