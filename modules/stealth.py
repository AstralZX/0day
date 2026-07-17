# stealth ops - anti-forensics, log wiping, timestomping etc
import os, subprocess, time, glob
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
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


def clear_bash_history():
    clr()
    console.print("[bold red]=== BASH HISTORY WIPE ===[/bold red]\n")
    
    console.print("[yellow]current history file locations:[/yellow]")
    for h in [os.path.expanduser("~/.bash_history"), 
              os.path.expanduser("~/.zsh_history"),
              "/root/.bash_history"]:
        if os.path.exists(h):
            size = os.path.getsize(h)
            console.print(f"  {h} ({size} bytes)")
    
    if not Confirm.ask("\n[cyan]wipe all shell history?[/cyan]"):
        return
    
    history_files = [
        os.path.expanduser("~/.bash_history"),
        os.path.expanduser("~/.zsh_history"),
        os.path.expanduser("~/.local/share/fish/fish_history"),
        "/root/.bash_history",
        "/root/.zsh_history",
    ]
    
    for hf in history_files:
        if os.path.exists(hf):
            # overwrite with garbage then delete
            with open(hf, 'wb') as f:
                f.write(b'\x00' * os.path.getsize(hf))
            os.remove(hf)
            console.print(f"  [green]wiped: {hf}[/green]")
    
    # clear in-memory history
    os.system("history -c 2>/dev/null")
    os.system("unset HISTFILE 2>/dev/null")
    
    console.print("\n[green]history wiped[/green]")
    console.print("[dim]tip: also run 'export HISTFILESIZE=0' to prevent future logging[/dim]")
    pause()

def clear_logs():
    clr()
    console.print("[bold red]=== SYSTEM LOG CLEANUP ===[/bold red]\n")
    console.print("[red]WARNING: this will mess up your system logs[/red]\n")
    
    if not Confirm.ask("[cyan]continue?[/cyan]"):
        return
    
    log_files = [
        "/var/log/auth.log",
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/kern.log",
        "/var/log/dmesg",
        "/var/log/boot.log",
        "/var/log/wtmp",
        "/var/log/btmp",
        "/var/log/lastlog",
        "/var/log/faillog",
        "/var/log/nginx/access.log",
        "/var/log/apache2/access.log",
        "/var/log/httpd/access_log",
    ]
    
    cleared = 0
    for lf in log_files:
        if os.path.exists(lf):
            try:
                if lf in ["/var/log/wtmp", "/var/log/btmp", "/var/log/lastlog"]:
                    # these are binary, truncate
                    runcmd(f"truncate -s 0 {lf} 2>/dev/null || > {lf}")
                else:
                    with open(lf, 'w') as f:
                        f.write("")
                console.print(f"  [green]cleared: {lf}[/green]")
                cleared += 1
            except:
                console.print(f"  [red]failed: {lf} (need root?)[/red]")
    
    # clear journal
    runcmd("journalctl --rotate 2>/dev/null")
    runcmd("journalctl --vacuum-time=1s 2>/dev/null")
    
    console.print(f"\n[green]cleared {cleared} log files[/green]")
    pause()

