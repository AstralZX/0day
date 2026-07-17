#!/bin/bash
# 0day setup - works on debian, ubuntu, arch, fedora, etc
# run: bash setup.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PANEL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${RED}    ___  _____      __     __${NC}"
echo -e "${RED}   / _ \\|  __ \\   /\\ \\   / /${NC}"
echo -e "${RED}  | | | | |  | | /  \\ \\_/ / ${NC}"
echo -e "${RED}  | | | | |  | |/ /\\ \\ \\ /  ${NC}"
echo -e "${RED}  | |_| | |__| / ____ \\| |   ${NC}"
echo -e "${RED}   \\___/|_____/_/    \\_\\_|   ${NC}"
echo ""
echo -e "${CYAN}0day setup - $PANEL_DIR${NC}"
echo ""

# detect package manager
install_pkg() {
    local pkg=$1
    if command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm "$pkg" 2>/dev/null
    elif command -v apt-get &>/dev/null; then
        sudo apt-get install -y "$pkg" 2>/dev/null
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y "$pkg" 2>/dev/null
    elif command -v zypper &>/dev/null; then
        sudo zypper install -y "$pkg" 2>/dev/null
    elif command -v apk &>/dev/null; then
        sudo apk add "$pkg" 2>/dev/null
    else
        echo -e "  ${YELLOW}[!] no package manager found for $pkg${NC}"
        return 1
    fi
}

# check if command exists
has() { command -v "$1" &>/dev/null; }

# ============================================================
echo -e "${GREEN}[1/5] Python...${NC}"
# ============================================================
PY=""
for cmd in python3 python; do
    if has "$cmd"; then
        ver=$("$cmd" --version 2>&1 | head -1)
        if echo "$ver" | grep -q "Python 3"; then
            PY="$cmd"
            echo -e "  ${GREEN}[+] $ver${NC}"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo -e "  ${RED}[!] Python 3 not found${NC}"
    echo -e "  ${YELLOW}[*] attempting to install...${NC}"
    install_pkg python3 || install_pkg python
    # recheck
    for cmd in python3 python; do
        if has "$cmd"; then PY="$cmd"; break; fi
    done
    if [ -z "$PY" ]; then
        echo -e "  ${RED}[!] install Python 3 manually: https://python.org${NC}"
        exit 1
    fi
fi

# ============================================================
echo -e "${GREEN}[2/5] pip packages...${NC}"
# ============================================================
for pkg in rich requests; do
    $PY -c "import $pkg" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}[+] $pkg${NC}"
    else
        echo -e "  ${YELLOW}[*] installing $pkg...${NC}"
        $PY -m pip install "$pkg" --quiet --break-system-packages 2>/dev/null || \
        $PY -m pip install "$pkg" --quiet --user 2>/dev/null || \
        $PY -m pip install "$pkg" --quiet 2>/dev/null || \
        echo -e "  ${RED}[!] failed to install $pkg${NC}"
    fi
done

# ============================================================
echo -e "${GREEN}[3/5] system tools...${NC}"
# ============================================================
# map package names per distro
declare -A PKGS
if has pacman; then
    PKGS=( [nmap]=nmap [whois]=whois [traceroute]=traceroute [curl]=curl [wget]=wget [socat]=socat [nc]=openbsd-netcat [hydra]=hydra [aircrack-ng]=aircrack-ng [hashcat]=hashcat [john]=john )
elif has apt-get; then
    PKGS=( [nmap]=nmap [whois]=whois [traceroute]=traceroute [curl]=curl [wget]=wget [socat]=socat [nc]=netcat-openbsd [hydra]=hydra [aircrack-ng]=aircrack-ng [hashcat]=hashcat [john]=john )
elif has dnf; then
    PKGS=( [nmap]=nmap [whois]=whois [traceroute]=traceroute [curl]=curl [wget]=wget [socat]=socat [nc]=nmap-ncat [hydra]=hydra [aircrack-ng]=aircrack-ng [hashcat]=hashcat [john]=john )
