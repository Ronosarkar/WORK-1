# 🚀 100% Free Cloud Setup Guide (NO Docker Needed)

This guide takes **3 minutes** and puts your Media Studio online for **$0**, with **no credit card** and **NO DOCKER**. Your PC can stay completely turned off!

---

### Step 1: Create a Free Account on Render
1. Go to [https://render.com](https://render.com).
2. Click **"Get Started for Free"** (Sign up with GitHub or Google/email).
3. **No credit card is required.**

---

### Step 2: Push Your Code to GitHub
If your project is already in GitHub, skip to Step 3. Otherwise:
1. Create a new repository on [github.com](https://github.com) (e.g. `media-variant-studio`).
2. Push this folder to your repository:
   ```bash
   git init
   git add .
   git commit -m "Deploy Media Studio"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/media-variant-studio.git
   git push -u origin main
   ```

---

### Step 3: Launch Your Free Web Service on Render
1. On your Render dashboard, click **"New +"** (top-right) and select **"Web Service"**.
2. Connect your GitHub repository.
3. Configure these simple fields:
   - **Name:** `media-variant-studio` (or any name you want)
   - **Language:** **Python 3** *(Do NOT select Docker)*
   - **Region:** Any (e.g., Oregon or Frankfurt)
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     chmod +x render-build.sh && ./render-build.sh
     ```
   - **Start Command:**
     ```bash
     gunicorn -w 1 -k gthread --threads 4 --timeout 300 server:app
     ```
   - **Instance Type:** Select **Free** ($0 / month)
4. Click **"Create Web Service"**.

---

### Step 4: You Are Live!
* Render will spend 1–2 minutes setting up Python and downloading dependencies.
* At the top of your dashboard, Render will give you a permanent HTTPS link:
  ```plaintext
  https://media-variant-studio.onrender.com
  ```
* Open this link on your phone in Safari or Chrome.
* **Turn off your PC** — the app will keep running 24/7 on the cloud!
