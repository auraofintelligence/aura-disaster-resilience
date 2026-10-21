# All-weather kiosk design

**Planning stage: design options for community and technical review.**

This design work will turn the kiosk vision into measured drawings, practical workshop tasks and a clear plan for unattended outdoor public equipment. The aim is a network that supports detailed disaster exercises and keeps useful information available when power, transport and communications change.

Tradespeople, assistants, drivers, artists, nurses, retirees and students can bring different skills to this work. People can try a full-size layout, check whether a message is easy to understand, map a maintenance route, measure a device's power use or help explain the results. Qualified designers and trades review the work that calls for their expertise.

## Our starting material

The [earlier concept artwork](https://github.com/auraofintelligence/straddie-disaster-kiosks/blob/main/assets/sovereign-atm.webp) gives us a visual starting point. The next drawings will show how people reach the controls, where the equipment fits, how rain drains away and how a maintainer opens and safely services it. Those details, followed by tests, will establish its weather performance.

The [earlier pitch](https://github.com/auraofintelligence/straddie-disaster-kiosks/blob/main/docs/Straddie_Disaster_Kiosk_Pitch.pdf), pages 7-10 and 13-15, describes a wooden arcade demonstrator, a later metal phone-booth or custom-steel enclosure, a touchscreen, an e-ink notice display, powerful computers and a separate lower-power service. E-ink is an electronic display that can retain its last image after power stops. The pitch also contains a candidate parts list, with different computer and solar options to compare.

We can now develop the dimensions, wiring, foundations, cooling, maintenance plan, prices and test results that will turn those options into a reviewable design. Weather performance will be stated as specific conditions and test results. [Design review](Question-PHY-10.md) and [power handover](Question-ENE-10.md) define that next package.

## Three useful physical forms

| Form | What it helps us do | What its design will cover |
|---|---|---|
| Sheltered arcade demonstrator | Learn by doing: try the interface, practise disaster scenarios, explore maps and assist other users in a workshop or suitable venue. | Screen and control positions, electrical safety, supervision, accessibility and the conditions of the sheltered venue. Outdoor weather testing is a later, separate step. |
| Operational fixed outdoor kiosk | Provide public information and agreed services at a particular site, including when it is unattended. | The site's weather, accessible approach, equipment protection, power, communication, cleaning, repair and evidence from tests. |
| Portable continuity kit | Keep information and contact available at a temporary location, replace a failed device or connect groups cut off from the main network. | Packing, carrying, setup, temporary anchors, safe batteries, weather limits, when to bring it back and how to restore messages after replacement. |

We can also define replaceable field devices for particular sensing or relay jobs. Their plan will state the loss we are prepared to accept, what service continues, and how people retrieve or replace them. See [device types](Question-PHY-01.md) and [field setup](Question-PHY-09.md).

## Put the public interface and computers where they work best

Compare two fixed arrangements: all equipment in a standalone outdoor cabinet, or a public screen connected to computers protected inside a suitable host building. Draw the cables, power connections and access arrangements in each option so everyone can see what the service relies on.

This lets us support both demanding simulations and dependable public information. The design will identify which services keep running when powerful computers are switched off to preserve energy. Notices, maps and message status should remain available in the agreed essential service.

A notice retained on an e-ink screen will show when it was issued and last checked. People will be able to see whether the kiosk is connected or displaying a saved notice.

Follow the work through [accessible controls](Question-PHY-03.md), [equipment layout](Question-PHY-04.md), [power use](Question-ENE-01.md), [changing power modes](Question-ENE-05.md), [matching messages to connections](Question-COM-01.md), [use without mobile service](Question-COM-07.md) and [clear status displays](Question-COM-08.md).

## Compare the arrangements

| Arrangement | What it offers | What we need to work through | Drawings and checks |
|---|---|---|---|
| Standalone outdoor cabinet | Public access with its own equipment and defined continuity service. | Rain and wind, heat inside the cabinet, separate battery space, damage, anchors, drainage, cleaning and room to repair it. | Measured front, side and inside views; equipment spaces; foundations; heat and energy studies; wiring and weather tests. |
| Weather-protected host installation | A sheltered public interface and protected space for powerful computers. | Host permission, building condition, opening hours, power, cables and access during an emergency or building closure. | Site and access plan; public route; equipment and power boundaries; named maintenance jobs; tests of what happens when the host space is unavailable. |
| Portable deployment | Equipment that a team can take where it is needed and use to restore service. | People and transport, weight, lifting, temporary restraint, charging, security, site permission, weather limits and retrieval. | Packing layout, weight, setup checklist, energy budget, skills needed and a drill that includes messages and equipment recovery. |

Compare all three using the same agreed services and disaster sequence. [Site sheets](Question-PHY-02.md), [outside power connections](Question-ENE-07.md) and [network layouts](Question-COM-02.md) will make the tradeoffs visible.

## Define what all-weather means at each site

For each form, describe four sets of conditions:

- **Working:** the services it provides while people use it.
- **Safe shutdown and survival:** when service pauses, how the equipment stays safe and what can be recovered.
- **Storage and transport:** how it is kept and moved between uses.
- **Return to service:** the checks and repairs needed after the event.

A weather rating is useful when its test conditions are clear: what was applied, from which direction, for how long and what passed. We will record operating and survival results separately.

| Conditions | Practical design questions | Work pages |
|---|---|---|
| Rain, wind and dust | Where does water go? What can enter an opening? How are panels, doors and antennas secured? When does a portable team bring equipment back? | [Weather and damage tests](Question-PHY-05.md), [antenna mounting](Question-COM-03.md) |
| Salt, humidity and heat | Which parts need corrosion protection and cleaning? How does heat leave? What happens when smoke closes the vents? Condensation is water forming on cool surfaces; how will the design manage it? | [Heat and moisture study](Question-PHY-06.md), [power budget](Question-ENE-01.md) |
| Fire, smoke and excessive heat | What triggers shutdown or withdrawal? Which parts remain safe, and who checks the unit before restart? State the actual exposure tested and the limits found. | [Hazard tests](Question-PHY-05.md), [keeping faults contained](Question-PHY-07.md) |
| Flood, splash and drainage | What level and route are suitable? How is power switched off safely? Who checks water damage and contamination before reuse? | [Sites and access](Question-PHY-02.md), [electrical design](Question-ENE-04.md) |
| Several days without normal supply or repairs | What service can the battery support through the agreed weather sequence? What changes when ferries stop, parts run out or the usual maintainer is away? | [Usable battery energy](Question-ENE-02.md), [generation](Question-ENE-03.md), [local maintenance](Question-ENE-08.md), [endurance tests](Question-ENE-09.md) |
| Disconnected groups or damaged devices | A network partition means some devices cannot reach others. What information can each group use, what happens to waiting messages, and how are different reports checked when the groups reconnect? | [Combining records](Question-COM-04.md), [checking authority](Question-COM-05.md), [network repairs](Question-COM-09.md), [field exercises](Question-COM-10.md) |

Each test will name the conditions, units, timing, uncertainty and result needed to pass. Compare measurements with the model and show what still needs checking. Plan practical testing with people and equipment over two to three days. Digital twins can simulate any chosen outage duration; record simulated time and computer runtime separately from practical test duration. [Sensor checks](Question-COM-06.md) will explain how observations are tested against a known reference and how real readings differ from simulated ones.

## Workshop tasks that move the design forward

- Make a full-size cardboard front panel. Try reaching the controls while standing, seated or helping someone else; mark improvements on the drawing.
- Put an equipment layout on a table. Use labelled shapes for batteries, computers and cables, then work out how a maintainer can reach each part.
- Practise a ferry closure with drivers, service staff and residents. Map how a repair person, spare part and portable kit could reach the site.
- Test a notice with assistants, nurses, retirees and students: find its source, time, directions and message status. Artists can help make the layout and diagrams clear.
- Measure power use and explain the results together. Qualified electrical staff lead connection and safety work; other participants can record readings and compare service schedules.
- Run an exercise where two groups lose contact, record different road reports and reconnect. Check what the public sees and who resolves the reports.

[Repair access](Question-PHY-08.md), [restart after power loss](Question-ENE-06.md) and [network acceptance exercises](Question-COM-10.md) turn these activities into evidence for the next review.

## D-002: the next human decision

**Proposed recommendation:** authorise the design brief for these three forms, the conditions each will be designed for, and alternative engineering drawings. Compare standalone and host-protected fixed kiosks, with the portable kit designed for its own job. Develop essential public information alongside the richer computing service.

Accepting D-002 would give the team a clear scope for that design work and agree the services and comparison criteria to use. Purchasing, building, electrical work, site use, outdoor trials and deployment have separate decisions, supported by the resulting evidence. Reviewers and decision-makers are still to be appointed.

The next review will bring together:

- Measured layouts, accessible approach and controls, equipment fit, weight and room for repairs.
- Equipment compartments, airflow, drainage, heat and moisture studies, and how faults are contained.
- Wiring and connection diagrams, safe switch-off points, protection and the skills required for each task.
- Site permissions, foundations and anchors, plus panel and antenna mounting options.
- Measured power use, usable battery energy, operating modes and restart steps.
- Weather and endurance tests, disconnected-network exercises, repair and replacement drills.
- A priced parts, installation and maintenance list with quantities, dated sources, exact selections or clear alternatives.
- A dated decision record identifying the people reviewing it, evidence considered, agreed scope, conditions, concerns and next work.

Community users, site hosts, maintainers and appropriately qualified mechanical, electrical, access and communications reviewers will each assess the parts they understand. Their feedback gives the next design version a practical foundation for a separately reviewed trial.
