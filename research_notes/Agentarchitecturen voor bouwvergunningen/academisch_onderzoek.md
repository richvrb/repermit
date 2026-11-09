# Academic and applied research on LLM agents and multi-agent systems for automated code compliance checking (ACC) in building permitting, plan review and BIM/IFC (2022–2026)

Research date: 2026-11-07. Notes in English. Peer-review status is marked per item: **[PR]** = peer-reviewed journal or conference, **[PP]** = preprint (arXiv/EasyChair), **[?]** = status not verified. Where a number or detail comes only from a search-engine snippet and not from the paper page, it is marked "(snippet only)".

**Background only (pre-2022, rule-based ACC):** Solibri, CORENET e-PlanCheck (Singapore), SMARTcodes and the classic four-stage ACC model of Eastman et al. (2009): (1) rule interpretation, (2) BIM data preparation, (3) rule execution, (4) reporting. Most LLM papers below still use this four-stage frame. See [Ying & Sacks 2024](https://easychair.org/publications/preprint/k2PJ/open) Section 2.1. Background reviews: Amor & Dimyadi (2021), "The promise of automated compliance checking", *Developments in the Built Environment* 5, 100039, cited there. A 2026 systematic review in *Building Research & Information* calls the FOL/SWRL/SPARQL era (incl. CORENET e-PlanCheck) "Phase I: The Deterministic Era". It says RASE and LegalRuleML gave structured representations but ran into a knowledge-acquisition bottleneck from manual rule extraction (snippet only): [A systematic review of methods for interpreting building code regulations in automated compliance systems, BRI 2026](https://www.tandfonline.com/doi/full/10.1080/09613218.2026.2637965).

---

## 1. Which papers propose LLM-agent or multi-agent architectures for building code compliance, what are the agents and how are they orchestrated?

### Takeaway
Most published "agentic" ACC systems are either (a) a single ReAct-style LLM agent with BIM tools (Ying & Sacks 2024), (b) fixed pipelines with role-specialized LLM steps (parser → reviewer → critic; extraction → rule → compliance engine), or (c) multi-agent setups with trigger-based arbitration or verifier-driven repair loops. True planner-plus-specialist multi-agent systems for *building permit* checking against BIM are still rare. The strongest multi-agent results come from adjacent domains (structural design) where a deterministic external verifier closes the loop.

### Cited Findings

**A. Single-agent / tool-using LLM for BIM compliance**
- **Ying, H. & Sacks, R. (2024). "From Automatic to Autonomous: A Large Language Model-driven Approach for Generic Building Compliance Checking."** Proc. CIB W78 2024, 1–3 Oct 2024, Marrakesh. Also EasyChair Preprint 15364 (5 Nov 2024). Technion. [PR, conference] — [EasyChair](https://easychair.org/publications/preprint/k2PJ/open)
  - Three LLM modules in a workflow: (1) *design requirement querying* (LLM + RAG over the code document; text, tables and figures embedded separately, with tables and figures first summarized/captioned by the LLM; top-5 chunks by cosine similarity); (2) *requirement checking* as a **ReAct agent** (Thought/Action/Action Input/Observation loop with a system prompt, tools and agent memory); (3) *design revision* (LLM + BIM manipulation tools). The user is in the loop at each module.
  - Prototype "RevitCopilot" (Revit plugin, C#/Python, GPT-4o, OpenAI text-embedding-3-small, Unstructured for PDF partitioning). Tools: `extractBuildingElement_property` (Revit API → JSON), `BIMJSONQuery` (natural-language query over that JSON), `adjustBuildingElementThickness`.
  - Experiment: a two-level duplex Revit model with 20 floor elements (4 slabs on ground, 2 deliberately made non-compliant), checked against IBC 2009 Chapter 19 (min. 3.5 in / 89 mm slab-on-ground). The agent correctly identified the 2 passing and 2 failing slabs in two ReAct cycles. The RAG query needed **two conversational rounds**, because the first round returned irrelevant concrete topics.
  - Authors' stated plan: upgrade the checking module "to a multi-agent system to address complex requirements".
- **Madireddy, S., Gao, L., Din, Z., Kim, K., Senouci, A., Han, Z., Zhang, Y. (2025). "Large Language Model-Driven Code Compliance Checking in Building Information Modeling."** arXiv:2506.20551 (25 Jun 2025), Univ. of Houston / UT Austin. [PP] — [arXiv](https://arxiv.org/abs/2506.20551)
  - Fixed pipeline: Input (BIM + regulation text) → LLM writes **IronPython scripts for the Revit 2024 API** → scripts run in Revit → report with recommendations. Script errors are fed back to the LLM. Execution is manual (copy-paste into Revit's Python shell). 12 rules (IRC, IMC, etc.), 2 case studies (a single-family house and an office building with 8 rules).
  - Script "success rate" on Rules 1–5: Grok 76.7%, DeepSeek 33.3%, Claude Sonnet 3.5 23.7%, Perplexity 14.4%, ChatGPT 4.0 13.2%, Gemini 9.7%, Llama 3.1-405B 0%, Copilot 0%. No precision/recall of violation detection is reported. Future work: an LLM agent that calls the Revit API directly.
- **Wan, H., Xu, W., Rosenberg, M., Zhang, J., Siddika, A. (2025). "Automatic Building Code Review: A Case Study."** arXiv:2510.02634 (3 Oct 2025), PNNL (PNNL-SA-216238). [PP] — [arXiv](https://arxiv.org/abs/2510.02634)
  - Agent-driven framework: LLM agents extract geometry, schedules and system attributes from heterogeneous BIM/files. Verification uses (1) **direct API calls to the DOE COMcheck engine** ("deterministic and audit-ready outputs") via an **MCP agent pipeline**, and (2) RAG reasoning over provisions where coverage is incomplete or ambiguous. MCP was found more rigorous and reliable than RAG reasoning. GPT-4o gave the best efficiency/stability, while smaller models were inconsistent or failed. Use cases: ASHRAE 90.1-2022 lighting allowances; geometric attributes (area, tilt, insulation). Target users: building officials in resource-constrained/rural jurisdictions.

**B. Role-specialized pipelines and multi-agent arbitration**
- **Yin, H., Chen, X., Zou, Y., Wu, L. (2026). "Retrieval-Augmented Generation and Multi-Agent Arbitration for Construction Code Compliance in AEC."** Proc. 43rd ISARC, Singapore, pp. 1824–1831, DOI 10.22260/ISARC2026/0233. [PR, conference] — [IAARC](http://www.iaarc.org/publications/2026_proceedings_of_the_43rd_isarc_singapore/retrieval_augmented_generation_and_multi_agent_arbitration_for_construction_code_compliance_in_aec.html)
  - Clause-centric RAG treated as "auditable evidence discovery". An **evidence-bounded selection contract** means outputs may only cite clause IDs from the retrieved candidate set, and evidence spans must match retrieved text so they can be mechanically validated. A **trigger-based multi-agent orchestrator** runs several "expert" agents, and an **arbiter** is invoked only when the experts disagree or a validation flag fires. Output: a "clause package" linking design decisions to clauses. Code and data are on GitHub.
- **Lu, X.Y. & Zhu, J.W. (2026). "A Role-Specialized Retrieval-Augmented Generation Framework for Automated Compliance Checking in Structural Engineering."** *Advanced Electromagnetics* 15(3), 10917–10925, DOI 10.7716/aem.v15i3.4301. [PR, but in an off-topic journal, so treat with caution] — [AEM](https://www.aemjournal.org/index.php/AEM/article/view/4301)
  - Roles: a **deterministic Parser**, a **Reviewer** (LLM guided by an "Equilibrium Rule" prompt) and a **Critic** (LLM, structured verdict). Fixed pipeline. Framed as decision support, "not a fully autonomous approval engine".
- **Gautam, S., Acharya, D., Kleeman, A., Foster, S. (2026). "Towards an automated AI-based framework for floor plan compliance checks for residential buildings."** arXiv:2607.00015 (RMIT). [PP; page mentions *Building and Environment*, not verified] — [arXiv](https://arxiv.org/html/2607.00015v1)
  - Three engines: a **Data Extraction Engine** (PDF/image → OCR → Mask R-CNN/U-Net detection and segmentation → JSON building model + room adjacency graph), a **Rule Engine** (LLM parses Australian regulations such as BADS, SEPP 65 and SPP 7.3 into JSON rules) and a **Compliance Check Engine** (PASS/FAIL + explanation + remediation). Conceptual paper.

**C. Multi-agent with an external deterministic verifier (adjacent domain: structural design)**
- **Chen & Bao (2025). "Multi-agent large language model framework for code-compliant automated design of reinforced concrete structures."** *Automation in Construction* 177. [PR] — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0926580525003711) (abstract not retrievable, 403; details from search snippet only): dedicated agents for query classification, parameter extraction, structural analysis and reinforcement design, which cross-check each other. The goal is "interpretability and verifiability".
- **Luo, J., Lin, W., Lin, Y., Wei, Q., Guo, W. (2026). "Verification-driven closed-loop multi-agent large language model framework for code-compliant structural design."** arXiv:2608.07978 (8 Aug 2026). [PP] — [arXiv](https://arxiv.org/abs/2608.07978)
  - An external **three-layer finite-element verifier** feeds back into a closed repair loop, with no reliance on LLM self-correction. Node 1 turns code violations into hard repair constraints. Node 2 turns a 4-dimensional quality score into soft constraints. A RAG code base makes each violation traceable to a clause. 44-case benchmark: code compliance went from **56.8% → 98.6%**, composite score 63.8 → 71.4 (p < 0.000001). Compliance did not differ detectably between the two backbone LLMs, so the authors attribute the gain to the verifier rather than the LLM.

**D. Graph-based reasoning / KG + agents**
- **Xiao, Z., Koh, P.T., Ma, J., Cheng, J.C.P. (2026). "Automating Geometry-Intensive Compliance Checking in BIM: Graph-Based Semantic Reasoning Framework" (SGR-BIM).** arXiv:2606.12065, journal ref. *Automation in Construction* 189 (2026) 107038, DOI 10.1016/j.autcon.2026.107038. [PR] — [arXiv](https://arxiv.org/abs/2606.12065)
  - A cross-modal knowledge graph linking user intent, regulatory semantics and IFC geometry, for multi-hop and spatial reasoning "without rigid hard-coding". Evaluated on **679 expert-verified fire-safety queries: 84.3% accuracy, +8.6% over "enhanced-tool single-agent baselines"** (absolute vs relative not stated on the abstract page). Categorized cs.MA (multi-agent), but agent roles are not described on the abstract page.

**E. Other related LLM/agent work (less detail verified)**
- **Zheng, Nabaei, Asadi, Campbell, Heydarian (2025). "A Vision-Language Model Agent for Building Code Compliance."** ACM BuildSys 2025 (12th ACM Int. Conf. on Systems for Energy-Efficient Buildings), Univ. of Virginia. [PR] — [PDF](https://www.cs.virginia.edu/~bjc8c/papers/zheng25inspection.pdf) (snippet only): VLM agent + RAG over IRC 2021, IPC 2021 and Virginia Residential Code 2021. It works from inspection photos, not BIM. **~96.25% average similarity to human-written inspection reports** across 4 building components (a similarity metric, not a compliance accuracy).
- **Nawari & Lawal (2026)**, *Buildings* 16(13) 2637, DOI 10.3390/buildings16132637, "An agentic AI system for roof design compliance using computer vision, retrieval-augmented generation and large language models". Multi-agent. Vision and reasoning components were evaluated separately, not end to end, and only for Florida (snippet only) — [citedrive](https://www.citedrive.com/en/discovery/an-agentic-ai-system-for-roof-design-compliance-using-computer-vision-retrieval-augmented-generation-and-large-language-models/)
- **Han et al. (2025), "AI BIM coordinator for non-expert interaction in building design using LLM-driven multi-agent systems"**, *Automation in Construction* 180. A multi-agent BIM assistant (clash detection, document generation, BIM code generation). It is not primarily code compliance (snippet only) — [ResearchGate](https://www.researchgate.net/publication/398170327_AI_BIM_coordinator_for_non-expert_interaction_in_building_design_using_LLM-driven_multi-agent_systems)
- **Text2BIM (Du et al., 2024)**: a multi-agent framework that generates BIM from text with iterative rule checking (generation, not permit checking; snippet only).
- **Zhang, L., Le, B., Akhtar, N., Ngo, T. (2025). "Automated Facility Enumeration for Building Compliance Checking using Door Detection and Large Language Models."** arXiv:2509.17283. [PP] Door detection + CoT LLM reasoning to count facilities (e.g. WCs) against statutory requirements. The abstract gives no metrics — [arXiv](https://arxiv.org/abs/2509.17283)
- "Leveraging large language models for BIM-based automated compliance checking", *Automation in Construction* 2025 (pii S0926580525007472). [PR] Snippet only, page 403: converts the building code into clause-segmented JSON and lets the LLM perform the check and write the report directly, without translating rules to code. The authors suggest a multi-agent extension in which a rule-execution agent requests missing data from a model-preparation agent — [ScienceDirect](https://sciencedirect.com/science/article/pii/S0926580525007472). Authors not verified.
- Related-work list in Gautam et al. 2026 (titles mostly not given there): Yang & Zhang (2024) prompt-based GPT with expert feedback; Yang et al. (2025) LLM + RAG for interpretation and non-compliance detection; Uhm et al. (2025) RAG for traceable regulatory assessment; Chen et al. (2024) BIM ontology + LLM; Hussain et al. (2026) hybrid geometry + LLM fire inspection; Ayanzadeh & Oates (2026) agentic floor-plan parsing (arXiv:2604.23970) — [arXiv 2607.00015](https://arxiv.org/html/2607.00015v1)

### Inferences
- Orchestration patterns found: (1) **single ReAct agent with tools** (Ying & Sacks); (2) **fixed linear pipeline with role-specialized LLM steps** (Madireddy; Lu & Zhu; Gautam); (3) **conditional arbitration**, where an arbiter runs only on disagreement (Yin et al. ISARC 2026); (4) **verifier-driven closed loop** (Luo et al.); (5) **LLM agent calling a certified deterministic engine via MCP** (Wan et al./COMcheck). No found paper uses open-ended debate between agents as the main decision mechanism. Arbitration is the closest.
- The trend between 2024 and 2026 is away from "LLM decides" towards "LLM orchestrates and translates, a deterministic engine decides".

### Gaps
- No paper found with a full end-to-end multi-agent system (planner + rule interpretation + IFC query + checking + report agents) evaluated on real permit applications at a municipality.
- Full texts of Chen & Bao 2025, the AiC 2025 "Leveraging LLMs for BIM-based ACC" paper, BuildThemis and SGR-BIM agent roles could not be retrieved (paywall / 403).

---

## 2. How do they combine LLMs with deterministic rule engines, semantic rule languages (LegalRuleML, SWRL, KBimCode, RASE, mvdXML, IDS) or knowledge graphs? Where do they explicitly NOT use the LLM?

### Takeaway
LLMs are mainly used as **translators** (text → LegalRuleML, JSON rules, function compositions, Python/IronPython scripts, intermediate representations) and as **orchestrators**. Final pass/fail is increasingly delegated to deterministic code, certified engines (COMcheck), FE verifiers or KG reasoning. No found paper uses LLMs to generate IDS or mvdXML, and none uses KBimCode with LLMs. RASE + LLM exists only within the EU ACCORD project.

### Cited Findings
- **LegalRuleML:** Fuchs, S., Witbrock, M., Dimyadi, J., Amor, R. (2024). "Using Large Language Models for the Interpretation of Building Regulations." arXiv:2407.21060, presented at the 13th Conf. on Engineering, Project and Production Management. [PR conference/PP] GPT-3.5 few-shot translation of New Zealand Building Code clauses into LegalRuleML. Tests chain-of-thought and self-consistency. The abstract gives no quantitative results — [arXiv](https://arxiv.org/abs/2407.21060)
- **Function mapping:** Zheng, Z., Lin, J.-R. et al. "LLM-FuncMapper: Function Identification for Interpreting Complex Clauses in Building Codes via LLM", arXiv:2308.08728 (2023). The v2 title is "Translating regulatory clauses into executable codes for building design checking via large language model driven function matching and composing". A predefined library of atomic functions is matched by the LLM (CoT + classification-based tuning) and composed into executable checking code. The coverage claim is "almost 100%" of computer-processible clauses, but secondhand sources disagree on the wording — [arXiv](https://arxiv.org/pdf/2308.08728v1.pdf); [ResearchGate v2](https://www.researchgate.net/publication/399300847_Translating_regulatory_clauses_into_executable_codes_for_building_design_checking_via_large_language_model_driven_function_matching_and_composing)
- **Intermediate representation + RL:** Shi, J.W.L., Dang, M., Solihin, W., Yeoh, J.K.W. (2026). "Reinforcement learning to improve large language model-based automated code compliance systems." arXiv:2606.22402 (v1 21 Jun 2026, v2 29 Oct 2026; NUS group, with a CORENET-related co-author). [PP] P4IR: SFT, then **GRPO** to generate intermediate representations (code skeletons). Results: up to **21.3% lower tree edit distance** and up to **41.0% lower token-level Levenshtein distance** vs SFT baselines, and a statistically significant reduction in false positives. Zero-shot, it beats leading LLMs used with few-shot prompting. Motivation: LLMs "often produce incorrect or hallucinated rules" — [arXiv](https://arxiv.org/abs/2606.22402)
- **RASE / ACCORD (Horizon Europe, grant 101056973):** RASE tagging is formalised in a semantic domain-specific Building Compliance Rule Language defined by the **AEC3PO ontology**. The project aims at the "first hybrid automated compliance checking methodology" combining manual RASE with AI/NLP. A CORDIS-listed paper is "Human-in-the-Loop Learning with LLMs for Efficient RASE Tagging in Building Compliance Regulations" (Al-Turki et al. 2024 per Gautam et al.). Its content and results could not be retrieved. The CODE-ACCORD corpus has 862 annotated regulation sentences — [CORDIS](https://cordis.europa.eu/project/id/101056973/results); [arXiv 2403.02231 (CODE-ACCORD)](https://arxiv.org/pdf/2403.02231v1.pdf)
- **Deterministic engine as decider:** Wan et al. (2025) send checks to the **DOE COMcheck engine via API (MCP)** for "deterministic and audit-ready outputs" and use RAG/LLM reasoning only where coverage is incomplete or ambiguous — [arXiv](https://arxiv.org/abs/2510.02634)
- **Deterministic parser + LLM reviewer:** Lu & Zhu (2026) use a deterministic Parser for BIM exports. A re-implemented **ontology- and rule-based baseline scored 89.10%**, against 96.68% for their framework — [AEM](https://www.aemjournal.org/index.php/AEM/article/view/4301)
- **JSON rule schema:** Gautam et al. (2026) have an LLM turn clauses into JSON rules (fields: rule ID, element category, policy source, measured variable, comparison operator, threshold, unit, applicability). Areas (shoelace formula), scale conversion and bearing are computed deterministically. The paper is ambiguous about whether the LLM also influences the final verdict ("LLM to interpret measurements in context") — [arXiv](https://arxiv.org/html/2607.00015v1)
- **Explicit non-LLM decision (open source, non-academic):** the GitHub project Batool-Jaber/ifc-compliance-checker states that "all calculations and the final PASS/FAIL decision are deterministic Python — the LLM never decides compliance" (IfcOpenShell + RAG) (snippet only) — [GitHub](https://github.com/Batool-Jaber/ifc-compliance-checker)
- **Physics verifier:** Luo et al. (2026) attribute the compliance gain (56.8% → 98.6%) to the external FE verifier, not to the LLM — [arXiv](https://arxiv.org/abs/2608.07978)
- **KG:** SGR-BIM (Xiao et al. 2026) builds a cross-modal KG linking regulation semantics to IFC geometry — [arXiv](https://arxiv.org/abs/2606.12065). A 2026 BRI review notes that KG construction has progressed but "scalability remains limited" (snippet only) — [BRI](https://www.tandfonline.com/doi/full/10.1080/09613218.2026.2637965)
- **SWRL via LLM outside AEC:** a 2026 *Procedia CIRP*-type paper generates executable SWRL for tolerance KGs with LLM + RAG and a verification module (manufacturing, not buildings) — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2212827126007328)

### Inferences
- The places where papers deliberately avoid the LLM are: geometry calculation, final threshold comparison, energy calculations (COMcheck), structural verification (FE) and BIM parsing (deterministic parser / IfcOpenShell → SQL). The LLM's role is clause retrieval, rule translation, tool selection and explanation.
- For a Dutch context (Bbl), the natural analogue would be an LLM that translates to or helps author a formal rule representation (e.g. RASE-like / JSON / DSL), with a deterministic engine doing the checking. This matches the direction of ACCORD and P4IR.

### Gaps
- No found LLM paper targets IDS (buildingSMART Information Delivery Specification) or mvdXML generation, and none uses KBimCode + LLM. This was not found in this search round and should not be read as proof of absence.
- Quantitative results of Fuchs et al. (LegalRuleML) and of the LLM-RASE ACCORD paper were not retrievable.

---

## 3. How do agents access BIM/IFC and what accuracy is reported?

### Takeaway
Four access patterns: (1) **vendor API tools** (Revit API → JSON; Ying & Sacks), (2) **LLM-generated scripts** (IronPython for Revit, IfcOpenShell Python; Madireddy, CodeAct prototypes), (3) **IFC → relational DB / graph DB with text-to-SQL / text-to-Cypher** (IfcLLM), (4) **knowledge graph over IFC** (SGR-BIM). Generated scripts are fragile (13–77% success). Structured DB querying with retries reaches 82–96% on small query sets, and silent wrong answers remain a risk.

### Cited Findings
- **IfcLLM:** Lamsal, R., Zlatanova, S., Xu, H., Sun, Y., Shen, X. (UNSW). "IfcLLM: Natural Language Querying of IFC Models through Complementary Relational and Graph Representations." arXiv:2605.13236 (v3, Oct 2026). [PP; Elsevier journal listed but not verified] — [arXiv](https://arxiv.org/html/2605.13236)
  - IfcOpenShell → **SQLite** (16 tables + an EAV property table, with precomputed centroids and bounding boxes) and a **Neo4j** graph (rooms–doors–stairs adjacency). A LangGraph agent routes attribute and aggregation queries to SQL and spatial and path queries to Cypher, retrying up to 5 iterations with error feedback.
  - 30 queries × 3 IFC models: GPT-OSS-120B **96%**, GPT-OSS-20B 93%, GPT-5.6 Luna (proprietary) 90%, Gemma 4 31B 87%, Llama 3.3 70B 82%. DB build took ~2.6 s (FZK Haus) to ~219 s (25,053 elements).
  - Limitations: small query set, graph limited to rooms, doors and stairs, context overflow on large results, and **semantic errors that return plausible but wrong answers without triggering a retry** (motivating an answer-validation stage). Bounding-box adjacency creates false connections for irregular rooms. Not a compliance paper itself.
- **IFC-MCQ (arXiv:2610.30533, 2026)** [PP]: automatically generated multiple-choice benchmark for LLM agents on IFC data retrieval. It compares a fixed-tool agent with a code agent writing IfcOpenShell Python. In the "no access to the IFC model" control, accuracy was 37.0–49.7% across 4 LLMs (snippet only; full results not retrieved) — [arXiv](https://arxiv.org/html/2610.30533)
- **Revit API tools:** Ying & Sacks use Revit API → JSON (28 properties × 20 slabs) and then an NL query over the JSON. The run was correct on the demo, but "different runs of the agent can produce varying process descriptions, and some runs result in incorrect results" — [EasyChair](https://easychair.org/publications/preprint/k2PJ/open)
- **Generated Revit scripts:** Madireddy et al. report script success rates of 0%–76.7% depending on the LLM (see Q1) — [arXiv](https://arxiv.org/abs/2506.20551)
- **BIM exports to a deterministic parser:** Lu & Zhu, 211 cases from real-project BIM exports (slabs, beams, columns), with an overall accuracy of 96.68% for compliance verdicts — [AEM](https://www.aemjournal.org/index.php/AEM/article/view/4301)
- **KG over IFC:** SGR-BIM, 84.3% on 679 fire-safety queries — [arXiv](https://arxiv.org/abs/2606.12065)
- Open-source prototypes: CodeAct IFC compliance agent with stateful/stateless Python execution (thesis, altux5/thesis-acc-agent); "ifc-skills", an IfcOpenShell skill for coding agents — [GitHub thesis-acc-agent](https://github.com/altux5/thesis-acc-agent); [GitHub ifc-skills](https://github.com/nbharathik/ifc-skills)
- Also found but not opened: "BIM Information Extraction Through LLM-based Adaptive Exploration", arXiv:2605.01698 — [arXiv](https://arxiv.org/pdf/2605.01698)

### Inferences
- Pre-structuring IFC deterministically (SQL/graph/KG) and letting the LLM only query it is more reliable than having the LLM write free-form scripts against the API.
- The IfcLLM finding that the most dangerous errors are silent plausible errors is directly relevant to permit decisions. It argues for deterministic re-verification and showing the queried elements and values to the reviewer.

### Gaps
- No standard benchmark yet for "IFC compliance query" accuracy. All numbers come from small, author-built sets (30, 211, 679 queries; 44 cases).

---

## 4. How is completeness checking (are required documents and information present) handled?

### Takeaway
Completeness checking of permit *applications* (are all required documents and data present) is **almost absent from the academic LLM-agent literature**. Academic work touches it only indirectly: BIM data quality/missing-information detection (Ying & Sacks), agents requesting missing data (the AiC 2025 proposal), and decisions with incomplete project data (Yin et al.). Completeness checking appears mainly in commercial plan-review products.

### Cited Findings
- Ying & Sacks identify missing or inaccurate BIM data as a major unsolved stage: "automating the recognition of quality issues and selecting the appropriate enrichment tools during a rule checking process remain unexplored" — [EasyChair](https://easychair.org/publications/preprint/k2PJ/open)
- The AiC 2025 paper (pii S0926580525007472) proposes a multi-agent setup where a rule-execution agent can request missing data from a model-preparation agent (snippet only) — [ScienceDirect](https://sciencedirect.com/science/article/pii/S0926580525007472)
- Yin et al. (ISARC 2026) frame the problem as making clause-level decisions "even when project data is incomplete" — [IAARC](http://www.iaarc.org/publications/2026_proceedings_of_the_43rd_isarc_singapore/retrieval_augmented_generation_and_multi_agent_arbitration_for_construction_code_compliance_in_aec.html)
- Madireddy et al.: the approach depends on "well-structured BIM models with accurate metadata" — [arXiv](https://arxiv.org/abs/2506.20551)
- Commercial (out of academic scope, vendor claims): Archistar "AI PreCheck Completeness Check", OpenGov AI Pre-Check (configured to completeness checklists), CivCheck (flags missing documents). Honolulu reported per-application review time falling from 60–90 to 15–20 min after RPA + CivCheck (vendor/case-study figure, unverified). It is not confirmed whether these use LLMs — [Archistar](https://www.archistar.ai/aiprecheck/ai-plan-review/); [OpenGov](https://opengov.com/products/permitting-and-licensing/ai-review/); [CivCheck](https://www.claritisoftware.com/products/civcheck-ai-plan-review-software); [case-studies.ai](https://case-studies.ai/use-cases/document-intelligence/DI-008-municipal-building-permit-review/)

### Inferences
- In practice, completeness checking is a precondition that the papers assume rather than solve. An agent architecture for permits would need an explicit "information requirements" stage. IDS (buildingSMART) is the obvious deterministic candidate for BIM, but no paper found links IDS to LLM agents.

### Gaps
- No peer-reviewed evaluation of LLM-based document-completeness checking for permit applications was found.

---

## 5. Evaluation datasets, metrics and results, and limitations reported by the authors

### Takeaway
Evaluations are small, author-built and heterogeneous. They mix retrieval metrics (Hit@1), verdict accuracy, script success rates, edit distance and report similarity. Results range widely, and the best numbers (96–99%) come from systems with deterministic components and narrow scope.

### Cited Findings
| Paper | Dataset | Metric → result | Source |
|---|---|---|---|
| Ying & Sacks 2024 (CIB W78) | 1 Revit duplex, 20 slabs, IBC 2009 Ch.19, 1 rule | Qualitative: 4/4 slabs correct in demo run; run-to-run variability | [EasyChair](https://easychair.org/publications/preprint/k2PJ/open) |
| Madireddy et al. 2025 (arXiv) | 2 Revit projects, 12 rules | Script success rate 0%–76.7% (Grok 76.7, DeepSeek 33.3, Claude 3.5 23.7, GPT-4 13.2) | [arXiv](https://arxiv.org/abs/2506.20551) |
| Lu & Zhu 2026 (AEM) | 211 cases, real BIM exports, 2 Chinese structural codes | Accuracy 96.68% vs zero-shot 57.35%, naive RAG 79.15%, naive RAG + rule 77.25%, ontology/rule baseline 89.10% | [AEM](https://www.aemjournal.org/index.php/AEM/article/view/4301) |
| Yin et al. 2026 (ISARC) | 300 labelled queries (dev200/test100), 600 codes, 141,681 clause units | Hit@1 dense 0.550 vs BM25 0.210; Qwen-plus 0.430 (USD 0.896/1K queries) vs GPT-4o 0.345 (USD 5.763/1K); arbiter triggered 37%, revised majority in 32.4% of triggered cases | [IAARC](http://www.iaarc.org/publications/2026_proceedings_of_the_43rd_isarc_singapore/retrieval_augmented_generation_and_multi_agent_arbitration_for_construction_code_compliance_in_aec.html) |
| Xiao et al. 2026 SGR-BIM (AiC) | 679 expert-verified fire-safety queries | 84.3% accuracy, +8.6% vs single-agent baselines | [arXiv](https://arxiv.org/abs/2606.12065) |
| Luo et al. 2026 (arXiv) | 44 structural cases | Code compliance 56.8% → 98.6% | [arXiv](https://arxiv.org/abs/2608.07978) |
| Shi et al. 2026 P4IR (arXiv) | Not stated on abstract page | −21.3% tree edit distance, −41.0% token Levenshtein vs SFT; significant FP reduction | [arXiv](https://arxiv.org/abs/2606.22402) |
| Lamsal et al. IfcLLM (arXiv) | 30 queries × 3 IFC models | 82%–96% answer accuracy | [arXiv](https://arxiv.org/html/2605.13236) |
| Zheng et al. 2025 (BuildSys) | 4 components from real inspection reports | ~96.25% similarity to human reports (snippet only) | [PDF](https://www.cs.virginia.edu/~bjc8c/papers/zheng25inspection.pdf) |
| Wan et al. 2025 (arXiv) | ASHRAE 90.1-2022 case demos | No quantitative metrics in abstract; GPT-4o most stable | [arXiv](https://arxiv.org/abs/2510.02634) |
| Gautam et al. 2026 (arXiv) | Worked examples only | No metrics; VLM counted 15 apartments instead of 6 on a multi-unit plan | [arXiv](https://arxiv.org/html/2607.00015v1) |

**Reported limitations (authors' own words or close paraphrase):**
- Ying & Sacks: insufficient AEC domain data in LLMs; **non-determinism** ("LLMs often produce different responses to the same query across different runs … undesirable for engineering tasks like ACC"); impossible to pre-build every tool, so code generation is suggested; token cost with large BIM data; **data privacy/leakage** when BIM is sent to an external LLM server; RAG retrieves irrelevant context — [EasyChair](https://easychair.org/publications/preprint/k2PJ/open)
- Madireddy et al.: only 2 cases and 12 rules; limited Revit versions; fast model churn; manual script execution; dependence on BIM quality; Revit lock-in — [arXiv](https://arxiv.org/abs/2506.20551)
- IfcLLM: silent plausible-but-wrong answers; context overflow; limited graph coverage — [arXiv](https://arxiv.org/html/2605.13236)
- Gautam et al.: no quantitative benchmark; VLMs strong semantically but weak at precise geometry; hallucination risk needs human review for low-confidence cases — [arXiv](https://arxiv.org/html/2607.00015v1)
- Shi et al.: LLMs "often produce incorrect or hallucinated rules" (motivation) — [arXiv](https://arxiv.org/abs/2606.22402)
- Nawari & Lawal: components evaluated separately rather than end to end; single jurisdiction (snippet only) — [citedrive](https://www.citedrive.com/en/discovery/an-agentic-ai-system-for-roof-design-compliance-using-computer-vision-retrieval-augmented-generation-and-large-language-models/)
- BRI 2026 review: calls for standardized benchmarks, cross-jurisdictional ontology alignment and explainable frameworks (snippet only) — [BRI](https://www.tandfonline.com/doi/full/10.1080/09613218.2026.2637965)

### Inferences
- Results are not comparable across papers (different metrics, codes and units of analysis). The Lu & Zhu comparison (rule/ontology baseline 89.1% vs naive RAG 79.2%) suggests naive RAG alone underperforms classic rule-based checking. Only well-structured multi-role systems beat it.
- No paper reports an explicit **hallucination rate** for compliance verdicts. Proxies are false-positive reduction (P4IR), script failure rates and silent-error observations (IfcLLM).

### Gaps
- No public, shared ACC-with-LLM benchmark on IFC models for building permits was found (CODE-ACCORD is a text corpus, not a checking benchmark).
- No evaluation on Dutch/European regulations (Bbl, Bouwbesluit) with LLM agents was found.

---

## 6. Explainability, traceability to clauses and keeping a human in charge

### Takeaway
The literature consistently positions LLM-based ACC as **decision support with a human in charge**. Traceability is implemented through (a) a full reasoning trace in the report (ReAct transcript), (b) citation constraints that only allow retrieved clause IDs with verifiable evidence spans, (c) RAG links from each violation to a clause, and (d) audit-ready output from a deterministic engine. Human-in-the-loop serves to resolve ambiguous rules and confirm revisions.

### Cited Findings
- Ying & Sacks: "the entire rule checking process is documented in the final report, including every thought, action, input, output, and the final answer". The report lists element IDs that pass or fail plus revision suggestions. Human-in-the-loop handles ambiguity: citing Zhang et al. (2023), "around 53% of building requirements contain ambiguities" (e.g. "close to"), the agent can ask the user for clarification. Designers confirm every BIM revision. Traditional ACC reporting is only "pass/fail with references to the original textual rules", and permit processes need experts to investigate failure causes manually — [EasyChair](https://easychair.org/publications/preprint/k2PJ/open)
- Yin et al.: outputs may cite **only clause IDs from the retrieved candidate set**, and evidence spans must match retrieved text and be "mechanically validated". The output is a "clause package". The arbiter fires on disagreement or validation flags — [IAARC](http://www.iaarc.org/publications/2026_proceedings_of_the_43rd_isarc_singapore/retrieval_augmented_generation_and_multi_agent_arbitration_for_construction_code_compliance_in_aec.html)
- Luo et al.: a retrieval-augmented code base makes "each violation traceable to a specific clause" — [arXiv](https://arxiv.org/abs/2608.07978)
- Wan et al.: COMcheck API produces "deterministic and audit-ready outputs" — [arXiv](https://arxiv.org/abs/2510.02634)
- Lu & Zhu: "decision-support approach … rather than a fully autonomous approval engine"; the Critic produces a structured verdict — [AEM](https://www.aemjournal.org/index.php/AEM/article/view/4301)
- Gautam et al.: output includes extracted_value, required_value, operator, status and a human-readable message, with human review for low-confidence cases. Their own worked example contains an inconsistency (message says 82.0 m² vs extracted 80.0 m²), which shows why generated explanations need checking against the structured values — [arXiv](https://arxiv.org/html/2607.00015v1)
- Madireddy et al.: reports carry Revit Element IDs so users can locate flagged elements, and humans run and repair scripts — [arXiv](https://arxiv.org/abs/2506.20551)
- ACCORD: "Human-in-the-Loop Learning with LLMs for Efficient RASE Tagging" (humans validate LLM-proposed rule tags) — [CORDIS](https://cordis.europa.eu/project/id/101056973/results)
- Commercial context: OpenGov states "nothing is automated past the point of human review", and Archistar says an AI pass does not guarantee permit approval — [OpenGov](https://opengov.com/products/permitting-and-licensing/ai-review/); [Archistar](https://www.archistar.ai/aiprecheck/ai-plan-review/)

### Inferences
- Design principles that recur across the papers: (1) structured, element-level output with clause ID, required and observed values; (2) the citation set constrained to retrieved, verifiable clauses; (3) the deterministic engine decides and the LLM explains; (4) escalate to a human on disagreement, low confidence or ambiguous clauses; (5) keep the full agent trace as an audit log. These map well onto requirements for Dutch permit decisions (motiveringsbeginsel, i.e. the duty to give reasons), but no paper addresses legal accountability under administrative law explicitly.
- A free-text ReAct transcript (Ying & Sacks) is transparent but non-deterministic. Runs differ, which undermines reproducibility as an audit basis.

### Gaps
- No paper found evaluating explanation quality with actual plan reviewers or permit officers (user studies).
- No paper found that measures the rate of incorrect clause citations (citation hallucination) in compliance reports, except the structural prevention via the citation contract in Yin et al.
