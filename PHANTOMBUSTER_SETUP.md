# PhantomBuster LinkedIn Search Setup

## What You Need to Add

The `.env` file has been set up with your credentials, but you need to add:

1. **PHANTOMBUSTER_API_KEY** - Your PhantomBuster API key
2. **PHANTOMBUSTER_SEARCH_AGENT_ID** - Your LinkedIn Search Export agent ID

## Where to Find These:

### 1. PhantomBuster API Key
1. Go to https://phantombuster.com/
2. Log in to your account
3. Click your profile icon (top right)
4. Go to "Settings" → "API"
5. Copy your API key
6. Paste it in `.env` as `PHANTOMBUSTER_API_KEY`

### 2. Agent ID
1. Go to https://phantombuster.com/phantombuster
2. Find or create a "LinkedIn Search Export" agent
3. Click on the agent
4. Look at the URL - it will be something like:
   ```
   https://phantombuster.com/phantombuster?agentId=123456789
   ```
5. The number after `agentId=` is your PHANTOMBUSTER_SEARCH_AGENT_ID
6. Paste it in `.env`

---

## API Endpoint

The endpoint is already created at:

```
POST http://localhost:8000/phantombuster/linkedin-search
```

### Request Body (Simple):

```json
{
  "query": "Waterloo girls",
  "limit": 5
}
```

### Request Body (Advanced - All Options):

```json
{
  "query": "Waterloo girls",
  "limit": 5,
  "search_url": "https://www.linkedin.com/search/results/all/?keywords=waterloo%20girls&origin=GLOBAL_SEARCH_HEADER",
  "category": "People",
  "search_type": "linkedInSearchUrl",
  "connection_degrees": ["2", "3+"],
  "lines_per_launch": 10,
  "results_per_launch": 1000,
  "results_per_search": 1000,
  "enrich": true
}
```

### Response:

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
      "raw": { /* full profile data */ }
    },
    // ... more profiles
  ],
  "container_id": "12345",
  "output_url": "https://phantombuster-data.s3.amazonaws.com/..."
}
```

---

## How It Works

1. **Launch**: Sends a request to PhantomBuster to start the agent
2. **Poll**: Waits up to 3 minutes, checking every 5 seconds for completion
3. **Fetch**: Downloads the results from PhantomBuster's S3 bucket
4. **Parse**: Extracts profile data (name, headline, location, URL)
5. **Return**: Sends back up to `limit` profiles

---

## Testing with cURL

Once you add your API key and Agent ID:

```bash
curl -X POST http://localhost:8000/phantombuster/linkedin-search \
  -H "Content-Type: application/json" \
  -d '{"query": "Waterloo girls", "limit": 5}'
```

---

## Testing with the Frontend

You can create a simple test button in your app:

```javascript
const testPhantomBuster = async () => {
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
};
```

---

## Environment Variables Explained

### Required:
- `PHANTOMBUSTER_API_KEY` - Your PhantomBuster account API key
- `PHANTOMBUSTER_SEARCH_AGENT_ID` - The ID of your LinkedIn Search Export agent
- `PHANTOMBUSTER_SESSION_COOKIE` - Your LinkedIn session cookie (already set)

### Optional (have defaults):
- `PHANTOMBUSTER_IDENTITY_ID` - Your PhantomBuster identity ID (already set)
- `PHANTOMBUSTER_USER_AGENT` - Browser user agent (already set)
- `PHANTOMBUSTER_CATEGORY` - Default: "People"
- `PHANTOMBUSTER_SEARCH_TYPE` - Default: "linkedInSearchUrl"
- `PHANTOMBUSTER_CONNECTION_DEGREES` - Default: "2,3+"
- `PHANTOMBUSTER_LINES_PER_LAUNCH` - Default: 10
- `PHANTOMBUSTER_RESULTS_PER_LAUNCH` - Default: 1000
- `PHANTOMBUSTER_RESULTS_PER_SEARCH` - Default: 1000
- `PHANTOMBUSTER_ENRICH` - Default: true
- `PHANTOMBUSTER_LINKEDIN_SEARCH_URL` - Default search URL

---

## Timeout Settings

- **Max Wait Time**: 180 seconds (3 minutes)
- **Poll Interval**: 5 seconds
- **HTTP Timeout**: 30 seconds per request

If the agent takes longer than 3 minutes, you'll get a timeout error.

---

## Error Messages

- `"PhantomBuster credentials are not configured"` - Missing API key or Agent ID
- `"PhantomBuster session cookie is not configured"` - Missing session cookie
- `"PhantomBuster launch did not return a container identifier"` - Agent launch failed
- `"PhantomBuster run ended with status: failed"` - Agent execution failed
- `"Timed out waiting for PhantomBuster results"` - Took longer than 3 minutes

---

## What You Need to Do Now

1. **Get your PhantomBuster API key** from https://phantombuster.com/
2. **Get your Agent ID** from the LinkedIn Search Export agent
3. **Update `.env`** with these two values:
   ```
   PHANTOMBUSTER_API_KEY=your_actual_key_here
   PHANTOMBUSTER_SEARCH_AGENT_ID=your_actual_agent_id_here
   ```
4. **Restart the backend server**
5. **Test the endpoint**!

---

## Example Usage in Your App

You could use this to populate the pack opening with real LinkedIn profiles instead of SAMPLE_CARDS:

```javascript
// In PackOpening.jsx or wherever you need profiles
const fetchRealProfiles = async () => {
  try {
    const response = await fetch('http://localhost:8000/phantombuster/linkedin-search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'Waterloo girls',
        limit: 5
      })
    });

    const data = await response.json();

    // Convert PhantomBuster profiles to your card format
    const cards = data.profiles.map((profile, index) => ({
      id: Date.now() + index,
      name: profile.name || 'Unknown',
      major: profile.headline || 'Not specified',
      company: profile.headline?.split(' at ')[1] || 'Not specified',
      image: null, // PhantomBuster doesn't provide images directly
      rarity: 'common', // You could randomize this
      bio: profile.headline || '',
      location: profile.location || 'Not specified',
      interests: [],
      age: null,
      experience: '',
      email: '',
      linkedin: profile.profile_url || ''
    }));

    return cards;
  } catch (error) {
    console.error('Failed to fetch profiles:', error);
    return [];
  }
};
```

---

That's it! Once you add your API key and Agent ID, the endpoint will work perfectly! 🚀
