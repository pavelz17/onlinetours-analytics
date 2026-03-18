import re
import json
import requests
import time
import logging
import traceback
from typing import Dict
from bs4 import BeautifulSoup

from utils.config_parser import parse_tour_dates


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


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
            logger.info(f'Start loading offers for {hotel_nm}')
            offers = self._get_offers(
                hotel_id,
                dates,
                operators,
                tour_params,
            )
            data[hotel_nm] = offers

        return data

    def _get_offers(self, hotel_id, dates, operators, tour_params):
        tour_params = {
            'depart_city_id': int(tour_params['depart_city_id']),
            'duration_from': int(tour_params['duration_from']),
            'duration_to': int(tour_params['duration_to']),
            'adults': int(tour_params['adults']),
            'ticket_strategy': tour_params['ticket_strategy'],
            'hotel_id': int(hotel_id),
        }
        offers = []
        dates_ranges = parse_tour_dates(dates['start_dates_ranges'])
        for dates in dates_ranges:
            tour_params['start_from'] = dates[0]
            tour_params['start_to'] = dates[1]
            search_id = self._generate_search_id(
                url=f'{self.vendor}/api/v3/hotel_searches',
                params=tour_params,
            )
            offers.append(self._load_offers(operators, search_id, dates))
        return offers

    def _generate_search_id(self, url, params: Dict) -> str:
        response = self.http_client.post(url, json=params)
        return json.loads(response.text)['search_id']

    def _load_offers(self, operators, search_id, dates_range):
        offer_params = {
            'filters[ticket_strategy][]': 'include',
            'limit': '5',
            'offset': '0',
            'date_from': dates_range[0],
            'date_to': dates_range[1],
        }
        offers = {}
        for operator_nm, operator_id in operators.items():
            try:
                logger.info(f'Search offers from {operator_nm} on dates {dates_range}')
                offer_params['filters[operator][]'] = operator_id
                data = self._get_offers_with_wait_success(
                    url=f'{self.vendor}/api/v3/hotel_searches/{search_id}',
                    params=offer_params,
                )

                #TODO groups rename to offers_headers?
                groups = data['groups']
                if len(groups) == 0:
                    print(f"Couldn't find offers for from {operator_nm}")
                    continue

                offers_data = self._get_offers_with_ids(groups.values())
                all_offers_ids = []
                for offer in offers_data:
                    offers_ids = offer.pop('offers_ids')
                    all_offers_ids.extend(offers_ids)
                    for offer_id in offers_ids:
                        offers[offer_id] = offer

                breakpoint()
                url = vendor + '/api/web/v1/start_offers_actualization'
                params = {'offers_ids': offers_ids}
                # resp = client.post(url, json=params)
                # for _ in range(5):
                #     tm.sleep(1.5)
                #     url = vendor + '/api/web/v1/get_offers_actualization_result'
                #     resp = client.post(url, json=params)
                #     data = json.loads(resp.text)
                #     offers = data['offers']
                #     count_offers = len(offers)
                #     success_offers = []
                #     for offer in offers:
                #         if offer.get('flights'):
                #             success_offers.append(offer)
                #     if len(success_offers) == count_offers:
                #         break

                # for offer in success_offers:
                #     flights = offer['flights']
                #     msg_data = messages[offer['id']]
                #     msg_data['flights'] = []
                #     for flight in flights:
                #         lfrom = flight['legs_from'][0]
                #         lto = flight['legs_to'][0]
                #         if not (lto.get('aircompany_id')
                #                 and lfrom.get('aircompany_id')):
                #             continue
                #         if (lfrom['aircompany_id'] not in aircompanies
                #                 or lto['aircompany_id'] not in aircompanies):
                #             continue

                #         dep_to = datetime.fromisoformat(lto['departure_date']).time()
                #         dep_from = datetime.fromisoformat(lfrom['departure_date']).time()
                #         if not (dpts <= dep_to <= dptd
                #                 and dpfs <= dep_from <= dpfd):
                #             continue

                #         msg_data['flights'].append(flight)
                #         msg_data['flight_cities'] = data['flight_cities']
                #         msg_data['airports'] = data['airports']
                #     msg_data['url'] = offer['url'][2:]
                #     result_messages.append(msg_data)

            except Exception as e:
                traceback.print_exc()

        return offers

    def _get_offers_with_ids(self, offer_groups):
        res = []
        for offer_group in offer_groups:
            for offer in offer_group['offers']:
                url = self.vendor + offer['url']
                resp = self.http_client.get(url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                raw_js = soup.find('script',
                    string=re.compile("INITIAL_STATE"))
                data = json.loads(raw_js.string.split(' = ')[1][:-1])
                res.append({
                    'start_date': offer['start_date'],
                    'duration': offer['duration'],
                    'room_type': offer['room_type'],
                    'operator': offer['operator_name'],
                    'meal': offer['meal_type'],
                    'offers_ids': data['page']['offers_ids'],
                })
        return res

    def _get_offers_with_wait_success(self, url, params, attempts=5):
        for attempt in range(1, attempts):
            response = self.http_client.get(url, params=params)
            data = json.loads(response.text)
            if data['status'] == 'success' and data['groups']:
                return data
        raise Exception
