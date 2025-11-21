// =============================================================================
// LEGAL KNOWLEDGE GRAPH - SAMPLE DATA
// =============================================================================
// This script creates sample data to demonstrate the schema and test queries
// =============================================================================

// -----------------------------------------------------------------------------
// STEP 1: CREATE JURISDICTIONS
// -----------------------------------------------------------------------------

CREATE (bd:Jurisdiction {
  jurisdiction_id: 'JUR-BD',
  code: 'BD',
  name: 'Bangladesh',
  jurisdiction_type: 'Country',
  legal_system: 'Common Law',
  independence_date: date('1971-12-16'),
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (india:Jurisdiction {
  jurisdiction_id: 'JUR-IN',
  code: 'IN',
  name: 'India',
  jurisdiction_type: 'Country',
  legal_system: 'Common Law',
  independence_date: date('1947-08-15'),
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (pakistan:Jurisdiction {
  jurisdiction_id: 'JUR-PK',
  code: 'PK',
  name: 'Pakistan',
  jurisdiction_type: 'Country',
  legal_system: 'Common Law',
  independence_date: date('1947-08-14'),
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 2: CREATE LEGAL DOMAINS
// -----------------------------------------------------------------------------

CREATE (criminal:LegalDomain {
  domain_id: 'DOMAIN-CRIMINAL',
  name: 'Criminal Law',
  description: 'Laws related to crimes and criminal procedures',
  keywords: ['crime', 'punishment', 'criminal procedure', 'prosecution'],
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (civil:LegalDomain {
  domain_id: 'DOMAIN-CIVIL',
  name: 'Civil Law',
  description: 'Laws governing private rights and remedies',
  keywords: ['civil rights', 'contracts', 'torts', 'remedies'],
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (constitutional:LegalDomain {
  domain_id: 'DOMAIN-CONSTITUTIONAL',
  name: 'Constitutional Law',
  description: 'Laws related to constitutional interpretation and fundamental rights',
  keywords: ['constitution', 'fundamental rights', 'judicial review'],
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (commercial:LegalDomain {
  domain_id: 'DOMAIN-COMMERCIAL',
  name: 'Commercial Law',
  description: 'Laws governing business and commercial transactions',
  keywords: ['business', 'commerce', 'trade', 'contracts'],
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 3: CREATE COURTS
// -----------------------------------------------------------------------------

CREATE (bdsc:Court {
  court_id: 'COURT-BD-SC',
  name: 'Supreme Court of Bangladesh',
  jurisdiction: 'BD',
  court_level: 'supreme',
  court_type: 'appellate',
  location: 'Dhaka',
  established_date: date('1972-12-16'),
  appellate_jurisdiction: true,
  original_jurisdiction: true,
  binding_precedent_scope: 'national',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (insc:Court {
  court_id: 'COURT-IN-SC',
  name: 'Supreme Court of India',
  jurisdiction: 'IN',
  court_level: 'supreme',
  court_type: 'appellate',
  location: 'New Delhi',
  established_date: date('1950-01-26'),
  appellate_jurisdiction: true,
  original_jurisdiction: true,
  binding_precedent_scope: 'national',
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 4: CREATE STATUTES
// -----------------------------------------------------------------------------

CREATE (bdpc:Statute {
  statute_id: 'STAT-BD-PC-1860',
  name: 'Penal Code, 1860',
  short_name: 'Penal Code',
  jurisdiction: 'BD',
  statute_type: 'Code',
  enactment_date: date('1860-10-06'),
  effective_date: date('1860-10-06'),
  status: 'Active',
  version: 1,
  is_current_version: true,
  summary: 'The primary criminal code of Bangladesh',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (inpc:Statute {
  statute_id: 'STAT-IN-PC-1860',
  name: 'Indian Penal Code, 1860',
  short_name: 'IPC',
  jurisdiction: 'IN',
  statute_type: 'Code',
  enactment_date: date('1860-10-06'),
  effective_date: date('1860-10-06'),
  status: 'Active',
  version: 1,
  is_current_version: true,
  summary: 'The primary criminal code of India',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (bdconst:Statute {
  statute_id: 'STAT-BD-CONST-1972',
  name: 'Constitution of Bangladesh',
  short_name: 'Constitution',
  jurisdiction: 'BD',
  statute_type: 'Constitution',
  enactment_date: date('1972-11-04'),
  effective_date: date('1972-12-16'),
  status: 'Active',
  version: 1,
  is_current_version: true,
  summary: 'The supreme law of Bangladesh',
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 5: CREATE SECTIONS
// -----------------------------------------------------------------------------

CREATE (sec302:Section {
  section_id: 'SEC-BD-PC-302',
  section_number: '302',
  title: 'Punishment for murder',
  section_type: 'Section',
  text: 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
  summary: 'Prescribes punishment for murder',
  version: 1,
  effective_from: date('1860-10-06'),
  is_current_version: true,
  status: 'Active',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (sec304:Section {
  section_id: 'SEC-BD-PC-304',
  section_number: '304',
  title: 'Punishment for culpable homicide not amounting to murder',
  section_type: 'Section',
  text: 'Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.',
  version: 1,
  effective_from: date('1860-10-06'),
  is_current_version: true,
  status: 'Active',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (art32:Section {
  section_id: 'SEC-BD-CONST-32',
  section_number: '32',
  title: 'Right to life',
  section_type: 'Article',
  text: 'No person shall be deprived of life or personal liberty save in accordance with law.',
  summary: 'Fundamental right to life and personal liberty',
  version: 1,
  effective_from: date('1972-12-16'),
  is_current_version: true,
  status: 'Active',
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 6: CREATE JUDGES
// -----------------------------------------------------------------------------

CREATE (judge1:Judge {
  judge_id: 'JUDGE-BD-001',
  name: 'Justice Obaidul Hassan',
  honorific: 'Hon\'ble',
  designation: 'Chief Justice',
  court: 'Supreme Court of Bangladesh',
  jurisdiction: 'BD',
  appointment_date: date('2020-01-01'),
  status: 'Active',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (judge2:Judge {
  judge_id: 'JUDGE-IN-001',
  name: 'Justice D.Y. Chandrachud',
  honorific: 'Hon\'ble',
  designation: 'Chief Justice of India',
  court: 'Supreme Court of India',
  jurisdiction: 'IN',
  appointment_date: date('2016-05-13'),
  status: 'Active',
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 7: CREATE LEGAL PRINCIPLES
// -----------------------------------------------------------------------------

CREATE (natjust:LegalPrinciple {
  principle_id: 'PRINCIPLE-001',
  name: 'Natural Justice',
  latin_name: 'audi alteram partem',
  description: 'The principle that no person should be judged without a fair hearing in which each party is given the opportunity to respond to the evidence against them.',
  principle_type: 'doctrine',
  legal_domain: ['administrative', 'constitutional'],
  jurisdiction: ['BD', 'IN', 'PK'],
  origin: 'common law',
  keywords: ['natural justice', 'fair hearing', 'audi alteram partem'],
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (presumption:LegalPrinciple {
  principle_id: 'PRINCIPLE-002',
  name: 'Presumption of Innocence',
  latin_name: 'ei incumbit probatio qui dicit, non qui negat',
  description: 'The principle that one is considered innocent until proven guilty.',
  principle_type: 'doctrine',
  legal_domain: ['criminal'],
  jurisdiction: ['BD', 'IN', 'PK'],
  origin: 'common law',
  keywords: ['presumption of innocence', 'burden of proof', 'criminal law'],
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 8: CREATE PARTIES
// -----------------------------------------------------------------------------

CREATE (state:Party {
  party_id: 'PARTY-BD-STATE',
  name: 'State of Bangladesh',
  party_type: 'government',
  organization_type: 'government_entity',
  jurisdiction: 'BD',
  anonymized: false,
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (accused1:Party {
  party_id: 'PARTY-BD-001',
  name: 'Md. Rahman',
  party_type: 'individual',
  jurisdiction: 'BD',
  anonymized: false,
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 9: CREATE CASES
// -----------------------------------------------------------------------------

CREATE (case1:Case {
  case_id: 'CASE-BD-SC-2023-001',
  citation: '2023 SCOB 1',
  neutral_citation: '[2023] BDSC 001',
  title: 'State v. Md. Rahman',
  short_title: 'Rahman',
  court: 'Supreme Court of Bangladesh',
  bench_type: 'Division Bench',
  bench_strength: 2,
  decision_date: date('2023-06-15'),
  filing_date: date('2022-01-10'),
  jurisdiction: 'BD',
  case_type: 'Criminal',
  case_number: 'Criminal Appeal No. 123/2023',
  outcome: 'Appeal Dismissed',
  status: 'Active',
  precedent_value: 'Binding',
  summary: 'Appeal against conviction under Section 302 of the Penal Code. Court upheld conviction and death sentence.',
  headnotes: 'Murder - Section 302 Penal Code - Death penalty - Constitutional validity - Right to life under Article 32',
  catchwords: ['murder', 'death penalty', 'constitutional validity', 'right to life'],
  created_at: datetime(),
  updated_at: datetime(),
  source_url: 'http://example.com/case1'
});

CREATE (case2:Case {
  case_id: 'CASE-IN-SC-1973-027',
  citation: 'AIR 1973 SC 1461',
  neutral_citation: '[1973] INSC 027',
  title: 'Kesavananda Bharati v. State of Kerala',
  short_title: 'Kesavananda Bharati',
  court: 'Supreme Court of India',
  bench_type: 'Constitution Bench',
  bench_strength: 13,
  decision_date: date('1973-04-24'),
  jurisdiction: 'IN',
  case_type: 'Constitutional',
  outcome: 'Partially Allowed',
  status: 'Active',
  precedent_value: 'Binding',
  summary: 'Landmark case establishing the basic structure doctrine of the Constitution.',
  headnotes: 'Constitutional Law - Basic Structure Doctrine - Parliamentary Sovereignty - Judicial Review',
  catchwords: ['basic structure', 'constitutional amendment', 'judicial review', 'fundamental rights'],
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 10: CREATE LEGAL ISSUES
// -----------------------------------------------------------------------------

CREATE (issue1:LegalIssue {
  issue_id: 'ISSUE-001',
  description: 'Whether the mandatory death penalty for murder violates the right to life guaranteed under the Constitution',
  issue_type: 'constitutional',
  legal_domain: ['criminal', 'constitutional'],
  keywords: ['death penalty', 'right to life', 'constitutional validity'],
  complexity: 'complex',
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 11: CREATE KEYWORDS
// -----------------------------------------------------------------------------

CREATE (kw1:Keyword {
  keyword_id: 'KW-MURDER',
  term: 'murder',
  normalized_term: 'murder',
  category: 'Crime',
  frequency: 1000,
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (kw2:Keyword {
  keyword_id: 'KW-DEATH-PENALTY',
  term: 'death penalty',
  normalized_term: 'death penalti',
  category: 'Remedy',
  frequency: 500,
  created_at: datetime(),
  updated_at: datetime()
});

// -----------------------------------------------------------------------------
// STEP 12: CREATE RELATIONSHIPS
// -----------------------------------------------------------------------------

// Link jurisdictions (can add parent-child for states/provinces later)

// Link courts to jurisdictions
MATCH (c:Court {court_id: 'COURT-BD-SC'}), (j:Jurisdiction {code: 'BD'})
CREATE (c)-[:IN_JURISDICTION {created_at: datetime()}]->(j);

MATCH (c:Court {court_id: 'COURT-IN-SC'}), (j:Jurisdiction {code: 'IN'})
CREATE (c)-[:IN_JURISDICTION {created_at: datetime()}]->(j);

// Link statutes to jurisdictions
MATCH (s:Statute {statute_id: 'STAT-BD-PC-1860'}), (j:Jurisdiction {code: 'BD'})
CREATE (s)-[:IN_JURISDICTION {created_at: datetime()}]->(j);

MATCH (s:Statute {statute_id: 'STAT-IN-PC-1860'}), (j:Jurisdiction {code: 'IN'})
CREATE (s)-[:IN_JURISDICTION {created_at: datetime()}]->(j);

MATCH (s:Statute {statute_id: 'STAT-BD-CONST-1972'}), (j:Jurisdiction {code: 'BD'})
CREATE (s)-[:IN_JURISDICTION {created_at: datetime()}]->(j);

// Link sections to statutes
MATCH (sec:Section {section_id: 'SEC-BD-PC-302'}), (stat:Statute {statute_id: 'STAT-BD-PC-1860'})
CREATE (stat)-[:CONTAINS {order: 302, created_at: datetime()}]->(sec);

MATCH (sec:Section {section_id: 'SEC-BD-PC-304'}), (stat:Statute {statute_id: 'STAT-BD-PC-1860'})
CREATE (stat)-[:CONTAINS {order: 304, created_at: datetime()}]->(sec);

MATCH (sec:Section {section_id: 'SEC-BD-CONST-32'}), (stat:Statute {statute_id: 'STAT-BD-CONST-1972'})
CREATE (stat)-[:CONTAINS {order: 32, created_at: datetime()}]->(sec);

// Link cases to courts
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (court:Court {court_id: 'COURT-BD-SC'})
CREATE (c)-[:BEFORE_COURT {
  hearing_date: date('2023-05-15'),
  decision_date: date('2023-06-15'),
  court_level: 'appellate',
  created_at: datetime()
}]->(court);

MATCH (c:Case {case_id: 'CASE-IN-SC-1973-027'}), (court:Court {court_id: 'COURT-IN-SC'})
CREATE (c)-[:BEFORE_COURT {
  decision_date: date('1973-04-24'),
  court_level: 'original',
  created_at: datetime()
}]->(court);

// Link cases to judges
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (j:Judge {judge_id: 'JUDGE-BD-001'})
CREATE (c)-[:DECIDED_BY {
  role: 'Presiding Judge',
  authoring_judge: true,
  created_at: datetime()
}]->(j);

// Link cases to parties
MATCH (p:Party {party_id: 'PARTY-BD-STATE'}), (c:Case {case_id: 'CASE-BD-SC-2023-001'})
CREATE (p)-[:PETITIONER {
  party_role: 'Appellant',
  party_number: 1,
  created_at: datetime()
}]->(c);

MATCH (p:Party {party_id: 'PARTY-BD-001'}), (c:Case {case_id: 'CASE-BD-SC-2023-001'})
CREATE (p)-[:RESPONDENT {
  party_role: 'Respondent',
  party_number: 1,
  created_at: datetime()
}]->(c);

// Link cases to sections (application)
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (s:Section {section_id: 'SEC-BD-PC-302'})
CREATE (c)-[:APPLIES_SECTION {
  application_type: 'Directly Applied',
  interpretation: 'Court upheld the mandatory death penalty provision',
  created_at: datetime()
}]->(s);

MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (s:Section {section_id: 'SEC-BD-CONST-32'})
CREATE (c)-[:APPLIES_SECTION {
  application_type: 'Interpreted',
  interpretation: 'Right to life does not prohibit death penalty when prescribed by law',
  created_at: datetime()
}]->(s);

// Link cases to legal issues
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (i:LegalIssue {issue_id: 'ISSUE-001'})
CREATE (c)-[:RAISES_ISSUE {
  issue_number: 1,
  resolution: 'Resolved in favor of respondent',
  is_main_issue: true,
  created_at: datetime()
}]->(i);

// Link cases to legal domains
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (d:LegalDomain {domain_id: 'DOMAIN-CRIMINAL'})
CREATE (c)-[:BELONGS_TO_DOMAIN {
  relevance: 'Primary',
  confidence: 1.0,
  created_at: datetime()
}]->(d);

MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (d:LegalDomain {domain_id: 'DOMAIN-CONSTITUTIONAL'})
CREATE (c)-[:BELONGS_TO_DOMAIN {
  relevance: 'Secondary',
  confidence: 0.8,
  created_at: datetime()
}]->(d);

// Link cases to legal principles
MATCH (c:Case {case_id: 'CASE-IN-SC-1973-027'}), (p:LegalPrinciple {principle_id: 'PRINCIPLE-001'})
CREATE (c)-[:ESTABLISHES_PRINCIPLE {
  principle_role: 'First Recognition',
  binding_nature: 'Ratio Decidendi',
  created_at: datetime()
}]->(p);

// Link cases to keywords
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (k:Keyword {keyword_id: 'KW-MURDER'})
CREATE (c)-[:HAS_KEYWORD {
  relevance_score: 1.0,
  frequency: 15,
  extraction_method: 'Manual',
  created_at: datetime()
}]->(k);

MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'}), (k:Keyword {keyword_id: 'KW-DEATH-PENALTY'})
CREATE (c)-[:HAS_KEYWORD {
  relevance_score: 0.95,
  frequency: 8,
  extraction_method: 'Manual',
  created_at: datetime()
}]->(k);

// Citation relationships (cross-jurisdiction)
// Case 1 cites Case 2 (Indian precedent)
MATCH (citing:Case {case_id: 'CASE-BD-SC-2023-001'}), (cited:Case {case_id: 'CASE-IN-SC-1973-027'})
CREATE (citing)-[:CITES {
  citation_type: 'Referred',
  treatment: 'Positive',
  weight: 0.7,
  context: 'Court referred to the basic structure doctrine while analyzing constitutional validity',
  created_at: datetime()
}]->(cited);

// =============================================================================
// VERIFICATION QUERIES
// =============================================================================

// Count nodes by type
MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC;

// Show sample case with all relationships
MATCH (c:Case {case_id: 'CASE-BD-SC-2023-001'})
OPTIONAL MATCH (c)-[r]->(related)
RETURN c, r, related LIMIT 50;

// Show precedent chain
MATCH path = (c1:Case)-[:CITES*1..3]->(c2:Case)
RETURN path LIMIT 10;

// =============================================================================
// SAMPLE DATA CREATION COMPLETE
// =============================================================================
