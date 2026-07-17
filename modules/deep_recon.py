# deep recon - email, username, phone, domain intel
import os, subprocess, json, re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def runcmd(cmd, t=30):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return p.stdout + p.stderr
    except:
        return "[!] failed"

def pause():
    Prompt.ask("\n[dim]enter to continue[/dim]")


def email_lookup():
    clr()
    console.print("[bold red]=== EMAIL INVESTIGATION ===[/bold red]\n")
    email = Prompt.ask("[cyan]target email[/cyan]")
    
    # basic checks
    parts = email.split("@")
    if len(parts) != 2:
        console.print("[red]invalid email format[/red]")
        pause()
        return
    
    user, domain = parts
    console.print(f"\n[yellow]user: {user}[/yellow]")
    console.print(f"[yellow]domain: {domain}[/yellow]")
    
    # MX records
    console.print(f"\n[yellow]--- MX Records for {domain} ---[/yellow]")
    console.print(runcmd(f"dig +short {domain} MX"))
    
    # common provider detection
    providers = {
        "gmail.com": ("Google Workspace / Gmail", "you can try ghunt or theHarvester"),
        "outlook.com": ("Microsoft 365", ""),
        "yahoo.com": ("Yahoo Mail", ""),
        "protonmail.com": ("ProtonMail", "end-to-end encrypted, hard to trace"),
        "proton.me": ("ProtonMail", "end-to-end encrypted"),
        "tutanota.com": ("Tutanota", "encrypted"),
        "aol.com": ("AOL Mail", ""),
        "zoho.com": ("Zoho Mail", ""),
        "icloud.com": ("Apple iCloud", ""),
        "yandex.com": ("Yandex Mail", ""),
        "mail.com": ("Mail.com", ""),
        "gmx.com": ("GMX Mail", ""),
    }
    
    if domain in providers:
        pname, tip = providers[domain]
        console.print(f"\n[green]provider: {pname}[/green]")
        if tip:
            console.print(f"[dim]{tip}[/dim]")
    
    # check if email has gravatar
    console.print("\n[yellow]--- Gravatar Check ---[/yellow]")
    import hashlib
    md5 = hashlib.md5(email.lower().encode()).hexdigest()
    avatar_url = f"https://www.gravatar.com/avatar/{md5}?d=404"
    try:
        import requests
        r = requests.get(avatar_url, timeout=5)
        if r.status_code == 200:
            console.print(f"  [green]gravatar found![/green] https://www.gravatar.com/avatar/{md5}")
        else:
            console.print("  [dim]no gravatar[/dim]")
    except:
        console.print("  [dim]could not check gravatar[/dim]")
    
    # haveibeenpwned check (API key needed for real, just show info)
    console.print("\n[yellow]--- Breach Check ---[/yellow]")
    console.print(f"  [dim]check manually: https://haveibeenpwned.com/account/{email}[/dim]")
    console.print(f"  [dim]or: https://dehashed.com (paid)[/dim]")
    
    # OSINT tool suggestions
    console.print("\n[yellow]--- Recommended Tools ---[/yellow]")
    console.print("  theHarvester: theharvester -d {domain} -b all".format(domain=domain))
    console.print("  holehe: holehe {email}".format(email=email))
    console.print("  ghunt: ghunt email {email}".format(email=email))
    console.print("  sherlock: sherlock {user}".format(user=user))
    
    pause()

