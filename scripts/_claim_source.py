"""Incident cores and narrative fragments used to synthesise claims.

Why cores plus fragments rather than whole hand-written narratives: 120 claims
need to vary in register, length, and quality of writing without varying in the
underlying facts, because the facts are what the golden labels assert. A core
fixes what happened; the fragment pools and the register decide how badly it
gets told.

Each core carries the labels the golden set needs:
  text     -- the incident, first person, one or two sentences
  mention  -- terms a correct rationale must contain
  chunks   -- chunk ids in the policy corpus that govern this claim

Categories:
  covered        -- clearly payable under the filed policy_type
  excluded       -- clearly barred by a stated exclusion
  ambiguous      -- genuinely arguable; a competent adjuster would hesitate
  contradiction  -- narrative describes a peril belonging to a DIFFERENT form
                    than the one the claim was filed under. These exist to test
                    whether the Reviewer catches the inconsistency.
  high_value     -- payable in principle but above the auto-decide ceiling
"""

from __future__ import annotations


def _c(text: str, mention: list[str], chunks: list[str]) -> dict:
    return {"text": text, "mention": mention, "chunks": chunks}


INCIDENTS: dict[str, dict[str, list[dict]]] = {
    "auto_collision": {
        "covered": [
            _c("I rear-ended the car in front of me when traffic stopped short on the "
               "off-ramp. My front bumper and radiator are wrecked.",
               ["collision", "deductible"],
               ["auto-collision#what-is-covered", "auto-collision#deductible-and-limits"]),
            _c("I clipped a guardrail on an icy bend and the whole passenger side is "
               "caved in. Nobody else was involved.",
               ["collision", "guardrail"],
               ["auto-collision#what-is-covered"]),
        ],
        "excluded": [
            _c("The damage happened during a track day at the local circuit. It was a "
               "timed run and I lost the back end going into turn three.",
               ["racing", "exclusion"],
               ["auto-collision#exclusions"]),
            _c("The transmission failed while I was driving and the car coasted into a "
               "kerb. I want the transmission replaced under the collision cover.",
               ["mechanical", "exclusion", "wear"],
               ["auto-collision#exclusions"]),
        ],
        "ambiguous": [
            _c("I was doing a grocery delivery run for an app when someone reversed into "
               "me in the car park. I only do it a few hours a week, it is not my job.",
               ["compensation", "delivery", "exclusion"],
               ["auto-collision#exclusions", "auto-collision#interaction-with-other-coverages"]),
        ],
        "contradiction": [
            _c("Water came up the street during the storm and my car was sitting in it "
               "up to the door handles overnight. The engine will not turn over now.",
               ["flood", "comprehensive"],
               ["flood-exclusion#interaction-with-other-coverages",
                "auto-comprehensive#what-is-covered"]),
        ],
        "high_value": [
            _c("Head-on collision at speed on the highway. The vehicle is a write-off and "
               "there is damage to the barrier as well.",
               ["collision", "total loss", "escalate"],
               ["auto-collision#what-is-covered", "auto-collision#deductible-and-limits"]),
        ],
    },
    "auto_comprehensive": {
        "covered": [
            _c("A deer came out of the treeline and I hit it square on. Bonnet, grille "
               "and one headlight are gone.",
               ["animal", "comprehensive"],
               ["auto-comprehensive#what-is-covered"]),
            _c("Someone smashed the rear window overnight and took the stereo out of the "
               "dash. There is glass everywhere.",
               ["theft", "vandalism", "glass"],
               ["auto-comprehensive#what-is-covered"]),
        ],
        "excluded": [
            _c("The car was taken from outside the shop. I had left it running with the "
               "keys in it because I was only going to be a minute.",
               ["keys", "exclusion", "theft"],
               ["auto-comprehensive#exclusions"]),
            _c("My aftermarket sound system and the wrap I had done were ruined. None of "
               "it was factory fitted but it cost me a lot.",
               ["aftermarket", "custom equipment", "exclusion"],
               ["auto-comprehensive#exclusions"]),
        ],
        "ambiguous": [
            _c("The car was parked on a slope, rolled, and ended up in the creek that had "
               "burst its banks. I cannot tell you what did the damage first.",
               ["flood", "collision", "proximate cause"],
               ["auto-comprehensive#interaction-with-other-coverages",
                "flood-exclusion#interaction-with-other-coverages"]),
        ],
        "contradiction": [
            _c("I misjudged the width of my garage door and scraped the entire length of "
               "the car against the frame. Deep gouges down both panels.",
               ["collision", "impact", "AC-2210"],
               ["auto-comprehensive#exclusions", "auto-collision#what-is-covered"]),
        ],
        "high_value": [
            _c("The car was destroyed by fire in the driveway. Fire service says it "
               "started in the engine bay. Total loss, it is a recent model.",
               ["fire", "total loss", "escalate"],
               ["auto-comprehensive#what-is-covered",
                "auto-comprehensive#deductible-and-limits"]),
        ],
    },
    "homeowners_dwelling": {
        "covered": [
            _c("A pipe in the upstairs bathroom wall burst on Tuesday morning and brought "
               "down part of the ceiling below before I got the stopcock off.",
               ["sudden and accidental discharge", "covered"],
               ["homeowners-dwelling#what-is-covered",
                "homeowners-dwelling#definitions"]),
            _c("Wind took about a third of the roof tiles off in the gale and there is "
               "damage to the rafters underneath.",
               ["windstorm", "dwelling"],
               ["homeowners-dwelling#what-is-covered"]),
        ],
        "excluded": [
            _c("There is a slow leak behind the shower that has been going on for the "
               "best part of a year. The floor joists have rotted right through.",
               ["seepage", "gradual", "exclusion"],
               ["homeowners-dwelling#exclusions", "homeowners-dwelling#definitions"]),
            _c("A crack has opened across the front of the house and the door frames are "
               "out of square. The surveyor says the ground has moved.",
               ["earth movement", "settling", "exclusion"],
               ["homeowners-dwelling#exclusions"]),
        ],
        "ambiguous": [
            _c("The storm was a named one and the water got in where the flashing "
               "lifted. I do not know whether the wind or the rain did it.",
               ["named storm deductible", "windstorm"],
               ["homeowners-dwelling#deductible-and-limits",
                "homeowners-dwelling#exclusions"]),
        ],
        "contradiction": [
            _c("The drains backed up during the downpour and sewage came through the "
               "downstairs floor drain into the hall.",
               ["backup", "WD-114", "endorsement"],
               ["water-damage-endorsement#what-is-covered",
                "homeowners-dwelling#interaction-with-other-coverages"]),
        ],
        "high_value": [
            _c("Fire started in the kitchen and spread through the roof space. Most of "
               "the upper floor is gone and the rest is smoke damaged.",
               ["fire", "dwelling", "escalate"],
               ["homeowners-dwelling#what-is-covered",
                "homeowners-dwelling#deductible-and-limits"]),
        ],
    },
    "homeowners_personal_property": {
        "covered": [
            _c("Someone forced the back door while we were away and took the television, "
               "a laptop and my wife's camera.",
               ["theft", "personal property"],
               ["homeowners-personal-property#what-is-covered"]),
            _c("The washing machine hose let go and soaked the rug, the sofa and a "
               "bookcase in the next room.",
               ["sudden and accidental discharge", "personal property"],
               ["homeowners-personal-property#what-is-covered"]),
        ],
        "excluded": [
            _c("My grandmother's ring is not where I left it. Nothing was broken into "
               "and I cannot say for certain it was taken.",
               ["mysterious disappearance", "exclusion"],
               ["homeowners-personal-property#exclusions"]),
            _c("The basement took on water in the wet weather and everything stored down "
               "there is ruined, including boxes of books and a freezer.",
               ["surface water", "flood", "exclusion"],
               ["homeowners-personal-property#exclusions",
                "flood-exclusion#exclusions"]),
        ],
        "ambiguous": [
            _c("The jewellery taken in the break-in was appraised at nine thousand. I "
               "know there is some sort of cap but the appraisal is recent.",
               ["sub-limit", "jewelry", "theft"],
               ["homeowners-personal-property#what-is-covered",
                "homeowners-personal-property#deductible-and-limits"]),
        ],
        "contradiction": [
            _c("The camera gear and two laptops that were stolen are what I use for my "
               "photography business. Total is about eleven thousand.",
               ["business property", "BE-7720", "sub-limit"],
               ["homeowners-personal-property#exclusions",
                "business-equipment-rider#what-is-covered"]),
        ],
        "high_value": [
            _c("We lost effectively the entire contents of the house in the fire, "
               "including furniture, clothing and electronics throughout.",
               ["fire", "contents", "escalate"],
               ["homeowners-personal-property#what-is-covered",
                "homeowners-personal-property#deductible-and-limits"]),
        ],
    },
    "water_damage_endorsement": {
        "covered": [
            _c("The main sewer line backed up and came out of the downstairs shower and "
               "toilet. The whole ground floor had to be stripped.",
               ["backup", "sewer", "covered"],
               ["water-damage-endorsement#what-is-covered"]),
            _c("Power went out in the storm, the sump pump stopped, and the basement "
               "filled from the sump. Drying and remediation took a week.",
               ["sump pump", "backup", "covered"],
               ["water-damage-endorsement#what-is-covered"]),
        ],
        "excluded": [
            _c("Rain pooled against the side of the house and came in under the "
               "foundation into the basement. There is a foot of mud down there.",
               ["surface water", "flood", "exclusion"],
               ["water-damage-endorsement#exclusions", "flood-exclusion#exclusions"]),
            _c("The pump had been making a noise for months and the inspector flagged it "
               "last year. It finally quit and the basement went under.",
               ["maintenance", "failure to maintain", "exclusion"],
               ["water-damage-endorsement#exclusions"]),
        ],
        "ambiguous": [
            _c("The street flooded and at the same time the drain backed up into the "
               "basement. I cannot tell which came in first and neither can the plumber.",
               ["efficient proximate cause", "surface water", "backup"],
               ["water-damage-endorsement#interaction-with-other-coverages",
                "water-damage-endorsement#definitions"]),
        ],
        "contradiction": [
            _c("A supply pipe under the kitchen sink split and ran for a couple of hours "
               "before I noticed. Cabinets and flooring are destroyed.",
               ["sudden and accidental discharge", "HD-1120"],
               ["homeowners-dwelling#what-is-covered",
                "water-damage-endorsement#interaction-with-other-coverages"]),
        ],
        "high_value": [
            _c("Sewer backup went through the ground floor and into the finished "
               "basement. Remediation quote covers structure, contents and mould works.",
               ["backup", "limit", "escalate"],
               ["water-damage-endorsement#what-is-covered",
                "water-damage-endorsement#deductible-and-limits"]),
        ],
    },
    "flood_exclusion": {
        "covered": [
            _c("Filing this so it is on record: the adjuster told me the flood form "
               "itself never pays and I want that confirmed in writing.",
               ["no coverage", "exclusionary form"],
               ["flood-exclusion#coverage-summary", "flood-exclusion#what-is-covered"]),
            _c("My car was submerged in the flood. I was told to file here but also told "
               "vehicles are treated differently.",
               ["covered auto", "AX-3105", "comprehensive"],
               ["flood-exclusion#interaction-with-other-coverages",
                "auto-comprehensive#what-is-covered"]),
        ],
        "excluded": [
            _c("The river came up and through the ground floor. Everything below waist "
               "height is destroyed.",
               ["flood", "exclusion"],
               ["flood-exclusion#exclusions"]),
            _c("The retaining wall at the back gave way after days of rain and the "
               "hillside came down against the house.",
               ["mudflow", "earth movement", "exclusion"],
               ["flood-exclusion#exclusions"]),
        ],
        "ambiguous": [
            _c("The council opened the flood gates upstream and that is what put water "
               "through my property. It was a deliberate release, not weather.",
               ["dam", "levee", "flood control", "exclusion"],
               ["flood-exclusion#exclusions"]),
        ],
        "contradiction": [
            _c("Groundwater has been seeping through the basement wall for two winters "
               "and the plaster is coming away.",
               ["water below the surface", "seepage", "exclusion"],
               ["flood-exclusion#exclusions", "homeowners-dwelling#exclusions"]),
        ],
        "high_value": [
            _c("Storm surge went right through the property. The claim covers structure "
               "and contents together on the estimate.",
               ["flood", "surge", "exclusion", "escalate"],
               ["flood-exclusion#exclusions", "flood-exclusion#deductible-and-limits"]),
        ],
    },
}

