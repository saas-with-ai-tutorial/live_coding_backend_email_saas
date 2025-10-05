# SaaS POC - Message Aggregator & Todo Manager

## 🎯 Project Overview

A SaaS application that integrates with multiple communication channels (Email, WhatsApp, Slack, Gmail), reads incoming messages, and automatically creates action items in a todo list.

**Status**: Proof of Concept (POC)
- ✅ No authentication required
- ✅ No database integration (in-memory storage)
- ✅ Focus on core functionality

---

## 📁 Repository Structure

```
/Users/rakeshbhugra/code/instructor_notes/live_coding_saas/
├── live_coding_frontend_email_saas/     # Next.js Frontend
└── live_coding_backend_email_saas/      # FastAPI Backend
```

---

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Client State Management**: Zustand
- **Server State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios (with TanStack Query)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Server**: Uvicorn
- **CORS**: FastAPI CORS middleware
- **Data Storage**: In-memory (POC)

---

## 🎨 Design References

1. **Landing Page**: `landing_website_home_page.png`
   - Hero section with call-to-action
   - "Get Started" button (top right)
   - Features showcase
   - Integration logos (Gmail, Slack, WhatsApp, etc.)

2. **Dashboard**: `app_screenshot.png`
   - Sidebar navigation
   - Main content area with todo list
   - Integration management section

---

## 📋 Phase 1: Frontend Setup

### 1.1 Initialize Next.js Project

```bash
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_frontend_email_saas

# Create Next.js app with latest version (15.x)
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

**Configuration Options**:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router
- ✅ src/ directory
- ✅ Import alias (@/*)

### 1.2 Install shadcn/ui

```bash
npx shadcn@latest init
```

**Configuration**:
- Style: Default
- Base color: Slate
- CSS variables: Yes
- Global CSS: `src/app/globals.css`
- Tailwind config: `tailwind.config.ts`
- Components: `@/components`
- Utils: `@/lib/utils`
- React Server Components: Yes

### 1.3 Install Required shadcn Components

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add checkbox
npx shadcn@latest add sidebar
npx shadcn@latest add dialog
npx shadcn@latest add badge
npx shadcn@latest add avatar
npx shadcn@latest add dropdown-menu
npx shadcn@latest add sheet
npx shadcn@latest add separator
npx shadcn@latest add switch
```

### 1.4 Additional Dependencies

```bash
npm install axios
npm install @tanstack/react-query              # Server state management
npm install @tanstack/react-query-devtools     # TanStack Query devtools (optional)
npm install zustand                            # Client state management
npm install lucide-react                       # Icons
npm install date-fns                           # Date utilities
npm install next-themes                        # Theme management
```

### 1.5 Folder Structure

```
src/
├── app/
│   ├── page.tsx              # Landing page
│   ├── dashboard/
│   │   ├── page.tsx          # Dashboard home
│   │   ├── todos/
│   │   │   └── page.tsx      # Todo list
│   │   └── integrations/
│   │       └── page.tsx      # Integrations management
│   ├── layout.tsx
│   ├── providers.tsx         # TanStack Query Provider
│   └── globals.css
├── components/
│   ├── ui/                   # shadcn components
│   ├── landing/
│   │   ├── hero.tsx
│   │   ├── features.tsx
│   │   ├── integrations.tsx
│   │   ├── navbar.tsx
│   │   └── footer.tsx
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── todo-list.tsx
│   │   ├── todo-item.tsx
│   │   └── integration-card.tsx
│   └── theme-provider.tsx
├── lib/
│   ├── utils.ts
│   ├── api.ts                # Axios API client
│   └── query-client.ts       # TanStack Query configuration
├── store/
│   ├── use-ui-store.ts       # UI state (sidebar, modals, etc.)
│   ├── use-filter-store.ts   # Filter/search state
│   └── index.ts              # Export all stores
├── hooks/
│   ├── use-todos.ts          # TanStack Query hooks for todos
│   ├── use-integrations.ts  # TanStack Query hooks for integrations
│   └── use-messages.ts       # TanStack Query hooks for messages
├── types/
│   ├── todo.ts
│   └── integration.ts
└── public/
    ├── logos/
    │   ├── gmail.svg
    │   ├── slack.svg
    │   ├── whatsapp.svg
    │   ├── outlook.svg
    │   └── telegram.svg
    └── images/
```

