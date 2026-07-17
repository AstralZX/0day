# opsec stuff - mac changing, vpn detection, dns leak test, etc
import os, subprocess, socket, random
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

def gen_mac():
    # generate random mac that looks legit
    # first byte needs bit 1 set (locally administered) and bit 0 cleared (unicast)
    first = random.randint(0x00, 0xFF) & 0xFE | 0x02
    mac = ':'.join(f'{random.randint(0,255):02x}' for _ in range(5))
    return f'{first:02x}:{mac}'

def mac_changer():
    clr()
    console.print("[bold red]=== MAC ADDRESS CHANGER ===[/bold red]\n")
    
    # show current
    console.print("[yellow]current MAC addresses:[/yellow]")
    console.print(runcmd("ip link show 2>/dev/null | grep -A1 'link/ether'"))
    print()
    
    console.print("[dim]1 = set random, 2 = set custom, 3 = restore original[/dim]")
    choice = Prompt.ask("[cyan]choice[/cyan]", choices=["1", "2", "3"])
    
    iface = Prompt.ask("[cyan]interface name (e.g. eth0, wlan0)[/cyan]")
    
    if choice == "1":
        new_mac = gen_mac()
        console.print(f"\n[yellow]random MAC: {new_mac}[/yellow]")
    elif choice == "2":
        new_mac = Prompt.ask("[cyan]new MAC address (xx:xx:xx:xx:xx:xx)[/cyan]")
    else:
        # try to restore - usually the original is stored somewhere
        console.print("[yellow]attempting to restore original MAC...[/yellow]")
        console.print("[dim]you might need to set it manually if this fails[/dim]")
        new_mac = None
    
    if new_mac:
        # bring interface down, change mac, bring up
        console.print(f"\n[yellow]changing MAC on {iface}...[/yellow]")
        runcmd(f"ip link set {iface} down")
        out = runcmd(f"macchanger -m {new_mac} {iface} 2>/dev/null || ip link set {iface} address {new_mac}")
        runcmd(f"ip link set {iface} up")
        console.print(out)
        
        console.print("\n[yellow]new MAC:[/yellow]")
        console.print(runcmd(f"ip link show {iface} | grep 'link/ether'"))
    
    pause()

def vpn_check():
    clr()
    console.print("[bold red]=== VPN / PROXY DETECTION CHECK ===[/bold red]\n")
    console.print("[dim]checks if your traffic looks like its coming from a VPN/proxy[/dim]\n")
    
    try:
        import requests
        
        # check 1: ipleak
        console.print("[yellow]checking ipleak.net...[/yellow]")
        r = requests.get("https://ipleak.net/json/", timeout=10)
        data = r.json()
        console.print(f"  IP: {data.get('ip', '?')}")
        console.print(f"  ISP: {data.get('isp', '?')}")
        console.print(f"  hostname: {data.get('hostname', '?')}")
        
        # check 2: detectvpn
        console.print("\n[yellow]checking vpn detection...[/yellow]")
        r2 = requests.get("https://api.ipify.org?format=json", timeout=10)
        my_ip = r2.json().get("ip")
        
        r3 = requests.get(f"http://ip-api.com/json/{my_ip}?fields=proxy,hosting,mobile", timeout=10)
        d3 = r3.json()
        
        if d3.get("proxy"):
            console.print("  [red]DETECTED: proxy/VPN traffic[/red]")
        else:
            console.print("  [green]looks like residential IP (no VPN detected)[/green]")
        
        if d3.get("hosting"):
            console.print("  [yellow]note: IP is from hosting/datacenter range[/yellow]")
        if d3.get("mobile"):
            console.print("  [yellow]note: IP is from mobile network[/yellow]")
            
    except Exception as e:
        console.print(f"[red]check failed: {e}[/red]")
    
    pause()

def dns_leak_test():
    clr()
    console.print("[bold red]=== DNS LEAK TEST ===[/bold red]\n")
    console.print("[dim]checking which DNS servers your system uses...[/dim]\n")
    
    # show current dns
    console.print("[yellow]configured DNS servers:[/yellow]")
    console.print(runcmd("cat /etc/resolv.conf 2>/dev/null | grep nameserver"))
    
    # query multiple dns providers to see which respond
    dns_servers = {
        "8.8.8.8": "Google",
        "1.1.1.1": "Cloudflare",
        "9.9.9.9": "Quad9",
        "208.67.222.222": "OpenDNS",
        "64.6.64.6": "Verisign",
    }
    
    console.print("\n[yellow]testing external DNS servers...[/yellow]")
    for server, name in dns_servers.items():
        out = runcmd(f"dig +short +time=2 +tries=1 whoami.akamai.net @{server} 2>/dev/null")
        if out.strip() and "timed out" not in out:
            console.print(f"  {name:15s} ({server}): responds")
        else:
            console.print(f"  {name:15s} ({server}): no response")
    
    # check for dns leaks using dnsleaktest
    console.print("\n[yellow]querying check.torproject.org for your exit IP...[/yellow]")
    out = runcmd("dig +short +time=5 check.torproject.org 2>/dev/null")
    if out.strip():
        console.print(f"  DNS resolves to: {out.strip()}")
    
    console.print("\n[dim]for full dns leak test visit: dnsleaktest.com or ipleak.net[/dim]")
    pause()

