"""Hand-authored source text for the 12 synthetic policy documents.

Why this is a separate module from generate_data.py: it is prose, not logic.
Keeping it apart means a reviewer reading the generator sees the generation
algorithm, and a reviewer checking the corpus sees the corpus.

Why the corpus looks the way it does. Retrieval here has to be hard enough
that hybrid search demonstrably beats vector search alone, so the documents
are written with three deliberate properties:

  1. **Form codes and section numbers** (`Form WD-114`, `Section 4.2`). These
     are exact tokens with no semantic neighbourhood -- BM25 finds them,
     embeddings do not.
  2. **Cross-references between documents.** The governing text for a claim is
     frequently in a document other than the one whose policy_type the claim
     was filed under. Water damage points at the flood exclusion; the flood
     exclusion points back at auto comprehensive, where flood damage to a
     vehicle IS covered. A retriever that returns the topically obvious
     document returns the wrong answer.
  3. **Defined terms with counter-intuitive meanings** ("Surface Water",
     "Sudden and Accidental Discharge"). Two documents can discuss water
     damage in near-identical language and reach opposite conclusions.

All content is invented. No real insurer's policy language was used.
"""

from __future__ import annotations

# Each policy: prose plus the structured numbers that coverage_rules.py will
# use. The numbers appear in both places on purpose -- the document is what the
# LLM reads, the fields are what the deterministic tool computes with -- and
# generate_data.py renders the fields into the prose so they cannot drift.

