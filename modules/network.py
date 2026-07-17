# network tools - ping, traceroute, scan, interfaces etc
import os, subprocess, socket, struct
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

def ping_host():
    clr()
    console.print("[bold red]=== PING ===[/bold red]\n")
    host = Prompt.ask("[cyan]target[/cyan]")
    count = Prompt.ask("[cyan]count[/cyan]", default="4")
    console.print(runcmd(f"ping -c {count} {host}", t=count*3+5))
    pause()

def traceroute_host():
    clr()
    console.print("[bold red]=== TRACEROUTE ===[/bold red]\n")
    host = Prompt.ask("[cyan]target[/cyan]")
    
    if os.path.exists("/usr/bin/traceroute"):
        console.print(runcmd(f"traceroute -n {host}", t=60))
    else:
        # manual traceroute
        console.print("[dim]traceroute not found, doing manual...[/dim]\n")
        ttl = 1
        max_hops = 30
        while ttl <= max_hops:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                s.settimeout(2)
                # send icmp with this ttl
                packet = struct.pack("!BBHHHBB", 8, 0, 0, 1, ttl) + b"\x00" * 32
                s.sendto(packet, (host, 0))
                addr = None
                try:
                    data, addr = s.recvfrom(1024)
                    addr = addr[0]
                except:
                    pass
                
                if addr:
                    try:
                        hostname = socket.gethostbyaddr(addr)[0]
                        console.print(f"  {ttl:3d}  {addr:15s}  {hostname}")
                    except:
                        console.print(f"  {ttl:3d}  {addr}")
                else:
                    console.print(f"  {ttl:3d}  *")
                
                s.close()
                ttl += 1
            except:
                break
    
    pause()

def local_info():
    clr()
    console.print("[bold red]=== LOCAL NETWORK INFO ===[/bold red]\n")
    
    console.print("[yellow]--- Interfaces ---[/yellow]")
    console.print(runcmd("ip -br addr show 2>/dev/null || ifconfig 2>/dev/null"))
    
    console.print("[yellow]--- Routing ---[/yellow]")
    console.print(runcmd("ip route show 2>/dev/null || route -n 2>/dev/null"))
    
    console.print("[yellow]--- DNS Config ---[/yellow]")
    console.print(runcmd("cat /etc/resolv.conf 2>/dev/null"))
    
    console.print("[yellow]--- Active Connections (top 20) ---[/yellow]")
    console.print(runcmd("ss -tunap 2>/dev/null | head -21 || netstat -tunap 2>/dev/null | head -21"))
    
    pause()

def arp_scan():
    clr()
    console.print("[bold red]=== ARP SCAN ===[/bold red]\n")
    interface = Prompt.ask("[cyan]interface (or leave empty)[/cyan]", default="")
    
    if os.path.exists("/usr/bin/arp-scan"):
        iface = f"-I {interface}" if interface else ""
        console.print(runcmd(f"arp-scan {iface} --localnet 2>/dev/null", t=30))
    else:
        console.print("[yellow]arp-scan not found, trying ip neigh...[/yellow]\n")
        console.print(runcmd("ip neigh show 2>/dev/null"))
    
    pause()

def whois_ripe():
    clr()
    console.print("[bold red]=== RIPE / WHOIS QUERY ===[/bold red]\n")
    target = Prompt.ask("[cyan]IP or ASN[/cyan]")
    
    # RIPE stat API
    try:
        import requests
        # basic info
        r = requests.get(f"https://stat.ripe.net/data/whois/data/resource/{target}/info.json", timeout=10)
        if r.status_code == 200:
            data = r.json()
            console.print(f"\n[green]query result:[/green]")
            records = data.get("data", {}).get("records", [])
            for rec in records:
                for k, v in rec.items():
                    console.print(f"  {k}: {v}")
        else:
            console.print("[red]RIPE query failed, falling back to whois[/red]")
            console.print(runcmd(f"whois {target}", t=15))
    except:
        console.print(runcmd(f"whois {target}", t=15))
    
    pause()

def host_discovery():
    clr()
    console.print("[bold red]=== HOST DISCOVERY (PING SWEEP) ===[/bold red]\n")
    subnet = Prompt.ask("[cyan]subnet (e.g. 192.168.1.0/24)[/cyan]")
    
    if os.path.exists("/usr/bin/nmap"):
        console.print("[yellow]using nmap...[/yellow]\n")
        console.print(runcmd(f"nmap -sn {subnet} 2>/dev/null", t=120))
    else:
        console.print("[dim]nmap not found, doing manual arp ping...[/dim]\n")
        # parse subnet and ping each
        base = subnet.rsplit('.', 1)[0] + "."
        for i in range(1, 255):
            ip = base + str(i)
            ret = os.system(f"ping -c 1 -W 1 {ip} >/dev/null 2>&1")
            if ret == 0:
                console.print(f"  [green]{ip} is up[/green]")
    
    pause()

def whois_asn():
    clr()
    console.print("[bold red]=== ASN LOOKUP ===[/bold red]\n")
    target = Prompt.ask("[cyan]IP or domain[/cyan]")
    
    try:
        import requests
        # get ASN from IP
        r = requests.get(f"https://stat.ripe.net/data/asns/data.json?resource={target}", timeout=10)
        data = r.json()
        
        if "data" in data and "asns" in data["data"]:
            for asn_info in data["data"]["asns"]:
                asn = asn_info.get("asn", "?")
                name = asn_info.get("name", "?")
                console.print(f"\n[green]ASN: AS{asn}[/green]")
                console.print(f"  name: {name}")
                
                # get more details
                r2 = requests.get(f"https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn}", timeout=10)
                d2 = r2.json().get("data", {})
                if d2:
                    console.print(f"  announced: {d2.get('announced_prefixes', '?')} prefixes")
                    console.print(f"  country: {d2.get('holder_country', '?')}")
                    console.print(f"  registrar: {d2.get('registrable', {}).get('name', '?')}")
        else:
            console.print("[red]could not find ASN info[/red]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== NETWORK TOOLS ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Ping",
            "Traceroute",
            "Local Network Info",
            "ARP Scan",
            "RIPE / IP Whois",
            "Host Discovery (Ping Sweep)",
            "ASN Lookup",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]NETWORK TOOLS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: ping_host()
        elif c == 2: traceroute_host()
        elif c == 3: local_info()
        elif c == 4: arp_scan()
        elif c == 5: whois_ripe()
        elif c == 6: host_discovery()
        elif c == 7: whois_asn()
        elif c == 0: return
