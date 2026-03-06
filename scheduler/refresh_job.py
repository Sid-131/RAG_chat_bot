"""
refresh_job.py
--------------
Phase 13: Data Refresh Scheduler

Uses APScheduler to trigger the ingestion and embedding pipelines.
Schedule: Every 2 days at 2:00 AM.
"""

import os
import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

def run_refresh_sync():
    """
    Wrapper to run the async data pipelines synchronously in the background thread.
    This replaces existing data in Chroma and fetches the latest HTML from sources.
    """
    logger.info("========== DATA REFRESH JOB STARTED ==========")
    
    # We import inside the function to avoid circular imports during startup
    from ingestion.pipeline import run_pipeline
    from embeddings.embedding_pipeline import run_embedding_pipeline
    
    try:
        # 1. Phase 2 & 3: Re-fetch Webpages and Clean
        logger.info("Executing Phase 2: Running Ingestion Pipeline...")
        docs = asyncio.run(run_pipeline())
        logger.info(f"Ingestion complete. Fetched {len(docs)} documents.")
        
        # 2. Phase 4 & 5: Chunk and Re-embed
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Refresh Failed: GEMINI_API_KEY is not set.")
            return
            
        logger.info("Executing Phase 4 & 5: Running Embedding Pipeline...")
        asyncio.run(run_embedding_pipeline(api_key))
        
        logger.info("========== DATA REFRESH JOB COMPLETED ==========")
        
    except Exception as e:
        logger.exception(f"Data Refresh Failed with Error: {e}")

def start_scheduler():
    """
    Initializes the BackgroundScheduler and adds the cron job.
    Returns the scheduler instance so the FastAPI lifespan can shut it down.
    """
    scheduler = BackgroundScheduler()
    
    # Run every 2 days (day="*/2") at 02:00 AM
    trigger = CronTrigger(hour=2, minute=0, day="*/2")
    
    scheduler.add_job(
        run_refresh_sync,
        trigger=trigger,
        id="data_refresh_job",
        replace_existing=True,
        misfire_grace_time=3600  # 1 hour grace period if missed
    )
    
    scheduler.start()
    logger.info("APScheduler started. Next refresh scheduled for: Every 2 days at 02:00 AM")
    return scheduler
