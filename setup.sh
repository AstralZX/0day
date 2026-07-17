#!/bin/bash
# 0day setup script
# run this once to get everything installed

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

BANNER='
    ___  _____      __     __
   / _ \|  __ \   /\ \   / /
  | | | | |  | | /  \ \_/ / 
  | | | | |  | |/ /\ \ \ /  
  | |_| | |__| / ____ \| |   
   \___/|_____/_/    \_\_|   
'

echo -e "${RED}${BANNER}${NC}"
echo -e "${CYAN}0day setup script${NC}"
echo ""

# check if root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] not running as root, some installs may need sudo${NC}"
fi

# detect package manager
install_pkg() {
    local pkg=$1
    if command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm "$pkg" 2>/dev/null || true
    elif command -v apt &>/dev/null; then
        sudo apt install -y "$pkg" 2>/dev/null || true
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y "$pkg" 2>/dev/null || true
    fi
}

install_aur() {
    local pkg=$1
    if command -v yay &>/dev/null; then
        yay -S --noconfirm "$pkg" 2>/dev/null || true
    elif command -v paru &>/dev/null; then
        paru -S --noconfirm "$pkg" 2>/dev/null || true
    else
        echo -e "${YELLOW}[!] no AUR helper found, skipping $pkg (install manually: yay -S $pkg)${NC}"
    fi
}

echo -e "${GREEN}[*] checking system...${NC}"

# detect distro
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${CYAN}    distro: $PRETTY_NAME${NC}"
fi

echo ""
echo -e "${GREEN}[1/6] installing python packages...${NC}"
pip3 install rich requests pyfiglet --break-system-packages 2>/dev/null || \
pip3 install rich requests pyfiglet 2>/dev/null || true

echo -e "${GREEN}[2/6] installing core tools...${NC}"
for pkg in nmap whois traceroute macchanger curl wget netcat-openbsd socat unzip; do
    if command -v "$pkg" &>/dev/null; then
        echo -e "  ${GREEN}[ok]${NC} $pkg"
    else
        echo -e "  ${YELLOW}[installing]${NC} $pkg"
        install_pkg "$pkg"
    fi
done

echo -e "${GREEN}[3/6] installing hacking tools...${NC}"
for pkg in aircrack-ng hashcat hydra john; do
    if command -v "$pkg" &>/dev/null; then
        echo -e "  ${GREEN}[ok]${NC} $pkg"
    else
        echo -e "  ${YELLOW}[installing]${NC} $pkg"
        install_pkg "$pkg"
    fi
done

echo -e "${GREEN}[4/6] installing optional tools...${NC}"
for pkg in perl-image-exiftool openbsd-netcat; do
    if command -v exiftool &>/dev/null || [ "$pkg" = "openbsd-netcat" ] && command -v nc &>/dev/null; then
        echo -e "  ${GREEN}[ok]${NC} $pkg"
    else
        echo -e "  ${YELLOW}[installing]${NC} $pkg"
        install_pkg "$pkg" 2>/dev/null || install_pkg "perl-image-exiftool" 2>/dev/null || true
    fi
done

echo -e "${GREEN}[5/6] installing AUR packages (if yay/paru available)...${NC}"
for pkg in sherlock exploitdb; do
    if command -v "$pkg" &>/dev/null; then
        echo -e "  ${GREEN}[ok]${NC} $pkg"
    else
        echo -e "  ${YELLOW}[installing via AUR]${NC} $pkg"
        install_aur "$pkg"
    fi
done

echo -e "${GREEN}[6/6] installing 0day...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin"

# create wrapper
cat > "$HOME/.local/bin/0day" << WRAPPER
#!/bin/bash
cd "$SCRIPT_DIR" || exit 1
exec python3 "$SCRIPT_DIR/0panel.py" "\$@"
WRAPPER
chmod +x "$HOME/.local/bin/0day"
chmod +x "$SCRIPT_DIR/0panel.py"

# check if .local/bin is in PATH
if ! echo "$PATH" | grep -q ".local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo -e "${YELLOW}[!] added ~/.local/bin to PATH in .bashrc${NC}"
    echo -e "${YELLOW}    run: source ~/.bashrc${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  0day setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# show what's installed vs what's missing
echo -e "${CYAN}installed tools:${NC}"
for tool in nmap whois traceroute macchanger curl wget nc socexiftool aircrack-ng hashcat hydra john sherlock searchsploit msfconsole msfvenom; do
    if command -v "$tool" &>/dev/null || [ -f "/usr/bin/$tool" ]; then
        echo -e "  ${GREEN}+${NC} $tool"
    fi
done

echo ""
echo -e "${CYAN}optional (install manually if needed):${NC}"
echo "  - metasploit    : https://www.metasploit.com/download"
echo "  - nuclei        : yay -S nuclei-bin"
echo "  - ligolo-ng     : github.com/nicocha30/ligolo-ng/releases"
echo "  - chisel        : github.com/jpillora/chisel/releases"
echo "  - evilginx2     : github.com/kgretzky/evilginx2"
echo "  - gophish       : getgophish.com"
echo "  - setoolkit     : sudo pacman -S set"
echo ""

echo -e "${GREEN}run ${RED}0day${GREEN} to start!${NC}"
