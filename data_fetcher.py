"""
College Football Data API Client
Fetches data from https://api.collegefootballdata.com/
"""

import requests
import pandas as pd
from typing import List, Dict, Optional


class CFBDataFetcher:
    """Client for fetching data from the College Football Data API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the CFB Data Fetcher
        
        Args:
            api_key: Your College Football Data API key
        """
        self.api_key = api_key
        self.base_url = "https://api.collegefootballdata.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    
    def get_games(self, year: int, week: Optional[int] = None, 
                  season_type: str = "regular", team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch games for a given year and optional week
        
        Args:
            year: Season year
            week: Week number (optional)
            season_type: Type of season (regular, postseason)
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with game information
        """
        url = f"{self.base_url}/games"
        params = {
            "year": year,
            "seasonType": season_type
        }
        
        if week:
            params["week"] = week
        if team:
            params["team"] = team
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def get_team_stats(self, year: int, team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch team statistics for a given year
        
        Args:
            year: Season year
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with team statistics
        """
        url = f"{self.base_url}/stats/season"
        params = {"year": year}
        
        if team:
            params["team"] = team
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def get_team_records(self, year: int, team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch team records for a given year
        
        Args:
            year: Season year
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with team records
        """
        url = f"{self.base_url}/records"
        params = {"year": year}
        
        if team:
            params["team"] = team
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def get_team_talent(self, year: int) -> pd.DataFrame:
        """
        Fetch team talent ratings
        
        Args:
            year: Season year
            
        Returns:
            DataFrame with team talent ratings
        """
        url = f"{self.base_url}/talent"
        params = {"year": year}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def get_teams(self) -> pd.DataFrame:
        """
        Fetch all FBS teams
        
        Returns:
            DataFrame with team information
        """
        url = f"{self.base_url}/teams/fbs"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def get_betting_lines(self, year: int, week: Optional[int] = None, 
                          team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch betting lines for games
        
        Args:
            year: Season year
            week: Week number (optional)
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with betting line information
        """
        url = f"{self.base_url}/lines"
        params = {"year": year}
        
        if week:
            params["week"] = week
        if team:
            params["team"] = team
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