POLICIES: list[dict] = [
    {
        "slug": "auto-collision",
        "policy_type": "auto_collision",
        "title": "Auto Collision Coverage",
        "form": "AC-2210",
        "policy_id": "POL-AUTO-0003",
        "deductible": 1000,
        "limit": 50000,
        "summary": (
            "This form covers direct and accidental physical damage to a Covered Auto "
            "resulting from impact with another vehicle or object, or from the Covered "
            "Auto overturning. Coverage applies regardless of fault, subject to the "
            "deductible stated in Section 4.1. Damage arising from any cause other than "
            "impact or overturn is not a collision loss and is addressed under Auto "
            "Comprehensive Coverage, Form AX-3105."
        ),
        "covered": (
            "We will pay for repair or replacement of the Covered Auto when the loss "
            "results from a Collision Event as defined in Section 6. This includes "
            "single-vehicle impacts with fixed objects such as guardrails, utility "
            "poles, and parked vehicles; multi-vehicle collisions on public or private "
            "roads; and overturn of the Covered Auto regardless of whether another "
            "vehicle was involved. Damage to permanently attached original equipment is "
            "included. Where the cost of repair exceeds the actual cash value of the "
            "Covered Auto immediately before the loss, we will settle on a total-loss "
            "basis at actual cash value less the deductible. Reasonable towing from the "
            "scene of a covered collision to the nearest qualified repair facility is "
            "included without application of a separate deductible."
        ),
        "exclusions": [
            "Loss occurring while the Covered Auto is operated in any organized racing, "
            "speed contest, track day, or timed competitive event, whether or not the "
            "event was sanctioned.",
            "Mechanical or electrical breakdown, wear and tear, rust, corrosion, and "
            "gradual deterioration, none of which constitute a Collision Event even "
            "where the failure occurs during operation and results in impact.",
            "Loss caused by Surface Water, rising water, storm surge, or flood, "
            "regardless of whether the Covered Auto was in motion at the time. Such "
            "loss is not a collision loss; see Form AX-3105 and Form FX-0090.",
            "Damage occurring while the Covered Auto is being used to carry persons or "
            "property for compensation, including ride-hail and delivery platform use, "
            "unless a commercial use endorsement is attached.",
        ],
        "limits_note": (
            "The per-occurrence limit under this form is ${limit:,}. A deductible of "
            "${deductible:,} applies to each Collision Event and is subtracted before "
            "payment. Where a single continuous event produces multiple impacts, the "
            "event is treated as one occurrence and one deductible applies."
        ),
        "interaction": (
            "Loss from fire, theft, vandalism, falling objects, hail, animal strike, or "
            "flood is not covered here; those perils are addressed under Auto "
            "Comprehensive Coverage, Form AX-3105. Substitute transportation following "
            "a covered collision is not paid under this form and requires Rental "
            "Reimbursement, Form RR-0310. Towing beyond the nearest qualified repair "
            "facility is payable only under Roadside Assistance, Form RA-0075."
        ),
                "conditions": (
            "Notice of loss must be given within thirty days of the Collision "
            "Event. The Covered Auto must be made available for inspection before "
            "repairs begin, except for emergency work needed to protect the "
            "vehicle from further damage. Where another party is at fault, we may "
            "pursue recovery from that party, and the insured must not settle "
            "privately in a way that prejudices that right. A police report is "
            "required where any injury occurred or where the loss exceeds the "
            "deductible by more than five thousand dollars."
        ),
        "definitions": [
            ("Collision Event", "impact of the Covered Auto with another vehicle or "
             "object, or overturn of the Covered Auto. Contact with an animal is not a "
             "Collision Event."),
            ("Covered Auto", "the vehicle identified on the declarations page, "
             "including permanently attached original equipment."),
            ("Actual Cash Value", "replacement cost at the time of loss less "
             "depreciation for age, mileage, and condition."),
        ],
    },
    {
        "slug": "auto-comprehensive",
        "policy_type": "auto_comprehensive",
        "title": "Auto Comprehensive Coverage",
        "form": "AX-3105",
        "policy_id": "POL-AUTO-0011",
        "deductible": 500,
        "limit": 40000,
        "summary": (
            "This form covers direct and accidental loss to a Covered Auto from causes "
            "other than collision, including fire, theft, vandalism, falling objects, "
            "hail, animal strike, and flood. Flood damage to a Covered Auto is payable "
            "under this form. The general flood exclusion in Form FX-0090 applies to "
            "real property and does not remove flood coverage for vehicles."
        ),
        "covered": (
            "We will pay for loss to the Covered Auto caused by fire or explosion; "
            "theft of the vehicle or of permanently attached parts; malicious mischief "
            "and vandalism; glass breakage; impact with a bird or animal; falling "
            "objects including trees and hail; civil commotion; and water, including "
            "Surface Water and flood, that enters the vehicle. Loss of personal "
            "belongings left inside the vehicle is not covered here and is addressed "
            "under Homeowners Personal Property, Form HP-1155, or Renters Coverage, "
            "Form RT-2040. Where the vehicle is stolen and not recovered within thirty "
            "days, we will settle at actual cash value less the deductible."
        ),
        "exclusions": [
            "Wear and tear, mechanical breakdown, and any loss resulting from failure "
            "to maintain the Covered Auto.",
            "Loss to tapes, discs, aftermarket electronics, and custom equipment not "
            "permanently installed by the manufacturer.",
            "Theft occurring while the keys were left in the unattended vehicle in a "
            "publicly accessible location, unless forced entry is documented.",
            "Damage from impact with another vehicle or object, or from overturn, which "
            "is a Collision Event under Form AC-2210 and not payable here.",
        ],
        "limits_note": (
            "The per-occurrence limit under this form is ${limit:,}, subject to a "
            "deductible of ${deductible:,}. Glass-only repairs are settled without "
            "application of the deductible where the glass is repaired rather than "
            "replaced."
        ),
        "interaction": (
            "Where a single event produces both impact damage and non-impact damage -- "
            "for example, a vehicle that strikes a barrier and is subsequently "
            "submerged -- the impact portion is adjusted under Form AC-2210 and the "
            "water portion under this form, with one deductible applied per form. See "
            "Form FX-0090, Section 3, which confirms that the flood exclusion does not "
            "extend to Covered Autos."
        ),
                "conditions": (
            "Theft losses must be reported to police before a claim is submitted, "
            "and the report number provided. We may require a sworn statement of "
            "the circumstances and proof of ownership for any item claimed. Where "
            "a stolen Covered Auto is recovered after settlement, ownership "
            "passes to us and the insured must cooperate in transferring title. "
            "Glass claims may be settled through an approved repairer without "
            "further inspection."
        ),
        "definitions": [
            ("Comprehensive Loss", "any direct and accidental loss to the Covered Auto "
             "that is not a Collision Event."),
            ("Surface Water", "water on the ground surface from rainfall, snowmelt, or "
             "overflow of a body of water, before it enters a drain or watercourse."),
        ],
    },
    {
        "slug": "homeowners-dwelling",
        "policy_type": "homeowners_dwelling",
        "title": "Homeowners Dwelling Coverage",
        "form": "HD-1120",
        "policy_id": "POL-HOME-0002",
        "deductible": 2500,
        "limit": 350000,
        "summary": (
            "This form covers the dwelling structure, attached structures, and "
            "materials on the residence premises intended for use in construction, "
            "against direct physical loss except as excluded. Coverage for water damage "
            "is limited and depends on whether the Water Damage Endorsement, Form "
            "WD-114, is attached to the policy."
        ),
        "covered": (
            "We insure against direct physical loss to the dwelling and structures "
            "attached to it, including fire, lightning, windstorm, hail, explosion, "
            "falling objects, weight of ice and snow, and Sudden and Accidental "
            "Discharge of water from a plumbing, heating, or air conditioning system. "
            "Coverage extends to the reasonable cost of tearing out and replacing any "
            "part of the building necessary to repair the system from which the water "
            "escaped, but not to the cost of repairing the system itself. Detached "
            "structures are covered at ten percent of the dwelling limit. Debris "
            "removal following a covered loss is included within the limit."
        ),
        "exclusions": [
            "Loss caused by Surface Water, flood, storm surge, tidal water, or the "
            "overflow of any body of water, whether or not driven by wind. This "
            "exclusion applies regardless of any other cause contributing concurrently "
            "to the loss. See Form FX-0090.",
            "Constant or repeated seepage or leakage of water over a period of weeks, "
            "months, or years, whether or not the insured was aware of it. Such loss is "
            "not a Sudden and Accidental Discharge.",
            "Earth movement, including earthquake, landslide, mudflow, sinkhole "
            "collapse, and settling of the foundation.",
            "Neglect of the insured to use reasonable means to preserve the property at "
            "and after the time of loss, including failure to maintain heat in the "
            "dwelling during a vacancy.",
        ],
        "limits_note": (
            "The dwelling limit is ${limit:,} per occurrence with a deductible of "
            "${deductible:,}. A separate Named Storm Deductible of two percent of the "
            "dwelling limit applies to loss caused by a storm that has been assigned a "
            "name by the national weather authority, in place of the standard "
            "deductible."
        ),
        "interaction": (
            "Water damage arising from backup of sewers or drains, or from a sump pump "
            "failure, is not covered by this form and requires the Water Damage "
            "Endorsement, Form WD-114. Personal belongings within the dwelling are "
            "covered under Form HP-1155, not here. Liability for injury to visitors is "
            "addressed under Form PL-5000."
        ),
                "conditions": (
            "The insured must take reasonable steps to protect the dwelling from "
            "further damage after a loss, and we will pay the reasonable cost of "
            "doing so. Repairs beyond emergency protective work should not begin "
            "until the property has been inspected. Proof of loss, including an "
            "inventory of damaged building material and any contractor estimates, "
            "must be submitted within sixty days of our request. Concealment or "
            "misrepresentation of a material fact voids coverage."
        ),
        "definitions": [
            ("Sudden and Accidental Discharge", "an abrupt escape of water from a "
             "system that was, immediately before the loss, functioning as intended. "
             "Discharge that develops gradually is excluded."),
            ("Named Storm Deductible", "a percentage deductible applied in place of the "
             "standard deductible when the loss is caused by a named storm."),
        ],
    },
    {
        "slug": "homeowners-personal-property",
        "policy_type": "homeowners_personal_property",
        "title": "Homeowners Personal Property Coverage",
        "form": "HP-1155",
        "policy_id": "POL-HOME-0007",
        "deductible": 1000,
        "limit": 100000,
        "summary": (
            "This form covers personal belongings owned or used by an insured, "
            "wherever located, against the perils listed in Section 2. Certain "
            "categories of property carry internal sub-limits well below the form "
            "limit, and business property is restricted."
        ),
        "covered": (
            "We cover personal property against fire, lightning, windstorm, hail, "
            "explosion, theft, vandalism, falling objects, and Sudden and Accidental "
            "Discharge of water. Property is covered while temporarily away from the "
            "residence premises, including in a vehicle, at ten percent of the form "
            "limit. Settlement is on an actual cash value basis unless replacement cost "
            "coverage is shown on the declarations page. Sub-limits apply: $2,000 for "
            "jewelry and watches, $2,500 for firearms, $2,500 for silverware, and "
            "$3,000 for business property on the residence premises."
        ),
        "exclusions": [
            "Property used primarily for a trade or business in excess of the $3,000 "
            "sub-limit, which requires the Business Equipment Rider, Form BE-7720.",
            "Loss to property caused by Surface Water or flood, including belongings in "
            "a basement affected by rising water. See Form FX-0090.",
            "Breakage of fragile articles such as glassware, ceramics, and statuary, "
            "except when caused by fire, theft, or collapse of the building.",
            "Loss of property that simply disappears, where no theft can be evidenced "
            "and no physical damage is present.",
        ],
        "limits_note": (
            "The per-occurrence limit is ${limit:,} with a deductible of "
            "${deductible:,}. Sub-limits stated in Section 2 apply within, not in "
            "addition to, the form limit."
        ),
        "interaction": (
            "Belongings of a tenant who does not own the dwelling are covered under "
            "Renters Coverage, Form RT-2040, not this form. Business equipment above "
            "the sub-limit requires Form BE-7720. Damage to the structure itself is "
            "addressed under Form HD-1120."
        ),
                "conditions": (
            "The insured must provide an inventory of damaged or stolen property "
            "showing the quantity, description, age, and amount claimed for each "
            "item, supported by receipts, photographs, or appraisals where "
            "available. For items subject to a sub-limit, a current appraisal may "
            "be required before settlement. Property must be made available for "
            "inspection, and damaged property should not be disposed of until we "
            "have examined it or waived inspection in writing."
        ),
        "definitions": [
            ("Personal Property", "movable belongings owned or used by an insured, "
             "excluding motor vehicles and property held for business use beyond the "
             "stated sub-limit."),
            ("Sub-limit", "a cap applying to a category of property, deducted from "
             "rather than added to the form limit."),
        ],
    },
    {
        "slug": "water-damage-endorsement",
        "policy_type": "water_damage_endorsement",
        "title": "Water Damage Endorsement",
        "form": "WD-114",
        "policy_id": "POL-HOME-0021",
        "deductible": 1500,
        "limit": 25000,
        "summary": (
            "This endorsement adds coverage for water that enters the dwelling from "
            "sewer backup, drain backup, and sump pump overflow or failure. It does not "
            "add flood coverage. The flood exclusion in Form FX-0090 continues to apply "
            "in full, and the distinction between backup and Surface Water determines "
            "which outcome applies."
        ),
        "covered": (
            "We will pay for direct physical loss to the dwelling and to personal "
            "property caused by water that backs up through sewers or drains, or that "
            "overflows from a sump, sump pump, or related equipment, including where "
            "the overflow results from mechanical failure of the pump or from a power "
            "outage. Coverage includes the reasonable cost of professional water "
            "extraction, drying, and mould remediation directly attributable to the "
            "covered event, and the cost of tearing out and replacing building material "
            "necessary to reach the affected area."
        ),
        "exclusions": [
            "Water that enters the dwelling at or above ground level as Surface Water, "
            "including water that pools against the foundation during heavy rainfall "
            "and then seeps inward. This is a flood loss under Form FX-0090, Section 2, "
            "and is excluded regardless of whether a drain or sump was also overwhelmed.",
            "Backup caused by the insured's failure to maintain the sump pump, clear a "
            "known blockage, or replace equipment identified as defective in a prior "
            "inspection.",
            "Loss where the sump pump had no functioning backup power source and the "
            "policy required one as a condition of this endorsement.",
            "Gradual seepage through foundation walls, which is neither backup nor "
            "Sudden and Accidental Discharge.",
        ],
        "limits_note": (
            "This endorsement carries its own per-occurrence limit of ${limit:,} and a "
            "separate deductible of ${deductible:,}, which applies instead of the "
            "dwelling deductible when the loss is payable solely under this "
            "endorsement."
        ),
        "interaction": (
            "Where water damage results from both a covered backup and excluded Surface "
            "Water, the adjuster must determine the efficient proximate cause; if "
            "Surface Water is the proximate cause, Form FX-0090 governs and no payment "
            "is made under this endorsement. Sudden and Accidental Discharge from "
            "internal plumbing is covered under Form HD-1120 and not here."
        ),
                "conditions": (
            "The insured must arrange professional water extraction promptly and "
            "must not delay drying while awaiting our inspection, as secondary "
            "mould damage caused by delay is not covered. Records of the "
            "extraction and remediation contractor, including moisture readings "
            "where taken, must be provided. Where a sump pump is involved, we may "
            "require its service history and evidence of the backup power "
            "arrangement required by this endorsement."
        ),
        "definitions": [
            ("Backup", "water reversing direction within a sewer or drain line and "
             "entering the dwelling through a fixture or floor drain."),
            ("Efficient Proximate Cause", "the peril that set in motion the chain of "
             "events producing the loss, which determines coverage where covered and "
             "excluded perils combine."),
        ],
    },
    {
        "slug": "flood-exclusion",
        "policy_type": "flood_exclusion",
        "title": "Flood Exclusion",
        "form": "FX-0090",
        "policy_id": "POL-HOME-0090",
        "deductible": 0,
        "limit": 0,
        "summary": (
            "This form states the flood exclusion applying to all property coverages "
            "issued under this programme. It grants no coverage and pays no claim. Its "
            "scope is limited to real property and its contents; Section 3 confirms "
            "that Covered Autos are not subject to it."
        ),
        "covered": (
            "Nothing is covered by this form. It is an exclusionary form and is "
            "referenced by Form HD-1120, Form HP-1155, Form RT-2040, and Form WD-114. "
            "Where any of those forms would otherwise pay for a loss, and the efficient "
            "proximate cause of that loss is a peril described in Section 2 below, no "
            "payment is made. Flood coverage for real property is available only "
            "through a separately purchased flood policy, which this programme does not "
            "issue."
        ),
        "exclusions": [
            "Flood, Surface Water, waves, tidal water, storm surge, tsunami, and the "
            "overflow of any body of water, whether or not driven by wind and whether "
            "or not the water is contaminated.",
            "Water below the surface of the ground, including water that exerts "
            "pressure on or flows, seeps, or leaks through a foundation, wall, floor, "
            "swimming pool, or other structure.",
            "Mudflow, mudslide, and the erosion or subsidence of land caused by water, "
            "including the collapse of a retaining wall from water pressure.",
            "Water released from a dam, levee, dike, or other flood control structure, "
            "whether the release was accidental or intentional.",
        ],
        "limits_note": (
            "No limit and no deductible apply, because no coverage is granted. Where "
            "this form applies, the payable amount is zero irrespective of the limits "
            "stated in the underlying form."
        ),
        "interaction": (
            "Section 3. This exclusion does not apply to a Covered Auto. Flood damage "
            "to a vehicle is payable under Auto Comprehensive Coverage, Form AX-3105, "
            "subject to that form's limit and deductible. This exclusion also does not "
            "remove coverage for sewer or drain Backup where the Water Damage "
            "Endorsement, Form WD-114, is attached and Surface Water is not the "
            "efficient proximate cause."
        ),
                "conditions": (
            "No claim is submitted under this form and no proof of loss is "
            "required, because no coverage is granted. Where an adjuster "
            "determines that this exclusion applies to a loss reported under "
            "another form, the denial must identify the specific paragraph of "
            "Section 2 relied upon and must state the efficient proximate cause "
            "finding. An insured may request that determination in writing and "
            "may submit further evidence of causation."
        ),
        "definitions": [
            ("Flood", "a general and temporary condition of partial or complete "
             "inundation of normally dry land from Surface Water, overflow of inland or "
             "tidal water, or unusual accumulation of runoff."),
            ("Surface Water", "water on the ground surface from rainfall, snowmelt, or "
             "overflow, before it enters a drain, sewer, or watercourse. Water that has "
             "entered a sewer and then reversed direction is Backup, not Surface "
             "Water."),
        ],
    },
]

