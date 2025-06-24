# Hoeflon Ridder ERP AI Chatbot Project

## 👥 **DEVELOPMENT TEAM STRUCTURE**

- **🎯 PROJECT MANAGER: Claude** - Overall coordination, planning, status tracking
- **🔧 PROGRAMMEUR: Broer** - Backend development, API implementation, database integration
- **🧪 TESTER: Oom** - Quality assurance, systematic testing, bug detection
- **👩‍💼 GEBRUIKER: Lola** - User experience feedback, requirements validation, acceptance testing
- **📋 DOCUMENTATIE: Diederick** - Technical documentation, system specifications, knowledge management
- **🚀 VISIONAIR: Erik** - Strategic direction, feature prioritization, business alignment

## 🎯 PROJECT OVERVIEW

This project creates an AI-powered chatbot that answers business questions about the Hoeflon ERP system by generating and executing SQL queries against the Ridder ERP database, with intelligent cross-database transaction linking capabilities.

## 📊 CURRENT STATUS (2025-06-20) - MODULAR & INTELLIGENT ✅

### ✅ **MODULAR ARCHITECTURE IMPLEMENTED:**
- **🏗️ FULLY MODULAR STRUCTURE** - Clean separation of concerns with logical modules
- **🧠 INTELLIGENT ROUTING READY** - AI-powered routing system in place
- **📁 ORGANIZED CODEBASE** - Easy navigation with clear file locations
- **🔧 SCALABLE ARCHITECTURE** - Ready for team development and feature expansion

### 🚧 **NEXT TASKS:**
- 🧪 **TEST MODULAR SYSTEM** - Verify all imports and modules work correctly
- 🔄 **COMPLETE ROUTER INTEGRATION** - Finish intelligent routing implementation
- ✅ **VALIDATE FUNCTIONALITY** - Ensure system works after modularization

## 🏗️ MODULAR PROJECT STRUCTURE

### **Root Directory:**
```
/home/jaapfrank/Hoeflon Ridder/Ridder AI/
├── 📋 CLAUDE.md                   # This project documentation
├── 🗺️ PROJECT_MAP.md              # Detailed navigation guide
├── backend/                       # Modular Python backend
├── react-frontend/               # React application
├── venv/                         # Python virtual environment
└── requirements.txt              # Dependencies
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
cd "/home/jaapfrank/Hoeflon Ridder/Ridder AI"
source venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8504 --reload
```

### **Frontend (Port 3000):**
```bash
cd react-frontend
npm start
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
- **AccountView Databases**: Hoeflon B.V. 2025 (14 tables), Hoeflon International 2025 (307 tables)
- **Company Database**: SQLite with structured company data (159 employees, HR policies)

### **Intelligent Features:**
- **AI-Powered Routing**: Questions automatically routed to correct database/system
- **Company Knowledge**: Instant lookup of phone numbers, HR policies, organization
- **Cross-Database Intelligence**: Links financial transactions to operational machine data
- **Natural Language Processing**: Dutch business questions to SQL queries

### **Core API Endpoints:**
- `/chat` - Main intelligent chat endpoint
- `/status` - System health monitoring
- `/company_chat` - Direct company database queries

## 🛡️ SECURITY MEASURES

- SQL injection prevention (only SELECT queries allowed)
- Forbidden SQL operations (DROP, DELETE, INSERT, etc.)
- Safe query execution with timeouts
- Audit logging of all interactions

## 🎯 WHAT WORKS NOW

✅ **Backend API** - FastAPI running stable on port 8504  
✅ **Database Connections** - ERP + AccountView + Company databases connected  
✅ **Basic Chat** - Natural language to SQL query generation  
✅ **Company Knowledge** - Phone numbers, HR policies, organization lookup  
✅ **Frontend Interface** - React application on port 3000  
✅ **Session Management** - Multi-user session handling  

## 📋 WHAT NEEDS TO BE COMPLETED

🔄 **Intelligent Router Integration** - Complete chat endpoint implementation  
🧪 **Testing** - Verify intelligent routing works with real business questions  
📝 **Documentation** - Update any remaining technical documentation  

---

**Last Updated**: 2025-06-20  
**Project Status**: Clean & Ready for Intelligent Routing Testing  
**Next Session**: Complete intelligent router integration and test with real questions