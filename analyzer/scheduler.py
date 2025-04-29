from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
import logging
import sys
import os

# 添加 spider/ 目录到 Python 路径
sys.path.append(os.path.join(settings.BASE_DIR, 'spider'))
from hiscrawl import CPUCrawler

logger = logging.getLogger(__name__)

class PriceScraperScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def scrape_job(self):
        """定时任务：运行"""
        try:
            crawler = CPUCrawler()
            crawler.crawl()
            logger.info("Completed scrape for power products")
        except Exception as e:
            logger.error(f"Error in scrape job: {str(e)}")

    def start(self):
        """启动定时任务"""
        try:
            self.scheduler.add_job(
                self.scrape_job,
                trigger=CronTrigger(hour=2, minute=0),  # 每天 02:00
                id='scrape_power',
                replace_existing=True
            )
            self.scheduler.start()
            logger.info("Scheduler started")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")

    def shutdown(self):
        """停止定时任务"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")