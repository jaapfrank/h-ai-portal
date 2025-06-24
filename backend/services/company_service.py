"""
Company Database Search Integration
==================================

Fast database search for Hoeflon company information.
Replaces slow AI processing with instant database lookups.
"""

import sqlite3
import os
import re
from typing import Dict, List, Any, Optional, Tuple

class CompanyDatabaseSearch:
    """Fast database search for company information"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to database/knowledge directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(backend_dir, "database", "knowledge", "hoeflon_company.db")
        else:
            self.db_path = db_path
    
    def is_company_question(self, question: str) -> bool:
        """Detect if this is a company information question"""
        question_lower = question.lower()
        
        # Phone number questions
        phone_patterns = [
            "telefoonnummer", "telefoon", "nummer van", "bel", "bellen",
            "bereikbaar", "contact", "phone", "number"
        ]
        
        # Organization questions  
        org_patterns = [
            "wie is", "wie werkt", "directeur", "manager", "hoofd", "leidinggevende",
            "afdeling", "team", "collega", "medewerker", "personeel"
        ]
        
        # Policy questions
        policy_patterns = [
            "verlof", "vakantie", "ouderschapsverlof", "geboorteverlof", 
            "hr", "aanvragen", "procedure", "beleid", "voorwaarden"
        ]
        
        # Company info questions
        company_patterns = [
            "hoeflon", "bedrijf", "adres", "vestiging", "kantoor", "barneveld",
            "algemene voorwaarden", "garantie", "organisatie"
        ]
        
        all_patterns = phone_patterns + org_patterns + policy_patterns + company_patterns
        
        return any(pattern in question_lower for pattern in all_patterns)
    
    def extract_name_from_question(self, question: str) -> Optional[str]:
        """Extract person name from question"""
        question_lower = question.lower()
        
        # Common patterns for asking about people (specific patterns first!)
        patterns = [
            r"wie\s+is\s+de\s+manager\s+van\s+(.+)$",  # "Wie is de manager van X" - FIRST!
            r"wie\s+is\s+de\s+leidinggevende\s+van\s+(.+)$",  # "Wie is de leidinggevende van X"
            r"leidinggevende.*?van\s+(.+)$",  # For manager questions  
            r"manager.*?van\s+(.+)$",
            r"telefoonnummer.*?van\s+(.+)$",  # Match to end of string
            r"telefoon.*?van\s+(.+)$", 
            r"nummer.*?van\s+(.+)$",
            r"contact.*?met\s+(.+)$",
            r"bel.*?naar\s+(.+)$",
            r"wie\s+is\s+(.+)$",  # Generic "wie is" - LAST!
            r"(?:^|\s)(.+?)\s+telefoonnummer",
            r"(?:^|\s)(.+?)\s+telefoon",
            r"(?:^|\s)(.+?)\s+nummer"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                name = match.group(1).strip()
                # Clean up common words and punctuation
                name = re.sub(r'\b(het|de|een|wat|is|van|naar|met)\b', '', name).strip()
                name = re.sub(r'[?!.,]', '', name).strip()  # Remove punctuation
                if name and len(name) > 1:
                    return name
        
        return None
    
    def search_contact_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for contacts by name (flexible matching)"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Flexible name search - split and search individual parts
        name_parts = name.lower().split()
        conditions = []
        params = []
        
        for part in name_parts:
            if len(part) > 1:  # Skip single character parts
                conditions.append("""
                (LOWER(full_name) LIKE ? OR 
                 LOWER(name_first) LIKE ? OR 
                 LOWER(name_last) LIKE ?)
                """)
                params.extend([f"%{part}%", f"%{part}%", f"%{part}%"])
        
        if not conditions:
            conn.close()
            return []
        
        # Use AND logic for better precision
        where_clause = " AND ".join(conditions)
        
        sql = f"""
        SELECT name_first, name_last, full_name, phone_internal, phone_mobile, 
               extension, department, role, email, is_external
        FROM contacts 
        WHERE {where_clause}
        ORDER BY 
            CASE 
                WHEN LOWER(full_name) = LOWER(?) THEN 1
                WHEN LOWER(full_name) LIKE LOWER(?) THEN 2
                ELSE 3
            END,
            full_name
        LIMIT 5
        """
        
        # Add exact match parameters for ordering
        all_params = params + [name, f"%{name}%"]
        
        cursor.execute(sql, all_params)
        results = cursor.fetchall()
        
        # Convert to dictionaries
        columns = ['name_first', 'name_last', 'full_name', 'phone_internal', 
                  'phone_mobile', 'extension', 'department', 'role', 'email', 'is_external']
        contacts = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return contacts
    
    def search_organization_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search organization structure by person name"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        name_parts = name.lower().split()
        conditions = []
        params = []
        
        for part in name_parts:
            if len(part) > 1:
                conditions.append("LOWER(person_name) LIKE ?")
                params.append(f"%{part}%")
        
        if not conditions:
            conn.close()
            return []
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
        SELECT person_name, role_title, department, manager, team_members, 
               responsibilities, certifications
        FROM organization 
        WHERE {where_clause}
        ORDER BY person_name
        LIMIT 5
        """
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        columns = ['person_name', 'role_title', 'department', 'manager', 
                  'team_members', 'responsibilities', 'certifications']
        org_entries = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return org_entries
    
    def search_policies(self, query: str) -> List[Dict[str, Any]]:
        """Search HR policies and procedures"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query_lower = query.lower()
        
        # Search in policy content
        sql = """
        SELECT policy_type, policy_name, description, requirements, 
               process_steps, contact_person, duration, conditions
        FROM policies 
        WHERE LOWER(policy_name) LIKE ? OR 
              LOWER(description) LIKE ? OR 
              LOWER(requirements) LIKE ?
        ORDER BY policy_name
        """
        
        search_term = f"%{query_lower}%"
        cursor.execute(sql, [search_term, search_term, search_term])
        results = cursor.fetchall()
        
        columns = ['policy_type', 'policy_name', 'description', 'requirements',
                  'process_steps', 'contact_person', 'duration', 'conditions']
        policies = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return policies
    
    def handle_company_question(self, question: str) -> Optional[str]:
        """Main handler for company questions - returns direct answer"""
        if not self.is_company_question(question):
            return None
        
        question_lower = question.lower()
        
        # 1. PHONE NUMBER QUESTIONS
        if any(pattern in question_lower for pattern in ["telefoonnummer", "telefoon", "nummer", "bel"]):
            name = self.extract_name_from_question(question)
            if name:
                contacts = self.search_contact_by_name(name)
                if len(contacts) > 1:
                    # Multiple people found - ask for clarification
                    names_list = [contact['full_name'] for contact in contacts]
                    return f"Ik heb meerdere personen gevonden met de naam '{name}': {', '.join(names_list)}. Bedoelde u {names_list[0]}? Gebruik de volledige naam voor een preciezer resultaat."
                elif len(contacts) == 1:
                    contact = contacts[0]  # Best match
                    phone = contact['phone_mobile'] or contact['extension'] or contact['phone_internal']
                    if phone:
                        return f"Het telefoonnummer van {contact['full_name']} is {phone}."
                    else:
                        return f"Ik heb {contact['full_name']} gevonden, maar er is geen telefoonnummer beschikbaar."
                else:
                    return f"Ik kan geen contactgegevens vinden voor '{name}'. Controleer of de naam correct gespeld is."
        
        # 2. ORGANIZATION QUESTIONS
        if any(pattern in question_lower for pattern in ["wie is", "directeur", "manager", "hoofd", "leidinggevende", "verantwoordelijk", "responsible"]):
            if "directeur" in question_lower:
                return "De directeur van Hoeflon is Gert van Hoef."
            
            # Handle manager/supervisor questions
            if any(word in question_lower for word in ["leidinggevende", "manager", "hoofd"]):
                name = self.extract_name_from_question(question)
                if name:
                    # First try to find the person - check for multiple matches
                    contacts = self.search_contact_by_name(name)
                    if len(contacts) > 1:
                        # Multiple people found - ask for clarification
                        names_list = [contact['full_name'] for contact in contacts]
                        return f"Ik heb meerdere personen gevonden met de naam '{name}': {', '.join(names_list)}. Kun je specificeren welke {names_list[0].split()[0]} je bedoelt door de volledige naam te gebruiken?"
                    elif len(contacts) == 1:
                        contact = contacts[0]
                        # Try to find their manager in organization data
                        org_results = self.search_organization_by_name(contact['full_name'])
                        if org_results:
                            org = org_results[0]
                            if org.get('manager'):
                                return f"De leidinggevende van {contact['full_name']} is {org['manager']}."
                            else:
                                return f"{contact['full_name']} werkt bij {org['department']} als {org['role_title']}. Voor leidinggevende informatie neem contact op met HR."
                        else:
                            return f"Ik heb {contact['full_name']} gevonden maar geen organisatie informatie. Neem contact op met HR voor leidinggevende details."
                    else:
                        # Try just first name search for common names like "Daniel"
                        if len(name.split()) == 1 and len(name) > 2:  # Single name like "daniel"
                            # Search more broadly
                            all_contacts = self.search_contact_by_name(name)
                            if len(all_contacts) == 0:
                                return f"Ik kan geen medewerker '{name}' vinden. Controleer de spelling of neem contact op met HR."
                            elif len(all_contacts) == 1:
                                # Found exactly one - use that
                                contact = all_contacts[0]
                                org_results = self.search_organization_by_name(contact['full_name'])
                                if org_results and org_results[0].get('manager'):
                                    return f"De leidinggevende van {contact['full_name']} is {org_results[0]['manager']}."
                                else:
                                    return f"Ik heb {contact['full_name']} gevonden. Voor leidinggevende informatie neem contact op met HR."
                            else:
                                # Multiple found - ask for clarification
                                names_list = [contact['full_name'] for contact in all_contacts[:3]]  # Show max 3
                                return f"Bedoel je {names_list[0]} of een andere {name.title()}? Gebruik de volledige naam voor een preciezer resultaat."
                        else:
                            return f"Ik kan geen medewerker '{name}' vinden. Controleer de spelling of neem contact op met HR."
            
            # Handle responsibility questions (IT, finance, etc.)
            if "verantwoordelijk" in question_lower or "responsible" in question_lower:
                if "it" in question_lower.replace(" ", ""):
                    return "Voor IT zaken kun je contact opnemen met de IT afdeling via het secretariaat: Berthine Methorst, Janine van de Graaf of Jette van de Haar."
                elif "hr" in question_lower:
                    return "Voor HR zaken kun je contact opnemen met Maria Rebel, Bertha Top of Tinsaye Veenema."
                elif "finance" in question_lower or "financie" in question_lower:
                    return "Voor financiële zaken kun je contact opnemen met de Finance afdeling via het secretariaat."
            
            # General name lookup
            name = self.extract_name_from_question(question)
            if name:
                org_results = self.search_organization_by_name(name)
                if org_results:
                    org = org_results[0]
                    return f"{org['person_name']} werkt bij {org['department']} als {org['role_title']}."
        
        # 3. POLICY QUESTIONS  
        if any(pattern in question_lower for pattern in ["verlof", "ouderschapsverlof", "geboorteverlof"]):
            if "geboorteverlof" in question_lower:
                return "Geboorteverlof kun je opnemen binnen 4 weken na de geboorte. Aanvraag via je leidinggevende naar HRM@hoeflon.com."
            elif "ouderschapsverlof" in question_lower:
                return "Ouderschapsverlof: 26 weken totaal (9 weken betaald 70% UWV, 17 weken onbetaald). Aanvraag minimaal 4 weken vooraf bij leidinggevende."
            elif "verlof" in question_lower and any(word in question_lower for word in ["aanvragen", "hoe", "procedure", "proces"]):
                return "Voor verlof aanvragen neem je contact op met je leidinggevende. Voor specifieke verlofregels:\n\n• Geboorteverlof: binnen 4 weken na geboorte, via leidinggevende naar HRM@hoeflon.com\n• Ouderschapsverlof: 26 weken totaal, aanvraag minimaal 4 weken vooraf\n• Algemene vakantieverlof: via je directe leidinggevende"
        
        # 4. GENERAL COMPANY INFO
        if "hoeflon" in question_lower and ("adres" in question_lower or "vestiging" in question_lower):
            return "Hoeflon is gevestigd aan de Zwolleweg 2, 3771 NR Barneveld. Algemeen telefoonnummer: 0342-400288."
        
        return None
    
    def get_contact_summary(self) -> str:
        """Get summary of all contacts for system info"""
        if not os.path.exists(self.db_path):
            return "Company database niet beschikbaar"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM contacts")
        contact_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM organization") 
        org_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM policies")
        policy_count = cursor.fetchone()[0]
        
        conn.close()
        
        return f"Company database: {contact_count} contacten, {org_count} organisatie entries, {policy_count} beleidsregels"

# Global instance for easy import
company_db_search = CompanyDatabaseSearch()

def quick_company_search(question: str) -> Optional[str]:
    """Quick function for easy integration"""
    return company_db_search.handle_company_question(question)

def is_company_info_question(question: str) -> bool:
    """Quick function to check if question is about company info"""
    return company_db_search.is_company_question(question)

def get_company_info(query: str) -> Optional[Dict[str, Any]]:
    """Get company information - wrapper for compatibility"""
    answer = company_db_search.handle_company_question(query)
    if answer:
        return {
            "success": True,
            "answer": answer,
            "source": "company_database"
        }
    return None

def get_company_search(query: str) -> Optional[str]:
    """Search company database - wrapper for compatibility"""
    return company_db_search.handle_company_question(query)

# Test function
def test_searches():
    """Test the database search functionality"""
    searcher = CompanyDatabaseSearch()
    
    test_questions = [
        "wat is het telefoonnummer van jaap frank",
        "telefoon van gert van hoef", 
        "wie is de directeur",
        "hoe vraag ik ouderschapsverlof aan",
        "waar is hoeflon gevestigd"
    ]
    
    print("🔍 Testing Company Database Search")
    print("=" * 40)
    
    for question in test_questions:
        print(f"\nQ: {question}")
        answer = searcher.handle_company_question(question)
        print(f"A: {answer or 'Geen antwoord gevonden'}")
    
    print(f"\n📊 {searcher.get_contact_summary()}")

if __name__ == "__main__":
    test_searches()