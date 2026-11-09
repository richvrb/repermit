# Overheidsprogramma's die AI, LLM's of agents inzetten bij bouwvergunningen en planbeoordeling

Peildatum onderzoek: 7 november 2026. Notities in het Engels/Nederlands. Elke bewering heeft een bron. "Announcement" (aankondiging) en "evaluated result" (geëvalueerd resultaat) worden expliciet onderscheiden. Initiatieven van vóór 2024 zijn gemarkeerd als [BACKGROUND].

Algemene kanttekening: veel cijfers komen uit persberichten van overheden of leveranciers. Het enige gevonden onafhankelijk-methodische overheidsevaluatierapport met nauwkeurigheidscijfers is het CivCheck-rapport van Seattle (zie Noord-Amerika).

---

## 1. Singapore: CORENET X (BCA/URA). Architectuur, IFC-SG, geautomatiseerde checks, AI-gebruik en de rol van ambtenaren

### Takeaway
CORENET X is een gecoördineerd, BIM/IFC-gebaseerd meer-agentschappen-indieningsplatform met een **regelgebaseerde (deterministische) Automated Model Checker**, en geen AI/LLM-systeem. Live zijn de IFC-schemacheck en de kwaliteitscheck. De regelgevingscheck wordt geleidelijk uitgerold. Het oordeel blijft bij de Qualified Persons (QP's) en de agentschappen: zij kunnen ook na een "pass" nog handmatig toetsen. AI staat bij BCA wel op de agenda ("automated design checks"), maar ik vond geen bevestigde AI-component in de officiële CORENET X-toetsing.

### Cited Findings
- De Model Checker heeft drie componenten. (1) De IFC Schema Check controleert versie, verplichte attributen en ruimtelijke hiërarchie en zit in de MVP. (2) De Quality Check controleert de IFC+SG-kwaliteitseisen en de volledigheid van informatie tegen de CORENET X Code of Practice en zit in de MVP. (3) De Regulatory Compliance Check is "upcoming", is bedoeld voor "automated assessment of selected regulatory requirements" en wordt geleidelijk uitgerold. — [CORENET X info: Model Checker](https://info.corenet.gov.sg/overview/corenet-x-submission-portal/model-checker) (geraadpleegd nov 2026)
- De kwaliteitschecks hebben vaste, regelgebaseerde criteria. Voorbeelden zijn clash detection met 1 mm tolerantie, slabs die volledig door spaces gedekt moeten zijn en levels met dezelfde naam die dezelfde FFL moeten hebben. Er zijn zes QC-categorieën (QC01–QC06). De resultaten (Pass/Fail/Alert) zijn als BCF te downloaden, en QP's moeten de gemelde issues, vooral Alerts, beoordelen en verifiëren. — [CORENET X info: Model Checker](https://info.corenet.gov.sg/overview/corenet-x-submission-portal/model-checker)
- Indieners kunnen via een "Pre-Submission Check" vóór de formele indiening IFC-modellen uploaden en checken. De pagina noemt geen AI of machine learning. — [CORENET X info: Model Checker](https://info.corenet.gov.sg/overview/corenet-x-submission-portal/model-checker)
- Volgens de BCA-FAQ richt de Automated Model Checker zich op "as many deterministic rules as possible, across multiple agencies". QP's gebruiken hem voor pre-submission checks, en agentschappen kunnen ook na een geslaagde MC-check nog handmatig toetsen. — [BCA CORENET X FAQ, new data requirements and technology](https://www1.bca.gov.sg/regulatory-info/building-control/corenet-x/corenet-x-faq/new-data-requirements-and-technology) (via zoeksnippet; de pagina gaf bij het ophalen een 404)
- IFC-SG is een uitbreiding van IFC met lokale regelgevingsrepresentaties. De configuratiebestanden bevatten parameters van BCA, LTA, NEA, NParks, PUB, SCDF en URA. — [BCA technological enablers](https://www1.bca.gov.sg/regulatory-info/building-control/corenet-x/more-information/technological-enablers) (via zoeksnippet)
- Implementatieplan URA: verplicht voor nieuwe projecten vanaf 1 april 2025, en lopende projecten vanaf 1H 2026. — [URA circular DC23-07, CORENET X Implementation Plan](https://www.ura.gov.sg/guidelines/circulars/dc23-07/). **Conflict:** andere bronnen melden verplichting vanaf oktober 2025 voor projecten vanaf 30.000 m² BVO — [99.co](https://www.99.co/singapore/insider/from-october-2025-corenet-x-mandatory-for-building-submissions/). Vanaf 1 oktober 2026 geldt de plicht voor nieuwe projecten vanaf 5.000 m² BVO, en de regering besloot de plicht niet uit te breiden naar alle projecten ongeacht omvang — [Highways Today, aug 2026](https://highways.today/2026/08/27/singapore-ai-ibew-2026/).
- BCA's eigen AI-programma noemt "automated design checks" naast voortgangsmonitoring en veiligheidssurveillance als toepassingen (programma/aankondiging, geen geëvalueerd resultaat). — [Highways Today, aug 2026](https://highways.today/2026/08/27/singapore-ai-ibew-2026/)
- Volgens BCA en URA zijn sinds de mandaatstart in 2025 meer dan 140 projecten met 300 bedrijven via CORENET X gegaan. — zoeksnippet uit de resultatenset over [CORENET X](https://info.corenet.gov.sg/resources/corenet-x-training---funding); de exacte primaire bron is niet geverifieerd.
- Risico's volgens de industrie (Nemetschek, niet onafhankelijk): verkeerd geclassificeerde objecten (bv. een branddeur gemodelleerd als generieke slab) worden niet herkend door de regelengine, automatisering op slechte modellen vermenigvuldigt fouten, en kleine bureaus kampen met capaciteits- en kostendruk. Hij adviseert audittrails en menselijke aftekening voor AI-aanbevelingen. — [TechNode Global, 22 sep 2026](https://technode.global/2026/09/22/nemetschek-jonathan-ng-corenet-x-ai-assisted-compliance-digital-delivery-qa/)
- Juridisch kader rond AI in Singapore: geen aparte AI-wet. IMDA publiceerde op 22 januari 2026 een Model AI Governance Framework for Agentic AI (vrijwillig). — [Mayer Brown, 3 jul 2026](https://mayerbrown.com/en/insights/publications/2026/07/ai-regulation-in-singapore-and-hong-kong-a-mid-year-checkpoint)

### Inferences
- CORENET X is vooral een **data- en procesarchitectuur**: één IFC-SG-model voor meerdere agentschappen, met deterministische regelchecks vooraf. Het is een referentie voor "machine-leesbare regels + gestandaardiseerd datamodel" en geen LLM-agent.
- De verantwoordelijkheid ligt nadrukkelijk bij de QP. De checker ondersteunt, beslist niet.

### Gaps
- Geen officiële bron gevonden over het aantal regels in de Regulatory Compliance Check of de live-status ervan in 2026.
- Geen bevestiging van AI- of LLM-gebruik binnen de toetsing door agentschappen. Geen gerapporteerde doorlooptijdwinst.
- De mandaatdata zijn tegenstrijdig tussen bronnen (april 2025, oktober 2025, oktober 2026). Controleer dit in de BCA/URA-circulaires.

---

## 2. Dubai: Dubai Municipality (BPS / "Build in Dubai"), DDA, Trakhees

### Takeaway
Dubai Municipality kondigde op 9 augustus 2026 een **AI-agent** aan die bouwvergunningen voor particuliere en investeringsvilla's "zonder menselijke tussenkomst" moet afgeven. De agent toetst tekeningen en documenten tegen de Dubai Building Code over meerdere disciplines, en handmatige beoordeling blijft alleen voor uitzonderingen. Het gaat om een **aankondiging met een gefaseerde uitrol van 26 weken**. Er zijn nog geen geëvalueerde resultaten. Het fundament is het in mei 2023 gelanceerde online vergunningensysteem met BIM-gebaseerde automatische checks [BACKGROUND].

### Cited Findings
- Aankondiging van 9 augustus 2026 door de Building Regulation and Permits Agency van Dubai Municipality. Het systeem moet villa-vergunningen afgeven zonder menselijke tussenkomst, leest ingediende tekeningen en documenten, en toetst tegen de Dubai Building Code en technische regels. — [Dubai Media Office, 9 aug 2026](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)
- De agent toetst kavelplanning, architectonisch ontwerp, installaties (MEP), constructieve veiligheid en stabiliteit, en cross-checks tussen tekeningen en ondersteunende documenten. Hij genereert automatisch "building card"-informatie. Aanvragers kunnen vooraf een ontwerpcheck doen en krijgen bijna direct een besluit, met feedback als er wijzigingen of extra informatie nodig zijn (dus een geautomatiseerd informatieverzoek aan de aanvrager). — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)
- Rol van de mens: handmatige beoordeling alleen in uitzonderingsgevallen, en technisch personeel verschuift naar werk met meer toegevoegde waarde. — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)
- Fasering over 26 weken: (1) ontwikkeling en test van de AI-agent per discipline, (2) een live pilot met geselecteerde ingenieursbureaus, (3) volledige uitrol voor alle villa-aanvragen van adviesbureaus, geïntegreerd met het platform "Build in Dubai". Er zijn geen numerieke doelen, alleen "from days to just minutes". De aankondiging is gekoppeld aan de Dubai Economic Agenda D33. — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically); zie ook [Gulf News](https://gulfnews.com/uae/dubai-to-cut-building-permit-processing-times-from-days-to-minutes-with-ai-1.500635246) en [Khaleej Times](https://www.khaleejtimes.com/uae/dubai-ai-system-villa-construction-permits)
- Citaat van CEO Mariam Al Muhairi: het doel is "not merely to improve government services, but to fundamentally redesign them". — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)
- [BACKGROUND] In mei 2023 lanceerde Dubai Municipality een nieuw online systeem voor bouwvergunningen en toezicht, met als doel geautomatiseerde checkservices voor adviseurs om naleving van de Dubai Building Code te borgen. — [Dubai Media Office, 26 mei 2023](https://www.mediaoffice.ae/en/news/2023/May/26-05/Dubai-Municipality-launches-new-online-system-for-building-permits-and-control-services). Volgens een vakpublicatie worden non-compliance-issues in een 3D-view van het model gemarkeerd, zodat de adviseur kan corrigeren en opnieuw uploaden. — [BIM Community, A New BIM Strategy for Dubai](https://www.bimcommunity.com/experiences/load/191/a-new-bim-strategy-for-dubai)
- Commentaar (geen officiële bron): menselijk toezicht en heldere governance blijven belangrijk waar geautomatiseerde besluiten juridische of commerciële gevolgen hebben. — [Middle East AI News](https://www.middleeastainews.com/p/dubai-municipality-to-slash-building)

### Inferences
- Dubai is het enige gevonden programma dat expliciet een **agent** inzet die het **besluit** neemt (volledig geautomatiseerde afgifte) voor een afgebakende, laag-risico categorie (villa's), met een menselijke uitzonderingsroute.
- De aankondiging zegt niets over uitlegbaarheid, beroep of aansprakelijkheid.

### Gaps
- Geen informatie gevonden over AI-initiatieven van Dubai Development Authority (DDA) of Trakhees voor vergunningen.
- Geen gegevens over het onderliggende model (LLM, computer vision of regelgebaseerd), nauwkeurigheid, of de status van de pilotfase per november 2026.
- Geen juridisch kader voor geautomatiseerde besluiten gevonden (beroep, motivering).

---

## 3. Overige VAE/GCC: Abu Dhabi (DMT / TAMM), Saoedi-Arabië (Balady), Qatar

### Takeaway
Abu Dhabi (DMT) lanceerde in april 2024 een "AI-Enabled BIM and Automated Plan Review System" plus chatbot, en in juni 2025 het AI-gedreven platform **Binaa**. Volgens media daalde de doorlooptijd voor villavergunningen daarmee met 57% en de herindieningen met meer dan de helft (door de overheid gerapporteerd, niet onafhankelijk geëvalueerd). Voor Saoedi-Arabië (Balady) en Qatar vond ik geen bevestigde AI-planreview voor bouwvergunningen.

### Cited Findings
- 22 april 2024: DMT Abu Dhabi lanceert (1) een AI-Enabled BIM and Automated Plan Review System (BIM/APRS) met geautomatiseerde code-compliancechecks, waarbij AI potentiële overtredingen van de Abu Dhabi-bouwcodes identificeert en 2D-CAD-tekeningen naar 3D-modellen worden omgezet, en (2) een Building Permits AI Virtual Assistant (chatbot, 24/7, meertalig) voor toegang tot codes en regels. Er worden geen metriek en geen beschrijving van de menselijke rol gegeven. — [Abu Dhabi Media Office, apr 2024](https://www.mediaoffice.abudhabi/en/infrastructure/department-of-municipalities-and-transport-launches-ai-solutions-to-streamline-building-permit-processes-in-the-emirate/)
- Juni 2025: lancering van het AI-gedreven platform **Binaa**, dat procedures moet unificeren en de verwerkingstijd met "tot 70%" moet verkorten (doelstelling). — [Economy Middle East](https://economymiddleeast.com/news/abu-dhabi-binaa-platform-reduce-building-permit-processing-times-70-percent)
- Gerapporteerd resultaat: sinds de lancering van Binaa daalde de gemiddelde tijd voor een vergunning voor een residentiële villa met 57%, en herindieningen daalden met meer dan de helft. In 2025 werden ruim 11.000 bouwvergunningen afgegeven (+15%). — [Khaleej Times](https://www.khaleejtimes.com/business/property/abu-dhabi-approves-75-million-sqm-of-development-in-2025); [Gulf News](https://gulfnews.com/uae/abu-dhabi-urban-indicators-record-75-million-square-metres-of-development-in-2025-1.500472524). **Conflict:** Gulf News dateert de lancering van Binaa op medio 2024, andere bronnen op juni 2025.
- Saoedi-Arabië: Balady biedt bouwvergunningen als elektronische dienst ("Electronic, Not instant"). Er is geen AI- of BIM-autocheck gevonden. — [Balady: issuing building permit](https://balady.gov.sa/en/services/issuing-building-permit). Het ministerie gaf in 1H 2026 meer dan 34.000 bouwvergunningen af via het digitale licentiesysteem. — [Zawya](https://www.zawya.com/en/projects/saudi-ministry-issues-over-34000-building-permits-in-first-half-of-2026-411454)

### Inferences
- Abu Dhabi combineert BIM-autocheck, AI-chatbot en een geünificeerd platform. Het gerapporteerde effect (57%) is een overheidsclaim zonder methodologie.

### Gaps
- Geen bronnen gevonden over AI in bouwvergunningen in Qatar of Riyadh (bv. de "instant permit"-claims in Saudische media zijn niet geverifieerd).
- Geen details gevonden over de AI-techniek in Binaa (LLM of regelgebaseerd) of over de menselijke eindbeslissing.

---

## 4. Europa

### Takeaway
Europa zit overwegend in de fase van **BIM-gebaseerde vergunningen en machine-leesbare regels** (Estland, Finland, EU-projecten ACCORD/CHEK) en van **kleinschalige AI-pilots voor intake en volledigheid** (Thüringen) of ondersteuning van planologische beoordeling (VK). In Noorwegen zijn er regelgebaseerde automatische besluiten voor eenvoudige zaken (Stavanger). Het VK is het verst met LLM-gebaseerde tools op nationale schaal (Extract live sinds juni 2026; Augmented Planning Decisions in alpha), met als expliciet uitgangspunt dat de planning officer beslist. Voor Nederland vond ik geen AI-pilot voor vergunningtoetsing, wel een BIM-autotoetsingspilot (Rotterdam).

### Cited Findings

**Verenigd Koninkrijk (planning, niet building control)**
- Extract (i.AI + MHCLG Digital Planning) zet oude planningsdocumenten en kaarten, inclusief handgeschreven notities, om in data. Sinds juni 2026 is het gratis beschikbaar voor alle lokale planningsautoriteiten in Engeland. — [MHCLG Digital blog, 17 jun 2026](https://mhclgdigital.blog.gov.uk/2026/06/17/extract-is-here-ai-powered-planning-data-for-every-council-in-england/); [GOV.UK, jun 2026](https://www.gov.uk/government/news/ai-tool-to-slash-planning-decision-times-as-government-accelerates-push-to-build-15-million-homes)
- Extract-trials vanaf april 2025 met Hillingdon, Exeter, en Nuneaton & Bedworth: gemiddeld 3 minuten per record tegenover 1–2 uur handmatig. Het tool gebruikt Google DeepMind's Gemini. Volgens i.AI vragen de outputs in ongeveer 59–72% van de gevallen slechts kleine correcties, en review door gebruikers blijft essentieel. Ongeveer 50 LPA's gebruiken het actief, met meer dan 1.000 verwerkte documenten (vooral Tree Preservation Orders). — zoeksamenvatting van [UKAuthority](https://www.ukauthority.com/articles/iai-plans-roll-out-of-extract-ai-tool-for-councils), [Construction Management](https://constructionmanagement.co.uk/government-rolls-out-digital-planning-tool-to-all-local-authorities/) en [MHCLG blog](https://mhclgdigital.blog.gov.uk/2026/06/17/extract-is-here-ai-powered-planning-data-for-every-council-in-england/) (het i.AI-evaluatierapport zelf is niet opgehaald)
- Augmented Planning Decisions (APD) is een prototype dat householder-aanvragen trieert, kerninformatie samenvat en de planning officer een eerste beoordeling geeft. Het is ontwikkeld met Google DeepMind, Google Cloud, Faculty en LPA's, met alpha-trials sinds mei 2026 bij Barnet, Camden en Dorset. Het doel is de beslistijd te halveren van 8 naar 4 weken (doelstelling). Bij goede resultaten volgt uitbreiding naar maximaal 10 extra councils in 2026 en een nationale uitrol vanaf 2027. "Every APD assessment is reviewed and approved by a qualified planning officer", en mensen "will remain the final decision makers". Extract zou per council ongeveer 255 uur per jaar besparen. — [GOV.UK persbericht, 16/17 jun 2026](https://www.gov.uk/government/news/ai-tool-to-slash-planning-decision-times-as-government-accelerates-push-to-build-15-million-homes)

**Duitsland**
- Thüringen, pilot "Automatisierte Entscheidungsunterstützung in kommunalen Baugenehmigungsverfahren" (TMDI met leverancier Rulemapping Group, onderste bouwtoezichtsautoriteiten Landkreis Greiz en Saalfeld-Rudolstadt). Looptijd: najaar 2025 tot juli 2026, met een verlenging gewenst. — [KOMMUNAL, 11 jul 2026](https://kommunal.de/ki-prueft-bauantraege-thueringen)
  - Module 1 splitst een gescande PDF in bouwtekeningen, statistiekformulieren en de aanvraag. Status: in test, niet live.
  - Module 2 controleert volledigheid en consistentie (adres, naam, perceelnummer) en bepaalt de procedure (vereenvoudigd of vergunningvrij). Status: werkt redelijk in test, maar met fouten.
  - Module 3 toetst de planologische toelaatbaarheid (binnengebied, buitengebied, bestemmingsplan). Status: nog niet werkbaar.
  - Problemen: er is geen landelijke dataset of GIS voor planologische zones, en de koppeling met de digitale bouwaanvraag (OZG-EfA) is pas tegen 2027 voorzien. Greiz krijgt ongeveer 800–900 aanvragen per jaar. — [KOMMUNAL](https://kommunal.de/ki-prueft-bauantraege-thueringen)
- Hessen: een KI-chatbot in het Bauportal Hessen is gepland en vervangt in de eerste fase de handleiding en de FAQ (aankondiging). — [Hessen digiBauG Newsletter zomer 2025](https://wirtschaft.hessen.de/sites/wirtschaft.hessen.de/files/2025-10/digibaug_newsletter_sommer_2025_final.pdf)
- Beieren: een Landtag-motie van de Grünen vraagt om KI- en LLM-ondersteunde controle op volledigheid en formele plausibiliteit. Dit is een politieke positie, geen beleid. — [Bayerischer Landtag Drucksache](https://www.bayern.landtag.de/www/ElanTextAblage_WP19/Drucksachen/Basisdrucksachen/0000009500/0000009599.pdf)

**Estland**
- [BACKGROUND] In 2020 kondigde het Ministerie van Economische Zaken (Jaan Saar) het plan aan om de afgifte van gebruiksvergunningen (kasutusluba) door een computer te laten beslissen op basis van BIM, met automatische controle van plannen, brandveiligheid, vluchtweglengtes, gevelmaterialen en het aantal bouwlagen. Een prototype zou op één gebouw worden getest. — [ERR, 20 feb 2020](https://www.err.ee/1055214/hoonele-kasutusloa-andmist-voib-hakata-otsustama-arvuti)
- BIM-gebaseerde bouwvergunningen zouden begin 2024 beschikbaar komen en waren in een pilotfase in geselecteerde gemeenten, via het bouwregister EHR. — [OECD Infrastructure Toolkit: Estonia Building Register](https://infrastructure-toolkit.oecd.org/wp-content/uploads/Estonia_BuildingRegister.pdf)
- Het Ministerie van Klimaat wil BIM in het register integreren om compliancechecks te automatiseren. — [Taylor & Francis hoofdstuk "BIM-based building permit"](https://www.taylorfrancis.com/chapters/oa-edit/10.1201/9781003650287-22/bim-based-building-permit-christopher-robin-raitviir-pille-riin-peet-irene-lill-raido-puust)
- Het Estse Ministerie van Economische Zaken en Communicatie was partner in ACCORD (zie hieronder). — [VTT CRIS, ACCORD](https://cris.vtt.fi/en/projects/automated-compliance-checks-for-construction-renovation-or-demoli/)

**Finland**
- [BACKGROUND 2023] Het RAVA3Pro-project (stad Helsinki) bouwt een standaard datamodel voor geautomatiseerde gegevensoverdracht en regelsets waarmee een machine numerieke voorschriften kan toetsen in afgebakende use-cases. AI werd nog niet gebruikt, alleen besproken als langetermijnvisie. Gemeenten zullen gegevens invoeren in het nationale informatiesysteem voor de gebouwde omgeving (Ryhti). — [Valtioneuvosto, RAVA3Pro](https://valtioneuvosto.fi/-/1410903/rava3pro-hanke-parantaa-rakennusvalvonnan-toimintaa-automatisoinnin-avulla)

**Noorwegen**
- Stavanger is volgens berichtgeving de eerste Noorse gemeente met automatische besluiten op bouwaanvragen, beginnend met de renovatie van schoorstenen. Het aanvraagsysteem controleert vooraf of aan de voorwaarden is voldaan (regelgebaseerd). — [Regjeringen.no, "Første steg for automatisk byggesaksbehandling"](https://www.regjeringen.no/no/aktuelt/forste-steg-for-automatisk-byggesaksbehandling/id3173846/) (de pagina gaf een 403; de inhoud komt uit een zoeksnippet)
- In een opiniestuk (juni 2026) van een productowner bij leverancier Sikri staat dat de gemiddelde behandeltijd in Stavanger daalde van meer dan 30 dagen (2020) naar 15,8 dagen (2025). Dit is geen onafhankelijke evaluatie en de daling is niet aan AI toe te schrijven. — [TU.no, "Byggesak på 15 dager"](https://www.tu.no/artikler/byggesak-pa-15-dager-slik-brukes-ki-trygt-og-sporbart/573649) (via zoeksnippet)
- Asker: KI voor bouwzaakbehandeling in de conceptfase, met een nieuwe versie gepland voor 2026. — [Asker kommune, KI-løftet](https://www.asker.kommune.no/om-asker-kommune/digitaliseringsprosjekter/digitaliseringprosjekter_/kunstig-intelligens/)
- KS (de vereniging van gemeenten) stelt als eerste maatregel een "KI-pilot for trygg saksbehandling" voor. — [KS, Plan for bruk av KI i kommunal sektor 2025](https://www.ks.no/fagomrader/digitalisering/kunstig-intelligens-ki/plan-for-bruk-av-kunstig-intelligens-i-kommunal-sektor-2025/)

**Nederland**
- Rotterdam heeft een pilotopzet voor het digitaal indienen en geautomatiseerd toetsen van minimaal 6 omgevingsvergunningaanvragen op basis van een 3D BIM-model, waarbij onderzocht wordt of een deel van de omgevingsregels machinaal te toetsen is. Softwareleveranciers moeten die regels machineleesbaar implementeren. Een beperking is of het Omgevingsloket BIM-modellen van voldoende omvang kan ontvangen. — [Omgevingsweb, pilotdocument (feb 2026)](https://omgevingsweb.nl/wp-content/uploads/2026/02/1099024.pdf)
- De DSO-vragenbomen (toepasbare regels) verwijzen burgers vaak nog naar de gemeente. — [Binnenlands Bestuur, "DSO zegt: neem contact op met uw gemeente"](https://www.binnenlandsbestuur.nl/ruimte-en-milieu/omgevingswet/dso-zegt-neem-contact-op-met-uw-gemeente)

**EU-projecten**
- ACCORD (Horizon Europe, 2022 tot 31 augustus 2025, gecoördineerd door VTT). Er zijn demonstraties in het VK, Finland, Estland, Duitsland en Spanje. Partners zijn onder meer het Estse ministerie en Cloudpermit Oy. De outputs zijn een semantisch framework, een tool voor regelformalisering, microservices voor permit- en compliancechecks, een beleidsaanbeveling voor BIM-gebaseerde vergunningen en 21 trainingsmaterialen. — [VTT CRIS](https://cris.vtt.fi/en/projects/automated-compliance-checks-for-construction-renovation-or-demoli/); [CORDIS 101056973](https://cordis.europa.eu/project/id/101056973)
- CHEK (Horizon Europe, 1 oktober 2022 tot 30 september 2025, ongeveer €5 mln) ontwikkelde een toolkit voor digitale bouwvergunningen: een modulair referentieproces, een virtuele assistent voor gemeenten en geautomatiseerde compliancechecks op basis van geïntegreerde 3D-stads- en gebouwmodellen. Pilots liepen in Ascoli Piceno (IT), Vila Nova de Gaia en Lissabon (PT) en Praag (CZ). Een deliverable met lessen uit de pilots verscheen in november 2025. — [CORDIS 101058559](https://cordis.europa.eu/projects/101058559); [TU Delft 3D, CHEK](https://3d.bk.tudelft.nl/projects/chek/); [Zenodo deliverable, nov 2025](https://zenodo.org/records/17591772)

### Inferences
- In Europa ligt de nadruk op het **formaliseren van regels** (ACCORD, RAVA3Pro, Rotterdam) als voorwaarde voor automatisering. LLM's verschijnen vooral bij documentdigitalisering (Extract), triage en samenvatting (APD) en intake (Thüringen).
- Het VK en Thüringen tonen dat **ontbrekende geodata en planningsdata** (GIS, bestemmingsplannen) de beperkende factor zijn, niet de AI zelf.
- De EU AI Act (high-risk-classificatie bij overheidsbesluiten) wordt in geen van de gevonden pilotbronnen expliciet genoemd. Dit is een aandachtspunt voor het rapport.

### Gaps
- Geen kwantitatieve resultaten gevonden van ACCORD- of CHEK-pilots (de deliverables zijn niet inhoudelijk gelezen).
- Geen informatie gevonden over een BIM-vergunning of AI binnen Ryhti in 2025–2026, over DiBK "eByggeSak"/ByggSøk-AI of over Duitse "BauGPT"/XBau-AI-initiatieven.
- Geen Nederlandse gemeentelijke AI- of LLM-pilot voor vergunningcheck of volledigheidstoets gevonden (de zoekopdracht leverde alleen BIM-autotoetsing en DSO-vragenbomen op).
- i.AI "Consult" gaat over consultatieresponsen in het algemeen en is niet specifiek voor vergunningen. Niet onderzocht.

---

## 5. Noord-Amerika: Los Angeles, New York, Honolulu, Seattle, Austin, Californië, Canada

### Takeaway
In Noord-Amerika domineren **AI-pre-screeningtools die de aanvrager vóór indiening gebruikt** (Archistar eCheck in LA, CivCheck/Clariti in Honolulu en Seattle). Ze lezen PDF-plannen met AI en voeren daarna **deterministische regelchecks** uit, terwijl de ambtenaar de beoordeling en het besluit behoudt. Het Seattle-rapport is de meest rigoureuze evaluatie: 87% van de in-scope intake-fouten gevonden, 91,7% overeenstemming in planreview, 6,4% gemiste correcties, en een geprojecteerde (gemodelleerde) besparing tot 46 dagen in intake. Honolulu rapporteert tot 55–70% kortere doorlooptijd, maar op basis van een kleine steekproef.

### Cited Findings

**Seattle (SDCI), CivCheck Proof of Value, maart–oktober 2025 (geëvalueerd resultaat)** — [Seattle CivCheck AI Pre-Screening Pilot Report, 2026](https://seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf)
- Methode: CivCheck "uses multiple AI techniques to read content from application documents such as PDF plan sets and assemble that content into structured data", en "performs deterministic checks on that data". Het is dus een hybride met AI-extractie plus een regelgebaseerde toets.
- Scope: "middle housing" (rijwoningen, eengezinswoningen, ADU's) onder de Seattle Residential Code. Er werden 34 volledigheidschecks en 67 compliancechecks geconfigureerd. Het ging om historische aanvragen, met ongeveer 40 medewerkers die toegang hadden (minstens 14 actief).
- Intake: van 90 afwijzingsredenen bij 29 aanvragen vielen er 35 buiten de pilotscope. 48 van de 55 in-scope redenen (87%) werden door CivCheck gevonden en 7 gemist. In 4 gevallen markeerde CivCheck een ontbrekende topografische survey die de medewerker bewust had laten vallen (discretie), wat volgens het rapport de noodzaak van menselijke discretie illustreert.
- Planreview (57 aanvragen, 1.262 checks): 91,7% overeenstemming met reviewers, 6,4% false positive (CivCheck gaf "pass" waar correctie nodig was) en 1,9% false negative (onterechte flag). De nauwkeurigheid verbeterde gedurende de pilot door kalibratie.
- Impact (gemodelleerde scenario's, geen gemeten productieresultaat): de mediane intake-duur van 54,5 dagen zou dalen naar 29 dagen (pilotconfiguratie) of 8 dagen (volledige configuratie). De mediane planreview van 161 dagen zou dalen naar 146 of 117 dagen.
- Problemen: "Our current codes, requirements, and processes do not always translate easily" naar machinelogica. Ook de volledigheidseisen zijn soms ambigu. Bij gemiddeld 6 reviewteams parallel levert alleen het versnellen van de bottleneck-review iets op. Er was geen integratie met Accela getest.
- Aanbeveling: een productiepilot, beperkt tot **volledigheidsscreening bij intake** (opt-in voor aanvragers). Compliance-checks vergen zorgvuldig verwachtingsmanagement.
- Waarborgen: CivCheck werd mede gekozen omdat "the core logic of the checks is deterministic, not probabilistic", met een transparante human-in-the-loop-aanpak waarbij gebruikers de logica kunnen zien, overrulen en verduidelijken. Het systeem doorliep de privacyreview van Seattle IT. Er gold een risico-acceptatieovereenkomst vanwege het ontbreken van certificeringen. Na de overname door Clariti zijn een nieuwe security- en AI-review vereist. Alle gebruikers kregen training in het Responsible AI-beleid van de stad. Van de medewerkers had 71% na de pilot een positiever beeld van AI.

**Honolulu (DPP), CivCheck**
- Publieke lancering op 8 december 2025 na een pilot van 5 maanden. Volgens het Clariti-prestatierapport (Q1 2026) daalde het aantal reviewcycli van 3,4 naar 1,4 (−58%), het aantal correcties van 23,5 naar 7,7 (−67%) en de tijd tot besluit van 73 naar 32,5 dagen (−55%), met een gemiddelde besparing van 40,5 dagen. Dit is gebaseerd op 19 CivCheck-vergunningen tegenover 17 vergelijkingsprojecten (kleine steekproef). Tijdens de pilot daalde de reviewtijd met 70% (60–90 minuten naar 20–30 minuten per review). Reviewers blijven beoordelen. — [Honolulu DPP, AI 50 award](https://www.honolulu.gov/dpp/city-earns-national-ai-50-award-for-innovative-permit-review-technology/); [HousingWire](https://www.housingwire.com/articles/how-honolulu-leveraged-ai-to-cut-permit-review-times-in-half/)
- Juli 2026: een fast-track-programma waarin plannen die CivCheck doorstaan naar prescreening gaan. — [Star-Advertiser, 2 jul 2026](https://www.staradvertiser.com/2026/07/02/hawaii-news/dpp-launches-fast-track-permit-review-program/). In augustus 2026 maakte DPP het gebruik van de AI-tool verplicht voor residentiële aanvragen (volgens de kop van het artikel; de inhoud is niet gelezen). — [Aloha State Daily, 6 aug 2026](https://alohastatedaily.com/2026/08/06/honolulu-dpp-requires-use-of-ai-tool-for-residential-project-permit-applications/)

**Los Angeles en Californië (Archistar eCheck)**
- 30 april 2025: gouverneur Newsom maakt de AI-tool van Archistar kosteloos beschikbaar voor LA City en County voor de wederopbouw na de bosbranden (gefinancierd door LA Rises, Steadfast LA, Autodesk en Amazon). Het tool gebruikt computer vision, machine learning en geautomatiseerde regelsets om ontwerpen tegen zonering en bouwcodes te toetsen. Eigenaren kunnen vooraf checken, en staf beoordeelt de plannen daarna nog steeds. Het is beschikbaar via een **statewide contract** voor alle lokale overheden. De claims ("weeks and months" naar "hours or days") zijn promotioneel en niet onderbouwd. — [Cal OES News, 30 apr 2025](https://www.news.caloes.ca.gov/governor-newsom-announces-launch-of-new-ai-tool-to-supercharge-the-approval-of-building-permits-and-speed-recovery-from-los-angeles-fires/)
- De betafase in Pacific Palisades startte op 16 juli 2025 (City of LA). LA County heeft een eigen pilot, waarbij het eCheck-rapport bij de aanvraag gevoegd kan worden. De workshop-presentatie (januari 2026) toont modules voor Building Code, Zoning Code/EO8 en EO1, met clause-by-clause-resultaten en een PDF-rapport. — [LA Mayor, persbericht](https://mayor.lacity.gov/news/city-launches-beta-testing-ai-tool-further-expedite-palisades-rebuilding) (403 bij ophalen; via snippet); [LA County DPW workshop-deck](https://file.lacounty.gov/SDSInter/dpw/recovery/1201690_RebuildingTogether_ArchistarDRAFTPPT12226.pdf)
- Er zijn geen LA-specifieke uitkomstcijfers gevonden. Een cijfer van 54% tijdsreductie op de Carahsoft-pagina is niet aan een jurisdictie gekoppeld. — [Carahsoft, Archistar](https://www.carahsoft.com/archistar)
- In augustus 2025 nam de LA City Council een motie aan voor een AI-pre-screeningpilot bij plan reviews. — [LA City Clerk, 25-0966](https://cityclerk.lacity.org/onlinedocs/2025/25-0966_misc_8-20-25.pdf) (via zoeksnippet)
- Californische wetgeving: er is geen wet gevonden die AI-planreview specifiek regelt. AB 253 (getekend op 10 oktober 2025) laat aanvragers private professionals inschakelen voor residentiële plan checks als de gemeente te traag is. Deze wet is niet AI-specifiek. — [Plural Policy, AB 253](https://open.pluralpolicy.com/ca/bills/20252026/AB253)

**Austin**
- Austin adopteerde na een pilot AI-gedreven permit-software (Archistar) voor residentiële zoneringsreview. Het systeem beoordeelt niet elk element van de plannen, maar vermindert de hoeveelheid data die staf moet controleren. — [Building Design+Construction](https://bdcnetwork.com/austin-texas-adopts-ai-driven-building-permit-software)

**New York**
- Geen AI-planreviewpilot bij NYC DOB gevonden. NYC DEP (niet DOB) test in een pilot van 6 maanden AI als beslisondersteuning voor de review van stormwaterplannen. — [Arcadis, 2026](https://www.arcadis.com/en/news/global/2026/arcadis-makes-waves-with-water-utilities-with-real-world-ai-pilots/)

**Canada**
- Surrey (BC) startte in 2024 een AI Development Inquiry Assistant-pilot die informatie geeft over vergunningen voor eengezinswoningen en tenant improvements. Het is vraagbeantwoording, geen beoordeling. — [Daily Hive](https://dailyhive.com/vancouver/surrey-development-inquiry-assistance-dia-ai-permitting-tool)
- Vancouver gebruikt eComply (Archistar) om plannen te uploaden en compliance-rapporten te ontvangen. Er is geen AI-pilot met resultaten gevonden. — [Govlaunch, Vancouver/Archistar](https://govlaunch.com/bg/projects/vancouver-bc-simplifies-permit-applications-and-compliance-with-archistar-digital-tools)

### Inferences
- Het dominante Noord-Amerikaanse patroon is **"AI extraheert, regels toetsen, mens beslist"**, gepositioneerd als pre-screening door de aanvrager. Het grootste meetbare effect zit in **minder correctierondes** en snellere **volledigheidsintake**, niet in vervanging van de reviewer.
- Seattle laat zien dat de inhoudelijke compliance-impact beperkt is zolang slechts een deel van de checks automatiseerbaar is, en zolang er meerdere parallelle reviews zijn.
- Geen enkel Noord-Amerikaans programma laat AI het besluit nemen. Dat contrasteert met Dubai.

### Gaps
- Geen onafhankelijke evaluatie van Archistar in LA of Austin gevonden.
- Geen agent- of multi-agentarchitectuur beschreven in de Noord-Amerikaanse programma's.
- Geen bevestigde AI-pilot gevonden voor NYC DOB of de City of Vancouver.
- Denver: er is een contract voor een AI-planreviewplatform, maar de bronnen spreken elkaar tegen over de leverancier (ComplyAI of CivCheck). Niet geverifieerd.

---

## 6. Dwarsdoorsnede: welke processtappen worden geautomatiseerd, welke techniek, waar blijft de mens

### Takeaway
Over alle programma's heen: **intake, volledigheid en informatieverzoeken** en **regelgebaseerde codecontrole op gestructureerde data (BIM/IFC)** zijn het verst. **Besluitvorming door AI** komt alleen voor in Dubai (aangekondigd, villa's) en als regelgebaseerd automatisch besluit voor triviale zaken in Stavanger. Elders ligt het besluit expliciet bij de mens (VK APD, Seattle, Honolulu, Singapore QP/agentschappen).

### Cited Findings
- Intake en volledigheid: Seattle (87% van in-scope fouten gevonden) — [Seattle rapport](https://seattle.gov/documents/Departments/Performance/Publications/2026CivCheckEvaluationReport.pdf); Thüringen module 2 — [KOMMUNAL](https://kommunal.de/ki-prueft-bauantraege-thueringen); Dubai pre-submission feedback — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically)
- Code- en planreview: Singapore Model Checker (deterministisch) — [CORENET X](https://info.corenet.gov.sg/overview/corenet-x-submission-portal/model-checker); Abu Dhabi BIM/APRS (AI) — [Abu Dhabi Media Office](https://www.mediaoffice.abudhabi/en/infrastructure/department-of-municipalities-and-transport-launches-ai-solutions-to-streamline-building-permit-processes-in-the-emirate/); Archistar (CV/ML + regelsets) — [Cal OES](https://www.news.caloes.ca.gov/governor-newsom-announces-launch-of-new-ai-tool-to-supercharge-the-approval-of-building-permits-and-speed-recovery-from-los-angeles-fires/)
- Triage en samenvatting voor de beslisser: VK APD — [GOV.UK](https://www.gov.uk/government/news/ai-tool-to-slash-planning-decision-times-as-government-accelerates-push-to-build-15-million-homes)
- Documentdigitalisering met een LLM (Gemini): VK Extract — [MHCLG blog](https://mhclgdigital.blog.gov.uk/2026/06/17/extract-is-here-ai-powered-planning-data-for-every-council-in-england/)
- Chatbots en vraagbeantwoording: Abu Dhabi, Hessen en Surrey — zie de bronnen hierboven.
- Geautomatiseerd besluit: Dubai AI-agent (aankondiging) — [Dubai Media Office](https://cd1.mediaoffice.ae/en/news/2026/august/09-08/dubai-redefines-the-future-of-building-permits-with-an-ai-system-that-issues-licences-automatically); Stavanger, regelgebaseerd, schoorstenen — [Regjeringen.no](https://www.regjeringen.no/no/aktuelt/forste-steg-for-automatisk-byggesaksbehandling/id3173846/)

### Inferences
- Het expliciet als "agent" benoemde ontwerp komt alleen voor in Dubai. Er is nergens een gedocumenteerde multi-agentarchitectuur, al suggereert de opsplitsing per discipline in Dubai (architectuur, MEP, constructie, cross-check) en de modulestructuur in Thüringen (sorteren, volledigheid, planologie) een modulaire of pijplijnstructuur.
- Het meest gerapporteerde probleem is de **vertaalbaarheid van regels naar machinelogica** (Seattle, ACCORD, RAVA3Pro, Rotterdam), gevolgd door **datakwaliteit en ontbrekende geodata** (Thüringen, Nemetschek over CORENET X) en **integratie met bestaande zaaksystemen** (Seattle/Accela, Thüringen/OZG).
- Waarborgen voor uitlegbaarheid zijn het best gedocumenteerd in Seattle (deterministische logica, zichtbare redenering, override, privacy- en AI-review) en in het VK (menselijke goedkeuring van elke APD-beoordeling).

### Gaps
- Er is nergens een formele juridische analyse gevonden (bv. EU AI Act, AVG art. 22, of het VAE-recht voor geautomatiseerde besluiten) die aan een specifiek vergunningprogramma is gekoppeld.
- Er zijn geen gepubliceerde foutpercentages of beroepszaken gevonden voor volledig geautomatiseerde besluiten.
