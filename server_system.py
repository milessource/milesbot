from __future__ import annotations

from typing import Tuple, List

from mcstatus.status_response import JavaStatusResponse
from mcstatus import JavaServer

_server_lookup: JavaServer | None = None
_server_status: JavaStatusResponse | None = None
is_working: bool = False

def _connect_to_server() -> None:
    """attempt to connect to the server and update global state"""
    global _server_lookup, _server_status, is_working
    try:
        _server_lookup = JavaServer.lookup("pixspace.ddns.net:25565")
        _server_status = _server_lookup.status()
        
        is_working = True
    except Exception as e: is_working = False
_connect_to_server()

def reconnect() -> None: _connect_to_server()

def request_lenght() -> Tuple[int, int] | None:
    """request online lenght in `tuple[int, int]` where first int is \
        online now and second is max"""
    if not is_working: return None
    try:
        return (_server_status.players.online, _server_status.players.max)
    except Exception as e: return None
    
def request_lenght_names() -> List[str]:
    if not is_working: return None
    try:
        return [jsp.name for jsp in _server_status.players.sample]
    except Exception as e: return None

def request_information() -> Tuple[str] | None:
    """request all information in tuple[...] with params -> version.name(str), \
        version.protocol(int), *request_lenght"""
    if not is_working: return None
    try:
        return (_server_status.version.name, _server_status.version.protocol,
            _server_status.players.online, _server_status.players.max)
    except Exception as e: return None
