web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT --timeout 600 --access-logfile - --error-logfile - --log-level info bot.bot_api:app
