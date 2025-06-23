# AI Running Coach - Implementation Summary

## Project Overview
A Python CLI application that provides intelligent running recommendations by analyzing Strava data using FREE AI models. Designed for $0 monthly operating cost through strategic API usage and caching.

## Architecture Decisions

### 1. Cost Optimization Strategy
- **FREE AI Models Only**: Uses `meta-llama/llama-3.1-8b-instruct:free` from OpenRouter
- **24-Hour Caching**: Prevents redundant API calls (max 1 AI call/day)
- **Data Compression**: Minimal data sent to AI (date, duration, distance, time)
- **Rule-Based Fallback**: Ensures functionality even without AI

### 2. Core Components

#### `strava_client.py` - Strava Integration
- OAuth 2.0 flow with local callback server (port 8080)
- Automatic token refresh mechanism
- Activity data compression (15 most recent runs)
- Extracts only essential metrics: date, duration, distance, start_hour, weekday

#### `ai_coach.py` - AI Coach Engine
- OpenAI-compatible client for OpenRouter
- Ultra-efficient prompting (<500 tokens)
- JSON response parsing with fallback handling
- Temperature=0.2 for consistent recommendations
- Single API call combines analysis + recommendation

#### `data_analyzer.py` - Rule-Based Analysis
- Statistical analysis of running patterns
- Time preference detection (morning/evening runner)
- Weekly pattern recognition (favorite days)
- Performance metrics calculation
- Works independently as fallback system

#### `main.py` - CLI Interface
- Argument-based command structure
- Cache management system
- Profile tracking for usage stats
- Multiple output formats (console, JSON export)
- Graceful error handling

### 3. Data Flow

```
User → CLI Command → Cache Check → Strava API → AI/Rules → Recommendation → Cache Save
                          ↓                                        ↑
                     (If Fresh)                              (If Cached)
                          └────────────────────────────────────────┘
```

### 4. Caching Strategy
- **Location**: `data/cache.json`
- **Duration**: 24 hours
- **Contents**: Strava activities + AI recommendation
- **Benefits**: 
  - Reduces Strava API calls
  - Minimizes AI API usage
  - Instant recommendations on subsequent runs

### 5. Security & Privacy
- Local token storage only (`data/tokens.json`)
- No personal data sent to AI
- Strava scope limited to `activity:read_all`
- All sensitive files in `.gitignore`

## Implementation Highlights

### Smart Prompt Engineering
```python
# Compressed format to minimize tokens:
"Recent runs (newest first):
Tue 18:30 - 35min, 5.2km
Thu 18:15 - 32min, 4.8km
..."
```

### Fallback Logic
1. Try AI recommendation
2. On failure → Rule-based analysis
3. On no data → Default beginner recommendation

### Context Awareness
- Current day of week
- Time since last run
- Time of day for recommendation
- Historical performance patterns

## Usage Patterns

### Daily Workflow
```bash
# Morning check
python main.py --recommend  # Uses cache if <24h old

# Force fresh analysis
python main.py --clear-cache
python main.py --recommend

# Weekly review
python main.py --analyze
```

### Cost Analysis
- **Strava API**: Free (rate limited)
- **OpenRouter AI**: Free tier (~1000 calls/month available)
- **Actual Usage**: ~30 calls/month max
- **Monthly Cost**: $0.00

## Technical Decisions

### Why OpenRouter?
- Free tier with quality models
- OpenAI-compatible API
- No credit card required
- Sufficient for our use case

### Why 24-Hour Cache?
- Balances freshness vs API usage
- Most runners check once daily
- Reduces costs to essentially zero

### Why Rule-Based Fallback?
- 100% reliability guarantee
- No dependency on external services
- Often sufficient for basic recommendations

## Performance Metrics

- **Startup Time**: <1 second (with cache)
- **Fresh Recommendation**: 2-5 seconds
- **Cache Size**: ~5-10 KB
- **Memory Usage**: Minimal (~20MB Python process)

## Future Optimization Opportunities

1. **Weather Integration**: Add context without AI calls
2. **Progressive Web App**: Browser-based interface
3. **Multi-User Support**: Family accounts
4. **Goal Tracking**: Long-term progress monitoring
5. **Workout Types**: Intervals, long runs, recovery

## Lessons Learned

1. **Free Tiers Are Powerful**: Careful usage stays within limits
2. **Caching Is Critical**: Dramatically reduces operational costs
3. **Fallbacks Are Essential**: Users need reliability
4. **Simple Prompts Work**: Don't over-engineer AI interactions
5. **Local-First Approach**: Privacy and cost benefits

## Maintenance Notes

- Monitor OpenRouter free tier changes
- Update Strava OAuth tokens before expiry
- Clear cache if data seems stale
- Check rule-based calculations seasonally

---

*This implementation demonstrates how to build a useful AI application with $0 operating costs through careful architecture and smart resource usage.*