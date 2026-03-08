# How to Deploy to Render (Manual / Free Tier)

This folder (`render_deploy`) contains the clean, production-ready version of your app. 
Since Render's "Blueprint" feature requires payment, you can easily deploy these 3 services manually for **free**!

## Step 1: Upload to GitHub
1. Create a new, empty repository on [GitHub](https://github.com/).
2. Upload all the files inside this `render_deploy` folder to that repository.

## Step 2: Deploy PostgreSQL Database (Free)
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **PostgreSQL**.
3. Name it `ai-dashboard-db`.
4. Select the **Free** instance type.
5. Click **Create Database**.
6. Once created, copy the **Internal Database URL** (for the backend) and **External Database URL** (for your local terminal later).

## Step 3: Deploy FastAPI Backend (Free)
1. Go back to the dashboard, click **New +** and select **Web Service**.
2. Connect your GitHub repository.
3. Configure the backend:
   - **Name:** `ai-dashboard-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
4. Scroll down to **Environment Variables** and add:
   - Key: `PYTHON_VERSION` | Value: `3.11.0` *(Required to fix psycopg2 error)*
   - Key: `GEMINI_API_KEY` | Value: *(Your actual Gemini API key)*
   - Key: `GEMINI_MODEL` | Value: `gemini-2.5-flash`
   - Key: `DATABASE_URL` | Value: *(Paste the **Internal** Database URL you copied in Step 2)*
5. Click **Create Web Service**.

## Step 4: Deploy Next.js Frontend (Free)
1. Go back to the dashboard, click **New +** and select **Web Service**.
2. Connect your GitHub repository again.
3. Configure the frontend:
   - **Name:** `ai-dashboard-frontend`
   - **Root Directory:** `frontend`
   - **Environment:** `Node`
   - **Build Command:** `rm -rf .next && npm install && npm run build`
   - **Start Command:** `npm start`
   - **Instance Type:** Free
4. Scroll down to **Environment Variables** and add:
   - Key: `NEXT_PUBLIC_API_URL` | Value: *(Paste the URL of your backend from Step 3, e.g., https://ai-dashboard-backend-xxxx.onrender.com)*
5. Click **Create Web Service**.

## Step 5: Populate the Remote Database
Your database on Render will be empty. To load your 130MB e-commerce data into it:
1. Open your *local* machine's `.env` file (the one in your original project folder, not here).
2. Temporarily change `DATABASE_URL` to your new Render **External Database URL**.
3. Run your python script locally: `python data_pipeline.py`.
4. Sit back and watch it upload your 1.5 million rows over the internet into your new Render database! (This may take roughly 2-5 minutes).

Once everything is deployed and the data is uploaded, click the URL for your `ai-dashboard-frontend` to use your live AI Dashboard!