def kill_switch_info():
    clr()
    console.print("[bold red]=== KILL SWITCH SETUP GUIDE ===[/bold red]\n")
    console.print("""[yellow]kill switch = block all traffic if VPN drops[/yellow]

[i]1. create a VPN-only user and group:[/i]
    sudo groupadd vpnusers
    sudo useradd -g vpnusers -s /bin/false vpnuser

[i]2. iptables rules (block everything except VPN):[/i]

    # allow loopback
    sudo iptables -A INPUT -i lo -j ACCEPT
    sudo iptables -A OUTPUT -o lo -j ACCEPT

    # allow VPN tunnel (change tun0 to your vpn interface)
    sudo iptables -A INPUT -i tun0 -j ACCEPT
    sudo iptables -A OUTPUT -o tun0 -j ACCEPT

    # allow VPN auth
    sudo iptables -A OUTPUT -d VPN_SERVER_IP -j ACCEPT

    # block everything else
    sudo iptables -A INPUT -j DROP
    sudo iptables -A OUTPUT -j DROP
    sudo iptables -A FORWARD -j DROP

[i]3. to remove rules:[/i]
    sudo iptables -F
    sudo iptables -P INPUT ACCEPT
    sudo iptables -P OUTPUT ACCEPT
    sudo iptables -P FORWARD ACCEPT

[yellow]pro tip: save rules with: sudo iptables-save > /etc/iptables/rules.v4[/yellow]
""")
    pause()

def check_own_ip():
    clr()
    console.print("[bold red]=== CHECK MY IP ADDRESSES ===[/bold red]\n")
    
    try:
        import requests
        
        endpoints = [
            ("https://api.ipify.org?format=json", "ipify"),
            ("https://ifconfig.me/ip", "ifconfig.me"),
            ("https://icanhazip.com/", "icanhazip"),
            ("https://api.my-ip.io/v2/ip.json", "my-ip.io"),
        ]
        
        ips = []
        for url, name in endpoints:
            try:
                r = requests.get(url, timeout=5)
                ip = r.text.strip()
                if '{' in ip:
                    ip = r.json().get("ip", r.json().get("query", "?"))
                ips.append((name, ip))
                console.print(f"  {name:15s}: [cyan]{ip}[/cyan]")
            except:
                console.print(f"  {name:15s}: [red]failed[/red]")
        
        # check if all match
        unique = set(ip for _, ip in ips)
        if len(unique) == 1:
            console.print(f"\n[green]all endpoints agree: {list(unique)[0]}[/green]")
        else:
            console.print(f"\n[red]WARNING: different IPs detected! possible proxy/VPN split tunneling[/red]")
            console.print("[yellow]if using VPN, some traffic may be leaking[/yellow]")
            
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def tor_check():
    clr()
    console.print("[bold red]=== TOR EXIT NODE CHECK ===[/bold red]\n")
    
    try:
        import requests
        r = requests.get("https://check.torproject.org/api/ip", timeout=10)
        data = r.json()
        
        ip = data.get("IP", "?")
        is_tor = data.get("IsTor", False)
        exit_ip = data.get("IsExit", False)
        
        console.print(f"  IP: {ip}")
        if is_tor:
            console.print("  [green]YES - you are using Tor[/green]")
        else:
            console.print("  [red]NO - you are NOT using Tor[/red]")
        
        if exit_ip:
            console.print("  [yellow]you are on a Tor exit node[/yellow]")
            
    except Exception as e:
        console.print(f"[red]check failed: {e}[/red]")
    
    console.print("\n[dim]to use tor: configure browser/system to use SOCKS5 proxy on 127.0.0.1:9050[/dim]")
    pause()

def webrtc_check():
    clr()
    console.print("[bold red]=== WEBRTC LEAK INFO ===[/bold red]\n")
    console.print("""[yellow]WebRTC can leak your real IP even behind VPN/Tor[/yellow]

[i]how to check:[/i]
  1. go to: browserleaks.com/webrtc
  2. or: ipleak.net
  
[i]how to fix:[/i]

  [cyan]firefox:[/i]
    1. go to about:config
    2. set media.peerconnection.enabled = false
    3. or install "uBlock Origin" and disable WebRTC

  [cyan]chrome/chromium:[/i]
    1. install "WebRTC Leak Prevent" extension
    2. or use --disable-webrtc flag

  [cyan]brave:[/i]
    shields already block most WebRTC leaks
  
  [cyan]tor browser:[/i]
    WebRTC is disabled by default

[yellow]nuclear option: disable webrtc completely in your VPN client config[/yellow]
""")
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== OPSEC & ANONYMITY ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "MAC Address Changer",
            "VPN / Proxy Detection",
            "DNS Leak Test",
            "Check My IP Address",
            "Tor Exit Node Check",
            "Kill Switch Setup Guide",
            "WebRTC Leak Info",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]OPSEC / ANON[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: mac_changer()
        elif c == 2: vpn_check()
        elif c == 3: dns_leak_test()
        elif c == 4: check_own_ip()
        elif c == 5: tor_check()
        elif c == 6: kill_switch_info()
        elif c == 7: webrtc_check()
        elif c == 0: return
