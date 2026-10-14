module.exports = {
  apps: [
    {
      name: "bhopal-backend",
      cwd: __dirname,   // keep this file in D:\RAS-7277\Bhopal\Bhopal_backend, next to main.py D:\RAS-7277\Bhopal\Bhopal_backend\app.py

      script: "./py-env/Scripts/python.exe",
      args: "-m uvicorn main:app --host 0.0.0.0 --port 8000",
      interpreter: "none",   // stops PM2 from running Python through Node

      autorestart: true,
      watch: false,
      env: {
        ENV: "local",
        // add your env vars here (DB URL, JWT secret, etc.)
      },
    },
  ],
};