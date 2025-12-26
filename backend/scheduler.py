import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import aioschedule
import sys
import os

# Add the backend directory to the Python path to resolve imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest_docs import process_docs
from rag_service import RAGService
from vector_db import VectorDB


class DocumentUpdateScheduler:
    """Scheduler for periodic document updates and reprocessing."""

    def __init__(self):
        self.rag_service = RAGService()
        self.is_running = False
        self.last_update_time = None

    async def check_and_update_documents(self):
        """Check for document changes and update vector database if needed."""
        try:
            logging.info("Starting document update check...")

            # Process documents from the docs directory
            docs_path = "docs"
            document_chunks = process_docs(docs_path)

            if not document_chunks:
                logging.info("No documents found to process")
                return

            # Add documents to RAG service (which will embed and store them)
            documents = []
            for chunk in document_chunks:
                documents.append({
                    "content": chunk.content,
                    "metadata": chunk.metadata
                })

            doc_ids = await self.rag_service.batch_add_documents(documents)

            self.last_update_time = datetime.now()
            logging.info(f"Document update completed. Processed {len(document_chunks)} chunks, {len(set(chunk.metadata.get('source_file') for chunk in document_chunks))} files")

        except Exception as e:
            logging.error(f"Error during document update: {str(e)}")
            logging.error(f"Traceback: {__import__('traceback').format_exc()}")

    async def start_scheduler(self):
        """Start the document update scheduler."""
        if self.is_running:
            logging.warning("Scheduler is already running")
            return

        logging.info("Starting document update scheduler...")

        # Schedule document updates daily at 2 AM
        aioschedule.every().day.at("02:00").do(self.check_and_update_documents)

        # For testing purposes, also schedule every hour
        aioschedule.every().hour.do(self.check_and_update_documents)

        self.is_running = True

        # Run the scheduler continuously
        while self.is_running:
            await aioschedule.run_pending()
            await asyncio.sleep(60)  # Check every minute

    async def stop_scheduler(self):
        """Stop the document update scheduler."""
        self.is_running = False
        logging.info("Scheduler stopped")

    async def force_update_now(self):
        """Force an immediate document update."""
        logging.info("Forcing immediate document update...")
        await self.check_and_update_documents()
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "message": "Forced document update completed"
        }


# Global scheduler instance
scheduler = DocumentUpdateScheduler()


async def start_document_scheduler():
    """Start the document update scheduler."""
    await scheduler.start_scheduler()


async def stop_document_scheduler():
    """Stop the document update scheduler."""
    await scheduler.stop_scheduler()


def get_scheduler_status():
    """Get the current status of the scheduler."""
    return {
        "is_running": scheduler.is_running,
        "last_update_time": scheduler.last_update_time.isoformat() if scheduler.last_update_time else None,
        "next_scheduled_update": str(aioschedule.next_run()) if aioschedule.next_run() else None
    }