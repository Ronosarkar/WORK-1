# 🌐 How to Host Media Variant Studio 100% Free (No PC Needed)

This guide shows you how to run this tool online **24/7 without keeping your PC turned on**, at **$0 cost** and **without needing a credit card**.

---

## 🏆 Recommended: Hugging Face Spaces (Docker)
**Why this is the best free option:**
- **Cost:** $0.00 / Free forever
- **Credit Card:** **None required**
- **Hardware provided for free:** 2 vCPUs, **16 GB RAM**, 50 GB storage (plenty of power to encode 1080p videos quickly)
- **Result:** A permanent HTTPS link you can open on your phone anytime, anywhere.

---

### ⏱️ Quick 3-Minute Setup

#### **Step 1: Create a Free Hugging Face Account**
1. Go to [https://huggingface.co/join](https://huggingface.co/join) and create a free account (takes 30 seconds).

#### **Step 2: Create a New Space**
1. Click your profile icon at top-right and click **"New Space"** (or visit [https://huggingface.co/new-space](https://huggingface.co/new-space)).
2. Fill in:
   - **Space name:** `media-variant-studio` (or any name you like)
   - **License:** `mit` (or choose any)
   - **Select the Space SDK:** Choose **Docker**
   - **Choose a Docker template:** Select **Blank**
   - **Space Hardware:** Select **Free (2 vCPU · 16 GB RAM)**
   - **Public / Private:** Choose **Public** (or Private if you only want you to access it)
3. Click **"Create Space"**.

#### **Step 3: Upload the Project Files**
You can upload the files directly through the browser:
1. In your new Space, click on the **"Files"** tab at the top.
2. Click **"Add file"** ➔ **"Upload files"**.
3. Drag and drop these files and folders from `Copyright bypass tool`:
   - `Dockerfile`
   - `requirements-server.txt`
   - `server.py`
   - `core/` (folder containing all `.py` files)
   - `web/` (folder containing `templates/index.html`)
4. At the bottom, click **"Commit changes to main"**.

*(Alternative: If you use Git, you can simply clone the space repo and `git push` these files).*

#### **Step 4: Done! Your Online Studio is Live**
* Hugging Face will automatically build the container (takes about 1–2 minutes).
* Once the status turns to **"Running"**, you will see your web app live right in the browser!
* Click the **"Embed this space"** or expand icon at the top right to get the direct full-screen URL.

---

## 📱 How to Use It From Your Phone
1. Open the Space URL in **Safari (iPhone)** or **Chrome (Android)**.
2. (Optional Tip): Tap the browser share/menu icon and select **"Add to Home Screen"**. It will appear like a real native app on your phone.
3. Select any video from your phone, choose your presets, click **"Generate Variants"**, and download the finished videos straight to your phone.
4. **Your PC can stay completely turned off!** All the encoding is done by the cloud servers.

---

## 🛡️ Built-in Cloud Features
- **Auto-Disk Cleanup:** The server automatically deletes temporary uploaded and exported files older than 1 hour, so your cloud storage space never runs out.
- **Large File Support:** Allows media uploads up to 1 GB.
- **Dynamic Port Binding:** Automatically listens on the cloud container's designated port (`7860`).
