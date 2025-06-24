#!/usr/bin/env python3
"""
Direct Query Mapper - 100% Accurate Query Generation
Gebaseerd op de bewezen accurate mappings uit simple_working_test.py
"""

from typing import Optional, Dict, Any
import re

class DirectQueryMapper:
    """Directe query mapping voor perfecte accuracy op basis vragen"""
    
    def __init__(self):
        self.exact_mappings = {
            # SUPPLIER/LEVERANCIER PERFORMANCE QUERIES (HIGHEST PRIORITY)
            "leverancier_delivery_performance_dit_jaar": {
                "patterns": [
                    r"(wat\s+is\s+)?(de\s+)?delivery\s+performance\s+(van\s+)?(onze\s+)?leveranciers?",
                    r"delivery\s+performance\s+(van\s+)?(onze\s+)?leveranciers?\s+(dit\s+jaar|2025)?",
                    r"(wat\s+is\s+)?(de\s+)?leverancier\s+prestatie",
                    r"(hoe\s+presteren\s+|prestatie\s+van\s+)onze\s+leveranciers?",
                    r"delivery\s+(prestatie|performance)\s+leveranciers?",
                    r"leverancier\s+performance",
                    r"performance\s+(van\s+)?(onze\s+)?leveranciers?"
                ],
                "query": """SELECT 
                    r.NAME as Leverancier,
                    COUNT(po.ID) as TotaalOrders,
                    COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) as OpTijd,
                    COUNT(CASE WHEN po.DELIVERYDATE > po.REQUESTEDDELIVERYDATE THEN 1 END) as TeLaat,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageOpTijd,
                    AVG(DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE)) as GemiddeldeVertraging
                FROM V_R_PURCHASEORDER po
                INNER JOIN V_R_RELATION r ON po.FK_SUPPLIER = r.ID
                WHERE DATEPART(YEAR, po.ORDERDATE) = DATEPART(YEAR, GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY r.NAME, r.ID
                ORDER BY PercentageOpTijd DESC""",
                "expected_result": None,  # Multiple rows
                "description": "Delivery performance van leveranciers dit jaar met op-tijd percentage"
            },
            "top_leveranciers_performance": {
                "patterns": [
                    r"(beste|top)\s+leveranciers?\s+(delivery\s+)?performance",
                    r"(welke|wat\s+zijn\s+de)\s+(beste|top)\s+leveranciers?",
                    r"leveranciers?\s+met\s+(beste|hoogste)\s+performance",
                    r"top\s+\d+\s+leveranciers?\s+performance"
                ],
                "query": """SELECT TOP 10
                    r.NAME as Leverancier,
                    COUNT(po.ID) as TotaalOrders,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageOpTijd,
                    SUM(po.TOTALAMOUNT) as TotaalWaarde,
                    AVG(DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE)) as GemiddeldeVertraging
                FROM V_R_PURCHASEORDER po
                INNER JOIN V_R_RELATION r ON po.FK_SUPPLIER = r.ID
                WHERE DATEPART(YEAR, po.ORDERDATE) = DATEPART(YEAR, GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY r.NAME, r.ID
                HAVING COUNT(po.ID) >= 3
                ORDER BY PercentageOpTijd DESC, TotaalOrders DESC""",
                "expected_result": None,  # Multiple rows
                "description": "Top 10 beste leveranciers op basis van delivery performance"
            },
            "leverancier_vertraging_analyse": {
                "patterns": [
                    r"(welke\s+)?leveranciers?\s+(hebben\s+)?(de\s+meeste\s+)?vertraging",
                    r"vertraging\s+(van\s+|bij\s+)?leveranciers?",
                    r"(analyse\s+)?delivery\s+delays?\s+leveranciers?",
                    r"(welke\s+)?leveranciers?\s+leveren\s+te\s+laat"
                ],
                "query": """SELECT 
                    r.NAME as Leverancier,
                    COUNT(po.ID) as TotaalOrders,
                    COUNT(CASE WHEN po.DELIVERYDATE > po.REQUESTEDDELIVERYDATE THEN 1 END) as OrdersTeLaat,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE > po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageTeLaat,
                    AVG(CASE WHEN po.DELIVERYDATE > po.REQUESTEDDELIVERYDATE 
                        THEN DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE) 
                        ELSE 0 END) as GemiddeldeVertragingDagen,
                    MAX(DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE)) as MaximaleVertraging
                FROM V_R_PURCHASEORDER po
                INNER JOIN V_R_RELATION r ON po.FK_SUPPLIER = r.ID
                WHERE DATEPART(YEAR, po.ORDERDATE) = DATEPART(YEAR, GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY r.NAME, r.ID
                HAVING COUNT(po.ID) >= 2
                ORDER BY PercentageTeLaat DESC, GemiddeldeVertragingDagen DESC""",
                "expected_result": None,  # Multiple rows
                "description": "Leveranciers met meeste vertraging en delivery issues"
            },
            "leverancier_maandelijkse_performance": {
                "patterns": [
                    r"leverancier\s+performance\s+per\s+maand",
                    r"maandelijkse\s+(delivery\s+)?performance\s+leveranciers?",
                    r"(hoe\s+ontwikkelt\s+zich\s+|trend\s+in\s+)?leverancier\s+performance",
                    r"performance\s+trend\s+leveranciers?"
                ],
                "query": """SELECT 
                    DATEPART(MONTH, po.ORDERDATE) as Maand,
                    DATENAME(month, po.ORDERDATE) as MaandNaam,
                    COUNT(po.ID) as TotaalOrders,
                    COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) as OrdersOpTijd,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageOpTijd,
                    COUNT(DISTINCT po.FK_SUPPLIER) as AantalLeveranciers
                FROM V_R_PURCHASEORDER po
                WHERE DATEPART(YEAR, po.ORDERDATE) = DATEPART(YEAR, GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY DATEPART(MONTH, po.ORDERDATE), DATENAME(month, po.ORDERDATE)
                ORDER BY DATEPART(MONTH, po.ORDERDATE)""",
                "expected_result": None,  # Multiple rows
                "description": "Maandelijkse delivery performance trend van alle leveranciers"
            },

            # Monthly chart queries (SECOND PRIORITY - most specific first)
            "grafiek_omzet_afgelopen_maand": {
                "patterns": [
                    r"(maak\s+een\s+)?grafiek\s+(van\s+de\s+)?omzet\s+(van\s+)?afgelopen\s+maand",
                    r"grafiek\s+omzet\s+afgelopen\s+maand",
                    r"visualiseer\s+omzet\s+afgelopen\s+maand",
                    r"toon\s+grafiek\s+omzet\s+afgelopen\s+maand"
                ],
                "query": """SELECT 
                    DAY(INVOICEDATE) as Dag,
                    SUM(TOTALAMOUNT) as Omzet
                FROM V_R_SALESINVOICE si
                WHERE DATEPART(YEAR, si.INVOICEDATE) = DATEPART(YEAR, DATEADD(MONTH, -1, GETDATE()))
                  AND DATEPART(MONTH, si.INVOICEDATE) = DATEPART(MONTH, DATEADD(MONTH, -1, GETDATE()))
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY DAY(INVOICEDATE)
                ORDER BY DAY(INVOICEDATE)""",
                "expected_result": None,  # Multiple rows
                "description": "Dagelijkse omzet grafiek van afgelopen maand"
            },
            "grafiek_omzet_deze_maand": {
                "patterns": [
                    r"(maak\s+een\s+)?grafiek\s+(van\s+de\s+)?omzet\s+(van\s+)?deze\s+maand",
                    r"grafiek\s+omzet\s+deze\s+maand",
                    r"visualiseer\s+omzet\s+deze\s+maand"
                ],
                "query": """SELECT 
                    DAY(INVOICEDATE) as Dag,
                    SUM(TOTALAMOUNT) as Omzet
                FROM V_R_SALESINVOICE si
                WHERE DATEPART(YEAR, si.INVOICEDATE) = DATEPART(YEAR, GETDATE())
                  AND DATEPART(MONTH, si.INVOICEDATE) = DATEPART(MONTH, GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY DAY(INVOICEDATE)
                ORDER BY DAY(INVOICEDATE)""",
                "expected_result": None,  # Multiple rows
                "description": "Dagelijkse omzet grafiek van deze maand"
            },
            "grafiek_omzet_per_maand_jaar": {
                "patterns": [
                    r"(geef\s+me\s+een\s+|maak\s+een\s+)?grafiek\s+(van\s+de\s+)?omzet\s+per\s+maand\s+(van\s+)?(\d{4})",
                    r"omzet\s+per\s+maand\s+(van\s+)?(\d{4})",
                    r"maandelijkse\s+omzet\s+(\d{4})",
                    r"grafiek\s+omzet\s+(\d{4})\s+per\s+maand"
                ],
                "query": """SELECT 
                    DATEPART(MONTH, INVOICEDATE) as Maand,
                    SUM(TOTALAMOUNT) as Omzet
                FROM V_R_SALESINVOICE si
                WHERE DATEPART(YEAR, si.INVOICEDATE) = {year}
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY DATEPART(MONTH, INVOICEDATE)
                ORDER BY DATEPART(MONTH, INVOICEDATE)""",
                "expected_result": None,  # Multiple rows
                "description": "Maandelijkse omzet grafiek voor specifiek jaar"
            },
            # Revenue comparison queries (SECOND PRIORITY - yearly comparison)
            "omzet_vergelijking": {
                "patterns": [
                    r"zet\s+de\s+omzet\s+van\s+dit\s+jaar\s+tegenover\s+(dat\s+van\s+)?vorig\s+jaar",
                    r"omzet\s+(van\s+)?dit\s+jaar\s+(tegenover|vs|tegen)\s+vorig\s+jaar",
                    r"vergelijk\s+(de\s+)?omzet\s+(van\s+)?dit\s+jaar\s+(met|tegenover|versus)\s+vorig\s+jaar",
                    r"vergelijk\s+omzet\s+(dit|huidig)\s+jaar",
                    r"(maak\s+een\s+)?grafiek\s+(van\s+de\s+)?omzet\s+(dit|huidig|vorig)?\s*jaar"
                ],
                "query": """SELECT 
                    DATEPART(YEAR, INVOICEDATE) as Jaar,
                    SUM(TOTALAMOUNT) as Omzet
                FROM V_R_SALESINVOICE si
                WHERE DATEPART(YEAR, si.INVOICEDATE) IN (DATEPART(YEAR, GETDATE()), DATEPART(YEAR, GETDATE())-1)
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY DATEPART(YEAR, INVOICEDATE)
                ORDER BY DATEPART(YEAR, INVOICEDATE)""",
                "expected_result": None,  # Multiple rows
                "description": "Omzet vergelijking dit jaar vs vorig jaar (alleen externe verkopen)"
            },
            
            # Machine queries (ORDER MATTERS - most specific first)
            # Weekly production tracking queries (HIGHEST PRIORITY - most specific)
            "c6_machines_deze_week_gereed": {
                "patterns": [
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?deze\s+week\s+(al\s+)?(gereed\s+gemeld|gereed|klaar)",
                    r"c6\s+machines?\s+deze\s+week\s+(gereed|klaar)",
                    r"aantal\s+c6\s+machines?\s+deze\s+week\s+(gereed|klaar)"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.DATUMGEREED >= DATEADD(week, -1, GETDATE())
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will vary by week
                "description": "C6 machines die deze week gereed werden"
            },
            "machines_afgelopen_week_geproduceerd": {
                "patterns": [
                    r"hoeveel\s+(machines?\s+)?zijn\s+er\s+(dan\s+)?geproduceerd\s+afgelopen\s+week",
                    r"(machines?\s+)?geproduceerd\s+afgelopen\s+week",
                    r"productie\s+afgelopen\s+week",
                    r"hoeveel\s+(machines?\s+)?afgelopen\s+week\s+(geproduceerd|gereed|klaar)"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so 
                    WHERE so.PRODUCTIESTATUS IN (5,6)
                    AND so.DATUMGEREED >= DATEADD(week, -2, GETDATE())
                    AND so.DATUMGEREED < DATEADD(week, -1, GETDATE())
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will vary by week
                "description": "Machines die afgelopen week geproduceerd werden"
            },
            "machines_deze_week_gereed": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?deze\s+week\s+(al\s+)?(gereed\s+gemeld|gereed|klaar)",
                    r"machines?\s+deze\s+week\s+(gereed|klaar)",
                    r"productie\s+deze\s+week"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so 
                    WHERE so.PRODUCTIESTATUS IN (5,6)
                    AND so.DATUMGEREED >= DATEADD(week, -1, GETDATE())
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will vary by week
                "description": "Machines die deze week gereed werden"
            },
            "c6_machines_verkocht": {
                "patterns": [
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+)?(verkocht|gereed)",
                    r"c6\s+machines?\s+(verkocht|gereed)",
                    r"aantal\s+c6\s+machines?\s+(verkocht|gereed)"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": 1402,
                "description": "C6 machines verkocht/gereed"
            },
            "c6_machines_dit_jaar_gebouwd": {
                "patterns": [
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|gereed|geleverd)",
                    r"c6\s+machines?\s+dit\s+jaar\s+(gebouwd|geproduceerd)",
                    r"aantal\s+c6\s+machines?\s+dit\s+jaar",
                    r"hoeveel\s+c6.*dit\s+jaar.*gebouwd",
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+gereed\s+gemeld"
                ],
                "query": """SELECT COUNT(*) as C6_Geleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will vary by year
                "description": "C6 machines gereed gemeld dit jaar (using same table as total cranes)"
            },
            "c6_machines_totaal": {
                "patterns": [
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?(in\s+)?totaal(?!\s+(dit|vorig|deze))",
                    r"aantal\s+c6\s+machines?(?!\s+(dit|vorig|deze))",
                    r"c6\s+machines?\s+totaal(?!\s+(dit|vorig|deze))"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so
                    WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": 1403,
                "description": "C6 machines totaal"
            },
            "c30_machines_verkocht": {
                "patterns": [
                    r"hoeveel\s+c30\s+machines?\s+(zijn\s+)?(verkocht|gereed)",
                    r"c30\s+machines?\s+(verkocht|gereed)",
                    r"aantal\s+c30\s+machines?\s+(verkocht|gereed)"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so
                    WHERE so.FK_SERVICEOBJECTTYPE = 15
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will be determined from DB
                "description": "C30 machines verkocht/gereed"
            },
            "c30_machines_dit_jaar_gereed": {
                "patterns": [
                    r"hoeveel\s+c30\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|gereed|geleverd)",
                    r"hoeveel\s+c30\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+gereed\s+gemeld",
                    r"c30\s+machines?\s+dit\s+jaar\s+(gereed|gebouwd)",
                    r"aantal\s+c30\s+machines?\s+dit\s+jaar\s+gereed"
                ],
                "query": """SELECT COUNT(*) as C30_Geleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 15
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,
                "description": "C30 machines gereed gemeld dit jaar (using same table as total cranes)"
            },
            "c30_machines_totaal": {
                "patterns": [
                    r"hoeveel\s+c30\s+machines?(\s+(zijn\s+er|totaal))?",
                    r"aantal\s+c30\s+machines?",
                    r"c30\s+machines?\s+totaal"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so
                    WHERE so.FK_SERVICEOBJECTTYPE = 15
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will be determined from DB
                "description": "C30 machines totaal"
            },
            "c10_machines_dit_jaar_gereed": {
                "patterns": [
                    r"hoeveel\s+c10\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|gereed|geleverd)",
                    r"hoeveel\s+c10\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+gereed\s+gemeld",
                    r"c10\s+machines?\s+dit\s+jaar\s+(gereed|gebouwd)",
                    r"aantal\s+c10\s+machines?\s+dit\s+jaar\s+gereed"
                ],
                "query": """SELECT COUNT(*) as C10_Geleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 6
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,
                "description": "C10 machines gereed gemeld dit jaar (using same table as total cranes)"
            },
            "c1_machines_dit_jaar_gereed": {
                "patterns": [
                    r"hoeveel\s+c1\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|gereed|geleverd)",
                    r"hoeveel\s+c1\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+gereed\s+gemeld",
                    r"c1\s+machines?\s+dit\s+jaar\s+(gereed|gebouwd)",
                    r"aantal\s+c1\s+machines?\s+dit\s+jaar\s+gereed"
                ],
                "query": """SELECT COUNT(*) as C1_Geleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 12
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,
                "description": "C1 machines gereed gemeld dit jaar (using same table as total cranes)"
            },
            "mc1200_machines_dit_jaar_gereed": {
                "patterns": [
                    r"hoeveel\s+mc1200\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|gereed|geleverd)",
                    r"hoeveel\s+mc1200\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+gereed\s+gemeld",
                    r"mc1200\s+machines?\s+dit\s+jaar\s+(gereed|gebouwd)",
                    r"aantal\s+mc1200\s+machines?\s+dit\s+jaar\s+gereed"
                ],
                "query": """SELECT COUNT(*) as MC1200_Geleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 29
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,
                "description": "MC1200 machines gereed gemeld dit jaar (using same table as total cranes)"
            },
            "machines_verkocht": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+)?(verkocht|gereed)",
                    r"aantal\s+(verkochte\s+)?machines?",
                    r"machines?\s+(verkocht|gereed)",
                    r"verkochte\s+machines?"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so
                    WHERE so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": 9358,
                "description": "Alle machines verkocht/gereed"
            },
            "machines_geproduceerd_dit_jaar": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(hebben\s+we\s+)?dit\s+jaar\s+(geproduceerd|gebouwd|gereed|gemaakt)",
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?dit\s+jaar\s+(geproduceerd|gebouwd|gereed)",
                    r"machines?\s+(geproduceerd|gebouwd|gereed)\s+dit\s+jaar",
                    r"aantal\s+machines?\s+dit\s+jaar\s+(geproduceerd|gebouwd|gereed)",
                    r"productie\s+machines?\s+dit\s+jaar",
                    r"hoeveel\s+machines?\s+dit\s+jaar",  # ADDED: generic "dit jaar" query
                    r"machines?\s+dit\s+jaar"  # ADDED: simple form
                ],
                "query": """SELECT COUNT(*) as MachinesGereedDitJaar
                    FROM V_R_SERVICEOBJECT so
                    WHERE DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will vary by year, but expect within reasonable range  
                "description": "Machines werkelijk gereed gemeld dit jaar (correcte telling)",
                "validation_trigger": True  # Trigger accuracy validation for this query
            },
            "machines_productie": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+)?in\s+productie",
                    r"machines?\s+(in\s+)?productie",
                    r"aantal\s+machines?\s+productie"
                ],
                "query": """SELECT COUNT(*) FROM V_R_SERVICEOBJECT so
                    WHERE so.PRODUCTIESTATUS = 1
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": 19,
                "description": "Machines in productie"
            },
            "machines_totaal_dit_jaar": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?(dit\s+jaar\s+)?gebouwd",
                    r"machines?\s+(van\s+)?dit\s+jaar",
                    r"hoeveel\s+machines?\s+(hebben\s+we\s+)?dit\s+jaar"
                ],
                "query": """SELECT COUNT(*) as TotaalMachinesDitJaar
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE IN (10, 15, 6, 12, 29, 13)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())""",
                "expected_result": 164,
                "description": "Machines gebouwd dit jaar"
            },
            "machines_totaal_alle_jaren": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?ooit\s+gebouwd",
                    r"totaal\s+(aantal\s+)?machines?\s+(alle\s+jaren|ooit)",
                    r"machines?\s+in\s+totaal\s+(alle\s+jaren)?",
                    r"hoeveel\s+machines?\s+hebben\s+we\s+in\s+de\s+geschiedenis"
                ],
                "query": """SELECT COUNT(*) as TotaalMachinesAlleJaren
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE IN (10, 15, 6, 12, 29, 13)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": 9590,
                "description": "Alle machines alle jaren (complete geschiedenis)"
            },
            # CLARIFICATION TRIGGER for ambiguous "machines totaal"
            "machines_totaal_clarification": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?(in\s+)?totaal(?!\s+(dit|vorig|deze|alle|ooit))",
                    r"totaal\s+(aantal\s+)?machines?(?!\s+(dit|vorig|deze|alle|ooit))",
                    r"aantal\s+machines?(\s+totaal)?(?!\s+(dit|vorig|deze|alle|ooit))",
                    r"hoeveel\s+machines?\s+hebben\s+we(?!\s+(dit|vorig|deze|alle|ooit))"
                ],
                "requires_clarification": True,
                "clarification_options": [
                    "Machines gebouwd dit jaar (2025)",
                    "Alle machines ooit gebouwd (complete geschiedenis)", 
                    "Machines in productie nu",
                    "Machines per type specificeren"
                ],
                "description": "Ambigue machines totaal vraag - clarification nodig"
            },
            # Revenue queries
            "omzet_dit_jaar": {
                "patterns": [
                    r"(wat\s+is\s+de\s+)?omzet\s+(van\s+)?dit\s+jaar",
                    r"omzet\s+(\d{4}|\w+\s+jaar)",
                    r"revenue\s+(this\s+)?year"
                ],
                "query": """SELECT SUM(si.TOTALAMOUNT) as External_Omzet 
                    FROM V_R_SALESINVOICE si 
                    WHERE DATEPART(YEAR, si.INVOICEDATE) = DATEPART(YEAR, GETDATE())
                      AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                      AND si.TOTALAMOUNT > 0""",
                "expected_result": None,  # Will vary by year - let AI determine correct criteria
                "description": "Omzet van dit jaar"
            },
            # Profit queries disabled - COST column not available in R_SALESINVOICE
            # "winst_afgelopen_maand": {
            #     "patterns": [
            #         r"(winst|profit)\s+(van\s+)?(afgelopen|laatste)\s+maand",
            #         r"hoeveel\s+winst.*afgelopen\s+maand",
            #         r"winst\s+vorige\s+maand"
            #     ],
            #     "query": """SELECT SUM(si.TOTALAMOUNT - ISNULL(si.COST, 0)) as External_Winst 
            #         FROM V_R_SALESINVOICE si 
            #         WHERE YEAR(si.INVOICEDATE) = YEAR(DATEADD(MONTH, -1, GETDATE())) 
            #           AND MONTH(si.INVOICEDATE) = MONTH(DATEADD(MONTH, -1, GETDATE()))
            #           AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
            #           AND si.TOTALAMOUNT > 0""",
            #     "expected_result": "single_value",
            #     "description": "Winst van afgelopen maand"
            # },
            "omzet_afgelopen_maand": {
                "patterns": [
                    r"(omzet|revenue)\s+(van\s+)?(afgelopen|laatste)\s+maand",
                    r"hoeveel\s+omzet.*afgelopen\s+maand",
                    r"omzet\s+vorige\s+maand"
                ],
                "query": """SELECT SUM(si.TOTALAMOUNT) as External_Omzet 
                    FROM V_R_SALESINVOICE si 
                    WHERE DATEPART(YEAR, si.INVOICEDATE) = DATEPART(YEAR, DATEADD(MONTH, -1, GETDATE())) 
                      AND DATEPART(MONTH, si.INVOICEDATE) = DATEPART(MONTH, DATEADD(MONTH, -1, GETDATE()))
                      AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                      AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Omzet van afgelopen maand"
            },
            "omzet_deze_maand": {
                "patterns": [
                    r"(omzet|revenue)\s+(van\s+)?deze\s+maand",
                    r"hoeveel\s+omzet.*deze\s+maand",
                    r"omzet\s+deze\s+maand",
                    r"en\s+van\s+deze\s+maand",
                    r"wat\s+is\s+de\s+omzet.*deze\s+maand"
                ],
                "query": """SELECT SUM(si.TOTALAMOUNT) as External_Omzet 
                    FROM V_R_SALESINVOICE si 
                    WHERE DATEPART(YEAR, si.INVOICEDATE) = DATEPART(YEAR, GETDATE()) 
                      AND DATEPART(MONTH, si.INVOICEDATE) = DATEPART(MONTH, GETDATE())
                      AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                      AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Omzet van deze maand"
            },
            "c6_machines_deze_week_gereed": {
                "patterns": [
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?deze\s+week\s+(al\s+)?(gereed\s+gemeld|gereed|klaar)",
                    r"c6\s+machines?\s+deze\s+week\s+(gereed|klaar)",
                    r"c6.*deze\s+week.*gereed"
                ],
                "query": """SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON s 
                    JOIN V_R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM 
                    WHERE i.DESCRIPTION LIKE '%C6%' 
                    AND s.STATE = 2 
                    AND s.DATECHANGED >= DATEADD(week, -1, GETDATE())""",
                "expected_result": "single_value",
                "description": "C6 machines gereed deze week"
            },
            "machines_geproduceerd_afgelopen_week": {
                "patterns": [
                    r"hoeveel\s+(zijn\s+er\s+dan\s+)?geproduceerd\s+afgelopen\s+week",
                    r"productie\s+afgelopen\s+week",
                    r"machines?\s+afgelopen\s+week\s+(geproduceerd|gereed|klaar)"
                ],
                "query": """SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON 
                    WHERE STATE = 2 
                    AND DATECHANGED >= DATEADD(week, -2, GETDATE())
                    AND DATECHANGED < DATEADD(week, -1, GETDATE())""",
                "expected_result": "single_value", 
                "description": "Machines geproduceerd afgelopen week"
            },
            "machines_deze_week_gereed": {
                "patterns": [
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?deze\s+week\s+(gereed|klaar)",
                    r"machines?\s+deze\s+week\s+(gereed|klaar)",
                    r"productie\s+deze\s+week"
                ],
                "query": """SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON 
                    WHERE STATE = 2 
                    AND DATECHANGED >= DATEADD(week, -1, GETDATE())""",
                "expected_result": "single_value",
                "description": "Machines gereed deze week"
            },
            "kranen_geproduceerd_dit_jaar": {
                "patterns": [
                    r"hoeveel\s+kranen?\s+(zijn\s+er\s+)?dit\s+jaar\s+(geproduceerd|geleverd|gereed|gebouwd)",
                    r"hoeveel\s+kranen?\s+(zijn\s+er\s+)?(al\s+)?gereed\s+dit\s+jaar",
                    r"kranen?\s+dit\s+jaar\s+(geproduceerd|geleverd|gereed|gebouwd)",
                    r"kranen?\s+gereed\s+dit\s+jaar",
                    r"aantal\s+kranen?\s+dit\s+jaar",
                    r"kranen?\s+productie\s+dit\s+jaar(?!.*vs|.*vorig|.*tegen|.*per\s+maand|.*vergelijk)",
                    r"hoeveel\s+c\d+\s+kranen?\s+(zijn\s+er\s+)?dit\s+jaar\s+(geproduceerd|gebouwd|gereed)"
                ],
                "query": """SELECT COUNT(*) as KranenGeleverd
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE IN (6,10,12,15,29)
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": None,  # Will validate against actual data - expect around 155 based on dashboard
                "description": "Kranen geproduceerd/geleverd dit jaar",
                "validation_trigger": True  # Trigger validation for this specific query
            },
            "kranen_geproduceerd_deze_maand": {
                "patterns": [
                    r"hoeveel\s+kranen?\s+(zijn\s+er\s+)?deze\s+maand\s+(geproduceerd|geleverd|gereed)",
                    r"kranen?\s+deze\s+maand\s+(geproduceerd|geleverd)",
                    r"aantal\s+kranen?\s+deze\s+maand",
                    r"kranen?\s+geproduceerd\s+deze\s+maand"
                ],
                "query": """SELECT COUNT(*) as KranenDezeMaand
                    FROM V_R_SERVICEOBJECT so
                    WHERE so.FK_SERVICEOBJECTTYPE IN (6,10,12,15,29)
                    AND DATEPART(YEAR, so.DATUMGEREED) = DATEPART(YEAR, GETDATE())
                    AND DATEPART(MONTH, so.DATUMGEREED) = DATEPART(MONTH, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                "expected_result": "single_value",
                "description": "Kranen geproduceerd deze maand"
            },
            "executive_dashboard": {
                "patterns": [
                    r"(maak|creeer|toon|geef)\s+(een\s+)?(executive\s+)?dashboard",
                    r"management\s+dashboard",
                    r"hoeflon\s+dashboard",
                    r"executive\s+overzicht",
                    r"bedrijfs\s+dashboard",
                    r"kpi\s+dashboard"
                ],
                "query": "EXECUTIVE_DASHBOARD_MULTI_QUERY",
                "expected_result": "dashboard",
                "description": "Executive Dashboard met KPIs en grafieken"
            },
            "production_dashboard": {
                "patterns": [
                    r"(maak|creeer|toon|geef)\s+(een\s+)?productie\s+dashboard",
                    r"(geef\s+me\s+een\s+)?productie\s+dashboard",
                    r"production\s+dashboard",
                    r"fabriek\s+dashboard",
                    r"productie\s+overzicht",
                    r"manufacturing\s+dashboard",
                    r"operationele\s+dashboard",
                    r"(toon|laat\s+zien)\s+(de\s+)?productie\s+(status|dashboard)"
                ],
                "query": "PRODUCTION_DASHBOARD_MULTI_QUERY", 
                "expected_result": "dashboard",
                "description": "Production Dashboard met real-time productie status"
            },
            "financial_dashboard": {
                "patterns": [
                    r"(maak|creeer|toon|geef)\s+(een\s+)?financieel\s+dashboard",
                    r"financial\s+dashboard", 
                    r"omzet\s+dashboard",
                    r"financiele\s+prestaties",
                    r"revenue\s+dashboard",
                    r"kasstroomdashboard"
                ],
                "query": "FINANCIAL_DASHBOARD_MULTI_QUERY",
                "expected_result": "dashboard", 
                "description": "Financial Dashboard met uitgebreide financiële analyse"
            },
            "kranen_vergelijking_per_maand": {
                "patterns": [
                    r"vergelijk\s+kranen?\s+productie\s+dit\s+jaar\s+vs\s+vorig\s+jaar\s+per\s+maand",
                    r"hoeveel\s+kranen?\s+(zijn\s+er\s+)?dit\s+jaar\s+(gebouwd|geproduceerd|geleverd)\s+(tegen\s?over|vs|tegenover)\s+vorig\s+jaar.*per\s+maand",
                    r"kranen?\s+dit\s+jaar\s+(tegen\s?over|vs)\s+vorig\s+jaar.*per\s+maand",
                    r"vergelijk\s+kranen?\s+(productie|aantal)\s+dit\s+jaar.*vorig\s+jaar.*maand",
                    r"kranen?\s+(gebouwd|geproduceerd).*dit\s+jaar.*vorig\s+jaar.*per\s+maand",
                    r"hoeveel\s+kranen?.*jaar.*tegenover.*jaar.*per\s+maand"
                ],
                "query": """SELECT 
                    DATEPART(YEAR, so.DATUMGEREED) as Jaar,
                    DATEPART(MONTH, so.DATUMGEREED) as Maand,
                    COUNT(*) as AantalKranen
                FROM V_R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE IN (10,6,15,12,29)
                    AND DATEPART(YEAR, so.DATUMGEREED) IN (DATEPART(YEAR, GETDATE()), DATEPART(YEAR, GETDATE())-1)
                    AND DATEPART(MONTH, so.DATUMGEREED) <= DATEPART(MONTH, GETDATE())
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                GROUP BY DATEPART(YEAR, so.DATUMGEREED), DATEPART(MONTH, so.DATUMGEREED)
                ORDER BY Jaar, Maand""",
                "expected_result": None,  # Multiple rows
                "description": "Kranen productie vergelijking dit jaar vs vorig jaar per maand"
            },
            # Revenue per machine queries
            "c6_gemiddelde_omzet_per_kraan": {
                "patterns": [
                    r"wat\s+leverd?t?\s+(gemiddeld\s+)?een\s+c6\s+(verkochte\s+)?kraan\s+op",
                    r"gemiddelde\s+(omzet|revenue)\s+(per\s+)?c6\s+(kraan|machine)",
                    r"hoeveel\s+(omzet|geld)\s+(leverd?t?\s+)?een\s+c6\s+(kraan|machine)\s+(gemiddeld\s+)?op",
                    r"c6\s+(kraan|machine)\s+(gemiddelde\s+)?(omzet|revenue)",
                    r"wat\s+(kost|leverd?t?\s+op)\s+een\s+c6\s+(kraan|machine)\s+gemiddeld",
                    r"wat\s+leverd?t?\s+een\s+c6\s+(kraan|machine)\s+gemiddeld\s+op"
                ],
                "query": """SELECT 
                    AVG(si.TOTALAMOUNT) as GemiddeldeOmzetPerC6Kraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE i.DESCRIPTION LIKE '%C6%'
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Gemiddelde omzet per verkochte C6 kraan"
            },
            "gemiddelde_omzet_per_kraan": {
                "patterns": [
                    r"wat\s+leverd?t?\s+(gemiddeld\s+)?een\s+(verkochte\s+)?kraan\s+op",
                    r"gemiddelde\s+(omzet|revenue)\s+(per\s+)?kraan",
                    r"hoeveel\s+(omzet|geld)\s+(leverd?t?\s+)?een\s+kraan\s+(gemiddeld\s+)?op",
                    r"wat\s+leverd?t?\s+een\s+kraan\s+gemiddeld\s+op"
                ],
                "query": """SELECT 
                    AVG(si.TOTALAMOUNT) as GemiddeldeOmzetPerKraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE (i.DESCRIPTION LIKE '%C%' OR i.DESCRIPTION LIKE '%kraan%' OR i.DESCRIPTION LIKE '%machine%')
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value", 
                "description": "Gemiddelde omzet per verkochte kraan"
            },
            
            # C30 PRICING QUERIES (NEW)
            "c30_gemiddelde_omzet_per_kraan": {
                "patterns": [
                    r"wat\s+(kost|leverd?t?\s+op)\s+een\s+c30\s+(kraan|machine)\s+gemiddeld",
                    r"wat\s+is\s+de\s+(prijs|kosten)\s+van\s+een\s+c30",
                    r"hoeveel\s+kost\s+een\s+c30\s+(kraan|machine)",
                    r"c30\s+(kraan|machine)\s+(prijs|kosten|prijzen)",
                    r"gemiddelde\s+(omzet|prijs)\s+(per\s+)?c30\s+(kraan|machine)",
                    r"hoeveel\s+(omzet|geld)\s+(leverd?t?\s+)?een\s+c30\s+(kraan|machine)\s+(gemiddeld\s+)?op"
                ],
                "query": """SELECT 
                    AVG(si.TOTALAMOUNT) as GemiddeldeOmzetPerC30Kraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE i.DESCRIPTION LIKE '%C30%'
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Gemiddelde omzet per verkochte C30 kraan"
            },
            
            # SUPERLATIVE QUERIES (NEW)
            "c6_duurste_kraan": {
                "patterns": [
                    r"wat\s+is\s+de\s+(duurste|hoogste\s+prijs)\s+c6\s+(kraan|machine)",
                    r"(welke\s+)?c6\s+(kraan|machine)\s+kost\s+het\s+(meest|meeste)",
                    r"hoogste\s+(prijs|omzet)\s+(van\s+)?een\s+c6\s+(kraan|machine)",
                    r"duurste\s+c6\s+(kraan|machine)",
                    r"maximale\s+(prijs|omzet)\s+c6"
                ],
                "query": """SELECT 
                    MAX(si.TOTALAMOUNT) as DuursteC6Kraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE i.DESCRIPTION LIKE '%C6%'
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Duurste verkochte C6 kraan"
            },
            "c30_duurste_kraan": {
                "patterns": [
                    r"wat\s+is\s+de\s+(duurste|hoogste\s+prijs)\s+c30\s+(kraan|machine)",
                    r"(welke\s+)?c30\s+(kraan|machine)\s+kost\s+het\s+(meest|meeste)",
                    r"hoogste\s+(prijs|omzet)\s+(van\s+)?een\s+c30\s+(kraan|machine)",
                    r"duurste\s+c30\s+(kraan|machine)",
                    r"maximale\s+(prijs|omzet)\s+c30"
                ],
                "query": """SELECT 
                    MAX(si.TOTALAMOUNT) as DuursteC30Kraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE i.DESCRIPTION LIKE '%C30%'
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Duurste verkochte C30 kraan"
            },
            "goedkoopste_c6_kraan": {
                "patterns": [
                    r"wat\s+is\s+de\s+(goedkoopste|laagste\s+prijs)\s+c6\s+(kraan|machine)",
                    r"(welke\s+)?c6\s+(kraan|machine)\s+kost\s+het\s+(minst|minste)",
                    r"laagste\s+(prijs|omzet)\s+(van\s+)?een\s+c6\s+(kraan|machine)",
                    r"goedkoopste\s+c6\s+(kraan|machine)",
                    r"minimale\s+(prijs|omzet)\s+c6"
                ],
                "query": """SELECT 
                    MIN(si.TOTALAMOUNT) as GoedkoopdsteC6Kraan
                FROM V_R_SALESINVOICE si
                JOIN V_R_SALESINVOICEDETAILITEM sil ON si.PK_R_SALESINVOICE = sil.FK_SALESINVOICE
                JOIN V_R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                WHERE i.DESCRIPTION LIKE '%C6%'
                    AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND si.TOTALAMOUNT > 0""",
                "expected_result": "single_value",
                "description": "Goedkoopste verkochte C6 kraan"
            },
            
            # PRODUCTION TIME QUERIES (NEW)
            "c6_productie_tijd": {
                "patterns": [
                    r"wat\s+is\s+de\s+gemiddelde\s+productie\s+tijd\s+van\s+een\s+c6\s+(kraan|machine)",
                    r"hoe\s+lang\s+duurt\s+het\s+om\s+een\s+c6\s+te\s+(maken|bouwen|produceren)",
                    r"productietijd\s+c6\s+(kraan|machine)",
                    r"gemiddelde\s+doorlooptijd\s+c6",
                    r"hoelang\s+duurt\s+c6\s+productie",
                    r"productie\s+tijd\s+c6"
                ],
                "query": """SELECT 
                    AVG(DATEDIFF(day, so.STARTDATUM, so.DATUMGEREED)) as GemiddeldeProductietijdC6
                FROM V_R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND so.STARTDATUM IS NOT NULL
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND DATEPART(YEAR, so.DATUMGEREED) >= DATEPART(YEAR, GETDATE())-2""",
                "expected_result": "single_value",
                "description": "Gemiddelde productietijd C6 kraan in dagen"
            },
            "c30_productie_tijd": {
                "patterns": [
                    r"wat\s+is\s+de\s+gemiddelde\s+productie\s+tijd\s+van\s+een\s+c30\s+(kraan|machine)",
                    r"hoe\s+lang\s+duurt\s+het\s+om\s+een\s+c30\s+te\s+(maken|bouwen|produceren)",
                    r"productietijd\s+c30\s+(kraan|machine)",
                    r"gemiddelde\s+doorlooptijd\s+c30",
                    r"hoelang\s+duurt\s+c30\s+productie",
                    r"productie\s+tijd\s+c30"
                ],
                "query": """SELECT 
                    AVG(DATEDIFF(day, so.STARTDATUM, so.DATUMGEREED)) as GemiddeldeProductietijdC30
                FROM V_R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE = 15
                    AND so.STARTDATUM IS NOT NULL
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND DATEPART(YEAR, so.DATUMGEREED) >= DATEPART(YEAR, GETDATE())-2""",
                "expected_result": "single_value",
                "description": "Gemiddelde productietijd C30 kraan in dagen"
            },
            "productie_tijd_algemeen": {
                "patterns": [
                    r"wat\s+is\s+de\s+gemiddelde\s+productie\s+tijd\s+van\s+een\s+(kraan|machine)",
                    r"hoe\s+lang\s+duurt\s+het\s+om\s+een\s+(kraan|machine)\s+te\s+(maken|bouwen|produceren)",
                    r"gemiddelde\s+productietijd\s+(kraan|machine)",
                    r"doorlooptijd\s+productie"
                ],
                "query": """SELECT 
                    AVG(DATEDIFF(day, so.STARTDATUM, so.DATUMGEREED)) as GemiddeldeProductietijd
                FROM V_R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE IN (6,10,12,15,29)
                    AND so.STARTDATUM IS NOT NULL
                    AND so.DATUMGEREED IS NOT NULL
                    AND so.PRODUCTIESTATUS IN (5,6)
                    AND DATEPART(YEAR, so.DATUMGEREED) >= DATEPART(YEAR, GETDATE())-2""",
                "expected_result": "single_value",
                "description": "Gemiddelde productietijd alle machines in dagen"
            }
        }
        
        # Compile regex patterns for performance
        self.compiled_patterns = {}
        for mapping_name, mapping_data in self.exact_mappings.items():
            self.compiled_patterns[mapping_name] = [
                re.compile(pattern, re.IGNORECASE) for pattern in mapping_data["patterns"]
            ]
    
    def map_question_to_query(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Map een vraag naar een exacte SQL query
        Returns: {query: str, expected_result: int/None, description: str, mapping_name: str}
        """
        question_clean = question.strip().lower()
        
        # Check each mapping in order (most specific first)
        for mapping_name, mapping_data in self.exact_mappings.items():
            patterns = self.compiled_patterns[mapping_name]
            
            # Check if any pattern matches
            for pattern in patterns:
                match = pattern.search(question_clean)
                if match:
                    # Check if this mapping requires clarification
                    if mapping_data.get("requires_clarification", False):
                        return {
                            "requires_clarification": True,
                            "clarification_options": mapping_data["clarification_options"],
                            "description": mapping_data["description"],
                            "mapping_name": mapping_name
                        }
                    
                    query = mapping_data["query"]
                    
                    # Special handling for year-based queries
                    if mapping_name == "grafiek_omzet_per_maand_jaar":
                        # Extract year from the pattern match
                        year = None
                        for group in match.groups():
                            if group and group.isdigit() and len(group) == 4:
                                year = group
                                break
                        
                        if year:
                            query = query.format(year=year)
                        else:
                            # Fallback to current year if no year found
                            from datetime import datetime
                            query = query.format(year=datetime.now().year)
                    
                    return {
                        "query": query,
                        "expected_result": mapping_data["expected_result"],
                        "description": mapping_data["description"],
                        "mapping_name": mapping_name,
                        "confidence": 1.0  # 100% confidence for exact matches
                    }
        
        return None
    
    def get_all_supported_questions(self) -> Dict[str, str]:
        """Retourneert alle ondersteunde vragen met hun beschrijvingen"""
        result = {}
        for mapping_name, mapping_data in self.exact_mappings.items():
            # Use first pattern as example
            example_pattern = mapping_data["patterns"][0]
            # Convert regex to readable example
            example = example_pattern.replace(r"\s+", " ").replace(r"(\s+)?", " ").replace(r"?", "")
            result[example] = mapping_data["description"]
        return result
    
    def validate_mapping_accuracy(self, execute_query_func) -> Dict[str, Any]:
        """
        Valideer de accuracy van alle mappings tegen de database
        execute_query_func: function that takes SQL query and returns result
        """
        results = {
            "total_mappings": len(self.exact_mappings),
            "tested_mappings": 0,
            "accurate_mappings": 0,
            "failed_mappings": [],
            "accuracy_percentage": 0.0
        }
        
        for mapping_name, mapping_data in self.exact_mappings.items():
            expected = mapping_data["expected_result"]
            if expected is None:
                continue  # Skip mappings without expected results
            
            try:
                query_result = execute_query_func(mapping_data["query"])
                actual = query_result[0][list(query_result[0].keys())[0]] if query_result else None
                
                results["tested_mappings"] += 1
                
                if actual == expected:
                    results["accurate_mappings"] += 1
                else:
                    results["failed_mappings"].append({
                        "mapping": mapping_name,
                        "expected": expected,
                        "actual": actual,
                        "query": mapping_data["query"]
                    })
            
            except Exception as e:
                results["failed_mappings"].append({
                    "mapping": mapping_name,
                    "expected": expected,
                    "actual": f"ERROR: {str(e)}",
                    "query": mapping_data["query"]
                })
        
        if results["tested_mappings"] > 0:
            results["accuracy_percentage"] = (results["accurate_mappings"] / results["tested_mappings"]) * 100
        
        return results