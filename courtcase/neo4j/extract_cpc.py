"""
Extract structured data from CPC case briefs PDF for knowledge graph construction
"""
import json
import re
from pathlib import Path

# Manually extracted data from cpc2.pdf
# This represents the 5 case briefs from the document

CPC_DATA = {
    "cases": [
        {
            "id": "case_1",
            "name": "Siddique Mia vs Md Idris Miah and others",
            "citation": "60 DLR 20",
            "year": 2007,
            "date": "2007-01-28",
            "topic": "Revision",
            "court": "High Court Division",
            "jurisdiction": "Civil Revisional Jurisdiction",
            "judges": ["Siddiqur Rahman Miah, J.", "Md Rezaul Haque, J."],
            "petitioner": ["Siddique Mia"],
            "respondent": ["Md Idris Miah and others"],
            "sections": ["Section 10", "Section 115(4)", "Order VI, rule 17"],
            "principles": ["Res judicata between stages", "Principle of finality"],
            "abstract": "Addresses the principle of finality in interlocutory matters and the limits of judicial discretion in allowing amendments to pleadings.",
            "issue": "Whether a party can file a second application for amendment with the same content after the first application was rejected",
            "holding": "Rule made absolute. Matter decided at one stage cannot be re-agitated at subsequent stage.",
            "significance": "Reinforces res judicata between stages principle"
        },
        {
            "id": "case_2",
            "name": "Syed Mayeenul Huq vs MA Razzaque and others",
            "citation": "60 DLR 704",
            "year": 2008,
            "date": "2008-02-25",
            "topic": "Revision",
            "court": "High Court Division",
            "jurisdiction": "Civil Revisional Jurisdiction",
            "judges": ["MA Wahhab Miah, J.", "Afzal Hossain Ahmed, J."],
            "petitioner": ["Syed Mayeenul Huq"],
            "respondent": ["MA Razzaque and others"],
            "sections": ["Section 115(2)", "Sections 8 and 11 (Suits Valuation Act)"],
            "principles": ["Stare decisis", "Pecuniary jurisdiction limits"],
            "abstract": "Clarifies the scope of a District Judge's pecuniary jurisdiction to hear revisions under Section 115(2) of the CPC.",
            "issue": "Whether a District Judge has unlimited pecuniary jurisdiction to entertain a revision application under Section 115(2)",
            "holding": "District Judge's revisional jurisdiction is co-extensive with appellate pecuniary jurisdiction",
            "significance": "Affirms stare decisis and clarifies jurisdiction limits"
        },
        {
            "id": "case_3",
            "name": "East West Property Development Private Limited and others vs Md Akrab Ali",
            "citation": "74 DLR 101",
            "year": 2021,
            "date": "2021-10-21",
            "topic": "Inherent Power",
            "court": "High Court Division",
            "jurisdiction": "Civil Revisional Jurisdiction",
            "judges": ["Sheikh Abdul Awal, J."],
            "petitioner": ["East West Property Development Private Limited and others"],
            "respondent": ["Md Akrab Ali"],
            "sections": ["Section 151", "Order VI, rule 18", "Section 115(4)"],
            "principles": ["Inherent power of court", "Ends of justice"],
            "abstract": "Addresses the court's discretion to use its inherent power under Section 151 to condone delays in procedural matters.",
            "issue": "Whether a trial court can exercise inherent power under Section 151 to extend time for amending a plaint",
            "holding": "Court may use inherent power to allow amendment beyond prescribed time limit to serve ends of justice",
            "significance": "Clarifies that procedural rules can be relaxed by inherent power"
        },
        {
            "id": "case_4",
            "name": "Yeamin Nobi (Md) and others vs Moklesur Rahman and others",
            "citation": "67 DLR 281",
            "year": 2015,
            "date": "2015-12-11",
            "topic": "Appeal",
            "court": "High Court Division",
            "jurisdiction": "Civil Appellate Jurisdiction",
            "judges": ["Sheikh Abdul Awal, J."],
            "petitioner": ["Yeamin Nobi (Md) and others"],
            "respondent": ["Moklesur Rahman and others"],
            "sections": ["Section 4 (Partition Act)", "Section 107", "Order XLI, rule 23"],
            "principles": ["Pre-emption rights", "No limitation for Section 4 applications", "Clean hands doctrine"],
            "abstract": "Addresses legal principles surrounding pre-emption under Section 4 of the Partition Act, particularly the issue of limitation.",
            "issue": "Whether a pre-emption case under Section 4 of the Partition Act is subject to a limitation period",
            "holding": "No time limit for filing pre-emption application, but pre-emptor must have clean hands",
            "significance": "Reaffirms no limitation period for Partition Act Section 4"
        },
        {
            "id": "case_5",
            "name": "SMA Razzaque vs Artha Rin Adalat",
            "citation": "72 DLR 803",
            "year": 2020,
            "date": "2020",
            "topic": "Appeal",
            "court": "High Court Division",
            "jurisdiction": "Special Original Jurisdiction",
            "judges": ["Not specified"],
            "petitioner": ["SMA Razzaque"],
            "respondent": ["Artha Rin Adalat"],
            "sections": ["Section 2(2)"],
            "principles": ["Doctrine of merger", "Functus officio"],
            "abstract": "Reinforces the fundamental legal principle regarding the finality of appellate court decisions, known as the doctrine of merger.",
            "issue": "Whether a lower court has jurisdiction to interfere with a decree after modification by appellate court",
            "holding": "Once decree modified by appellate court, lower court loses all jurisdiction. Subsequent action is void.",
            "significance": "Upholds hierarchical structure and finality of appellate decisions"
        }
    ],
    "courts": [
        {
            "id": "high_court",
            "name": "High Court Division",
            "type": "Appellate Court"
        },
        {
            "id": "district_judge",
            "name": "District Judge",
            "type": "Revisional Court"
        },
        {
            "id": "trial_court",
            "name": "Trial Court",
            "type": "Original Jurisdiction"
        }
    ],
    "sections": [
        {
            "id": "sec_10",
            "section_id": "Section 10",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Stay of suit",
            "description": "Aimed at preventing multiplicity of proceedings"
        },
        {
            "id": "sec_115_2",
            "section_id": "Section 115(2)",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Revisional jurisdiction of District Judge",
            "description": "Confers revisional jurisdiction upon the District Judge"
        },
        {
            "id": "sec_115_4",
            "section_id": "Section 115(4)",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Revisional jurisdiction of High Court Division",
            "description": "Jurisdiction for a second revision before the High Court Division"
        },
        {
            "id": "sec_151",
            "section_id": "Section 151",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Inherent power of court",
            "description": "Power to make orders necessary for the ends of justice or to prevent abuse of process"
        },
        {
            "id": "order_6_17",
            "section_id": "Order VI, rule 17",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Amendment of pleadings",
            "description": "Rules for amending pleadings"
        },
        {
            "id": "order_6_18",
            "section_id": "Order VI, rule 18",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Time limit for amendment",
            "description": "Amendment must be done within 14 days if no time specified"
        },
        {
            "id": "sec_2_2",
            "section_id": "Section 2(2)",
            "statute": "Code of Civil Procedure, 1908",
            "title": "Definition of Decree",
            "description": "Defines what constitutes a decree"
        },
        {
            "id": "partition_sec_4",
            "section_id": "Section 4",
            "statute": "Partition Act, 1893",
            "title": "Pre-emption rights",
            "description": "Gives co-sharer in undivided dwelling house right to buy share sold to stranger"
        }
    ],
    "principles": [
        {
            "id": "res_judicata",
            "name": "Res judicata between stages",
            "description": "A matter decided at one stage of litigation cannot be re-agitated at a subsequent stage in the same suit",
            "category": "Procedural Law"
        },
        {
            "id": "stare_decisis",
            "name": "Stare decisis",
            "description": "Judicial precedent - lower benches are bound by rulings of larger benches",
            "category": "Judicial Principle"
        },
        {
            "id": "doctrine_merger",
            "name": "Doctrine of merger",
            "description": "Upon appeal, the decision of lower court merges with decision of appellate court, making latter the only operative decision",
            "category": "Appellate Law"
        },
        {
            "id": "inherent_power",
            "name": "Inherent power",
            "description": "Court's inherent jurisdiction to make orders necessary for ends of justice",
            "category": "Judicial Power"
        },
        {
            "id": "clean_hands",
            "name": "Clean hands doctrine",
            "description": "Party seeking equitable relief must have acted fairly and honestly",
            "category": "Equity"
        },
        {
            "id": "functus_officio",
            "name": "Functus officio",
            "description": "Once function is discharged, court loses authority to alter the matter",
            "category": "Judicial Principle"
        }
    ],
    "statutes": [
        {
            "id": "cpc_1908",
            "name": "Code of Civil Procedure, 1908",
            "short_name": "CPC",
            "country": "Bangladesh"
        },
        {
            "id": "partition_act_1893",
            "name": "Partition Act, 1893",
            "country": "Bangladesh"
        },
        {
            "id": "suits_valuation_act",
            "name": "Suits Valuation Act, 1887",
            "country": "Bangladesh"
        }
    ]
}


def extract_and_save():
    """Extract data and save to JSON file"""
    output_path = Path(__file__).parent / "cpc_data.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(CPC_DATA, f, indent=2, ensure_ascii=False)

    print(f"✓ Extracted data from CPC PDF")
    print(f"✓ Saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  - Cases: {len(CPC_DATA['cases'])}")
    print(f"  - Courts: {len(CPC_DATA['courts'])}")
    print(f"  - Sections: {len(CPC_DATA['sections'])}")
    print(f"  - Principles: {len(CPC_DATA['principles'])}")
    print(f"  - Statutes: {len(CPC_DATA['statutes'])}")

    return CPC_DATA


if __name__ == "__main__":
    extract_and_save()
