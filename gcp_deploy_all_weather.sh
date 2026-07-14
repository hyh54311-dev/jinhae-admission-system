#!/bin/bash
set -e

echo "=================================================="
echo "🚀 [All Weather] GCP Cloud Function Deploy Helper"
echo "=================================================="
echo ""

FUNC_NAME="all-weather-bot"
FUNC_REGION="asia-northeast3" # Seoul Region

# 1. Setup deploy directory
echo ">> Preparing deploy directory..."
ORIG_DIR=$(pwd)
mkdir -p ~/gcp_deploy_all_weather
cd ~/gcp_deploy_all_weather
rm -f *

# Copy code and configuration
if [ -f "$ORIG_DIR/all_weather_quant_bot.py" ]; then
  cp "$ORIG_DIR/all_weather_quant_bot.py" .
  echo "✅ Copied all_weather_quant_bot.py"
else
  echo "🚨 Error: all_weather_quant_bot.py not found in $ORIG_DIR. Deployment aborted."
  exit 1
fi

if [ -f "$ORIG_DIR/.env" ]; then
  cp "$ORIG_DIR/.env" .
  echo "✅ Copied .env file"
else
  echo "🚨 Error: .env file not found in $ORIG_DIR. Deployment aborted."
  exit 1
fi

# 2. Write main.py Cloud Function wrapper
echo ">> Writing Cloud Function wrapper (main.py)..."
cat << 'EOF' > main.py
# -*- coding: utf-8 -*-
import os
import sys
import importlib
from unittest.mock import patch
import functions_framework

# 봇 패키지 임포트를 위해 현재 경로 추가
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
if BOT_DIR not in sys.path:
    sys.path.append(BOT_DIR)

@functions_framework.http
def trigger_all_weather(request):
    """
    구글 클라우드 펑션 HTTP 트리거 래퍼.
    - force=true : 강제 리밸런싱 실행
    - test=true  : 모의 시뮬레이션 모드 실행
    """
    # 매 요청마다 상태 혼선 방지를 위해 모듈을 dynamic import 및 reload
    import all_weather_quant_bot
    importlib.reload(all_weather_quant_bot)
    
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
    test_run = str(args.get('test', 'false')).lower() in ('true', '1', 'yes')
    
    # 동시 요청 시 sys.argv 덮어쓰기 오염을 막기 위해 가상 argv로 격리 조치 (patch 사용)
    mock_argv = ['all_weather_quant_bot.py']
    if force_run:
        mock_argv.append('--force')
    if test_run:
        mock_argv.append('--test')
        
    try:
        print(">> GCP Cloud Function Triggered.")
        print(f"   - Force Run: {force_run}")
        print(f"   - Test Run: {test_run}")
        
        # patch 환경 안에서만 sys.argv가 mock_argv로 작동하므로 스레드/동시성 안전 확보
        with patch.object(sys, 'argv', mock_argv):
            all_weather_quant_bot.main()
        
        return {
            "status": "success",
            "message": "All Weather bot executed successfully.",
            "config": {"force": force_run, "test": test_run}
        }, 200
        
    except Exception as e:
        import traceback
        err_trace = traceback.format_exc()
        print(f"🚨 [Error] GCP All Weather execution failed: {e}")
        print(err_trace)
        return {
            "status": "error",
            "message": f"Execution failed: {str(e)}",
            "trace": err_trace
        }, 500

EOF

# 3. Write requirements.txt
echo ">> Writing requirements.txt..."
cat << 'EOF' > requirements.txt
requests==2.31.0
python-dotenv==1.0.1
functions-framework==3.5.0
urllib3==2.2.1
EOF

# 4. Deploy the Cloud Function
echo ">> Deploying Cloud Function (this will take a few minutes)..."
gcloud functions deploy $FUNC_NAME \
  --gen2 \
  --region=$FUNC_REGION \
  --runtime=python312 \
  --trigger-http \
  --allow-unauthenticated \
  --source=. \
  --entry-point=trigger_all_weather \
  --memory=512Mi \
  --timeout=300s

# 5. Get HTTP Trigger URL
echo ">> Querying HTTP Trigger URL..."
URL=$(gcloud functions describe $FUNC_NAME --region=$FUNC_REGION --format="value(url)")
if [ -z "$URL" ]; then
  URL=$(gcloud functions describe $FUNC_NAME --region=$FUNC_REGION --format="value(httpsTrigger.url)")
fi
if [ -z "$URL" ]; then
  URL=$(gcloud functions describe $FUNC_NAME --region=$FUNC_REGION --format="value(serviceConfig.uri)")
fi
echo "✅ Cloud Function deployed successfully!"
echo "🔗 Trigger URL: $URL"
echo ""

# 6. Delete old scheduler job if exists to prevent duplication
echo ">> Deleting old scheduler job if exists..."
gcloud scheduler jobs delete all-weather-daily-job --location=$FUNC_REGION --quiet 2>/dev/null || true

# 7. Create Google Cloud Scheduler job for 11:00 PM KST (Mon-Fri)
echo ">> Scheduling daily cron execution for Mon-Fri at 11:00 PM KST..."
gcloud scheduler jobs create http all-weather-daily-job \
  --schedule="0 23 * * 1-5" \
  --time-zone="Asia/Seoul" \
  --uri="${URL}" \
  --http-method=GET \
  --location=$FUNC_REGION \
  --quiet

echo ""
echo "=================================================="
echo "🎉 Google Cloud Serverless Setup Completed!"
echo "- Cloud Function '$FUNC_NAME' is deployed."
echo "- Scheduler job 'all-weather-daily-job' is registered."
echo "- Trigger time: Monday to Friday at 11:00 PM KST."
echo "=================================================="
cd $ORIG_DIR
rm -rf ~/gcp_deploy_all_weather
