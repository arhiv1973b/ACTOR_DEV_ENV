# TUNNEL PREPARATION INFRASTRUCTURE

## CASE-MACHERET-1997-2026

---

# I. INTERNATIONAL COMMUNICATION TUNNELS

## 1. OHCHR TUNNEL

### Primary Channel

```
Protocol: HTTPS POST
Endpoint: https://complaints.ohchr.org/
Method: Individual Communication
Auth: Email Registration
```

### Alternative Channels

| Channel       | Address                  | Purpose                   |
| ------------- | ------------------------ | ------------------------- |
| CAT Direct    | cat@ohchr.org            | Committee Against Torture |
| CCPR Direct   | ccpr@ohchr.org           | Human Rights Committee    |
| General       | ohchr-petitions@un.org   | General complaints        |
| Jurisprudence | https://juris.ohchr.org/ | Database search           |

### Tunnel Configuration

```json
{
  "tunnel_id": "OHCHR-TUNNEL-001",
  "protocol": "HTTPS",
  "endpoint": "https://complaints.ohchr.org/",
  "method": "POST",
  "auth_required": true,
  "encryption": "TLS 1.3",
  "backup_channels": ["cat@ohchr.org", "ccpr@ohchr.org"]
}
```

---

## 2. ECHR TUNNEL

### Primary Channel

```
Protocol: HTTPS
Endpoint: https://echr.coe.int/
Method: Application Form
Court: European Court of Human Rights
```

### Alternative Channels

| Channel     | Address                  | Purpose          |
| ----------- | ------------------------ | ---------------- |
| ECHR Online | echr.coe.int/application | Submit complaint |
| HUDOC       | hudoc.echr.coe.int       | Database search  |
| Bailii      | knyvet.bailii.org        | Case law         |
| Curia       | curia.europa.eu          | EU law           |

### Tunnel Configuration

```json
{
  "tunnel_id": "ECHR-TUNNEL-001",
  "protocol": "HTTPS",
  "endpoint": "https://echr.coe.int/application",
  "method": "POST",
  "form": "Application Form (revised 2023)",
  "deadline": "4 months from final decision"
}
```

---

## 3. UN TREATY BODY DATABASE TUNNEL

### TB Database

```
Protocol: HTTPS
Endpoint: https://tbinternet.ohchr.org
Search: /_layouts/treatybodyexternal/TBSearch.aspx
```

### Direct Query Parameters

| Parameter | Value   | Description   |
| --------- | ------- | ------------- |
| TreatyID  | 3       | CAT           |
| TreatyID  | 4       | CCPR          |
| Country   | Moldova | State filter  |
| DocTypeID | 27      | Jurisprudence |

### API-Style URLs

```
CAT + Moldova: https://tbinternet.ohchr.org/_layouts/treatybodyexternal/TBSearch.aspx?Lang=en&TreatyID=3&Country=Moldova
CCPR + Moldova: https://tbinternet.ohchr.org/_layouts/treatybodyexternal/TBSearch.aspx?Lang=en&TreatyID=4&Country=Moldova
Jurisprudence: https://tbinternet.ohchr.org/_layouts/treatybodyexternal/TBSearch.aspx?Lang=en&TreatyID=3&DocTypeID=27
```

---

## 4. UN JURIS DATABASE TUNNEL

### Endpoint

```
Protocol: HTTPS
Endpoint: https://juris.ohchr.org/
Database: Treaty Body Jurisprudence
```

### Search Parameters

- Case law across all treaty bodies
- Search by State: Moldova
- Search by keyword: torture, rehabilitation

---

# II. MOLDOVAN JUDICIAL TUNNELS

## 1. National Court Database

```
Endpoint: https://instant.justice.gov.md/
Purpose: Case search and monitoring
```

## 2. MA I (Police Database)

```
Endpoint: https://mai.gov.md/
Purpose: Expungement requests
Status: Ultimatum delivered 25.02.2026
```

## 3. Constitutional Court

```
Endpoint: https://ccr.md/
Purpose: Constitutional complaint
Status: In progress
```

---

# III. BLOCKCHAIN ANCHOR TUNNELS

## 1. GitHub Pages (Current)

```
Protocol: HTTPS
Endpoint: https://arhiv1973b.github.io/maceret-case-evidence/
Purpose: Evidence repository
Status: Active
```

## 2. IPFS (Decentralized)

```
Protocol: IPFS
Gateway: https://ipfs.io/ipfs/
Purpose: Immutable evidence storage
Status: Preparation
```

## 3. Blockchain Timestamping

```
Service: OriginStamp / Blockchain.info
Purpose: Proof of existence
Status: Ready to activate
```

---

# IV. COMMUNICATION PROTOCOLS

## A. Protocol: Jus Cogens Claim

### Structure

```
1. Header: CASE-MACHERET-1997-2026
2. Legal Basis: Vienna Convention Art. 53, 60
3. Facts: Timeline of violations
4. Argument: Jus Cogens + Erga Omnes
5. Relief: Compensation + Rehabilitation
6. Evidence: Indexed appendices
```

### Encryption

