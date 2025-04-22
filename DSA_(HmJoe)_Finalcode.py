# Harish 1st code

import streamlit as st
import base64
import os
import json
import re
from groq import Groq
from pinecone import Pinecone, ServerlessSpec
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import dateparser
from datetime import timedelta
import pytz

# ============ Utility ============
def clean_json_response(text):
    text = re.sub(r"``(json)?", "", text).strip(" \n\t")
    text = text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
    
    lines = text.splitlines()
    cleaned_lines = []
    for i, line in enumerate(lines):
        if ":" in line and not line.strip().endswith(",") and i < len(lines) - 2:
            cleaned_lines.append(line.rstrip() + ",")
        else:
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines)

# ============ Calendar Manager ============
class CalendarManager:
    def __init__(self, scopes):
        self.scopes = scopes
        self.credentials_file ="D:\\SEM_2_PROJECTS\\Personal Assistant AI\\PAAI calendar credentials.json"
        self.token_file = "D:\\SEM_2_PROJECTS\\Personal Assistant AI\\token.json"

    def authenticate_google_calendar(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        return service

    def create_calendar_event(self, service, event_details):
        try:
            required_fields = ["summary", "date", "start_time"]
            for field in required_fields:
                if field not in event_details or not event_details[field]:
                    raise ValueError(f"Missing required field: {field}")

            timezone = event_details.get("timezone", "UTC")
            start_datetime = self._parse_datetime(event_details["date"], event_details["start_time"], timezone)
            end_datetime = self._parse_datetime(event_details["date"], event_details.get("end_time"), timezone)
            
            if not start_datetime:
                raise ValueError("Invalid start date/time")
            
            if not end_datetime:
                end_datetime = start_datetime + timedelta(hours=1)

            event = {
                "summary": event_details["summary"],
                "location": event_details.get("location", ""),
                "description": event_details.get("description", ""),
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": timezone,
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},
                        {"method": "popup", "minutes": 10},
                    ],
                },
            }
            
            created_event = service.events().insert(
                calendarId="primary", body=event
            ).execute()
            
            return created_event.get("htmlLink")
        
        except Exception as e:
            st.error(f"Failed to create event: {str(e)}")
            return None

    def _parse_datetime(self, date_str, time_str, timezone):
        if not date_str:
            return None
            
        datetime_str = f"{date_str} {time_str}" if time_str else date_str
        parsed = dateparser.parse(
            datetime_str,
            settings={
                "TIMEZONE": timezone,
                "RETURN_AS_TIMEZONE_AWARE": True,
                "PREFER_DATES_FROM": "future"
            }
        )
        return parsed

# ============ Node class (separated) ============
class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

    def __str__(self):
        return (f"Task: {self.data[0]}, Priority: {self.data[1]}, Category: {self.data[2]}, "
                f"Due: {self.data[3].strftime('%d-%m-%Y') if isinstance(self.data[3], datetime) else self.data[3]}, "
                f"Recurrence: {self.data[4]}")

# ============ To-Do List Manager ============
class ToDoListManager:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_task(self, description, priority, category, due_date, recurrence): # O(n)
        try:
            due_date_obj = datetime.strptime(due_date, '%d-%m-%Y')
        except ValueError:
            st.warning("Invalid date format! Please use dd-mm-yyyy")
            return False

        new_task = Node([description, priority, category, due_date_obj, recurrence])

        if not self.head:
            self.head = self.tail = new_task
        else:
            current = self.head
            while current and current.data[1] >= priority:
                current = current.next

            if not current:
                self.tail.next = new_task
                new_task.prev = self.tail
                self.tail = new_task
            elif not current.prev:
                new_task.next = self.head
                self.head.prev = new_task
                self.head = new_task
            else:
                new_task.prev = current.prev
                new_task.next = current
                current.prev.next = new_task
                current.prev = new_task

        st.success(f"Task '{description}' added successfully!")
        return True

    def remove_task(self, description): # O(n)
        current = self.head
        while current:
            if current.data[0] == description:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                st.success(f"Task '{description}' completed and removed!")
                return True
            current = current.next

        st.warning("Task not found!")
        return False

    def get_all_tasks(self): # O(n)
        tasks = []
        current = self.head
        while current:
            tasks.append(current.data)
            current = current.next
        return tasks

    def count_tasks(self): # O(n)
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

    def clear_tasks(self): # O(1)
        self.head = self.tail = None
        st.success("All tasks have been cleared!")

# ============ Environment Setup ============
os.environ["GROQ_API_KEY"] = "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"
os.environ["PINECONE_API_KEY"] = "e9549a8f-6384-4850-b05e-4dd6fdcd51d4"
SCOPES = ['https://www.googleapis.com/auth/calendar']

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("quickstart")

st.session_state.api_key = os.environ.get("GROQ_API_KEY")

