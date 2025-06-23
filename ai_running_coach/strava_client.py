import json
import time
import webbrowser
import requests
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

from config import (
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI,
    STRAVA_AUTH_URL, STRAVA_TOKEN_URL, STRAVA_API_BASE,
    TOKENS_FILE
)


class StravaCallbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Success!</h1><p>You can close this window.</p></body></html>")
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Error!</h1><p>No authorization code received.</p></body></html>")


class StravaClient:
    def __init__(self):
        self.tokens = self.load_tokens()
        
    def get_authorization_url(self):
        params = {
            "client_id": STRAVA_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": STRAVA_REDIRECT_URI,
            "approval_prompt": "force",
            "scope": "activity:read_all"
        }
        url = f"{STRAVA_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return url
    
    def exchange_code_for_tokens(self, code):
        data = {
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(STRAVA_TOKEN_URL, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.tokens = tokens
            self.save_tokens()
            return True
        return False
    
    def refresh_access_token(self):
        if not self.tokens or "refresh_token" not in self.tokens:
            return False
            
        data = {
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "refresh_token": self.tokens["refresh_token"],
            "grant_type": "refresh_token"
        }
        
        response = requests.post(STRAVA_TOKEN_URL, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.tokens.update(tokens)
            self.save_tokens()
            return True
        return False
    
    def ensure_valid_token(self):
        if not self.tokens:
            return False
            
        if "expires_at" in self.tokens:
            if time.time() > self.tokens["expires_at"]:
                return self.refresh_access_token()
        return True
    
    def get_athlete_activities(self, limit=20):
        if not self.ensure_valid_token():
            return None
            
        headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
        params = {"per_page": limit}
        
        response = requests.get(f"{STRAVA_API_BASE}/athlete/activities", headers=headers, params=params)
        
        if response.status_code == 200:
            activities = response.json()
            running_activities = []
            
            for activity in activities:
                if activity["type"] in ["Run", "VirtualRun"]:
                    compressed = {
                        "date": activity["start_date_local"][:10],
                        "start_time": activity["start_date_local"][11:16],
                        "duration_minutes": int(activity["elapsed_time"] / 60),
                        "distance_km": round(activity["distance"] / 1000, 2),
                        "start_hour": int(activity["start_date_local"][11:13]),
                        "weekday": datetime.fromisoformat(activity["start_date_local"]).strftime("%A"),
                        "average_speed": round(activity["average_speed"] * 3.6, 2) if "average_speed" in activity else None
                    }
                    running_activities.append(compressed)
            
            return running_activities[:MAX_ACTIVITIES_TO_ANALYZE]
        return None
    
    def save_tokens(self):
        with open(TOKENS_FILE, "w") as f:
            json.dump(self.tokens, f)
    
    def load_tokens(self):
        try:
            with open(TOKENS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def oauth_flow(self):
        auth_url = self.get_authorization_url()
        print(f"\n🌐 Opening browser for Strava authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        
        webbrowser.open(auth_url)
        
        server = HTTPServer(("localhost", 8080), StravaCallbackHandler)
        server.auth_code = None
        
        print("\n⏳ Waiting for authorization...")
        
        def serve_once():
            while server.auth_code is None:
                server.handle_request()
        
        server_thread = threading.Thread(target=serve_once)
        server_thread.start()
        server_thread.join(timeout=120)
        
        if server.auth_code:
            print("✅ Authorization code received!")
            if self.exchange_code_for_tokens(server.auth_code):
                print("✅ Tokens saved successfully!")
                return True
            else:
                print("❌ Failed to exchange code for tokens")
        else:
            print("❌ No authorization code received")
        
        return False


from config import MAX_ACTIVITIES_TO_ANALYZE