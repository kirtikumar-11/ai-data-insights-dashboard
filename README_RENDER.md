# How to Deploy to Render

This folder (`render_deploy`) contains the clean, production-ready version of your app. 
It includes a `render.yaml` Blueprint which automatically configures your Frontend, Backend, and a Managed PostgreSQL Database for you!

## Step 1: Upload to GitHub
1. Create a new, empty repository on [GitHub](https://github.com/).
2. Upload all the files inside this `render_deploy` folder to that repository.
   *(Make sure the `render.yaml` is in the main root of your GitHub repo!)*

## Step 2: Deploy on Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub account and select the repository you just created.
4. Render will automatically read the `render.yaml` file and start building your 3 services:
   - `ai-dashboard-db` (PostgreSQL)
   - `ai-dashboard-backend` (FastAPI)
   - `ai-dashboard-frontend` (Next.js)
5. **CRITICAL:** Before the backend can run successfully, go to the **Environment** tab of `ai-dashboard-backend` in the Render dashboard and add your `GEMINI_API_KEY`!

## Step 3: Populate the Remote Database
Your database on Render will be empty. To load your 130MB e-commerce data into it:
1. Go to the `ai-dashboard-db` in your Render dashboard and copy the **External Database URL**.
2. Open your *local* machine's `.env` file (the one in your original project folder, not here).
3. Temporarily change `DATABASE_URL` to your new Render External Database URL.
4. Run your python script locally: `python data_pipeline.py`.
5. Sit back and watch it upload your 1.5 million rows over the internet into your new Render database! (This may take roughly 2-5 minutes).

Once everything is deployed and the data is uploaded, click the URL for `ai-dashboard-frontend` to use your live AI Dashboard!
