from typing import Dict


class OnlinetoursDownloader:
    def __init__(self, vendor, http_client):
        self.vendor = vendor
        self.http_client = http_client

    def run_downloading(
        self,
        dates: Dict[str, str],
        hotels: Dict[str, str],
        operators: Dict[str, str],
        tour_params: Dict[str, str],
    ) -> Dict:
        data = {}
        for hotel_nm, hotel_id in hotels.items():
            breakpoint()
            offers = self._get_offers(hotel_id, dates, operators)
            data[hotel_nm] = offers

        return data

    def _get_offers(self, hotel_id, dates, operators):
        offers = []
        for dt in dates:
            for operator in operators:
                pass

        return offers
