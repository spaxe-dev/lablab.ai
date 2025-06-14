"""Configuration settings for the Dependency Health Checker"""

import os
from typing import List

class Settings:
    # API Configuration
    API_TITLE = "Dependency Health Checker"
    API_DESCRIPTION = "API for checking vulnerabilities in Python and Node.js dependencies"
    API_VERSION = "1.0.0"
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    
    # NVD API Configuration
    NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    NVD_API_KEY = os.getenv("NVD_API_KEY")  # Optional, for higher rate limits
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 60
    REQUEST_DELAY = 0.1  # Delay between NVD API calls
    
    # File Upload Limits
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES = ["requirements.txt", "package.json"]
    
    # GitHub Configuration
    GITHUB_BASE_URL = "https://raw.githubusercontent.com"
    SUPPORTED_BRANCHES = ["main", "master", "develop"]
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

settings = Settings()
