# Hoeflon AI Portal Project

## 👥 **DEVELOPMENT TEAM STRUCTURE**

- **🎯 PROJECT MANAGER: Claude** - Overall coordination, planning, status tracking
- **🔧 PROGRAMMER: Broer** - Backend development, API implementation, database integration  
- **🧪 TESTER: Oom** - Quality assurance, systematic testing, bug detection
- **👩‍💼 USER: Lola** - User experience feedback, requirements validation, acceptance testing
- **📋 DOCUMENTATION: Diederick** - Technical documentation, system specifications, knowledge management
- **🚀 VISIONARY: Erik** - Strategic direction, feature prioritization, business alignment

## 🎯 PROJECT OVERVIEW

Hoeflon AI Portal is an intelligent chatbot system that answers business questions about the Hoeflon ERP system by generating and executing SQL queries against multiple databases, with AI-powered routing, cross-database transaction linking, and AutoGen agent orchestration capabilities.

## 📊 CURRENT STATUS (2025-07-02) - PRODUCTION READY ✅

### ✅ **PRODUCTION READY FEATURES:**
- **🏗️ MODULAR ARCHITECTURE** - Clean separation with FastAPI backend, React frontend, AutoGen agents
- **🧠 INTELLIGENT ROUTING** - AI-powered query routing to appropriate databases
- **🤖 AGENT ORCHESTRATION** - AutoGen framework with specialized AI agents
- **📊 REAL-TIME MONITORING** - System health dashboards and ML analytics
- **🔒 ENTERPRISE SECURITY** - SQL injection prevention, query validation, audit logging
- **🌐 MULTI-DATABASE** - Ridder ERP, AccountView, Company knowledge integration

### 🎯 **SYSTEM CAPABILITIES:**
- Natural language processing for Dutch business questions
- Cross-database transaction linking and analysis
- Interactive dashboards with data visualization
- Real-time confidence scoring and result validation
- Multi-agent collaboration for complex workflows

## 🏗️ MODULAR PROJECT STRUCTURE

### **Root Directory:**
```
/home/jfrank/projecten/hoeflon/hoeflon ai/hoeflon-ai-portaal/
├── 📋 README.md                   # Project overview and setup
├──    CLAUDE.md                 # This project documentation
├── 📁 docs/                      # Complete documentation
│   ├── PROJECT_MAP.md            # Detailed navigation guide
│   └── *.md                      # Additional documentation
├── 🐍 backend/                   # FastAPI Python backend
├── ⚛️ react-frontend/            # React application
├── 🤖 agents/                    # AutoGen agent system
├── 🧪 tests/                     # Test suite
├── 📜 scripts/                   # Setup and utility scripts
└── 📋 requirements.txt           # Python dependencies
```

### **Backend Modular Structure:**
```
backend/
├── 🚀 main.py                    # FastAPI entry point
├── 🎯 core/                      # Core system (config, exceptions)
├── 🗄️ database/                  # Database layer & knowledge stores
├── 🧭 routing/                   # Intelligent query routing
├── ⚙️ engines/                   # Processing engines (query, analysis, AI)
├── 🏢 services/                  # Business logic services
└── 🌐 api/                       # FastAPI endpoints
```

**📖 SEE PROJECT_MAP.md FOR DETAILED NAVIGATION GUIDE**

## 🚀 SYSTEM STARTUP COMMANDS

### **Backend (Port 8504):**
```bash
cd "/home/jfrank/projecten/hoeflon/hoeflon ai/hoeflon-ai-portaal"
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8504 --reload
```

### **Frontend (Port 3000):**
```bash
cd "/home/jfrank/projecten/hoeflon/hoeflon ai/hoeflon-ai-portaal/react-frontend"
npm install
npm start
```

### **Agent System:**
```bash
cd "/home/jfrank/projecten/hoeflon/hoeflon ai/hoeflon-ai-portaal"
python bootstrap_agents.py
python main_agents.py
```

### **Verify System Status:**
```bash
curl http://localhost:8504/status
curl http://localhost:3000
```

## 🧪 TEST INTELLIGENT ROUTING

```bash
# Test intelligent routing with business questions
curl -X POST http://localhost:8504/chat -H "Content-Type: application/json" -d '{"message": "Hoeveel machines hebben we dit jaar geproduceerd?", "session_id": "test_intelligent"}'

# Test company knowledge routing  
curl -X POST http://localhost:8504/chat -H "Content-Type: application/json" -d '{"message": "wat is het telefoonnummer van jaap frank?", "session_id": "test_intelligent"}'

# Test financial routing
curl -X POST http://localhost:8504/chat -H "Content-Type: application/json" -d '{"message": "Wat is onze omzet dit jaar?", "session_id": "test_intelligent"}'
```

## 💼 SYSTEM CAPABILITIES

### **Database Integration:**
- **ERP Database**: Ridder ERP on SQL Server (966 tables)
- **AccountView Databases**: Financial data across multiple companies
- **Company Database**: Employee directory, HR policies, organizational structure

### **AI & Technology Stack:**
- **Backend**: Python, FastAPI, SQLAlchemy, AutoGen, Anthropic Claude
- **Frontend**: React 18, Tailwind CSS, Chart.js, React Router
- **Database**: SQL Server, SQLite, ODBC connectivity
- **AI/ML**: OpenAI GPT, Natural Language Processing
- **Testing**: Pytest with async support, coverage, parallel execution

### **Intelligent Features:**
- **Multi-Agent System**: Specialized agents (SQL Guru, Viz Master, Test Ninja, etc.)
- **AI-Powered Routing**: Questions automatically routed to correct database/system
- **Company Knowledge**: Instant lookup of contacts, policies, procedures
- **Cross-Database Intelligence**: Links operational and financial data
- **Natural Language Processing**: Dutch business questions to SQL queries
- **Confidence Scoring**: Query result validation and accuracy assessment

### **Core API Endpoints:**
- `/chat` - Main intelligent chat endpoint
- `/status` - System health monitoring
- `/company_chat` - Direct company database queries

## 🛡️ SECURITY MEASURES

- SQL injection prevention (only SELECT queries allowed)
- Forbidden SQL operations (DROP, DELETE, INSERT, etc.)
- Safe query execution with timeouts
- Audit logging of all interactions

## 🎯 PRODUCTION FEATURES

✅ **Complete Backend** - FastAPI with modular architecture on port 8504  
✅ **Multi-Database Integration** - Ridder ERP, AccountView, Company databases  
✅ **AutoGen Agent System** - Specialized AI agents with orchestration  
✅ **React Frontend** - Modern interface with dashboards on port 3000  
✅ **Intelligent Routing** - AI-powered query routing system  
✅ **Real-time Monitoring** - System health and ML analytics panels  
✅ **Security Implementation** - SQL injection prevention, query validation  
✅ **Cross-Database Linking** - Transaction analysis across systems  

## 🧪 TESTING & DEVELOPMENT

```bash
# Run backend tests
pytest tests/

# Test chat endpoint
curl -X POST http://localhost:8504/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hoeveel machines hebben we dit jaar geproduceerd?", "session_id": "test"}'

# Check system health
curl http://localhost:8504/health
```

## 🔧 CONFIGURATION

- **Database Config**: `backend/core/config.py`
- **API Settings**: Port 8504, CORS enabled for React frontend
- **Security**: Forbidden SQL operations, 30-second query timeout
- **Session Management**: 60-minute timeout, max 1000 sessions

---

**Last Updated**: 2025-07-02  
**Project Status**: Production Ready  
**Architecture**: Clean, modular, and fully documented