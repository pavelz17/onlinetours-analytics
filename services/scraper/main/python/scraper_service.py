import logging

from impl.onlinetours_downloader import OnlinetoursDownloader
from impl.http_client import HttpClient
from utils.config_parser import ConfigParser


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
#TODO filter method by aircompanies
#TODO filter method by moon
#TODO common filter method accepted collection and filter func


class ScraperService:
    def __init__(self):
        self.config = ConfigParser(config_file='common.ini')
        self.downloader = OnlinetoursDownloader(
            vendor=self.config.get_property('vendors', 'onlinetours'),
            http_client=HttpClient(),
        )

    def run(self):
        raw_data = self.downloader.run_downloading(
            dates = self.config.get_group('tour_dates'),
            hotels = self.config.get_group('onlinetours.hotels'),
            operators = self.config.get_group('onlinetours.operators'),
            tour_params = self.config.get_group('onlinetours.tour_params'),
        )


service = ScraperService()
service.run()
