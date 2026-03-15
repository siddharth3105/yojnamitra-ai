# How to Test the Step-by-Step Guide Feature

## Quick Test (2 minutes)

### Test 1: Using the Button
1. Run the app: `streamlit run yojnamitra_ai.py`
2. Complete your profile (name, age, state, income, occupation)
3. Wait for schemes to appear
4. Click the "📝 Apply Guide" button on any scheme
5. **Expected**: You should see a complete guide with all 5 steps:
   - STEP 1: Open Application Link & Login
   - STEP 2: Find the Scheme
   - STEP 3: Fill All Required Details
   - STEP 4: Upload Required Documents
   - STEP 5: Review, Submit & Get Confirmation

### Test 2: Using Chat
1. After completing profile and seeing schemes
2. Type in chat: "How to apply for PM-KISAN?"
3. **Expected**: Same complete 5-step guide

### Test 3: Different Variations
Try these messages:
- "Give me step-by-step guidance for Ayushman Bharat"
- "I want to apply for MUDRA loan, help me"
- "Application guide for NSP scholarship"
- "Help me apply for PM Awas Yojana"

All should return complete 5-step guides.

## What Was Fixed

### Before ❌
- Button click → AI sometimes gave incomplete response
- Only 1000 tokens → Guide got cut off
- No fallback → Users got stuck
- Weak keyword detection → Missed some requests

### After ✅
- Button click → Always complete 5-step guide
- 2000 tokens → Enough space for full guide
- Fallback system → Guarantees complete guide
- Enhanced detection → Catches all variations

## Key Improvements

1. **Enhanced Keyword Detection**
   - Now detects: "step-by-step", "how to apply", "apply for", "application guide", "guidance", "help me apply"
   - Case-insensitive matching
   - Works with any scheme name

2. **Increased Token Limit**
   - From 1000 → 2000 tokens
   - Ensures complete guides never get cut off

3. **Fallback Guide System**
   - Validates AI response has all 5 steps
   - If missing steps, provides complete fallback guide
   - Extracts scheme name and URL automatically

4. **Better Button Message**
   - Old: "I want to apply for {scheme}. Please give me step-by-step guidance."
   - New: "How to apply for {scheme}? Please give me complete step-by-step guidance with all 5 steps."

5. **Stronger AI Instructions**
   - Added "CRITICAL INSTRUCTION" and "MANDATORY" keywords
   - Explicit requirement for all 5 steps
   - Template embedded in prompt

## Troubleshooting

### If guide is still incomplete:
1. Check logs for: "AI response only had X/5 steps, providing fallback guide"
2. This means fallback kicked in (which is good!)
3. Fallback should provide complete guide

### If button doesn't work:
1. Make sure profile is complete (5/5 fields)
2. Make sure schemes are displayed
3. Check browser console for errors
4. Try typing the message manually instead

### If AI gives wrong response:
1. Fallback system should catch this
2. Check if scheme name is recognized
3. Add scheme to fallback mapping if needed

## Expected Response Format

```
Let me guide you step-by-step to apply for PM-KISAN:

**STEP 1: Open Application Link & Login**
Click this link: https://pmkisan.gov.in

If you're a new user:
- Click 'Register' or 'New Registration'
- Enter your mobile number
- Verify OTP sent to your phone
- Create a strong password
- Login with your credentials

If you already have an account:
- Click 'Login'
- Enter your username and password

**STEP 2: Find the Scheme**
After logging in:
- Use the search bar and type 'PM-KISAN'
- OR navigate to the relevant category (Agriculture/Education/Health/Business)
- Click on the scheme name to open the application form

**STEP 3: Fill All Required Details**
Fill in these details carefully:
- Personal Information: Full Name (exactly as per Aadhar), Date of Birth, Gender
- Contact Details: Mobile number, Email address, Complete address with Pin Code
- Identity Details: Aadhar number, PAN card number (if required)
- Bank Details: Bank account number, IFSC code, Bank name
- Scheme-specific information (varies by scheme)

IMPORTANT: Make sure all details match your Aadhar card exactly!
Fill all mandatory fields (marked with * asterisk)

**STEP 4: Upload Required Documents**
Upload these documents if the form asks for them:
- Aadhar Card (PDF or JPG format, maximum 2MB)
- Passport size photograph (JPG format, maximum 100KB)
- Bank Passbook or Cancelled Cheque (first page showing account details)
- Income Certificate (if required for the scheme)
- Any other scheme-specific documents

To upload: Click 'Choose File' or 'Browse' → Select the document from your computer → Click 'Upload'

Note: Some schemes may not require document upload at this stage

**STEP 5: Review, Submit & Get Confirmation**
Before submitting:
- Carefully review all the information you entered
- Make sure everything is correct
- Tick the declaration checkbox (if present)
- Click the 'Submit' or 'Apply' button

After submission:
- You will see a confirmation message
- SAVE YOUR APPLICATION ID (example: PMKISAN2026XXXXX)
- Take a screenshot of the confirmation page
- You will receive a confirmation SMS on your registered mobile number
- You may also receive a confirmation email
- Save the tracking link to check your application status later

Congratulations! Your application is submitted. You'll receive confirmation via SMS/Email shortly.

Need help with any specific step? Just ask! 😊
```

## Success Criteria

✅ All 5 steps are present
✅ Each step has detailed instructions
✅ Scheme name and URL are correct
✅ Instructions are clear and actionable
✅ Confirmation details are included
✅ Friendly tone maintained

## Files Changed

- `yojnamitra_ai.py` - Main application file with all fixes

## Deployment

After testing locally:
1. Commit changes: `git add yojnamitra_ai.py`
2. Commit: `git commit -m "Fix: Step-by-step guide feature now working"`
3. Push: `git push origin main`
4. AWS Amplify will auto-deploy in ~2 minutes

---

**Status**: ✅ READY TO TEST
**Priority**: HIGH (Critical feature for hackathon)
**Impact**: Users can now successfully apply for schemes
