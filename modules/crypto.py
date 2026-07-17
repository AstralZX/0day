# crypto and hashing tools
import os, hashlib, base64, secrets, string, binascii, math, codecs
from urllib.parse import quote, unquote
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

def hash_text():
    clr()
    console.print("[bold red]=== HASH GENERATOR ===[/bold red]\n")
    text = Prompt.ask("[cyan]text to hash[/cyan]")
    
    algos = ["md5", "sha1", "sha256", "sha512", "sha3_256", "blake2b"]
    
    t = Table(box=box.SIMPLE, title="Hash Results")
    t.add_column("Algorithm", style="bold cyan")
    t.add_column("Hash")
    
    for algo in algos:
        try:
            h = hashlib.new(algo)
            h.update(text.encode())
            t.add_row(algo.upper(), h.hexdigest())
        except:
            t.add_row(algo.upper(), "unsupported")
    
    console.print(t)
    pause()

def hash_file():
    clr()
    console.print("[bold red]=== FILE HASH ===[/bold red]\n")
    path = Prompt.ask("[cyan]file path[/cyan]")
    
    if not os.path.exists(path):
        console.print("[red]file not found[/red]")
        pause()
        return
    
    console.print(f"\n[yellow]hashing {path}...[/yellow]\n")
    
    algos = ["md5", "sha1", "sha256", "sha512"]
    t = Table(box=box.SIMPLE)
    t.add_column("Algorithm", style="bold cyan")
    t.add_column("Hash")
    
    for algo in algos:
        try:
            h = hashlib.new(algo)
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            t.add_row(algo.upper(), h.hexdigest())
        except Exception as e:
            t.add_row(algo.upper(), f"error: {e}")
    
    console.print(t)
    size = os.path.getsize(path)
    console.print(f"\n[dim]file size: {size} bytes ({size/1024:.1f} KB)[/dim]")
    pause()

def verify_hash():
    clr()
    console.print("[bold red]=== HASH VERIFICATION ===[/bold red]\n")
    path = Prompt.ask("[cyan]file path[/cyan]")
    known = Prompt.ask("[cyan]known hash[/cyan]")
    
    if not os.path.exists(path):
        console.print("[red]file not found[/red]")
        pause()
        return
    
    kl = len(known.strip())
    if kl == 32:
        algos = ["md5"]
    elif kl == 40:
        algos = ["sha1"]
    elif kl == 64:
        algos = ["sha256"]
    elif kl == 128:
        algos = ["sha512"]
    else:
        algos = ["md5", "sha1", "sha256", "sha512"]
    
    console.print(f"\n[dim]detected algo(s): {', '.join(algos)}[/dim]\n")
    
    for algo in algos:
        h = hashlib.new(algo)
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        computed = h.hexdigest()
        
        if computed == known.strip():
            console.print(f"[green]{algo.upper()}: MATCH![/green]")
        else:
            console.print(f"[red]{algo.upper()}: no match[/red]")
            console.print(f"  computed: {computed}")
            console.print(f"  expected: {known}")
    
    pause()

