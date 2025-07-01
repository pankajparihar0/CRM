from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import add_messages
from IPython.display import Image, display
from dotenv import load_dotenv
import os
import calendar
from datetime import datetime, timedelta,timezone
from zoneinfo import ZoneInfo
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal
load_dotenv()
memory = MemorySaver()
GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")
model=ChatGoogleGenerativeAI(model="gemini-2.5-flash")

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/calendar"]
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

class State(TypedDict):
    messages: Annotated[list, add_messages]
    next : str


def get_date(t_dalta: int | str) -> str:
    """Return date in ISO format for a given timedelta or weekday name.

    Args:
        t_dalta: Can be an int (for relative days) or str like 'monday', 'next friday'.

    Returns:
        ISO formatted date string.
    """
    now = datetime.now()

    if isinstance(t_dalta, int):
        delta = timedelta(days=t_dalta)
        return (now + delta).date().isoformat()

    # Handle weekday name (e.g., 'monday', 'next friday')
    t_dalta = t_dalta.lower().strip()
    weekdays = list(calendar.day_name)

    for i, day in enumerate(weekdays):
        if day.lower() in t_dalta:
            today_idx = now.weekday()
            days_ahead = (i - today_idx + 7) % 7
            if days_ahead == 0:
                days_ahead = 7 if "next" in t_dalta else 0
            return (now + timedelta(days=days_ahead)).date().isoformat()

    raise ValueError(f"Unrecognized date input: {t_dalta}")

# def book_for_day(day: str) -> str:
#     """Book a hotel slot for 'today' or 'tomorrow'."""
#     day = day.lower().strip()
#     if day == "today":
#         date = get_date(0)
#     elif day == "tomorrow":
#         date = get_date(1)
#     else:
#         return "I can only book for 'today' or 'tomorrow'."

#     return book_slot(date)

def get_event():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    now = datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    if not events:
        print("No upcoming events found.")
        return

    # Prints the start and name of the next 10 events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
    
    
def set_event(date,time):
    IST = timezone(timedelta(hours=0, minutes=00))
    start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    end_dt = start_dt + timedelta(minutes=5)
    formatted_start = start_dt.isoformat()
    formatted_end = end_dt.isoformat()
    event ={
  'summary': 'test',
  'location': 'Edquest office',
  'description': 'A test.',
  'start': {
    'dateTime': formatted_start,
    'timeZone': 'Asia/Calcutta',
  },
  'end': {
    'dateTime': formatted_end,
    'timeZone': 'Asia/Calcutta',
  }
}

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created:  {event.get('htmlLink')}")
    except Exception as error:
        print(f"error :- {error}")

def book_slot(date: str, time: str) -> str:
    """add event or schedule event in calender.
    Args:
        date: Date string in 'YYYY-MM-DD' format
        time: Time string in 'HH:MM' 24-hr format
    Returns:
        Success message
    """
    set_event(date,time)
    return f"event added in calender for {date} at {time}."
tools = [book_slot,get_date]

def next_node(state:State)->Literal["booking_bot","info_bot"]:
    next = state["next"]
    if next == "info":
        return "info_bot"
    else:
        return "booking_bot"


def chatBot(state: dict):
    sysMessage = SystemMessage(content="""You are an experienced customer care agent.
Your job is to analyze based on the conversition and last AI message, whether the user wants to:
1. Gather information / just chat — reply with `info`
2. Schedule a meeting or call — reply with `schedule`

Your response MUST be only one word: either `info` or `schedule`. Do not include anything else.""")

    response = model.invoke([sysMessage] + state["messages"])
    
    # Ensure correct extraction of the response content
    if hasattr(response, "content"):
        result = response.content.strip().lower()
    elif isinstance(response, str):
        result = response.strip().lower()
    else:
        raise ValueError("Unexpected response format from model")

    if result == "info":
        state["next"] = "info"
    elif result == "schedule":
        state["next"] = "schedule"
    else:
        raise ValueError(f"Unexpected model output: {result}")
    return state