INCIDENTS.update({
    "renters": {
        "covered": [
            _c("The flat was broken into through the balcony door and my laptop, "
               "television and bike were taken.",
               ["theft", "personal property", "tenant"],
               ["renters#what-is-covered"]),
            _c("The tenant above me left a tap running and it came through my ceiling "
               "onto the bed and wardrobe.",
               ["sudden and accidental discharge", "neighbouring unit"],
               ["renters#what-is-covered"]),
        ],
        "excluded": [
            _c("The kitchen cabinets and the built-in oven were damaged. They belong to "
               "the landlord but I am the one living here.",
               ["structure", "landlord", "exclusion"],
               ["renters#exclusions"]),
            _c("My flatmate's things were taken in the same burglary. He is not on the "
               "policy but he lives here too.",
               ["roommate", "named insured", "exclusion"],
               ["renters#exclusions"]),
        ],
        "ambiguous": [
            _c("The damage happened while I had the place listed on a short-term rental "
               "site. The guests left a tap running.",
               ["short-term rental", "home-sharing", "exclusion"],
               ["renters#exclusions"]),
        ],
        "contradiction": [
            _c("Water came in at street level during the storm and soaked everything in "
               "the ground floor flat.",
               ["surface water", "flood", "exclusion"],
               ["renters#exclusions", "flood-exclusion#exclusions"]),
        ],
        "high_value": [
            _c("Fire in the building destroyed the contents of my unit entirely and I "
               "have been in a hotel since. Contents plus loss of use.",
               ["fire", "loss of use", "escalate"],
               ["renters#what-is-covered", "renters#deductible-and-limits"]),
        ],
    },
    "personal_liability": {
        "covered": [
            _c("My dog bit a neighbour on the hand in my garden. She needed stitches and "
               "is now talking about a claim.",
               ["bodily injury", "occurrence", "liability"],
               ["personal-liability#what-is-covered"]),
            _c("A visitor tripped on a loose step at my front door and broke a wrist. He "
               "has instructed a solicitor.",
               ["bodily injury", "premises", "defence costs"],
               ["personal-liability#what-is-covered"]),
        ],
        "excluded": [
            _c("I lost my temper and put a chair through his windscreen. I did not mean "
               "for it to be that bad but I did throw it.",
               ["intentional", "expected or intended", "exclusion"],
               ["personal-liability#exclusions"]),
            _c("I reversed into somebody at the shops and they are claiming for a neck "
               "injury. I want it handled under my liability cover.",
               ["motor vehicle", "exclusion"],
               ["personal-liability#exclusions"]),
        ],
        "ambiguous": [
            _c("A client came to the house to collect an order and slipped in the hall. "
               "I only run the business from here part time.",
               ["business", "exclusion", "premises"],
               ["personal-liability#exclusions"]),
        ],
        "contradiction": [
            _c("My son fell off the trampoline in our garden and broke his arm. I want "
               "the medical bills paid.",
               ["insured", "household resident", "exclusion", "MP-0450"],
               ["personal-liability#exclusions", "medical-payments#exclusions"]),
        ],
        "high_value": [
            _c("The injury on my property was serious and the other side's demand is "
               "well into six figures, plus their legal costs.",
               ["bodily injury", "limit", "escalate"],
               ["personal-liability#what-is-covered",
                "personal-liability#deductible-and-limits"]),
        ],
    },
    "medical_payments": {
        "covered": [
            _c("A friend cut her hand badly on my garden gate and went to urgent care. I "
               "would like her bill covered, fault aside.",
               ["medical payments", "without regard to fault"],
               ["medical-payments#what-is-covered"]),
            _c("The window cleaner slipped on my path and went to hospital by ambulance. "
               "The ambulance and x-ray bills came to me.",
               ["ambulance", "necessary medical expense"],
               ["medical-payments#what-is-covered"]),
        ],
        "excluded": [
            _c("The accident was four years ago and she is only now having the surgery "
               "for it. The injury definitely happened on my property.",
               ["three years", "time bar", "exclusion"],
               ["medical-payments#exclusions"]),
            _c("My daughter, who lives with us, hurt herself on the stairs and I want the "
               "treatment paid under this cover.",
               ["resident", "insured", "exclusion"],
               ["medical-payments#exclusions"]),
        ],
        "ambiguous": [
            _c("The person hurt was doing paid work on the house at the time. He is a "
               "sole trader, not someone I employ regularly.",
               ["residence employee", "workers compensation", "business"],
               ["medical-payments#exclusions", "medical-payments#definitions"]),
        ],
        "contradiction": [
            _c("They are not just claiming treatment costs, they want damages for time "
               "off work and are threatening to sue.",
               ["damages", "PL-5000", "liability"],
               ["medical-payments#interaction-with-other-coverages",
                "personal-liability#what-is-covered"]),
        ],
        "high_value": [
            _c("The injured party's hospital and rehabilitation costs are far beyond the "
               "small limit on this cover and they have sent the full bill.",
               ["limit", "escalate", "medical"],
               ["medical-payments#deductible-and-limits",
                "medical-payments#interaction-with-other-coverages"]),
        ],
    },
    "roadside_assistance": {
        "covered": [
            _c("Battery died in the supermarket car park and I had to have someone come "
               "out to jump it.",
               ["jump start", "roadside"],
               ["roadside-assistance#what-is-covered"]),
            _c("Flat tyre on the dual carriageway. The recovery driver put my spare on at "
               "the roadside.",
               ["flat tyre", "roadside"],
               ["roadside-assistance#what-is-covered"]),
        ],
        "excluded": [
            _c("Got stuck in mud on a forest track about two miles off the road. Needed a "
               "proper recovery truck with a winch to drag it out.",
               ["off-road", "specialised equipment", "exclusion"],
               ["roadside-assistance#exclusions"]),
            _c("This is the fifth call-out this year. The tyre needed replacing as well "
               "and I paid for the tyre on the spot.",
               ["four occurrences", "parts", "exclusion"],
               ["roadside-assistance#exclusions"]),
        ],
        "ambiguous": [
            _c("The car was towed from the hard shoulder but the nearest garage was shut, "
               "so it went on to my usual one, about forty miles.",
               ["nearest qualified repair facility", "towing"],
               ["roadside-assistance#what-is-covered",
                "roadside-assistance#deductible-and-limits"]),
        ],
        "contradiction": [
            _c("The tow was from the scene of the crash where I went into the back of a "
               "van. Recovery cost me two hundred.",
               ["collision", "AC-2210", "towing"],
               ["roadside-assistance#interaction-with-other-coverages",
                "auto-collision#what-is-covered"]),
        ],
        "high_value": [
            _c("The recovery invoice is enormous because the vehicle had to be lifted out "
               "with a crane and stored for two weeks.",
               ["per-occurrence limit", "escalate", "recovery"],
               ["roadside-assistance#deductible-and-limits",
                "roadside-assistance#exclusions"]),
        ],
    },
    "rental_reimbursement": {
        "covered": [
            _c("My car has been in the body shop for eleven days after the collision "
               "claim and I have been paying for a hire car.",
               ["substitute vehicle", "daily rate"],
               ["rental-reimbursement#what-is-covered"]),
            _c("Car was stolen and not recovered. I hired something two days after "
               "reporting it to the police and still have it.",
               ["theft", "forty-eight hours", "substitute vehicle"],
               ["rental-reimbursement#what-is-covered"]),
        ],
        "excluded": [
            _c("The damage claim was turned down in the end, but I had already had the "
               "hire car for three weeks by then.",
               ["underlying claim", "denied", "exclusion"],
               ["rental-reimbursement#exclusions"]),
            _c("I hired a larger vehicle at ninety a day and kept it for forty-five days "
               "while I decided what to do about repairs.",
               ["daily rate", "thirty days", "exclusion"],
               ["rental-reimbursement#exclusions"]),
        ],
        "ambiguous": [
            _c("The car was still drivable but the boot would not shut, so I hired "
               "something while waiting for the parts to come in.",
               ["out of service", "drivable", "deferred repair"],
               ["rental-reimbursement#exclusions",
                "rental-reimbursement#definitions"]),
        ],
        "contradiction": [
            _c("I am claiming the thousand pound deductible from the repair bill back, "
               "since I had to pay it before they released the car.",
               ["deductible", "not reimbursed", "underlying form"],
               ["rental-reimbursement#deductible-and-limits"]),
        ],
        "high_value": [
            _c("Repairs have dragged on for four months with a specialist vehicle and the "
               "hire bill has run well past what I expected.",
               ["aggregate limit", "thirty days", "escalate"],
               ["rental-reimbursement#deductible-and-limits",
                "rental-reimbursement#exclusions"]),
        ],
    },
    "business_equipment": {
        "covered": [
            _c("My work laptop and two lenses were stolen from the home office during the "
               "break-in.",
               ["business equipment", "theft", "rider"],
               ["business-equipment-rider#what-is-covered"]),
            _c("A power surge in the storm took out the desktop workstation and the "
               "printer I use for client work.",
               ["business equipment", "covered peril"],
               ["business-equipment-rider#what-is-covered"]),
        ],
        "excluded": [
            _c("I could not take on work for three weeks while I waited for the "
               "replacement gear, so I am claiming the lost bookings as well.",
               ["business income", "consequential", "exclusion"],
               ["business-equipment-rider#exclusions"]),
            _c("The drive that failed had eight years of client files on it and the "
               "recovery quote is more than the drive cost.",
               ["data", "software", "exclusion"],
               ["business-equipment-rider#exclusions"]),
        ],
        "ambiguous": [
            _c("The kit was stolen from my van outside a client's office. I was working "
               "away from home that week.",
               ["off the residence premises", "fifty percent", "transit"],
               ["business-equipment-rider#what-is-covered",
                "business-equipment-rider#exclusions"]),
        ],
        "contradiction": [
            _c("The equipment was in the basement office and the basement took on water "
               "when the ground flooded.",
               ["surface water", "flood", "exclusion"],
               ["business-equipment-rider#exclusions", "flood-exclusion#exclusions"]),
        ],
        "high_value": [
            _c("The whole studio setup was taken, cameras, lighting, computers and "
               "backup drives. The schedule of items runs to two pages.",
               ["rider limit", "escalate", "business equipment"],
               ["business-equipment-rider#deductible-and-limits",
                "business-equipment-rider#what-is-covered"]),
        ],
    },
})
