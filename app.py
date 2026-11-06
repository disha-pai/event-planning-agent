from datetime import date
import hashlib

import streamlit as st


def get_event_style(event_type: str) -> str:
    """Choose a few event-specific planning hints from the user's description."""
    event_name = event_type.lower()

    if any(word in event_name for word in ("workshop", "training", "class")):
        return "workshop"
    if any(word in event_name for word in ("conference", "seminar", "lecture", "talk")):
        return "talk"
    if any(word in event_name for word in ("concert", "music", "festival", "performance")):
        return "performance"
    if any(word in event_name for word in ("fundraiser", "charity", "fundraising")):
        return "fundraiser"
    if any(word in event_name for word in ("outdoor", "sports", "sport", "race")):
        return "outdoor"
    if any(word in event_name for word in ("social", "party", "networking", "mixer")):
        return "social"

    return "general"


def get_timeline_hint(days_until_event: int) -> str:
    """Return a simple planning hint based on how soon the event takes place."""
    if days_until_event < 0:
        return "The selected date has passed. Confirm whether it is correct before using these timeline suggestions."
    if days_until_event <= 6:
        return "The event is soon: focus on confirmations, final checks, and clear day-of instructions."
    if days_until_event <= 29:
        return "There are a few weeks left: prioritize the venue, registration, and sharing the event details."
    if days_until_event <= 90:
        return "There is time to compare options: settle the venue and schedule, then start publicity and registration."
    return "There is plenty of lead time: plan in stages and set dates for the main decisions and announcements."


def build_checklist(
    event_type: str, event_date: date, attendees: int, budget: float
) -> list[dict[str, str]]:
    """Build practical suggestions; this function never performs event actions."""
    style = get_event_style(event_type)
    is_outdoor = any(
        word in event_type.lower() for word in ("outdoor", "sports", "sport", "race")
    )
    days_until_event = (event_date - date.today()).days
    timeline_hint = get_timeline_hint(days_until_event)
    per_person_budget = budget / attendees

    venue_type = "an indoor space"
    if is_outdoor or style == "outdoor":
        venue_type = "an outdoor site with an indoor or weather backup"
    elif style == "performance":
        venue_type = "a space with suitable sound and audience seating"
    elif style == "workshop":
        venue_type = "a room with tables and a usable presentation area"

    if budget == 0:
        venue_budget_hint = "Start with free campus or community spaces because no budget is entered."
    else:
        venue_budget_hint = (
            f"That is {per_person_budget:.2f} per attendee. Compare free options first; "
            f"a suggested venue spending cap is "
            f"{budget * 0.25:.2f} (25% of the entered budget)."
        )

    if attendees <= 30:
        registration_hint = "A simple RSVP list may be enough; set a clear response deadline."
    elif attendees >= 100:
        registration_hint = (
            "Consider a registration form with a capacity limit and waitlist; "
            "collect only information you need."
        )
    else:
        registration_hint = (
            "Use a simple registration form or RSVP list and track responses against capacity."
        )

    if style == "workshop":
        run_of_show = "Outline a welcome, learning/activity blocks, a break, and time for questions."
        equipment = "List presentation equipment, a board or flip chart, and any workshop materials."
    elif style == "talk":
        run_of_show = "Outline opening remarks, talk segments, transitions, and a Q&A."
        equipment = "Check the presentation display and microphone needs; plan a sound check."
    elif style == "performance":
        run_of_show = "Draft set times, performer transitions, audience entry, and closing."
        equipment = "List sound, power, and stage needs; schedule a sound check with performers."
    elif style == "fundraiser":
        run_of_show = "Plan the welcome, main program, donation moment, and thank-you."
        equipment = "List presentation needs plus any clearly marked donation or information materials."
    elif style == "outdoor":
        run_of_show = "Plan arrival, activity blocks, breaks, and a weather-related backup schedule."
        equipment = "Check outdoor power, shade or shelter, first-aid arrangements, and weather backup needs."
    elif style == "social":
        run_of_show = "Plan a welcome, time to mingle or take part in an activity, and a closing."
        equipment = "List seating, signs, and any audio or activity supplies needed for the group."
    else:
        run_of_show = "Draft an agenda with a welcome, main activities, transitions, and a closing."
        equipment = "List the room's audio, display, seating, and power needs before the event."

    if is_outdoor and style != "outdoor":
        run_of_show += " Include a weather contingency and indoor backup."
        equipment += " Check weather backup and shelter arrangements."

    if attendees >= 40 and style not in ("performance", "talk"):
        equipment += " For this group size, check whether a microphone is needed."

    if budget == 0:
        equipment_budget_hint = "Prioritize borrowed or already-available equipment."
        publicity_budget_hint = "Use free campus, club, and community channels before considering paid promotion."
    else:
        equipment_budget_hint = (
            f"Check borrowed options first; a suggested equipment spending cap is "
            f"{budget * 0.15:.2f} (15% of the entered budget)."
        )
        publicity_budget_hint = (
            f"Start with free channels; a suggested publicity spending cap is "
            f"{budget * 0.10:.2f} (10% of the entered budget)."
        )

    if days_until_event < 0:
        publicity_hint = "Confirm the event date before scheduling announcements."
        communication_hint = "Confirm the date first, then prepare participant information for the correct schedule."
    elif days_until_event <= 6:
        publicity_hint = "Share a concise final announcement now, if registration is still open."
        communication_hint = "Prepare a reminder and day-of message with arrival and contact details."
    elif days_until_event <= 29:
        publicity_hint = "Share the announcement soon and include a registration deadline."
        communication_hint = "Plan a confirmation message and a reminder for the days before the event."
    else:
        publicity_hint = "Set an announcement date and a later reminder to keep publicity on schedule."
        communication_hint = "Plan a confirmation message and schedule participant reminders nearer the event."

    return [
        {
            "category": "Venue",
            "id": "venue",
            "task": f"Find {venue_type} that can accommodate about {attendees} attendees.",
            "detail": (
                f"Check capacity, accessibility, transport, and setup rules. {venue_budget_hint}"
            ),
        },
        {
            "category": "Venue",
            "id": "venue-backup",
            "task": "Compare the venue options and note a backup choice.",
            "detail": "Record questions to ask the venue; this app does not contact or book it.",
        },
        {
            "category": "Schedule",
            "id": "schedule",
            "task": "Draft the event run-of-show.",
            "detail": f"{run_of_show} Leave time for transitions and setup.",
        },
        {
            "category": "Schedule",
            "id": "timeline",
            "task": "Set planning milestones and a setup/cleanup window.",
            "detail": f"{timeline_hint} Add a short buffer for delays.",
        },
        {
            "category": "Equipment",
            "id": "equipment",
            "task": "Make an equipment and materials checklist.",
            "detail": f"{equipment} {equipment_budget_hint}",
        },
        {
            "category": "Equipment",
            "id": "equipment-test",
            "task": "Plan who will test the equipment and when.",
            "detail": "Include power, connections, and any accessibility-related equipment.",
        },
        {
            "category": "Publicity",
            "id": "publicity",
            "task": "Choose suitable publicity channels and prepare an announcement.",
            "detail": (
                f"Include the event type, date, location or location plan, and how to register. "
                f"{publicity_hint} {publicity_budget_hint}"
            ),
        },
        {
            "category": "Publicity",
            "id": "publicity-review",
            "task": "Set a date to review the announcement and registration response.",
            "detail": "Check that the information is accurate and accessible before sharing.",
        },
        {
            "category": "Registration",
            "id": "registration",
            "task": "Choose an RSVP or registration method and set a response deadline.",
            "detail": registration_hint,
        },
        {
            "category": "Registration",
            "id": "registration-info",
            "task": f"Plan how to track responses for the target of {attendees} attendees.",
            "detail": "Decide how to handle cancellations and whether a waitlist is useful.",
        },
        {
            "category": "Participant Communication",
            "id": "communication",
            "task": "Prepare a participant confirmation and reminder plan.",
            "detail": f"{communication_hint} Include the event date and start time.",
        },
        {
            "category": "Participant Communication",
            "id": "day-of-info",
            "task": "Prepare day-of instructions for participants.",
            "detail": "Include arrival details, accessibility information, and a contact person or channel.",
        },
    ]


