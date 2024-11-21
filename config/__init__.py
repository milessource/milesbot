from __future__ import annotations

from dotenv import load_dotenv; load_dotenv()
from os import environ

from typing import List
from dataclasses import dataclass

@dataclass
class configuration:
    secure_discord_token: str = environ.get("TOKEN")
    
    oids: List[int] = [719689674813079683, 1307111409338814625]
