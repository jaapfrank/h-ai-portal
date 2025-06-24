#!/usr/bin/env python3
"""
CSV Database Knowledge Integration
Integreert de CSV files met ERP database informatie om het systeem slimmer te maken
"""

import csv
import json
import os
from typing import Dict, List, Any
import pandas as pd

class CSVDatabaseKnowledge:
    """Verwerkt CSV database informatie om query generatie te verbeteren"""
    
    def __init__(self, csv_folder_path: str):
        self.csv_folder = csv_folder_path
        self.table_descriptions = {}
        self.table_metadata = {}
        self.column_details = {}
        self.load_all_csv_data()
    
    def load_all_csv_data(self):
        """Laadt alle CSV bestanden met database knowledge"""
        try:
            # Load table descriptions (1.csv)
            file1_path = os.path.join(self.csv_folder, "1.csv")
            if os.path.exists(file1_path):
                self.load_table_descriptions(file1_path)
            
            # Load table metadata (Document2.csv)
            file2_path = os.path.join(self.csv_folder, "Document2.csv")
            if os.path.exists(file2_path):
                self.load_table_metadata(file2_path)
                
            # Load column details (Document3.csv)
            file3_path = os.path.join(self.csv_folder, "Document3.csv")
            if os.path.exists(file3_path):
                self.load_column_details(file3_path)
                
            print(f"✅ CSV Database Knowledge geladen:")
            print(f"   📋 Tabellen: {len(self.table_descriptions)}")
            print(f"   🔧 Metadata: {len(self.table_metadata)}")
            print(f"   📊 Kolommen: {len(self.column_details)}")
            
        except Exception as e:
            print(f"⚠️ Error loading CSV database knowledge: {e}")
    
    def load_table_descriptions(self, file_path: str):
        """Laadt tabel beschrijvingen uit 1.csv"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f, delimiter=';')
                        for row in reader:
                            table_name = row.get('Tablename', '').strip()
                            description = row.get('Description', '').strip()
                            if table_name and description:
                                self.table_descriptions[table_name] = description
                    print(f"📄 Table descriptions loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"Error loading table descriptions: {e}")
    
    def load_table_metadata(self, file_path: str):
        """Laadt tabel metadata uit Document2.csv"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f, delimiter=';')
                        for row in reader:
                            table_name = row.get('Tablename', '').strip()
                            if table_name:
                                self.table_metadata[table_name] = {
                                    'description': row.get('Description', '').strip(),
                                    'browseable': row.get('Browseable', '').strip(),
                                    'scope': row.get('Scope', '').strip(),
                                    'version': row.get('Version', '').strip()
                                }
                    print(f"📄 Table metadata loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"Error loading table metadata: {e}")
    
    def load_column_details(self, file_path: str):
        """Laadt kolom details uit Document3.csv"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f, delimiter=';')
                        for row in reader:
                            table_name = row.get('Tablename.Tablename', '').strip()
                            column_name = row.get('Column name', '').strip()
                            if table_name and column_name:
                                if table_name not in self.column_details:
                                    self.column_details[table_name] = {}
                                
                                self.column_details[table_name][column_name] = {
                                    'description': row.get('Description', '').strip(),
                                    'data_type': row.get('Data type', '').strip(),
                                    'table_description': row.get('Tablename.Description', '').strip()
                                }
                    print(f"📄 Column details loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"Error loading column details: {e}")
    
    def find_relevant_tables(self, user_question: str) -> List[Dict[str, Any]]:
        """Vindt relevante tabellen op basis van gebruikersvraag"""
        question_lower = user_question.lower()
        relevant_tables = []
        
        # Keywords mapping naar tabellen (inclusief meervoud)
        table_keywords = {
            'machine': ['U_SERIENUMMERSHOEFLON', 'V_R_SERVICEOBJECT', 'R_SERVICEOBJECT'],
            'machines': ['U_SERIENUMMERSHOEFLON', 'V_R_SERVICEOBJECT', 'R_SERVICEOBJECT'],
            'omzet': ['R_SALESINVOICE', 'R_SALESORDER'], 
            'revenue': ['R_SALESINVOICE', 'R_SALESORDER'],
            'factuur': ['R_SALESINVOICE', 'R_PURCHASEINVOICE'],
            'facturen': ['R_SALESINVOICE', 'R_PURCHASEINVOICE'],
            'invoice': ['R_SALESINVOICE', 'R_PURCHASEINVOICE'],
            'invoices': ['R_SALESINVOICE', 'R_PURCHASEINVOICE'],
            'klant': ['R_RELATION', 'R_DEBTOR'],
            'klanten': ['R_RELATION', 'R_DEBTOR'],
            'customer': ['R_RELATION', 'R_DEBTOR'],
            'customers': ['R_RELATION', 'R_DEBTOR'],
            'leverancier': ['R_CREDITOR', 'R_RELATION'],
            'leveranciers': ['R_CREDITOR', 'R_RELATION'],
            'supplier': ['R_CREDITOR', 'R_RELATION'],
            'suppliers': ['R_CREDITOR', 'R_RELATION'],
            'voorraad': ['R_ITEMWAREHOUSE', 'R_STOCKINFO'],
            'inventory': ['R_ITEMWAREHOUSE', 'R_STOCKINFO'],
            'productie': ['R_JOBORDER', 'R_WORKACTIVITY'],
            'production': ['R_JOBORDER', 'R_WORKACTIVITY'],
            'medewerker': ['R_EMPLOYEE', 'R_PROJECTTIME'],
            'medewerkers': ['R_EMPLOYEE', 'R_PROJECTTIME'],
            'employee': ['R_EMPLOYEE', 'R_PROJECTTIME'],
            'employees': ['R_EMPLOYEE', 'R_PROJECTTIME'],
            'artikel': ['R_ITEM', 'R_ITEMGROUP'],
            'artikelen': ['R_ITEM', 'R_ITEMGROUP'],
            'item': ['R_ITEM', 'R_ITEMGROUP'],
            'items': ['R_ITEM', 'R_ITEMGROUP']
        }
        
        # Zoek relevante tabellen
        for keyword, tables in table_keywords.items():
            if keyword in question_lower:
                for table in tables:
                    table_info = self.get_table_info(table)
                    if table_info:
                        relevant_tables.append(table_info)
        
        return relevant_tables
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Geeft complete informatie over een tabel"""
        if table_name not in self.table_descriptions:
            return None
            
        return {
            'table_name': table_name,
            'description': self.table_descriptions.get(table_name, ''),
            'metadata': self.table_metadata.get(table_name, {}),
            'columns': self.column_details.get(table_name, {}),
            'column_count': len(self.column_details.get(table_name, {}))
        }
    
    def suggest_better_query(self, user_question: str, current_table: str) -> Dict[str, Any]:
        """Suggereert betere queries op basis van database kennis"""
        relevant_tables = self.find_relevant_tables(user_question)
        
        suggestions = {
            'current_table': current_table,
            'current_description': self.table_descriptions.get(current_table, 'Onbekend'),
            'alternative_tables': [],
            'suggested_columns': [],
            'business_context': ''
        }
        
        # Vind alternatieve tabellen
        for table_info in relevant_tables:
            if table_info['table_name'] != current_table:
                suggestions['alternative_tables'].append({
                    'table': table_info['table_name'],
                    'description': table_info['description'],
                    'reason': self._get_suggestion_reason(user_question, table_info)
                })
        
        # Suggereer relevante kolommen
        if current_table in self.column_details:
            columns = self.column_details[current_table]
            suggestions['suggested_columns'] = self._get_relevant_columns(user_question, columns)
        
        # Business context
        suggestions['business_context'] = self._generate_business_context(user_question, relevant_tables)
        
        return suggestions
    
    def _get_suggestion_reason(self, question: str, table_info: Dict) -> str:
        """Geeft reden waarom tabel relevant is"""
        question_lower = question.lower()
        description = table_info['description'].lower()
        
        if 'machine' in question_lower and 'serienummer' in description:
            return "Bevat serienummers van machines"
        elif 'omzet' in question_lower and 'factuur' in description:
            return "Bevat facturatiegegevens voor omzetberekening"
        elif 'productie' in question_lower and ('bon' in description or 'werk' in description):
            return "Bevat productiegegevens en bewerkingen"
        else:
            return f"Relevant voor: {table_info['description']}"
    
    def _get_relevant_columns(self, question: str, columns: Dict) -> List[Dict[str, str]]:
        """Vindt relevante kolommen voor de vraag"""
        question_lower = question.lower()
        relevant_cols = []
        
        for col_name, col_info in columns.items():
            col_desc_lower = col_info['description'].lower()
            
            # Check relevantie
            if ('aantal' in question_lower and ('count' in col_name.lower() or 'quantity' in col_name.lower())) or \
               ('datum' in question_lower and 'date' in col_name.lower()) or \
               ('bedrag' in question_lower and 'amount' in col_name.lower()) or \
               ('jaar' in question_lower and 'date' in col_name.lower()):
                relevant_cols.append({
                    'column': col_name,
                    'description': col_info['description'],
                    'data_type': col_info['data_type']
                })
        
        return relevant_cols[:10]  # Max 10 suggesties
    
    def _generate_business_context(self, question: str, tables: List[Dict]) -> str:
        """Genereert business context op basis van vraag en tabellen"""
        question_lower = question.lower()
        
        if 'machine' in question_lower:
            return "Machines kunnen geteld worden via serienummers (U_SERIENUMMERSHOEFLON) of service objecten (V_R_SERVICEOBJECT). Verschil: serienummers = werkelijke machines, service objecten = registraties."
        elif 'omzet' in question_lower:
            return "Omzet berekenen via R_SALESINVOICE (gefactureerde bedragen). Let op: externe verkopen uitsluiten met FK_INVOICERELATION filters."
        elif 'productie' in question_lower:
            return "Productiegegevens in R_JOBORDER (bonnen) en R_WORKACTIVITY (bewerkingen). Status en gereed-datum bepalen voltooiing."
        else:
            return "Gebruik CSV database kennis voor accurate query's en juiste tabel selectie."
    
    def export_knowledge_summary(self, output_path: str):
        """Exporteert overzicht van database kennis"""
        summary = {
            'total_tables': len(self.table_descriptions),
            'key_tables': {
                'machines': ['U_SERIENUMMERSHOEFLON', 'V_R_SERVICEOBJECT'],
                'sales': ['R_SALESINVOICE', 'R_SALESORDER'], 
                'production': ['R_JOBORDER', 'R_WORKACTIVITY'],
                'inventory': ['R_ITEMWAREHOUSE', 'R_STOCKINFO'],
                'customers': ['R_RELATION', 'R_DEBTOR']
            },
            'machine_tables_details': {
                table: self.get_table_info(table) 
                for table in ['U_SERIENUMMERSHOEFLON', 'V_R_SERVICEOBJECT', 'R_SERVICEOBJECT']
                if self.get_table_info(table)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Database knowledge summary exported to: {output_path}")

# Global instance
csv_db_knowledge = None

def get_csv_database_knowledge():
    """Returns global CSV database knowledge instance"""
    global csv_db_knowledge
    if csv_db_knowledge is None:
        csv_folder = os.path.join(os.path.dirname(__file__), "..", "Extra erp database info")
        csv_db_knowledge = CSVDatabaseKnowledge(csv_folder)
    return csv_db_knowledge

def enhance_query_with_csv_knowledge(user_question: str, current_table: str = None) -> Dict[str, Any]:
    """Verbetert query met CSV database kennis"""
    knowledge = get_csv_database_knowledge()
    
    # Vind relevante tabellen
    relevant_tables = knowledge.find_relevant_tables(user_question)
    
    # Krijg suggesties voor betere query
    suggestions = knowledge.suggest_better_query(user_question, current_table) if current_table else {}
    
    return {
        'relevant_tables': relevant_tables,
        'suggestions': suggestions,
        'total_tables_available': len(knowledge.table_descriptions)
    }

if __name__ == "__main__":
    # Test the CSV database knowledge
    csv_folder = "../Extra erp database info"
    knowledge = CSVDatabaseKnowledge(csv_folder)
    
    # Test queries
    test_questions = [
        "Hoeveel machines hebben we dit jaar verkocht?",
        "Wat is de omzet van dit jaar?", 
        "Welke facturen zijn er deze maand?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 VRAAG: {question}")
        enhancement = enhance_query_with_csv_knowledge(question)
        print(f"   📋 Relevante tabellen: {len(enhancement['relevant_tables'])}")
        for table in enhancement['relevant_tables'][:3]:
            print(f"      • {table['table_name']}: {table['description']}")