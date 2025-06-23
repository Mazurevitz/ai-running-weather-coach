# AI Running Coach 🏃‍♂️

An intelligent running coach that uses your Strava data and FREE AI models to provide personalized daily recommendations. Designed to cost $0-2/month maximum through smart caching and free tier usage.

## Features

- **Strava Integration**: OAuth flow to securely access your running data
- **FREE AI Analysis**: Uses free models from OpenRouter (meta-llama/llama-3.1-8b-instruct:free)
- **Smart Caching**: 24-hour cache to minimize API calls (max 1 AI call per day)
- **Rule-Based Fallback**: Works even without AI for reliable recommendations
- **Pattern Recognition**: Analyzes your running habits, preferred times, and consistency
- **Cost Optimization**: Designed to stay within free tier limits

## Quick Start

1. **Clone and Setup**
   ```bash
   cd ai_running_coach
   cp .env.example .env
   # Edit .env with your API keys
   pip install -r requirements.txt
   ```

2. **Get API Keys**
   - Strava: Create app at https://www.strava.com/settings/api
   - OpenRouter: Get free API key at https://openrouter.ai/keys

3. **Initial Setup**
   ```bash
   python main.py --setup
   ```

4. **Get Daily Recommendation**
   ```bash
   python main.py --recommend          # AI recommendation (1 API call)
   python main.py --recommend --free   # Rule-based only (0 API calls)
   ```

## Usage Examples

```bash
# View weekly patterns and insights
python main.py --analyze

# Check status and API usage
python main.py --status

# Export your data
python main.py --export json

# Clear cache to force fresh data
python main.py --clear-cache
```

## Sample Output

```
🏃‍♂️ AI Running Coach Recommendation
==================================================

📊 Quick Analysis:
   - You typically run Tuesday, Thursday
   - Average duration: 32 minutes
   - Best performance: around 18:00

🎯 Today's Recommendation:
   ⏰ Time: 6:00 PM
   🏃‍♂️ Duration: 30 minutes
   💪 Intensity: Moderate pace
   📍 Route: Your usual neighborhood loop

🧠 AI Insight: "You perform 18% better on weekday evenings based on your last 10 runs"

💬 Motivation: "Tuesday is your sweet spot - go crush it!"

📈 Using cached data (saves API calls) | Next refresh: Jun 24 at 2:30 PM
🤖 Powered by: meta-llama/llama-3.1-8b-instruct:free
```

## Cost Breakdown

- **Strava API**: FREE (within rate limits)
- **OpenRouter AI**: FREE (using free models, ~30-50 calls/month)
- **Total Monthly Cost**: $0.00

## Technical Details

- **Caching**: All data cached for 24 hours to minimize API usage
- **Data Compression**: Only essential running metrics sent to AI (date, duration, distance, time)
- **Fallback Logic**: Rule-based analysis when AI unavailable
- **Token Management**: Automatic refresh of Strava OAuth tokens

## Project Structure

```
ai_running_coach/
├── main.py              # CLI interface
├── strava_client.py     # Strava OAuth & API
├── ai_coach.py          # FREE AI integration
├── data_analyzer.py     # Rule-based analysis
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── data/               # Cache and tokens (gitignored)
```

## Privacy & Security

- All data stored locally in `data/` directory
- Strava tokens encrypted and never shared
- AI receives only anonymized running metrics
- No personal information sent to AI services

## Troubleshooting

1. **"No Strava credentials"**: Check your .env file has correct STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET
2. **"Failed to fetch Strava data"**: Run `python main.py --setup` to re-authenticate
3. **"AI API error"**: Verify your OPENROUTER_API_KEY is valid
4. **Cache issues**: Run `python main.py --clear-cache`

## Future Enhancements

- Weather integration for context-aware recommendations
- Goal tracking and progress monitoring
- Export to training platforms
- Multi-user support for families

## License

MIT License - feel free to modify and share!