def encode_b64():
    clr()
    console.print("[bold red]=== BASE64 ===[/bold red]\n")
    console.print("  [1] encode")
    console.print("  [2] decode")
    choice = Prompt.ask("[cyan]choice[/cyan]")
    text = Prompt.ask("[cyan]input[/cyan]")
    
    try:
        if choice == "1":
            result = base64.b64encode(text.encode()).decode()
        else:
            result = base64.b64decode(text.encode()).decode()
        console.print(f"\n[green]{result}[/green]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def encode_hex():
    clr()
    console.print("[bold red]=== HEX ===[/bold red]\n")
    console.print("  [1] text -> hex")
    console.print("  [2] hex -> text")
    choice = Prompt.ask("[cyan]choice[/cyan]")
    text = Prompt.ask("[cyan]input[/cyan]")
    
    try:
        if choice == "1":
            result = binascii.hexlify(text.encode()).decode()
        else:
            result = binascii.unhexlify(text.encode()).decode()
        console.print(f"\n[green]{result}[/green]")
    except Exception as e:
        console.print(f"[red]error: {e}[/red]")
    
    pause()

def url_encode():
    clr()
    console.print("[bold red]=== URL ENCODE ===[/bold red]\n")
    console.print("  [1] encode")
    console.print("  [2] decode")
    choice = Prompt.ask("[cyan]choice[/cyan]")
    text = Prompt.ask("[cyan]input[/cyan]")
    
    if choice == "1":
        result = quote(text)
    else:
        result = unquote(text)
    console.print(f"\n[green]{result}[/green]")
    pause()

def rot13():
    clr()
    console.print("[bold red]=== ROT13 ===[/bold red]\n")
    text = Prompt.ask("[cyan]input[/cyan]")
    result = codecs.decode(text, 'rot_13')
    console.print(f"\n[green]{result}[/green]")
    pause()

def password_gen():
    clr()
    console.print("[bold red]=== PASSWORD GENERATOR ===[/bold red]\n")
    
    length = int(Prompt.ask("[cyan]length[/cyan]", default="20"))
    use_upper = Prompt.ask("[cyan]uppercase? (y/n)[/cyan]", default="y")
    use_lower = Prompt.ask("[cyan]lowercase? (y/n)[/cyan]", default="y")
    use_digits = Prompt.ask("[cyan]numbers? (y/n)[/cyan]", default="y")
    use_special = Prompt.ask("[cyan]symbols? (y/n)[/cyan]", default="y")
    count = int(Prompt.ask("[cyan]how many?[/cyan]", default="5"))
    
    chars = ""
    if use_upper.lower() == "y":
        chars += string.ascii_uppercase
    if use_lower.lower() == "y":
        chars += string.ascii_lowercase
    if use_digits.lower() == "y":
        chars += string.digits
    if use_special.lower() == "y":
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    if not chars:
        console.print("[red]need at least one character set[/red]")
        pause()
        return
    
    console.print(f"\n[green]{count} passwords (length {length}):[/green]\n")
    for i in range(count):
        pw = ''.join(secrets.choice(chars) for _ in range(length))
        pool = len(chars)
        entropy = math.log2(pool) * length
        
        if entropy > 100:
            strength = "very strong"
        elif entropy > 80:
            strength = "strong"
        elif entropy > 60:
            strength = "okay"
        else:
            strength = "weak"
        
        console.print(f"  {pw}  [dim]({entropy:.0f} bits - {strength})[/dim]")
    
    pause()

def uuid_gen():
    clr()
    console.print("[bold red]=== UUID GENERATOR ===[/bold red]\n")
    count = int(Prompt.ask("[cyan]how many?[/cyan]", default="5"))
    
    import uuid
    for i in range(count):
        console.print(f"  {uuid.uuid4()}")
    
    pause()

def hash_crack():
    clr()
    console.print("[bold red]=== HASH IDENTIFIER ===[/bold red]\n")
    h = Prompt.ask("[cyan]paste hash[/cyan]")
    h = h.strip()
    hl = len(h)
    
    console.print(f"\n[yellow]hash length: {hl} chars[/yellow]\n")
    
    known = {
        32: ["MD5", "NTLM", "MD4"],
        40: ["SHA-1", "RIPEMD-160"],
        56: ["SHA-224"],
        64: ["SHA-256", "SHA3-256", "BLAKE2-256"],
        96: ["SHA-384"],
        128: ["SHA-512", "SHA3-512"],
        16: ["CRC32", "MySQL 4.1+"],
        41: ["MySQL (old)"],
        60: ["bcrypt"],
    }
    
    if hl in known:
        console.print(f"[green]likely hash types:[/green]")
        for ht in known[hl]:
            console.print(f"  - {ht}")
    else:
        console.print("[dim]unknown hash length, could be custom or salted[/dim]")
    
    # basic pattern checks
    if h.startswith("$2"):
        console.print("[green]  detected: bcrypt hash[/green]")
    elif h.startswith("$2b$"):
        console.print("[green]  detected: bcrypt variant[/green]")
    elif h.startswith("$argon2"):
        console.print("[green]  detected: Argon2[/green]")
    elif h.startswith("$pbkdf2"):
        console.print("[green]  detected: PBKDF2[/green]")
    elif re.match(r'^[a-f0-9]+$', h):
        console.print("[green]  format: lowercase hex[/green]")
    elif re.match(r'^[A-F0-9]+$', h):
        console.print("[green]  format: uppercase hex[/green]")
    
    pause()

import re


def run():
    while True:
        clr()
        console.print("[bold red]=== CRYPTO & HASH ===[/bold red]\n")
        from rich.table import Table
        t = Table(show_header=False, box=box.ROUNDED, border_style="red", padding=(0, 2))
        t.add_column("", style="bold yellow", width=4)
        t.add_column("")
        opts = [
            "Hash Text (md5/sha/etc)",
            "Hash a File",
            "Verify File Hash",
            "Hash Identifier",
            "Base64 Encode/Decode",
            "Hex Encode/Decode",
            "URL Encode/Decode",
            "ROT13",
            "Password Generator",
            "UUID Generator",
        ]
        for i, o in enumerate(opts, 1):
            t.add_row(str(i), o)
        t.add_row("", "")
        t.add_row("b", "Back")
        console.print(Panel(t, title="[bold]CRYPTO & HASH[/bold]", border_style="red"))
        
        try:
            c = int(Prompt.ask("[bold yellow]>[/bold yellow]"))
        except ValueError:
            c = 0
        
        if c == 1: hash_text()
        elif c == 2: hash_file()
        elif c == 3: verify_hash()
        elif c == 4: hash_crack()
        elif c == 5: encode_b64()
        elif c == 6: encode_hex()
        elif c == 7: url_encode()
        elif c == 8: rot13()
        elif c == 9: password_gen()
        elif c == 10: uuid_gen()
        elif c == 0: return