else
    PKGS=( [nmap]=nmap [whois]=whois [curl]=curl [wget]=wget [socat]=socat )
fi

for cmd in nmap whois traceroute curl wget socat nc hydra aircrack-ng hashcat john; do
    if has "$cmd"; then
        echo -e "  ${GREEN}[+] $cmd${NC}"
    else
        pkg="${PKGS[$cmd]}"
        if [ -n "$pkg" ]; then
            echo -e "  ${YELLOW}[*] installing $cmd...${NC}"
            install_pkg "$pkg" 2>/dev/null
            if has "$cmd"; then
                echo -e "  ${GREEN}[+] $cmd${NC}"
            else
                echo -e "  ${YELLOW}[~] $cmd skipped (install manually if needed)${NC}"
            fi
        fi
    fi
done

# exiftool has different names
if ! has exiftool; then
    echo -e "  ${YELLOW}[*] installing exiftool...${NC}"
    install_pkg perl-image-exiftool 2>/dev/null || install_pkg libimage-exiftool-perl 2>/dev/null
fi

# ============================================================
echo -e "${GREEN}[4/5] AUR packages (if available)...${NC}"
# ============================================================
if has yay; then
    for pkg in sherlock exploitdb; do
        if ! has "$pkg"; then
            echo -e "  ${YELLOW}[*] installing $pkg from AUR...${NC}"
            yay -S --noconfirm "$pkg" 2>/dev/null || echo -e "  ${YELLOW}[~] $pkg skipped${NC}"
        else
            echo -e "  ${GREEN}[+] $pkg${NC}"
        fi
    done
elif has paru; then
    for pkg in sherlock exploitdb; do
        if ! has "$pkg"; then
            paru -S --noconfirm "$pkg" 2>/dev/null || echo -e "  ${YELLOW}[~] $pkg skipped${NC}"
        else
            echo -e "  ${GREEN}[+] $pkg${NC}"
        fi
    done
else
    echo -e "  ${YELLOW}[~] no AUR helper found, skipping sherlock/exploitdb${NC}"
fi

# ============================================================
echo -e "${GREEN}[5/5] creating 0day command...${NC}"
# ============================================================
mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/0day" << EOF
#!/bin/bash
cd "$PANEL_DIR" || exit 1
exec $PY "$PANEL_DIR/0panel.py" "\$@"
EOF
chmod +x "$HOME/.local/bin/0day"
chmod +x "$PANEL_DIR/0panel.py"

# also make setup.sh executable
chmod +x "$PANEL_DIR/setup.sh" 2>/dev/null

# add to PATH if needed
ADDED_PATH=false
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    if [ -f "$rc" ] && ! grep -q '.local/bin' "$rc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
        ADDED_PATH=true
        break
    fi
done

if [ "$ADDED_PATH" = true ]; then
    echo -e "  ${YELLOW}[!] added ~/.local/bin to PATH (restart terminal or run: source ~/.bashrc)${NC}"
fi

# ============================================================
#  done
# ============================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  0day setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${CYAN}installed:${NC}"
for cmd in nmap whois traceroute curl wget socat nc hydra aircrack-ng hashcat john exiftool sherlock; do
    if has "$cmd"; then echo -e "  ${GREEN}+${NC} $cmd"; fi
done

echo ""
echo -e "${CYAN}install manually if needed:${NC}"
echo "  metasploit  : https://www.metasploit.com/download"
echo "  nuclei      : yay -S nuclei-bin"
echo "  ligolo-ng   : github.com/nicocha30/ligolo-ng/releases"
echo "  chisel      : github.com/jpillora/chisel/releases"
echo "  evilginx2   : github.com/kgretzky/evilginx2"
echo ""
echo -e "${GREEN}run: ${RED}0day${NC}"