def info_bot(state: State):
    symmssg = SystemMessage(content="""
You're 'The Grand Residences' dedicated sales representative! My goal is to give you clear, accurate answers about our project in Sector 65, Gurgaon, strictly based on the information below. I can't guess or make up details, so if your question isn't covered here, I'll offer to connect you with one of our senior experts. Let's keep it friendly and professional!
you have to pick the information form here and then rephrase it in human tone and remove the "*" from responce .
**Here are the official project details for 'The Grand Residences':**
* **Developer:** Edquest
* **RERA ID:** RC/REP/HARERA/GGM/XXXX/YYYY/ZZZ
* **Current Status:** Under Construction
* **Expected Possession:** December 2026
* **Location & Connectivity:** We're located in Sector 65, Golf Course Extension Road, directly opposite Grand Hyatt and near Pathways School. Enjoy direct access to Golf Course Extension Road, a 5-minute drive to the Sector 56/57 Metro, and only 30-40 minutes from IGI Airport. Cyber Hub is also conveniently close by.
* **Configurations Available:**
    * 3 BHK: 2200–2800 sq. ft.
    * 4 BHK: 3200–4000 sq. ft.
* **Pricing:** Prices range from ₹25,000–₹30,000/sq. ft., with 3 BHK units starting from ₹5.50 Cr.
* **Payment Plans:** We offer CLP, DPP, and Subvention (if applicable).
* **Associated Charges:** These include EDC/IDC, IFMS, Club Membership, Car Parking, Power Backup, and Registration & Stamp Duty.
* **Key Features:** Expect grand lobbies, smart home readiness, concierge services, 24/7 security, 100% power backup, imported finishes, VRV/VRF ACs, and a modular kitchen.
* **Clubhouse:** Our expansive 50,000 sq. ft. clubhouse boasts a gym, multiple pools, various sports courts, indoor games, a spa, a cafeteria, and a library, among other amenities.
* **Our Unique Selling Points (USP):** A prime location, a renowned architect, extensive green spaces, high appreciation potential, and a proven developer record.
* **Approvals:** All necessary approvals from HUDA, T&CP, and Environment are in place.
* **Approved Banks for Loans:** HDFC, ICICI, SBI, and Axis Bank.
* **Available Marketing Assets:** E-brochure, Floor Plans, Virtual Tour, Site Visit Booking, and Sample Apartment Photos/Videos.

**If I can't answer your specific question with the information provided, I'll respond with:** "I’d love to help further, but that requires a bit more detail. Would you like me to schedule a call with one of our senior property experts?"
""")
    msg = model.invoke([symmssg] + state['messages']) 
    print(state["messages"])
    print("Assistent: "+msg.content)
    user_input = input("User: ")

    return {
    "messages": [
        AIMessage(content=msg.content),
        HumanMessage(content=user_input)
    ]}

def booking_bot(state: State):
    symmssg = SystemMessage(content="""
You are a calender schedular bot with access to two tools: `get_date` and `book_slot`.

Your job is to help users schedule calender events ONLY IF they explicitly ask to add in the calender or schedule — for example:
- "shedule call for today"
- "I want to schedule for next Monday"
- "Please schedule for 2025-07-10"

Only then should you:
1. Identify the date (using `get_date` if needed)
2.ask for the time is not given .
3. Call `book_slot(date)` with the date in YYYY-MM-DD format only if both date and time is available.

If the user only says something like "today", "Monday", or "tomorrow", DO NOT book — ask for clarification or ignore.

Use:
- `get_date(0)` for "today"
- `get_date(1)` for "tomorrow"
- `get_date("next monday")`, `get_date("friday")` etc. for weekdays
Strictly follow following instructions:
DO not call get_date if user already provide a date.
DO Not call book_slot( multiple time call it only one time when you have date and time both and after calling it Do not call any tool.)
Do NOT pass anything other than a string like '2025-06-28' to the `book_slot()` tool.
""")

    messages = state["messages"]

    # Optimization: if the latest message is already from assistant AND it contains a booking confirmation, skip
    if isinstance(messages[-1], AIMessage) and "Event added in calender" in messages[-1].content:
        return {"messages": messages}  # Do nothing

    return {"messages": [model.bind_tools(tools).invoke([symmssg] + messages)]}

builder = StateGraph(State)
builder.add_node("booking_bot",booking_bot)
builder.add_node("info_bot", info_bot)
builder.add_node("tools",ToolNode(tools))
builder.add_node("chat_bot",chatBot)

builder.add_edge(START,"chat_bot")
builder.add_conditional_edges("chat_bot",next_node)
builder.add_edge("info_bot","chat_bot")
builder.add_conditional_edges("booking_bot",tools_condition)
builder.add_edge("tools","booking_bot")
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
def stream_graph_updates(user_input: str):
    events= graph.stream({"messages": [{"role": "user", "content": user_input}]},config,
    stream_mode="values",)
    for event in events:
     event["messages"][-1].pretty_print()


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        
        break




# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass
