# -*- coding: utf-8 -*-
"""
Verification Script for KOSPI Daily Tracker Parser
Mocks the network response and verifies the extraction and monthly calculation logic.
"""
import sys
import os
import unittest
import pandas as pd
from unittest.mock import patch

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PARENT_DIR)

import kospi_investor_tracker

# Mock HTML content
MOCK_INDEX_HTML = """
<table class="type_1">
  <tr>
    <td class="date">2026.06.10</td>
    <td class="number_1">2,605.12</td>
    <td class="number_1"><span class="tah p11 red02">▲15.20</span></td>
    <td class="number_1"><span class="tah p11 red02">+0.59%</span></td>
  </tr>
  <tr>
    <td class="date">2026.06.09</td>
    <td class="number_1">2,589.92</td>
    <td class="number_1"><span class="tah p11 nv01">▼10.10</span></td>
    <td class="number_1"><span class="tah p11 nv01">-0.39%</span></td>
  </tr>
</table>
"""

MOCK_INVESTOR_HTML = """
<table>
  <tr>
    <td class="date">2026.06.10</td>
    <td class="number">-340</td>
    <td class="number">120</td>
    <td class="number">210</td>
    <td class="number">150</td>
    <td class="number">0</td>
    <td class="number">20</td>
    <td class="number">0</td>
    <td class="number">0</td>
    <td class="number">40</td>
    <td class="number">10</td>
  </tr>
  <tr>
    <td class="date">2026.06.09</td>
    <td class="number">500</td>
    <td class="number">-200</td>
    <td class="number">-300</td>
    <td class="number">-200</td>
    <td class="number">0</td>
    <td class="number">-50</td>
    <td class="number">0</td>
    <td class="number">0</td>
    <td class="number">-50</td>
    <td class="number">0</td>
  </tr>
  <tr>
    <td class="date">2026.05.29</td>
    <td class="number">200</td>
    <td class="number">100</td>
    <td class="number">-300</td>
    <td class="number">-100</td>
    <td class="number">0</td>
    <td class="number">-100</td>
    <td class="number">0</td>
    <td class="number">0</td>
    <td class="number">-100</td>
    <td class="number">0</td>
  </tr>
</table>
"""

class TestKOSPIParser(unittest.TestCase):
    
    @patch('kospi_investor_tracker.fetch_html_via_gas')
    def test_get_kospi_index_data(self, mock_fetch):
        mock_fetch.return_value = MOCK_INDEX_HTML
        data = kospi_investor_tracker.get_kospi_index_data()
        
        # Verify length and today's first row
        self.assertEqual(len(data), 2)
        today = data[0]
        self.assertEqual(today["date"], "2026.06.10")
        self.assertEqual(today["close"], "2,605.12")
        self.assertEqual(today["change"], "+15.20")
        self.assertEqual(today["fluc_rate"], "+0.59%")
        
        # Verify yesterday's row
        yesterday = data[1]
        self.assertEqual(yesterday["date"], "2026.06.09")
        self.assertEqual(yesterday["change"], "-10.10")
        self.assertEqual(yesterday["fluc_rate"], "-0.39%")

    @patch('kospi_investor_tracker.fetch_html_via_gas')
    def test_get_kospi_investor_data_and_trends(self, mock_fetch):
        # Setup mock fetch to return mock html for both page 1 and page 2 calls
        mock_fetch.return_value = MOCK_INVESTOR_HTML
        df = kospi_investor_tracker.get_kospi_investor_data()
        
        # We expect unique dates: 2026.06.10, 2026.06.09, and 2026.05.29
        self.assertEqual(len(df), 3)
        
        # Check today's row
        today_row = df[df["date"] == "2026.06.10"].iloc[0]
        self.assertEqual(today_row["individual"], -340)
        self.assertEqual(today_row["foreigner"], 120)
        self.assertEqual(today_row["institution"], 210)
        self.assertEqual(today_row["fin_inv"], 150)
        self.assertEqual(today_row["pension"], 40)
        
        # Check monthly trend for June 2026 (should exclude May 29 row)
        stats = kospi_investor_tracker.analyze_monthly_trend(df, "2026-06")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_days"], 2) # Only June 10 and June 9
        
        # Individual: -340 + 500 = +160
        self.assertEqual(stats["individual"], 160)
        # Foreigner: 120 + (-200) = -80
        self.assertEqual(stats["foreigner"], -80)
        # Institution: 210 + (-300) = -90
        self.assertEqual(stats["institution"], -90)
        
        # Check buy/sell days
        # Individual: June 10 (-340, sell), June 9 (+500, buy) -> 1 buy, 1 sell
        self.assertEqual(stats["ind_days"], (1, 1))
        # Foreigner: June 10 (+120, buy), June 9 (-200, sell) -> 1 buy, 1 sell
        self.assertEqual(stats["frg_days"], (1, 1))
        # Institution: June 10 (+210, buy), June 9 (-300, sell) -> 1 buy, 1 sell
        self.assertEqual(stats["inst_days"], (1, 1))

if __name__ == '__main__':
    print("Running parser unit tests...")
    unittest.main()
