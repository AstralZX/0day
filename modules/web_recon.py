# web recon - headers, tech stack, robots, directory busting etc
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

def header_check():
    clr()
    console.print("[bold red]=== HTTP HEADER CHECK ===[/bold red]\n")
    url = Prompt.ask("[cyan]URL[/cyan]")
    if not url.startswith("http"):
        url = "https://" + url
    
    try:
        import requests
        r = requests.get(url, timeout=10, allow_redirects=True)
        
        console.print(f"\n[yellow]Status: {r.status_code}[/yellow]")
        console.print(f"[yellow]Final URL: {r.url}[/yellow]\n")
        
        t = Table(box=box.SIMPLE, title="Response Headers")
        t.add_column("Header", style="bold cyan")
        t.add_column("Value")
        
        security_headers = {
            "strict-transport-security": "[green]HSTS[/green]",
            "x-frame-options": "[green]X-Frame[/green]",
            "x-content-type-options": "[green]XCTO[/green]",
            "x-xss-protection": "[green]XSS[/green]",
            "content-security-policy": "[green]CSP[/green]",
            "permissions-policy": "[green]Permissions[/green]",
            "referrer-policy": "[green]Referrer[/green]",
        }
        
        found_sec = []
        for k, v in r.headers.items():
            style = ""
            if k.lower() in security_headers:
                found_sec.append(k)
                style = " [green]![/green]"
            t.add_row(f"{k}{style}", v)
        
        console.print(t)
        
        # security analysis
        console.print("\n[bold yellow]--- Security Analysis ---[/bold yellow]")
        missing = []
        for h in security_headers:
            if h not in [k.lower() for k in r.headers.keys()]:
                missing.append(h)
        
        if missing:
            console.print(f"[red]missing security headers:[/red]")
            for m in missing:
                console.print(f"  [red]- {m}[/red]")
        else:
            console.print("[green]all common security headers present![/green]")
        
        # check server header leak
        server = r.headers.get("server", "")
        powered = r.headers.get("x-powered-by", "")
        if server:
            console.print(f"\n[yellow]server header leaks: {server}[/yellow]")
        if powered:
            console.print(f"[yellow]x-powered-by leaks: {powered}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def tech_stack():
    clr()
    console.print("[bold red]=== TECHNOLOGY DETECTION ===[/bold red]\n")
    url = Prompt.ask("[cyan]target URL[/cyan]")
    if not url.startswith("http"):
        url = "https://" + url
    
    # try whatweb first
    if os.path.exists("/usr/bin/whatweb"):
        console.print("[yellow]using whatweb...[/yellow]\n")
        out = runcmd(f"whatweb -a 3 {url} 2>/dev/null", t=20)
        console.print(out)
    else:
        console.print("[dim]whatweb not found, using header analysis[/dim]\n")
    
    # analyze headers for tech hints
    try:
        import requests
        r = requests.get(url, timeout=10, allow_redirects=True)
        
        techs = []
        headers = {k.lower(): v for k, v in r.headers.items()}
        
        # server header
        if "server" in headers:
            techs.append(f"Server: {headers['server']}")
        if "x-powered-by" in headers:
            techs.append(f"Powered by: {headers['x-powered-by']}")
        if "x-generator" in headers:
            techs.append(f"Generator: {headers['x-generator']}")
        
        # check html for clues
        html = r.text[:50000]  # first 50kb
        patterns = {
            r'wp-content': 'WordPress',
            r'wp-includes': 'WordPress',
            r'/static/': 'Static files',
            r'__next': 'Next.js',
            r'_nuxt': 'Nuxt.js',
            r'react': 'React',
            r'angular': 'Angular',
            r'vue\.js|vue\.min\.js': 'Vue.js',
            r'jquery': 'jQuery',
            r'bootstrap': 'Bootstrap',
            r'laravel': 'Laravel',
            r'django': 'Django',
            r'flask': 'Flask',
            r'rails': 'Ruby on Rails',
            r'nginx': 'Nginx',
            r'apache': 'Apache',
            r'cloudflare': 'Cloudflare',
            r'cdn\.': 'CDN detected',
            r'google-analytics': 'Google Analytics',
            r'gtag': 'Google Tag Manager',
            r'facebook': 'Facebook SDK/Pixel',
            r'recaptcha': 'reCAPTCHA',
            r'hcaptcha': 'hCaptcha',
        }
        
        found_techs = []
        for pattern, name in patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                if name not in found_techs:
                    found_techs.append(name)
        
        if techs or found_techs:
            console.print("[bold yellow]detected technologies:[/bold yellow]")
            for t in techs:
                console.print(f"  [cyan]{t}[/cyan]")
            for t in found_techs:
                console.print(f"  [cyan]{t}[/cyan]")
        else:
            console.print("[dim]couldnt detect specific tech stack[/dim]")
        
        # cookies
        if r.cookies:
            console.print("\n[bold yellow]cookies:[/bold yellow]")
            for name, val in r.cookies.items():
                secure = "secure" if r.cookies[name]._rest.get("Secure") else "no-secure"
                console.print(f"  {name} = {val[:30]}... ({secure})")
                
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def robots_check():
    clr()
    console.print("[bold red]=== ROBOTS.TXT / SITEMAP CHECK ===[/bold red]\n")
    domain = Prompt.ask("[cyan]domain[/cyan]")
    if not domain.startswith("http"):
        domain = "https://" + domain
    
    urls_to_check = [
        "/robots.txt",
        "/sitemap.xml",
        "/.well-known/security.txt",
        "/.env",
        "/.git/HEAD",
        "/.svn/entries",
        "/wp-admin/",
        "/administrator/",
        "/server-status",
        "/server-info",
        "/.htaccess",
        "/crossdomain.xml",
        "/clientaccesspolicy.xml",
        "/favicon.ico",
    ]
    
    try:
        import requests
        for path in urls_to_check:
            url = domain.rstrip("/") + path
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                status = r.status_code
                size = len(r.content)
                
                if status == 200:
                    console.print(f"  [green]{path:30s} {status} ({size} bytes)[/green]")
                    if path == "/robots.txt":
                        # show interesting lines
                        lines = r.text.split('\n')
                        interesting = [l for l in lines if 'disallow' in l.lower() or 'allow' in l.lower()]
                        if interesting:
                            for line in interesting[:10]:
                                console.print(f"    [dim]{line.strip()}[/dim]")
                    elif path == "/.env":
                        console.print(f"    [red]!!! .env file is exposed !!![/red]")
                    elif path == "/.git/HEAD":
                        console.print(f"    [red]!!! git repo exposed !!![/red]")
                elif status in [301, 302]:
                    loc = r.headers.get("Location", "?")
                    console.print(f"  [yellow]{path:30s} {status} -> {loc}[/yellow]")
                else:
                    console.print(f"  [dim]{path:30s} {status}[/dim]")
            except:
                console.print(f"  [dim]{path:30s} timeout/error[/dim]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def dir_bust():
    clr()
    console.print("[bold red]=== DIRECTORY BRUTE FORCE ===[/bold red]\n")
    url = Prompt.ask("[cyan]target URL[/cyan]")
    if not url.startswith("http"):
        url = "https://" + url
    
    # check for common wordlists
    wordlists = [
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt",
        "/usr/share/seclists/Discovery/Web-Content/common.txt",
    ]
    wl = None
    for w in wordlists:
        if os.path.exists(w):
            wl = w
            break
    
    if not wl:
        console.print("[red]no wordlist found. install dirb or seclists[/red]")
        console.print("[dim]arch: pacman -S dirb[/dim]")
        pause()
        return
    
    console.print(f"[yellow]using wordlist: {wl}[/yellow]")
    console.print("[yellow]starting dirb...[/yellow]\n")
    
    if os.path.exists("/usr/bin/dirb"):
        out = runcmd(f"dirb {url} {wl} -r -S -w 2>/dev/null", t=120)
        console.print(out)
    else:
        # manual curl approach
        console.print("[dim]dirb not found, doing manual check...[/dim]\n")
        try:
            import requests
            with open(wl) as f:
                words = [w.strip() for w in f.readlines() if w.strip()]
            
            found = 0
            for word in words[:500]:  # limit
                test_url = url.rstrip("/") + "/" + word
                try:
                    r = requests.get(test_url, timeout=5, allow_redirects=False)
                    if r.status_code not in [404, 403, 405]:
                        console.print(f"  [green]{r.status_code} {test_url}[/green]")
                        found += 1
                except:
                    pass
            
            console.print(f"\n[green]found {found} paths[/green]")
        except Exception as e:
            console.print(f"[red]{e}[/red]")
    
    pause()

def ssl_check():
    clr()
    console.print("[bold red]=== SSL/TLS CHECK ===[/bold red]\n")
    host = Prompt.ask("[cyan]domain[/cyan]")
    
    if os.path.exists("/usr/bin/nmap"):
        out = runcmd(f"nmap --script ssl-enum-ciphers -p 443 {host} 2>/dev/null", t=30)
        console.print(out)
    else:
        # python ssl check
        import ssl, socket
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.settimeout(10)
                s.connect((host, 443))
                cert = s.getpeercert()
                
                console.print(f"\n[green]SSL/TLS connected successfully[/green]")
                console.print(f"  subject: {dict(x[0] for x in cert.get('subject', []))}")
                console.print(f"  issuer:  {dict(x[0] for x in cert.get('issuer', []))}")
                console.print(f"  version: {cert.get('version')}")
                console.print(f"  serial:  {cert.get('serialNumber')}")
                console.print(f"  valid:   {cert.get('notBefore')} -> {cert.get('notAfter')}")
                
                sans = cert.get('subjectAltName', [])
                if sans:
                    console.print(f"  SANs:")
                    for t, v in sans[:20]:
                        console.print(f"    {t}: {v}")
        except Exception as e:
            console.print(f"[red]ssl check failed: {e}[/red]")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== WEB RECON ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "HTTP Header Analysis",
            "Technology Detection",
            "Robots.txt / Sensitive Files",
            "Directory Brute Force",
            "SSL/TLS Certificate Check",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]WEB RECON[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: header_check()
        elif c == 2: tech_stack()
        elif c == 3: robots_check()
        elif c == 4: dir_bust()
        elif c == 5: ssl_check()
        elif c == 8 or c == 0: return
