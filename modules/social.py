# social media osint - profile scraping, info gathering
import os, subprocess, json, re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

def clr():
    os.system('clear')

def runcmd(cmd, t=30):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return p.stdout + p.stderr
    except:
        return "[!] failed"

def pause():
    Prompt.ask("\n[dim]enter to continue[/dim]")


def profile_search():
    clr()
    console.print("[bold red]=== SOCIAL MEDIA PROFILE SEARCH ===[/bold red]\n")
    username = Prompt.ask("[cyan]target username[/cyan]")
    
    # all the platforms we can check
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Twitter/X": f"https://x.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "LinkedIn": f"https://www.linkedin.com/in/{username}/",
        "Medium": f"https://medium.com/@{username}",
        "Keybase": f"https://keybase.io/{username}",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
        "npm": f"https://www.npmjs.com/~{username}",
        "Docker Hub": f"https://hub.docker.com/u/{username}",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Flickr": f"https://www.flickr.com/people/{username}/",
        "Telegram": f"https://t.me/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Fiverr": f"https://www.fiverr.com/{username}",
        "Gravatar": f"https://en.gravatar.com/{username}",
        "Imgur": f"https://imgur.com/user/{username}",
        "Pastebin": f"https://pastebin.com/u/{username}",
        "Replit": f"https://replit.com/@{username}",
        "CodePen": f"https://codepen.io/{username}",
        "LeetCode": f"https://leetcode.com/{username}",
        "Chess.com": f"https://chess.com/member/{username}",
        "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
    }
    
    console.print(f"\n[yellow]checking {len(platforms)} platforms for @{username}...[/yellow]\n")
    
    try:
        import requests
        found = []
        ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        for name, url in platforms.items():
            try:
                r = requests.get(url, timeout=5, allow_redirects=False, headers=ua)
                if r.status_code == 200:
                    console.print(f"  [green]{name:15s} FOUND  {url}[/green]")
                    found.append((name, url))
                elif r.status_code == 404:
                    pass  # not found, skip
                elif r.status_code in [301, 302]:
                    loc = r.headers.get("Location", "")
                    if "login" not in loc.lower():
                        console.print(f"  [yellow]{name:15s} {r.status_code} -> {loc}[/yellow]")
                else:
                    pass
            except:
                pass
        
        console.print(f"\n[green]found {len(found)} profiles[/green]")
        
        if found:
            console.print("\n[dim]use 'curl -L <url>' for more info on each profile[/dim]")
            
    except ImportError:
        console.print("[red]install requests: pip3 install requests[/red]")
    
    console.print("\n[dim]for deeper search, install:[/dim]")
    console.print("  [dim]sherlock: pip3 install sherlock-project[/dim]")
    console.print("  [dim]maigret: pip3 install maigret[/dim]")
    pause()

def email_to_social():
    clr()
    console.print("[bold red]=== EMAIL -> SOCIAL ACCOUNTS ===[/bold red]\n")
    email = Prompt.ask("[cyan]target email[/cyan]")
    
    console.print(f"\n[yellow]checking accounts linked to {email}...[/yellow]\n")
    
    # gravatar
    import hashlib
    md5 = hashlib.md5(email.lower().strip().encode()).hexdigest()
    console.print(f"[yellow]Gravatar:[/yellow]")
    console.print(f"  hash: {md5}")
    console.print(f"  url: https://www.gravatar.com/avatar/{md5}")
    
    # try haveibeenpwned (just link)
    console.print(f"\n[yellow]Breach databases:[/yellow]")
    console.print(f"  https://haveibeenpwned.com/account/{email}")
    console.print(f"  https://breachdirectory.org/")
    
    # holehe suggestion
    console.print(f"\n[yellow]recommended tools:[/yellow]")
    console.print(f"  holehe {email}     (checks 100+ sites)")
    console.print(f"  holehe_all {email}  (all modules)")
    console.print(f"  ghunt {email}       (google account lookup)")
    console.print(f"  theHarvester -d {email.split('@')[-1]}")
    
    # google dorks
    domain = email.split("@")[-1]
    user = email.split("@")[0]
    console.print(f"\n[yellow]Google dorks:[/yellow]")
    console.print(f'  "{email}" site:linkedin.com')
    console.print(f'  "{email}" site:twitter.com')
    console.print(f'  "{email}" site:facebook.com')
    console.print(f'  "{user}" site:github.com')
    console.print(f'  intext:"{email}" filetype:pdf')
    
    pause()

def meta_data():
    clr()
    console.print("[bold red]=== IMAGE METADATA EXTRACTION ===[/bold red]\n")
    path = Prompt.ask("[cyan]image file path[/cyan]")
    
    if not os.path.exists(path):
        console.print("[red]file not found[/red]")
        pause()
        return
    
    # exiftool
    if os.path.exists("/usr/bin/exiftool"):
        console.print(f"\n[yellow]exiftool output:[/yellow]\n")
        out = runcmd(f"exiftool '{path}'")
        console.print(out)
    else:
        console.print("[dim]exiftool not found, installing...[/dim]")
    
    # python fallback
    console.print("[yellow]--- basic info ---[/yellow]")
    import struct
    
    try:
        size = os.path.getsize(path)
        console.print(f"  file size: {size} bytes")
        
        with open(path, 'rb') as f:
            header = f.read(32)
            if header[:2] == b'\xff\xd8':
                console.print("  format: JPEG")
                # try to find EXIF
                f.seek(0)
                data = f.read()
                exif_pos = data.find(b'Exif')
                if exif_pos >= 0:
                    console.print(f"  EXIF data found at offset {exif_pos}")
                else:
                    console.print("  no EXIF data found")
            elif header[:4] == b'\x89PNG':
                console.print("  format: PNG")
            elif header[:4] == b'RIFF':
                console.print("  format: WebP")
            else:
                console.print(f"  format: unknown (header: {header[:4].hex()})")
    except Exception as e:
        console.print(f"  error: {e}")
    
    console.print("\n[dim]install exiftool for full metadata: pacman -S perl-image-exiftool[/dim]")
    pause()