POLICIES += [
    {
        "slug": "renters",
        "policy_type": "renters",
        "title": "Renters Coverage",
        "form": "RT-2040",
        "policy_id": "POL-RENT-0004",
        "deductible": 500,
        "limit": 30000,
        "summary": (
            "This form covers the personal property of a tenant occupying a rented "
            "dwelling or unit, and provides limited coverage for improvements made by "
            "the tenant. It does not cover the structure, which remains the "
            "responsibility of the property owner under Form HD-1120."
        ),
        "covered": (
            "We cover the insured's personal property against fire, lightning, "
            "windstorm, hail, explosion, theft, vandalism, falling objects, and Sudden "
            "and Accidental Discharge of water from plumbing serving the unit, "
            "including discharge originating in a neighbouring unit. Tenant "
            "improvements such as installed shelving and flooring are covered up to ten "
            "percent of the form limit. Loss of use is payable for reasonable "
            "additional living expense for up to twelve months where the unit is "
            "rendered uninhabitable by a covered peril. The sub-limits stated in Form "
            "HP-1155, Section 2, apply equally to this form."
        ),
        "exclusions": [
            "Damage to the building structure, fixtures owned by the landlord, and "
            "common areas, none of which are the tenant's insurable interest.",
            "Loss caused by Surface Water or flood entering the unit, including a "
            "ground-floor or basement unit affected by rising water. See Form FX-0090.",
            "Property of roommates, subtenants, or guests who are not named insureds on "
            "the declarations page.",
            "Loss occurring while the unit is sublet through a short-term rental "
            "platform, unless a home-sharing endorsement is attached.",
        ],
        "limits_note": (
            "The per-occurrence limit is ${limit:,} with a deductible of "
            "${deductible:,}. Loss of use is payable in addition to the form limit, "
            "capped at twenty percent of that limit."
        ),
        "interaction": (
            "Where the tenant owns business equipment above the $3,000 sub-limit, Form "
            "BE-7720 is required. Injury to a visitor within the unit is addressed "
            "under Form PL-5000, and their medical costs may be payable under Form "
            "MP-0450 without regard to fault."
        ),
                "conditions": (
            "The insured must notify the landlord and, where theft or vandalism "
            "is alleged, the police, before submitting a claim. An inventory of "
            "damaged property is required on the same terms as Form HP-1155. "
            "Where loss of use is claimed, receipts for accommodation and "
            "additional meal costs must be provided, and only the amount above "
            "the insured's normal living expense is payable."
        ),
        "definitions": [
            ("Tenant Improvement", "an alteration or addition made by the insured to a "
             "unit the insured does not own."),
            ("Loss of Use", "reasonable additional living expense incurred because the "
             "unit is uninhabitable following a covered loss."),
        ],
    },
    {
        "slug": "personal-liability",
        "policy_type": "personal_liability",
        "title": "Personal Liability Coverage",
        "form": "PL-5000",
        "policy_id": "POL-LIAB-0001",
        "deductible": 0,
        "limit": 300000,
        "summary": (
            "This form pays damages an insured becomes legally obligated to pay because "
            "of bodily injury or property damage to a third party caused by an "
            "Occurrence. It also pays the cost of defending a covered claim, in "
            "addition to the limit. It does not pay for injury to an insured or damage "
            "to the insured's own property."
        ),
        "covered": (
            "We will pay damages for bodily injury or property damage to others "
            "resulting from an Occurrence to which this coverage applies, including "
            "injuries occurring on the residence premises and injuries caused by an "
            "insured away from the premises. Defence costs, court expenses, and "
            "reasonable expenses incurred at our request are paid in addition to the "
            "limit and do not reduce it. Dog bite liability is included subject to the "
            "breed and prior-incident conditions in Section 5. We may settle any claim "
            "as we consider appropriate, and our duty to defend ends when the limit has "
            "been exhausted by payment of judgments or settlements."
        ),
        "exclusions": [
            "Bodily injury or property damage expected or intended by the insured, "
            "including the consequences of an intentional act even where the resulting "
            "harm was greater than intended.",
            "Liability arising from the ownership or operation of a motor vehicle, "
            "watercraft over twenty-five horsepower, or aircraft, which requires the "
            "applicable auto or specialty form.",
            "Liability arising out of a business conducted from the residence premises, "
            "including injury to a client visiting for a business purpose.",
            "Injury to an insured or to a resident of the insured's household, which is "
            "not injury to a third party.",
        ],
        "limits_note": (
            "The per-occurrence limit is ${limit:,}. No deductible applies to this "
            "form. Where multiple claimants arise from a single Occurrence, the limit "
            "applies to the occurrence in aggregate, not to each claimant."
        ),
        "interaction": (
            "Medical expenses of an injured third party may be payable without any "
            "finding of fault under Medical Payments to Others, Form MP-0450, and "
            "payment under that form is not an admission of liability under this one. "
            "Damage to the insured's own dwelling is a first-party matter under Form "
            "HD-1120."
        ),
                "conditions": (
            "The insured must forward every demand, notice, summons, and legal "
            "document received to us immediately, and must not make any payment, "
            "assume any obligation, or admit fault except at their own cost. The "
            "insured must cooperate in the defence, attend hearings and trials "
            "where required, and assist in securing evidence and witnesses. No "
            "legal action may be brought against us until the insured has fully "
            "complied with these conditions."
        ),
        "definitions": [
            ("Occurrence", "an accident, including continuous exposure to the same "
             "harmful conditions, that results in bodily injury or property damage "
             "during the policy period."),
            ("Bodily Injury", "physical harm, sickness, or disease sustained by a "
             "person, including death resulting from it."),
        ],
    },
    {
        "slug": "medical-payments",
        "policy_type": "medical_payments",
        "title": "Medical Payments to Others",
        "form": "MP-0450",
        "policy_id": "POL-LIAB-0009",
        "deductible": 0,
        "limit": 5000,
        "summary": (
            "This form pays reasonable and necessary medical expenses incurred by a "
            "person other than an insured who is injured on the residence premises or "
            "by an insured's activities, without any determination of fault. It is a "
            "goodwill coverage with a low limit and a strict time bar."
        ),
        "covered": (
            "We will pay necessary medical, surgical, x-ray, dental, ambulance, "
            "hospital, professional nursing, and funeral expenses incurred within three "
            "years of an accident causing bodily injury to a person who is not an "
            "insured. The person must have been on the residence premises with the "
            "permission of an insured, or injured off the premises by an insured's "
            "activity, by a condition of the premises, or by an animal owned by an "
            "insured. Payment is made regardless of whether the insured was negligent, "
            "and does not constitute an admission of liability under Form PL-5000."
        ),
        "exclusions": [
            "Expenses incurred more than three years after the date of the accident, "
            "regardless of when the condition was diagnosed.",
            "Injury to an insured or to any regular resident of the residence premises "
            "other than a residence employee.",
            "Injury arising from a business activity conducted on the premises, or to a "
            "person entitled to workers compensation benefits.",
            "Injury caused by a motor vehicle, watercraft, or aircraft operated by an "
            "insured, which is addressed under the applicable auto or specialty form.",
        ],
        "limits_note": (
            "The limit is ${limit:,} per injured person per accident. No deductible "
            "applies. This limit is separate from and does not reduce the limit of Form "
            "PL-5000."
        ),
        "interaction": (
            "Where an injured party pursues damages beyond medical expense, the claim "
            "is adjusted under Personal Liability Coverage, Form PL-5000, and any "
            "amount paid here is credited against a later liability settlement for the "
            "same Occurrence."
        ),
                "conditions": (
            "The injured person, or someone acting for them, must give us written "
            "proof of claim as soon as practicable and must authorise us to "
            "obtain the relevant medical records. We may require the injured "
            "person to submit to a physical examination by a physician of our "
            "choosing, at our expense, as often as is reasonably necessary. "
            "Payment may be made directly to the treating provider."
        ),
        "definitions": [
            ("Residence Employee", "a person employed by an insured to perform duties "
             "related to the residence premises."),
            ("Necessary Medical Expense", "an expense for treatment that is customary "
             "for the injury and provided by a licensed practitioner."),
        ],
    },
    {
        "slug": "roadside-assistance",
        "policy_type": "roadside_assistance",
        "title": "Roadside Assistance",
        "form": "RA-0075",
        "policy_id": "POL-AUTO-0044",
        "deductible": 0,
        "limit": 250,
        "summary": (
            "This form reimburses the cost of emergency roadside services for a Covered "
            "Auto that becomes disabled. It is a service reimbursement with a low "
            "per-occurrence limit and an annual usage cap; it is not physical damage "
            "coverage and pays nothing toward repair of the vehicle."
        ),
        "covered": (
            "We will reimburse reasonable charges for towing the disabled Covered Auto "
            "to the nearest qualified repair facility; roadside battery jump start; "
            "delivery of fuel, oil, or water, excluding the cost of the fluid itself; "
            "changing a flat tyre using the vehicle's own spare; locksmith service "
            "where keys are locked inside; and winching from a location adjacent to a "
            "public roadway. Service must be arranged through an approved provider or, "
            "where none is available, supported by an itemised receipt. Reimbursement "
            "is limited to four occurrences in any twelve-month period."
        ),
        "exclusions": [
            "The cost of parts, fuel, replacement tyres, and any repair work, all of "
            "which are the insured's responsibility.",
            "Towing from a location that is not adjacent to a public roadway, "
            "recovery of a vehicle from off-road or private terrain, and any recovery "
            "requiring specialised heavy equipment.",
            "Service for a vehicle that is not the Covered Auto shown on the "
            "declarations page, including a rental or borrowed vehicle.",
            "Any occurrence beyond the fourth in a twelve-month period, and any tow "
            "following a Collision Event, which is payable under Form AC-2210 instead.",
        ],
        "limits_note": (
            "The per-occurrence limit is ${limit:,}. No deductible applies. Amounts "
            "above the per-occurrence limit are the insured's responsibility even where "
            "the annual usage cap has not been reached."
        ),
        "interaction": (
            "Towing from the scene of a covered collision is included within Form "
            "AC-2210 and does not consume an occurrence under this form. Where a "
            "vehicle is disabled by a comprehensive peril such as animal strike, the tow "
            "may be claimed under Form AX-3105 without a separate deductible."
        ),
                "conditions": (
            "Service should be requested through the assistance line so the "
            "provider can be dispatched and billed directly. Where the insured "
            "arranges service independently, an itemised receipt showing the "
            "date, location, service performed, and vehicle registration is "
            "required for reimbursement, and claims must be submitted within "
            "ninety days of the service date. We may decline reimbursement where "
            "the receipt does not identify the Covered Auto."
        ),
        "definitions": [
            ("Disabled", "unable to be driven safely under its own power from the "
             "location at which the service is requested."),
            ("Approved Provider", "a service operator dispatched through our assistance "
             "line or listed in the provider directory."),
        ],
    },
    {
        "slug": "rental-reimbursement",
        "policy_type": "rental_reimbursement",
        "title": "Rental Reimbursement",
        "form": "RR-0310",
        "policy_id": "POL-AUTO-0052",
        "deductible": 0,
        "limit": 900,
        "summary": (
            "This form reimburses the cost of a substitute vehicle while a Covered Auto "
            "is out of service because of a loss payable under Form AC-2210 or Form "
            "AX-3105. It pays a daily rate up to a maximum number of days and is "
            "contingent on the underlying claim being covered."
        ),
        "covered": (
            "We will reimburse the actual cost of renting a substitute vehicle of "
            "comparable class, up to $30 per day for a maximum of thirty days, "
            "beginning on the date the Covered Auto is delivered to a repair facility "
            "or, in the case of theft, forty-eight hours after the theft is reported to "
            "police. Reimbursement continues until the repair is complete, the vehicle "
            "is recovered and repaired, or a total-loss settlement is offered, "
            "whichever occurs first. Taxes and mandatory fees charged by the rental "
            "company are included; optional insurance and fuel are not."
        ),
        "exclusions": [
            "Rental incurred where the underlying physical damage claim is denied, "
            "withdrawn, or falls entirely within the deductible.",
            "Days beyond the thirtieth, and any daily amount above the stated daily "
            "rate, regardless of vehicle availability or class.",
            "Rental during a period when the Covered Auto remained drivable and the "
            "insured chose to defer repair.",
            "Optional damage waivers, fuel, mileage overage, additional driver fees, "
            "and delivery charges billed by the rental company.",
        ],
        "limits_note": (
            "The aggregate limit is ${limit:,} per occurrence, representing thirty days "
            "at the stated daily rate. No deductible applies to this form, but the "
            "deductible under the underlying form is not reimbursed here."
        ),
        "interaction": (
            "Eligibility depends entirely on the underlying claim. If the collision "
            "claim under Form AC-2210 is denied, nothing is payable here even where a "
            "rental was genuinely incurred. Substitute transport following a "
            "non-collision loss is payable only where Form AX-3105 responds."
        ),
                "conditions": (
            "The insured must provide the rental agreement and the final invoice "
            "showing the daily rate, the rental period, and any charges excluded "
            "by this form. The repair facility's records may be requested to "
            "establish the dates on which the Covered Auto was out of service. "
            "Reimbursement is made after the rental ends unless the rental period "
            "exceeds fourteen days, in which case interim payment may be "
            "requested."
        ),
        "definitions": [
            ("Substitute Vehicle", "a rented vehicle of class comparable to the Covered "
             "Auto, obtained from a commercial rental operator."),
            ("Out of Service", "undergoing repair, or awaiting repair with a documented "
             "facility booking, following a covered loss."),
        ],
    },
    {
        "slug": "business-equipment-rider",
        "policy_type": "business_equipment",
        "title": "Business Equipment Rider",
        "form": "BE-7720",
        "policy_id": "POL-HOME-0033",
        "deductible": 750,
        "limit": 15000,
        "summary": (
            "This rider extends coverage to property used in a trade or business "
            "conducted from the residence premises, above the $3,000 sub-limit in Form "
            "HP-1155. It covers equipment, not income, and excludes stock held for "
            "sale beyond a stated amount."
        ),
        "covered": (
            "We cover business equipment owned by an insured and used in a trade or "
            "business conducted from the residence premises, against the same perils "
            "listed in Form HP-1155, Section 2. Covered items include computers, "
            "cameras, tools, and specialised instruments. Equipment is covered while "
            "temporarily off the residence premises, including at a client site or in "
            "transit, up to fifty percent of the rider limit. Settlement is on a "
            "replacement cost basis for equipment less than five years old and on an "
            "actual cash value basis thereafter. Stock and materials held for sale are "
            "covered to $2,500 in aggregate."
        ),
        "exclusions": [
            "Loss of business income, extra expense, and any consequential loss arising "
            "from the inability to use the equipment, none of which is property damage.",
            "Data, software, and the cost of recreating records, whether stored on a "
            "covered device or elsewhere.",
            "Equipment used in a business conducted away from the residence premises, "
            "including a separate commercial location.",
            "Loss caused by Surface Water or flood, consistent with Form FX-0090, "
            "including equipment stored in a basement office.",
        ],
        "limits_note": (
            "The per-occurrence limit is ${limit:,} with a deductible of "
            "${deductible:,}. This limit is in addition to the Form HP-1155 limit but "
            "the $3,000 business property sub-limit in that form is absorbed by, not "
            "added to, this rider."
        ),
        "interaction": (
            "Property that is not business property remains covered under Form HP-1155. "
            "Injury to a client visiting the residence premises for a business purpose "
            "is excluded under Form PL-5000 and is not made payable by this rider."
        ),
                "conditions": (
            "The insured must maintain a schedule of business equipment showing "
            "the description, serial number where applicable, purchase date, and "
            "purchase price of each item, and must provide it at the time of "
            "claim. Equipment purchased after the rider was issued is covered "
            "automatically for sixty days, after which it must be added to the "
            "schedule. Business use must be substantiated on request."
        ),
        "definitions": [
            ("Business Equipment", "property used to generate income in a trade or "
             "business, excluding stock held for sale beyond the stated amount."),
            ("Replacement Cost", "the cost to replace with new property of like kind "
             "and quality, without deduction for depreciation."),
        ],
    },
]
