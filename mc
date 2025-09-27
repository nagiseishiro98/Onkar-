#!/bin/bash
# PaperMC Auto Setup & Run Script

# Server folder (current directory assumed)
SERVER_DIR=$(pwd)

# PaperMC jar download URL
PAPER_URL="https://api.papermc.io/v2/projects/paper/versions/1.20.1/builds/196/downloads/paper-1.20.1-196.jar"
JAR_NAME="paper.jar"

# Check if jar exists, if not download
if [ ! -f "$SERVER_DIR/$JAR_NAME" ]; then
    echo "[+] PaperMC jar not found, downloading..."
    wget -O "$SERVER_DIR/$JAR_NAME" "$PAPER_URL"
fi

# Auto accept EULA
echo "eula=true" > "$SERVER_DIR/eula.txt"
echo "[+] EULA accepted"

# Enable cracked/offline mode in server.properties
if [ ! -f "$SERVER_DIR/server.properties" ]; then
    cat > "$SERVER_DIR/server.properties" <<EOF
server-port=25565
online-mode=false
motd=Codespaces/Termux Server
EOF
    echo "[+] server.properties created (offline mode)"
else
    sed -i 's/online-mode=.*/online-mode=false/' "$SERVER_DIR/server.properties" || echo "online-mode=false" >> "$SERVER_DIR/server.properties"
    echo "[+] offline mode enabled in existing server.properties"
fi

# Check Java
if ! command -v java &> /dev/null; then
    echo "Java not found! Please install Java (OpenJDK 17+)"
    exit 1
fi

# Run server
echo "[+] Starting PaperMC server..."
java -Xmx4G -Xms2G -jar "$SERVER_DIR/$JAR_NAME" nogui