---

## 📋 Phase 2: Backend Setup

### 2.1 Initialize FastAPI Project

```bash
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_backend_email_saas

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2.2 Install Dependencies

```bash
# Core dependencies
pip install fastapi
pip install "uvicorn[standard]"
pip install pydantic
pip install python-dotenv

# Optional but recommended
pip install python-multipart  # For file uploads
pip install email-validator   # For email validation
```

### 2.3 Create requirements.txt

```bash
pip freeze > requirements.txt
```

### 2.4 Folder Structure

```
live_coding_backend_email_saas/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── todo.py           # Todo Pydantic models
│   │   └── message.py        # Message Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── todos.py          # Todo endpoints
│   │   ├── messages.py       # Message processing endpoints
│   │   └── integrations.py  # Integration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── todo_service.py
│   │   └── message_processor.py
│   └── storage/
│       ├── __init__.py
│       └── memory_store.py   # In-memory data storage
├── venv/
├── requirements.txt
└── .env
```

---

## 📋 Phase 3: State Management Setup

### 3.1 TanStack Query Configuration

**lib/query-client.ts**
```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

**app/providers.tsx**
```typescript
'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/lib/query-client';
import { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Update app/layout.tsx**
```typescript
import { Providers } from './providers';
import { ThemeProvider } from '@/components/theme-provider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            {children}
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  );
}
```

### 3.2 TanStack Query Hooks for Todos

**hooks/use-todos.ts**
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Todo, CreateTodoRequest } from '@/types/todo';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Fetch all todos
export function useTodos() {
  return useQuery({
    queryKey: ['todos'],
    queryFn: async () => {
      const { data } = await axios.get<Todo[]>(`${API_URL}/api/todos`);
      return data;
    },
  });
}

// Create todo
export function useCreateTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (todo: CreateTodoRequest) => {
      const { data } = await axios.post<Todo>(`${API_URL}/api/todos`, todo);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Update todo
export function useUpdateTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...todo }: Partial<Todo> & { id: string }) => {
      const { data } = await axios.put<Todo>(`${API_URL}/api/todos/${id}`, todo);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Toggle todo completion
export function useToggleTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await axios.patch<Todo>(`${API_URL}/api/todos/${id}/toggle`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Delete todo
export function useDeleteTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await axios.delete(`${API_URL}/api/todos/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}
```

### 3.3 Zustand Store for UI State

**store/use-ui-store.ts**
```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  
  createTodoDialogOpen: boolean;
  toggleCreateTodoDialog: () => void;
  setCreateTodoDialogOpen: (open: boolean) => void;
  
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        sidebarOpen: true,
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        
        createTodoDialogOpen: false,
        toggleCreateTodoDialog: () => 
          set((state) => ({ createTodoDialogOpen: !state.createTodoDialogOpen })),
        setCreateTodoDialogOpen: (open) => set({ createTodoDialogOpen: open }),
        
        theme: 'system',
        setTheme: (theme) => set({ theme }),
      }),
      {
        name: 'ui-storage',
      }
    )
  )
);
```

**store/use-filter-store.ts**
```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface FilterState {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  
  filterStatus: 'all' | 'active' | 'completed';
  setFilterStatus: (status: 'all' | 'active' | 'completed') => void;
  
  filterPriority: 'all' | 'low' | 'medium' | 'high';
  setFilterPriority: (priority: 'all' | 'low' | 'medium' | 'high') => void;
  
  filterSource: 'all' | 'gmail' | 'slack' | 'whatsapp' | 'outlook' | 'telegram' | 'manual';
  setFilterSource: (source: 'all' | 'gmail' | 'slack' | 'whatsapp' | 'outlook' | 'telegram' | 'manual') => void;
  
  sortBy: 'createdAt' | 'priority' | 'dueDate';
  setSortBy: (sortBy: 'createdAt' | 'priority' | 'dueDate') => void;
  
  sortOrder: 'asc' | 'desc';
  setSortOrder: (sortOrder: 'asc' | 'desc') => void;
  
  resetFilters: () => void;
}

