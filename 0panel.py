#!/usr/bin/env python3
# 0day - OSINT/OPSEC panel

import os
import sys
import subprocess
import hashlib
import base64
import secrets
import string
import socket
import json
import time
import re
import shutil
from datetime import datetime
from pathlib import Path
from getpass import getpass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt
    from rich import box
except ImportError:
    print("install rich first: pip3 install rich --break-system-packages")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None

console = Console()

TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR))

BANNER = r"""
    ___  _____      __     __
   / _ \|  __ \   /\ \   / /
  | | | | |  | | /  \ \_/ / 
  | | | | |  | |/ /\ \ \ /  
  | |_| | |__| / ____ \| |   
   \___/|_____/_/    \_\_|   
"""

def clr():
    os.system('clear')

def runcmd(cmd, timeout=30):
    # run a shell cmd and return output
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return "[!] timed out"
    except Exception as e:
        return f"[!] {e}"

def has_tool(name):
    return shutil.which(name) is not None

def banner():
    clr()
    console.print(BANNER, justify="center", style="bold red")
    console.print("[dim]OSINT & OPSEC Command Center[/dim]", justify="center")
    console.print(f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]", justify="center")
    print()

def menu(title, opts, extra=None):
    # generic menu builder
    t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
    t.add_column("", style="bold yellow", width=4)
    t.add_column("", style="white")
    for i, o in enumerate(opts, 1):
        t.add_row(str(i), o)
    if extra:
        t.add_row("", "")
        for k, v in extra.items():
            t.add_row(k, v)
    console.print(Panel(t, title=f"[bold]{title}[/bold]", border_style="red"))

def pick(mx):
    while True:
        raw = Prompt.ask("[bold yellow]>[/bold yellow]").strip()
        if raw.lower() in ('q', 'quit', 'exit'):
            clean_exit()
            sys.exit(0)
        try:
            c = int(raw)
            if 1 <= c <= mx:
                return c
        except ValueError:
            pass
        console.print("[red]bad input[/red]")

def pause():
    Prompt.ask("\n[dim]enter to go back[/dim]")

def safe_request(url, method="GET", **kwargs):
    if not requests:
        console.print("[red]requests not installed[/red]")
        return None
    try:
        kwargs.setdefault("timeout", 10)
        if method == "POST":
            return requests.post(url, **kwargs)
        return requests.get(url, **kwargs)
    except Exception as e:
        console.print(f"[red]request failed: {e}[/red]")
        return None

def clean_exit():
    # wipe temp stuff
    import glob
    for f in glob.glob("/tmp/.0day_*"):
        try: os.remove(f)
        except: pass


# ============================================================
#  MAIN
# ============================================================
def main():
    while True:
        banner()
        menu("0DAY", [
            "OSINT Recon       - IP/DNS/WHOIS/Ports/Subdomains",
            "Web Recon         - Headers/Tech/Dirs/Robots",
            "Network Tools     - Ping/Trace/Scan/Interfaces",
            "OPSEC & Anon      - MAC/VPN/DNS Leak/Wipe",
            "Metasploit        - Cmd Builder & Payloads",
            "Crypto & Hash     - Hash/Encode/Decode/Passwd Gen",
            "Deep Recon        - Email/Username/Phone Intel",
            "Stealth Ops       - Anti-Forensics/Timestomp",
            "Wireless          - WiFi Recon/Handshake Tools",
            "Social Recon      - Social Media OSINT",
            "C2 Panel          - Listeners/Sessions/Post-Exploit",
            "Reverse Shells    - Every Language Shell Generator",
            "Webshells         - PHP/JSP/ASP/Python Shells",
            "Exploits & Vulns  - CVE DB/SearchSploit/Nmap Vuln",
            "Credentials       - Hashcat/John/Password Spray",
            "Persistence       - Cron/Systemd/Registry/Services",
            "Privilege Esc     - Linux/Windows Privesc Checklist",
            "Tunnels & Pivots  - SSH/Chisel/Ligolo/Socat",
            "Phishing          - Credential Harvester/SET/Evilginx",
        ], {"q": "Quit"})

        c = pick(20)
        if c == 1:
            from modules.recon import run as mod
            mod()
        elif c == 2:
            from modules.web_recon import run as mod
            mod()
        elif c == 3:
            from modules.network import run as mod
            mod()
        elif c == 4:
            from modules.opsec import run as mod
            mod()
        elif c == 5:
            from modules.metasploit import run as mod
            mod()
        elif c == 6:
            from modules.crypto import run as mod
            mod()
        elif c == 7:
            from modules.deep_recon import run as mod
            mod()
        elif c == 8:
            from modules.stealth import run as mod
            mod()
        elif c == 9:
            from modules.wireless import run as mod
            mod()
        elif c == 10:
            from modules.social import run as mod
            mod()
        elif c == 11:
            from modules.c2 import run as mod
            mod()
        elif c == 12:
            from modules.shells import run as mod
            mod()
        elif c == 13:
            from modules.webshells import run as mod
            mod()
        elif c == 14:
            from modules.exploits import run as mod
            mod()
        elif c == 15:
            from modules.credentials import run as mod
            mod()
        elif c == 16:
            from modules.persistence import run as mod
            mod()
        elif c == 17:
            from modules.privesc import run as mod
            mod()
        elif c == 18:
            from modules.tunnels import run as mod
            mod()
        elif c == 19:
            from modules.phishing import run as mod
            mod()
        elif c == 20:
            clean_exit()
            console.print("[red]later nerd[/red]")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        clean_exit()
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]something broke: {e}[/red]")
        clean_exit()
        sys.exit(1)
