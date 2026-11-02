# Source analysis: public rules for building permits in Dubai

Research status: 1 November 2026. Basis of the ruleset [dubai_public.yaml](../src/repermit/packs/dubai_public.yaml).

## Conclusion

The public sources are useful for the process: what type of change it is, which route applies and which documents are required. They are not sufficient for the substantive check. The fire code and the Dubai Municipality document list could not be read. See `reports/Bronnen RePermit kennisbank Dubai.md` for the full source research.

The ruleset therefore contains 20 rules and 7 explicit gaps. This is not legal advice. Have a competent expert check the rules before they are used for real.

## How the regulations fit together

- The Dubai Building Code (DBC) and the UAE Fire and Life Safety Code (FLSC) together form the main rules for building design in Dubai (DBC A.4.3).
- The DBC applies across the emirate, including free zones and DIFC, to designs permitted after it took effect (Decree 45/2021, art. 3).
- If it conflicts with model codes, the strictest requirement applies. Between a general and a specific requirement, the specific one applies (DBC A.4.3).
- Planning rules from developers or planning authorities take precedence over DBC Part B where plot-specific rules exist (DBC A.4.1).
- For changes to existing buildings, the authority can allow an alternative solution if the requirements cause disproportionate cost (DBC A.8). The consultant carries the burden of proof, and existing conditions must be kept or improved.

## Sources read

| Source | Issuer | Used for | Limitation |
|---|---|---|---|
| [Dubai Building Code 2021](https://dmpmedia.dm.gov.ae/uploads/2021/12/Dubai%20Building%20Code_English_2021%20Edition_compressed.pdf) | Dubai Municipality | Change types, scope, heritage | Mainly Part A read. Resolution 225/2024 relaxes seven parameters, only for plots of 250 m² or less |
| [Decree 45/2021](https://dlp.dubai.gov.ae/Legislation%20Reference/2021/Decree%20No.%20%2845%29%20of%202021%20Concerning%20the%20Dubai%20Building%20Code.html) | Ruler of Dubai, 18 November 2021 | Validity of the DBC | Says nothing about existing buildings |
| [Local Order 3/1999](https://www.dm.gov.ae/documents/local-order-no-3-of-1999-regulating-construction-works-in-the-emirate-of-dubai/) | Chairman of Dubai Municipality | Permit obligation (art. 4), deviating from drawings (art. 14) | Art. 4, 8 and 9 were replaced by Executive Council Resolution 65/2022. An English translation exists but still shows the old articles. Local Order 6/2000 only moved the commencement date |
| [Resolution 85/2019](https://www.dm.gov.ae/documents/administrative-resolution-no-85-of-2019-concerning-the-licensing-of-decoration-works/) | Dubai Municipality | Decoration work, 100 m² threshold | Arabic, read in full. Own translation |
| [DDA Service ID Cards](https://webzoning.dda.gov.ae/Zoning/Content/dda/ServicesIDs/Building%20Modification%20Services'%20ID%20Cards.pdf) | Dubai Development Authority | Route and documents | December 2021 issue, DDA area only. Historical: the live service pages, Form ZA-DC-F-69A and circulars are the current layer |
| [Law 3/2026](https://dlp.dubai.gov.ae/Legislation%20Reference/2026/Law%20No.%20(3)%20of%202026%20Concerning%20the%20Quality%20and%20Safety%20of%20Buildings.pdf) | Government of Dubai | No rule included | Covers periodic certificates for buildings aged 20 years and over, not modifications. See also art. 9(a)(4) on maintenance and art. 10 on the management entity |
| [Dubai BIM Standard v1.4](https://dxmdigitaldocs.github.io/site/assets/bim-standard/DubaiBuildingPermitBIMStandards.pdf) | Not established | IFC as format | DM house style on an unofficial host. DM circulars confirm that a Dubai BIM Standard exists, but no government copy was reached |

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
- A fire separation leads to a Civil Defence NOC, on the basis of Law 4/2025 art. 17(4). The fire rating itself is in the FLSC, which was not read.
- Moving a wall changes two units. An NOC from the second owner is still not literally required, but Law 6/2019 art. 9(e) makes the wall shared and art. 39(a) requires approvals for substantial alterations. The ruleset therefore escalates to a reviewer.

## Interpretations in the ruleset

These choices are not literally in the sources. They are also noted on the rules themselves.

- The DDA card says "if applicable" for the Civil Defence NOC and structural calculations, without a criterion. The triggers (`fire_compartment_boundary`, `load_bearing`) were chosen during this analysis.
- That modifications require modified drawings is an elaboration of the approval duty in art. 14. For DDA, the service card confirms this.
- The sources are also labelled `derived`: the documents are official, but the rules are paraphrases.

## Gaps

| Gap | Effect in the app | Solution |
|---|---|---|
| UAE Fire and Life Safety Code 2018 unreachable: the Civil Defence site did not respond and the u.ae page returned a 404 | No fire values, only the NOC requirement | Supply the code. Do not copy from unauthorized copies |
| Dubai Municipality document list not found | Every case under Dubai Municipality escalates (`DM-DOCS`) | Supply service card 4127 from hub.dm.gov.ae |
| No rules for other authorities, such as Trakhees and DIFC | Escalation (`OTHER-ENTITY`) | Trakhees procedures are public and can become rules |
| Historical buildings fall outside the DBC | Escalation (`HISTORICAL`) | Request the authority's guidelines |
| Law 14/2025 (consultants) and Law 7/2025 (contractors) are in Arabic only | No rules on competence | Add rules if roles need real checking |

## BIM: the requirement in the app is broader than the source

The app requires a real IFC design model for every new permit and every public-pack modification. That is a product requirement. The sources show a narrower duty:

- Circular 9-1-2 of 2023 applies to new permits from 1 January 2024 and requires Open BIM.
- Circular 9-1-3 of 2026 applies from 1 April 2026 to new buildings above G+12 or with 15,000 m² or more.
- For modifications, Circular 9-1-3 covers only buildings previously licensed using BIM. For a building without a BIM licence these circulars set no duty.
- Neither circular names IFC. Only the BIM Standard does.
- RePermit therefore treats IFC for modifications as a product choice.

## Not included

- Figures from blogs, such as fees, lead times and the BIM thresholds.
- Dimensions from the DBC, such as minimum room sizes. That check needs drawing or BIM data the app does not read.
- Acoustic requirements. The code was not fully researched on this point.
