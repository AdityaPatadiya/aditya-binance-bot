import os
from threading import Lock
from dotenv import load_dotenv
from typing import Dict, Any


class Config:
    _instance = None
    _initialized = False

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__class__._initialized:
            self.load_env()
            self.__class__._initialized = True

    def load_env(self) -> None:
        """Load enviroment variables from .env file"""
        try:
            load_dotenv()
            self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
            self.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

            if not self.api_key or not self.api_secret:
                raise ValueError("API credentials not found in .env file.")

            self.base_url = "https://testnet.binancefuture.com"
            self.timeout = 100

        except Exception as e:
            raise RuntimeError(f"Configuration failed: {str(e)}") from e
    
    @property
    def credentials(self) -> Dict[str, Any]:
        """Get alll credentials as a dictionary"""
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "base_url": self.base_url
        }
