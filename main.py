# -*- coding: utf-8 -*-
import os
import sys
import functions_framework

# Add the current directory to sys.path so Python can import kis_bot_multi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@functions_framework.http
def trigger_rebalancing(request):
    """
    Google Cloud Function HTTP Trigger Wrapper for K-Dual Momentum Bot.
    Supports query parameters for runtime overrides:
    - force=true  : Forces execution even if today is not the rebalancing date.
    - mock=true   : Runs in Mock Trading mode (overrides KIS_MOCK to True).
    - dry_run=true: Runs in Dry Run mode (overrides KIS_DRY_RUN to True).
    """
    import kis_bot_multi
    
    # Extract query parameters or JSON body (for easy manual testing in Cloud Functions console)
    args = {}
    if request.args:
        args.update(request.args)
    if request.is_json:
        try:
            body = request.get_json()
            if isinstance(body, dict):
                args.update(body)
        except Exception:
            pass
    
    force_run = str(args.get('force', 'false')).lower() in ('true', '1', 'yes')
    mock_run = str(args.get('mock', ''))
    dry_run = str(args.get('dry_run', ''))
    
    # 1. Handle force run flag via command line argument emulation
    if force_run:
        sys.argv = ['kis_bot_multi.py', '--force']
    else:
        sys.argv = ['kis_bot_multi.py']
        
    # 2. Backup original env vars
    orig_mock = os.environ.get("KIS_MOCK")
    orig_dry_run = os.environ.get("KIS_DRY_RUN")
    
    # 3. Apply overrides if specified
    if mock_run != '':
        is_mock_bool = mock_run.lower() in ('true', '1', 'yes')
        os.environ["KIS_MOCK"] = "True" if is_mock_bool else "False"
        kis_bot_multi.KIS_MOCK = is_mock_bool
        # Re-set key/url configurations dynamically
        if is_mock_bool:
            kis_bot_multi.APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
            kis_bot_multi.APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
            kis_bot_multi.URL_BASE = "https://openapivts.koreainvestment.com:29443"
            # Set ACCOUNTS dynamically
            kis_bot_multi.ACCOUNTS = []
            mock_cano1 = os.getenv("KIS_MOCK_CANO1", "")
            mock_cano2 = os.getenv("KIS_MOCK_CANO2", "")
            if mock_cano1:
                kis_bot_multi.ACCOUNTS.append({"name": "모의_주식계좌1", "cano": mock_cano1, "prdt_cd": "01"})
            if mock_cano2:
                kis_bot_multi.ACCOUNTS.append({"name": "모의_주식계좌2", "cano": mock_cano2, "prdt_cd": "01"})
        else:
            kis_bot_multi.APP_KEY = os.getenv("KIS_APP_KEY", "")
            kis_bot_multi.APP_SECRET = os.getenv("KIS_APP_SECRET", "")
            kis_bot_multi.URL_BASE = "https://openapi.koreainvestment.com:9443"
            kis_bot_multi.ACCOUNTS = [
                {"name": "연금저축계좌", "cano": os.getenv("KIS_PENSION_CANO", ""), "prdt_cd": "22"},
                {"name": "개인주식계좌", "cano": os.getenv("KIS_STOCK_CANO", ""), "prdt_cd": "01"}
            ]
            
    if dry_run != '':
        is_dry_bool = dry_run.lower() in ('true', '1', 'yes')
        os.environ["KIS_DRY_RUN"] = "True" if is_dry_bool else "False"
        kis_bot_multi.KIS_DRY_RUN = is_dry_bool
        
    try:
        print(">> GCP 서버리스 트리거 수신. 가동 모드:")
        print(f"   - Force Run: {force_run}")
        print(f"   - KIS_MOCK Override: {os.environ.get('KIS_MOCK', orig_mock)}")
        print(f"   - KIS_DRY_RUN Override: {os.environ.get('KIS_DRY_RUN', orig_dry_run)}")
        
        # Trigger the bot main execution
        kis_bot_multi.main()
        
        return {
            "status": "success",
            "message": "Rebalancing executed successfully in serverless environment.",
            "config": {
                "force": force_run,
                "mock": os.environ.get('KIS_MOCK', orig_mock),
                "dry_run": os.environ.get('KIS_DRY_RUN', orig_dry_run)
            }
        }, 200
        
    except Exception as e:
        import traceback
        err_trace = traceback.format_exc()
        print(f"🚨 [에러] GCP 리밸런싱 실행 실패: {e}")
        print(err_trace)
        return {
            "status": "error",
            "message": f"Execution failed: {str(e)}",
            "trace": err_trace
        }, 500
        
    finally:
        # Restore original environment variables to maintain stateless consistency
        if orig_mock is not None:
            os.environ["KIS_MOCK"] = orig_mock
        elif "KIS_MOCK" in os.environ:
            del os.environ["KIS_MOCK"]
            
        if orig_dry_run is not None:
            os.environ["KIS_DRY_RUN"] = orig_dry_run
        elif "KIS_DRY_RUN" in os.environ:
            del os.environ["KIS_DRY_RUN"]
