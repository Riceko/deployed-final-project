This is a web application. We did not deploy the web app due to the financial cost. However, if this were a real client, we would have deployed it.

To run this web app locally, follow these steps:

1) Clone the repository
2) Create and activate a virtualenv (recommended)
3) Install dependencies: `pip install -r requirements.txt`
4) Run the app: `python src/app.py`
5) Open the link printed by Flask (usually http://127.0.0.1:5000)

Deploying to Vercel (quick guide):

- Ensure you have a Vercel account and the Vercel CLI installed.
- This project includes `vercel.json` and an `api/index.py` ASGI adapter so the
	Flask app can be deployed as a serverless function.
- Add any production env vars in the Vercel dashboard (for example `SECRET_KEY`).
- From the project root run: `vercel` and follow the prompts to link and deploy.

Notes and caveats:

- The app writes temporary files to `data/` and `logs/` on disk. Vercel serverless
	functions have an ephemeral filesystem; files written during one invocation
	will not persist across invocations or deployments. For persistent storage,
	use an external store (S3, database, etc.).
- Make sure to set `SECRET_KEY` in production to avoid rotating session keys.