# 0day

OSINT & OPSEC command center for penetration testers and security researchers.

## install

**Linux:**
```bash
git clone https://github.com/AstralZX/0day.git
cd 0day
chmod +x setup.sh
./setup.sh
```

**Windows:**
```powershell
git clone https://github.com/AstralZX/0day.git
cd 0day
powershell -ExecutionPolicy Bypass -File install.ps1
```

then run `0day` from your terminal.

## modules

| module | description |
|--------|-------------|
| OSINT Recon | IP lookup, DNS, WHOIS, port scanner, subdomain enum, banner grab |
| Web Recon | HTTP headers, tech detection, robots.txt, directory bust, SSL check |
| Network Tools | ping, traceroute, local info, ARP scan, host discovery, ASN lookup |
| OPSEC & Anon | MAC changer, VPN/proxy detection, DNS leak test, Tor check, kill switch, WebRTC |
| Metasploit | msfvenom payload builder, exploit browser, meterpreter cheat sheet, resource scripts |
| Crypto & Hash | hash generator, file hashing, hash verification, base64/hex/url encode, password generator |
| Deep Recon | email OSINT, username enumeration, domain recon, phone lookup, breach check, git recon |
| Stealth Ops | bash history wipe, log cleanup, timestomping, file shredder, anti-forensics guide |
| Wireless | WiFi scan, handshake capture guide, PMKID attack, aircrack-ng cheat sheet |
| Social Recon | username search (30+ platforms), email-to-social, image metadata, git dorking |
| C2 Panel | MSF/netcat/python listeners, session management, multi-handler, bind shells |
| Reverse Shells | bash, python, php, netcat, perl, ruby, java, powershell, lua, node.js, go, socat |
| Webshells | PHP (8 types), JSP, ASP/ASPX, Python, CGI, msfvenom webshells |
| Exploits & Vulns | built-in CVE database, searchsploit, CVE lookup, service enumeration |
| Credentials | hashcat modes, john reference, password spraying, hash identifier, shadow/sam dump |
| Persistence | linux (cron, systemd, SSH, bashrc, LD_PRELOAD) + windows (registry, tasks, services, WMI) |
| Privilege Esc | linux and windows privesc checklists with tools and common exploits |
| Tunnels & Pivots | SSH tunnels, Chisel, Ligolo-NG, Socat, port forward builder |
| Phishing | credential harvester, SET, GoPhish, Evilginx2, email spoofing, QR phishing |

## requirements

- Python 3.8+
- `rich`, `requests` (installed by setup script)

**optional (for full functionality):**
```bash
# arch
sudo pacman -S nmap whois traceroute macchanger aircrack-ng hashcat hydra john socat

# AUR
yay -S sherlock exploitdb
```

## usage

```
0day
```

navigate with number keys, type `b` to go back, `q` to quit.

## disclaimer

this tool is for authorized security testing and educational purposes only. don't be a dick with it.

## license

[GNU Affero General Public License v3.0](LICENSE)
