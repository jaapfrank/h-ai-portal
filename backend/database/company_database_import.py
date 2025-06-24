"""
Hoeflon Company Information Database Import System
==================================================

Automatically imports all company information from "Extra hoeflon info" directory
into a structured SQLite database for efficient searching and retrieval.

This solves the problem of slow AI responses by making company data queryable.
"""

import os
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Any
import PyPDF2
import docx
from pathlib import Path

class HoeflonCompanyDatabaseImporter:
    """Import all Hoeflon company information into structured database"""
    
    def __init__(self, db_path: str = "hoeflon_company.db"):
        self.db_path = db_path
        self.base_dir = "/home/jaapfrank/Hoeflon Ridder/Ridder AI"
        self.info_dir = os.path.join(self.base_dir, "Extra hoeflon info")
        self.json_file = os.path.join(self.base_dir, "backend", "hoeflon_company_info.json")
        
    def create_database_schema(self):
        """Create comprehensive database schema for company information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. CONTACTS TABLE - For all phone numbers and contact information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_last TEXT,
            name_first TEXT,
            full_name TEXT,
            phone_internal TEXT,
            phone_mobile TEXT,
            extension TEXT,
            department TEXT,
            role TEXT,
            email TEXT,
            location TEXT,
            is_external BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. ORGANIZATION TABLE - For organizational structure
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS organization (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT,
            role_title TEXT,
            department TEXT,
            manager TEXT,
            team_members TEXT,
            responsibilities TEXT,
            certifications TEXT,
            contact_id INTEGER,
            level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
        ''')
        
        # 3. POLICIES TABLE - For HR policies and procedures
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_type TEXT,
            policy_name TEXT,
            description TEXT,
            requirements TEXT,
            process_steps TEXT,
            contact_person TEXT,
            duration TEXT,
            conditions TEXT,
            document_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 4. COMPANY_INFO TABLE - For general company information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            subcategory TEXT,
            key_name TEXT,
            value TEXT,
            description TEXT,
            document_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 5. SEARCH_INDEX TABLE - For fast text searching
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            record_id INTEGER,
            search_text TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indexes for fast searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name_last, name_first)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_internal, phone_mobile)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_text ON search_index(search_text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_category ON search_index(category)')
        
        conn.commit()
        conn.close()
        print("✅ Database schema created successfully")
    
    def parse_phone_list(self, content: str) -> List[Dict[str, Any]]:
        """Parse the internal phone list into structured contact data"""
        contacts = []
        
        # Find the table data
        lines = content.split('\n')
        in_phone_table = False
        
        for line in lines:
            line = line.strip()
            
            # Detect if we're in a phone table
            if 'Telefoonnummers intern' in line or 'Telefoonnummers extern' in line:
                in_phone_table = True
                is_external = 'extern' in line.lower()
                continue
            
            # Skip table headers and empty lines
            if not line or line.startswith('===') or line.startswith('|') or 'Telefoon' in line:
                continue
            
            # Parse phone entries
            if '|' in line and any(char.isdigit() for char in line):
                parts = line.split('|')
                if len(parts) >= 2:
                    name_part = parts[0].strip()
                    phone_part = parts[1].strip()
                    
                    if name_part and phone_part:
                        # Parse name (handle "Last, First" format)
                        if ',' in name_part:
                            name_last, name_first = name_part.split(',', 1)
                            name_last = name_last.strip()
                            name_first = name_first.strip()
                        else:
                            # Handle cases like "Service" or single names
                            name_parts = name_part.split()
                            if len(name_parts) > 1:
                                name_first = name_parts[0]
                                name_last = ' '.join(name_parts[1:])
                            else:
                                name_first = ""
                                name_last = name_part
                        
                        full_name = f"{name_first} {name_last}".strip()
                        
                        # Parse phone numbers
                        phone_mobile = ""
                        phone_internal = ""
                        extension = ""
                        
                        if phone_part.startswith('06'):
                            phone_mobile = phone_part
                        elif '/' in phone_part:
                            # Handle format like "248/ 06 30 66 95 56"
                            parts = phone_part.split('/')
                            extension = parts[0].strip()
                            if len(parts) > 1:
                                phone_mobile = parts[1].strip()
                        elif phone_part.isdigit() and len(phone_part) <= 4:
                            extension = phone_part
                        else:
                            phone_internal = phone_part
                        
                        contact = {
                            'name_last': name_last,
                            'name_first': name_first,
                            'full_name': full_name,
                            'phone_internal': phone_internal,
                            'phone_mobile': phone_mobile,
                            'extension': extension,
                            'is_external': is_external if 'is_external' in locals() else False
                        }
                        contacts.append(contact)
        
        return contacts
    
    def parse_organization(self, content: str) -> List[Dict[str, Any]]:
        """Parse organizational structure from organigram"""
        org_data = []
        
        # Extract key personnel information
        lines = content.split('\n')
        current_department = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect departments/sections
            if any(keyword in line.lower() for keyword in ['directeur', 'sales', 'engineering', 'operations', 'finance', 'it', 'service', 'machinebouw']):
                if 'directeur' in line.lower():
                    current_department = "Directie"
                elif 'sales' in line.lower():
                    current_department = "Sales & Marketing"
                elif 'engineering' in line.lower():
                    current_department = "Engineering & Innovatie"
                elif 'operations' in line.lower():
                    current_department = "Operations"
                elif 'finance' in line.lower():
                    current_department = "Finance & IT"
                elif 'service' in line.lower():
                    current_department = "Service"
                elif 'machinebouw' in line.lower():
                    current_department = "Machinebouw"
            
            # Extract person names and roles
            if current_department and any(char.isupper() for char in line):
                # Look for name patterns
                words = line.split()
                for word in words:
                    if word and word[0].isupper() and len(word) > 2:
                        # Likely a name
                        org_entry = {
                            'person_name': word,
                            'department': current_department,
                            'role_title': line if len(line) < 100 else "",
                        }
                        org_data.append(org_entry)
        
        return org_data
    
    def parse_policies(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Parse HR policies and procedures"""
        policies = []
        
        if 'geboorteverlof' in filename.lower():
            policy = {
                'policy_type': 'HR',
                'policy_name': 'Geboorteverlof',
                'description': 'Verlof opnemen binnen 4 weken na geboorte',
                'requirements': 'Partner moet zijn bevallen',
                'process_steps': 'Aanvraag via leidinggevende naar HRM@hoeflon.com',
                'contact_person': 'HRM@hoeflon.com',
                'duration': '1 week regulier + aanvullend mogelijk',
                'document_source': filename
            }
            policies.append(policy)
        
        elif 'ouderschapsverlof' in filename.lower():
            policy = {
                'policy_type': 'HR',
                'policy_name': 'Ouderschapsverlof',
                'description': '26 weken totaal ouderschapsverlof',
                'requirements': 'Kind onder 8 jaar',
                'process_steps': 'Aanvraag minimaal 4 weken vooraf bij leidinggevende',
                'contact_person': 'Leidinggevende + HRM@hoeflon.com',
                'duration': '9 weken betaald (70% UWV), 17 weken onbetaald',
                'conditions': 'In 1e levensjaar recht op UWV-uitkering',
                'document_source': filename
            }
            policies.append(policy)
        
        elif 'algemene voorwaarden' in filename.lower():
            policy = {
                'policy_type': 'Legal',
                'policy_name': 'Algemene Voorwaarden',
                'description': 'Hoeflon International B.V. algemene leveringsvoorwaarden',
                'requirements': 'Van toepassing op alle leveringen en diensten',
                'contact_person': 'Rechtbank Gelderland te Arnhem',
                'duration': 'Geldig tot wijziging',
                'conditions': '12 maanden garantie nieuwe producten, 3 maanden werkzaamheden',
                'document_source': filename
            }
            policies.append(policy)
        
        return policies
    
    def import_all_data(self):
        """Import all company data from JSON into database"""
        print("🚀 Starting comprehensive company data import...")
        
        # Create database schema
        self.create_database_schema()
        
        # Load existing JSON data
        if not os.path.exists(self.json_file):
            print(f"❌ JSON file not found: {self.json_file}")
            return
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            company_data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM contacts')
        cursor.execute('DELETE FROM organization')
        cursor.execute('DELETE FROM policies')
        cursor.execute('DELETE FROM company_info')
        cursor.execute('DELETE FROM search_index')
        
        contact_count = 0
        org_count = 0
        policy_count = 0
        info_count = 0
        
        # Process each document
        for filename, content in company_data.items():
            print(f"📄 Processing: {filename}")
            
            if 'telefoonlijst' in filename.lower():
                # Import contacts
                contacts = self.parse_phone_list(content)
                for contact in contacts:
                    cursor.execute('''
                    INSERT INTO contacts (name_last, name_first, full_name, phone_internal, 
                                        phone_mobile, extension, is_external)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        contact['name_last'], contact['name_first'], contact['full_name'],
                        contact['phone_internal'], contact['phone_mobile'], contact['extension'],
                        contact['is_external']
                    ))
                    
                    contact_id = cursor.lastrowid
                    contact_count += 1
                    
                    # Add to search index
                    search_text = f"{contact['full_name']} {contact['name_first']} {contact['name_last']} {contact['phone_mobile']} {contact['extension']}"
                    cursor.execute('''
                    INSERT INTO search_index (table_name, record_id, search_text, category)
                    VALUES (?, ?, ?, ?)
                    ''', ('contacts', contact_id, search_text, 'contact'))
            
            elif 'organigram' in filename.lower():
                # Import organization structure
                org_entries = self.parse_organization(content)
                for org in org_entries:
                    cursor.execute('''
                    INSERT INTO organization (person_name, department, role_title)
                    VALUES (?, ?, ?)
                    ''', (org['person_name'], org['department'], org['role_title']))
                    
                    org_id = cursor.lastrowid
                    org_count += 1
                    
                    # Add to search index
                    search_text = f"{org['person_name']} {org['department']} {org['role_title']}"
                    cursor.execute('''
                    INSERT INTO search_index (table_name, record_id, search_text, category)
                    VALUES (?, ?, ?, ?)
                    ''', ('organization', org_id, search_text, 'organization'))
            
            else:
                # Import policies and general info
                policies = self.parse_policies(filename, content)
                for policy in policies:
                    cursor.execute('''
                    INSERT INTO policies (policy_type, policy_name, description, requirements,
                                        process_steps, contact_person, duration, conditions, document_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        policy['policy_type'], policy['policy_name'], policy['description'],
                        policy.get('requirements', ''), policy.get('process_steps', ''), policy.get('contact_person', ''),
                        policy.get('duration', ''), policy.get('conditions', ''), policy['document_source']
                    ))
                    
                    policy_id = cursor.lastrowid
                    policy_count += 1
                    
                    # Add to search index
                    search_text = f"{policy['policy_name']} {policy['description']} {policy['contact_person']}"
                    cursor.execute('''
                    INSERT INTO search_index (table_name, record_id, search_text, category)
                    VALUES (?, ?, ?, ?)
                    ''', ('policies', policy_id, search_text, 'policy'))
                
                # Store raw content as company info
                cursor.execute('''
                INSERT INTO company_info (category, key_name, value, document_source)
                VALUES (?, ?, ?, ?)
                ''', ('document', filename, content[:2000], filename))  # Limit content size
                
                info_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"""
✅ Company database import completed!

📊 IMPORT STATISTICS:
   • Contacts imported: {contact_count}
   • Organization entries: {org_count}  
   • Policies imported: {policy_count}
   • Info documents: {info_count}
   
📁 Database location: {self.db_path}
🔍 Search index entries: {contact_count + org_count + policy_count}
        """)
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts by name or phone"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search by name (flexible matching)
        search_terms = query.lower().split()
        conditions = []
        params = []
        
        for term in search_terms:
            conditions.append("(LOWER(full_name) LIKE ? OR LOWER(name_first) LIKE ? OR LOWER(name_last) LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
        
        sql = f"""
        SELECT * FROM contacts 
        WHERE {' AND '.join(conditions)}
        ORDER BY full_name
        """
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # Convert to dictionaries
        columns = [desc[0] for desc in cursor.description]
        contacts = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return contacts
    
    def quick_search(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Quick search across all company data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search in search index
        search_terms = query.lower().split()
        conditions = []
        params = []
        
        for term in search_terms:
            conditions.append("LOWER(search_text) LIKE ?")
            params.append(f"%{term}%")
        
        sql = f"""
        SELECT DISTINCT table_name, record_id, category, search_text
        FROM search_index 
        WHERE {' AND '.join(conditions)}
        LIMIT 20
        """
        
        cursor.execute(sql, params)
        index_results = cursor.fetchall()
        
        results = {
            'contacts': [],
            'organization': [],
            'policies': [],
            'summary': f"Found {len(index_results)} matches for '{query}'"
        }
        
        # Get detailed records
        for table_name, record_id, category, search_text in index_results:
            if table_name == 'contacts':
                cursor.execute("SELECT * FROM contacts WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    results['contacts'].append(dict(zip(columns, row)))
            
            elif table_name == 'organization':
                cursor.execute("SELECT * FROM organization WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    results['organization'].append(dict(zip(columns, row)))
            
            elif table_name == 'policies':
                cursor.execute("SELECT * FROM policies WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    results['policies'].append(dict(zip(columns, row)))
        
        conn.close()
        return results

def main():
    """Run the complete import process"""
    importer = HoeflonCompanyDatabaseImporter()
    
    print("🏢 Hoeflon Company Database Import System")
    print("=" * 50)
    
    # Import all data
    importer.import_all_data()
    
    # Test searches
    print("\n🔍 Testing search functionality...")
    
    # Test contact search
    jaap_results = importer.search_contacts("jaap frank")
    print(f"\nSearch for 'jaap frank': {len(jaap_results)} results")
    for contact in jaap_results:
        print(f"  • {contact['full_name']}: {contact['phone_mobile'] or contact['extension'] or contact['phone_internal']}")
    
    # Test quick search
    phone_results = importer.quick_search("telefoonnummer")
    print(f"\nQuick search for 'telefoonnummer': {phone_results['summary']}")
    
    print("\n✅ Database import and testing completed!")

if __name__ == "__main__":
    main()