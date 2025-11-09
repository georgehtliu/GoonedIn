# PhantomBuster Returning 1000 Profiles Instead of 10

## The Problem

Even though your `.env` file has:
```
PHANTOMBUSTER_RESULTS_PER_LAUNCH=10
PHANTOMBUSTER_RESULTS_PER_SEARCH=10
```

PhantomBuster is still searching for 1000 profiles.

## Why This Happens

**PhantomBuster agents have their own configuration saved on the website** that can override the parameters sent via API.

## The Fix

You need to update your agent's configuration directly on PhantomBuster's website:

### Step 1: Go to Your Agent
1. Visit: https://phantombuster.com/phantombuster
2. Find your agent with ID: `3743298056749302`
3. Click on it to open the configuration page

### Step 2: Update the Settings
Look for these settings in the agent configuration form:
- **Number of results per launch**: Change to `10`
- **Number of results per search**: Change to `10`
- **Number of lines per launch**: Change to `10`

### Step 3: Save the Agent
Click "Save" or "Update" at the bottom of the form.

### Step 4: Test Again
Run your curl command:
```bash
curl -X POST http://localhost:8000/phantombuster/linkedin-search \
  -H "Content-Type: application/json" \
  -d '{"query": "Waterloo girls", "limit": 5}'
```

Now it should only scrape 10 profiles instead of 1000.

---

## Alternative: Use Agent Arguments (If Supported)

Some PhantomBuster agents allow you to override settings via API arguments. Our code already tries to do this by sending:

```json
{
  "numberOfResultsPerLaunch": 10,
  "numberOfResultsPerSearch": 10,
  "numberOfLinesPerLaunch": 10
}
```

However, if the agent's web configuration locks these values, the API parameters won't work.

---

## Summary

**The issue is not in your code** - it's in the PhantomBuster agent's saved configuration on their website. You must update it there manually.
