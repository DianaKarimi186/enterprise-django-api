import time
from celery import shared_task

@shared_task
def simulate_heavy_background_job(product_name):
    print(f"🚀 [WORKER START]: Beginning heavy data logging for {product_name}...")
    
    # Simulate a slow 10-second operations delay (like an email network request)
    time.sleep(10)
    
    print(f"✅ [WORKER SUCCESS]: Heavy processing for {product_name} complete!")
    return f"Processed {product_name}"