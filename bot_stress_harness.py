# -*- coding: utf-8 -*-
"""
K-Dual Momentum Bot Stress Test Harness
Verifies all 6 fail-safe guardrails over 5+ iterations in mock sandbox environments.
"""
import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Windows 콘솔 인코딩 대응
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# 대상 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import kis_bot_multi

@patch('kis_bot_multi.time.sleep', MagicMock())
class TestBotSafetyHarness(unittest.TestCase):
    
    def setUp(self):
        # 테스트 전역 설정값 보존 및 임시 mock 객체 준비
        self.original_mock = kis_bot_multi.KIS_MOCK
        self.original_dry = kis_bot_multi.KIS_DRY_RUN
        self.original_max_amount = kis_bot_multi.MAX_ORDER_AMOUNT
        
        # 기본값 리셋
        kis_bot_multi.KIS_MOCK = True
        kis_bot_multi.KIS_DRY_RUN = False
        kis_bot_multi.MAX_ORDER_AMOUNT = 100000000 # 1억 원
        
    def tearDown(self):
        # 원본 설정 복구
        kis_bot_multi.KIS_MOCK = self.original_mock
        kis_bot_multi.KIS_DRY_RUN = self.original_dry
        kis_bot_multi.MAX_ORDER_AMOUNT = self.original_max_amount

    @patch('kis_bot_multi.requests.get')
    @patch('kis_bot_multi.submit_order')
    def test_scenario_1_normal_rebalancing(self, mock_submit, mock_get):
        """[시나리오 1] 정상 리밸런싱 루프 검증 (30회 반복)"""
        print("\n=== [테스트 시나리오 1] 정상 리밸런싱 루프 검증 (30회 반복) ===")
        
        # 1. Mocking 잔고 API 응답
        mock_balance_res = MagicMock()
        mock_balance_res.status_code = 200
        mock_balance_res.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상 처리되었습니다.",
            "output1": [
                {"pdno": "360750", "hldg_qty": "10", "prpr": "10000", "evlu_amt": "100000"} # 기존 비타겟 보유 자산
            ],
            "output2": [
                {"dnca_tot_amt": "5000000", "prvs_rcvb_evt_amt": "5000000"} # 예수금 500만원
            ]
        }
        
        # 2. Mocking 현재가 API 응답
        mock_price_res = MagicMock()
        mock_price_res.status_code = 200
        mock_price_res.json.return_value = {
            "rt_cd": "0",
            "output": {"stck_prpr": "50000"} # 타겟 종목 현재가 50,000원
        }
        
        # GET 호출 분기 매핑
        def get_side_effect(url, **kwargs):
            if "inquire-balance" in url:
                return mock_balance_res
            elif "inquire-price" in url:
                return mock_price_res
            return MagicMock()
            
        mock_get.side_effect = get_side_effect
        
        # 주문 제출 응답 성공 모킹
        mock_submit.return_value = {
            "rt_cd": "0",
            "msg1": "주문 접수 완료",
            "output": {"ODNO": "123456"}
        }

        # 30회 연속 반복 테스트를 수행하여 리밸런싱 프로세스 무결성 검증 (메모리 오염, 변수 스택 오버플로우 방지)
        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            acc = {"name": "모의_개인주식계좌", "cano": "50189317", "prdt_cd": "01"}
            target_ticker = "069500" # 타겟 자산 (KODEX 200)
            
            # 리밸런싱 수행
            res_msg = kis_bot_multi.rebalance_account("mock_token", acc, target_ticker)
            
            # Assertions
            self.assertIn("리밸런싱 수행 완료", res_msg)
            self.assertIn("069500", res_msg)
            
            # 매도 주문이 시장가(00)로 1회 발행되었는지 검증
            mock_submit.assert_any_call("mock_token", "50189317", "01", "360750", 10, "SELL", ord_dvsn="00")
            # 매수 주문이 지정가(01, curr_price=50000)로 1회 발행되었는지 검증
            # 500만원 예수금의 98%는 490만원, 490만원 / 5만원 = 98주
            mock_submit.assert_any_call("mock_token", "50189317", "01", "069500", 98, "BUY", price=50000.0, ord_dvsn="01")
            
            # 호출 횟수 리셋
            mock_submit.reset_mock()
            
        print("✅ [성공] 시나리오 1: 30회 연속 무결성 검증 완료!")

    @patch('kis_bot_multi.requests.get')
    def test_scenario_2_insufficient_margin(self, mock_get):
        """[시나리오 2] 예수금 부족 대응 테스트 (30회 반복)"""
        print("\n=== [테스트 시나리오 2] 예수금 부족 대응 테스트 (30회 반복) ===")
        
        # 1. 예수금이 극단적으로 낮은(100원) 잔고 리스폰스 모킹
        mock_balance_res = MagicMock()
        mock_balance_res.status_code = 200
        mock_balance_res.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상 처리",
            "output1": [],
            "output2": [{"dnca_tot_amt": "100"}] # 예수금 100원
        }
        
        mock_price_res = MagicMock()
        mock_price_res.status_code = 200
        mock_price_res.json.return_value = {
            "rt_cd": "0",
            "output": {"stck_prpr": "50000"} # 1주당 5만원
        }
        
        mock_get.side_effect = lambda url, **kwargs: mock_balance_res if "inquire-balance" in url else mock_price_res

        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            acc = {"name": "모의_개인주식계좌", "cano": "50189317", "prdt_cd": "01"}
            res_msg = kis_bot_multi.rebalance_account("mock_token", acc, "069500")
            
            # Assertions: 100원으로는 5만원짜리 주식을 1주도 살 수 없으므로 예수금 부족 취소가 떨어져야 함.
            self.assertIn("예수금 부족 주문 취소", res_msg)
            
        print("✅ [성공] 시나리오 2: 예수금 부족 방어 30회 연속 검증 완료!")

    @patch('kis_bot_multi.requests.get')
    @patch('kis_bot_multi.submit_order')
    def test_scenario_3_fail_fast_on_sell_error(self, mock_submit, mock_get):
        """[시나리오 3] 청산 매도 실패 시 즉시 중단(Fail-Fast) 테스트 (30회 반복)"""
        print("\n=== [테스트 시나리오 3] 청산 매도 실패 시 즉시 중단(Fail-Fast) 테스트 (30회 반복) ===")
        
        # 보유 자산이 존재하는 잔고
        mock_balance_res = MagicMock()
        mock_balance_res.status_code = 200
        mock_balance_res.json.return_value = {
            "rt_cd": "0",
            "output1": [{"pdno": "360750", "hldg_qty": "5", "prpr": "10000", "evlu_amt": "50000"}],
            "output2": [{"dnca_tot_amt": "1000000"}]
        }
        mock_get.side_effect = lambda url, **kwargs: mock_balance_res
        
        # 청산 매도 주문이 'API 에러(rt_cd="9")'를 리턴한다고 모킹
        mock_submit.return_value = {
            "rt_cd": "9",
            "msg1": "잔고에 매도불가 수량이 포함되어 있습니다."
        }

        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            acc = {"name": "모의_개인주식계좌", "cano": "50189317", "prdt_cd": "01"}
            
            # Assertions: 매도 주문 실패 시 Exception이 던져지고 리밸런싱이 강제 폭파되는지 검증
            with self.assertRaises(Exception) as context:
                kis_bot_multi.rebalance_account("mock_token", acc, "069500")
                
            self.assertIn("Fail-Fast 매도 실패", str(context.exception))
            
            # Fail-Fast 장치 덕분에 매수 단계로 진입하지 않아 BUY 주문이 단 한 건도 시도되지 않아야 함
            for call in mock_submit.call_args_list:
                # call[0]의 4번째 인자(order_type) 확인
                if len(call[0]) > 4:
                    self.assertNotEqual(call[0][4], "BUY")
                
        print("✅ [성공] 시나리오 3: Fail-Fast 차단 및 전량 청산 안전 잠금 30회 연속 검증 완료!")

    @patch('kis_bot_multi.requests.get')
    def test_scenario_4_fat_finger_limit(self, mock_get):
        """[시나리오 4] Fat Finger 방지용 주문 제한 금액 상한 차단 테스트 (30회 반복)"""
        print("\n=== [테스트 시나리오 4] Fat Finger 방지용 주문 제한 금액 상한 차단 테스트 (30회 반복) ===")
        
        # 1. 2억 원의 대량 예수금 존재 모킹
        mock_balance_res = MagicMock()
        mock_balance_res.status_code = 200
        mock_balance_res.json.return_value = {
            "rt_cd": "0",
            "output1": [],
            "output2": [{"dnca_tot_amt": "200000000"}] # 예수금 2억
        }
        
        # 현재가 5만원
        mock_price_res = MagicMock()
        mock_price_res.status_code = 200
        mock_price_res.json.return_value = {
            "rt_cd": "0",
            "output": {"stck_prpr": "50000"}
        }
        
        mock_get.side_effect = lambda url, **kwargs: mock_balance_res if "inquire-balance" in url else mock_price_res
        
        # 안전선 상한을 5000만원으로 설정하여 2억원 예수금 전량 주문 발행 시 차단되게 세팅
        kis_bot_multi.MAX_ORDER_AMOUNT = 50000000 # 5000만원
        
        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            acc = {"name": "모의_개인주식계좌", "cano": "50189317", "prdt_cd": "01"}
            
            # Assertions: 주문 예상액이 5천만원을 넘으므로 ValueError가 솟구쳐 나와야 함
            with self.assertRaises(ValueError) as context:
                kis_bot_multi.rebalance_account("mock_token", acc, "069500")
                
            self.assertIn("Fat Finger 차단", str(context.exception))
            
        print("✅ [성공] 시나리오 4: 대형 주문 오폭 차단 30회 연속 검증 완료!")

    def test_scenario_5_pension_asset_isolation(self):
        """[시나리오 5] 연금저축 계좌(22 & 이름에 '연금' 포함) 비정상 자산 차단 테스트 (30회 반복)"""
        print("\n=== [테스트 시나리오 5] 연금저축 계좌 비정상 자산 차단 테스트 (30회 반복) ===")
        
        # 매수 격리 위반 대상 종목: 삼성전자("005930")
        illegal_ticker = "005930"
        
        # 케이스 A: 실전 연금저축계좌 (상품코드 22)
        acc_real = {"name": "실전_연금저축계좌", "cano": "12345678", "prdt_cd": "22"}
        # 케이스 B: 모의 연금저축대체계좌 (상품코드 01이나 이름에 '연금' 포함)
        acc_mock = {"name": "모의_연금대체계좌", "cano": "87654321", "prdt_cd": "01"}
        
        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            
            # A 실전 연금 격리 작동 확인
            with self.assertRaises(ValueError) as context_a:
                kis_bot_multi.rebalance_account("mock_token", acc_real, illegal_ticker)
            self.assertIn("보안 침해 예방", str(context_a.exception))
            
            # B 모의 연금 격리 작동 확인 (동기화 완료 부분)
            with self.assertRaises(ValueError) as context_b:
                kis_bot_multi.rebalance_account("mock_token", acc_mock, illegal_ticker)
            self.assertIn("보안 침해 예방", str(context_b.exception))
            
        print("✅ [성공] 시나리오 5: 연금 계좌 비정상 개별자산 원천격리 30회 연속 검증 완료!")

    @patch('kis_bot_multi.get_actual_rebalance_date')
    @patch('kis_bot_multi.is_market_open')
    @patch('kis_bot_multi.send_telegram')
    def test_scenario_6_market_closed_gatekeeper(self, mock_send, mock_is_open, mock_get_date):
        """[시나리오 6] 장외 시간 전역 가동 차단 Gatekeeper 테스트 (30회 반복)"""
        print("\n=== [테스트 시나리오 6] 장외 시간 전역 가동 차단 Gatekeeper 테스트 (30회 반복) ===")
        
        # 장외 시간(시장 영업일 외) 상황 모킹
        mock_is_open.return_value = False
        # 날짜 체크 통과용 모킹 (오늘을 무조건 리밸런싱 실행일로 만듦)
        import datetime
        mock_get_date.return_value = datetime.date.today()
        
        # 실전 투자 가동 모드로 설정
        kis_bot_multi.KIS_MOCK = False
        kis_bot_multi.KIS_DRY_RUN = False

        for i in range(1, 31):
            print(f" -> Iteration {i}/30 실행 중...")
            
            # Assertions: sys.exit(1)로 가동이 즉시 중단되어야 함
            with self.assertRaises(SystemExit) as context:
                kis_bot_multi.main()
                
            self.assertEqual(context.exception.code, 1)
            mock_send.assert_any_call("🚨 [가동 즉시 중단] 현재 주식시장 정규 운영 시간(평일 09:00 ~ 15:30)이 아닙니다. 안전을 위해 실행을 즉시 중단합니다.")
            
        print("✅ [성공] 시나리오 6: 장외 시간 무단 구동 즉각 셧다운 30회 연속 검증 완료!")

if __name__ == '__main__':
    unittest.main()