export const useFilterStore = create<FilterState>()(
  devtools((set) => ({
    searchQuery: '',
    setSearchQuery: (query) => set({ searchQuery: query }),
    
    filterStatus: 'all',
    setFilterStatus: (status) => set({ filterStatus: status }),
    
    filterPriority: 'all',
    setFilterPriority: (priority) => set({ filterPriority: priority }),
    
    filterSource: 'all',
    setFilterSource: (source) => set({ filterSource: source }),
    
    sortBy: 'createdAt',
    setSortBy: (sortBy) => set({ sortBy }),
    
    sortOrder: 'desc',
    setSortOrder: (sortOrder) => set({ sortOrder }),
    
    resetFilters: () => set({
      searchQuery: '',
      filterStatus: 'all',
      filterPriority: 'all',
      filterSource: 'all',
      sortBy: 'createdAt',
      sortOrder: 'desc',
    }),
  }))
);
```

**store/index.ts**
```typescript
export { useUIStore } from './use-ui-store';
export { useFilterStore } from './use-filter-store';
```

### 3.4 Usage Example in Component

**components/dashboard/todo-list.tsx**
```typescript
'use client';

import { useTodos, useToggleTodo, useDeleteTodo } from '@/hooks/use-todos';
import { useFilterStore } from '@/store';
import { TodoItem } from './todo-item';
import { Loader2 } from 'lucide-react';

export function TodoList() {
  const { data: todos, isLoading, error } = useTodos();
  const toggleTodo = useToggleTodo();
  const deleteTodo = useDeleteTodo();
  
  const { searchQuery, filterStatus, filterPriority } = useFilterStore();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }
  
  if (error) {
    return <div className="text-red-500">Error loading todos</div>;
  }
  
  // Filter todos based on store state
  const filteredTodos = todos?.filter((todo) => {
    if (searchQuery && !todo.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (filterStatus !== 'all') {
      if (filterStatus === 'completed' && !todo.completed) return false;
      if (filterStatus === 'active' && todo.completed) return false;
    }
    if (filterPriority !== 'all' && todo.priority !== filterPriority) {
      return false;
    }
    return true;
  });
  
  return (
    <div className="space-y-2">
      {filteredTodos?.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={() => toggleTodo.mutate(todo.id)}
          onDelete={() => deleteTodo.mutate(todo.id)}
        />
      ))}
    </div>
  );
}
```

---

## 📋 Phase 4: Core Features Implementation

### 4.1 Landing Page Components

#### Features:
- **Hero Section**
  - Compelling headline
  - Subheadline explaining the value proposition
  - "Get Started" CTA button (top right navbar)
  - Hero image from Unsplash

- **Features Section**
  - Multi-channel integration
  - Automatic action item creation
  - Centralized todo management
  - Real-time updates

- **Integrations Showcase**
  - Grid of supported platforms with logos
  - Gmail, Slack, WhatsApp, Outlook, Telegram

- **Footer**
  - Company/app information
  - Navigation links (About, Features, Integrations, Contact)
  - Social media links (optional)
  - Copyright notice
  - Privacy & Terms links (optional for POC)

### 4.2 Dashboard Components

#### Sidebar Menu Items:
1. **Dashboard** (Home)
2. **Todos** - Main todo list view
3. **Integrations** - Manage channel connections
4. **Settings** (optional)
5. **Help** (optional)

#### Todo List Features:
- Add new todo
- Mark as complete/incomplete
- Delete todo
- View source (which channel it came from)
- Priority levels
- Due dates

#### Integrations Page Features:
- List of available integrations
- Enable/disable integrations (mock for POC)
- Status indicators (connected/disconnected)
- Integration cards with logos

### 4.3 Backend API Endpoints

#### Todo Endpoints
```
GET    /api/todos              # Get all todos
POST   /api/todos              # Create new todo
GET    /api/todos/{id}         # Get specific todo
PUT    /api/todos/{id}         # Update todo
DELETE /api/todos/{id}         # Delete todo
PATCH  /api/todos/{id}/toggle  # Toggle completion status
```

#### Message Processing Endpoints
```
POST   /api/messages/process   # Process incoming message
POST   /api/messages/gmail     # Receive Gmail messages
POST   /api/messages/slack     # Receive Slack messages
POST   /api/messages/whatsapp  # Receive WhatsApp messages
POST   /api/messages/outlook   # Receive Outlook messages
POST   /api/messages/telegram  # Receive Telegram messages
```

#### Integration Endpoints
```
GET    /api/integrations              # Get all integrations
GET    /api/integrations/{name}       # Get specific integration
POST   /api/integrations/{name}/toggle # Enable/disable integration
```

---

## 📋 Phase 4: Data Models

### Frontend TypeScript Types

**types/todo.ts**
```typescript
export interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  source: string;  // 'gmail', 'slack', 'whatsapp', 'outlook', 'telegram', 'manual'
  createdAt: string;
  dueDate?: string;
}

