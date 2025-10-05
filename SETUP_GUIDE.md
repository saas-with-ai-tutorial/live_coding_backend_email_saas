# Gmail Auto-Sync Email SaaS - Setup Guide

This guide will help you set up the FastAPI backend that automatically polls Gmail every minute and syncs with the frontend dashboard.

## Features

✅ **Automatic Gmail Polling** - Polls Gmail every 60 seconds for new emails  
✅ **AI-Powered Action Item Extraction** - Uses LLM to identify and extract action items from emails  
✅ **JSON Storage** - Persists todos in JSON files for easy data management  
✅ **Real-time Dashboard** - Live status updates and manual sync controls  
✅ **Background Processing** - Non-blocking background task for continuous monitoring  

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** for the frontend
3. **Gmail Account** with App Password enabled
4. **OpenAI API Key** (or other LLM provider)

## Backend Setup

### 1. Gmail App Password Setup

1. Go to your Google Account settings: https://myaccount.google.com/
2. Enable 2-Factor Authentication if not already enabled
3. Go to App Passwords: https://myaccount.google.com/apppasswords
4. Create a new App Password for "Mail"
5. Save the generated 16-character password

### 2. Environment Variables

Create a `.env` file in the backend root directory:

```bash
# Gmail Credentials
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password

# OpenAI API Key (or other LLM provider)
OPENAI_API_KEY=your-openai-api-key

# Optional: LLM Model (default: openai/gpt-4o-mini)
LLM_MODEL=openai/gpt-4o-mini
```

### 3. Install Dependencies

```bash
cd live_coding_backend_email_saas
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start the Backend

```bash
# Option 1: Using the start script
./start_backend.sh

# Option 2: Using uvicorn directly
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

### 5. Verify Backend is Running

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Polling Status: http://localhost:8000/api/gmail/polling-status

## Frontend Setup

### 1. Install Dependencies

```bash
cd live_coding_frontend_email_saas
npm install
```

### 2. Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start the Frontend

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## How It Works

### Backend Architecture

1. **Gmail Poller Service** (`app/services/gmail_poller.py`)
   - Runs as a background task when FastAPI starts
   - Polls Gmail every 60 seconds for unread emails
   - Tracks processed emails to avoid duplicates

2. **Email Processor** (`src/core/email_processor.py`)
   - Uses LiteLLM to analyze email content
   - Extracts action items with priority and due dates
   - Returns structured data (ActionItem model)

3. **Storage** (`app/storage/memory_store.py`)
   - In-memory storage with JSON persistence
   - Saves todos to `data/todos.json`
   - Auto-saves on every change

4. **API Endpoints** (`app/routes/gmail.py`)
   - `GET /api/gmail/polling-status` - Get poller status
   - `POST /api/gmail/trigger-poll` - Manually trigger a poll
   - `POST /api/gmail/sync` - Full manual sync
   - `GET /api/gmail/test-connection` - Test Gmail connection

### Frontend Features

1. **Dashboard** (`src/app/dashboard/page.tsx`)
   - Real-time polling status (updates every 5 seconds)
   - Background polling indicator (Active/Inactive)
   - Stats: total emails processed, todos created, last poll time
   - Manual sync buttons

2. **Hooks** (`src/hooks/use-gmail-sync.ts`)
   - `useGmailPollingStatus()` - Get polling status
   - `useTriggerPoll()` - Trigger manual poll
   - `useGmailSync()` - Full manual sync

## Usage

### Automatic Polling

Once the backend is running, it will automatically:
1. Poll Gmail every 60 seconds
2. Fetch unread emails
3. Process them with AI to extract action items
4. Create todos in the database
5. Update the polling status

### Manual Sync

From the dashboard, you can:
1. **Trigger Poll Now** - Immediately poll Gmail (uses background poller)
2. **Full Manual Sync** - Complete manual sync with custom parameters

### View Todos

Navigate to the Todos page to see all created action items.

## Data Storage

Todos are stored in:
- **Location**: `data/todos.json`
- **Format**: JSON
- **Persistence**: Auto-saved on every change

## Troubleshooting

### Backend Issues

**Gmail Connection Failed**
- Verify Gmail credentials in `.env`
- Check that App Password is correct (16 characters, no spaces)
- Ensure 2FA is enabled on your Google account

**LLM API Errors**
- Verify OpenAI API key is set
- Check API key has sufficient credits
- Ensure internet connection is active

**Poller Not Running**
- Check backend logs for errors
- Visit `/api/gmail/polling-status` to see status
- Restart the backend

### Frontend Issues

**Cannot Connect to Backend**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

**Toast Notifications Not Showing**
- Ensure `Toaster` component is added to layout
- Check browser console for errors

## API Documentation

Full API documentation is available at:
http://localhost:8000/docs

## Development

### Backend Structure
```
app/
├── main.py                 # FastAPI app with background tasks
├── routes/
│   ├── gmail.py           # Gmail sync endpoints
│   └── todos.py           # Todo CRUD endpoints
├── services/
│   ├── gmail_poller.py    # Background polling service
│   └── message_processor.py # Message processing
├── models/                 # Pydantic models
└── storage/
    └── memory_store.py    # JSON storage

src/core/
├── gmail_helper.py        # Gmail IMAP client
└── email_processor.py     # LLM-based email processing

data/
└── todos.json             # Persisted todos
```

### Frontend Structure
```
src/
├── app/dashboard/
│   ├── page.tsx           # Dashboard with sync controls
│   └── todos/page.tsx     # Todos page
├── hooks/
│   ├── use-gmail-sync.ts  # Gmail sync hooks
│   └── use-todos.ts       # Todo hooks
└── components/
    └── ui/                # Reusable UI components
```

## Configuration

### Polling Interval

To change the polling interval, modify `gmail_poller.py`:

```python
gmail_poller = GmailPoller(poll_interval_seconds=120)  # Poll every 2 minutes
```

### Email Processing

Customize the AI prompt in `email_processor.py` to adjust how action items are extracted.

## Security Notes

- Never commit `.env` files to version control
- Keep your Gmail App Password secure
- Rotate API keys regularly
- Use environment variables for all sensitive data

## Support

For issues or questions:
1. Check the API docs at `/docs`
2. Review backend logs
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

## Next Steps

- [ ] Add email filters (by sender, subject, etc.)
- [ ] Support multiple email accounts
- [ ] Add priority levels for todos
- [ ] Implement email categorization
- [ ] Add webhook notifications
- [ ] Database migration (PostgreSQL, MongoDB, etc.)
