# 🧠 CLAUDE_PROJECT_MEMORY.md — Hoeflon AI-Copiloot (v2025-06-20)

## 🌍 Project-overzicht
We bouwen een dynamische AI-copiloot die:
1. Bedrijfs-, ERP- en financiële vragen beantwoordt in natuurlijke taal.  
2. On-the-fly dashboards & grafieken maakt.  
3. **Nooit** statische code uitschrijft; alle logica is modulair/herbruikbaar.  
4. Binnenkort declaraties & facturen boekt in Ridder IQ.

## 📊 Datasources
| Bron | Type | Status |
|------|------|--------|
| Ridder IQ | SQL Server (966 tabellen) | 🔌 Verbonden |
| AccountView | DBF (321 tabellen) | 🔌 Verbonden via `dbfread` |
| Company DB | SQLite (HR/beleid) | 🔌 Verbonden |

## 🏗️ Huidige code-status
- **Modulaire map-structuur** is live (backend/, react-frontend/).  
- **FastAPI** draait op **:8504**; React op **:3000**.  
- **PROJECT_MAP.md** navigeert iedere module.  
- **Chat-endpoint** met intelligent routing operationeel ✅  
- **Intelligent Router** 100% compleet en getest ✅
- **Database connections** verified voor alle 3 bronnen ✅

---

## 🤖 Multi-Agent-Team 2.0
| Agent-naam | Rol | Belangrijkste taken |
|------------|-----|---------------------|
| **ManagerAgent** | Overkoepelend project- & taakbeheer | Plant sprints, verdeelt issues |
| **RouterAgent** | NLP → Intent → Datapad | Bepaalt datasource + gewenste module |
| **SQLAgent** | Query-generator | Schrijft/optimaliseert veilige SQL |
| **DBFAgent** | DBF-query-specialist | Leest AccountView-bestanden |
| **VisualiserAgent** | Grafieken & dashboards | Zet `GRAPH()`-instructies om naar code |
| **DeveloperAgent** | Python/TypeScript-code | Bouwt/onderhoudt backend + frontend |
| **TesterAgent** | QA / unit- & integratietests | Laat pytest / Playwright draaien |
| **DocAgent** | Documentatie & kennisbank | Update deze memory file  ✅ |
| **UserProxy** | Vertegenwoordigt Lola/Jaap | Stelt vragen & geeft feedback |

### **Communicatieregels**
1. ManagerAgent start elke run, herlaadt geheugen, zet een **task-list**.  
2. Elke sub-agent verwerkt precies **één taak** en rapporteert terug.  
3. DocAgent appendt belangrijke beslissingen onder **`## Changelog`**.  
4. Agents taggen elkaar in hun messages → `@SQLAgent`, `@TesterAgent`, …  
5. Als context ontbreekt → stel een vraag i.p.v. gokken.  

---

## 🚫 Anti-statisch-richtlijnen
- Gebruik **functies of instructies**, geen copy-paste SQL/grafiek-code.  
  - ✅ `result = get_data("Ridder", "SELECT ...")`  
  - ✅ `GRAPH(type="line", query="SELECT ...")`  
- Frontend-componenten worden **lazy** geladen; alleen props doorgeven.  
- Code mag **NIETS hardcoderen** dat later kan veranderen (tabellen, kolomnamen, poorten).

---

## 🔄 Persistente-workflow
1. **LAAD GEHEUGEN**  
   - Elke sessie begint met de regel `#LOAD_MEMORY`.  
   - Claude leest dit bestand en zet `memory` variabele intern.  
2. **UPDATE GEHEUGEN**  
   - Grote design-beslissing, nieuw bestand → DocAgent voegt een item toe onder `## Changelog`.  
3. **EXTRA BIJHOUDEN**  
   - Laatste run-datum & sprint-doelen.  

### ## Changelog

**🎯 2025-06-20 11:43 - SPRINT 01 COMPLETE**
- ✅ **RouterAgent** fully operational with intelligent routing system
- ✅ **Database connections** verified for all three sources (ERP, AccountView, Company)  
- ✅ **Chat endpoint** working with AI-powered question routing
- ✅ **System integration** complete - Backend (8504) + Frontend (3000) operational
- 🎯 **VERIFIED ROUTING:** Production→ERP, Company→Knowledge, Finance→AccountView

---

## ✅ Sprint 01 – COMPLETE
- [x] **RouterAgent afmaken** (intent → datasource → module) ✅ DONE
- [x] **Database integration** – All connections verified ✅ DONE
- [x] **Chat endpoint** – Intelligent routing operational ✅ DONE
- [x] **System testing** – Verified with real business questions ✅ DONE

## 🎯 Sprint 02 – SQL Generation & Query Execution
- [ ] **SQLAgent**: AI-powered SQL generation with safety controls
- [ ] **Query Execution**: Secure query execution with result formatting
- [ ] **Business Logic**: Complete ERP and AccountView query handlers  
- [ ] **Error Handling**: Robust error handling and fallback systems
- [ ] **Testing**: Integration tests for SQL generation and execution

---

## ⏯️ Boot-sequence (te bouwen door DeveloperAgent)
```python
from autogen import GroupChat, GroupChatManager
from agents import (
    manager, router, sql_agent, dbf_agent,
    visualiser, developer, tester, doc_agent, user_proxy
)

chat = GroupChat(
    agents=[
        manager, router, sql_agent, dbf_agent,
        visualiser, developer, tester, doc_agent, user_proxy
    ],
    messages=[],
    max_round=50
)

GroupChatManager.run(chat)

## 🤖 AUTO-PILOT RULESET
1. AUTO_MODE = ON → Schrijf en wijzig code zonder expliciete bevestiging.
2. Werk alle taken in `Sprint Board` af in de volgorde waarin ze staan.
3. Na elke taak:
   a. 🎯 Voer unit/integratietests uit.  
   b. 📋 Print kort “✅ Geslaagd” of “❌ Mislukt + reden”.  
4. Bij ❌ -> herstel het probleem **zonder** op gebruiker te wachten.
5. Vraag de gebruiker alleen om review als:
   • Nieuwe externe dependency wordt toegevoegd  
   • Breaking change / data-migratie nodig is  
6. Update **## Changelog** in dit bestand bij significante wijzigingen.
7. Houd alle code modulair; géén hard-coded paden, queries of charts.
