# 🤖 H AI Portal

**AI-powered ERP chatbot for business intelligence and database queries**

## 🎯 Overview

H AI Portal is an intelligent chatbot system that answers business questions about the Hoeflon ERP system by generating and executing SQL queries against multiple databases, with AI-powered routing and cross-database transaction linking capabilities.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Modular FastAPI backend** with intelligent routing
- **Multi-database integration** (SQL Server, SQLite)
- **AI-powered query generation** with natural language processing
- **Cross-database transaction linking** for comprehensive business insights
- **AutoGen agent orchestration** for complex workflows

### Frontend (React)
- **Modern React interface** with real-time monitoring
- **Interactive dashboards** for data visualization
- **AI monitoring panels** for system health
- **Responsive design** with Tailwind CSS

### Agent System
- **Multi-agent collaboration** using AutoGen framework
- **Specialized AI agents** for different business functions
- **Intelligent routing** based on query context
- **Real-time orchestration** and monitoring

## 🚀 Quick Start

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8504 --reload
```

### Frontend Setup
```bash
# Install React dependencies
cd react-frontend
npm install

# Start development server
npm start
```

### Agent System
```bash
# Bootstrap agent system
python bootstrap_agents.py

# Run agent orchestration
python main_agents.py
```

## 📊 System Capabilities

### Database Integration
- **ERP Database**: Ridder ERP on SQL Server (966 tables)
- **AccountView Databases**: Financial data across multiple companies
- **Company Database**: Employee directory, HR policies, organizational structure

### AI Features
- **Natural Language Processing**: Dutch business questions to SQL queries
- **Intelligent Routing**: Automatic query routing to appropriate databases
- **Company Knowledge**: Instant lookup of contacts, policies, procedures
- **Cross-Database Intelligence**: Links operational and financial data
- **Confidence Scoring**: Query result validation and accuracy assessment

### Security
- **SQL Injection Prevention**: Only SELECT queries allowed
- **Query Validation**: Forbidden operations (DROP, DELETE, INSERT)
- **Audit Logging**: Complete interaction tracking
- **Safe Execution**: Query timeouts and error handling

## 🗄️ Project Structure

```
├── backend/                 # FastAPI backend
│   ├── api/                # REST API endpoints
│   ├── config/             # Configuration files
│   ├── core/               # Core configuration and exceptions
│   ├── database/           # Database connections and knowledge
│   ├── engines/            # Processing engines (query, analysis, AI)
│   ├── routing/            # Intelligent query routing
│   └── services/           # Business logic services
├── agents/                 # AutoGen agent system + orchestration scripts
├── react-frontend/         # React web interface
├── scripts/                # Setup and utility scripts
├── tests/                  # Test suite
└── docs/                   # Complete project documentation
```

## 🛠️ Technologies

- **Backend**: Python, FastAPI, SQLAlchemy, AutoGen
- **Frontend**: React, Tailwind CSS, Chart.js
- **Database**: SQL Server, SQLite
- **AI/ML**: OpenAI GPT, Natural Language Processing
- **Infrastructure**: Docker, GitHub Actions

## 📋 API Endpoints

- `POST /chat` - Main intelligent chat endpoint
- `GET /status` - System health monitoring
- `POST /company_chat` - Direct company database queries
- `GET /health` - API health check

## 🧪 Testing

```bash
# Run backend tests
pytest tests/

# Test intelligent routing
curl -X POST http://localhost:8504/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hoeveel machines hebben we dit jaar geproduceerd?", "session_id": "test"}'
```

## 🔧 Configuration

1. **Database Connections**: Configure in `backend/core/config.py`
2. **AI Models**: Set API keys in environment variables
3. **Agent Settings**: Modify `agents/` configuration files

## 📝 Documentation

- [Project Instructions](CLAUDE.md) - Team structure and development guidelines
- [Architecture Guide](PROJECT_MAP.md) - Detailed navigation and module descriptions
- [MCP Servers](MCP_SERVERS_README.md) - Model Context Protocol setup
- [GitHub Setup](GITHUB_SETUP.md) - Repository configuration guide

## 👥 Development Team

- **🎯 PROJECT MANAGER**: Claude - Overall coordination and planning
- **🔧 PROGRAMMER**: Broer - Backend development and API implementation
- **🧪 TESTER**: Oom - Quality assurance and systematic testing
- **👩‍💼 USER**: Lola - User experience feedback and requirements
- **📋 DOCUMENTATION**: Diederick - Technical documentation and specifications
- **🚀 VISIONARY**: Erik - Strategic direction and business alignment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request


