#!/usr/bin/env python3
"""
Enhanced Transaction Linking Engine for Hoeflon AI
Links financial transactions to machines, customers, serial numbers using database relationships
Supports both ERP internal linking and ERP ↔ AccountView cross-database linking
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

class EnhancedTransactionLinkingEngine:
    """Enhanced engine using actual database relationships for linking"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        
        # Database relationship mapping (from actual schema analysis)
        self.erp_relationships = {
            "U_SERIENUMMERSHOEFLON": {
                "FK_ITEMNR": "R_ITEM.PK_R_ITEM",
                "FK_SERVICEOBJECT": "R_SERVICEOBJECT.PK_R_SERVICEOBJECT"
            },
            "R_SALESINVOICE": {
                "FK_INVOICERELATION": "R_RELATION.PK_R_RELATION",
                "FK_ORDERRELATION": "R_RELATION.PK_R_RELATION"
            },
            "R_SALESINVOICEDETAILITEM": {
                "FK_ITEM": "R_ITEM.PK_R_ITEM",
                "FK_SALESINVOICE": "R_SALESINVOICE.PK_R_SALESINVOICE",
                "FK_ORDER": "R_ORDER.PK_R_ORDER"
            },
            "R_SERVICEOBJECT": {
                "FK_ITEM": "R_ITEM.PK_R_ITEM",
                "FK_OBJECTRELATION": "R_RELATION.PK_R_RELATION",
                "FK_ORDERRELATION": "R_RELATION.PK_R_RELATION",
                "FK_SALESORDER": "R_ORDER.PK_R_ORDER"
            }
        }
        
        # Cross-database linking patterns (ERP ↔ AccountView)
        self.cross_db_patterns = {
            "invoice_linking": {
                "accountview_field": "INV_NR",
                "erp_query": "SELECT * FROM R_SALESINVOICE WHERE PK_R_SALESINVOICE = ?",
                "confidence": 0.95
            },
            "customer_name_linking": {
                "accountview_pattern": r"(\d+)-(.+)",  # "3244016-Smakranar"
                "erp_query": "SELECT * FROM R_RELATION WHERE NAME LIKE ?",
                "confidence": 0.85
            },
            "amount_matching": {
                "tolerance": 0.01,  # €0.01 tolerance for amount matching
                "confidence": 0.75
            }
        }
        
        # Cache for performance
        self.cache = {
            "machines": None,
            "customers": None,
            "products": None,
            "invoices": None,
            "last_update": None
        }
    
    def link_transaction_to_operational_data(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced linking using database relationships"""
        
        linked_data = {
            "transaction_id": transaction_data.get("transaction_id", "unknown"),
            "original_data": transaction_data,
            "linked_machines": [],
            "linked_customers": [],
            "linked_products": [],
            "linked_invoices": [],
            "cross_database_links": [],
            "confidence_score": 0.0,
            "linking_methods": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Try cross-database linking (AccountView → ERP)
        cross_db_links = self._cross_database_linking(transaction_data)
        linked_data["cross_database_links"] = cross_db_links["matches"]
        linked_data["confidence_score"] += cross_db_links["confidence"] * 0.6
        linked_data["linking_methods"].extend(cross_db_links["methods"])
        
        # Step 2: ERP relationship-based linking
        if cross_db_links["erp_entities"]:
            relationship_links = self._relationship_based_linking(cross_db_links["erp_entities"])
            linked_data["linked_machines"].extend(relationship_links["machines"])
            linked_data["linked_customers"].extend(relationship_links["customers"])
            linked_data["linked_products"].extend(relationship_links["products"])
            linked_data["confidence_score"] += relationship_links["confidence"] * 0.4
            linked_data["linking_methods"].extend(relationship_links["methods"])
        
        # Step 3: Fallback to pattern matching if low confidence
        if linked_data["confidence_score"] < 0.5:
            pattern_links = self._pattern_matching_fallback(transaction_data)
            linked_data["linked_machines"].extend(pattern_links["machines"])
            linked_data["linked_customers"].extend(pattern_links["customers"])
            linked_data["confidence_score"] += pattern_links["confidence"] * 0.2
            linked_data["linking_methods"].extend(pattern_links["methods"])
        
        return linked_data
    
    def _cross_database_linking(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Link AccountView transaction to ERP entities"""
        
        matches = []
        erp_entities = {"invoices": [], "customers": [], "orders": []}
        confidence = 0.0
        methods = []
        
        try:
            # Method 1: Direct invoice number linking
            inv_nr = transaction_data.get("INV_NR")
            if inv_nr and str(inv_nr).isdigit():
                invoice_links = self._link_by_invoice_number(inv_nr)
                if invoice_links:
                    matches.extend(invoice_links["matches"])
                    erp_entities["invoices"].extend(invoice_links["invoices"])
                    erp_entities["customers"].extend(invoice_links["customers"])
                    confidence += 0.95
                    methods.append(f"Direct invoice linking: {inv_nr}")
            
            # Method 2: Customer name extraction from description  
            trn_desc = transaction_data.get("TRN_DESC", "")
            if trn_desc:
                customer_links = self._link_by_customer_description(trn_desc)
                if customer_links:
                    matches.extend(customer_links["matches"])
                    erp_entities["customers"].extend(customer_links["customers"])
                    confidence += 0.85
                    methods.append(f"Customer name linking: {customer_links['customer_name']}")
            
            # Method 3: Amount matching (as verification)
            amount = transaction_data.get("AMOUNT", 0) or transaction_data.get("CR_AMT", 0) or 0
            if amount and isinstance(amount, (int, float)) and amount > 100:
                amount_links = self._link_by_amount_matching(amount, erp_entities["invoices"])
                if amount_links:
                    confidence += 0.3
                    methods.append(f"Amount verification: €{amount:,.2f}")
        
        except Exception as e:
            methods.append(f"Cross-database linking error: {str(e)}")
        
        return {
            "matches": matches,
            "erp_entities": erp_entities,
            "confidence": min(confidence, 1.0),
            "methods": methods
        }
    
    def _link_by_invoice_number(self, inv_nr: str) -> Optional[Dict[str, Any]]:
        """Link by direct invoice number match"""
        try:
            # Query ERP for matching invoice
            invoice_query = """
                SELECT 
                    si.PK_R_SALESINVOICE,
                    si.TOTALAMOUNT,
                    si.INVOICEDATE,
                    si.DESCRIPTION,
                    si.FK_INVOICERELATION,
                    r.NAME as CUSTOMER_NAME,
                    r.EMAIL as CUSTOMER_EMAIL
                FROM R_SALESINVOICE si
                LEFT JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                WHERE si.PK_R_SALESINVOICE = ?
            """
            
            invoices = self.multi_db_manager.query_erp(invoice_query.replace("?", str(int(inv_nr))))
            
            if invoices:
                invoice = invoices[0]
                return {
                    "matches": [{
                        "type": "invoice_direct",
                        "erp_invoice_id": invoice["PK_R_SALESINVOICE"],
                        "amount": invoice["TOTALAMOUNT"],
                        "customer_name": invoice["CUSTOMER_NAME"],
                        "confidence": 0.95
                    }],
                    "invoices": invoices,
                    "customers": [{"PK_R_RELATION": invoice["FK_INVOICERELATION"], 
                                 "NAME": invoice["CUSTOMER_NAME"]}] if invoice["CUSTOMER_NAME"] else []
                }
        
        except Exception as e:
            print(f"Invoice linking error: {e}")
        
        return None
    
    def _link_by_customer_description(self, description: str) -> Optional[Dict[str, Any]]:
        """Extract customer name from description pattern: '3244016-Smakranar'"""
        try:
            # Pattern: number-customer_name
            pattern_match = re.match(r"(\d+)-(.+)", description.strip())
            if pattern_match:
                invoice_ref = pattern_match.group(1)
                customer_name = pattern_match.group(2).strip()
                
                # Query ERP for matching customer
                customer_query = """
                    SELECT 
                        PK_R_RELATION,
                        NAME,
                        EMAIL,
                        PHONE1
                    FROM R_RELATION 
                    WHERE NAME LIKE ? 
                    ORDER BY NAME
                """
                
                customers = self.multi_db_manager.query_erp(customer_query.replace("?", f"'%{customer_name}%'"))
                
                if customers:
                    return {
                        "matches": [{
                            "type": "customer_name",
                            "customer_name": customer_name,
                            "erp_customer_id": customers[0]["PK_R_RELATION"],
                            "confidence": 0.85
                        }],
                        "customers": customers,
                        "customer_name": customer_name
                    }
        
        except Exception as e:
            print(f"Customer description linking error: {e}")
        
        return None
    
    def _link_by_amount_matching(self, amount: float, known_invoices: List[Dict]) -> Optional[Dict[str, Any]]:
        """Verify linking by matching transaction amounts to invoice amounts"""
        try:
            tolerance = 0.01  # €0.01 tolerance
            
            # Check if amount matches any known invoices
            for invoice in known_invoices:
                invoice_amount = invoice.get("TOTALAMOUNT", 0)
                if isinstance(invoice_amount, (int, float)):
                    if abs(amount - invoice_amount) <= tolerance:
                        return {
                            "matches": [{
                                "type": "amount_verification",
                                "amount_match": f"€{amount:,.2f} ≈ €{invoice_amount:,.2f}",
                                "confidence": 0.9
                            }]
                        }
        
        except Exception as e:
            print(f"Amount matching error: {e}")
        
        return None
    
    def _relationship_based_linking(self, erp_entities: Dict[str, List]) -> Dict[str, Any]:
        """Use ERP foreign key relationships to find linked machines, etc."""
        
        machines = []
        customers = []
        products = []
        confidence = 0.0
        methods = []
        
        try:
            # Link customers to their machines via service objects
            for customer in erp_entities.get("customers", []):
                customer_id = customer.get("PK_R_RELATION")
                if customer_id:
                    machine_links = self._get_customer_machines(customer_id)
                    machines.extend(machine_links["machines"])
                    confidence += machine_links["confidence"]
                    methods.extend(machine_links["methods"])
            
            # Link invoices to their products and machines
            for invoice in erp_entities.get("invoices", []):
                invoice_id = invoice.get("PK_R_SALESINVOICE")
                if invoice_id:
                    product_links = self._get_invoice_products(invoice_id)
                    products.extend(product_links["products"])
                    confidence += product_links["confidence"]
                    methods.extend(product_links["methods"])
        
        except Exception as e:
            methods.append(f"Relationship linking error: {str(e)}")
        
        return {
            "machines": machines,
            "customers": customers,
            "products": products,
            "confidence": min(confidence, 1.0),
            "methods": methods
        }
    
    def _get_customer_machines(self, customer_id: int) -> Dict[str, Any]:
        """Get machines linked to customer via R_SERVICEOBJECT"""
        try:
            machine_query = """
                SELECT 
                    so.PK_R_SERVICEOBJECT,
                    so.SERIALNUMBER,
                    so.DESCRIPTION as SERVICE_DESCRIPTION,
                    i.DESCRIPTION as ITEM_DESCRIPTION,
                    i.CODE as ITEM_CODE,
                    sn.SERIALNUMBER as SERIAL_HOEFLON,
                    sn.STATE
                FROM R_SERVICEOBJECT so
                LEFT JOIN R_ITEM i ON so.FK_ITEM = i.PK_R_ITEM
                LEFT JOIN U_SERIENUMMERSHOEFLON sn ON sn.FK_SERVICEOBJECT = so.PK_R_SERVICEOBJECT
                WHERE so.FK_OBJECTRELATION = ?
                ORDER BY so.DATECREATED DESC
            """
            
            machines = self.multi_db_manager.query_erp(machine_query.replace("?", str(customer_id)))
            
            return {
                "machines": [{
                    "machine_id": m["PK_R_SERVICEOBJECT"],
                    "serial_number": m["SERIALNUMBER"] or m["SERIAL_HOEFLON"],
                    "description": m["SERVICE_DESCRIPTION"] or m["ITEM_DESCRIPTION"],
                    "item_code": m["ITEM_CODE"],
                    "state": m["STATE"],
                    "match_method": "Customer relationship",
                    "confidence": 0.9
                } for m in machines],
                "confidence": 0.4 if machines else 0.0,
                "methods": [f"Found {len(machines)} machines via customer relationship"] if machines else []
            }
        
        except Exception as e:
            return {"machines": [], "confidence": 0.0, "methods": [f"Customer machine query error: {e}"]}
    
    def _get_invoice_products(self, invoice_id: int) -> Dict[str, Any]:
        """Get products from invoice details"""
        try:
            product_query = """
                SELECT 
                    sid.PK_R_SALESINVOICEDETAILITEM,
                    sid.DESCRIPTION,
                    sid.QUANTITY,
                    sid.TOTALAMOUNT,
                    i.CODE as ITEM_CODE,
                    i.DESCRIPTION as ITEM_DESCRIPTION
                FROM R_SALESINVOICEDETAILITEM sid
                LEFT JOIN R_ITEM i ON sid.FK_ITEM = i.PK_R_ITEM
                WHERE sid.FK_SALESINVOICE = ?
            """
            
            products = self.multi_db_manager.query_erp(product_query.replace("?", str(invoice_id)))
            
            return {
                "products": [{
                    "product_id": p["PK_R_SALESINVOICEDETAILITEM"],
                    "code": p["ITEM_CODE"],
                    "description": p["DESCRIPTION"] or p["ITEM_DESCRIPTION"],
                    "quantity": p["QUANTITY"],
                    "amount": p["TOTALAMOUNT"],
                    "match_method": "Invoice relationship",
                    "confidence": 0.95
                } for p in products],
                "confidence": 0.3 if products else 0.0,
                "methods": [f"Found {len(products)} products via invoice relationship"] if products else []
            }
        
        except Exception as e:
            return {"products": [], "confidence": 0.0, "methods": [f"Invoice product query error: {e}"]}
    
    def _pattern_matching_fallback(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to pattern matching when database linking fails"""
        
        machines = []
        customers = []
        confidence = 0.0
        methods = []
        
        # Extract text for pattern analysis
        text_fields = []
        for field in ["TRN_DESC", "DESCRIPTION", "MEMO", "REFERENCE", "BANK_DESC"]:
            value = transaction_data.get(field, "")
            if value and isinstance(value, str):
                text_fields.append(value.upper())
        
        combined_text = " ".join(text_fields)
        
        # Basic machine type detection
        machine_patterns = {
            "C6": ["C6", "HOEFLON C6", "C-6"],
            "C3": ["C3", "HOEFLON C3", "C-3"],
            "C10": ["C10", "HOEFLON C10", "C-10"],
            "C30": ["C30", "HOEFLON C30", "C-30"]
        }
        
        for machine_type, patterns in machine_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                machines.append({
                    "type": machine_type,
                    "match_method": "Text pattern",
                    "confidence": 0.5,
                    "source_text": combined_text[:100] + "..." if len(combined_text) > 100 else combined_text
                })
                confidence += 0.3
                methods.append(f"Machine type detected: {machine_type}")
                break
        
        return {
            "machines": machines,
            "customers": customers,
            "confidence": min(confidence, 1.0),
            "methods": methods
        }
    
    def analyze_transaction_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced batch analysis with relationship-based linking"""
        
        batch_analysis = {
            "total_transactions": len(transactions),
            "linked_transactions": 0,
            "cross_database_links": 0,
            "machine_links": 0,
            "customer_links": 0,
            "product_links": 0,
            "invoice_links": 0,
            "average_confidence": 0.0,
            "linking_summary": {},
            "high_confidence_links": [],
            "relationship_based_links": 0,
            "pattern_based_links": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        total_confidence = 0.0
        
        for i, transaction in enumerate(transactions):
            linked = self.link_transaction_to_operational_data(transaction)
            
            if linked["confidence_score"] > 0.5:
                batch_analysis["linked_transactions"] += 1
            
            if linked["cross_database_links"]:
                batch_analysis["cross_database_links"] += 1
            
            if linked["linked_machines"]:
                batch_analysis["machine_links"] += 1
            
            if linked["linked_customers"]:
                batch_analysis["customer_links"] += 1
            
            if linked["linked_products"]:
                batch_analysis["product_links"] += 1
            
            if "Direct invoice linking" in str(linked["linking_methods"]):
                batch_analysis["invoice_links"] += 1
                batch_analysis["relationship_based_links"] += 1
            elif "relationship" in str(linked["linking_methods"]).lower():
                batch_analysis["relationship_based_links"] += 1
            elif "pattern" in str(linked["linking_methods"]).lower():
                batch_analysis["pattern_based_links"] += 1
            
            total_confidence += linked["confidence_score"]
            
            # Store high-confidence links
            if linked["confidence_score"] > 0.8:
                batch_analysis["high_confidence_links"].append({
                    "transaction_index": i,
                    "confidence": linked["confidence_score"],
                    "linking_methods": linked["linking_methods"],
                    "linked_data": linked
                })
        
        if len(transactions) > 0:
            batch_analysis["average_confidence"] = total_confidence / len(transactions)
        
        # Generate enhanced summary
        batch_analysis["linking_summary"] = {
            "success_rate": f"{(batch_analysis['linked_transactions'] / len(transactions) * 100):.1f}%" if transactions else "0%",
            "cross_database_rate": f"{(batch_analysis['cross_database_links'] / len(transactions) * 100):.1f}%" if transactions else "0%",
            "invoice_linking_rate": f"{(batch_analysis['invoice_links'] / len(transactions) * 100):.1f}%" if transactions else "0%",
            "relationship_vs_pattern": f"{batch_analysis['relationship_based_links']} relationship / {batch_analysis['pattern_based_links']} pattern"
        }
        
        return batch_analysis