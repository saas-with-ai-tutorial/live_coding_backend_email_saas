# Quick Start Guide

Get your Gmail auto-sync system running in 5 minutes!

## Step 1: Configure Gmail (2 minutes)

1. Go to https://myaccount.google.com/apppasswords
2. Create an App Password for "Mail"
3. Copy the 16-character password

## Step 2: Setup Backend (.env file)

Create `.env` in the backend root:

```bash
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=abcd-efgh-ijkl-mnop
OPENAI_API_KEY=sk-your-openai-key
```

## Step 3: Start Backend

```bash
cd live_coding_backend_email_saas
source venv/bin/activate  # Or: venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

You should see:
```
✅ Started Gmail background poller
🚀 Gmail poller started - polling every 60 seconds
```

## Step 4: Start Frontend

```bash
cd live_coding_frontend_email_saas
npm run dev
```

## Step 5: Test It!

1. Open http://localhost:3000/dashboard
2. You'll see:
   - **Background Polling Status** - Shows "Active"
   - **Total emails processed** - Updates automatically
   - **Last poll time** - Updates every 60 seconds
3. Click **"Trigger Poll Now"** to manually sync
4. Go to **Todos** page to see created action items

## How It Works

1. **Background Service** polls Gmail every 60 seconds
2. **AI (GPT-4o-mini)** analyzes emails for action items
3. **Todos** are automatically created
4. **Dashboard** shows real-time status

## Test with Sample Email

Send yourself an email with subject: "Test Task"

Body:
```
Hi,

Please review the Q4 report by Friday. This is urgent!

Thanks
```

Within 60 seconds (or click "Trigger Poll Now"), you should see a new todo:
- Title: "Review the Q4 report"
- Priority: High
- Due Date: Friday
- Source: Gmail

## Troubleshooting

**No todos appearing?**
- Check backend logs for errors
- Verify `.env` file has correct credentials
- Check http://localhost:8000/api/gmail/polling-status

**Backend not starting?**
- Run `pip install -r requirements.txt`
- Activate virtual environment

**Frontend error?**
- Run `npm install`
- Check backend is running on port 8000

## API Endpoints

- Status: http://localhost:8000/api/gmail/polling-status
- Docs: http://localhost:8000/docs
- Todos: http://localhost:8000/api/todos

## Data Storage

Todos are saved in: `data/todos.json`

## What's Next?

- View all todos in the Todos page
- Filter by priority, completion status
- Create manual todos
- Enable other integrations

Enjoy your automated email-to-todo system! 🎉
