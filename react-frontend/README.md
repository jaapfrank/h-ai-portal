# Hoeflon Ridder ERP AI Chatbot - React Frontend

Een moderne React-gebaseerde frontend voor de Ridder ERP AI Chatbot.

## Features

- 🎨 Moderne UI met Tailwind CSS
- 💬 Real-time chat interface
- 📊 SQL query viewer
- 📈 System status monitoring
- 📱 Responsive design
- 🔒 Geïntegreerde authenticatie

## Installation

### Vereisten
- Node.js 16+ 
- npm 7+
- Draaiende FastAPI backend op poort 8501

### Setup

```bash
# Installeer dependencies
npm install

# Start development server
npm start
```

De app draait op http://localhost:3000

## Scripts

- `npm start` - Start development server
- `npm build` - Build voor productie
- `npm test` - Run tests
- `npm eject` - Eject uit Create React App

## Project Structuur

```
src/
├── components/
│   ├── ChatInterface.js    # Hoofdchat component
│   ├── StatusPanel.js      # Status monitoring
│   └── Header.js          # App header
├── services/
│   └── api.js             # API calls naar backend
├── App.js                 # Hoofdapp component
└── index.js              # Entry point
```

## Configuration

Configuratie via `.env` bestand:

```
REACT_APP_API_URL=http://localhost:8501
PORT=3000
```

## API Integration

De app communiceert met de FastAPI backend via:
- `POST /chat` - Chat berichten
- `GET /status` - System status
- `GET /test_sql` - Database test
- `GET /test_ad` - AD test  
- `GET /test_claude` - Claude AI test

## Styling

- **Tailwind CSS** voor styling
- **Lucide React** voor iconen
- **React Markdown** voor chat rendering
- Custom animations en transitions

## Deployment

Voor productie deployment:

```bash
npm run build
```

Served de `build/` folder via een webserver.

## Troubleshooting

### CORS Errors
Zorg dat de FastAPI backend CORS middleware heeft geconfigureerd voor `http://localhost:3000`

### API Connection
Controleer dat:
- Backend draait op poort 8501
- Netwerk connectiviteit
- REACT_APP_API_URL correct is ingesteld