# PhantomBuster Quick Start - 3 Steps

## ✅ What's Already Done

The endpoint is **already coded and ready to use**! I just need you to add 2 values:

## 🔑 Step 1: Get Your PhantomBuster API Key (1 minute)

1. Go to https://phantombuster.com/
2. Log in
3. Click profile icon → **Settings** → **API**
4. Copy your API key

## 🤖 Step 2: Get Your Agent ID (1 minute)

1. Go to https://phantombuster.com/phantombuster
2. Find **"LinkedIn Search Export"** agent (or create one)
3. Click on it
4. Look at the URL:
   ```
   https://phantombuster.com/phantombuster?agentId=YOUR_AGENT_ID_HERE
   ```
5. Copy the number after `agentId=`

## 📝 Step 3: Update .env File (30 seconds)

Open `server/.env` and replace these two lines:

```env
PHANTOMBUSTER_API_KEY=your_phantombuster_api_key_here
PHANTOMBUSTER_SEARCH_AGENT_ID=your_agent_id_here
```

With your actual values:

```env
PHANTOMBUSTER_API_KEY=abc123xyz456...
PHANTOMBUSTER_SEARCH_AGENT_ID=123456789
```

**Everything else is already configured!**

---

## 🧪 Test It

### Option 1: Use the Test Script

```bash
python test_phantombuster.py
```

### Option 2: Use cURL

```bash
curl -X POST http://localhost:8000/phantombuster/linkedin-search \
  -H "Content-Type: application/json" \
  -d '{"query": "Waterloo girls", "limit": 5}'
```

### Option 3: Use Your Frontend

```javascript
const response = await fetch('http://localhost:8000/phantombuster/linkedin-search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Waterloo girls',
    limit: 5
  })
});

const data = await response.json();
console.log('Found profiles:', data.profiles);
```

---

## 📡 The Endpoint

```
POST http://localhost:8000/phantombuster/linkedin-search
```

**Simple Request:**
```json
{
  "query": "Waterloo girls",
  "limit": 5
}
```

**Response:**
```json
{
  "query": "Waterloo girls",
  "limit": 5,
  "profiles": [
    {
      "profile_url": "https://www.linkedin.com/in/...",
      "name": "Jane Doe",
      "headline": "Software Engineer at Google",
      "location": "Waterloo, Ontario",
      "raw": { /* full data */ }
    }
  ],
  "container_id": "12345",
  "output_url": "https://..."
}
```

---

## ⚙️ What's Already Configured

All of this is **already set in your `.env`**:

- ✅ LinkedIn session cookie
- ✅ Identity ID
- ✅ User agent
- ✅ Search parameters (category, connection degrees, etc.)
- ✅ Default search URL
- ✅ Enrichment settings

**You only need to add the API key and Agent ID!**

---

## 🚀 Next Steps

Once it's working, you can:

1. **Replace SAMPLE_CARDS** with real LinkedIn profiles
2. **Add a "Fetch New Profiles"** button in Pack Opening
3. **Customize search queries** based on user preferences
4. **Cache results** to avoid repeated API calls

See [PHANTOMBUSTER_SETUP.md](./PHANTOMBUSTER_SETUP.md) for detailed documentation!

---

That's it! Just add those 2 values and you're ready to search LinkedIn! 🎉
