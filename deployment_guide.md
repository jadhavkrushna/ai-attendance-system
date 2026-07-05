# AI Attendance System Deployment Guide

This guide explains how to deploy the AI Attendance System to a production cloud environment. Since the application utilizes complex machine learning libraries like `dlib` (for face recognition) and `librosa` (for audio processing), **Docker-based deployment** is highly recommended. It guarantees that the compiler tools and system-level dependencies (`cmake`, `libsndfile1`, etc.) are correctly installed and configured without manual environment setup.

---

## 1. Prerequisites & Environment Variables

The application relies on Supabase for the database, so the database itself is hosted in the cloud. You do not need to host or run a database container.

You must configure the following Environment Variables in your hosting environment:
* `SUPABASE_URL`: The URL of your Supabase project (e.g., `https://your-project.supabase.co`).
* `SUPABASE_KEY`: Your Supabase anonymous (`anon`) or `service_role` API key.

---

## 2. Local Testing (Highly Recommended)

Before deploying to the cloud, you can test the production setup locally in two ways.

### Option A: Running Flask Directly (Without Streamlit)
Activate your virtual environment and run the Flask application directly:
```powershell
.venv\Scripts\python.exe app.py
```
* The Flask application will run in the foreground on `http://localhost:5000/`.
* Streamlit will not be launched, and there are no background threads.

### Option B: Running via Docker Compose
Build and run the container locally:
```bash
docker compose up --build
```
* The container compiles `dlib` and runs Gunicorn on port `5000`.
* The portal will be available at `http://localhost:5000/`.
* Stop the container with `docker compose down`.

---

## 3. Production Deployment Options

### Option A: Render (Recommended & Easiest)
Render supports Docker deployments natively, making it a very simple option.

1. Sign in to [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Set the following details:
   * **Name**: `ai-attendance-system`
   * **Runtime**: Select **Docker** (it will automatically read the `Dockerfile` in the root).
   * **Instance Type**: Select your tier (Free or Starter). *Note: Building the container compiles dlib from source, which requires moderate CPU. A standard starter instance or higher works best.*
5. Expand **Advanced** and add the following Environment Variables:
   * `SUPABASE_URL` = (your supabase url)
   * `SUPABASE_KEY` = (your supabase key)
6. Click **Deploy Web Service**. Render will build the Docker container and deploy it automatically.

---

### Option B: Google Cloud Run (Highly Scalable)
GCP Cloud Run is an excellent choice for hosting containerized Python applications with low cost (pay-per-request).

1. Install and initialize the [Google Cloud SDK](https://cloud.google.com/sdk).
2. Configure Docker to authenticate with GCP Artifact Registry:
   ```bash
   gcloud auth configure-docker
   ```
3. Build and push your image to GCP Artifact Registry (replace `PROJECT_ID` with your GCP project ID):
   ```bash
   docker build -t gcr.io/PROJECT_ID/ai-attendance-system:latest .
   docker push gcr.io/PROJECT_ID/ai-attendance-system:latest
   ```
4. Deploy the container to Cloud Run:
   ```bash
   gcloud run deploy ai-attendance-system \
     --image gcr.io/PROJECT_ID/ai-attendance-system:latest \
     --platform managed \
     --allow-unauthenticated \
     --port 5000 \
     --set-env-vars="SUPABASE_URL=YOUR_SUPABASE_URL,SUPABASE_KEY=YOUR_SUPABASE_KEY"
   ```
5. GCP will provide a HTTPS URL (e.g. `https://ai-attendance-system-xxx.a.run.app`) where your app is live.

---

### Option C: Heroku (Docker Registry)
Heroku's standard Python buildpack might run into compile timeouts when building `dlib`. Using Heroku's Docker Registry is recommended.

1. Log in to the Heroku CLI and container registry:
   ```bash
   heroku login
   # Authenticate container service
   heroku container:login
   ```
2. Create a Heroku app:
   ```bash
   heroku create ai-attendance-system
   ```
3. Set your environment variables:
   ```bash
   heroku config:set SUPABASE_URL=your-supabase-url
   heroku config:set SUPABASE_KEY=your-supabase-key
   ```
4. Build the image and push to Heroku:
   ```bash
   heroku container:push web
   ```
5. Release the image to start your app:
   ```bash
   heroku container:release web
   ```

---

## 4. Key Deployment Notes & Troubleshooting

* **Build Time**: The first Docker build takes **5–10 minutes** because compiling the C++ code for `dlib` is CPU-intensive. Subsequent builds will be very fast because Docker caches the layers.
* **Timeout Errors on Deploy**: Some cloud providers have short build-time limits. Using Docker-based builds avoids this because the environment is prebuilt. If using Heroku, do not use the git-push method; use the `heroku container:push` command as outlined above.
* **Audio processing errors**: The voice recognition code utilizes `librosa` and `resemblyzer`, which require system-level audio libraries. The `Dockerfile` includes `libsndfile1` to prevent any audio loading errors.
