#!/usr/bin/env python3
"""
Conversational Memory Engine for Hoeflon Ridder ERP AI
Enables follow-up questions, context retention, and reference to previous results
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import pandas as pd

class ConversationalMemoryEngine:
    """
    Advanced conversational memory system that:
    - Stores conversation history per session
    - Enables follow-up questions and context references
    - Maintains query results for deeper analysis
    - Supports "wat bedoelt u met..." type questions
    - Enables drilling down into previous results
    """
    
    def __init__(self, memory_storage_path: str = None):
        self.memory_storage_path = memory_storage_path or "/home/jaapfrank/Hoeflon Ridder/Ridder AI/memory"
        os.makedirs(self.memory_storage_path, exist_ok=True)
        self.sessions = {}  # Active session memory
        
    def create_session(self, user_id: str = None) -> str:
        """Create new conversation session"""
        session_id = f"{user_id or 'user'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "user_id": user_id,
            "conversation_history": [],
            "query_results": {},
            "context_entities": set(),
            "last_activity": datetime.now().isoformat(),
            "session_summary": ""
        }
        
        self._save_session(session_id)
        return session_id
    
    def add_interaction(self, session_id: str, user_question: str, ai_response: str, 
                       sql_query: str = None, results: List[Dict] = None, 
                       confidence: float = None, chart_data: str = None) -> None:
        """Add interaction to conversation memory"""
        
        if session_id not in self.sessions:
            self.sessions[session_id] = self._load_session(session_id) or {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "query_results": {},
                "context_entities": set(),
                "last_activity": datetime.now().isoformat(),
                "session_summary": ""
            }
        
        interaction_id = f"interaction_{len(self.sessions[session_id]['conversation_history']) + 1}"
        
        interaction = {
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "user_question": user_question,
            "ai_response": ai_response,
            "sql_query": sql_query,
            "results_count": len(results) if results else 0,
            "confidence": confidence,
            "has_chart": chart_data is not None,
            "entities_mentioned": self._extract_entities(user_question)
        }
        
        # Store full results for follow-up queries
        if results:
            self.sessions[session_id]["query_results"][interaction_id] = {
                "results": results,
                "sql_query": sql_query,
                "question": user_question,
                "timestamp": datetime.now().isoformat(),
                "chart_data": chart_data
            }
        
        # Update context entities
        self.sessions[session_id]["context_entities"].update(interaction["entities_mentioned"])
        
        # Add to conversation history
        self.sessions[session_id]["conversation_history"].append(interaction)
        self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        # Update session summary
        self._update_session_summary(session_id)
        
        # Save to persistent storage
        self._save_session(session_id)
    
    def get_conversation_context(self, session_id: str, current_question: str) -> Dict[str, Any]:
        """Get relevant conversation context for current question"""
        
        if session_id not in self.sessions:
            session_data = self._load_session(session_id)
            if not session_data:
                return {"context_type": "new_session", "context": ""}
            self.sessions[session_id] = session_data
        
        session = self.sessions[session_id]
        current_entities = self._extract_entities(current_question)
        
        # Detect follow-up question patterns
        context_type = self._detect_question_type(current_question, session)
        
        if context_type == "follow_up":
            return self._get_follow_up_context(session, current_question, current_entities)
        elif context_type == "clarification":
            return self._get_clarification_context(session, current_question)
        elif context_type == "drill_down":
            return self._get_drill_down_context(session, current_question, current_entities)
        elif context_type == "reference":
            return self._get_reference_context(session, current_question, current_entities)
        else:
            return self._get_general_context(session, current_entities)
    
    def _detect_question_type(self, question: str, session: Dict) -> str:
        """Detect the type of question based on patterns"""
        question_lower = question.lower()
        
        # Follow-up indicators
        follow_up_patterns = [
            "en nu", "vervolgens", "daarna", "hierna", "dan nu", "wat nu",
            "verder", "meer details", "extra info", "aanvullend"
        ]
        
        # Clarification indicators  
        clarification_patterns = [
            "wat bedoel", "wat betekent", "leg uit", "verduidelijk", "explain",
            "hoe zit", "wat houdt in", "wat is", "snap niet", "begrijp niet"
        ]
        
        # Drill down indicators
        drill_down_patterns = [
            "specificeer", "details van", "breakdown", "verdieping", "zoom in",
            "per ", "van die", "daarvan", "ervan", "specifieke"
        ]
        
        # Reference indicators (referring to previous results)
        reference_patterns = [
            "die nummers", "die cijfers", "dat resultaat", "die lijst", "die data",
            "vorige", "eerder", "hierboven", "zojuist", "net genoemd"
        ]
        
        if any(pattern in question_lower for pattern in follow_up_patterns):
            return "follow_up"
        elif any(pattern in question_lower for pattern in clarification_patterns):
            return "clarification"
        elif any(pattern in question_lower for pattern in drill_down_patterns):
            return "drill_down"
        elif any(pattern in question_lower for pattern in reference_patterns):
            return "reference"
        else:
            return "general"
    
    def _get_follow_up_context(self, session: Dict, question: str, entities: set) -> Dict[str, Any]:
        """Get context for follow-up questions"""
        last_interactions = session["conversation_history"][-3:]  # Last 3 interactions
        
        # Find most relevant previous interaction
        relevant_interaction = None
        for interaction in reversed(last_interactions):
            if any(entity in interaction.get("user_question", "").lower() for entity in entities):
                relevant_interaction = interaction
                break
        
        if not relevant_interaction:
            relevant_interaction = last_interactions[-1] if last_interactions else None
        
        context = {
            "context_type": "follow_up",
            "previous_question": relevant_interaction.get("user_question", "") if relevant_interaction else "",
            "previous_response": relevant_interaction.get("ai_response", "") if relevant_interaction else "",
            "previous_results": self._get_interaction_results(session, relevant_interaction.get("interaction_id")) if relevant_interaction and relevant_interaction.get("interaction_id") else None,
            "context_message": f"💭 **Vervolg op**: '{relevant_interaction.get('user_question', '') if relevant_interaction else ''}'"
        }
        
        return context
    
    def _get_clarification_context(self, session: Dict, question: str) -> Dict[str, Any]:
        """Get context for clarification questions"""
        last_interaction = session["conversation_history"][-1] if session["conversation_history"] else None
        
        context = {
            "context_type": "clarification",
            "needs_clarification_about": last_interaction.get("user_question", "") if last_interaction else "",
            "previous_response": last_interaction.get("ai_response", "") if last_interaction else "",
            "context_message": f"🤔 **Verduidelijking van**: '{last_interaction.get('user_question', '') if last_interaction else ''}'"
        }
        
        return context
    
    def _get_drill_down_context(self, session: Dict, question: str, entities: set) -> Dict[str, Any]:
        """Get context for drill-down questions"""
        # Find interactions with shared entities
        relevant_interactions = []
        for interaction in reversed(session["conversation_history"][-5:]):
            interaction_entities = set(interaction.get("entities_mentioned", []))
            if interaction_entities & entities:  # Intersection
                relevant_interactions.append(interaction)
        
        most_relevant = relevant_interactions[0] if relevant_interactions else session["conversation_history"][-1] if session["conversation_history"] else None
        
        context = {
            "context_type": "drill_down",
            "drill_down_target": most_relevant.get("user_question", "") if most_relevant else "",
            "available_data": self._get_interaction_results(session, most_relevant.get("interaction_id")) if most_relevant and most_relevant.get("interaction_id") else None,
            "context_message": f"🔍 **Dieper inzoomen op**: '{most_relevant.get('user_question', '') if most_relevant else ''}'"
        }
        
        return context
    
    def _get_reference_context(self, session: Dict, question: str, entities: set) -> Dict[str, Any]:
        """Get context for questions referring to previous results"""
        # Look for recent interactions with numerical results
        relevant_interactions = []
        for interaction in reversed(session["conversation_history"][-10:]):
            if interaction.get("results_count", 0) > 0:
                relevant_interactions.append(interaction)
        
        # Get the most recent interaction with results
        target_interaction = relevant_interactions[0] if relevant_interactions else None
        
        context = {
            "context_type": "reference",
            "referenced_interaction": target_interaction,
            "referenced_results": self._get_interaction_results(session, target_interaction.get("interaction_id")) if target_interaction and target_interaction.get("interaction_id") else None,
            "context_message": f"📊 **Referentie naar**: '{target_interaction.get('user_question', '') if target_interaction else 'vorige resultaten'}'"
        }
        
        return context
    
    def _get_general_context(self, session: Dict, entities: set) -> Dict[str, Any]:
        """Get general conversation context"""
        recent_topics = []
        for interaction in session.get("conversation_history", [])[-5:]:
            interaction_entities = set(interaction.get("entities_mentioned", []))
            if interaction_entities & set(entities):
                recent_topics.append(interaction.get("user_question", ""))
        
        context = {
            "context_type": "general",
            "recent_topics": recent_topics,
            "session_summary": session.get("session_summary", ""),
            "context_message": f"💬 **Conversatie context**: {len(session['conversation_history'])} eerdere vragen besproken" if session.get("conversation_history") else ""
        }
        
        return context
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text for context matching"""
        text_lower = text.lower()
        entities = []
        
        # Machine types
        machine_types = ["c6", "c30", "c10", "c1", "mc1200", "c4", "kraan", "kranen", "machine", "machines"]
        entities.extend([t for t in machine_types if t in text_lower])
        
        # Time periods
        time_entities = ["jaar", "maand", "kwartaal", "week", "dag", "2024", "2025", "2023", "dit jaar", "vorig jaar"]
        entities.extend([t for t in time_entities if t in text_lower])
        
        # Business terms
        business_entities = ["omzet", "revenue", "verkoop", "productie", "klant", "klanten", "factuur", "order"]
        entities.extend([t for t in business_entities if t in text_lower])
        
        # Numbers (object numbers from user's example)
        import re
        numbers = re.findall(r'\b\d{4,}\b', text)
        entities.extend(numbers)
        
        return list(set(entities))  # Remove duplicates as list
    
    def _get_interaction_results(self, session: Dict, interaction_id: str) -> Optional[Dict]:
        """Get stored results for specific interaction"""
        return session.get("query_results", {}).get(interaction_id)
    
    def _update_session_summary(self, session_id: str) -> None:
        """Update session summary with key topics"""
        session = self.sessions[session_id]
        
        # Extract key topics from conversation
        all_entities = session.get("context_entities", set())
        recent_questions = [interaction.get("user_question", "") for interaction in session.get("conversation_history", [])[-5:]]
        
        summary = f"Sessie met {len(session.get('conversation_history', []))} vragen. "
        summary += f"Hoofdonderwerpen: {', '.join(list(all_entities)[:10])}. "
        summary += f"Laatste vragen over: {', '.join([q[:30] + '...' for q in recent_questions[-3:]])}"
        
        session["session_summary"] = summary
    
    def _save_session(self, session_id: str) -> None:
        """Save session to persistent storage"""
        session_data = self.sessions.get(session_id, {}).copy()
        
        # Convert set to list for JSON serialization
        if "context_entities" in session_data:
            session_data["context_entities"] = list(session_data["context_entities"])
        
        session_file = os.path.join(self.memory_storage_path, f"{session_id}.json")
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_session(self, session_id: str) -> Optional[Dict]:
        """Load session from persistent storage"""
        session_file = os.path.join(self.memory_storage_path, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Convert list back to set
            if "context_entities" in session_data:
                session_data["context_entities"] = set(session_data["context_entities"])
            
            return session_data
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for session"""
        if session_id not in self.sessions:
            session_data = self._load_session(session_id)
            if not session_data:
                return []
            self.sessions[session_id] = session_data
        
        history = self.sessions[session_id].get("conversation_history", [])
        return history[-limit:] if limit else history
    
    def search_conversation_history(self, session_id: str, search_term: str) -> List[Dict]:
        """Search through conversation history"""
        history = self.get_session_history(session_id, limit=None)
        
        matching_interactions = []
        search_lower = search_term.lower()
        
        for interaction in history:
            if (search_lower in interaction.get("user_question", "").lower() or 
                search_lower in interaction.get("ai_response", "").lower()):
                matching_interactions.append(interaction)
        
        return matching_interactions
    
    def get_followup_suggestions(self, session_id: str) -> List[str]:
        """Generate follow-up question suggestions based on conversation history"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        last_interaction = session.get("conversation_history", [])[-1] if session.get("conversation_history") else None
        
        if not last_interaction:
            return []
        
        suggestions = []
        last_question = last_interaction.get("user_question", "").lower()
        entities = last_interaction.get("entities_mentioned", [])
        
        # Generate contextual follow-up suggestions
        if any(term in last_question for term in ["hoeveel", "aantal"]):
            suggestions.extend([
                "Kun je dit vergelijken met vorig jaar?",
                "Wat is de trend over de laatste maanden?",
                "Kun je dit uitsplitsen per type?",
                "Hoe zit dit verdeeld over klanten?"
            ])
        
        if any(term in last_question for term in ["omzet", "revenue"]):
            suggestions.extend([
                "Wat zijn de top 5 klanten hierbij?",
                "Hoe is de winstmarge hiervan?",
                "Vergelijk dit met vorige periodes",
                "Welke producten dragen het meest bij?"
            ])
        
        if "kraan" in last_question or any(machine in last_question for machine in ["c6", "c30", "c10"]):
            suggestions.extend([
                "Welke klanten kopen deze machines?",
                "Wat is de productietijd hiervoor?",
                "Vergelijk met andere machine types",
                "Wat is de omzet per machine?"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions

# Global instance for use in main app
conversational_memory = ConversationalMemoryEngine()

if __name__ == "__main__":
    # Test the conversational memory system
    print("🧠 Testing Conversational Memory Engine...")
    
    memory = ConversationalMemoryEngine()
    
    # Create test session
    session_id = memory.create_session("test_user")
    print(f"✅ Created session: {session_id}")
    
    # Add test interactions
    memory.add_interaction(
        session_id=session_id,
        user_question="Hoeveel C6 machines zijn er dit jaar gebouwd?",
        ai_response="Er zijn 72 C6 machines gebouwd dit jaar.",
        sql_query="SELECT COUNT(*) FROM ...",
        results=[{"count": 72}],
        confidence=0.95
    )
    
    memory.add_interaction(
        session_id=session_id,
        user_question="En wat is de omzet daarvan?",
        ai_response="De omzet van C6 machines dit jaar is €15.2 miljoen.",
        sql_query="SELECT SUM(amount) FROM ...",
        results=[{"revenue": 15200000}],
        confidence=0.88
    )
    
    # Test context retrieval
    context = memory.get_conversation_context(session_id, "Kun je die nummers uitleggen?")
    print(f"\n📊 Context detected: {context['context_type']}")
    print(f"💭 Context message: {context.get('context_message', '')}")
    
    # Test follow-up suggestions
    suggestions = memory.get_followup_suggestions(session_id)
    print(f"\n💡 Follow-up suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print("\n✅ Conversational Memory Engine test completed!")