def osint_framework():
    clr()
    console.print("[bold red]=== OSINT FRAMEWORK REFERENCE ===[/bold red]\n")
    console.print("""[yellow]useful OSINT websites and tools:[/y]

[i]--- IP & Domain ---[/i]
  shodan.io              - internet device search
  censys.io              - certificate/host search  
  riskiq.com             - threat intelligence
  virustotal.com         - file/url/domain scanning
  urlscan.io             - website scanner
  securitytrails.com    - domain history
  viewdns.info           - DNS tools
  mxtoolbox.com          - email/DNS tools

[i]--- Username ---[/i]
  namechk.com            - username availability
  whatsmyname.app        - username enumeration
  sherlock               - CLI username search

[i]--- Email ---[/i]
  hunter.io              - email finder
  holehe                 - CLI email OSINT
  ghunt                  - google account lookup
  theHarvester           - email/domain harvest

[i]--- Social Media ---[/i]
  social-searcher.com    - social media search
  pipl.com               - people search (paid)
  spokeo.com             - people search (paid)
  whitepages.com         - people search

[i]--- Data Breaches ---[/i]
  haveibeenpwned.com     - breach checker
  dehashed.com           - breach database (paid)
  leaked.site            - leaked data search
  intelx.io              - intelligence search

[i]--- Phone ---[/i]
  truecaller.com         - caller ID
  numverify.com          - number validation
  sync.me                - contact sync

[i]--- Geolocation ---[/i]
  google.com/maps        - street view
  yandex.com/maps        - satellite view
  mapillary.com          - street-level photos
  sunCalc.org            - sun position (shadow analysis)
  
[i]--- Crypto ---[/i]
  blockchain.com         - bitcoin explorer
  etherscan.io           - ethereum explorer
  osint.industries       - crypto tracking
""")
    pause()

def git_dorking():
    clr()
    console.print("[bold red]=== GIT DORKING ===[/bold red]\n")
    target = Prompt.ask("[cyan]target (org, user, or repo)[/cyan]")
    
    console.print(f"\n[yellow]Google dorks for GitHub:[/yellow]\n")
    
    dorks = [
        f'site:github.com "{target}" password',
        f'site:github.com "{target}" api_key',
        f'site:github.com "{target}" secret',
        f'site:github.com "{target}" token',
        f'site:github.com "{target}" credential',
        f'site:github.com "{target}" aws_key',
        f'site:github.com "{target}" private_key',
        f'site:github.com "{target}" .env',
        f'site:github.com "{target}" config.json',
        f'site:github.com "{target}" database_url',
    ]
    
    for i, dork in enumerate(dorks, 1):
        console.print(f"  [{i}] {dork}")
    
    console.print(f"\n[yellow]direct searches:[/yellow]")
    console.print(f"  https://github.com/search?q={target}&type=code")
    console.print(f"  https://github.com/search?q={target}&type=commits")
    console.print(f"  https://github.com/search?q={target}&type=repositories")
    
    # try github api
    console.print(f"\n[yellow]GitHub API info:[/yellow]")
    try:
        import requests
        r = requests.get(f"https://api.github.com/users/{target}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            for k in ["name", "bio", "blog", "location", "email", "company",
                      "public_repos", "followers", "created_at"]:
                if k in data and data[k]:
                    console.print(f"  {k}: {data[k]}")
    except:
        pass
    
    pause()

def whois_domain_history():
    clr()
    console.print("[bold red]=== DOMAIN HISTORY ===[/bold red]\n")
    domain = Prompt.ask("[cyan]domain[/cyan]")
    
    # wayback machine
    console.print("[yellow]Wayback Machine snapshots:[/yellow]")
    try:
        import requests
        r = requests.get(
            f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=10&fl=timestamp,statuscode,mimetype",
            timeout=10
        )
        data = r.json()
        if len(data) > 1:  # first row is headers
            for row in data[1:]:
                ts, status, mime = row
                date = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
                console.print(f"  {date}  {status}  {mime}")
        else:
            console.print("  [dim]no snapshots found[/dim]")
    except Exception as e:
        console.print(f"  [red]error: {e}[/red]")
    
    # whois history
    console.print(f"\n[yellow]WHOIS history (check manually):[/yellow]")
    console.print(f"  https://whois.domaintools.com/{domain}")
    console.print(f"  https://securitytrails.com/domain/{domain}/dns")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== SOCIAL RECON ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Username Profile Search",
            "Email -> Social Accounts",
            "Image Metadata Extraction",
            "Git Dorking",
            "Domain History (Wayback)",
            "OSINT Framework Reference",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]SOCIAL RECON[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: profile_search()
        elif c == 2: email_to_social()
        elif c == 3: meta_data()
        elif c == 4: git_dorking()
        elif c == 5: whois_domain_history()
        elif c == 6: osint_framework()
        elif c == 0: return
