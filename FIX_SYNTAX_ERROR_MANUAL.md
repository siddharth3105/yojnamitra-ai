# Fix Syntax Error - Manual Steps for EC2

## Problem
Syntax error at line 725 in `yojnamitra_ai.py` - duplicate code after `else` block

## Solution
The `_fallback_response` function has duplicate unreachable code that needs to be removed.

## Manual Fix on EC2

### Step 1: Connect to EC2
Use EC2 Instance Connect (browser terminal)

### Step 2: Edit the file
```bash
cd yojnamitra-ai
nano yojnamitra_ai.py
```

### Step 3: Find line 725
Press `Ctrl + _` (underscore) and type `725` to jump to line 725

### Step 4: Delete duplicate code
You'll see this around line 725:
```python
        else:
            return f"Perfect {user_profile['name']} ji! Ab main aapke liye best government schemes dhundh raha hoon... 🔍"
        
        elif not user_profile.get('age'):    # <-- THIS LINE AND EVERYTHING BELOW IT IS DUPLICATE
            questions = [
                ...
```

**Delete everything from line 725 onwards** until you see the next class definition:
```python
class SchemeSearchEngine:
```

The function should end at line 722 with the `else` block and return statement.

### Step 5: Save and exit
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### Step 6: Restart Streamlit
```bash
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Step 7: Verify
```bash
# Check if running
ps aux | grep streamlit

# Check logs for errors
tail -f streamlit.log
```

Press `Ctrl + C` to stop viewing logs.

### Step 8: Test
Open: http://13.201.55.10:8501

---

## What the function should look like after fix:

```python
def _fallback_response(self, user_message: str, user_profile: Dict) -> str:
    """Fallback response when AI unavailable - simple and effective"""
    
    if not user_profile.get('name'):
        return "Hi! 👋 Main YojnaMitra-AI hoon..."
    
    elif not user_profile.get('age'):
        return f"Bahut achha {user_profile['name']} ji! Aapki age kitni hai?"
    
    elif not user_profile.get('state'):
        return f"Great {user_profile['name']} ji! Aap kis state se belong karte ho?..."
    
    elif not user_profile.get('income'):
        return f"Perfect {user_profile['name']} ji! Aapki yearly income kitni hai..."
    
    elif not user_profile.get('occupation'):
        return f"Nice {user_profile['name']} ji! Aap kya kaam karte ho?..."
    
    else:
        return f"Perfect {user_profile['name']} ji! Ab main aapke liye best government schemes dhundh raha hoon... 🔍"


class SchemeSearchEngine:
    """Search and match government schemes"""
```

**The function ends at the `else` block. No more `elif` statements after that!**

---

## Quick Command (Alternative)
If you want to download the fixed file directly from your local machine to EC2, you can use SCP or just copy-paste the corrected function.

---

**Status**: Ready to fix manually on EC2! 🛠️
