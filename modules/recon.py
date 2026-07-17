# recon stuff - IP lookups, DNS, whois, port scanning etc
import os, socket, subprocess, json, re
from pathlib import Path
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

def ip_lookup():
    clr()
    console.print("[bold red]=== IP LOOKUP ===[/bold red]\n")
    ip = Prompt.ask("[cyan]target IP (leave empty for your own)[/cyan]", default="")
    if not ip:
        ip = ""
    
    console.print("\n[yellow]--- Basic Info ---[/yellow]")
    if ip:
        out = runcmd(f"dig +short {ip}")
        console.print(f"DNS: {out.strip() if out.strip() else 'no reverse dns'}")
    
    # use ip-api.com
    try:
        import requests
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("status") == "success":
            t = Table(box=box.SIMPLE)
            t.add_column("Field", style="bold")
            t.add_column("Value")
            for k in ["query", "country", "regionName", "city", "zip", "lat", "lon", 
                       "timezone", "isp", "org", "as", "mobile", "proxy", "hosting"]:
                if k in data:
                    t.add_row(k, str(data[k]))
            console.print(t)
        else:
            console.print("[red]lookup failed[/red]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    # also try ipinfo.io
    if ip:
        console.print("\n[yellow]--- Extra from ipinfo ---[/yellow]")
        out = runcmd(f"curl -s https://ipinfo.io/{ip}/json 2>/dev/null")
        try:
            info = json.loads(out)
            for k, v in info.items():
                console.print(f"  {k}: {v}")
        except:
            console.print("[dim]ipinfo failed or no data[/dim]")
    
    pause()

def dns_lookup():
    clr()
    console.print("[bold red]=== DNS LOOKUP ===[/bold red]\n")
    host = Prompt.ask("[cyan]domain[/cyan]")
    
    console.print("\n[yellow]--- A Records ---[/yellow]")
    console.print(runcmd(f"dig +short {host} A"))
    
    console.print("[yellow]--- AAAA Records ---[/yellow]")
    console.print(runcmd(f"dig +short {host} AAAA"))
    
    console.print("[yellow]--- MX Records ---[/yellow]")
    console.print(runcmd(f"dig +short {host} MX"))
    
    console.print("[yellow]--- NS Records ---[/yellow]")
    console.print(runcmd(f"dig +short {host} NS"))
    
    console.print("[yellow]--- TXT Records ---[/yellow]")
    console.print(runcmd(f"dig +short {host} TXT"))
    
    console.print("[yellow]--- SOA ---[/yellow]")
    console.print(runcmd(f"dig +short {host} SOA"))
    
    console.print("[yellow]--- CNAME ---[/yellow]")
    console.print(runcmd(f"dig +short {host} CNAME"))
    
    pause()

def whois_lookup():
    clr()
    console.print("[bold red]=== WHOIS ===[/bold red]\n")
    target = Prompt.ask("[cyan]domain or IP[/cyan]")
    
    if not os.path.exists("/usr/bin/whois") and not os.path.exists("/usr/bin/whois"):
        console.print("[red]whois not installed, install with: pacman -S whois[/red]")
        pause()
        return
    
    out = runcmd(f"whois {target}", t=15)
    # just show first 60 lines so it dont flood
    lines = out.strip().split('\n')
    for line in lines[:60]:
        console.print(f"  {line}")
    if len(lines) > 60:
        console.print(f"\n  [dim]... {len(lines) - 60} more lines (full output saved)[/dim]")
        Path("/tmp/.0panel_whois.txt").write_text(out)
        console.print("  [dim]saved to /tmp/.0panel_whois.txt[/dim]")
    
    pause()

def port_scan():
    clr()
    console.print("[bold red]=== PORT SCANNER ===[/bold red]\n")
    host = Prompt.ask("[cyan]target host/IP[/cyan]")
    console.print("[dim]quick = common ports only, full = 1-1024, all = 1-65535[/dim]")
    mode = Prompt.ask("[cyan]scan mode[/cyan]", choices=["quick", "full", "all"], default="quick")
    
    if mode == "quick":
        ports = "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080,8443"
    elif mode == "full":
        ports = "1-1024"
    else:
        ports = "1-65535"
    
    console.print(f"\n[yellow]scanning {host} ({mode})...[/yellow]\n")
    
    # try nmap first
    if os.path.exists("/usr/bin/nmap"):
        out = runcmd(f"nmap -sV -p {ports} --open {host} -T4 2>/dev/null", t=120)
        console.print(out)
    else:
        # fallback to python socket scan (only for quick mode)
        console.print("[dim]nmap not found, using basic socket scan (slow)[/dim]\n")
        open_ports = []
        port_list = [int(x) for x in ports.split(',')] if '-' not in ports else list(range(int(ports.split('-')[0]), int(ports.split('-')[1])+1))
        
        for p in port_list[:1000]:  # limit to 1000 ports for sanity
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((host, p)) == 0:
                    console.print(f"  [green]port {p} OPEN[/green]")
                    open_ports.append(p)
                s.close()
            except:
                pass
        
        if not open_ports:
            console.print("[red]no open ports found (or host is down)[/red]")
    
    pause()

def subdomain_enum():
    clr()
    console.print("[bold red]=== SUBDOMAIN ENUMERATION ===[/bold red]\n")
    domain = Prompt.ask("[cyan]target domain[/cyan]")
    
    console.print("[yellow]trying crt.sh certificate transparency...[/yellow]")
    try:
        import requests
        r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
        data = r.json()
        subs = set()
        for entry in data:
            name = entry.get("name_value", "")
            for s in name.split('\n'):
                if s.endswith(f".{domain}") or s == domain:
                    subs.add(s.strip())
        
        if subs:
            t = Table(box=box.SIMPLE)
            t.add_column("#", style="bold")
            t.add_column("Subdomain")
            for i, s in enumerate(sorted(subs), 1):
                t.add_row(str(i), s)
            console.print(t)
            console.print(f"\n[green]found {len(subs)} subdomains[/green]")
        else:
            console.print("[red]no subdomains found on crt.sh[/red]")
    except Exception as e:
        console.print(f"[red]crt.sh failed: {e}[/red]")
    
    # also try subfinder if installed
    if os.path.exists("/usr/bin/subfinder"):
        console.print("\n[yellow]running subfinder...[/yellow]")
        out = runcmd(f"subfinder -d {domain} -silent 2>/dev/null", t=60)
        if out.strip():
            console.print(out)
    
    pause()

def email_dns():
    clr()
    console.print("[bold red]=== EMAIL -> DOMAIN CHECK ===[/bold red]\n")
    email = Prompt.ask("[cyan]email address[/cyan]")
    domain = email.split('@')[-1]
    
    console.print(f"\n[yellow]checking MX records for {domain}...[/yellow]")
    console.print(runcmd(f"dig +short {domain} MX"))
    
    console.print(f"\n[yellow]checking if domain exists...[/yellow]")
    console.print(runcmd(f"dig +short {domain} A"))
    
    # check common email providers
    providers = {
        "gmail.com": "Google Mail",
        "outlook.com": "Microsoft Outlook",
        "yahoo.com": "Yahoo Mail",
        "protonmail.com": "ProtonMail (encrypted)",
        "proton.me": "ProtonMail (encrypted)",
        "tutanota.com": "Tutanota (encrypted)",
        "icloud.com": "Apple iCloud",
        "aol.com": "AOL Mail",
    }
    if domain in providers:
        console.print(f"\n[green]provider: {providers[domain]}[/green]")
    else:
        console.print(f"\n[dim]unknown provider for {domain} (might be self-hosted)[/dim]")
    
    pause()

def banner_grab():
    clr()
    console.print("[bold red]=== BANNER GRAB ===[/bold red]\n")
    host = Prompt.ask("[cyan]target host[/cyan]")
    port = Prompt.ask("[cyan]port[/cyan]", default="80")
    
    console.print(f"\n[yellow]grabbing banner from {host}:{port}...[/yellow]\n")
    
    # python socket banner grab
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, int(port)))
        
        # send HTTP request if its port 80/443
        if port in ["80", "443", "8080", "8443"]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
        
        banner = s.recv(4096)
        console.print(f"[green]{banner.decode(errors='replace')}[/green]")
        s.close()
    except Exception as e:
        console.print(f"[red]failed: {e}[/red]")
    
    # also try nmap
    if os.path.exists("/usr/bin/nmap"):
        console.print("\n[yellow]nmap banner grab:[/yellow]")
        console.print(runcmd(f"nmap -sV --top-ports 1 -sC {host} 2>/dev/null"))
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== OSINT RECON ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "IP Lookup (geo/ISP/org)",
            "DNS Lookup (A/AAAA/MX/NS/TXT)",
            "WHOIS Lookup",
            "Port Scanner",
            "Subdomain Enumeration",
            "Email -> DNS Check",
            "Banner Grabbing",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back to main")
        console.print(Panel(t, title="[bold]RECON TOOLS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: ip_lookup()
        elif c == 2: dns_lookup()
        elif c == 3: whois_lookup()
        elif c == 4: port_scan()
        elif c == 5: subdomain_enum()
        elif c == 6: email_dns()
        elif c == 7: banner_grab()
        elif c == 8 or c == 0: return
