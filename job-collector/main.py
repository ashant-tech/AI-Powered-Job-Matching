"""
Job Collector - Main entry point for collecting jobs from various sources
"""
import schedule
import time
from sources.source1 import Source1
from sources.source2 import Source2
from sources.source3 import Source3
from processors.cleaner import JobCleaner
from processors.duplicate_detector import DuplicateDetector

class JobCollector:
    def __init__(self):
        self.sources = [
            Source1(),
            Source2(),
            Source3()
        ]
        self.cleaner = JobCleaner()
        self.duplicate_detector = DuplicateDetector()

    def collect_jobs(self):
        """Collect jobs from all sources"""
        all_jobs = []
        
        for source in self.sources:
            try:
                print(f"Collecting jobs from {source.name}...")
                jobs = source.fetch_jobs()
                print(f"Found {len(jobs)} jobs from {source.name}")
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error collecting from {source.name}: {e}")
        
        print(f"Total jobs collected: {len(all_jobs)}")
        return all_jobs

    def process_jobs(self, jobs):
        """Process collected jobs"""
        print("Cleaning jobs...")
        cleaned_jobs = self.cleaner.clean_jobs(jobs)
        print(f"Cleaned {len(cleaned_jobs)} jobs")
        
        print("Detecting duplicates...")
        unique_jobs = self.duplicate_detector.remove_duplicates(cleaned_jobs)
        print(f"Found {len(unique_jobs)} unique jobs")
        
        return unique_jobs

    def run(self):
        """Main run loop"""
        print("Starting job collector...")
        
        while True:
            try:
                # Collect jobs
                jobs = self.collect_jobs()
                
                # Process jobs
                processed_jobs = self.process_jobs(jobs)
                
                # Save to database (implement this)
                print(f"Saving {len(processed_jobs)} jobs to database...")
                # self.save_to_database(processed_jobs)
                
                print("Job collection cycle completed")
                
            except Exception as e:
                print(f"Error in job collection cycle: {e}")
            
            # Wait for next scheduled run
            time.sleep(3600)  # Run every hour

    def run_once(self):
        """Run job collection once"""
        print("Running job collection once...")
        jobs = self.collect_jobs()
        processed_jobs = self.process_jobs(jobs)
        print(f"Job collection completed. {len(processed_jobs)} unique jobs processed.")
        return processed_jobs

if __name__ == "__main__":
    collector = JobCollector()
    
    # Run once for testing
    collector.run_once()
    
    # Or run continuously with scheduler
    # schedule.every(1).hours.do(collector.run_once)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
