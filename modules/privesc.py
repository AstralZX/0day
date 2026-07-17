# privilege escalation checklist
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


def linux_privesc():
    clr()
    console.print("[bold red]=== LINUX PRIVILEGE ESCALATION ===[/bold red]\n")
    
    console.print("[bold yellow]--- Enumeration Commands ---[/bold yellow]\n")
    
    enum_cmds = {
        "whoami / id": "current user and groups",
        "uname -a": "kernel version (check for exploits)",
        "cat /etc/os-release": "OS version",
        "find / -perm -4000 2>/dev/null": "SUID binaries",
        "find / -writable -type f 2>/dev/null": "writable files",
        "find / -writable -type d 2>/dev/null": "writable directories",
        "cat /etc/crontab": "crontabs",
        "crontab -l": "user crontab",
        "ls -la /etc/cron*": "cron directories",
        "netstat -tlnp": "listening ports",
        "ss -tlnp": "listening ports (newer)",
        "ps aux": "running processes",
        "cat /etc/passwd": "all users",
        "find / -name '*.conf' -writable": "writable configs",
        "find / -name '*.log' -writable": "writable logs",
        "sudo -l": "sudo permissions",
        "find / -name '*.sh' -writable": "writable scripts",
    }
    
    for cmd, desc in enum_cmds.items():
        console.print(f"  [cyan]{cmd}[/cyan]")
        console.print(f"    [dim]{desc}[/dim]")
    
    console.print("\n[bold yellow]--- Common Exploits ---[/bold yellow]\n")
    console.print("  - dirty cow: CVE-2016-5195 (kernel < 4.8.3)")
    console.print("  - dirty pipe: CVE-2022-0847 (kernel 5.8+)")
    console.print("  - dirty cow 2: CVE-2022-2588")
    console.print("  - polkit: CVE-2021-4034 (pkexec)")
    console.print("  - log4shell: CVE-2021-44228")
    
    console.print("\n[bold yellow]--- Tools ---[/bold yellow]\n")
    console.print("  [cyan]linux-exploit-suggester.sh[/cyan]  - auto find exploits")
    console.print("  [cyan]LinPEAS[/cyan]                      - comprehensive enum")
    console.print("  [cyan]LinEnum.sh[/cyan]                   - quick enum")
    console.print("  [cyan]pspy[/cyan]                         - watch processes")
    
    pause()

def windows_privesc():
    clr()
    console.print("[bold red]=== WINDOWS PRIVILEGE ESCALATION ===[/bold red]\n")
    
    console.print("[bold yellow]--- Enumeration ---[/bold yellow]\n")
    enum_cmds = [
        "whoami /all",
        "systeminfo",
        "net user",
        "net localgroup administrators",
        "netstat -ano",
        "tasklist /svc",
        "sc query",
        "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services",
        "wmic service list brief",
        "wmic process list brief",
        "cmdkey /list",
        "dir /s /b C:\\Users\\*.kdbx",
    ]
    for cmd in enum_cmds:
        console.print(f"  [cyan]{cmd}[/cyan]")
    
    console.print("\n[bold yellow]--- Common Privesc Vectors ---[/bold yellow]\n")
    vectors = [
        "Unquoted Service Path",
        "Weak Service Permissions",
        "DLL Hijacking",
        "AlwaysInstallElevated (registry)",
        "Token Impersonation (SeImpersonatePrivilege)",
        "Stored Credentials (cmdkey /list)",
        "Startup Applications",
        "Scheduled Tasks (writable)",
        "Registry autorun (writable)",
        "Kernel Exploits (MS16-032, MS16-075, etc)",
    ]
    for v in vectors:
        console.print(f"  - {v}")
    
    console.print("\n[bold yellow]--- Tools ---[/bold yellow]\n")
    console.print("  [cyan]WinPEAS.exe[/cyan]        - comprehensive enum")
    console.print("  [cyan]PowerUp.ps1[/cyan]        - PowerShell enum")
    console.print("  [cyan]Seatbelt.exe[/cyan]       - security check")
    console.print("  [cyan]SharpUp.exe[/cyan]        - .NET privesc")
    console.print("  [cyan]JAWS[/cyan]               - another enum tool")
    
    pause()

def run():
    while True:
        clr()
        console.print("[bold red]=== PRIVILEGE ESCALATION ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Linux Privesc Checklist",
            "Windows Privesc Checklist",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]PRIVESC[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: linux_privesc()
        elif c == 2: windows_privesc()
        elif c == 0: return