def username_lookup():
    clr()
    console.print("[bold red]=== USERNAME ENUMERATION ===[/bold red]\n")
    username = Prompt.ask("[cyan]target username[/cyan]")
    
    # sites to check (basic http 200/404 check)
    sites = {
        "github": f"https://github.com/{username}",
        "gitlab": f"https://gitlab.com/{username}",
        "twitter/x": f"https://x.com/{username}",
        "instagram": f"https://www.instagram.com/{username}/",
        "reddit": f"https://www.reddit.com/user/{username}",
        "youtube": f"https://www.youtube.com/@{username}",
        "tiktok": f"https://www.tiktok.com/@{username}",
        "twitch": f"https://www.twitch.tv/{username}",
        "pinterest": f"https://www.pinterest.com/{username}/",
        "linkedin": f"https://www.linkedin.com/in/{username}/",
        "facebook": f"https://www.facebook.com/{username}",
        "medium": f"https://medium.com/@{username}",
        "keybase": f"https://keybase.io/{username}",
        "hackernews": f"https://news.ycombinator.com/user?id={username}",
        "npm": f"https://www.npmjs.com/~{username}",
        "dockerhub": f"https://hub.docker.com/u/{username}",
        "spotify": f"https://open.spotify.com/user/{username}",
        "deviantart": f"https://www.deviantart.com/{username}",
        "flickr": f"https://www.flickr.com/people/{username}/",
        "telegram": f"https://t.me/{username}",
    }
    
    console.print(f"\n[yellow]checking {len(sites)} platforms for @{username}...[/yellow]\n")
    
    try:
        import requests
        found = []
        not_found = []
        
        for name, url in sites.items():
            try:
                r = requests.get(url, timeout=5, allow_redirects=False, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"})
                if r.status_code == 200:
                    console.print(f"  [green]{name:15s} {url}[/green]")
                    found.append(name)
                elif r.status_code == 404:
                    console.print(f"  [dim]{name:15s} not found[/dim]")
                    not_found.append(name)
                else:
                    console.print(f"  [yellow]{name:15s} {r.status_code} (ambiguous)[/yellow]")
            except:
                console.print(f"  [dim]{name:15s} timeout[/dim]")
        
        console.print(f"\n[green]found on {len(found)} platforms[/green]")
    except:
        console.print("[red]requests not installed[/red]")
    
    # suggest sherlock
    if os.path.exists("/usr/bin/sherlock"):
        console.print("\n[yellow]running sherlock...[/yellow]")
        console.print(runcmd(f"sherlock {username} --timeout 5 2>/dev/null", t=120))
    else:
        console.print("\n[dim]for deeper search, install sherlock: pip3 install sherlock[/dim]")
    
    pause()

def domain_recon():
    clr()
    console.print("[bold red]=== DOMAIN RECONNAISSANCE ===[/bold red]\n")
    domain = Prompt.ask("[cyan]target domain[/cyan]")
    
    # DNS
    console.print("\n[yellow]--- DNS Records ---[/yellow]")
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
        out = runcmd(f"dig +short {domain} {rtype} 2>/dev/null")
        if out.strip():
            console.print(f"  {rtype}: {out.strip()}")
    
    # web info
    console.print(f"\n[yellow]--- Web Info ---[/yellow]")
    try:
        import requests
        r = requests.get(f"https://{domain}", timeout=10, allow_redirects=True)
        console.print(f"  status: {r.status_code}")
        console.print(f"  final url: {r.url}")
        console.print(f"  server: {r.headers.get('server', 'unknown')}")
        console.print(f"  powered by: {r.headers.get('x-powered-by', 'unknown')}")
        
        # check for common paths
        paths = ["/admin", "/login", "/wp-admin", "/api", "/robots.txt", 
                 "/.env", "/.git", "/sitemap.xml", "/favicon.ico"]
        console.print("\n[yellow]--- Common Paths ---[/yellow]")
        for p in paths:
            try:
                pr = requests.get(f"https://{domain}{p}", timeout=3, allow_redirects=False)
                status = pr.status_code
                if status == 200:
                    console.print(f"  [green]{p:20s} {status}[/green]")
                elif status in [301, 302]:
                    console.print(f"  [yellow]{p:20s} {status} redirect[/yellow]")
                else:
                    console.print(f"  [dim]{p:20s} {status}[/dim]")
            except:
                pass
    except Exception as e:
        console.print(f"  [red]web check failed: {e}[/red]")
    
    # whois summary
    console.print(f"\n[yellow]--- WHOIS Summary ---[/yellow]")
    out = runcmd(f"whois {domain} 2>/dev/null | head -30", t=10)
    if out.strip():
        for line in out.strip().split('\n')[:15]:
            console.print(f"  {line}")
    
    # SSL cert info
    console.print(f"\n[yellow]--- SSL Certificate ---[/yellow]")
    out = runcmd(f"echo | openssl s_client -connect {domain}:443 -servername {domain} 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null")
    if out.strip():
        for line in out.strip().split('\n'):
            console.print(f"  {line}")
    
    pause()

def phone_lookup():
    clr()
    console.print("[bold red]=== PHONE NUMBER OSINT ===[/bold red]\n")
    phone = Prompt.ask("[cyan]phone number (with country code, e.g. +14155552671)[/cyan]")
    
    # basic validation
    clean = re.sub(r'[^\d+]', '', phone)
    console.print(f"\n[yellow]cleaned: {clean}[/yellow]")
    
    # try to identify country from code
    codes = {
        "+1": "USA/Canada",
        "+44": "UK",
        "+49": "Germany",
        "+33": "France",
        "+39": "Italy",
        "+34": "Spain",
        "+61": "Australia",
        "+81": "Japan",
        "+86": "China",
        "+91": "India",
        "+55": "Brazil",
        "+7": "Russia",
        "+82": "South Korea",
        "+31": "Netherlands",
        "+46": "Sweden",
        "+47": "Norway",
        "+48": "Poland",
        "+41": "Switzerland",
        "+43": "Austria",
        "+32": "Belgium",
    }
    
    for code, country in codes.items():
        if clean.startswith(code):
            console.print(f"  [green]country: {country} ({code})[/green]")
            break
    
    console.print("\n[yellow]--- Manual OSINT Resources ---[/yellow]")
    console.print("  - numverify.com (number validation)")
    console.print("  - truecaller.com (caller ID lookup)")
    console.print("  - sync.me (sync contacts)")
    console.print("  - whitepages.com (US numbers)")
    console.print("  - spydialer.com (voicemail check)")
    console.print("  - callingweb.com (verify carrier)")
    
    # google dork
    console.print(f"\n[yellow]--- Google Dorks ---[/yellow]")
    console.print(f'  site:truecaller.com "{clean}"')
    console.print(f'  site:whitepages.com "{clean}"')
    console.print(f'  "{clean}" site:linkedin.com')
    console.print(f'  "{clean}" filetype:pdf')
    
    pause()

def breach_check():
    clr()
    console.print("[bold red]=== BREACH / LEAK CHECK ===[/bold red]\n")
    console.print("  [1] email breach check")
    console.print("  [2] domain breach stats")
    console.print("  [3] paste check")
    choice = Prompt.ask("[cyan]choice[/cyan]")
    
    if choice == "1":
        email = Prompt.ask("[cyan]email[/cyan]")
        console.print(f"\n[yellow]manual check URLs:[/yellow]")
        console.print(f"  https://haveibeenpwned.com/account/{email}")
        console.print(f"  https://dehashed.com/search?query={email}")
        console.print(f"  https://leaked.site/")
        console.print(f"  https://intelx.io/")
    elif choice == "2":
        domain = Prompt.ask("[cyan]domain[/cyan]")
        console.print(f"\n[yellow]check:[/yellow]")
        console.print(f"  https://haveibeenpwned.com/DomainSearch?domainName={domain}")
        console.print(f"  https://dehashed.com/search?query={domain}")
    elif choice == "3":
        console.print(f"\n[yellow]paste search:[/yellow]")
        console.print(f"  https://pastebin.com/search")
        console.print(f"  https://intelx.io/")
    
    console.print("\n[dim]note: most breach databases require API keys for automated access[/dim]")
    pause()

def git_recon():
    clr()
    console.print("[bold red]=== GIT RECONNAISSANCE ===[/bold red]\n")
    target = Prompt.ask("[cyan]github username or repo (e.g. user/repo)[/cyan]")
    
    # check if its user or repo
    if "/" in target:
        # repo recon
        console.print(f"\n[yellow]--- repo info: {target} ---[/yellow]")
        
        # check for sensitive files
        sensitive = [
            ".env", ".env.local", ".env.production",
            "config.json", "config.yml", "config.yaml",
            "credentials.json", "secrets.json",
            "id_rsa", "id_ed25519", ".htpasswd",
            "database.yml", "database.json",
            "wp-config.php", ".htaccess",
            "docker-compose.yml",
        ]
        
        console.print("[yellow]checking for exposed sensitive files...[/yellow]")
        try:
            import requests
            for f in sensitive:
                url = f"https://raw.githubusercontent.com/{target}/master/{f}"
                try:
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        console.print(f"  [red]EXPOSED: {f}[/red]")
                        console.print(f"    {r.text[:200]}...")
                except:
                    pass
                # also check main branch
                url2 = f"https://raw.githubusercontent.com/{target}/main/{f}"
                try:
                    r2 = requests.get(url2, timeout=5)
                    if r2.status_code == 200:
                        console.print(f"  [red]EXPOSED: {f} (main branch)[/red]")
                except:
                    pass
        except:
            console.print("[red]requests not available[/red]")
    else:
        # user recon
        console.print(f"\n[yellow]--- user: {target} ---[/yellow]")
        try:
            import requests
            r = requests.get(f"https://api.github.com/users/{target}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                for k in ["name", "bio", "blog", "location", "email", 
                          "public_repos", "followers", "following", "created_at"]:
                    if k in data and data[k]:
                        console.print(f"  {k}: {data[k]}")
            
            # list repos
            r2 = requests.get(f"https://api.github.com/users/{target}/repos?sort=updated&per_page=10", timeout=10)
            if r2.status_code == 200:
                repos = r2.json()
                console.print(f"\n[yellow]recent repos:[/yellow]")
                for repo in repos[:10]:
                    console.print(f"  {repo['name']:30s} stars:{repo.get('stargazers_count',0)} forks:{repo.get('forks_count',0)}")
        except Exception as e:
            console.print(f"[red]error: {e}[/red]")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== DEEP RECON ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Email Investigation",
            "Username Enumeration",
            "Domain Recon",
            "Phone Number OSINT",
            "Breach / Leak Check",
            "GitHub Recon",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]DEEP RECON[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: email_lookup()
        elif c == 2: username_lookup()
        elif c == 3: domain_recon()
        elif c == 4: phone_lookup()
        elif c == 5: breach_check()
        elif c == 6: git_recon()
        elif c == 0: return
