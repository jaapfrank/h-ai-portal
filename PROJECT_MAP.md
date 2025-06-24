# 🗺️ PROJECT NAVIGATION MAP
*Hoeflon Ridder ERP AI Chatbot - Modular Architecture Guide*

## 📁 PROJECT STRUCTURE

```
/home/jaapfrank/Hoeflon Ridder/Ridder AI/
├── 📋 CLAUDE.md                   # Project instructions & team structure
├── 🗺️ PROJECT_MAP.md              # This navigation guide
├── 📦 requirements.txt             # Python dependencies
│
├── 🔧 backend/                     # Python FastAPI Backend (MODULAR)
│   ├── 📄 __init__.py             # Package initialization
│   ├── 🚀 main.py                 # FastAPI app entry point
│   ├── 📄 main_old.py             # Backup of old monolithic main.py
│   │
│   ├── 🎯 core/                   # Core system components
│   │   ├── 📄 __init__.py
│   │   ├── ⚙️ config.py           # Configuration management
│   │   ├── ❌ exceptions.py       # Custom exceptions
│   │   └── 🗄️ config_database.py  # Database configuration
│   │
│   ├── 🗄️ database/               # Database layer
│   │   ├── 📄 __init__.py
│   │   ├── 🔗 connections.py      # Database connections (was multi_database_manager.py)
│   │   ├── 📊 managers.py         # Database operation managers (was csv_database_knowledge.py)
│   │   ├── 📥 company_database_import.py # Company data import utilities
│   │   └── 💾 knowledge/          # Knowledge databases
│   │       ├── 📄 __init__.py
│   │       ├── 📊 csv_database_knowledge.db    # ERP table knowledge (788 tables)
│   │       ├── 🏢 hoeflon_company.db           # Company info (159 employees)
│   │       └── 🧠 ml_learning.db               # Machine learning data
│   │
│   ├── 🧭 routing/                # Query routing logic
│   │   ├── 📄 __init__.py
│   │   ├── 🧠 intelligent_router.py          # AI-powered query routing
│   │   ├── 🔄 preprocessor.py                # Query preprocessing
│   │   ├── 📊 table_analyzer.py              # Table analysis
│   │   ├── 🗄️ intelligent_table_cache.py     # Table caching
│   │   ├── 🔍 dynamic_table_selector.py      # Table selection
│   │   └── 📈 dynamic_database_analyzer.py   # Database analysis
│   │
│   ├── ⚙️ engines/                # Processing engines
│   │   ├── 📄 __init__.py
│   │   ├── 🔍 query/              # Query generation & validation
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 🛠️ generator.py            # SQL query generation
│   │   │   ├── ✅ validator.py            # Answer validation
│   │   │   ├── 🔄 hybrid.py               # Hybrid query generation
│   │   │   ├── 📋 multi_query_validator.py     # Multi-query validation
│   │   │   └── 🔍 enhanced_result_validator.py # Enhanced validation
│   │   ├── 📊 analysis/           # Analysis engines
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 🎯 accuracy.py             # Accuracy analysis
│   │   │   ├── 📈 confidence.py           # Confidence calculation
│   │   │   ├── 🔍 integrity.py            # Data integrity
│   │   │   ├── 📊 drill_down.py           # Drill-down analysis
│   │   │   ├── 🎯 drill_down_engine.py    # Additional drill-down
│   │   │   └── 🔄 unified_confidence_system.py # Unified confidence
│   │   └── 🧠 intelligence/       # AI-powered engines
│   │       ├── 📄 __init__.py
│   │       ├── 🧠 memory.py               # Conversational memory
│   │       ├── ❓ clarification.py        # Clarification requests
│   │       └── 📝 narrative.py            # Narrative responses
│   │
│   ├── 🏢 services/               # Business logic services
│   │   ├── 📄 __init__.py
│   │   ├── 💬 chat_service.py             # Main chat orchestration
│   │   ├── 🏢 company_service.py          # Company information service
│   │   ├── 🔗 cross_database.py           # Cross-database operations
│   │   ├── 🔍 direct_query_mapper.py      # Direct query mapping
│   │   ├── 🔗 enhanced_transaction_linking_engine.py # Transaction linking
│   │   └── 📊 dashboard_engine.py         # Dashboard services
│   │
│   └── 🌐 api/                    # FastAPI endpoints
│       ├── 📄 __init__.py
│       ├── 💬 chat.py             # Main chat endpoints
│       ├── 🏢 company.py          # Company-specific endpoints  
│       └── ❤️ health.py           # Health check & status
│
├── 🎨 react-frontend/             # React Application
│   ├── 📄 package.json           # Node.js dependencies
│   ├── 🔧 public/                # Static assets
│   └── 💻 src/                   # React source code
│       ├── 📄 App.js             # Main React app
│       ├── 🎨 components/        # React components
│       ├── 📄 index.js           # React entry point
│       ├── 📊 pages/             # React pages
│       └── 🔧 services/          # API services
│
└── 🐍 venv/                      # Python virtual environment
```

## 🎯 KEY FILE PURPOSES

### 🚀 **Entry Points**
- `backend/main.py` - FastAPI application startup
- `react-frontend/src/App.js` - React application startup

### 🔧 **Core Configuration** 
- `backend/core/config.py` - All system configuration
- `backend/core/exceptions.py` - Custom error handling
- `CLAUDE.md` - Project instructions & team roles

### 🗄️ **Database Layer**
- `backend/database/connections.py` - Database connection management
- `backend/database/knowledge/` - SQLite knowledge databases
- `backend/database/managers.py` - Database operations

### 🧭 **Intelligence & Routing**
- `backend/routing/intelligent_router.py` - AI-powered question routing
- `backend/engines/intelligence/` - AI processing engines
- `backend/services/chat_service.py` - Main chat orchestration

### 🌐 **API Endpoints**
- `backend/api/chat.py` - Main chat API
- `backend/api/company.py` - Company information API
- `backend/api/health.py` - System health monitoring

## 🔍 COMMON WORKFLOWS

### **Adding New Features:**
1. **Business Logic** → `backend/services/`
2. **API Endpoint** → `backend/api/`
3. **Frontend Component** → `react-frontend/src/components/`

### **Database Changes:**
1. **Configuration** → `backend/core/config.py`
2. **Connections** → `backend/database/connections.py`
3. **Knowledge Updates** → `backend/database/knowledge/`

### **AI Intelligence:**
1. **Query Routing** → `backend/routing/intelligent_router.py`
2. **Processing** → `backend/engines/intelligence/`
3. **Responses** → `backend/services/chat_service.py`

## 🚧 DEVELOPMENT COMMANDS

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

### **Testing:**
```bash
curl http://localhost:8504/status
curl -X POST http://localhost:8504/chat -H "Content-Type: application/json" -d '{"message": "test", "session_id": "test"}'
```

## 🎯 BENEFITS OF MODULAR STRUCTURE

✅ **Clear Navigation** - Know exactly where to find any functionality  
✅ **Separation of Concerns** - Each module has a specific responsibility  
✅ **Easy Debugging** - Isolated components make issues easier to track  
✅ **Scalable Architecture** - Add new features without affecting existing code  
✅ **Team Development** - Multiple developers can work on different modules  
✅ **Clean Imports** - Logical import paths and dependencies  

---

*Last Updated: 2025-06-20*  
*Version: 2.0.0 - Modular Architecture*