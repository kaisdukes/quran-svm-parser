from typing import Dict

import requests

from ..orthography.location import Location
from .responses import GraphLocation, MetadataResponse, VerseResponse, GraphResponse


class CorpusClient:
    BASE_URL = 'https://qurancorpus.app/api'

    def metadata(self):
        json = self._get('/metadata', None)
        return MetadataResponse.parse_obj(json)

    def morphology(self, location: Location, count: int):
        json = self._get(
            '/morphology',
            {
                'location': location,
                'n': count,
                'features': True
            })
        return [VerseResponse.parse_obj(item) for item in json]

    def syntax(self, location: GraphLocation):
        _location = location.location
        json = self._get(
            '/syntax',
            {
                'location': Location(_location[0], _location[1]),
                'graph': location.graph_number
            })
        return GraphResponse.parse_obj(json)

    def _get(self, relative_path: str, params: Dict):
        response = requests.get(self.BASE_URL + relative_path, params)
        response.raise_for_status()
        return response.json()
