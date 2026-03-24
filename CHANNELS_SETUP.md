# Django Channels Implementation Guide

## Overview
Your Django project now includes real-time messaging and announcements using Django Channels with persistent storage via Redis and SQLite.

## Components Implemented

### 1. **Models** (sportscio/models.py)
- **Message**: Stores all chat messages with sender, content, timestamp, and room
- **Announcement**: Stores announcements with title, content, author, and status

### 2. **WebSocket Consumers** (sportscio/consumers.py)
- **ChatConsumer**: Handles real-time messaging in chat rooms
- **AnnouncementConsumer**: Broadcasts announcements to all connected users

### 3. **URL Routing** (sportscio/routing.py)
- `/ws/chat/<room_name>/` - Chat WebSocket endpoint
- `/ws/announcements/` - Announcements WebSocket endpoint

### 4. **Views** (sportscio/views.py)
- `announcements_view()` - Display announcements page
- `create_announcement()` - API endpoint to create announcements (admin only)
- `get_announcements()` - API endpoint to fetch all active announcements
- `messages_view()` - Display messages page with chat history

### 5. **Templates**
- **announcements.html** - Announcements board with admin creation form
- **messages.html** - Real-time chat interface with message history

## Database Schema

### Message Table
```
- id (Primary Key)
- sender (Foreign Key to User)
- content (Text)
- timestamp (DateTime)
- room (String) - e.g., 'general', 'sports', etc.
```

### Announcement Table
```
- id (Primary Key)
- author (Foreign Key to User)
- title (String)
- content (Text)
- created_at (DateTime)
- updated_at (DateTime)
- is_active (Boolean)
```

## Feature Details

### Real-Time Messaging
- **Persistent**: All messages are stored in the database and can be retrieved later
- **Real-time**: Uses WebSocket for instant message delivery
- **Room-based**: Messages are organized by room (currently 'general' is the default)
- **User authentication required**: Only authenticated users can send/receive messages

### Announcements System
- **Admin-only creation**: Only superusers/admins can publish announcements
- **Real-time broadcasting**: New announcements are instantly visible to all connected clients
- **Persistent**: All announcements are stored and displayed on page load
- **Manageable**: Announcements can be deactivated via Django admin

## Setting Up for Production/Development

### Development Environment (In-Memory Redis)
For local development, you can use Redis locally:
```bash
# Install Redis (Windows: use WSL or Docker)
# Or temporarily use in-memory channel layer by updating settings.py

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

### Production Environment
Redis is configured via `CHANNEL_LAYERS` in settings.py:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Change for production
            "capacity": 1500,
            "expiry": 10,
        },
    },
}
```

## Running the Application

### Development Server
```bash
# Terminal 1: Start Daphne ASGI server
python manage.py runserver

# Terminal 2: Start Redis (if using Redis)
redis-server
```

### With Gunicorn (Production-like)
```bash
gunicorn -k uvicorn.workers.UvicornWorker mysite.asgi:application
```

## URL Endpoints

### Admin Panel
- `/admin/` - Django admin interface
- Messages and Announcements can be managed here

### User Pages
- `/messages/` - Chat interface
- `/announcements/` - Announcements board

### API Endpoints
- `POST /api/announcements/create/` - Create announcement (admin only)
- `GET /api/announcements/` - Get all active announcements

## Security Considerations

1. **Admin-only announcements**: Only superusers can create announcements
2. **Authenticated messaging**: Only logged-in users can send messages
3. **CSRF Protection**: Include CSRF token when making POST requests
4. **WebSocket Auth**: Channels uses Django's session authentication

## Troubleshooting

### WebSocket Connection Issues
1. Check browser console for connection errors
2. Verify Redis is running: `redis-cli ping`
3. Check ALLOWED_HOSTS in settings.py
4. Ensure ASGI application is properly configured

### Messages Not Persisting
1. Run migrations: `python manage.py migrate`
2. Check database file exists: `db.sqlite3`
3. Verify Message model is registered in admin

### Announcements Not Broadcasting
1. Check Redis connection
2. Verify CHANNEL_LAYERS configuration
3. Ensure user is superuser for creating announcements
4. Check browser console for WebSocket errors

## Customization

### Adding New Chat Rooms
Update `messages.html` to allow room selection, then modify the WebSocket URL in JavaScript:
```javascript
const roomName = 'your-room-name';
const chatSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${roomName}/`);
```

### Storing Additional Message Metadata
Extend the Message model in `models.py`:
```python
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=100)
    # Add custom fields here
```

Then run `makemigrations` and `migrate`.

## Dependencies
- `channels==4.0.0` - WebSocket support
- `channels-redis==4.1.0` - Redis backend for Channels
- `redis==5.0.0` - Redis Python client
- `daphne` - ASGI server (already in your project)

## Next Steps
1. Install and run Redis locally
2. Test messaging on `/messages/`
3. Test announcements on `/announcements/`
4. Create test announcements via admin panel
5. Deploy to production with Redis support
