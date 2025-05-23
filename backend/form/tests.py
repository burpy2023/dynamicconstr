from django.test import TestCase, Client
from unittest.mock import patch
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class CeilingConstructionViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = '/api/next/'

    def mock_df(self, rows):
        """Ensure each test row has all required columns"""
        required_columns = [
            'Ceiling type', 'Deck construction', 'Attic ventilation', 'Attic fan',
            'Radiant barrier', 'Roofing material', 'Roof color',
            'Insulation', 'R-value', 'Extended Construction Numbers',
            'Look-Up Construction Number', 'Total Price', 'Notes'
        ]
        complete_rows = []
        for row in rows:
            full_row = {col: row.get(col, None) for col in required_columns}
            complete_rows.append(full_row)
        return pd.DataFrame(complete_rows)

    @patch('form.views.df.copy')
    def test_initial_request(self, mock_copy):
        mock_copy.return_value = self.mock_df([
            {
                'Ceiling type': 'Type A',
                'Roofing material': 'Material X',
                'Extended Construction Numbers': '18A-1',
                'Total Price': 5000
            },
            {
                'Ceiling type': 'Type B',
                'Roofing material': 'Material Y',
                'Extended Construction Numbers': '18A-2',
                'Total Price': 7500
            }
        ])

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['next'], 'Ceiling type')
        self.assertIn('Type A', data['options'])
        self.assertIn('Type B', data['options'])

    @patch('form.views.df.copy')
    def test_full_selection_flow(self, mock_copy):
        mock_copy.return_value = self.mock_df([
            {
                'Ceiling type': 'Type A',
                'Roofing material': 'Material X',
                'Extended Construction Numbers': '18A-1',
                'Total Price': 5000.0
            }
        ])

        response = self.client.get(self.url, {'Ceiling type': 'Type A'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['next'], 'Roofing material')
        self.assertIn('Material X', data['options'])

        response = self.client.get(self.url, {
            'Ceiling type': 'Type A',
            'Roofing material': 'Material X'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data['next'])
        self.assertEqual(data['construction_number'], '18A-1')
        self.assertAlmostEqual(data['price'], 5000.0, places=2)

    @patch('form.views.df.copy')
    def test_no_match_scenario(self, mock_copy):
        mock_copy.return_value = self.mock_df([
            {
                'Ceiling type': 'Type A',
                'Extended Construction Numbers': '18A-1',
                'Total Price': 5000.0
            }
        ])

        response = self.client.get(self.url, {'Ceiling type': 'Invalid Type'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data['next'])
        self.assertIsNone(data['construction_number'])
        self.assertIsNone(data['price'])

    def test_invalid_parameter(self):
        response = self.client.get(self.url, {'InvalidColumn': 'some value'})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid filter: InvalidColumn')

    @patch('form.views.df.copy')
    def test_empty_dataframe(self, mock_copy):
        mock_copy.return_value = pd.DataFrame()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Internal server error.')
