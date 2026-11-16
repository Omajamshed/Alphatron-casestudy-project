# 🚀 ContractGuard Vercel Deployment Guide

This guide provides end-to-end instructions for deploying **ContractGuard** on **Vercel** with zero friction.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Omajamshed/Alphatron-casestudy-project)

---

## 🏗️ Deployment Architecture Overview

ContractGuard is architected to support two deployment patterns on Vercel:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VERCEL EDGE NETWORK (CDN)                       │
│  React 19 + TypeScript + Vite Single Page Application                  │
│  • Instant Global Edge Cache           • Client-Side SPA Routing       │
│  • Clean URLs & Security Headers       • Automatic HTTPS / SSL         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┴────────────────────────────┐
       ▼ (Pattern A - Recommended)                               ▼ (Pattern B)
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│ DEDICATED BACKEND (Railway / Render) │       │ VERCEL SERVERLESS PYTHON FUNCTIONS   │
│ FastAPI + LangGraph + PostgreSQL/pgv │       │ api/index.py via @vercel/python      │
│ • Persistent Checkpointing (DB)      │       │ • Stateless execution                │
│ • Long-running Agent Evaluation      │       │ • Lightweight serverless endpoints   │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
```

---

## ⚡ Option 1: Vercel Dashboard (Recommended & Easiest)

### Step 1: Push Repository to GitHub
Ensure all your files and the new `vercel.json` are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "feat: add vercel deployment configuration and guides"
git push origin main
```

### Step 2: Import Project in Vercel
1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** → **"Project"**.
3. Import your repository: **`Omajamshed/Alphatron-casestudy-project`**.

### Step 3: Configure Build & Project Settings

Depending on whether you deploy the whole repository or just the frontend:

#### Approach A: Deploying from Root Repository (`Alphatron-casestudy-project`)
- **Framework Preset:** `Vite`
- **Root Directory:** `./` (Leave as default root)
- **Build Command:** `cd contractguard/frontend && npm install && npm run build`
- **Output Directory:** `contractguard/frontend/dist`
- **Install Command:** `npm --version` *(or leave default)*

#### Approach B: Setting Root Directory to Frontend (Cleanest)
- In the project configuration screen, next to **Root Directory**, click **Edit**.
- Select **`contractguard/frontend`**.
- Vercel automatically detects **Vite**!
  - **Build Command:** `npm run build`
  - **Output Directory:** `dist`
  - **Install Command:** `npm install`

### Step 4: Configure Environment Variables
Under **Environment Variables**, add:
| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://your-backend.up.railway.app` | Base URL of your deployed FastAPI backend. If empty, defaults to `/api/v1`. |

### Step 5: Deploy!
Click **"Deploy"**. Within 60 seconds, your site is live with a secure `*.vercel.app` domain!

---

## 💻 Option 2: Deploy Using the Vercel CLI

You can also deploy directly from your local terminal using the Vercel CLI:

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy Frontend Directly
```bash
cd contractguard/frontend

# Preview deployment
vercel

# Production deployment
vercel --prod
```

When prompted:
- Set up and deploy? **`Y`**
- Which scope? **`<your-team-or-username>`**
- Link to existing project? **`N`**
- What's your project's name? **`contractguard`**
- In which directory is your code located? **`./`**
- Want to modify these settings? **`N`** (the provided `vercel.json` handles everything automatically)

---

## 🛠️ Included Vercel Configuration Files

The project contains pre-configured `vercel.json` files tailored for each deployment scope:

### 1. `contractguard/frontend/vercel.json`
Ensures that all client-side routes (e.g., `/contracts/1`, `/review/2`, `/history`) rewrite correctly to `/index.html` without returning 404 errors, and sets production caching headers on Vite assets:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### 2. Monorepo Config (`contractguard/vercel.json` & root `vercel.json`)
Allows deploying from the parent directory by automatically routing the build command to `frontend`.

### 3. Python Serverless Entrypoint (`contractguard/api/index.py`)
Provides an ASGI serverless handler adapting the FastAPI application for Vercel's Python runtime.

---

## 🌐 Deploying the Backend (Complementary to Vercel)

Since ContractGuard utilizes **LangGraph stateful checkpoints**, **pgvector embeddings**, and **ReportLab PDF generation**, the backend runs best on a containerized service. Recommended free/low-cost platforms:

### Option A: Railway (1-Click)
1. Go to [railway.app](https://railway.app) and click **"New Project"** → **"Deploy from GitHub repo"**.
2. Set the root directory to `contractguard/backend`.
3. Add a **PostgreSQL** database service (with pgvector extension enabled).
4. Set environment variables:
   ```env
   DATABASE_URL=postgresql://postgres:...
   JWT_SECRET=your_super_secret_jwt_key_here
   ```
5. Copy the generated Railway URL (e.g. `https://contractguard-backend.up.railway.app`) and paste it as `VITE_API_BASE_URL` in your Vercel project settings!

### Option B: Render
1. Go to [render.com](https://render.com) and create a **Web Service**.
2. Connect your repository, select **Docker** or **Python**, and point root directory to `contractguard/backend`.
3. Add your environment variables and copy the Render service URL to Vercel.

---

## 🔍 Troubleshooting Vercel Deployments

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **404 on Page Refresh** | Client-side routing not rewritten to `index.html`. | Verify that `vercel.json` contains `"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]`. |
| **CORS Errors When Calling API** | Backend does not allow the Vercel domain. | In `backend/app/main.py`, `CORSMiddleware` already allows `*`. Ensure your backend is running with HTTPS. |
| **API Calls Going to `localhost:8000`** | `VITE_API_BASE_URL` not set on Vercel. | Add `VITE_API_BASE_URL=https://your-backend-url.com` in Vercel Project Settings → Environment Variables and redeploy. |
| **Build Fails with `dist not found`** | Output directory mismatch. | Ensure output directory is set to `dist` (or `contractguard/frontend/dist` if building from root). |
