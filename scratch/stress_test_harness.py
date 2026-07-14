# -*- coding: utf-8 -*-
"""
Stress Test Harness for KOSPI Telegram Tracker
Tests robustness against network failures, HTML changes, malformed data, date boundary edge cases, and Telegram transmission issues.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Add parent directory to path to import kospi_investor_tracker
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import kospi_investor_tracker

# Sample valid HTML contents for mocking
MOCK_INDEX_HTML_VALID = """
<html>
<body>
<table class="type_1">
    <tr>
        <td>2026.06.10</td>
        <td>2,650.50</td>
        <td>▲ 15.20</td>
        <td>+0.58%</td>
    </tr>
    <tr>
        <td>2026.06.09</td>
        <td>2,635.30</td>
        <td>▼ 5.10</td>
        <td>-0.19%</td>
    </tr>
</table>
</body>
</html>
"""

MOCK_INVESTOR_HTML_PAGE1_VALID = """
<html>
<body>
<table>
    <tr>
        <td>2026.06.10</td>
        <td>1,500</td><td>-800</td><td>-600</td><td>-100</td><td>-50</td><td>-200</td><td>-100</td><td>-50</td><td>-100</td><td>-100</td>
    </tr>
    <tr>
        <td>2026.06.09</td>
        <td>-500</td><td>1,200</td><td>-600</td><td>200</td><td>-50</td><td>-300</td><td>-100</td><td>-50</td><td>-300</td><td>-100</td>
    </tr>
    <tr>
        <td>2026.06.08</td>
        <td>800</td><td>-300</td><td>-400</td><td>-100</td><td>50</td><td>-150</td><td>-50</td><td>-50</td><td>-100</td><td>-100</td>
    </tr>
</table>
</body>
</html>
"""

MOCK_INVESTOR_HTML_PAGE2_VALID = """
<html>
<body>
<table>
    <tr>
        <td>2026.06.05</td>
        <td>-1,000</td><td>2,000</td><td>-900</td><td>400</td><td>100</td><td>-800</td><td>-100</td><td>-50</td><td>-400</td><td>-100</td>
    </tr>
    <tr>
        <td>2026.06.04</td>
        <td>400</td><td>-200</td><td>-100</td><td>-50</td><td>-20</td><td>-10</td><td>0</td><td>-10</td><td>-10</td><td>0</td>
    </tr>