export interface CreateTodoRequest {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}
```

**types/integration.ts**
```typescript
export interface Integration {
  id: string;
  name: string;
  displayName: string;
  description: string;
  logo: string;
  enabled: boolean;
  status: 'connected' | 'disconnected' | 'error';
}
```

### Backend Pydantic Models

**models/todo.py**
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    due_date: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: str
    completed: bool = False
    source: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**models/message.py**
```python
from pydantic import BaseModel
from typing import Optional

class MessageBase(BaseModel):
    content: str
    sender: str
    source: str  # 'gmail', 'slack', 'whatsapp', 'outlook', 'telegram'

class MessageCreate(MessageBase):
    pass

class ProcessedMessage(BaseModel):
    message: MessageBase
    todos_created: list[str]  # List of todo IDs created
```

---

## 📋 Phase 5: Implementation Steps

### Step 1: Frontend Landing Page
1. Create landing page layout
2. Implement hero section with Unsplash images
3. Add features section
4. Create integration showcase with downloaded logos
5. Add navigation with "Get Started" button
6. Link "Get Started" to dashboard/todos

### Step 2: Frontend Dashboard
1. Create dashboard layout with sidebar
2. Implement sidebar navigation
3. Build todo list component
4. Create todo item component with actions
5. Add form for creating new todos
6. Implement integrations page with cards

### Step 3: Backend Core
1. Set up FastAPI application with CORS
2. Create in-memory storage class
3. Implement todo CRUD operations
4. Add todo service layer
5. Create todo API routes

### Step 4: Message Processing
1. Create message processor service
2. Implement logic to extract action items from messages
3. Add message API routes for different sources
4. Mock integration with different channels

### Step 5: Integration
1. Create API client in frontend
2. Connect todo list to backend API
3. Implement real-time updates
4. Add error handling
5. Test end-to-end flow

### Step 6: Polish
1. Add loading states
2. Implement error boundaries
3. Add toast notifications
4. Improve responsive design
5. Add animations/transitions

---

## 📋 Phase 6: Assets & Resources

### Images to Download

#### Logos (SVG format preferred)
Download from official brand resources or icon libraries:

1. **Gmail** - https://fonts.google.com/icons or official brand
2. **Slack** - https://slack.com/media-kit
3. **WhatsApp** - https://www.whatsapp.com/brand
4. **Microsoft Outlook** - https://www.microsoft.com/en-us/microsoft-365/blog/brand-central/
5. **Telegram** - https://telegram.org/img/ or icon libraries

Save to: `frontend/public/logos/`

**Note**: You can also use icon libraries like:
- [Simple Icons](https://simpleicons.org/) - Has all major brand icons in SVG
- [Lucide React](https://lucide.dev/) - For generic icons
- Download brand assets directly from official brand pages

#### Hero/Feature Images
Use Unsplash API or direct downloads:
- Productivity themes
- Team collaboration
- Communication tools
- Modern workspace

URLs:
- https://unsplash.com/s/photos/productivity
- https://unsplash.com/s/photos/team-collaboration
- https://unsplash.com/s/photos/workspace

Save to: `frontend/public/images/`

---

## 📋 Phase 7: Running the Application

### Frontend Development Server

```bash
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_frontend_email_saas
npm run dev
```

Access at: http://localhost:3000

### Backend Development Server

```bash
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_backend_email_saas
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Access at: http://localhost:8000
API Docs: http://localhost:8000/docs

