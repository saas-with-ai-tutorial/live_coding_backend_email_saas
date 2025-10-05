# Email SaaS - Backend API

FastAPI backend for the Email SaaS application that processes messages and creates action items.

## Features

- ✅ Todo CRUD operations
- ✅ Gmail integration with IMAP
- ✅ AI-powered action item extraction
- ✅ Message processing from multiple sources
- ✅ Integration management
- ✅ In-memory storage (POC)

## Tech Stack

- **FastAPI** - Modern web framework
- **Python 3.11+** - Programming language
- **LiteLLM** - LLM integration (OpenAI GPT-4o-mini)
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example env file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=openai/gpt-4o-mini
```

#### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password at: https://myaccount.google.com/apppasswords
3. Use the generated password in `GMAIL_APP_PASSWORD`

#### OpenAI Setup

1. Get your API key from: https://platform.openai.com/api-keys
2. Add it to `OPENAI_API_KEY`

### 4. Run the Server

```bash
# Make sure you're in the backend directory and virtual environment is activated
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Todos

- `GET /api/todos` - Get all todos
- `POST /api/todos` - Create a new todo
- `GET /api/todos/{id}` - Get a specific todo
- `PUT /api/todos/{id}` - Update a todo
- `DELETE /api/todos/{id}` - Delete a todo
- `PATCH /api/todos/{id}/toggle` - Toggle todo completion

### Messages

- `POST /api/messages/process` - Process a message and create action items
- `POST /api/messages/gmail` - Process a Gmail message
- `POST /api/messages/slack` - Process a Slack message
- `POST /api/messages/whatsapp` - Process a WhatsApp message
- `POST /api/messages/outlook` - Process an Outlook message
- `POST /api/messages/telegram` - Process a Telegram message

### Gmail

- `POST /api/gmail/sync` - Sync emails from Gmail
- `GET /api/gmail/test-connection` - Test Gmail connection

### Integrations

- `GET /api/integrations` - Get all integrations
- `GET /api/integrations/{name}` - Get a specific integration
- `POST /api/integrations/{name}/toggle` - Toggle integration enabled status

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── models/                 # Pydantic models
│   ├── todo.py
│   └── message.py
├── routes/                 # API endpoints
│   ├── todos.py
│   ├── messages.py
│   ├── integrations.py
│   └── gmail.py
├── services/               # Business logic
│   ├── todo_service.py
│   └── message_processor.py
└── storage/                # Data storage
    └── memory_store.py

src/
└── core/                   # Core utilities
    ├── gmail_helper.py
    └── email_processor.py
```

## Testing

You can test the API using the interactive docs at http://localhost:8000/docs or with curl:

```bash
# Create a todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test todo", "priority": "high"}'

# Get all todos
curl http://localhost:8000/api/todos

# Sync Gmail
curl -X POST "http://localhost:8000/api/gmail/sync?count=5&unread_only=true"
```

## Notes

- This is a POC with in-memory storage - data will be lost on restart
- No authentication is implemented
- Gmail integration uses IMAP with App Password
- AI processing uses OpenAI GPT-4o-mini via LiteLLM