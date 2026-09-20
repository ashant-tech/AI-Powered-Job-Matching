"""
Job Collector - Main entry point for collecting jobs from various sources
"""
import schedule
import time
import os
from dotenv import load_dotenv
from sources.source1 import Source1
from sources.source2 import Source2
from sources.source3 import Source3
from sources.source4 import Source4
from sources.source5 import Source5
from sources.source6 import Source6
from sources.source7 import Source7
from sources.source8 import Source8
from sources.source9 import Source9
from sources.telegram_source import TelegramJobSource
from processors.cleaner import JobCleaner
from processors.duplicate_detector import DuplicateDetector

# Load environment variables
load_dotenv()

class JobCollector:
    def __init__(self):
        self.sources = [
            Source1(),  # Ethiojobs
            Source2(),  # HaHuJobs
            Source3(),  # Reporter Jobs Gazette
            Source4(),  # Afriwork
            Source5(),  # Srafelagi
            Source6(),  # SemayJobs
            Source7(),  # AddisJobs
            Source8(),  # Enjera (Tech/Startup jobs)
            Source9(),  # Shega Jobs (Professional services)
            TelegramJobSource()  # Telegram Channels (50+ Ethiopian channels)
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

    def save_to_database(self, jobs):
        """Save processed jobs to database"""
        try:
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from app.config.database import SessionLocal, Base, engine
            from app.models.job import Job
            from app.models.cv import CV
            from app.services.matching_service import MatchingService
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            
            db = SessionLocal()
            
            saved_count = 0
            for job_data in jobs:
                # Check if job already exists
                existing_job = db.query(Job).filter(
                    Job.source_url == job_data.get('source_url', '')
                ).first()
                
                if not existing_job:
                    # Create new job
                    db_job = Job(
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        description=job_data.get('description', ''),
                        requirements=job_data.get('requirements', ''),
                        skills=job_data.get('skills', ''),
                        location=job_data.get('location', ''),
                        salary_min=job_data.get('salary_min', 0),
                        salary_max=job_data.get('salary_max', 0),
                        job_type=job_data.get('job_type', 'full-time'),
                        source=job_data.get('source', ''),
                        source_url=job_data.get('source_url', ''),
                        is_active=1
                    )
                    db.add(db_job)
                    saved_count += 1
            
            db.commit()

            if saved_count:
                print(f"New jobs saved: {saved_count}. Triggering matching and notifications...")
                matching_service = MatchingService(db)
                cv_count = 0
                for cv in db.query(CV).all():
                    try:
                        print(f"Finding matches for CV {cv.id} (User: {cv.user_id})...")
                        matching_service.find_matches_for_cv(cv.user_id, cv.id)
                        cv_count += 1
                        print(f"Successfully processed CV {cv.id}")
                    except Exception as e:
                        print(f"Error matching jobs for CV {cv.id}: {e}")
                print(f"Processed {cv_count} CVs for new job matches")
                print("Notifications will be sent automatically for high-quality matches")

            db.close()
            
            print(f"Saved {saved_count} new jobs to database")
            return saved_count
            
        except ImportError as e:
            print(f"Database integration not available: {e}")
            print("Jobs collected but not saved to database")
            return 0
        except Exception as e:
            print(f"Error saving to database: {e}")
            return 0
    
    def save_to_json(self, jobs, filename="collected_jobs.json"):
        """Save jobs to JSON file as fallback"""
        import json
        try:
            with open(filename, 'w') as f:
                json.dump(jobs, f, indent=2)
            print(f"Saved {len(jobs)} jobs to {filename}")
            return len(jobs)
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return 0

    def run(self):
        """Main run loop"""
        print("Starting job collector...")
        
        while True:
            try:
                # Collect jobs
                jobs = self.collect_jobs()
                
                # Process jobs
                processed_jobs = self.process_jobs(jobs)
                
                # Save to database
                print(f"Saving {len(processed_jobs)} jobs to database...")
                saved_count = self.save_to_database(processed_jobs)
                
                # Fallback to JSON if database save failed
                if saved_count == 0:
                    print("Database save failed, saving to JSON fallback...")
                    self.save_to_json(processed_jobs)
                
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
        saved_count = self.save_to_database(processed_jobs)
        
        # Fallback to JSON if database save failed
        if saved_count == 0:
            print("Database save failed, saving to JSON fallback...")
            self.save_to_json(processed_jobs)
        
        print(f"Job collection completed. {len(processed_jobs)} unique jobs processed, {saved_count} saved to database.")
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