---

## 📋 Phase 8: Testing Strategy

### Manual Testing Checklist

#### Landing Page
- [ ] Hero section loads correctly
- [ ] Integration logos display properly
- [ ] "Get Started" button navigates to dashboard
- [ ] Responsive on mobile/tablet/desktop

#### Dashboard
- [ ] Sidebar navigation works
- [ ] Todo list displays correctly
- [ ] Can create new todo
- [ ] Can mark todo as complete
- [ ] Can delete todo
- [ ] Integrations page loads

#### API
- [ ] GET /api/todos returns todos
- [ ] POST /api/todos creates todo
- [ ] DELETE /api/todos/{id} deletes todo
- [ ] POST /api/messages/process creates todos from messages

---

## 📋 Phase 9: Future Enhancements (Post-POC)

### Authentication
- User registration/login
- JWT tokens
- Protected routes

### Database
- PostgreSQL or MongoDB
- Data persistence
- User data isolation

### Real Integrations
- Gmail API integration
- Slack App/Bot
- WhatsApp Business API
- Microsoft Graph API (Outlook)

### Advanced Features
- AI-powered action item extraction (GPT-4)
- Smart categorization
- Priority detection
- Due date suggestion
- Recurring tasks
- Collaboration features
- Mobile app

---

## 📋 Phase 10: Deployment (Future)

### Frontend
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify

### Backend
- Railway
- Render
- Heroku
- AWS EC2/Lambda
- Google Cloud Run

---

## 🎯 Success Criteria

### MVP Features Completed
- ✅ Landing page with design matching reference
- ✅ Dashboard with sidebar navigation
- ✅ Todo list CRUD operations
- ✅ Integrations page (UI only for POC)
- ✅ Message processing endpoint (mock)
- ✅ Frontend-backend integration
- ✅ Responsive design

---

## 📝 Notes

### POC Limitations
- No real authentication (anyone can access)
- In-memory storage (data lost on restart)
- Mock integrations (no real API connections)
- No data validation/sanitization
- No proper error handling
- No logging/monitoring

### Development Tips
- Use TypeScript strict mode
- Follow ESLint rules
- Use proper component structure
- Keep components small and focused
- Use custom hooks for logic reuse
- Add proper TypeScript types
- Document complex logic

---

## 🚀 Getting Started Command Summary

### Initial Setup
```bash
# Frontend
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_frontend_email_saas
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npx shadcn@latest init
npm install axios @tanstack/react-query @tanstack/react-query-devtools zustand lucide-react date-fns next-themes

# Backend
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_backend_email_saas
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic python-dotenv
pip freeze > requirements.txt
```

