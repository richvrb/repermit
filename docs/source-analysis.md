# Source analysis: public rules for building permits in Dubai

Research status: 1 November 2026. Basis of the ruleset [dubai_public.yaml](../src/repermit/packs/dubai_public.yaml).

## Conclusion

The public sources are useful for the process: what type of change it is, which route applies and which documents are required. They are not sufficient for the substantive check. The fire code, the current BIM circulars and the Dubai Municipality document list could not be read.

The ruleset therefore contains 14 rules and 3 explicit gaps. This is not legal advice. Have a competent expert check the rules before they are used for real.

## How the regulations fit together

- The Dubai Building Code (DBC) and the UAE Fire and Life Safety Code (FLSC) together form the main rules for building design in Dubai (DBC A.4.3).
- The DBC applies across the emirate, including free zones and DIFC (Decree 45/2021, art. 3).
- If it conflicts with model codes, the strictest requirement applies. Between a general and a specific requirement, the specific one applies (DBC A.4.3).
- Planning rules from developers or planning authorities take precedence over DBC Part B where plot-specific rules exist (DBC A.4.1).
- For changes to existing buildings, the authority can allow an alternative solution if the requirements cause disproportionate cost (DBC A.8).

## Sources read

| Source | Issuer | Used for | Limitation |
|---|---|---|---|
| [Dubai Building Code 2021](https://dmpmedia.dm.gov.ae/uploads/2021/12/Dubai%20Building%20Code_English_2021%20Edition_compressed.pdf) | Dubai Municipality | Change types, scope, heritage | Mainly Part A read. Resolution 225/2024 amends parts of the code and was not read |
| [Decree 45/2021](https://dlp.dubai.gov.ae/Legislation%20Reference/2021/Decree%20No.%20%2845%29%20of%202021%20Concerning%20the%20Dubai%20Building%20Code.html) | Government of Dubai | Validity of the DBC | Says nothing about existing buildings |
| [Local Order 3/1999](https://www.dm.gov.ae/documents/local-order-no-3-of-1999-regulating-construction-works-in-the-emirate-of-dubai/) | Dubai Municipality | Permit obligation (art. 4), deviating from drawings (art. 14) | Arabic base text, art. 4 to 21 read. Amendment Local Order 6/2000 and the implementing rules not read |
| [Resolution 85/2019](https://www.dm.gov.ae/documents/administrative-resolution-no-85-of-2019-concerning-the-licensing-of-decoration-works/) | Dubai Municipality | Decoration work, 100 m² threshold | Arabic, read in full. Own translation |
| [DDA Service ID Cards](https://webzoning.dda.gov.ae/Zoning/Content/dda/ServicesIDs/Building%20Modification%20Services'%20ID%20Cards.pdf) | Dubai Development Authority | Route and documents | December 2021 issue, DDA area only. A newer version may exist |
| [Law 3/2026](https://dlp.dubai.gov.ae/Legislation%20Reference/2026/Law%20No.%20(3)%20of%202026%20Concerning%20the%20Quality%20and%20Safety%20of%20Buildings.pdf) | Government of Dubai | No rule included | Covers periodic certificates for buildings aged 20 years and over, not modifications |
| [Dubai BIM Standard v1.4](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf) | Not established | IFC as format | Found on a GitHub site, not a government domain. Provenance needs confirming |

## Change types according to DBC Table A.1

| Type | Meaning | The codes apply to |
|---|---|---|
| `renovation` | Finishes or strengthening, no reconfiguration | Interior finishes and building envelope |
| `modification` | Fit-out, or change to a system or building element | The fit-out or change |
| `reconstruction` | Change affecting adjacent egress routes or systems | The change and the affected parts |
| `change_of_use` | Different use of part or all of the building | The change and affected parts, such as escape stairs and sanitary facilities |
| `addition` | More area, height or depth | The addition, and the existing building if the addition relies on it |

## What the sources mean for the wall between 4A and 4B

- A relocated wall between apartments is probably a `modification`, or a `reconstruction` if egress routes are affected.
- Resolution 85/2019 does not help here. It applies to commercial and similar units, and excludes merging or splitting space.
- The 100 m² threshold quoted in blogs therefore does not simply apply to apartments.
- A fire separation leads to a Civil Defence NOC. The fire rating itself is in the FLSC, which was not read.
- Moving a wall changes two units. An NOC from the second owner is not explicit in the sources. That remains a question for the reviewer.

## Interpretations in the ruleset

These choices are not literally in the sources. They are also noted on the rules themselves.

- The DDA card says "if applicable" for the Civil Defence NOC and structural calculations, without a criterion. The triggers (`fire_compartment_boundary`, `load_bearing`) were chosen during this analysis.
- That modifications require modified drawings is an elaboration of the approval duty in art. 14. For DDA, the service card confirms this.
- The sources are also labelled `derived`: the documents are official, but the rules are paraphrases.

## Gaps

| Gap | Effect in the app | Solution |
|---|---|---|
| UAE Fire and Life Safety Code 2018 unreachable: the Civil Defence site did not respond and the u.ae page returned a 404 | No fire values, only the NOC requirement | Supply the code. Do not copy from unauthorized copies |
| Dubai Municipality document list not found | Every case under Dubai Municipality escalates (`DM-DOCS`) | Supply the service card from the BPS portal |
| Other authorities, such as Trakhees and DIFC, not researched | Escalation (`OTHER-ENTITY`) | Research per authority |
| Historical buildings fall outside the DBC | Escalation (`HISTORICAL`) | Request the authority's guidelines |
| Regulation 3/2007 and Regulation 10/2006 on change of use and planning rules not read | Only the DBC rule, and for DDA the zoning exception | Read the Arabic texts |
| Law 14/2025 (consultants) and Law 7/2025 (contractors) not read | No rules on competence | Read if roles need real checking |

## BIM: the requirement in the app is broader than the source

The app requires a real IFC design model for every new permit and every public-pack modification. That is a product requirement. The sources show a narrower duty:

- The BIM Standard reports that BIM has applied to specific project types since 1 January 2024, extended by Circular 9-1-3 of 2026. At that time only Dubai Municipality required it.
- The thresholds are known only from secondary sources, which partly contradict each other. They are therefore not in the ruleset.
- The circulars themselves were not found.

## Not included

- Figures from blogs, such as fees, lead times and the BIM thresholds.
- Dimensions from the DBC, such as minimum room sizes. That check needs drawing or BIM data the app does not read.
- Acoustic requirements. The code was not fully researched on this point.
