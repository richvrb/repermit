# Commercial AI products and startups for building permits, plan review and code compliance (2023-2026)

Research date: 2026-11-07. Notes in English (for a Dutch report). "VENDOR" = the vendor's own claim, not verified. "INDEPENDENT" = city evaluation report or third-party source. Date of each source is given where known.

---

## 1. Which products exist and what do they automate?

### Takeaway
The market splits into four groups. (a) City-side AI pre-screening and plan review on 2D PDFs: CivCheck/Clariti, Archistar AI PreCheck, Blitz AI, CodeComply/CivicPlus, Govstream.ai, Symbium, Deloitte Smart Permitting. (b) Applicant- or designer-side QA/QC and code research: UpCodes, Autodesk Drawing Compliance Review (announced, not yet released), Solibri (BIM/IFC rule engine), Archie (Norway), Firmus (now Bluebeam). (c) Permit-expediting services that combine AI and people: PermitFlow, GreenLite, Pulley. (d) Generative design tools that produce "permit-ready" drawings: Blueprints AI, Consigli. Northspyre is development and cost management, not permitting.

### Cited Findings

**CivCheck (Clariti), US/Canada, city-side and applicant-facing pre-screening**
- Clariti announced on 8 Oct 2025 that it had acquired CivCheck, a startup founded in 2023 near Chicago. Terms were not disclosed. Clariti said CivCheck would stay a standalone product that other permitting software can integrate, with Clariti Enterprise integration planned for spring 2026 — [Clariti blog](https://www.claritisoftware.com/blog/clariti-acquires-civcheck-to-accelerate-permit-approvals-with-ai); [BusinessWire 2025-10-08](https://www.businesswire.com/news/home/20251008364671/en); [GovTech](https://www.govtech.com/biz/permitting-software-firm-clariti-buys-startup-civcheck)
- Modules: an applicant portal with a "readiness score", intake/completeness checks (missing documents and information), and code checks across review disciplines for applicants and staff. The tool is "PDF-native" and needs no BIM. The product page does not mention drafting comment letters — [Clariti CivCheck product page](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software) (accessed 2026-11)
- Named customers (VENDOR): Honolulu, Seattle, New York City, San Jose, Greeley, Chanhassen, North Central Texas COG, Denver, and Calgary as a case study — [Clariti CivCheck page](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software)
- Toronto launched a one-year pilot on 27 Aug 2026, limited to houses and small residential projects. The tool compares uploaded drawings and documents with zoning, building permit and Ontario Building Code requirements. It runs on Google Cloud with data stored in Canada — [Toronto AI Register](https://www.toronto.ca/city-government/data-research-maps/ai-register/building-permit-application-precheck/) (page modified 2026-10-21)
- The Seattle report says CivCheck had worked with 13 jurisdictions across North America — [Seattle CivCheck PoV report, 2026](https://www.seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf)
- Denver: search snippets report that the city council approved a $4.6M contract (2026). I could not open the primary article (HTTP 403) — [Clariti: Denver selects CivCheck](https://www.claritisoftware.com/blog/city-of-denver-selects-civcheck-to-improve-permitting-efficiency); [Denverite 2026-03-10](https://denverite.com/2026/03/10/denver-complyai-ai-permit-review/)

**Archistar AI PreCheck (formerly eCheck), Australia, city-side plus pre-submission**
- Applicants upload PDF, CAD or BIM files and can view them in 2D or 3D. The tool checks them against local code and zoning with "custom rule configurations" per city and returns pass/fail per check with a visual report. Applicants can revise and resubmit. It integrates with CityView, Computronix and Civic Marketplace. Archistar says it is "Built on generative AI, computer vision, and machine learning" — [Archistar AI PreCheck](https://www.archistar.ai/aiprecheck/) (accessed 2026-11)
- Named customers (VENDOR): Burlington, LA County, Burnaby, Cambridge (Ont.), Surrey, Kingston, Cape Coral, Yonkers, Austin. Archistar claims more than 30 cities — [Archistar AI PreCheck](https://www.archistar.ai/aiprecheck/)
- ICC partnership, 24 Jul 2025: the ICC became a "Premier Platinum Reseller", and eCheck uses the ICC Code Connect API for I-Codes content. An 11-city pilot reported faster plan review and greater consistency, but published no figures — [ICC press release 2025-07-24](https://www.iccsafe.org/about/periodicals-and-newsroom/international-code-council-collaborates-with-archistar-to-modernize-permitting-and-accelerate-housing-development)
- Los Angeles wildfire rebuild: beta started 15 Jul 2025 in the City and County of LA, announced by Governor Newsom. The City's beta covered single-family homes in Pacific Palisades and was optional. Steadfast LA paid most of the implementation cost of up to $2M, and LA Rises paid the $200 per-application fee — [Archistar blog](https://www.archistar.ai/blog/echeck-beta-now-live-in-la/); [KNX/Audacy](https://www.audacy.com/knxnews/news/local/la-county-launches-ai-plan-check-to-help-wildfire-survivors); [Westside Current](https://www.westsidecurrent.com/news/la-using-ai-tool-to-help-rebuild-from-palisades-fire/article_6ed3018b-4f6c-4453-a311-a1422f911c08.html)
- Austin has a published "Pre-Check" FAQ for residential projects — [City of Austin FAQ PDF](https://www.austintexas.gov/sites/default/files/files/Development_Services/RES_CityofAustinPre-CheckFAQ.pdf)

**UpCodes, US, designer-side code research and QA/QC**
- Copilot is an AI for code research. Every answer links to the adopted code section it relies on, and it also generates project-specific compliance checklists — [UpCodes Copilot](https://cms-v2.up.codes/features/copilot); [YC launch](https://www.ycombinator.com/launches/Iu3-upcodes-copilot-for-building-codes)
- AI Plan Review launched 10 Jun 2026. Users upload drawings, which are checked against the jurisdiction and code year and also against the specifications. Issues are sorted by severity and category, and each links to the drawing page and the governing code section. The features page still describes access as "early access ... rolling out to select customers" — [UpCodes Plan Review](https://cms-v2.up.codes/features/plan-review); [UpCodes: AI-native plan review](https://cms-v2.up.codes/a/ai-native-plan-review)
- In Mar 2026 UpCodes added a Specifications product with QA/QC "diagnostics". The source is secondary — [Nomic glossary](https://www.nomic.ai/glossary/upcodes)
- I found no product called "UpCodes Diagnostics" as such. Note also that UpCodes already marketed "AI checks BIM models" in 2018 — [Tradeline 2018](https://www.tradelineinc.com/news/2018-7/upcodes-ai-checks-bim-models-code-compliance)

**Symbium, California, "instant" permits through computational law**
- Symbium's core is the proprietary "Complaw" computational law engine. Job postings describe logic programs that translate legal text into "structured, verifiable code" and refer to a Prolog-style rule system, fed by structured property and parcel data — [Symbium comparison page](https://symbium.com/automated-permitting-comparison); [Symbium careers](https://www.symbium.com/careers/software-engineer)
- Bakersfield has used it since April (2025 per the coverage) and approved roughly 500 permits. The city manager said "instant" means "within 10 to 15 minutes". The traditional route remains available. The CEO said the software differs from generative AI such as ChatGPT — [Bakersfield Californian](https://www.bakersfield.com/news/city-debuts-instant-permitting-software/article_ccb00314-cbda-4fdc-952e-6a3b71b09fbc.html); [Yahoo mirror](https://www.yahoo.com/news/articles/city-debuts-instant-permitting-software-010100253.html)
- Wildomar, CA automates residential solar permits through Symbium, with 112 permits issued since launch — [Citizen Portal](https://citizenportal.ai/articles/10890183/California/Riverside-County/Wildomar-City/Wildomar-launches-CivicRec-new-app-and-automated-solar-permitting-officials-report-early-use-metrics)

**Govstream.ai, Seattle area, conversational permitting layer on top of existing systems**
- The seed round of $3.6M was led by 47th Street Partners (Dec 2025), bringing total funding to about $5M. The company describes the product as a "modern permitting layer" that unifies chat, email, voice, plans and policies — [GeekWire 2025](https://geekwire.com/2025/seattle-area-startup-govstream-ai-raises-3-6m-to-improve-city-permitting-processes-using-ai); [GovTech](https://www.govtech.com/biz/ai-permitting-firm-govstream-ai-raises-3-6m-seed-round)
- Bellevue, WA: a design partnership since 2025. Phase 1 gave staff two AI assistants trained on city code, GIS data and permit data, and adoption grew from about 40 to nearly 200 staff. Phase 2 adds an applicant-facing "Research Assistant" (permit path and required documents) and an "Application Assistant" (extracts project data from uploaded plans, fills in forms, scores completeness in real time), plus AI-assisted triage — [Bellevue case study, Aug 2026](https://bellevuewa.gov/sites/default/files/media/pdf_document/2026/dsd-08042026-govstreamai-case-study-early-results.pdf)
- Louisville Metro, KY: Govstream.ai was selected through the city's first AI RFP for a pilot on new residential construction, including multifamily (8 Jan 2026) — [GovTech 2026-01-08](https://www.govtech.com/biz/louisville-govstream-ai-launch-ai-backed-permitting-test); [Louisville press release](https://louisvilleky.gov/news/mayor-greenberg-announces-first-ai-pilot-project-improve-permitting-process)

**Blitz AI (BlitzPermits), US, city-side**
- Blitz screens applications for completeness and checks compliance against IRC, IBC and local amendments, producing reports "in minutes". Naples, FL adopted it alongside CityView — [Journal of Cyber Policy](https://journalofcyberpolicy.com/?p=328335); [CivicTech directory](https://directory.civictech.guide/listing/blitz-ai). Both are secondary sources. I found no primary documentation.

**CodeComply (CivicPlus), US**
- CodeComply uses AI to review floor plans against IBC, IMC, IPC, IRC, ADA, FHA, UFC, state amendments and NFPA. It is sold to designers (design-time and pre-submittal checks) and to building departments inside the CivicPlus permitting platform. CivicPlus calls it "decision-support tools [that] assist qualified reviewers while preserving their professional authority" — [CivicPlus CodeComply](https://www.civicplus.com/community-development/codecomply/); [CivicPlus blog](https://www.civicplus.com/blog/cd/how-ai-is-changing-the-game-for-plan-reviews/)

**Deloitte Smart Permitting Agent for Housing (AWS Marketplace, built on AWS Bedrock)**
- Deloitte markets it as an "agentic AI" product that interprets codes and analyzes CAD drawings. It flags violations at specific locations with regulation references and visual annotation. Deloitte's wider "Smart Permitting" offer covers automated intake, PDF and form extraction, duplicate detection and dashboards — [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-zqttwzsi3rwvq); [Deloitte public sector PDF 2026](https://www.deloitte.com/content/dam/assets-shared/docs/alliances/google/2026/dggca-ai-reimagination-ind-overview-public-sector.pdf). I found no named government deployment.

**PermitFlow, US, applicant-side expediting**
- PermitFlow raised a $54M Series B led by Accel, with Kleiner Perkins, Felicis, Initialized, Altos and YC. Coverage dates the announcement to 2 Dec 2025, while the company blog post is dated 13 Mar 2026. Total funding is about $90.5-91M — [PermitFlow blog](https://www.permitflow.com/blog/permitflow-series-b); [Forbes 2025-12-02](https://www.forbes.com/sites/the-prompt/2025/12/02/this-ai-startup-is-cutting-through-construction-red-tape/); [AlleyWatch Dec 2025](https://www.alleywatch.com/2025/12/permitflow-permit-automation-software-construction-ai-platform-francis-thumpasery/)
- Its agents search municipal websites, prepare and submit applications, and handle licensing and inspections (Forbes). The blog names "AI Agents for Inspections and License Management". Customers named: Amazon, Lennar, IKEA, Toll Brothers, Service Experts — [Forbes](https://www.forbes.com/sites/the-prompt/2025/12/02/this-ai-startup-is-cutting-through-construction-red-tape/); [PermitFlow blog](https://www.permitflow.com/blog/permitflow-series-b)

**GreenLite, New York, "Private Plan Review" plus end-to-end permitting**
- GreenLite raised a $49.5M Series B led by Insight Partners in Sep 2025; total funding is about $86-87M. Its software (LiteTable) ingests plan sets and flags compliance issues using a jurisdiction-specific comment library — [PR Newswire, Sep 2025](https://www.prnewswire.com/news-releases/greenlite-raises-49-5m-series-b-to-advance-the-privatization-of-construction-permitting-with-ai-powered-solutions-302555315.html); [Built In NYC 2025-09-17](https://www.builtinnyc.com/articles/greenlite-announces-49-million-to-expand-ai-platform-20250917)
- Licensed professionals and AI agents manage permits from roadmap to issuance: plan review, submission, responses to authority (AHJ) comments, and tracking. "Agentic software" drafts and tracks responses. GreenLite says it is live in 46 states plus DC and 998 jurisdictions — [GreenLite website](https://greenlite.com/) (accessed 2026-11)

**Pulley, US**
- Pulley says it combines "deep permitting expertise with AI technology" to compress permit timelines and cites "20,000 unique jurisdictions" — [Pulley company page](https://www.withpulley.com/company). The page body could not be retrieved, so no further detail.

**Autodesk**
- Drawing Compliance Review was announced at Autodesk University 2026 as part of Forma Data Management. It will check drawings against customizable rules ("building codes, design standards, and owner requirements") with a human reviewer in charge, and launch is planned for early 2027 — [Cadalyst, AU 2026](https://blog.cadalyst.com/cadmanagement/autodesk-university-2026-what-the-announcements-mean-for-cad-teams); [LearnArchitecture](https://learnarchitecture.net/artificial-intelligence/40465-autodesk-launch-ai-powered-drawing-compliance-review.html)
- The Autodesk Assistant in AutoCAD 2027 (technology preview) compares drawings with CAD standards. One source says it "does not validate calculations, approve designs, verify code compliance" — [Eastern Engineering Group](https://www.easternengineeringgroup.com/autodesk-assistant-autocad-2027-mcp-estandares-cad-2/)
- The older Revit Model Checker is free and rule-based, with custom rules — [MDPI 2025 paper](https://www.mdpi.com/2079-9292/14/11/2146)

**Solibri (Nemetschek), BIM/IFC rule engine**
- Solibri is a classic rule-based model checker for IFC (accessibility, egress and similar). In Dec 2025 Solibri and AcePLP launched a beta Compliance Checker for Singapore's Accessibility Code 2025 on IFC+SG, which links each issue to a code clause — [DailyCADCAM](https://dailycadcam.com/?p=495514)
- In 2026 Solibri moved to tiers (Essential/Advanced/Premium), with an AI Assistant in beta in Premium that helps with navigating results and setting up rules. The source is secondary — [Solibri 25.12 release notes](https://www.solibri.com/articles/solibri-25-12-0-release-notes); [Nomic](https://www.nomic.ai/glossary/solibri)

**Others**
- Firmus: AI design review and constructability risk for contractors (preconstruction, not permitting). It raised a round led by Navitas in May 2024 and was acquired by Nemetschek in Sep 2025, with its team folded into Bluebeam — [Construction Dive 2024-05-15](https://www.constructiondive.com/press-release/20240515-firmus-raises-new-round-of-financing-for-pre-construction-ai-risk-managemen); [Pulse2](https://pulse2.com/firmus-pre-construction-ai-design-review-and-risk-analysis-company-raises-funding)
- Consigli (Oslo): "The Autonomous Engineer", an AI agent for early design (space planning, MEP loads, Level 3 BIM models). AECOM acquired it in Nov 2025; the reported $390M deal value is unconfirmed — [Smart Water Magazine](https://smartwatermagazine.com/news/smart-water-magazine/aecom-acquires-norwegian-ai-startup-consigli-390-million); [StreamBIM](https://streambim.com/?p=2164)
- Archie (Archie Knows, Oslo): an AI copilot for Norwegian building regulations (TEK17) and project documents that also automates compliance checks. It integrates with Revit, ArchiCAD and BIM 360 — [archieknows.com](https://www.archieknows.com/)
- Northspyre: development management and cost software. "Northspyre AI" (Mar 2024) targets scope gaps in bids, not permits — [BusinessWire 2024-03-05](https://www.businesswire.com/news/home/20240305365651/en/Northspyre-Unveils-Northspyre-AI-Including-Industry-First-Generative-AI-Tool-for-Bidding-Process-To-Drive-Down-Development-Costs)
- Blueprints AI (Santa Monica) generates "permit-ready" construction drawings from a sketch or PDF. Licensed professionals still review and seal them — [TechCrunch 2026-10-12](https://techcrunch.com/2026/10/12/this-ai-startup-says-it-can-generate-permit-ready-blueprints-in-minutes/)
- Other smaller tools (not researched in depth): permittable.ai, PlanChecker.ai, Blueplan, Permitify, InspectMind, GovWell — [permittable](https://www.permittable.ai/); [Barchart/PlanChecker](https://www.barchart.com/story/news/32574324/planchecker-ai-launches-ai-powered-platform-to-transform-plan-review-and-permit-approvals); [GovWell](https://govwell.com/resources/how-ai-plan-review-software-is-reshaping-community-development)

### Inferences
- The products that cities actually deploy (CivCheck, Archistar, Symbium, Govstream) focus on small residential work (single-family homes, ADUs, middle housing, solar, tree permits). Complex buildings remain human territory.
- Consolidation is underway. Clariti bought CivCheck, Nemetschek bought Firmus, AECOM bought Consigli, and ICC resells Archistar. Plan-check AI is becoming a module inside permitting platforms (Clariti, CivicPlus, CityView) rather than a standalone product.
- There is a business-model split. City-licensed tools (CivCheck, Archistar, Blitz) compete with private-review and expediting services (GreenLite, PermitFlow, Pulley) that work on the applicant side, in GreenLite's case using legal private plan review authority.

### Gaps
- Pulley: no detail on product, funding or architecture (page body not retrievable).
- Bentley: no evidence of an AI code-checking or plan-review product for permits.
- Blitz AI: no primary vendor documentation found.
- No product named "UpCodes Diagnostics" was found as a standalone item.
- Denver's contract details came from snippets only (Denverite page returned 403).

---

## 2. Agent and multi-agent architectures and workflow coverage

### Takeaway
Explicit "agentic" language comes mainly from applicant-side services (PermitFlow, GreenLite) and from Deloitte's Smart Permitting Agent. City-side tools describe a hybrid pipeline: AI or LLM extraction from PDFs into structured data, then deterministic rule checks (CivCheck, Symbium, Solibri), or LLM assistants grounded on city code and GIS data (Govstream; essentially RAG). No vendor publishes a detailed multi-agent design. Coverage is strongest for pre-submission completeness and simple code checks. Drafting comment letters and responses appears only at GreenLite (responses to AHJ comments) and in Bellevue (staff draft answers with citations).

### Cited Findings
- **CivCheck architecture (INDEPENDENT, Seattle):** "CivCheck uses multiple AI techniques to read content from application documents such as PDF plan sets and assemble that content into structured data. CivCheck performs deterministic checks on that data..." and "the core logic of the checks is deterministic, not probabilistic." Checks are configured by the vendor per city (34 completeness checks and 67 compliance checks in Seattle, each mapped to a code section, e.g. SMC 23.44.014 and SRC R302.1) — [Seattle CivCheck PoV report 2026, p.4 and p.11, Appendix A](https://www.seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf)
- CivCheck vendor claims: rule updates take 2-3 minutes plus about 24 hours of testing, and when the AI is uncertain it asks the user for input instead of guessing — [Clariti CivCheck page](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software)
- **Symbium:** symbolic logic programming (Prolog-style) over legal text plus parcel data. The CEO explicitly distances it from generative AI. Some press nevertheless describes it as "machine-learning models trained on local codes", so descriptions conflict — [Symbium careers](https://symbium.com/careers/senior-software-engineer); [Pulse](https://www.pulse.bot/proptech/news/ai-powered-permitting-takes-off-in-bakersfield-with-symbium-partnership-682a6551-c4cd-4406-90ea-6970e14459c5/)
- **Govstream.ai (Bellevue):** two assistant roles, "Research Assistant" and "Application Assistant", grounded in "the city's own codes, policies, GIS data, and configured business rules". This is LLM plus retrieval plus configured rules. Staff refine rule configurations in "tuning rounds" — [Bellevue case study 2026](https://bellevuewa.gov/sites/default/files/media/pdf_document/2026/dsd-08042026-govstreamai-case-study-early-results.pdf)
- **Archistar:** "generative AI, computer vision, and machine learning" plus per-city rule configurations, with I-Codes content via the ICC Code Connect API. No detailed architecture is published — [Archistar](https://www.archistar.ai/aiprecheck/); [ICC 2025-07-24](https://www.iccsafe.org/about/periodicals-and-newsroom/international-code-council-collaborates-with-archistar-to-modernize-permitting-and-accelerate-housing-development)
- **UpCodes:** an LLM copilot over a structured, adopted-code database with section-level citations (code RAG), and an AI plan review that links findings to code sections — [UpCodes Copilot](https://cms-v2.up.codes/features/copilot); [UpCodes Plan Review](https://cms-v2.up.codes/features/plan-review)
- **Deloitte:** explicitly "agentic AI" on AWS Bedrock. It is described as an "applicant and reviewer assistant" that "accelerates end-to-end permit decisions", covering intake, extraction, code interpretation and CAD analysis — [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-zqttwzsi3rwvq); [Deloitte PDF](https://www.deloitte.com/content/dam/assets-shared/docs/alliances/google/2026/dggca-ai-reimagination-ind-overview-public-sector.pdf)
- **PermitFlow:** "AI agents" that research municipal requirements, prepare and submit applications, and handle inspections and licensing, drawing on a proprietary dataset of more than 12M permit data points — [Forbes 2025-12-02](https://www.forbes.com/sites/the-prompt/2025/12/02/this-ai-startup-is-cutting-through-construction-red-tape/); [PermitFlow blog](https://www.permitflow.com/blog/permitflow-series-b)
- **GreenLite:** "agentic software" drafts and tracks responses to AHJ comments, and the AI "learns from expert decisions" — [GreenLite](https://greenlite.com/)
- **Consigli:** calls its product "The Autonomous Engineer", an agent for design rather than permits — [StreamBIM](https://streambim.com/?p=2164)

**Step coverage (based on public sources):**

| Step | Products |
|---|---|
| Pre-submission completeness/intake | CivCheck, Govstream, Archistar, Blitz, GreenLite (intake), Deloitte |
| Code/zoning check | CivCheck, Archistar, Blitz, CodeComply, UpCodes, Solibri (IFC), Symbium (rules), Deloitte, Autodesk (2027) |
| Drafting comments/corrections | GreenLite (responses to AHJ comments); Bellevue staff drafts (Q&A, not corrections); CivCheck/Archistar produce findings reports, not formal letters |
| Applicant communication | Govstream (chat/email/voice), CivCheck portal, PermitFlow, GreenLite |
| Resubmission review | Archistar (revise and resubmit loop); otherwise not documented |
| Automatic issuance | Symbium only (Bakersfield, simple permits) |

### Inferences
- In practice the dominant pattern is "LLM/vision for extraction, then deterministic rules for the decision". This is an explainability and responsible-AI choice. Seattle explicitly selected CivCheck in part because its check logic is deterministic.
- "Agentic" is mainly marketing language from applicant-side services and consultancies. City deployments use assistants with tightly scoped tasks.

### Gaps
- No vendor publishes its model choice (which LLM), orchestration, or multi-agent design.
- No public source documents automated drafting of formal correction letters by city-side tools.
- No public evaluation of AI-supported resubmission review.

---

## 3. Explainability and human review; does anyone decide autonomously?

### Takeaway
Almost every vendor and city positions AI as advisory. Staff make the final decision (CivCheck, Archistar, Toronto, Bellevue, CodeComply, GreenLite, Autodesk). Explainability comes through code-section citations, highlighted plan locations and calculation breakdowns. The only documented autonomous approval is Symbium in Bakersfield (simple permits, deterministic rules, traditional route still available).

### Cited Findings
- CivCheck FAQ: "AI should never make a decision directly." Staff approve every AI interpretation, and applicants and staff can override results. Outputs include code links with plain-language summaries, calculation breakdowns and highlighted plan data — [Clariti CivCheck page](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software)
- Seattle (INDEPENDENT): "at every step, users can see the logic behind a suggestion, override automated suggestions, add clarifications, and make independent determinations." In the pilot, reviewers clicked "approve" or "needs correction" for each check — [Seattle report, p.9 and p.11](https://www.seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf)
- Toronto: outputs are "advisory only"; staff independently review every application; the tool "does not approve" — [Toronto AI Register](https://www.toronto.ca/city-government/data-research-maps/ai-register/building-permit-application-precheck/)
- Bellevue: staff "review these results, make edits as needed, and finalize responses". Drafts come with citations ("citation-backed draft responses in under a minute") — [Bellevue case study](https://bellevuewa.gov/sites/default/files/media/pdf_document/2026/dsd-08042026-govstreamai-case-study-early-results.pdf)
- Archistar says AI PreCheck does not replace professional judgment or final approval authority. Cambridge (Ont.) says results "may contain errors or inaccuracies" and are for information only — [Archistar](https://www.archistar.ai/aiprecheck/ai-plan-review/); [Cambridge AI PreCheck](https://www.cambridge.ca/business-building-development/building-planning/ai-precheck/)
- GreenLite: "The accountability layer is always human". It has in-house stamp and license authority, and findings cite code sections and plan locations — [GreenLite](https://greenlite.com/)
- UpCodes: each finding links to the drawing page and the code section — [UpCodes Plan Review](https://cms-v2.up.codes/features/plan-review)
- Solibri/AcePLP: each issue is linked to a code clause — [DailyCADCAM](https://dailycadcam.com/?p=495514)
- **Autonomous:** Symbium says "permit applications submitted through Symbium are instantly approved for issuance". Bakersfield has approved about 500 permits, and the CEO claimed it is "always 100% accurate" (unverified) — [Symbium](https://symbium.com/automated-permitting-comparison); [Bakersfield Californian](https://www.bakersfield.com/news/city-debuts-instant-permitting-software/article_ccb00314-cbda-4fdc-952e-6a3b71b09fbc.html)
- Blueprints AI: licensed professionals review and seal the drawings before submission — [TechCrunch 2026-10-12](https://techcrunch.com/2026/10/12/this-ai-startup-says-it-can-generate-permit-ready-blueprints-in-minutes/)

### Inferences
- Autonomous decisions appear only where the rules can be fully formalized and the scope is narrow (solar, simple residential). That is a symbolic rule engine, not an LLM.
- Applicants want an override path and human contact. Seattle's applicant interviews stress "access to a person that can help us override in unique cases".

### Gaps
- No public source describes how applicants can contest an AI report (Toronto states explicitly that this is not addressed).
- No legal framework or case law on liability; see section 5.

---

## 4. BIM/IFC versus 2D PDF

### Takeaway
City-side permitting AI is almost entirely 2D PDF-based, because that is what applicants submit. BIM/IFC checking remains the domain of rule-based model checkers (Solibri, Revit Model Checker), designer-side tools, and specific government programs (Singapore IFC+SG). Archistar is the only city-side tool that claims to accept PDF, CAD and BIM.

### Cited Findings
- CivCheck: "PDF-native", no BIM required — [Clariti](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software). Seattle reviewers complained that it "fails to recognize text in images" — [Seattle report, App. D](https://www.seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf)
- Archistar: accepts PDF, CAD or BIM, with 2D/3D viewing — [Archistar](https://www.archistar.ai/aiprecheck/)
- Deloitte: analyzes CAD drawings — [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-zqttwzsi3rwvq)
- UpCodes Plan Review and CodeComply: drawings and floor plans (PDF) — [UpCodes](https://cms-v2.up.codes/features/plan-review); [CivicPlus](https://www.civicplus.com/community-development/codecomply/)
- Solibri: IFC (plus BCF and COBie); the Singapore checker uses IFC+SG — [DailyCADCAM](https://dailycadcam.com/?p=495514). Academic work stresses that Solibri results "depend on model preparation and IFC exchange quality" — [MDPI 2025](https://www.mdpi.com/2079-9292/14/11/2146)
- Archie integrates with Revit, ArchiCAD and BIM 360 — [archieknows.com](https://www.archieknows.com/)
- Autodesk Drawing Compliance Review targets drawings in Forma Data Management — [Cadalyst](https://blog.cadalyst.com/cadmanagement/autodesk-university-2026-what-the-announcements-mean-for-cad-teams)

### Inferences
- For a Dutch or European context, where BIM and IFC are more common in large projects, PDF-based tools fit residential permit applications, while IFC rule engines fit large projects. Hybrid approaches (Archistar) are rare.

### Gaps
- No published accuracy comparison between PDF-based and IFC-based checking in a permitting context.

---

## 5. Reported metrics, adoption, criticism and failures

### Takeaway
The only rigorous independent evaluation found is Seattle's CivCheck report (2026). It found 87% of in-scope intake errors detected and 91.7% agreement on plan review checks, but also a 6.4% "missed correction" rate, and it recommended only a limited completeness pilot. Most other figures are vendor claims or vendor-produced reports with small samples (Honolulu: 19 permits). Main criticisms: codes are hard to formalize, coverage is limited, integration is missing, there is a risk of "another hurdle", liability is unclear, and hallucinations occur in LLM-based approaches.

### Cited Findings

**INDEPENDENT: Seattle CivCheck Proof of Value (Mar-Oct 2025, report 2026)** — [Seattle report](https://www.seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf); [Seattle Innovation Hub 2026-06-17](https://innovation-hub.seattle.gov/2026/06/17/ai-construction-permitting-seattle-civcheck-study/)
- Scope: middle housing under the Seattle Residential Code. Intake: 29 historical applications, 34 checks. Plan review: 57 active applications, 67 checks. CivCheck staff loaded the data; there was no Accela integration.
- Intake: 90 rejection reasons, of which 35 were outside the configured scope. 48 of the 55 in-scope reasons (87%) were found and 7 missed. CivCheck flagged 4 extra applications for a topographic survey where staff had used discretion to waive it.
- Plan review: 1,262 checks performed. Overall accuracy 91.7%. "False positive" (missed correction) rate 6.4%; "false negative" (unnecessary flag) rate 1.9%. Reviewers gave feedback on 6.8% of checks.
- Modeled impact: median intake time could fall from 54.5 days to 29 days (pilot configuration) or 8 days (full configuration), "up to a 46-day reduction". Plan review: 3.72 to 3.39 or 2.72 correction cycles. These are scenario estimates, not measurements.
- Recommendation: "Scale to larger scale production pilot", starting with completeness screening only. Compliance checks "need careful expectation-setting".
- Limitations: "it is not clear how much of the Land Use Code and Seattle Residential Code requirements could be accurately assessed with automated checks", and "our current codes, requirements, and processes do not always translate easily" into unambiguous logic. The pilot ran under a risk acceptance agreement because CivCheck lacked third-party certifications, and a new security and AI review is needed. Staff reported a clunky interface and that the tool "fails to recognize text in images". Structural reviewers were skeptical. Applicants feared a tool that becomes "just another hurdle" and expressed "low tolerance for inaccuracy".
- Staff survey (14): 71% had a more favorable view of AI after the pilot; 86% agreed with at least one business-value statement.

**Bellevue / Govstream.ai (city case study, co-branded with the vendor, Aug 2026)** — [Bellevue PDF](https://bellevuewa.gov/sites/default/files/media/pdf_document/2026/dsd-08042026-govstreamai-case-study-early-results.pdf)
- Back test on 276 residential permits from 2025: complete on first submission rose from 22% to 67%, and 96% of required documents were correctly identified. Tree permits (265): 40% to 76%, with 86% of documents identified (74% in round 1).
- Staff estimate 152 hours saved in one month (June-July 2026) on pre-application questions, toward a 30% goal. Note: this is a replay or back test with the vendor, not a live controlled trial.

**Honolulu / CivCheck (vendor-produced performance report)** — [Honolulu DPP](https://www.honolulu.gov/dpp/city-earns-national-ai-50-award-for-innovative-permit-review-technology/); [Clariti case](https://www.claritisoftware.com/honolulu-cuts-review-times-by-70-percent-with-civchecks-ai-plan-review-software)
- 19 CivCheck permits compared with 17 non-CivCheck permits (Q1 2026). Cycles fell from 3.4 to 1.4 (-58%), corrections from 23.5 to 7.7 (-67%), and time to decision from 73 to 32.5 days (-55%). A "70%" review-time reduction was reported for the pilot. Public launch was 8 Dec 2025. Small sample, no matched control; the city director called it a "relatively small sample" (per search snippet). The city won the "AI 50" award from the Center for Public Sector AI (e.Republic).

**Vendor claims (unverified)**
- CivCheck: 98%+ accuracy, cycles cut from 3-6 to 1-2, "up to 90% faster", residential review from 90 to 15 minutes. The page itself is inconsistent (Honolulu 70% vs "as much as 90%") — [Clariti](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software)
- Clariti projects 25,200 staff hours saved per year in Seattle if scaled (a model, not a measurement) — [Clariti Seattle case](https://www.claritisoftware.com/resources/case-studies/how-seattle-used-ai-to-address-the-root-cause-of-permit-delays)
- Archistar: up to 55% fewer review cycles; 54% less processing time (LA County); about 50% time savings on zoning (Austin); first-submission quality of 90% — [Archistar](https://www.archistar.ai/aiprecheck/)
- UpCodes: Copilot scored "93% weighted accuracy" on 43 questions judged by experts, "more than 2x" generic AI (UpCodes' own study). Plan Review covered more than 1,300 plan sets with more than 180,000 "potential issues" (Oct 2026) — [UpCodes AI](https://cms-v2.up.codes/features/ai); [Construction Dive press release 2026-10-13](https://www.constructiondive.com/press-release/20261013-upcodes-ai-reviews-1300-plan-sets-identifying-more-than-180000-potenti/)
- PermitFlow: timelines up to 60% shorter, about 90% less workload, 5x ROI, more than $20B in construction value — [PermitFlow](https://www.permitflow.com/blog/permitflow-series-b)
- GreenLite: 45 days on average to issuance, 0.5 resubmissions vs an industry average of 3.2, 95% passing intake on first submission. The page is internally inconsistent about the industry baseline (118 days vs "90+") — [GreenLite](https://greenlite.com/)
- Symbium: "100% accurate" (CEO) and about 60 CA cities — [Bakersfield Californian](https://www.bakersfield.com/news/city-debuts-instant-permitting-software/article_ccb00314-cbda-4fdc-952e-6a3b71b09fbc.html)

**Adoption and market**
- An industry article estimates about 10-15 US cities with active AI plan review as of June 2026. The source is a blog of moderate reliability — [AI Home Building](https://aihomebuilding.com/articles/ai-permit-review-city-builder-bottleneck)
- Harris County (TX) approved an AI permitting initiative in Nov 2025 (per search snippet; not verified in a primary source).
- Stateline (20 Aug 2026) reports on Seattle with roughly a 50% cut in intake days and a 35% drop in correction cycles, and says Seattle was not yet ready to adopt the tool fully. The page itself returned HTTP 403, so these figures are search snippets only — [Stateline 2026-08-20](https://stateline.org/2026/08/20/cities-turn-to-ai-to-speed-housing-permitting/)

**Criticism and concerns**
- Seattle's own conclusion: the pilot showed "the City has more work to do to make our requirements and processes clearer and less subjective" — [Seattle Innovation Hub](https://innovation-hub.seattle.gov/2026/06/17/ai-construction-permitting-seattle-civcheck-study/)
- Liability: as of mid-2026 no published court decision has addressed liability for a deficiency an AI review missed, and contracts rarely cover indemnification or audit rights. Hallucinated rules remain a core failure mode in the 2026 literature. No jurisdiction formally credits a private AI pre-check. The source is a vendor blog (Lintel) — [Lintel: What is AI plan review](https://www.uselintel.com/blog/ai-plan-review)
- Practitioners worry that AI "will just confidently replicate those non-compliant errors" and that oversight requires "someone competent" — [Building Code Forum](https://www.thebuildingcodeforum.com/forum/threads/what-will-you-do-when-ai-does-begin-to-work-well-for-code-compliance.39304/)
- A Utah planning commission (Feb 2026) noted concerns about "dilution of quality" and the need for human verification — [Utah PMN minutes](https://www.utah.gov/pmn/files/1401081.pdf)
- Autodesk's own AutoCAD assistant does not verify code compliance (see section 1) — [Eastern Engineering Group](https://www.easternengineeringgroup.com/autodesk-assistant-autocad-2027-mcp-estandares-cad-2/)

### Inferences
- Independent evidence supports gains in completeness and intake (fewer incomplete applications, fewer intake cycles) much more strongly than gains in substantive code review. Plan review only speeds up if the bottleneck review is shortened (Seattle: on average 6 review teams working in parallel across 3+ cycles).
- A missed-correction rate of about 6% in pre-screening is acceptable as advisory feedback, but would be a reason in a legal decision context not to let AI decide autonomously.
- Code formalization (unambiguous "trigger logic") and integration with the permitting system (Accela, GIS) are preconditions that cities themselves must deliver.

### Gaps
- No independent audit of Archistar (the ICC 11-city pilot published no figures), Symbium, Blitz, CodeComply, PermitFlow or GreenLite.
- No documented incident in which AI missed a safety-relevant violation that was then built.
- Stateline and Denverite were not directly accessible (403). Their figures come from search snippets only.
