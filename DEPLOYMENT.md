# DINOv3 Utilities - Production Deployment Guide

## 🚀 Production Deployment Checklist

### Prerequisites
- [ ] **Server**: Ubuntu 20.04+ or Windows Server with NVIDIA GPU
- [ ] **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 4060 Ti 16GB recommended)
- [ ] **RAM**: 16GB+ system memory
- [ ] **Storage**: 50GB+ free space
- [ ] **Network**: Stable internet connection for initial setup

### Infrastructure Requirements
- [ ] **MongoDB**: Local or cloud instance (MongoDB Atlas recommended)
- [ ] **Redis**: Local or cloud instance for caching
- [ ] **Cloudflare R2**: Bucket configured with API credentials
- [ ] **Domain**: Optional, for custom API endpoint

## 📋 Step-by-Step Deployment

### 1. Server Setup

#### Ubuntu/Linux
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Install NVIDIA drivers (if not already installed)
sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit

# Install system dependencies
sudo apt install -y git curl wget build-essential
```

#### Windows Server
```powershell
# Install Python 3.12 from python.org
# Install NVIDIA drivers and CUDA toolkit
# Install Git for Windows
```

### 2. Application Deployment

```bash
# Clone repository
git clone <your-repository-url> /opt/dinov3-utilities
cd /opt/dinov3-utilities

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify GPU support
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**
```env
# Database
MONGODB_URL=mongodb://localhost:27017/dinov3_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2
CLOUDFLARE_R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=your_bucket_name
CLOUDFLARE_R2_PUBLIC_URL=https://your-domain.com

# Model Configuration
DINOV3_MODEL_NAME=models/dinov3-vitb16-pretrain-lvd1689m
DINOV3_DEVICE=cuda
DINOV3_BATCH_SIZE=32

# API Configuration
API_HOST=0.0.0.0
API_PORT=3012

# Hugging Face Token
HF_TOKEN=your_hugging_face_token
```

### 4. Database Setup

#### MongoDB
```bash
# Install MongoDB (Ubuntu)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### Redis
```bash
# Install Redis (Ubuntu)
sudo apt install -y redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 5. Model Setup

```bash
# Ensure model files are in place
ls -la models/dinov3-vitb16-pretrain-lvd1689m/

# If model files are missing, they will be downloaded automatically
# on first startup (requires HF_TOKEN)
```

### 6. Service Configuration

Create systemd service file:
```bash
sudo nano /etc/systemd/system/dinov3-service.service
```

```ini
[Unit]
Description=DINOv3 Utilities Service
After=network.target mongod.service redis-server.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dinov3-utilities
Environment=PATH=/opt/dinov3-utilities/venv/bin
ExecStart=/opt/dinov3-utilities/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 3012
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dinov3-service
sudo systemctl start dinov3-service
```

### 7. Reverse Proxy Setup (Optional)

#### Nginx Configuration
```bash
sudo apt install -y nginx

# Create site configuration
sudo nano /etc/nginx/sites-available/dinov3-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3012;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dinov3-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 Verification & Testing

### Health Check
```bash
# Check service status
sudo systemctl status dinov3-service

# Test API endpoint
curl http://localhost:3012/api/v1/health

# Check logs
sudo journalctl -u dinov3-service -f
```

### API Documentation
- **Local**: http://localhost:3012/docs
- **Production**: http://your-domain.com/docs

## 📊 Monitoring Setup

### Log Management
```bash
# View service logs
sudo journalctl -u dinov3-service -f

# View system logs
sudo tail -f /var/log/syslog
```

### Performance Monitoring
```bash
# GPU monitoring
nvidia-smi -l 1

# System resources
htop

# Service metrics
curl http://localhost:3012/api/v1/health
```

## 🔒 Security Considerations

### Firewall Configuration
```bash
# Allow SSH and API port
sudo ufw allow 22
sudo ufw allow 3012
sudo ufw enable
```

### SSL/TLS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
sudo journalctl -u dinov3-service -n 50

# Check dependencies
source /opt/dinov3-utilities/venv/bin/activate
pip check
```

**GPU not detected:**
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify CUDA installation
nvcc --version
```

**Database connection issues:**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
mongo --eval "db.adminCommand('ping')"
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use Redis Cluster for distributed caching
- Implement database read replicas

### Vertical Scaling
- Upgrade to higher-end GPU (RTX 4090, A100)
- Increase system RAM for larger batch processing
- Use NVMe storage for faster model loading

---

**🎉 Your DINOv3 Utilities Service is now ready for production!**

For support and updates, refer to the main README.md and API documentation.
