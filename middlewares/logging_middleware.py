import logging
import time
from fastapi import Request

logger = logging.getLogger("requests")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request received: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"An error occurred during request processing: {e}")
        raise
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"Request completed in {formatted_process_time}ms. Status code: {response.status_code}")
    return response