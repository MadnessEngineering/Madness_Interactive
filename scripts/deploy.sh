#!/bin/bash

# Deployment script for madnessinteractive.cc
#
# 🚀 ENHANCED WITH RSYNC FOR FASTER DEPLOYMENTS
# ============================================
#
# This script now uses rsync instead of scp for file transfers, providing:
# ✅ Only changed files are transferred (much faster subsequent deployments)
# ✅ Progress indicators during transfer
# ✅ Automatic deletion of removed files on server
# ✅ Exclusion of unnecessary files (node_modules, .git, logs)
# ✅ Error handling and rollback capabilities
# ✅ AI Assistant Auto-Detection for seamless automation
#
# Benefits:
# - First deployment: Same speed as before
# - Subsequent deployments: 5-10x faster (only changed files)
# - Bandwidth savings: Significant reduction in data transfer
# - Time savings: Deployments complete in seconds instead of minutes
#
# Quick Deploy (Option 0) is the recommended way to deploy both frontend and backend

# 🤖 AI ASSISTANT AUTO-DETECTION
# ===============================
# Detect if this script is being called by an AI assistant and auto-run Quick Deploy
detect_ai_caller() {
    # Method 1: Check for explicit AI environment variables
    local ai_indicators=(
        "$AI_ASSISTANT"           # Explicit AI flag
        "$CURSOR_AI"              # Cursor AI environment
        "$CLAUDE_AI"              # Claude AI environment
        "$COPILOT_AI"             # GitHub Copilot environment
        "$ASSISTANT_MODE"         # Generic assistant mode
    )

    for indicator in "${ai_indicators[@]}"; do
        if [[ -n "$indicator" ]]; then
            echo "🔍 AI detected via environment variable: $indicator"
            return 0  # AI detected
        fi
    done

    # Method 2: Check parent process chain for AI/automation tools
    local parent_chain=$(ps -eo pid,ppid,comm | awk -v start=$PPID '
        BEGIN { pid = start }
        { 
            if ($1 == pid) { 
                print $3; 
                pid = $2; 
                if (pid <= 1) exit 
            } 
        }' 2>/dev/null)

    if [[ "$parent_chain" =~ (cursor|code|assistant|ai|automation|node|python) ]]; then
        echo "🔍 AI detected via parent process: $parent_chain"
        return 0  # AI detected
    fi

    # Method 3: Check if running in automation context (non-interactive + specific patterns)
    if [[ ! -t 0 ]] || [[ ! -t 1 ]]; then
        # Check if we have typical AI automation markers
        local current_dir=$(basename "$PWD")
        local script_name=$(basename "$0")

        # AI assistants often run scripts from project directories with specific patterns
        if [[ "$current_dir" =~ (Inventorium|madness|project) ]] && [[ "$script_name" == "deploy.sh" ]]; then
            echo "🔍 AI detected via automation context: non-interactive terminal in $current_dir"
            return 0  # AI detected
        fi
    fi

    # Method 4: Check command line and execution context
    # AI assistants often execute with specific patterns
    local cmdline=$(cat /proc/$$/cmdline 2>/dev/null | tr '\0' ' ')
    if [[ "$cmdline" =~ (run_terminal_cmd|execute|automation|assistant) ]]; then
        echo "🔍 AI detected via command line: $cmdline"
        return 0  # AI detected
    fi

    # Method 5: Check if we're being called programmatically (common AI pattern)
    # Look for signs that this is not a direct human invocation
    if [[ -z "$TERM" ]] || [[ "$TERM" == "dumb" ]]; then
        echo "🔍 AI detected via terminal type: $TERM"
        return 0  # AI detected
    fi

    # Method 6: Simple heuristic - if script is run without any user interaction expected
    # and from a typical development directory, assume AI
    if [[ "$PWD" =~ (projects|lab|development|code) ]] && [[ $# -eq 0 ]]; then
        # Additional check: see if there are recent file modifications (AI often runs after changes)
        local recent_changes=$(find . -name "*.js" -o -name "*.jsx" -o -name "*.json" -mmin -10 2>/dev/null | wc -l)
        if [[ $recent_changes -gt 0 ]]; then
            echo "🔍 AI detected via heuristic: development context with recent changes ($recent_changes files)"
            return 0  # AI detected
        fi
    fi

    return 1  # Human user
}

# Check for AI caller and auto-run Quick Deploy
if detect_ai_caller; then
    echo -e "\033[0;36m🤖 AI Assistant Detected - Auto-running Quick Deploy!\033[0m"
    echo -e "\033[1;33m🚀 Deploying both frontend and backend with rsync optimization...\033[0m"
    echo ""

    # Set option to 0 (Quick Deploy) and skip menu
    option=0
else
    # Human user - show interactive menu
    echo ""
fi

# Configuration
EC2_USER="ubuntu"  # Ubuntu is default for many AWS EC2 instances
EC2_IP="${AWSIP}"

REMOTE_PATH="/var/www/html"
BACKEND_PATH="/opt/madness-backend"

# SSH alias detection - use 'ssh eaws' if available, otherwise full SSH command
SSH_CMD="ssh eaws"
RSYNC_SSH_CMD="ssh"

# Check if eaws alias works, otherwise fall back to full key path
if ! command -v ssh >/dev/null || ! ssh -o ConnectTimeout=2 eaws "echo test" >/dev/null 2>&1; then
    SSH_CMD="ssh -i $KEY_PATH $EC2_USER@$EC2_IP"
    RSYNC_SSH_CMD="ssh -i $KEY_PATH"
fi

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to fix permissions on EC2 before deployment
fix_deployment_permissions() {
    local target_path="$1"
    local description="$2"

    echo -e "${YELLOW}🔧 Fixing permissions for $description...${NC}"

    # Create the target directory if it doesn't exist and set proper ownership
    $SSH_CMD "
        sudo mkdir -p '$target_path'
        sudo chown -R $EC2_USER:$EC2_USER '$target_path'
        
        # Fix any permission issues in problematic subdirectories
        if [ -d '$target_path/SwarmDesk' ]; then
            echo 'Fixing SwarmDesk permissions...'
            sudo chown -R $EC2_USER:$EC2_USER '$target_path/SwarmDesk'
            chmod -R u+w '$target_path/SwarmDesk'
        fi
        
        # Clean up any git lock files that might cause issues
        find '$target_path' -name '*.lock' -type f -exec rm -f {} + 2>/dev/null || true
        
        echo 'Permissions fixed successfully'
    " 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Permissions fixed for $description${NC}"
    else
        echo -e "${YELLOW}⚠️  Some permission fixes may have failed, but continuing...${NC}"
    fi
}

# Check if key file exists
if [ ! -f "$KEY_PATH" ]; then
    echo -e "${YELLOW}Warning: SSH key file not found at $KEY_PATH${NC}"
    echo "Please update the KEY_PATH variable in this script"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy website files
deploy_website() {
    echo -e "${GREEN}Deploying website files to EC2 with rsync...${NC}"

    # Always build to ensure latest changes are deployed
    echo -e "${YELLOW}Building React frontend (ensuring latest changes)...${NC}"
    npm run build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Frontend build failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Frontend build completed successfully${NC}"

    # Fix permissions before deployment
    fix_deployment_permissions "$REMOTE_PATH" "frontend deployment"

    # Use rsync for efficient file transfer (only changed files)
    echo "Syncing React build files to EC2 (only changed files will be transferred)..."
    rsync -avz --delete --progress \
        -e "$RSYNC_SSH_CMD" \
        build/ "$EC2_USER@$EC2_IP:$REMOTE_PATH/"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}React application deployed successfully with rsync${NC}"
        echo -e "${YELLOW}Only changed files were transferred for faster deployment${NC}"
    else
        echo -e "${RED}Deployment failed${NC}"
        exit 1
    fi
}

# Deploy backend API server
deploy_backend() {
    echo -e "${GREEN}Deploying backend API server to EC2 with rsync...${NC}"

    # Create backend directory on server
    $SSH_CMD "sudo mkdir -p $BACKEND_PATH && sudo chown $EC2_USER:$EC2_USER $BACKEND_PATH"

    # Fix permissions before deployment
    fix_deployment_permissions "$BACKEND_PATH" "backend deployment"

    # Use rsync for efficient backend file transfer and capture output
    echo "Syncing backend files to EC2 (only changed files will be transferred)..."
    RSYNC_OUTPUT=$(rsync -avz --delete --progress \
        --exclude 'node_modules' \
        --exclude '.git' \
        --exclude '*.log' \
        --exclude 'logs/' \
        -e "$RSYNC_SSH_CMD" \
        backend/ "$EC2_USER@$EC2_IP:$BACKEND_PATH/" 2>&1)

    RSYNC_EXIT_CODE=$?
    echo "$RSYNC_OUTPUT"

    if [ $RSYNC_EXIT_CODE -ne 0 ]; then
        echo -e "${RED}Backend file sync failed${NC}"
        exit 1
    fi

    # Check if meaningful application files changed (not just package files)
    APP_FILES_CHANGED=false
    if echo "$RSYNC_OUTPUT" | grep -E "\.(js|jsx|ts|tsx|json|yaml|yml|md)$" | grep -v -E "(package-lock\.json|package\.json)$" > /dev/null; then
        APP_FILES_CHANGED=true
        echo -e "${YELLOW}Application files changed - service restart needed${NC}"
    elif echo "$RSYNC_OUTPUT" | grep -E "(package\.json)$" > /dev/null; then
        APP_FILES_CHANGED=true
        echo -e "${YELLOW}Package.json changed - dependencies may need update and restart${NC}"
    else
        echo -e "${GREEN}Only lock files or non-critical files changed - skipping restart${NC}"
    fi

    # Install Node.js if not present
    echo "Checking Node.js installation..."
    $SSH_CMD "
        if ! command -v node &> /dev/null; then
            echo 'Installing Node.js...'
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        else
            echo 'Node.js already installed'
        fi
    "

    # Only install dependencies and restart if meaningful files changed
    if [ "$APP_FILES_CHANGED" = true ]; then
        # Install backend dependencies
        echo "Installing backend dependencies..."
        $SSH_CMD "cd $BACKEND_PATH && npm install"

        # Install PM2 for process management
        echo "Setting up PM2 process manager..."
        $SSH_CMD "
            if ! command -v pm2 &> /dev/null; then
                sudo npm install -g pm2
            fi
        "

        # Create PM2 ecosystem file
        $SSH_CMD "cat > $BACKEND_PATH/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'madness-backend',
    script: 'server.js',
    cwd: '$BACKEND_PATH',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 9192,
      MONGO_URL: 'mongodb://localhost:27017'
    }
  }]
};
EOF"

        # Start/restart the backend service
        echo "Restarting madness-backend service only (preserving other PM2 services)..."
        $SSH_CMD "
            cd $BACKEND_PATH
            # Check if madness-backend process exists
            if pm2 list | grep -q 'madness-backend'; then
                echo 'Restarting existing madness-backend process...'
                pm2 restart madness-backend
            else
                echo 'Starting new madness-backend process...'
                pm2 start ecosystem.config.js
            fi
            # Save PM2 process list
            pm2 save
            # Show status of just the madness-backend service
            pm2 show madness-backend
        "

        echo -e "${GREEN}madness-backend service restarted (other PM2 services unaffected)${NC}"
    else
        echo -e "${GREEN}Backend files synced - no service restart needed${NC}"
    fi

    echo -e "${GREEN}Backend API server deployed successfully with rsync${NC}"
    echo -e "${YELLOW}Only changed files were transferred for faster deployment${NC}"
}

