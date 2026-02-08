# Deploying Loukaniko API to Render

## Prerequisites
- GitHub account
- Your code pushed to a GitHub repository
- Database file (`app/db/data.db`) committed to git

## Deployment Steps

### 1. Prepare Your Repository

Make sure your database is committed:
```bash
git add app/db/data.db
git commit -m "Add database for deployment"
git push
```

### 2. Sign Up for Render

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account (no credit card needed)

### 3. Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `loukaniko-api` (or whatever you prefer)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

4. Click **"Create Web Service"**

### 4. Wait for Deployment

Render will:
- Clone your repository
- Run the build script
- Start your FastAPI app
- Give you a URL like: `https://loukaniko-api.onrender.com`

### 5. Access Your API

Once deployed, your API will be available at:
- **API Root**: `https://loukaniko-api.onrender.com/`
- **Interactive Docs (Swagger)**: `https://loukaniko-api.onrender.com/docs`
- **ReDoc**: `https://loukaniko-api.onrender.com/redoc`

## Important Notes

⚠️ **Free Tier Limitations**:
- Service spins down after 15 minutes of inactivity
- Cold starts take ~30 seconds
- 750 hours/month of uptime

⚠️ **Database Persistence**:
- The database file must be committed to git
- Updates to the database won't persist between deployments
- For production, consider using a persistent database service

## Troubleshooting

### Build fails
- Check the build logs in Render dashboard
- Ensure `build.sh` has execute permissions: `git update-index --chmod=+x build.sh`

### App crashes on startup
- Check the logs in Render dashboard
- Verify database path is correct
- Ensure all dependencies are in `requirements.txt`

### Database not found
- Make sure `app/db/data.db` is committed to git
- Check file paths are relative (not absolute Windows paths)

## Alternative: Manual Database Upload

If you don't want to commit the database to git:

1. Deploy without the database
2. Use Render Shell to upload it:
   - Go to your service → **Shell** tab
   - Upload `data.db` to `app/db/data.db`

Note: The database will be lost on each new deployment.