### Running Both Servers
```bash
# Terminal 1 - Backend
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_backend_email_saas
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_frontend_email_saas
npm run dev
```

---

## 📞 Integration Mock Examples

### Gmail Message Example
```json
{
  "content": "Need to review the Q4 budget report by Friday",
  "sender": "boss@company.com",
  "source": "gmail",
  "subject": "Q4 Budget Review"
}
```

### Slack Message Example
```json
{
  "content": "Can someone deploy the new feature to staging?",
  "sender": "@john_doe",
  "source": "slack",
  "channel": "#engineering"
}
```

### WhatsApp Message Example
```json
{
  "content": "Don't forget to pickup groceries on the way home",
  "sender": "+1234567890",
  "source": "whatsapp"
}
```

### Outlook Message Example
```json
{
  "content": "Please schedule a meeting with the marketing team for next week",
  "sender": "manager@company.com",
  "source": "outlook",
  "subject": "Marketing Meeting Request"
}
```

### Telegram Message Example
```json
{
  "content": "Update the documentation for the new API endpoints",
  "sender": "@dev_team_bot",
  "source": "telegram",
  "chat": "Development Team"
}
```

---

## 🎨 Color Scheme Suggestions

Based on shadcn/ui with Slate base:

```css
Primary: #0f172a (Slate 900)
Secondary: #64748b (Slate 500)
Accent: #3b82f6 (Blue 500)
Success: #10b981 (Green 500)
Warning: #f59e0b (Amber 500)
Error: #ef4444 (Red 500)
Background: #ffffff / #0f172a (Light/Dark)
```

---

## 📚 State Management Architecture

### When to Use What

#### Use Zustand for:
- **UI State**: Sidebar open/closed, modal states, drawer states
- **User Preferences**: Theme, language, layout preferences
- **Filters & Search**: Client-side filtering, sorting, search queries
- **Form State**: Multi-step forms, temporary form data
- **Local App State**: Navigation state, active tabs, selected items

#### Use TanStack Query for:
- **Server Data**: Fetching todos, integrations, messages
- **Mutations**: Creating, updating, deleting todos
- **Caching**: Automatic caching and revalidation
- **Background Refetching**: Keeping data fresh
- **Optimistic Updates**: Immediate UI updates before server confirmation

### Benefits of This Approach

**Zustand**:
- ✅ Simple API, minimal boilerplate
- ✅ No providers needed (except for persisted state)
- ✅ Great TypeScript support
- ✅ DevTools for debugging
- ✅ Middleware for persistence and logging

**TanStack Query**:
- ✅ Automatic caching and deduplication
- ✅ Background refetching
- ✅ Loading and error states built-in
- ✅ Optimistic updates
- ✅ Query invalidation and refetching
- ✅ DevTools for inspecting queries

### State Flow Example

```
User clicks "Mark as Complete"
       ↓
useToggleTodo mutation (TanStack Query)
       ↓
Optimistic UI update
       ↓
API call to backend
       ↓
On success: invalidate todos query
       ↓
TanStack Query refetches todos
       ↓
UI updates with latest data

Meanwhile, if filter changes:
       ↓
useFilterStore.setFilterStatus() (Zustand)
       ↓
Component re-renders with new filter
       ↓
Filtered todos displayed (client-side)
```

---

## 📚 Resources & Documentation

- Next.js 15: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- shadcn/ui: https://ui.shadcn.com
- FastAPI: https://fastapi.tiangolo.com
- Pydantic: https://docs.pydantic.dev
- TanStack Query: https://tanstack.com/query/latest
- Zustand: https://zustand-demo.pmnd.rs
- Lucide Icons: https://lucide.dev
- Unsplash: https://unsplash.com

---

**Last Updated**: October 5, 2025
**Status**: Ready for Implementation
**Estimated Timeline**: 2-3 days for MVP POC
