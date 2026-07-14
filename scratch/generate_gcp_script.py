import os

def main():
    # Paths to local files
    workspace = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    kis_bot_path = os.path.join(workspace, "kis_bot_multi.py")
    main_path = os.path.join(workspace, "main.py")
    req_path = os.path.join(workspace, "requirements.txt")
    
    # Read files
    with open(kis_bot_path, "r", encoding="utf-8") as f:
        kis_bot_content = f.read()
        
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
        
    with open(req_path, "r", encoding="utf-8") as f:
        req_content = f.read()

    # Create the shell script content
    shell_script = f"""#!/bin/bash
set -e

echo "=================================================="
echo "🚀 [Antigravity] GCP Deploy & Schedule Helper"
echo "=================================================="
echo ""

# 1. Find the existing Cloud Function
echo ">> Searching for your Cloud Function..."
FUNC_INFO=$(gcloud functions list --format="value(name,region)" | grep -i rebalancing | head -n 1)

if [ -z "$FUNC_INFO" ]; then
  FUNC_INFO=$(gcloud functions list --format="value(name,region)" | head -n 1)
fi

if [ -z "$FUNC_INFO" ]; then
  echo "❌ Error: Cloud Function not found. Please make sure you are in the correct GCP project."
  exit 1
fi

FUNC_NAME=$(echo $FUNC_INFO | awk '{{print $1}}')
FUNC_REGION=$(echo $FUNC_INFO | awk '{{print $2}}')
echo "✅ Found Cloud Function: '$FUNC_NAME' in region '$FUNC_REGION'"
echo ""

# 2. Setup deploy directory
echo ">> Preparing deploy directory..."
mkdir -p ~/gcp_deploy_temp
cd ~/gcp_deploy_temp
rm -f *

# 3. Write code files
echo ">> Writing code files..."

cat << 'EOF' > main.py
{main_content}
EOF

cat << 'EOF' > kis_bot_multi.py
{kis_bot_content}
EOF

cat << 'EOF' > requirements.txt
{req_content}
EOF

# 4. Deploy the Cloud Function
echo ">> Deploying Cloud Function (this will take a few minutes)..."
gcloud functions deploy $FUNC_NAME \\
  --region=$FUNC_REGION \\
  --source=. \\
  --entry-point=trigger_rebalancing

# 5. Get HTTP Trigger URL
URL=$(gcloud functions describe $FUNC_NAME --region=$FUNC_REGION --format="value(httpsTrigger.url)")
echo "✅ Cloud Function deployed successfully!"
echo "🔗 Trigger URL: $URL"
echo ""

# 6. Delete old temp job if exists
echo ">> Checking for existing temporary scheduler job..."
gcloud scheduler jobs delete temp-rebalance-job --location=$FUNC_REGION --quiet 2>/dev/null || true

# 7. Create temporary Cloud Scheduler job for tomorrow (June 18) at 09:30 AM KST
echo ">> Scheduling one-time execution for tomorrow (June 18) at 09:30 AM KST..."
gcloud scheduler jobs create http temp-rebalance-job \\
  --schedule="30 9 18 6 *" \\
  --time-zone="Asia/Seoul" \\
  --uri="${{URL}}?force=true" \\
  --http-method=GET \\
  --location=$FUNC_REGION \\
  --quiet

echo ""
echo "=================================================="
echo "🎉 Google Cloud Setup Completed Successfully!"
echo "- Cloud Function '$FUNC_NAME' is updated with timezone and TPS limit fixes."
echo "- Scheduled a one-time trigger for tomorrow at 09:30 AM KST (temp-rebalance-job)."
echo "- Next month's schedule is untouched."
echo "=================================================="
"""

    # Write output shell script
    output_path = os.path.join(workspace, "gcp_deploy_and_schedule.sh")
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(shell_script)
        
    print(f"Generated script at: {output_path}")

if __name__ == "__main__":
    main()