def timestomp():
    clr()
    console.print("[bold red]=== TIMESTOMPING ===[/bold red]\n")
    console.print("[dim]change file timestamps to hide modifications[/dim]\n")
    
    path = Prompt.ask("[cyan]file path[/cyan]")
    if not os.path.exists(path):
        console.print("[red]file not found[/red]")
        pause()
        return
    
    # show current timestamps
    stat = os.stat(path)
    console.print(f"\n[yellow]current timestamps:[/yellow]")
    console.print(f"  modified:  {datetime.fromtimestamp(stat.st_mtime)}")
    console.print(f"  accessed:  {datetime.fromtimestamp(stat.st_atime)}")
    console.print(f"  changed:   {datetime.fromtimestamp(stat.st_ctime)}")
    
    console.print("\n[yellow]options:[/yellow]")
    console.print("  [1] copy timestamps from another file")
    console.print("  [2] set to specific date")
    console.print("  [3] set to random old date")
    choice = Prompt.ask("[cyan]choice[/cyan]")
    
    if choice == "1":
        src = Prompt.ask("[cyan]source file (copy its timestamps)[/cyan]")
        if os.path.exists(src):
            runcmd(f"touch -r {src} {path}")
            console.print("[green]timestamps copied[/green]")
    elif choice == "2":
        date_str = Prompt.ask("[cyan]date (YYYY-MM-DD HH:MM:SS)[/cyan]")
        runcmd(f"touch -d '{date_str}' {path}")
        console.print("[green]timestamps set[/green]")
    elif choice == "3":
        # random date in past 2 years
        import random
        days_ago = random.randint(30, 730)
        runcmd(f"touch -d '{days_ago} days ago' {path}")
        console.print(f"[green]set to ~{days_ago} days ago[/green]")
    
    # show new timestamps
    stat = os.stat(path)
    console.print(f"\n[yellow]new timestamps:[/yellow]")
    console.print(f"  modified:  {datetime.fromtimestamp(stat.st_mtime)}")
    console.print(f"  accessed:  {datetime.fromtimestamp(stat.st_atime)}")
    pause()

