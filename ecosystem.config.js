module.exports = {
  apps: [{
    name: 'dinov3-utilities',
    script: 'venv/bin/python',
    args: '-m uvicorn app.main:app --host 0.0.0.0 --port 3012',
    cwd: '/home/ubuntu/dinov3-utilities',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '2G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/home/ubuntu/dinov3-utilities'
    },
    env_production: {
      NODE_ENV: 'production',
      DEBUG: 'false'
    },
    log_date_format: 'YYYY-MM-DD HH:mm Z',
    error_file: '/home/ubuntu/dinov3-utilities/logs/pm2-error.log',
    out_file: '/home/ubuntu/dinov3-utilities/logs/pm2-out.log',
    log_file: '/home/ubuntu/dinov3-utilities/logs/pm2-combined.log',
    time: true
  }]
};