# ============ Streamlit UI ============
st.markdown(
    """
    <style>
    /* Modified CSS for left-aligned back button */
    .back-button-container {
        text-align: left;
        margin-bottom: 20px;
        padding-left: 1rem;
    }
    
    .stApp {
        background-image: url('https://i.pinimg.com/736x/a9/28/c4/a928c490208c08d7771e8c7acf58ad42.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-color: rgba(153, 102, 204, 0.4);
        background-blend-mode: overlay;
        height: 100vh;
        width: 100vw;
    }
    
    /* Chat input box styling */
    .stChatInput {
        background: transparent !important;
        padding: 0 !important;
        margin-top: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stChatInput .stTextInput textarea {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        padding: 20px !important;
        color: black !important;
        font-size: 18px !important;
        min-height: 100px !important;
    }
    
    .stChatInput .stTextInput textarea::placeholder {
        color: rgba(0, 0, 0, 0.7) !important;
        font-size: 18px !important;
    }
    
    .stChatInput .stTextInput > div {
        background: transparent !important;
    }
    
    .stChatInput .stTextInput button {
        background: rgba(153, 102, 204, 0.8) !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        margin-left: 15px !important;
        font-size: 24px !important;
    }
    
    /* Make container transparent */
    .stChatInputContainer {
        background: transparent !important;
        padding: 0 !important;
        margin-top: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* User message bubble */
    [data-testid="stChatMessage-user"] {
        background: rgba(153, 102, 204, 0.8) !important;
        border-radius: 25px 25px 0 25px !important;
        padding: 20px 25px !important;
        margin: 15px 0 !important;
        max-width: 80%;
        margin-left: auto;
        font-size: 18px !important;
    }
    
    /* Assistant message bubble */
    [data-testid="stChatMessage-assistant"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 25px 25px 25px 0 !important;
        padding: 20px 25px !important;
        margin: 15px 0 !important;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 18px !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: fadeIn 0.3s ease-out;
    }
    
    .stButton>button {
        transition: all 0.2s ease;
        font-size: 18px !important;
        padding: 15px 25px !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .task-item {
        background: rgba(255,255,255,0.8);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 18px;
    }
    
    .app-title {
        text-align: center;
        margin-bottom: 40px;
        color: white !important;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        font-size: 3.5rem !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: black !important;
        font-size: 20px !important;
    }
    
    /* Menu button styles */
    .menu-button {
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 28px;
        border-radius: 25px;
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
        margin: 20px;
        padding: 30px;
        cursor: pointer;
    }
    
    .menu-button:hover {
        transform: translateY(-5px);
        background: rgba(153, 102, 204, 0.8);
        color: white !important;
    }
    
    .menu-button i {
        font-size: 64px;
        margin-bottom: 15px;
    }
    
    .back-button {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 10px 20px;
        margin-bottom: 30px;
        display: inline-block;
        font-size: 20px !important;
    }
    
    /* Center the REVA title */
    .reva-title {
        text-align: center;
        font-size: 5rem !important;
        font-weight: bold;
        color: white !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        margin: 30px 0 50px 0;
    }
    
    /* Form elements */
    .stTextInput>div>div>input, 
    .stTextArea>div>textarea,
    .stSelectbox>div>select {
        font-size: 18px !important;
        padding: 15px !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
    }
    
    .stTab {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px !important;
        font-size: 18px !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
        padding: 0 25px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(153, 102, 204, 0.8) !important;
        color: white !important;
    }
    
    /* Complete button fixes */
    .complete-button {
        white-space: nowrap;
        width: 100%;
        padding: 0.5em 1em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if "chat_messages" not in st.session_state:
    st.session_state.groq_chat_messages = [{"role": "system", "content": """You are a helpful assistant.
    The user will give their schedule description, and you wil Extract the following details from the given text and your response must be ONLY as JSON format WITHOUT ANY COMMENTS:      
    "Respond only in raw JSON format. Do not add any extra text or punctuation. Strictly enclose all keys and values in double quotes ("), and use standard commas between key-value pairs. Do not include smart quotes, bullet points, or stylistic punctuation."                             
      "Summary": "A concise summary of the event.",
      "Date": "Extract the date or date range if mentioned (e.g., 'March 10, 2024' or 'June 1st to June 10th'). If no date is given, return today's date.",
      "Day": "Extract the day of the week if a single date is provided, else return Day not found",
      "Start Time": "Extract the exact time of start of the event (e.g., '10:00 AM') or time range if mentioned. If no time is found, return ''.",
      "End Time": "Extract the exact time of end of event (e.g., '10:00 AM') or time range if mentioned. If no time is found, return ".",
      "Location": "Extract all locations from the text as a comma-separated list. If no location is found, return 'Not Found'." """
    }]
    st.session_state.chat_messages = []

if 'todo_list' not in st.session_state:
    st.session_state.todo_list = ToDoListManager()

if 'current_view' not in st.session_state:
    st.session_state.current_view = "main_menu"

# Main menu function
def show_main_menu():
    st.markdown("<div class='reva-title'>REVA</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗓 Event Scheduler", key="scheduler_btn", use_container_width=True, 
                    help="Schedule events using natural language"):
            st.session_state.current_view = "scheduler"
            st.rerun()
    
    with col2:
        if st.button("✅ To-Do List", key="todo_btn", use_container_width=True, 
                    help="Manage your tasks and priorities"):
            st.session_state.current_view = "todo"
            st.rerun()

# Scheduler view function
def show_scheduler():
    st.markdown("<div class='reva-title'>REVA</div>", unsafe_allow_html=True)
    
    # Left-aligned back button container
    st.markdown("<div class='back-button-container'>", unsafe_allow_html=True)
    if st.button("← Back to Main Menu", key="back_scheduler"):
        st.session_state.current_view = "main_menu"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    for messages in st.session_state.chat_messages:
        if messages["role"] in ["user", "assistant"]:
            with st.chat_message(messages["role"]):
                st.markdown(messages["content"])

    def get_chat():
        try:
            embedding = pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[st.session_state.chat_messages[-1]["content"]],
                parameters={"input_type": "query"}
            )
            results = index.query(
                namespace="ns1",
                vector=embedding[0].values,
                top_k=3,
                include_values=False,
                include_metadata=True
            )
            context = ""
            for result in results.matches:
                if result['score'] > 0.8:
                    context += result['metadata']['text']
            st.session_state.groq_chat_messages[-1]["content"] = f"User Query: {st.session_state.chat_messages[-1]['content']} \n Retrieved Content (optional): {context}"
            chat_completion = client.chat.completions.create(
                messages=st.session_state.groq_chat_messages,
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Failed to get chat completion: {str(e)}")
            return "Sorry, I encountered an error. Please try again."

    if prompt := st.chat_input("Schedule an Event now!"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.groq_chat_messages.append({"role": "user", "content": prompt})

        with st.spinner("Getting response..."):
            response = get_chat()

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.groq_chat_messages.append({"role": "assistant", "content": response})

        calendar_manager = CalendarManager(SCOPES)

        try:
            service = calendar_manager.authenticate_google_calendar()

            cleaned_response = clean_json_response(response)
            st.code(cleaned_response, language="json")
            response_dic = json.loads(cleaned_response)

            timezone = st.selectbox("Select timezone", pytz.common_timezones, 
                                  index=pytz.common_timezones.index("Asia/Kolkata"))

            event_details = {
                "summary": response_dic.get("Summary", ""),
                "date": response_dic.get("Date", ""),
                "start_time": response_dic.get("Start Time", ""),
                "end_time": response_dic.get("End Time", ""),
                "location": response_dic.get("Location", ""),
                "timezone": timezone
            }

            event_link = calendar_manager.create_calendar_event(service, event_details)
            if event_link:
                st.success(f"✅ Event created successfully! [View in Calendar]({event_link})")

        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON from LLM. Details: {e}")
            st.code(response)
        except Exception as e:
            st.error(f"❌ Error creating calendar event: {e}")

# To-Do List view function
def show_todo_list():
    st.markdown("<div class='reva-title'>REVA</div>", unsafe_allow_html=True)
    
    # Left-aligned back button container
    st.markdown("<div class='back-button-container'>", unsafe_allow_html=True)
    if st.button("← Back to Main Menu", key="back_todo"):
        st.session_state.current_view = "main_menu"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Add Task", "View Tasks", "Statistics"])
    
    with tab1:
        with st.form("add_task_form"):
            description = st.text_input("Task Description*")
            priority = st.selectbox("Priority*", [1, 2, 3, 4, 5], index=2, 
                                  help="1 = Highest, 5 = Lowest")
            category = st.text_input("Category")
            due_date = st.text_input("Due Date (dd-mm-yyyy)*", 
                                   value=datetime.now().strftime('%d-%m-%Y'))
            recurrence = st.selectbox("Recurrence", 
                                     ["None", "Daily", "Weekly", "Monthly", "Yearly"])
            
            if st.form_submit_button("Add Task"):
                if description and due_date:
                    st.session_state.todo_list.add_task(description, priority, category, due_date, recurrence)
                else:
                    st.warning("Please fill required fields (marked with *)")
    
    with tab2:
        if st.session_state.todo_list.count_tasks() == 0:
            st.info("No tasks in your to-do list yet!")
        else:
            st.subheader("Your Tasks")
            current = st.session_state.todo_list.head
            while current:
                col1, col2 = st.columns([3, 1])  # Adjusted ratio
                with col1:
                    st.markdown(f"""
                    <div class="task-item">
                        <h4>{current.data[0]}</h4>
                        <p>Priority: {current.data[1]} | Category: {current.data[2]}</p>
                        <p>Due: {current.data[3].strftime('%d-%m-%Y')} | Repeats: {current.data[4]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("✓ Complete", 
                               key=f"complete_{current.data[0]}",
                               use_container_width=True):
                        st.session_state.todo_list.remove_task(current.data[0])
                        st.rerun()
                st.divider()
                current = current.next
    
    with tab3:
        st.metric("Total Tasks", st.session_state.todo_list.count_tasks())
        
        if st.button("Clear All Tasks", type="primary"):
            st.session_state.todo_list.clear_tasks()
            st.rerun()

# Main app routing
if st.session_state.current_view == "main_menu":
    show_main_menu()
elif st.session_state.current_view == "scheduler":
    show_scheduler()
elif st.session_state.current_view == "todo":
    show_todo_list()