def file_shred():
    clr()
    console.print("[bold red]=== FILE SHREDDER ===[/bold red]\n")
    path = Prompt.ask("[cyan]file to shred[/cyan]")
    
    if not os.path.exists(path):
        console.print("[red]file not found[/red]")
        pause()
        return
    
    size = os.path.getsize(path)
    console.print(f"\n[yellow]file: {path} ({size} bytes)[/yellow]")
    
    if not Confirm.ask("[cyan]shred this file? (overwrites then deletes)[/cyan]"):
        return
    
    # multiple passes
    passes = int(Prompt.ask("[cyan]passes (3 is standard, 7 is paranoid)[/cyan]", default="3"))
    
    console.print(f"\n[yellow]shredding with {passes} passes...[/yellow]")
    
    try:
        with open(path, 'ba+') as f:
            length = f.tell()
            for i in range(passes):
                f.seek(0)
                if i % 2 == 0:
                    f.write(b'\x00' * length)
                else:
                    f.write(b'\xff' * length)
                f.flush()
                os.fsync(f.fileno())
                console.print(f"  pass {i+1}/{passes} done")
        
        os.remove(path)
        console.print(f"\n[green]file shredded and deleted[/green]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def secure_delete():
    clr()
    console.print("[bold red]=== SECURE DELETE ===[/bold red]\n")
    path = Prompt.ask("[cyan]path to delete[/cyan]")
    
    if not os.path.exists(path):
        console.print("[red]not found[/red]")
        pause()
        return
    
    if os.path.isdir(path):
        console.print("[yellow]directory detected, will shred all files inside[/yellow]")
        files = glob.glob(os.path.join(path, "*"))
        console.print(f"found {len(files)} files")
        
        if Confirm.ask("[cyan]shred all?[/cyan]"):
            for f in files:
                if os.path.isfile(f):
                    runcmd(f"shred -vfz -n 3 '{f}' 2>/dev/null && rm -f '{f}'")
                    console.print(f"  shredded: {f}")
            runcmd(f"rmdir '{path}' 2>/dev/null")
            console.print("[green]done[/green]")
    else:
        runcmd(f"shred -vfz -n 3 '{path}' && rm -f '{path}'")
        console.print("[green]done[/green]")
    
    pause()

def hide_process():
    clr()
    console.print("[bold red]=== PROCESS ANONYMITY ===[/bold red]\n")
    console.print("[dim]tips for hiding processes[/dim]\n")
    
    console.print("""[yellow]--- methods ---[/yellow]

  1. rename your process:
     exec -a fake_name ./payload

  2. use LD_PRELOAD to hide from /proc:
     compile a .so that hooks readdir() for /proc

  3. run in background with nohup:
     nohup ./script.sh &

  4. use a different process name in argv[0]:
     argv[0] = "[kworker/0:1]"
     
  5. modify /proc/self/comm:
     echo -n "kworker" > /proc/self/comm

[yellow]--- detection evasion ---[/yellow]
  
  - avoid suspicious process names
  - keep memory usage low  
  - dont spawn too many threads
  - use familiar ports (80, 443)
  - check: ps aux | grep <your process>
""")
    pause()

def anti_forensics():
    clr()
    console.print("[bold red]=== ANTI-FORENSICS GUIDE ===[/bold red]\n")
    
    console.print("""[yellow]--- covering tracks ---[/yellow]

  [1] clear bash history:
      history -c && unset HISTFILE
      rm -f ~/.bash_history ~/.zsh_history

  [2] clear system logs:
      truncate -s 0 /var/log/auth.log
      truncate -s 0 /var/log/syslog
      journalctl --vacuum-time=1s

  [3] clear temp files:
      rm -rf /tmp/* /var/tmp/*

  [4] clear recent files:
      rm -rf ~/.local/share/recently-used.xbel
      rm -rf ~/.recently-used*

  [5] clear thumbnails:
      rm -rf ~/.cache/thumbnails/*

  [6] clear DNS cache:
      sudo systemd-resolve --flush-caches 2>/dev/null
      sudo resolvectl flush-caches 2>/dev/null

  [7] clear mac address traces:
      sudo ip link set dev eth0 down
      sudo macchanger -r eth0
      sudo ip link set dev eth0 up

  [8] clear package manager cache:
      sudo pacman -Scc (arch)
      sudo apt clean (debian)

  [9] timestomp sensitive files:
      touch -r /etc/hosts <your_file>

  [10] shred before deleting:
       shred -vfz -n 3 <file>

[yellow]--- important ---[/yellow]

  - always work from a live USB or VM
  - use full disk encryption
  - route traffic through tor/VPN
  - check: last -f /var/log/wtmp
  - check: lastb -f /var/log/btmp
  - check: ausearch -m LOGIN
""")
    pause()

def clean_traces():
    clr()
    console.print("[bold red]=== QUICK TRACE CLEANUP ===[/bold red]\n")
    console.print("[yellow]running automated cleanup...[/yellow]\n")
    
    cleaned = 0
    
    # bash history
    for f in [os.path.expanduser("~/.bash_history"), os.path.expanduser("~/.zsh_history")]:
        if os.path.exists(f):
            try:
                os.remove(f)
                console.print(f"  [green]removed: {f}[/green]")
                cleaned += 1
            except:
                pass
    
    # recent files
    recent = os.path.expanduser("~/.local/share/recently-used.xbel")
    if os.path.exists(recent):
        try:
            os.remove(recent)
            console.print(f"  [green]removed: recent files[/green]")
            cleaned += 1
        except:
            pass
    
    # thumbnails
    thumbs = os.path.expanduser("~/.cache/thumbnails")
    if os.path.exists(thumbs):
        runcmd(f"rm -rf {thumbs}")
        console.print("  [green]cleared thumbnails[/green]")
        cleaned += 1
    
    # tmp files
    runcmd("rm -rf /tmp/.0day_*")
    console.print("  [green]cleared temp files[/green]")
    cleaned += 1
    
    # DNS cache
    runcmd("systemd-resolve --flush-caches 2>/dev/null || resolvectl flush-caches 2>/dev/null")
    console.print("  [green]flushed DNS cache[/green]")
    cleaned += 1
    
    # clear in-memory history
    os.system("history -c 2>/dev/null")
    
    console.print(f"\n[green]cleaned {cleaned} things[/green]")
    console.print("[dim]for full cleanup, use the individual tools in the stealth menu[/dim]")
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== STEALTH OPS ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Wipe Bash History",
            "Clear System Logs",
            "Timestomp Files",
            "Shred Files (multi-pass)",
            "Secure Delete",
            "Quick Trace Cleanup",
            "Process Anonymity Tips",
            "Anti-Forensics Guide",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]STEALTH OPS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: clear_bash_history()
        elif c == 2: clear_logs()
        elif c == 3: timestomp()
        elif c == 4: file_shred()
        elif c == 5: secure_delete()
        elif c == 6: clean_traces()
        elif c == 7: hide_process()
        elif c == 8: anti_forensics()
        elif c == 0: return