</table>
</body>
</html>
"""

class TestKOSPINotifier(unittest.TestCase):
    def setUp(self):
        # Reset environment settings inside module
        kospi_investor_tracker.GAS_PROXY_URL = "https://script.google.com/macros/s/MOCK_GAS_URL/exec"
        kospi_investor_tracker.TELEGRAM_TOKEN = "MOCK_TOKEN"
        kospi_investor_tracker.TELEGRAM_CHAT_ID = "MOCK_CHAT_ID"
        self.sent_telegram_messages = []
        self.telegram_status_code = 200
        self.telegram_response_text = '{"ok": true}'
        
        # Patching Telegram post call
        self.patcher_post = patch('requests.post')
        self.mock_post = self.patcher_post.start()
        
        def mock_post_side_effect(url, json, verify, timeout):
            self.sent_telegram_messages.append(json.get("text", ""))
            mock_res = MagicMock()
            mock_res.status_code = self.telegram_status_code
            mock_res.text = self.telegram_response_text
            return mock_res
            
        self.mock_post.side_effect = mock_post_side_effect
        
    def tearDown(self):
        self.patcher_post.stop()

    @patch('requests.get')
    @patch('kospi_investor_tracker.datetime')
    def test_scenario_1_baseline_success(self, mock_datetime, mock_get):
        """Scenario 1: Baseline success scenario with valid HTML data."""
        print("\n--- Running Scenario 1: Baseline Success ---")
        mock_datetime.now.return_value = datetime(2026, 6, 10, 10, 30)
        
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = MOCK_INDEX_HTML_VALID
            elif "investorDealTrendDay.nhn" in target_url or "KOSPI_INVESTOR_MULTIPLE" in target_url:
                mock_res.text = MOCK_INVESTOR_HTML_PAGE1_VALID + "\n" + MOCK_INVESTOR_HTML_PAGE2_VALID
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        # Execute
        with patch('sys.argv', ['kospi_investor_tracker.py', '--am']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("[코스피 오전 장중 (10:30)]", self.sent_telegram_messages[0])
        self.assertIn("지수: <b>2,650.50</b>", self.sent_telegram_messages[0])
        self.assertIn("개인: <code>+1,500억</code>", self.sent_telegram_messages[0])
        self.assertIn("외국인: <code>-800억</code>", self.sent_telegram_messages[0])
        self.assertIn("1달(30일): 개인 <code>+1,200억</code> | 외인 <code>+1,900억</code> | 기관 <code>-2,600억</code>", self.sent_telegram_messages[0])
        self.assertIn("6개월(120일): 개인 <code>+1,200억</code> | 외인 <code>+1,900억</code> | 기관 <code>-2,600억</code>", self.sent_telegram_messages[0])
        print("Scenario 1 Passed.")

    def test_scenario_2_missing_gas_url(self):
        """Scenario 2: GAS Proxy URL missing or default value."""
        print("\n--- Running Scenario 2: Missing GAS Proxy URL ---")
        kospi_investor_tracker.GAS_PROXY_URL = "YOUR_GAS_PROXY_URL"
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("GAS_PROXY_URL", self.sent_telegram_messages[0])
        print("Scenario 2 Passed.")

    @patch('requests.get')
    def test_scenario_3_gas_network_failure(self, mock_get):
        """Scenario 3: Network error/timeout calling GAS Proxy."""
        print("\n--- Running Scenario 3: GAS Network Failure ---")
        mock_get.side_effect = Exception("Connection timed out")
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("웹 호출 실패", self.sent_telegram_messages[0])
        print("Scenario 3 Passed.")

    @patch('requests.get')
    def test_scenario_4_gas_internal_error_response(self, mock_get):
        """Scenario 4: GAS Proxy returns internal error messages."""
        print("\n--- Running Scenario 4: GAS Internal Error Response ---")
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.text = "Error: Spreadsheet not found"
        mock_get.return_value = mock_res
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("GAS 프록시 서버 에러", self.sent_telegram_messages[0])
        print("Scenario 4 Passed.")

    @patch('requests.get')
    def test_scenario_5_index_table_missing(self, mock_get):
        """Scenario 5: KOSPI Index daily table missing from Naver response."""
        print("\n--- Running Scenario 5: Index Table Missing ---")
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = "<html><body>No Table Here</body></html>"
            else:
                mock_res.text = MOCK_INVESTOR_HTML_PAGE1_VALID
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("KOSPI 지수 일별 테이블을 찾을 수 없습니다", self.sent_telegram_messages[0])
        print("Scenario 5 Passed.")

    @patch('requests.get')
    def test_scenario_6_index_data_rows_empty(self, mock_get):
        """Scenario 6: Index table exists but rows are invalid or mismatch regex."""
        print("\n--- Running Scenario 6: Index Data Rows Empty ---")
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = """
                <html><body><table class="type_1">
                    <tr><td>Header1</td><td>Header2</td></tr>
                    <tr><td>InvalidDate</td><td>2,600</td><td>10</td><td>0.5%</td></tr>
                </table></body></html>
                """
            else:
                mock_res.text = MOCK_INVESTOR_HTML_PAGE1_VALID
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("KOSPI 지수 데이터 파싱 실패", self.sent_telegram_messages[0])
        print("Scenario 6 Passed.")

    @patch('requests.get')
    def test_scenario_7_investor_table_missing(self, mock_get):
        """Scenario 7: Investor daily trend table missing or parse fails."""
        print("\n--- Running Scenario 7: Investor Table Missing ---")
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = MOCK_INDEX_HTML_VALID
            else:
                mock_res.text = "<html><body>No Table</body></html>"
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("투자자별 매매동향 데이터 파싱 실패", self.sent_telegram_messages[0])
        print("Scenario 7 Passed.")

    @patch('requests.get')
    def test_scenario_8_malformed_numeric_values(self, mock_get):
        """Scenario 8: Numeric fields contain characters or are empty, parsing robustness."""
        print("\n--- Running Scenario 8: Malformed Numeric Values ---")
        malformed_investor_html = """
        <html><body><table>
            <tr>
                <td>2026.06.10</td>
                <td>1,500억원</td><td>-</td><td>N/A</td><td>--</td><td></td><td>-200</td><td>-100</td><td>-50</td><td>-100</td><td>-100</td>
            </tr>
        </table></body></html>
        """
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = MOCK_INDEX_HTML_VALID
            else:
                mock_res.text = malformed_investor_html
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertNotIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        print("Scenario 8 Passed.")

    @patch('requests.get')
    @patch('kospi_investor_tracker.datetime')
    def test_scenario_9_date_boundary_monthly_trend_empty(self, mock_datetime, mock_get):
        """Scenario 9: Date boundary condition where recent data belongs to previous month, resulting in empty monthly stats."""
        print("\n--- Running Scenario 9: Date Boundary (Empty Monthly Stats) ---")
        mock_datetime.now.return_value = datetime(2026, 6, 1, 10, 30)
        
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                # Latest date is 2026.06.01
                mock_res.text = """
                <html><body><table class="type_1">
                    <tr><td>2026.06.01</td><td>2,650.50</td><td>▲ 15.20</td><td>+0.58%</td></tr>
                </table></body></html>
                """
            else:
                # Only 2026.05 data
                mock_res.text = """
                <html><body><table>
                    <tr><td>2026.05.29</td><td>1,500</td><td>-800</td><td>-600</td><td>-100</td><td>-50</td><td>-200</td><td>-100</td><td>-50</td><td>-100</td><td>-100</td></tr>
                </table></body></html>
                """
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        self.assertNotIn("🚨 <b>KOSPI 수급 분석기 실행 실패</b>", self.sent_telegram_messages[0])
        self.assertIn("기간별 누적 매매동향", self.sent_telegram_messages[0])
        print("Scenario 9 Passed.")

    @patch('requests.get')
    def test_scenario_10_telegram_api_failure(self, mock_get):
        """Scenario 10: Telegram API sends error code (e.g., 400 Bad Request or 401 Unauthorized)."""
        print("\n--- Running Scenario 10: Telegram API Failure ---")
        self.telegram_status_code = 400
        self.telegram_response_text = '{"ok": false, "description": "Bad Request: can\'t parse entities"}'
        
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                mock_res.text = MOCK_INDEX_HTML_VALID
            else:
                mock_res.text = MOCK_INVESTOR_HTML_PAGE1_VALID
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        # Should gracefully log and return
        print("Scenario 10 Passed.")

    @patch('requests.get')
    def test_scenario_11_html_unescaped_entities_in_parse(self, mock_get):
        """Scenario 11: Malicious HTML elements (like <, >, &) in parsed data causing Telegram HTML parse mode failure."""
        print("\n--- Running Scenario 11: HTML Unescaped Entities ---")
        
        def mock_get_side_effect(url, params=None, verify=False, timeout=20):
            mock_res = MagicMock()
            mock_res.status_code = 200
            target_url = params.get("url", "") if params else ""
            if "sise_index_day.nhn" in target_url:
                # Contain raw '<' or '>' in change or fluc rate
                mock_res.text = """
                <html><body><table class="type_1">
                    <tr><td>2026.06.10</td><td>2,650.50</td><td>▲ <15.20></td><td>+0.58% & test</td></tr>
                </table></body></html>
                """
            else:
                mock_res.text = MOCK_INVESTOR_HTML_PAGE1_VALID
            return mock_res
            
        mock_get.side_effect = mock_get_side_effect
        
        with patch('sys.argv', ['kospi_investor_tracker.py', '--test']):
            kospi_investor_tracker.main()
            
        self.assertTrue(len(self.sent_telegram_messages) > 0)
        msg = self.sent_telegram_messages[0]
        # Verify that <15.20> has been escaped to &lt;15.20&gt;
        self.assertIn("&lt;15.20&gt;", msg)
        # Verify that & has been escaped to &amp;
        self.assertIn("+0.58% &amp; test", msg)
        print("Scenario 11 Passed.")

if __name__ == "__main__":
    unittest.main()
