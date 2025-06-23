from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics


class SimpleAnalyzer:
    def analyze_time_patterns(self, activities):
        if not activities:
            return {"most_common_time": "18:00", "time_distribution": {}}
        
        hours = [act['start_hour'] for act in activities]
        hour_counts = Counter(hours)
        most_common_hour = hour_counts.most_common(1)[0][0] if hour_counts else 18
        
        time_distribution = defaultdict(int)
        for hour in hours:
            if hour < 6:
                time_distribution["early_morning"] += 1
            elif hour < 12:
                time_distribution["morning"] += 1
            elif hour < 17:
                time_distribution["afternoon"] += 1
            elif hour < 21:
                time_distribution["evening"] += 1
            else:
                time_distribution["night"] += 1
        
        return {
            "most_common_time": f"{most_common_hour:02d}:00",
            "time_distribution": dict(time_distribution)
        }
    
    def calculate_avg_duration(self, activities):
        if not activities:
            return 30
        
        durations = [act['duration_minutes'] for act in activities]
        return round(statistics.mean(durations))
    
    def detect_weekly_pattern(self, activities):
        if not activities:
            return {"favorite_days": ["Tuesday", "Thursday"], "runs_per_week": 3}
        
        weekdays = [act['weekday'] for act in activities]
        day_counts = Counter(weekdays)
        
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        favorite_days = [day[0] for day in sorted_days[:3]]
        
        dates = [datetime.fromisoformat(act['date']) for act in activities]
        if dates:
            date_range = (max(dates) - min(dates)).days + 1
            weeks = date_range / 7
            runs_per_week = round(len(activities) / weeks) if weeks > 0 else len(activities)
        else:
            runs_per_week = 3
        
        return {
            "favorite_days": favorite_days,
            "runs_per_week": runs_per_week,
            "day_counts": dict(day_counts)
        }
    
    def generate_rule_based_recommendation(self, patterns, context):
        time_patterns = patterns["time_patterns"]
        avg_duration = patterns["avg_duration"]
        weekly_pattern = patterns["weekly_pattern"]
        
        current_day = context['today']
        current_hour = int(context['time_now'].split(':')[0])
        
        if current_day in weekly_pattern["favorite_days"]:
            recommended_time = time_patterns["most_common_time"]
            confidence = 0.8
        else:
            recommended_time = time_patterns["most_common_time"]
            confidence = 0.6
        
        rec_hour = int(recommended_time.split(':')[0])
        if rec_hour < current_hour:
            recommended_time = f"tomorrow {recommended_time}"
        
        time_dist = time_patterns["time_distribution"]
        max_period = max(time_dist.items(), key=lambda x: x[1])[0] if time_dist else "evening"
        
        insight = f"You typically run {weekly_pattern['runs_per_week']} times per week, "
        insight += f"mostly in the {max_period} around {time_patterns['most_common_time']}"
        
        if current_day in weekly_pattern["favorite_days"]:
            motivation = f"{current_day} is one of your favorite running days - stay consistent!"
        else:
            motivation = f"Mix it up today! Your usual days are {', '.join(weekly_pattern['favorite_days'][:2])}"
        
        intensity = "moderate"
        if context['last_run_days_ago'] > 3:
            intensity = "easy"
            avg_duration = int(avg_duration * 0.8)
        elif context['last_run_days_ago'] == 0:
            intensity = "easy"
            avg_duration = int(avg_duration * 0.7)
        
        return {
            "time": recommended_time,
            "duration": avg_duration,
            "intensity": intensity,
            "insight": insight,
            "motivation": motivation,
            "confidence": confidence
        }
    
    def calculate_performance_metrics(self, activities):
        if not activities:
            return {}
        
        total_distance = sum(act['distance_km'] for act in activities)
        total_time = sum(act['duration_minutes'] for act in activities)
        
        avg_pace = total_time / total_distance if total_distance > 0 else 0
        
        distances = [act['distance_km'] for act in activities]
        durations = [act['duration_minutes'] for act in activities]
        
        return {
            "total_distance_km": round(total_distance, 1),
            "total_time_hours": round(total_time / 60, 1),
            "average_pace_min_per_km": round(avg_pace, 1),
            "average_distance_km": round(statistics.mean(distances), 1),
            "average_duration_min": round(statistics.mean(durations)),
            "longest_run_km": round(max(distances), 1),
            "total_runs": len(activities)
        }
    
    def generate_weekly_insights(self, activities):
        metrics = self.calculate_performance_metrics(activities)
        patterns = self.detect_weekly_pattern(activities)
        
        insights = []
        
        if metrics.get("total_runs", 0) > 0:
            insights.append(
                f"You've completed {metrics['total_runs']} runs totaling "
                f"{metrics['total_distance_km']}km in {metrics['total_time_hours']} hours"
            )
        
        if patterns["favorite_days"]:
            insights.append(
                f"Your most consistent running days are {' and '.join(patterns['favorite_days'][:2])}"
            )
        
        if metrics.get("average_pace_min_per_km", 0) > 0:
            pace = metrics["average_pace_min_per_km"]
            mins = int(pace)
            secs = int((pace - mins) * 60)
            insights.append(f"Your average pace is {mins}:{secs:02d} per kilometer")
        
        return {
            "insights": insights[:3],
            "ai_used": False,
            "model": "rule-based"
        }