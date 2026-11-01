# Dubai Municipality permit documents and BIM mandate: sources for the RePermit knowledge base (status: 1 November 2026)

Conventions used in these notes:
- "PRIMARY" means the document itself was retrieved and read from a government domain.
- "LEAD" means a secondary source or a search-result snippet. A lead is not evidence.
- English renderings of Arabic circulars are my own working translations, not official ones. The Arabic text prevails.
- Unreachable hosts: hub.dm.gov.ae, api.buildindubai.gov.ae and buildindubai.gov.ae refused the connection, and bpspermit.dm.gov.ae and www.buildindubai.gov.ae did not resolve. web.archive.org could not be fetched either. The cause is unknown: it may be geo-blocking or a network restriction. It does not show that these pages require a login, and it does not show they are public.

## Where are DM's service cards or document lists for building modification, addition, alteration and renovation permits? Are they retrievable, and what do they list?

### Takeaway
The DM service exists and its service card URL is now known: "Permit to Make Modifications or Additions to Buildings", ServiceCode 4127, on hub.dm.gov.ae. The card could not be retrieved, so **the official document list for modifications remains NOT FOUND**. No primary source reviewed lists the documents for this service. Do not fill this gap with the DDA list, which comes from a different authority.

### Cited Findings
Service catalogue (PRIMARY, catalogue page only):
- DM's services page lists "Permit to Make Modifications or Additions to Buildings", for changes and additions to existing or under-construction buildings. Card: hub.dm.gov.ae/link/servicedetails?ServiceCode=4127 — [DM services](https://www.dm.gov.ae/dubai-municipality-services/)
- Related services on the same page:
  - Permit to Build Extensions to Private Villas (4117)
  - Self Permit to Carry Out Decorative Works (4193; units over 100 sqm, subject to conditions)
  - Self Permit to Carry Out Structural Maintenance Works (3413)
  - Issue Building Completion Certificate (4191; covers permits including decor, modifications, adjustments and maintenance)
  - Initial approval for Design Concept (3397; proposed construction or modification works)
  - Historical-area services (2084, 2086)
  - Request for Alteration/Addition on the Leased Properties (NOC; no card link) — [DM services](https://www.dm.gov.ae/dubai-municipality-services/)
- Fetches of the cards for 4127 and 4117 failed with connection refused — [card 4127, not retrieved](https://hub.dm.gov.ae/link/servicedetails?ServiceCode=4127)
- The BPS help-documents page cited in DM's FAQ (bpspermit.dm.gov.ae/BPCSWeb/help/LinkDocuments.jsp?category=5) did not resolve. No login was attempted. — [DM FAQ](https://dmpmedia.dm.gov.ae/uploads/2023/09/FAQ-for-Buildings-Permit-Procedures-and-Regulations-eng-1.pdf)

Primary procedure and rules that were retrieved:
- Circular 3-7-1 of 2021 (23/08/2021, "Approval of Modification Drawings", signed by the Director of the Building Permits Department):
  - The consultant may submit all architectural drawings for internal modifications made during construction in one batch at the end of the works, before starting the completion certificate procedure, provided they do not conflict with the building system, regulations and circulars.
  - Major modifications, such as structural ones, must be approved by the Permits section before execution.
  - The consultant bears full responsibility for any conflict or violation. — [Circular 3-7-1](https://dmpmedia.dm.gov.ae/uploads/2022/04/3-7-1.pdf)
  - Inference from the text: this concerns changes during construction, not modifications to completed buildings.
- DM procedure "Procedure of Issuing Building Permit & Building Completion Certificate", 03 Multistorey Buildings, version 4, 10/5/2020:
  - The consultant applies through Dubai BPS, attaches all required drawings and documents, fills in the building card and pays fees.
  - Authorities upload NOCs through BPS, and DM issues the permit and stamps the drawings.
  - Inspection of adjustments, additions and decor work is by the DM Building Control Department only, with a Civil Defence task generated only if required.
  - No document list is given. — [DM procedure](https://dmpmedia.dm.gov.ae/uploads/2020/06/Multi-Story_Building-Permits-Procedures.pdf)
- DM FAQ "Buildings Permit Procedures and Regulations" (12 pages, undated; file created April 2023 and modified August 2023 per metadata):
  - It has no modification document list.
  - Modifications to villas through a self-decoration permit: see Circular 231 of 2018.
  - External cladding approval for existing projects and modifications: contact the Civil Defense external cladding approval department.
  - A new project cannot be submitted while an application is open on the same plot or unit. — [DM FAQ](https://dmpmedia.dm.gov.ae/uploads/2023/09/FAQ-for-Buildings-Permit-Procedures-and-Regulations-eng-1.pdf)
- Circular 2-2-1 of 2022 (14/11/2022) implements Administrative Resolution 227 of 2022:
  - The resolution has been in force since gazette publication on 24 August 2022.
  - It sets which planning and building parameters may be modified and under what conditions, and allows a podium for multi-storey buildings.
  - It cancels Circular 3-5-1 of 2021 (date and number as in the Arabic original; the English technical translation prints "1-5-3"). — [Arabic](https://dmpmedia.dm.gov.ae/uploads/2022/11/2-2-1.pdf); [English technical translation](https://dmpmedia.dm.gov.ae/uploads/2024/11/2-2-1-Implementation-of-Administrative-Resolution-No.-227-of-2022.pdf)
- The DM circulars index has these relevant sections: 1 (Modification of Building Uses, 1-1-1 to 1-3-1-1), 2 (Modifications on Planning and Building Regulations, 2-1-1 to 2-3-1) and 3-7 (Approval of Modifications Drawings). — [DM circulars index](https://www.dm.gov.ae/building-planning-circulars-2/)
- DM's "Required-Documents.pdf" is a false positive. It concerns qualifying contractors as design-and-build contractors, not modification permits. — [DM file](https://dmpmedia.dm.gov.ae/uploads/2020/11/Required-Documents.pdf)

LEADS (not evidence):
- A third-party guide says minor or major modifications are distinguished, DM replies through BPS within 3 working days, fees are AED 100 (minor/medium) and AED 200 (major/radical), and contractor insurance applies from 300 sqm. The text was seen only in a search snippet (page fetch failed) and is about 1,386 days old. — [tesz.in, lead](https://www.tesz.in/guide/request-permit-modifications-additions-buildings-dubai)
- Legal basis claimed: Article 3 of Local Order 3 of 1999. Not verified against the Order. — [The Law Reporters, lead](https://thelawreporters.com/dubai-s-renovation-regulations-essential-approvals-procedures-for-property-modifications)
- DDA (a different authority, not DM): a design submission reportedly needs approved stamped drawings with changes highlighted, owner NOC, consultant appointment letter, structural calculations and Civil Defence NOC where applicable. A government source, but seen only through search-result text and not applicable to DM-jurisdiction plots. — [DDA design](https://dda.gov.ae/en/planning-development/design/building-modification-design); [DDA Service ID Cards, Issue 6, Dec 2021, not read](https://webzoning.dda.gov.ae/Zoning/Content/dda/ServicesIDs/Building%20Modification%20Services'%20ID%20Cards.pdf)

### Inferences
- The DM document list most likely sits on the 4127 card or inside BPS. Someone with a UAE connection or a browser should open the 4127 card (it may be public) and capture it.
- The DDA list can serve only as a clearly labelled analogue in a demo, never as a DM requirement.
- DM's procedural regime distinguishes major from internal or other modifications, but the two definitions differ. Circular 3-7-1 (2021) uses "major" for changes during construction; Circular 9-1-3 (2026) has its own list for BIM. They should not be merged.

### Gaps
- NOT VERIFIED: the official document list, fees and durations for services 4127 and 4117.
- Circular 2-1-1 ("Cases where request for modification is permitted", listed 25/11/2022) was not read. Its page's download link leads to the 2-2-1 PDF, an apparent DM mislinking.
- Not read: Administrative Resolution 227 of 2022, Circular 231 of 2018, and the section 1 circulars.
- Dubai Now was not reached. A domain-restricted search of dubai.ae, u.ae and dubainow returned no modification checklist.

## BIM circulars: Circular 9-1-3 of 2026 and the circular behind the 1 January 2024 obligation (issuer, date, text, URL)

### Takeaway
Both gaps are closed and both circulars were retrieved from DM's domain. The 1 January 2024 obligation comes from **Circular 9-1-2 of 2023, dated 13/10/2023**. **Circular 9-1-3 of 2026, dated 15/01/2026, applies from 1 April 2026**. Both are signed by Mariam Obaid Al Muhairi, CEO of the Building Regulation and Licensing Establishment, under the Dubai Municipality letterhead. Both are in Arabic and addressed to engineering consulting offices and building contracting companies.

### Cited Findings
Circular 9-1-3 of 2026 (PRIMARY), "on expanding the obligation to submit BIM models with the building permit application for certain building types". It builds on 9-1-2 and applies from 1 April 2026.
- Part I, new buildings, for architectural and structural designs:
  - buildings, structures and complexes taller than G+12
  - buildings, structures and complexes with a built area of 15,000 m² or more
- Part II, "Modifications and additions to buildings previously licensed using BIM":
  - Major modifications require a BIM model with the permit application: adding or removing floors; adding 1,500 m² or more; complete design change; change of the building's main use; change of the building's position on the plot.
  - Other modifications: submit the final BIM model before applying for the completion certificate, reflecting the works approved and actually executed on site.
- BIM models must be submitted simultaneously with the drawings required for licensing, and the drawings must be extracted directly from the models so that they match fully.
- Consultants are urged, optionally, to submit models for buildings not currently covered.
- Further information: buildindubai.gov.ae/bim and GeoDubai@dm.gov.ae. — [Circular 9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf); [DM listing, dated 03/02/2026](https://www.dm.gov.ae/documents/circular-9-1-3/)

Circular 9-1-2 of 2023 (PRIMARY), "on the obligation to submit a BIM model with the building permit application for certain building types". It follows Circulars 196 of 2013, 207 of 2015 and 9-1-1 of 2021.
- It launches automated checking of building designs using BIM against the Dubai Building Code and the "Dubai BIM Standard", accessible via buildindubai.gov.ae.
- It requires architectural and structural designs in Open BIM format, per the Dubai standards, when applying for **new** building permits, as a first phase from 01/01/2024, for:
  1. buildings and structures over 20 floors (architectural) or over 40 floors (structural)
  2. buildings, structures and complexes over 20,000 m² (architectural) or over 30,000 m² (structural)
  3. specialised buildings such as hospitals and universities
  4. government projects, excepting service-utility projects only
- Submission runs parallel to the other drawings and requirements and does not replace them.
- Voluntary architectural models for private and investment villas and other buildings are welcome, and support consultant excellence assessments. — [Circular 9-1-2](https://dmpmedia.dm.gov.ae/uploads/2023/10/%D8%AA%D8%B9%D9%85%D9%8A%D9%85-BIM-9-1-2.pdf); [DM listing, dated 18/10/2023](https://www.dm.gov.ae/documents/circular-9-1-2/)

Circular 9-1-1 of 2021 (PRIMARY, DM technical English translation; Arabic prevails), dated 23/8/2021:
- BIM applies to architectural and mechanical works for buildings over 20 floors, over 200,000 sq ft, specialised buildings, all government projects, and projects submitted by a foreign office subsidiary.
- It applies to structural works for over 40 floors, over 300,000 sq ft, specialised buildings, and buildings submitted by a foreign office subsidiary. — [Circular 9-1-1](https://dmpmedia.dm.gov.ae/uploads/2024/11/9-1-1-Application-of-Buildings-Information-Modelling.pdf); [DM listing, dated 29/11/2024](https://www.dm.gov.ae/documents/circular-9-1-1/)

Date conflicts resolved: the DM listing dates (03/02/2026, 18/10/2023, 29/11/2024) differ from the dates printed on the circulars. Cite the date on the circular. Secondary sources that give 3 February 2026 as the date of 9-1-3 are repeating the listing date. — [DM listing](https://www.dm.gov.ae/documents/circular-9-1-3/)

### Inferences
- The 2026 thresholds are lower than the 2023 ones, so the earlier suspicion of a conflict in secondary sources is unfounded. 9-1-3 is expressly an expansion.
- LEAD corrected: one source's reference to the mandate as "Circular 207 (2021)" is wrong. 207 is from 2015 and 9-1-1 is the 2021 circular.
- The bonarchdraft page is broadly accurate on dates and thresholds but drops the key qualifier in Part II (see the next section). — [Bonarch, lead](https://bonarchdraft.com/dubai-bim-circular-9-1-3/)

### Gaps
- Circulars 196 of 2013 and 207 of 2015 were not retrieved. The URLs given in the BIM Standard's references now return the DM homepage. They are superseded in practice and are of historical interest.
- The copy at api.buildindubai.gov.ae/assets/circulars/913.pdf, cited by the BIM Standard, could not be reached. The dmpmedia copy is sufficient.
- The original Arabic 9-1-1 was not read.

## Which project types and thresholds does the BIM duty officially cover? Does it apply to modifications of existing buildings? Does it require IFC?

### Takeaway
**The BIM duty does not generally apply to modifications of existing buildings.** Under the text of 9-1-3 it reaches only modifications and additions to buildings **previously licensed using BIM**. A building permitted without BIM falls outside Part II. IFC is not named in either circular. 9-1-2 requires "Open BIM" per the Dubai standards, and the Dubai BIM Standard v1.4 then specifies IFC4 in .ifc files.

### Cited Findings
- New buildings from 1 April 2026: over G+12, or 15,000 m² built area or more, for architectural and structural designs. — [Circular 9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf)
- Modifications: only under the heading "previously licensed using BIM". The five major triggers require a model with the application. Everything else requires a final as-built-type model before the completion certificate. — [Circular 9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf)
- 9-1-2 covered new building permits only. — [Circular 9-1-2](https://dmpmedia.dm.gov.ae/uploads/2023/10/%D8%AA%D8%B9%D9%85%D9%8A%D9%85-BIM-9-1-2.pdf)
- Format: 9-1-2 says "Open BIM"; 9-1-3 states no format and does not mention IFC. — [9-1-2](https://dmpmedia.dm.gov.ae/uploads/2023/10/%D8%AA%D8%B9%D9%85%D9%8A%D9%85-BIM-9-1-2.pdf); [9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf)
- BIM Standard v1.4 (unconfirmed copy, see next section):
  - Primary files "shall be in Industry Foundation Classes (IFC) schema", exported using IFC4 and delivered as .ifc, with IFC authoritative for regulatory assessment (6.1.1).
  - Native files are supporting only.
  - Files are geo-referenced to EPSG:3997 (4.1.2).
  - One building and one discipline per file; disciplines AR and ST (Table 3, 7.6.2).
  - IfcSpace is mandatory for all BIM submissions (7.5.1).
  - 2D drawing requirements remain, generated from the model (6.1.1).
  - No BEP submission is required (3.2.3).
  - BIM submission is mandated only by DM as of issue, not by the other permit authorities (1.1).
  - Where BIM is not mandated, the process is recommended (3.2.2, section 4). — [Standard copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf)
- The Standard has no separate rules for modifications. It says the Level of Information Need depends on the type of permit application, with detail in Appendices A and B, which were not retrieved. — [Standard copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf)

### Inferences
- For RePermit: a typical modification to a pre-existing building has no BIM or IFC duty under these circulars. An IFC input is a demo design choice and may not be presented as a legal requirement. The honest statement is that IFC is required only where BIM is mandated, and for modifications that means buildings already BIM-permitted.
- BIM-permitted buildings can only go back to the 1 January 2024 obligation, or to earlier circulars if those are counted (9-1-1 and earlier "application of BIM"). Whether a pre-2024 BIM submission counts as "licensed using BIM" is undefined. Likely few such buildings have reached the modification stage, but no data supports this.
- 9-1-3 does not restate the specialised-building and government-project categories of 9-1-2. Because it is described as expanding 9-1-2, those categories probably persist. The text does not say so expressly.
- Binding chain for IFC: 9-1-2 names the "Dubai BIM Standard" without a version, and the Standard then fixes IFC4. The obligation therefore depends on which version is current.

### Gaps
- The circular is silent on a non-BIM building whose extension itself exceeds the thresholds, or adds 1,500 m² or more. On the text, Part II does not apply. Confirm with GeoDubai@dm.gov.ae.
- Enforcement practice is not verified. The Build in Dubai BIM page could not be reached, and it may carry FAQs.
- Whether the foreign-office-subsidiary category of 9-1-1 survived 9-1-2 is unclear. 9-1-2 does not repeat it and does not expressly repeal it.
- The current submission platform is unconfirmed. Leads conflict between bim.geodubai.ae and Build in Dubai. — [AEC Zone, lead](https://www.aeczoneglobal.com/blog/dubai-municipality-ifc-bim-online-submission-guide/); [LinkedIn FAQ, lead](https://www.linkedin.com/pulse/dubais-mandatory-bim-submission-building-permits-your-fahdah-qofwf)

## Provenance of the BIM Standard: is it issued by DM? Is there an official copy on a government domain? What is the latest version?

### Takeaway
The content is very probably a DM document, but **provenance is only partly confirmed**. The GitHub copy has DM branding and is hosted on an expressly unofficial personal site. The circulars confirm that a "Dubai BIM Standard" exists and lives on Build in Dubai, a government domain that could not be reached. v1.4 is the highest version seen; its status as latest is NOT verified.

### Cited Findings
- The cover shows the Dubai Municipality logo and "DUBAI BIM Standard Version 1.4". The footer reads "OPEN DATA / بيانات مفتوحة". There are 29 pages, no issue date, and no revision history or signatory in the text. — [Standard copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf)
- PDF metadata: author "Ali Ismail", created 18 May 2026 in Word, keyword "OPEN DATA". Read directly from the [same file](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf). The author's affiliation is unknown.
- It cites Circular 9-1-3 (2026, 01 15) at api.buildindubai.gov.ae, so it post-dates that circular. — [Standard copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf)
- The hosting site says it is "not an official Dubai Municipality website", is maintained by Dr. Ibrahim Fahdah and takes its content from DM public materials. The MIT notice appears to relate to the site theme, not the Standard. The changelog is empty. — [DxM Digital Docs](https://dxmdigitaldocs.github.io/site/); [Changelog](https://dxmdigitaldocs.github.io/site/CHANGELOG/)
- DM circular 9-1-2 names the "Dubai BIM Standard" and locates it at buildindubai.gov.ae. — [Circular 9-1-2](https://dmpmedia.dm.gov.ae/uploads/2023/10/%D8%AA%D8%B9%D9%85%D9%8A%D9%85-BIM-9-1-2.pdf)
- LEAD: a v1.2 exists on Scribd, so versions have circulated. — [Scribd, lead](https://www.scribd.com/document/884754413/Dubai-Building-Permit-BIM-Standards-V1-2-Fr)

### Inferences
- The May 2026 metadata and the references to 9-1-3 fit a genuine post-January 2026 revision. This is circumstantial and does not prove DM issued this file.
- The Standard's own wording speaks for the "Building Permit Authorities" collectively and also says "Dubai Municipality Circular". Its issuer may be a joint committee. Cite it as "Dubai BIM Standard v1.4 (copy; DM-branded; issuer unconfirmed)".
- For the knowledge base, treat it as provisional until a copy from buildindubai.gov.ae is compared with it, for example by hash.

### Gaps
- NOT VERIFIED: any official government-hosted copy, the issue date, the latest version as of November 2026, and Appendices A, B and C, the Technical Guides and the IDS files.
- The geodubai/bim.geodubai.ae roadmap cited in the Standard was not fetched.

## Terms of reuse for dm.gov.ae content

### Takeaway
dm.gov.ae gives **no general reuse licence**. The site is "all rights reserved", protected by UAE and foreign copyright. The open-data permission covers listed datasets, and circulars are not among them. Labels on the documents are inconsistent. For ingestion and quotation in a demo, permission is advisable and has not been obtained. No legal conclusion is drawn here.

### Cited Findings
- Website terms: the site's contents are protected by UAE and foreign copyright laws and international conventions, and users agree to abide by all posted copyright notices. There is no reuse, reproduction or linking clause. These quotes and this summary come through the fetch tool, and the page was not read in raw form. — [DM Terms & Conditions](https://www.dm.gov.ae/website-policies/terms-and-conditions/)
- Footer: "Copyright © 2026 Dubai Municipality, all rights reserved." — [DM circulars index](https://www.dm.gov.ae/building-planning-circulars-2/)
- Open data page:
  - "Customers have the right to use this data and statistics at their own liability."
  - "The source of the data must be mentioned when used."
  - DM accepts no liability for distortion, modification or wrong use.
  - Published under Law 26 of 2015 and Law 2 of 2016.
  - No named licence.
  - The listed items are datasets, including building permits, demolition permits and building usage data, via Dubai Pulse. Circulars and service cards are not listed. — [DM Open Data](https://www.dm.gov.ae/open-data2/)
- Document labels conflict:
  - 9-1-1, 9-1-2 and 9-1-3 carry "SHARED – CONFIDENTIAL / مشترك – خاص" although they are publicly posted. — [9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf)
  - The Arabic 2-2-1 carries "OPEN DATA" while its English translation carries "SHARED – CONFIDENTIAL". — [Arabic](https://dmpmedia.dm.gov.ae/uploads/2022/11/2-2-1.pdf); [English](https://dmpmedia.dm.gov.ae/uploads/2024/11/2-2-1-Implementation-of-Administrative-Resolution-No.-227-of-2022.pdf)
  - The BIM Standard copy carries "OPEN DATA". — [Standard copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf)
- False lead: the old URL dm.gov.ae/terms-and-conditions/ redirects to terms for the Consumer Products Testing Service, not website terms. — [PDF](https://dmpmedia.dm.gov.ae/uploads/2024/01/Terms-and-Conditions.pdf)

### Inferences
- Linking and short attributed quotation are the lowest-risk approach. Storing full texts in a RAG index is reproduction, and no term expressly allows it.
- The "SHARED" label probably reflects the Dubai data classification scheme rather than secrecy, given the public posting. Its effect on reuse is unconfirmed and should be checked.
- Sensible step: ask DM (GeoDubai@dm.gov.ae for BIM) for written permission, and keep the origin URL and date for each chunk.

### Gaps
- The Dubai Data Establishment reuse licence text and the meaning of "SHARED" were not retrieved.
- The DxM copy's content licence is unclear. An unofficial host cannot grant rights in DM content.

### Source register (all retrieval attempts on 2026-11-01)

| Source | Issuer | Version/date | Language | Retrieved | Reuse terms |
|---|---|---|---|---|---|
| [Circular 9-1-3](https://dmpmedia.dm.gov.ae/uploads/2026/02/Circular-9-1-3.pdf) | BRLE / Dubai Municipality | 15/01/2026; effective 1/4/2026 | Arabic | Yes | All rights reserved; labelled SHARED |
| [Circular 9-1-2](https://dmpmedia.dm.gov.ae/uploads/2023/10/%D8%AA%D8%B9%D9%85%D9%8A%D9%85-BIM-9-1-2.pdf) | BRLE / DM | 13/10/2023; effective 1/1/2024 | Arabic | Yes | All rights reserved; labelled SHARED |
| [Circular 9-1-1](https://dmpmedia.dm.gov.ae/uploads/2024/11/9-1-1-Application-of-Buildings-Information-Modelling.pdf) | DM | 23/8/2021 | English translation | Yes | All rights reserved; labelled SHARED |
| [Circular 3-7-1](https://dmpmedia.dm.gov.ae/uploads/2022/04/3-7-1.pdf) | DM Building Permits Dept | 23/8/2021 | Arabic | Yes | All rights reserved; no label seen |
| [Circular 2-2-1](https://dmpmedia.dm.gov.ae/uploads/2022/11/2-2-1.pdf) | BRLE / DM | 14/11/2022 | Arabic, plus [English](https://dmpmedia.dm.gov.ae/uploads/2024/11/2-2-1-Implementation-of-Administrative-Resolution-No.-227-of-2022.pdf) | Yes | Arabic OPEN DATA; English SHARED |
| [Circular 2-1-1 listing](https://www.dm.gov.ae/documents/circular-2-1-1/) | DM | Listed 25/11/2022 | Unknown | No, link leads to 2-2-1 | Not known |
| [Procedure, Multistorey](https://dmpmedia.dm.gov.ae/uploads/2020/06/Multi-Story_Building-Permits-Procedures.pdf) | DM | v4, 10/5/2020 | English | Yes | All rights reserved |
| [FAQ, Permit Procedures](https://dmpmedia.dm.gov.ae/uploads/2023/09/FAQ-for-Buildings-Permit-Procedures-and-Regulations-eng-1.pdf) | DM | Undated (2023 metadata) | English | Yes | All rights reserved |
| [Services catalogue](https://www.dm.gov.ae/dubai-municipality-services/) | DM | Modified 1/11/2026 | English | Yes | All rights reserved |
| [Service card 4127](https://hub.dm.gov.ae/link/servicedetails?ServiceCode=4127) | DM | Unknown | Unknown | No, connection refused | Not known |
| [Terms & Conditions](https://www.dm.gov.ae/website-policies/terms-and-conditions/) | DM | Current | English | Yes | n/a |
| [Open Data page](https://www.dm.gov.ae/open-data2/) | DM | Current | English | Yes | Listed data only: attribution, own liability |
| [BIM Standard v1.4 copy](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf) | DM-branded; hosted by private party; issuer unconfirmed | v1.4; file dated 18/5/2026 | English | Yes (unofficial copy) | Labelled OPEN DATA; licence unclear |
| [Build in Dubai BIM](https://buildindubai.gov.ae/bim) | Named in DM circulars | Unknown | Unknown | No, connection refused | Not known |
