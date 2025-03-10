import streamlit as st
import streamlit as st
import base64
import os
import json
import speech_recognition as sr
from groq import Groq
from pinecone import Pinecone, ServerlessSpec
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import dateparser
class CalendarManager:
    """
  Class to handle Google Calendar authentication and event creation.
    """

    def __init__(self, scopes):
        self.scopes = scopes

    def authenticate_google_calendar(self):
        """Authenticates and returns a Google Calendar service object."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "D:\SEM_2_PROJECTS\Personal Assistant AI\PA-AI python folder\credentials.json", self.scopes)  # Replace 'credentials.json' with your credentials file
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)
        return service

    
   


    def create_calendar_event(self, service, summary, date, day, start_time, end_time, location):
        """Creates a new event in Google Calendar."""

        # Combine date with start and end time
        start_datetime = dateparser.parse(f"{date} {start_time}")
        end_datetime = dateparser.parse(f"{date} {end_time}")

        if not start_datetime or not end_datetime:
            print("Error parsing date/time")
            return

        event = {
            'summary': summary,
            'location': location,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata'  # Adjust the timezone if necessary
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # Email reminder 1 day before
                    {'method': 'popup', 'minutes': 10},  # Popup reminder 10 minutes before
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created:', event.get('htmlLink'))
class InputHandler:
    """
    Class to handle user input (text or voice).
    """

    def __init__(self):
        pass

    def get_voice_input(self):
        """Captures voice input and converts it to text using Google Speech Recognition."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening... Speak now.")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand the audio.")
                return None
            except sr.RequestError:
                print("Could not request results, please check your internet connection.")
                return None
handle_input = InputHandler()

os.environ["GROQ_API_KEY"] = "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"
os.environ["PINECONE_API_KEY"] = "e9549a8f-6384-4850-b05e-4dd6fdcd51d4"
SCOPES = ['https://www.googleapis.com/auth/calendar']
client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("quickstart")

st.session_state.api_key = os.environ.get("GROQ_API_KEY")

# Only show the API key input if the key is not already set
if not st.session_state.api_key:
    # Ask the user's API key if it doesn't exist
    api_key = st.text_input("Enter API Key", type="password")
    
    # Store the API key in the session state once provided
    if api_key:
        st.session_state.api_key = api_key
        st.rerun()  # Refresh the app once the key is entered to remove the input field
else:
    # If the API key exists, show the chat app
    # Inject CSS for background image and black text for the title
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://i.pinimg.com/736x/a9/28/c4/a928c490208c08d7771e8c7acf58ad42.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color:rgba(153, 102, 204,0.4);
            background-blend-mode: overlay;
            height: 100vh;
            width: 100vw;
        }
        
        .top-right {
            position: absolute;
            top: 2px;
            right: 0px;
            text-align: right;
        }
        .h1{
            color: white}
        
        h2, h3, h4, h5, h6, p, div, span, label {
            color: white !important;}
        
        </style>
        """,
        unsafe_allow_html=True
    )
    # Streamlit content with customized title text
    st.markdown("<div class='top-right'><h1>REVA - RESOURCEFUL EVERYDAY VIRTUAL ASSISTANT </h1></div>", unsafe_allow_html=True)
    # Initialize the chat message list in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.groq_chat_messages = [{"role": "system", "content": """You are a helpful assistant.
        The user will give their schedule description, and you wil Extract the following details from the given text and return ONLY a valid JSON WITHOUT ANY COMMENTS:                                   
          "Summary": "A concise summary of the event.",
          "Date": "Extract the date or date range if mentioned (e.g., 'March 10, 2024' or 'June 1st to June 10th'). If no date is given, return today's date.",
          "Day": "Extract the day of the week if a single date is provided, else return 'Multiple Days' for date ranges.",
          "Start Time": "Extract the exact time of start of the event (e.g., '10:00 AM') or time range if mentioned. If no time is found, return ''.",
          "End Time": "Extract the exact time of end of event (e.g., '10:00 AM') or time range if mentioned. If no time is found, return ''.",
          "Location": "Extract all locations from the text as a comma-separated list. If no location is found, return 'Not Found'." """
        }]
        st.session_state.chat_messages = []
        
    # Display previous chat messages
    for messages in st.session_state.chat_messages:
        if messages["role"] in ["user", "assistant"]:
            with st.chat_message(messages["role"]):
                st.markdown(messages["content"])
    
    # Define a function to simulate chat interaction (you would replace this with an actual API call)
    def get_chat():
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[st.session_state.chat_messages[-1]["content"]],
            parameters={
                "input_type": "query"
            }
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
    col1, col2 = st.columns([3,1]) 
    
    # Handle user input
    with col1:
        prompt = st.chat_input("Schedule an Event now!")
    with col2:
        if st.button("🎙️ Speak"):
            prompt = handle_input()
    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.groq_chat_messages.append({"role": "user", "content": prompt})
        # Get the assistant's response (in this case, it's just echoing the prompt)
        with st.spinner("Getting responses..."):
            response = get_chat()
        with st.chat_message("assistant"):
            st.markdown(response)
            
        # Add user message and assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.groq_chat_messages.append({"role": "assistant", "content": response})
        
        calendar_manager = CalendarManager(SCOPES)
        try:
            service = calendar_manager.authenticate_google_calendar()
        
            response_dic = json.loads(response)
                
            summary = response_dic.get("Summary")
            date = response_dic.get("Date")
            day = response_dic.get("Day")
            location = response_dic.get("Location")
            start_time = response_dic.get("Start Time")
            end_time = response_dic.get("End Time")
            
            # Correct function call with proper argument order
            calendar_manager.create_calendar_event(service, summary, date, day, start_time, end_time, location)
            st.markdown("Created a calendar event.")

        except Exception as e:
            st.markdown(f"Error creating calendar event: {e}")
