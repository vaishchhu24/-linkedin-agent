ICPS = [
    {
        "id": "business-club",
        "name": "Business Club Member",
        "description": (
            "Early-stage HR consultants or solo HR founders who've made the leap from corporate—"
            "now looking to build a profitable and sustainable business model that aligns with their values and life."
        ),
        "who_they_are": [
            "Ambitious, heart-led HR professionals turned business owners.",
            "Seeking clarity, community, and momentum—not just tactics.",
            "Craving a blend of high-touch support and self-paced progress."
        ],
        "primary_goals": [
            "Attract and retain ideal clients consistently.",
            "Gain confidence in pricing, positioning, and pitching.",
            "Build systems that scale their time and energy.",
            "Feel less isolated in decision-making."
        ],
        "challenges": [
            "Scaling Uncertainty",
            "Loneliness",
            "DIY Fatigue",
            "Overgiving",
            "Imposter Syndrome",
            "Time Scarcity"
        ],
        "psychographics": [
            "Growth-oriented but wary of bro-marketing and superficial gurus.",
            "Deep care for clients and people, but need sharper commercial skills.",
            "Want to be seen, celebrated, and supported—not just sold to."
        ],
        "voice": "Supportive, strategic, empathetic, confidence-building"
    },
    {
        "id": "mastermind-member",
        "name": "Mastermind Member",
        "description": (
            "Established HR consultancy founders ready to scale with sophistication or fresh out corporate strategic-level individuals "
            "who want to scale rapidly and are not afraid to invest in that. Typically 3–7 years into business and have tasted success—"
            "but want more control, more clarity, and more cashflow."
        ),
        "who_they_are": [
            "Visionary, resilient, and often juggling a small team or associate model.",
            "Already earning, but now want to earn well—with less chaos.",
            "Hungry for peer-level challenge, higher thinking, and leveraged growth."
        ],
        "primary_goals": [
            "Refine their offer suite and raise pricing with confidence.",
            "Build a pipeline that doesn't rely on hustle or hope.",
            "Step into a thought-leader/advisory role with gravitas.",
            "Design a business model that doesn't depend on their every hour."
        ],
        "challenges": [
            "Strategic Stagnation",
            "Team Pressure",
            "Sophisticated Sales",
            "Time Leverage",
            "Brand Positioning",
            "Scaling with Integrity"
        ],
        "psychographics": [
            "Smart, self-aware, and emotionally intelligent.",
            "Not afraid of doing the work—but need it to count.",
            "Value strategy over tactics, connection over competition, and sustainability over speed."
        ],
        "voice": "Confident, polished, grounded in strategy, with high-trust language"
    }
]

def get_icp():
    """
    Get the Ideal Customer Profile for HR consultants.
    """
    return "HR consultants transitioning from corporate, aged 30-45, dealing with imposter syndrome and pricing challenges"

def get_icp_detailed():
    """
    Get detailed ICP information.
    """
    return {
        "icp_summary": "HR consultants transitioning from corporate, aged 30-45, dealing with imposter syndrome and pricing challenges",
        "demographics": {
            "age_range": "30-45",
            "experience": "5-15 years in HR",
            "background": "Corporate HR professionals"
        },
        "pain_points": [
            "Imposter syndrome",
            "Pricing challenges",
            "Client acquisition",
            "Loneliness in consulting",
            "Self-doubt"
        ],
        "goals": [
            "Build successful consulting business",
            "Replace corporate income",
            "Work with purpose",
            "Achieve work-life balance"
        ]
    }