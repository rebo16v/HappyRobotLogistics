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
    print(params)
    params_str = "|".join(f"{k}:{v}" for k, v in params.items())
    req = f"CMD:{cmd}|AUTH:{os.environ['AUTH_TOKEN']}|{params_str}\r\n"
    print(req)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((os.environ['TMS_ADDRESS'], int(os.environ['TMS_PORT'])))
    s.send(req.encode("utf-8"))
    data = s.recv(4096)
    s.close()
    
    recs = data.decode('ascii').split("\r\n")
    
    if recs[0].startswith("ERR"):
        print("ERR")
        print(recs[0])
        res = {"error": {f.split(":")[0].lower(): f.split(":")[1] for f in
                         recs[0].split("|") if not f.startswith("ERR")}}
        print(res)
        return res
    else:
        res = {"loads": {f.split(":")[0].lower(): f.split(":")[1] for f in field.split("|")} for field in
                    [rec for rec in recs if len(rec) > 0 and not rec.startswith("END")]}
        print(res)
        return res
