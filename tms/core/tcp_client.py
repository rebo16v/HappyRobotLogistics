import socket
import os
from typing import Dict


def make_request(cmd: str, params: Dict[str, str]) -> Dict:
    """
    Send a command to the TCP server and return the response.
    
    Args:
        cmd: The command to execute (e.g., "LOAD_QUERY", "LOAD_GET", "LOAD_BOOK")
        params: Dictionary of parameters for the command
    
    Returns:
        Dictionary containing either the response data or error information
    """

    params_str = "|".join(f"{k}:{v}" for k, v in params.items())
    req = f"CMD:{cmd}|AUTH:{os.environ['AUTH_TOKEN']}|{params_str}\r\n"
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((os.environ['TMS_ADDRESS'], int(os.environ['TMS_PORT'])))
        s.send(req.encode("utf-8"))
        data = s.recv(4096)
    except socket.timeout:
        return {"error": {"type": "timeout", "message": "Connection timed out"}}
    except ConnectionRefusedError:
        return {"error": {"type": "connection_refused", "message": "Connection refused by server"}}
    except socket.gaierror:
        return {"error": {"type": "dns_error", "message": "Failed to resolve server address"}}
    except OSError as e:
        return {"error": {"type": "socket_error", "message": str(e)}}
    finally:
        s.close()
    
    try:
        res = data.decode('ascii')
        recs = res.split("\r\n")
    except UnicodeDecodeError:
        return {"error": {"type": "decode_error", "message": "Failed to decode response as ASCII"}}
    
    if not recs or len(recs) == 0:
        return {"error": {"type": "empty_response", "message": "Server returned empty response"}}
    
    try:
        if recs[0].startswith("ERR"):
            res = {"error": {f.split(":")[0].lower(): f.split(":")[1] for f in
                             recs[0].split("|") if not f.startswith("ERR")}}
        else:
            res = {"loads": {f.split(":")[0].lower(): f.split(":")[1] for f in field.split("|")} for field in
                        [rec for rec in recs if len(rec) > 0 and not rec.startswith("END")]}

        return res
    except (IndexError, ValueError) as e:
        return {"error": {"type": "parse_error", "message": f"Failed to parse response: {str(e)}"}}
