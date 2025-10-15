"""
College Football Data API Client
Fetches data from https://api.collegefootballdata.com/
"""

import requests
import pandas as pd
import logging
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CFBDataFetcher:
    """Client for fetching data from the College Football Data API"""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the CFB Data Fetcher
        
        Args:
            api_key: Your College Football Data API key
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        if not api_key:
            raise ValueError("API key is required")
            
        self.api_key = api_key
        self.base_url = "https://api.collegefootballdata.com"
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info("CFBDataFetcher initialized successfully")
    
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
            
        Raises:
            ValueError: If invalid parameters are provided
            requests.RequestException: If API request fails
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100")
        
        url = f"{self.base_url}/games"
        params = {
            "year": year,
            "seasonType": season_type
        }
        
        if week:
            if week < 1 or week > 20:
                raise ValueError(f"Invalid week: {week}. Must be between 1 and 20")
            params["week"] = week
        if team:
            params["team"] = team
        
        try:
            logger.info(f"Fetching games for year={year}, week={week}, season_type={season_type}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} games")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching games: {e}")
            raise
    
    def get_team_stats(self, year: int, team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch team statistics for a given year
        
        Args:
            year: Season year
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with team statistics
            
        Raises:
            ValueError: If invalid parameters are provided
            requests.RequestException: If API request fails
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100")
            
        url = f"{self.base_url}/stats/season"
        params = {"year": year}
        
        if team:
            params["team"] = team
        
        try:
            logger.info(f"Fetching team stats for year={year}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched stats for {len(data)} team records")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching team stats: {e}")
            raise
    
    def get_team_records(self, year: int, team: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch team records for a given year
        
        Args:
            year: Season year
            team: Specific team to filter by (optional)
            
        Returns:
            DataFrame with team records
            
        Raises:
            ValueError: If invalid parameters are provided
            requests.RequestException: If API request fails
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100")
            
        url = f"{self.base_url}/records"
        params = {"year": year}
        
        if team:
            params["team"] = team
        
        try:
            logger.info(f"Fetching team records for year={year}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched records for {len(data)} teams")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching team records: {e}")
            raise
    
    def get_team_talent(self, year: int) -> pd.DataFrame:
        """
        Fetch team talent ratings
        
        Args:
            year: Season year
            
        Returns:
            DataFrame with team talent ratings
            
        Raises:
            ValueError: If invalid parameters are provided
            requests.RequestException: If API request fails
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100")
            
        url = f"{self.base_url}/talent"
        params = {"year": year}
        
        try:
            logger.info(f"Fetching team talent for year={year}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched talent for {len(data)} teams")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching team talent: {e}")
            raise
    
    def get_teams(self) -> pd.DataFrame:
        """
        Fetch all FBS teams
        
        Returns:
            DataFrame with team information
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/teams/fbs"
        
        try:
            logger.info("Fetching all FBS teams")
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} teams")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching teams: {e}")
            raise
    
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
            
        Raises:
            ValueError: If invalid parameters are provided
            requests.RequestException: If API request fails
        """
        if year < 2000 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Must be between 2000 and 2100")
            
        url = f"{self.base_url}/lines"
        params = {"year": year}
        
        if week:
            if week < 1 or week > 20:
                raise ValueError(f"Invalid week: {week}. Must be between 1 and 20")
            params["week"] = week
        if team:
            params["team"] = team
        
        try:
            logger.info(f"Fetching betting lines for year={year}, week={week}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched betting lines for {len(data)} games")
            return pd.DataFrame(data)
        except requests.RequestException as e:
            logger.error(f"Error fetching betting lines: {e}")
            raise