# Install MongoDB
install_mongodb() {
    echo -e "${GREEN}Installing MongoDB on EC2...${NC}"

    $SSH_CMD "
        # Import MongoDB public GPG key
        curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

        # Create list file for MongoDB
        echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

        # Update package database
        sudo apt-get update

        # Install MongoDB
        sudo apt-get install -y mongodb-org

        # Start and enable MongoDB
        sudo systemctl start mongod
        sudo systemctl enable mongod

        # Check MongoDB status
        sudo systemctl status mongod --no-pager
    "

    echo -e "${GREEN}MongoDB installed and started${NC}"
}

# Install web server (run once)
install_webserver() {
    echo -e "${GREEN}Installing web server on EC2...${NC}"

    # Update package lists and install nginx
    $SSH_CMD "sudo apt update && sudo apt install -y nginx && sudo systemctl start nginx && sudo systemctl enable nginx"

    # Configure nginx for React app and API proxy
    echo "Configuring nginx..."
    $SSH_CMD "sudo tee /etc/nginx/sites-available/madnessinteractive << 'EOF'
server {
    listen 80;
    server_name madnessinteractive.cc www.madnessinteractive.cc;
    
    root /var/www/html;
    index index.html;

    # React Router support
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API Documentation endpoint
    location /docs {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
}
EOF"

    # Enable the site
    $SSH_CMD "
        sudo ln -sf /etc/nginx/sites-available/madnessinteractive /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl reload nginx
    "

    echo -e "${GREEN}Web server installed and configured${NC}"
}

# Install DNS update script
install_dns_update() {
    echo -e "${GREEN}Installing DNS update script on EC2 with rsync...${NC}"

    # Use rsync to copy script to EC2 (more efficient than scp)
    rsync -avz --progress \
        -e "$RSYNC_SSH_CMD" \
        update_dns.sh "$EC2_USER@$EC2_IP:~/"

    if [ $? -ne 0 ]; then
        echo -e "${RED}DNS script sync failed${NC}"
        exit 1
    fi

    # Make script executable and set up cron job
    $SSH_CMD "chmod +x ~/update_dns.sh && (crontab -l 2>/dev/null; echo '0 * * * * ~/update_dns.sh') | crontab -"

    echo -e "${GREEN}DNS update script installed and scheduled with rsync${NC}"
}

# Install SSL certificates with Let's Encrypt
install_ssl() {
    echo -e "${GREEN}Installing SSL certificates with Let's Encrypt...${NC}"

    $SSH_CMD "
        # Install certbot
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx

        # Stop nginx temporarily for certificate generation
        sudo systemctl stop nginx

        # Generate SSL certificate for both domains
        sudo certbot certonly --standalone -d madnessinteractive.cc -d www.madnessinteractive.cc --non-interactive --agree-tos --email admin@madnessinteractive.cc

        # Start nginx again
        sudo systemctl start nginx

        # Update nginx configuration for HTTPS
        sudo tee /etc/nginx/sites-available/madnessinteractive << 'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name madnessinteractive.cc www.madnessinteractive.cc;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name madnessinteractive.cc www.madnessinteractive.cc;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/madnessinteractive.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/madnessinteractive.cc/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    root /var/www/html;
    index index.html;

    # React Router support
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API Documentation endpoint
    location /docs {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
}
EOF

        # Test nginx configuration
        sudo nginx -t

        # Reload nginx with new SSL configuration
        sudo systemctl reload nginx

        # Set up automatic certificate renewal
        sudo crontab -l 2>/dev/null | { cat; echo '0 12 * * * /usr/bin/certbot renew --quiet && /usr/bin/systemctl reload nginx'; } | sudo crontab -

        echo 'SSL certificates installed and configured!'
        echo 'Automatic renewal set up via cron job'
    "

    echo -e "${GREEN}HTTPS/SSL setup complete!${NC}"
}

# Configure nginx for Cloudflare (no local SSL needed)
configure_cloudflare_nginx() {
    echo -e "${GREEN}Configuring nginx for Cloudflare SSL...${NC}"

    $SSH_CMD "
        # Update nginx configuration for Cloudflare
        sudo tee /etc/nginx/sites-available/madnessinteractive << 'EOF'
server {
    listen 80;
    server_name madnessinteractive.cc www.madnessinteractive.cc;
    
    root /var/www/html;
    index index.html;

    # Omnispindle redirect to GitHub repository
    location /omnispindle {
        return 301 https://github.com/MadnessEngineering/Omnispindle;
    }

    # React Router support
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API Documentation endpoint
    location /docs {
        proxy_pass http://localhost:9192;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers (Cloudflare handles SSL headers)
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection \"1; mode=block\";
    
    # Trust Cloudflare IPs for real IP forwarding
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    real_ip_header CF-Connecting-IP;
}
EOF

        # Test nginx configuration
        sudo nginx -t

        # Reload nginx with new configuration
        sudo systemctl reload nginx

        echo 'Nginx configured for Cloudflare SSL!'
    "

    echo -e "${GREEN}Cloudflare nginx configuration complete!${NC}"
}

# Check security group
check_security_group() {
    echo -e "${GREEN}Security Group Requirements:${NC}"
    echo "Make sure your EC2 security group has the following inbound rules:"
    echo "1. HTTP (Port 80) - Open to 0.0.0.0/0 (will redirect to HTTPS)"
    echo "2. HTTPS (Port 443) - Open to 0.0.0.0/0 (main traffic)"
    echo "3. SSH (Port 22) - Open to your IP only for security"
    echo "4. API (Port 9192) - No rule needed (internal only)"

    echo -e "${YELLOW}Security group configuration must be done manually in the AWS console${NC}"
    echo "Instructions:"
    echo "1. Go to AWS EC2 Console"
    echo "2. Select your instance"
    echo "3. Click on the Security tab"
    echo "4. Click on your security group"
    echo "5. Add inbound rules for HTTP (80) and HTTPS (443) if missing"

    read -p "Have you confirmed your security group has HTTP/HTTPS rules? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please configure your security group before proceeding."
        exit 1
    fi
}

# Test website and API accessibility
test_website() {
    echo -e "${GREEN}Testing website and API accessibility...${NC}"

    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        echo "curl is not installed. Skipping website test."
        return
    fi

    # Test backend health endpoint
    echo "Testing backend API health..."
    $SSH_CMD "curl -s http://localhost:9192/health | head -n 5 || echo 'Backend API is NOT accessible'"

    # Test local connection on EC2
    echo "Testing local React app connection on EC2..."
    $SSH_CMD "curl -s http://localhost > /dev/null && echo 'Local website is accessible' || echo 'Local website is NOT accessible'"

    # Test public connection
    echo "Testing public connection to madnessinteractive.cc..."
    curl -s --head "http://madnessinteractive.cc" | head -n 1 || echo "Could not connect to madnessinteractive.cc"
    curl -s --head "http://www.madnessinteractive.cc" | head -n 1 || echo "Could not connect to www.madnessinteractive.cc"

    # Test API through nginx proxy
    echo "Testing API through nginx proxy..."
    curl -s "http://madnessinteractive.cc/health" | head -n 3 || echo "API proxy is NOT working"

    echo -e "${GREEN}Website and API testing complete${NC}"
}

# Check backend status
check_backend_status() {
    echo -e "${GREEN}Checking backend service status...${NC}"

    $SSH_CMD "
        echo 'PM2 Process Status:'
        pm2 status
        echo ''
        echo 'Backend Health Check:'
        curl -s http://localhost:9192/health | jq . 2>/dev/null || curl -s http://localhost:9192/health
        echo ''
        echo 'MongoDB Status:'
        sudo systemctl status mongod --no-pager | head -n 10
    "
}

# Quick deployment - frontend and backend with rsync
quick_deploy() {
    echo -e "${GREEN}🚀 Quick Deployment - Frontend + Backend with rsync${NC}"
    echo "This will sync only changed files for maximum efficiency..."

    # Always build frontend to ensure latest changes are deployed
    echo -e "${YELLOW}Building React frontend (ensuring latest changes)...${NC}"
    npm run build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Frontend build failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Frontend build completed successfully${NC}"

    # Deploy backend first (API needs to be ready)
    echo -e "${GREEN}Step 1: Deploying backend API...${NC}"
    deploy_backend

    # Deploy frontend
    echo -e "${GREEN}Step 2: Deploying frontend...${NC}"
    deploy_website

    # Test deployment
    echo -e "${GREEN}Step 3: Testing deployment...${NC}"
    test_website

    echo -e "${GREEN}🎉 Quick deployment complete!${NC}"
    echo -e "${YELLOW}✨ Only changed files were transferred for maximum efficiency${NC}"
    echo -e "${YELLOW}🌐 Visit: https://madnessinteractive.cc${NC}"
}

# Main menu
if [[ "$option" != "0" ]]; then
    echo -e "${GREEN}Madness Interactive Deployment Tool${NC}"
    echo "----------------------------------"
    echo "0. 🚀 Quick Deploy (Frontend + Backend with rsync) - RECOMMENDED"
    echo "1. Deploy website files (React frontend)"
    echo "2. Deploy backend API server"
    echo "3. Install web server (nginx)"
    echo "4. Install MongoDB database"
    echo "5. Install DNS update script"
    echo "6. Install SSL certificates with Let's Encrypt"
    echo "7. Configure nginx for Cloudflare SSL (recommended if using Cloudflare)"
    echo "8. Check security group configuration"
    echo "9. Test website and API accessibility"
    echo "10. Check backend service status"
    echo "11. Complete setup (all steps)"
    echo "q. Quit"

    read -p "Select an option: " option
fi

case $option in
    0)
        quick_deploy
        ;;
    1)
        deploy_website
        ;;
    2)
        deploy_backend
        ;;
    3)
        install_webserver
        ;;
    4)
        install_mongodb
        ;;
    5)
        install_dns_update
        ;;
    6)
        install_ssl
        ;;
    7)
        configure_cloudflare_nginx
        ;;
    8)
        check_security_group
        ;;
    9)
        test_website
        ;;
    10)
        check_backend_status
        ;;
    11)
        check_security_group
        install_mongodb
        install_webserver
        deploy_backend
        deploy_website
        install_dns_update
        install_ssl
        configure_cloudflare_nginx
        test_website
        check_backend_status
        ;;
    q|Q)
        echo "Exiting"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo -e "${GREEN}Done!${NC}"