st.set_page_config(page_title="Autonomous Event Planning Agent", page_icon="📋")
st.title("Autonomous Event Planning Agent")
st.write(
    "Build a practical event checklist using simple planning rules. "
    "Every item below is a suggestion for you to review and carry out."
)
st.info(
    "This app does not book venues, purchase equipment, register participants, "
    "or send messages."
)

with st.sidebar:
    st.header("Event details")
    event_type = st.text_input("Event name or type", value="College workshop")
    event_date = st.date_input("Event date", value=date.today())
    attendees = st.number_input(
        "Expected number of attendees", min_value=1, value=30, step=1
    )
    budget = st.number_input(
        "Total budget (enter any currency)", min_value=0.0, value=0.0, step=100.0
    )

attendee_count = int(attendees)
checklist = build_checklist(event_type, event_date, attendee_count, float(budget))
signature = (
    event_type.strip(),
    event_date.isoformat(),
    attendee_count,
    float(budget),
)
signature_id = hashlib.sha256(repr(signature).encode("utf-8")).hexdigest()[:12]

# Start a fresh checklist when the event details change.
if st.session_state.get("planning_signature") != signature:
    st.session_state["planning_signature"] = signature
    st.session_state["completed_tasks"] = {}

st.subheader(f"Suggestions for: {event_type.strip() or 'your event'}")
st.caption(
    f"Planning for {attendee_count} attendees. "
    f"Entered budget per attendee: {float(budget) / attendee_count:.2f}."
)

categories = list(dict.fromkeys(item["category"] for item in checklist))
completed_tasks = st.session_state["completed_tasks"]

for category in categories:
    st.header(category)
    for item in (task for task in checklist if task["category"] == category):
        task_key = f"task_{signature_id}_{item['id']}"
        is_complete = st.checkbox(item["task"], key=task_key)
        completed_tasks[item["id"]] = is_complete
        st.caption(item["detail"])

total_tasks = len(checklist)
completed_count = sum(completed_tasks.values())
progress_percent = round(completed_count / total_tasks * 100)

st.subheader("Planning progress")
st.progress(progress_percent, text=f"{progress_percent}% complete ({completed_count}/{total_tasks} tasks)")

unfinished_tasks = [item for item in checklist if not completed_tasks.get(item["id"], False)]
st.subheader("Unfinished suggested tasks")
if unfinished_tasks:
    for item in unfinished_tasks:
        st.write(f"- **{item['category']}:** {item['task']}")
else:
    st.success("All suggested tasks are marked complete.")