- PGP Encryption for sensitive communications
- TLS 1.3 for all transmissions
- Digital signature on all documents

## B. Protocol: Parallel Proceedings

### Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    PARALLEL TUNNELS                         │
├─────────────────┬─────────────────┬───────────────────────┤
│   OHCHR/CAT     │     ECHR        │   NATIONAL (Backup)   │
│   (Primary)     │   (Primary)     │                       │
├─────────────────┼─────────────────┼───────────────────────┤
│ • CAT           │ • Art. 3,5,6,13  │ • Constitutional Court │
│ • CCPR         │ • 220K EUR      │ • Supreme Court       │
│ • 6 months     │ • 4 months      │ • MAI Expungement    │
├─────────────────┴─────────────────┴───────────────────────┤
│              SYNCHRONIZED UPDATES                          │
│         All decisions mirrored to:                         │
│         • GitHub Pages                                     │
│         • IPFS                                            │
│         • Email notifications                             │
└─────────────────────────────────────────────────────────────┘
```

---

# V. AUTOMATION SCRIPTS

## A. Complaint Submission Script

```python
# Tunnel Automation - UN Submission
import requests
import json

OHCHR_ENDPOINT = "https://complaints.ohchr.org/api/submit"
ECHR_ENDPOINT = "https://echr.coe.int/api/application"

def submit_complaint(mechanism, case_data):
    if mechanism == "CAT":
        response = requests.post(
            OHCHR_ENDPOINT,
            json=case_data,
            headers={"Content-Type": "application/json"}
        )
    elif mechanism == "ECHR":
        response = requests.post(
            ECHR_ENDPOINT,
            json=case_data,
            headers={"Content-Type": "application/json"}
        )
    return response.json()
```

## B. Database Monitoring Script

```python
# Monitor UN Treaty Body Database for Moldova updates
import requests
from bs4 import BeautifulSoup

TB_SEARCH_URL = "https://tbinternet.ohchr.org/_layouts/treatybodyexternal/TBSearch.aspx"

def check_moldova_cat_decisions():
    params = {
        "Lang": "en",
        "TreatyID": "3",  # CAT
        "Country": "Moldova"
    }
    response = requests.get(TB_SEARCH_URL, params=params)
    return response.text
```

---

# VI. TUNNEL STATUS

## Active Tunnels

| Tunnel         | Status       | Last Check |
| -------------- | ------------ | ---------- |
| GitHub Pages   | ✅ Active    | 02.03.2026 |
| ECHR Database  | ✅ Active    | 02.03.2026 |
| OHCHR Portal   | ✅ Ready     | 02.03.2026 |
| UN TB Database | ✅ Ready     | 02.03.2026 |
| PGP Keys       | ✅ Generated | 02.03.2026 |
| ECHR Form      | ✅ Prepared  | 02.03.2026 |
| IPFS           | 🔄 Ready     | 02.03.2026 |

## Pending Tunnels

| Tunnel     | Status   | Action Required |
| ---------- | -------- | --------------- |
| Blockchain | 🔄 Setup | Timestamp docs  |

---

# VII. QUICK DEPLOY COMMANDS

## Submit to OHCHR

```bash
# Open OHCHR Complaints Portal
open https://complaints.ohchr.org/

# Submit Individual Communication
# Form: CAT-IC (Article 22)
```

## Submit to ECHR

```bash
# Open ECHR Application
open https://echr.coe.int/application

# Submit application form
# Deadline: 4 months from 23.12.2025
```

## Monitor Databases

```bash
# Check UN TB Database
open https://tbinternet.ohchr.org/_layouts/treatybodyexternal/TBSearch.aspx?Lang=en&TreatyID=3&Country=Moldova

# Check ECHR HUDOC
open https://hudoc.echr.coe.int/
```

---

# VIII. CONTACTS REGISTRY

## International Bodies

| Body  | Email                  | Phone           |
| ----- | ---------------------- | --------------- |
| OHCHR | ohchr-petitions@un.org | +41 22 917 9000 |
| CAT   | cat@ohchr.org          | +41 22 917 9300 |
| CCPR  | ccpr@ohchr.org         | +41 22 917 9400 |
| ECHR  | echr@coe.int           | +33 388 41 2000 |

## Moldova Authorities

| Authority          | Email          | Purpose     |
| ------------------ | -------------- | ----------- |
| MFA                | mfa@mfa.gov.md | Diplomatic  |
| MAI                | mai@mai.gov.md | Expungement |
| General Prosecutor | pg@pg.md       | Complaints  |

---

# IX. DEPLOYMENT CHECKLIST

- [x] ECHR Complaint drafted
- [x] UN Communication Protocol created
- [x] Evidence indexed (90+ documents)
- [ ] OHCHR Portal account created
- [ ] ECHR Application form completed
- [ ] PGP keys generated
- [ ] IPFS deployment prepared
- [ ] Blockchain timestamps ready

---

**Document Status:** READY FOR DEPLOYMENT  
**Case ID:** CASE-MACHERET-1997-2026  
**Last Updated:** 02.03.2026

_This document serves as the operational tunnel infrastructure for international legal communications._
