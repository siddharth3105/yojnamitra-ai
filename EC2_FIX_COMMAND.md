# EC2 Deployment - Fix Divergent Branches

## The Issue
Git has divergent branches and needs to know how to reconcile them.

## Solution - Copy-Paste This Command

```bash
cd yojnamitra-ai && git fetch origin && git reset --hard origin/main && pkill -f streamlit && nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

This will:
1. Fetch latest code from GitHub
2. Force reset to match GitHub exactly (discard local changes)
3. Kill old Streamlit process
4. Start new Streamlit with fixed code

## Verify It's Running

```bash
tail -20 streamlit.log
```

Look for: "You can now view your Streamlit app in your browser"

## Test Your App

Open: http://13.201.55.10:8501

---

**That's it! Your fixed app will be live!** 🚀
