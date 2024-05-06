import streamlit as st
from datetime import date
from listings import events
#from data_gen import events_gen
import psycopg2
from psycopg2 import sql
import json
#from dotenv import load_dotenv
import os
import base64

# Load environment variables from .env file, which is assumed to be in the same directory as the script
#load_dotenv()

# # Access variables securely
# database_host = os.environ.get('DATABASE_HOST')
# database_name = os.environ.get('DATABASE_NAME')
# database_user = os.environ.get('DATABASE_USER')
# database_password = os.environ.get('DATABASE_PASSWORD')

bg_url="https://storage.googleapis.com/herav3.appspot.com/new_bg.png"

def set_background_image(image_path):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({image_path});
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_styling_form():
    st.markdown("""
    <style>
    /* Overall form background */
    div[data-testid="stForm"] {
        background-color: rgba(117, 26, 71,0.9); /* Semi-transparent white */
        border-radius: 20px;
        padding: 40px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Optional shadow for depth */
    }
    
    /* Input fields with only bottom border */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid #ccc !important;
        border-radius: 0 !important; /* Removes border radius */
    }
    
    /* Adjust the padding and font size of the input fields */
    .stTextInput input {
        padding: 10px 0 10px 0 !important;
        font-size: 16px;
    }

    /* Adjust the style of the login button */
    .stButton > button {
        color: white !important;
        background-color: #751a47; /* Your button color */
        padding: 10px 24px;
        border-radius: 20px;
        border: none;
        font-size: 18px;
        margin-top: 20px;
        transition: background-color 0.3s;
    }
    
    /* Change the hover effect of the button */
    .stButton > button:hover {
        background-color: #751a47; /* Darken button color on hover */
    }
    </style>
    """, unsafe_allow_html=True)


def font_style():
    st.markdown("""
    <style>
    /* Change font color and style of all text in the app */
    body {
        color: #ffffff; /* Pink font color */
        font-family: 'Garamond', serif; /* Example font family */
    }

    /* Specific Streamlit components can also be targeted */
    .stButton > button {
        color: #ffffff; /* White font color */
        font-family: 'Helvetica', sans-serif; /* Example font family */
    }
    </style>
    """, unsafe_allow_html=True)

# Database code
conn = psycopg2.connect(
    dbname="hera",
    user="main",
    password="Hera@group53",
    host="127.0.0.1",
    port=3306
)


# conn = psycopg2.connect(
#     dbname=database_name,
#     user=database_user,
#     password=database_password,
#     host=database_host,
#     port=5432
# )

cur = conn.cursor()



# Dictionary to store user data
#users_db = {}

import pydeck as pdk

def display_events_and_map(activities):
    """ Function to display events and a map in an expander (simulating a pop-up) """
    with st.expander("See activities and map"):
        map_data = []
        for event_category in activities:
            for event_type, events in event_category.items():
                st.header(event_type)
                for event in events:
                    # Add data for map plotting
                    map_data.append({
                        "lat": event['lat'],
                        "lon": event['lng'],
                        "name": event['name']
                    })
                    # Display the event name as a clickable link
                    st.markdown(f"[{event['name']}]({event['attributions_link']})")
                    st.write(f"Address: {event['formatted_address']}")
                    st.write(f"Latitude: {event['lat']}, Longitude: {event['lng']}")
                    st.write("")
        
        # Creating a map using Pydeck
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=37.7749,
                longitude=-122.4194,
                zoom=11,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=map_data,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
            ],
        ))



def add_user(user_data):
    """Add the user data to the table using the username as the primary key."""
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    existing_user = cur.fetchone()
    if existing_user:
        return False
    

    true_hobbies = [hobby for hobby, is_interested in user_data['hobbies'].items() if is_interested is True]
    if user_data['hobbies'].get('Other'):
        true_hobbies.append(user_data['hobbies']['Other'])  # Append the 'Other' hobby if it's non-empty

    # Insert the user data into the table
    cur.execute("""
    INSERT INTO users (
        name, dob, gender, address, city, state, email, phone_number, occupation, education,
        relationship, parent, preferred_location, hobbies, friends, username, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    user_data['name'], user_data['dob'], user_data['gender'], user_data['address'], user_data['city'],
    user_data['state'], user_data['email'], user_data['phone_number'], user_data['occupation'], user_data['education'],
    user_data['relationship'], user_data['parent'], user_data['preferred_location'], true_hobbies,
    [], user_data['username'], user_data['password']
))
    conn.commit()
    return True


# Function to add a friend to the current user's friends list in the PostgreSQL table
def add_friend(current_user, friend_username):
    """Add a friend to the current user's friends list."""
    # Fetch the current user's friends list from the database
    cur.execute("SELECT friends FROM users WHERE username=%s", (current_user,))
    result = cur.fetchone()
    if result is not None:
        current_friends = result[0]  # result is a tuple, result[0] is the first column
        if current_friends is None:
            current_friends = []  # Ensure it's a list even if it's NULL in the database
    else:
        current_friends = []  # No user found, default to empty list
    print(current_friends)
    # Check if the friend is already in the current user's friends list
    if friend_username in current_friends:
        return False
    print(friend_username)
    # Append the friend's username to the current user's friends list
    current_friends.append(friend_username)
    
    # Update the current user's friends list in the database
    cur.execute("UPDATE users SET friends=%s WHERE username=%s",
                   (current_friends, current_user))
    conn.commit()
    return True


def get_friends(current_user):
    """Fetch the current user's friends list from the table."""
    # Execute a SELECT query to fetch the current user's friends list from the database
    cur.execute("SELECT friends FROM users WHERE username=%s", (current_user,))
    friends_data = cur.fetchone()
    # Otherwise, parse the friends list from the database and return it
    return friends_data[0]

def fetch_user_by_username(username):
    """Fetch a row from the table based on username."""
    # Execute a SELECT query to fetch the row with the specified username
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    # Fetch the row from the database
    user_data = cur.fetchone()
    
    # Return the fetched row if it exists
    return user_data



# Function to log in a user by checking username and password in the PostgreSQL table
def user_login(username, password):
    """Check if the user exists in the database and the password matches."""
    # Execute a SELECT query to fetch the user from the database
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    #print([user[16] , password])
    # Check if the user exists and if the password matches
    return user[15] and user[16] == password  # Assuming password is at index 14 in the user tuple


# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'login'


#####TOP BAR#####

col1, col2, col3, col4, col5 = st.columns(5)


if 'user'  not in st.session_state:
    with col1:
        if st.button('Login'):
            st.session_state.page = 'login'
    with col2:
        if st.button('Signup'):
            st.session_state.page = 'signup'
if 'user' in st.session_state:
    with col1:
        if st.button('Home'):
            st.session_state.page = 'home'
    with col2:
        if st.button('Friends'):
            st.session_state.page = 'manage_friends'
    with col3:
        if st.button('Activities'):
            st.session_state.page = 'create_activities'

set_background_image(bg_url)


# Page Content based on navigation
if st.session_state.page == 'home':
    set_styling_form()
    font_style()
    st.subheader('Home Page')
    if 'user' in st.session_state:
        st.write(f"Welcome {st.session_state['user']}!")
    else:
        st.warning('You are not logged in. Please login to access features.')

elif st.session_state.page == 'login':
    set_styling_form()
    font_style()
    with st.form(key="login_form"):

        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_login = st.form_submit_button('Login')

        if submit_login:
            #print([username,password])
            if user_login(username, password):
                users_db_name=user_login(username, password)
                st.session_state['user'] = username
                st.session_state.page = 'home'  # Redirect to home page
                st.rerun() 
                st.success('Logged in successfully.')
            else:
                st.error('Incorrect username or password.')
        
elif st.session_state.page == 'signup':
    set_styling_form()
    font_style()
    # Streamlit form for signup
    with st.form('signup_form', clear_on_submit=True):
        st.markdown('<div class="signup-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="hera-title">Signup</h1>', unsafe_allow_html=True)

        # User information
        name = st.text_input('Name:', placeholder="Name")
        dob = st.date_input('Date of Birth:', max_value=date.today())
        gender = st.selectbox('Gender:', ['Female', 'Male', 'Other', 'Prefer not to say'])
        address = st.text_input('Address:', placeholder="Address Line 1")
        city = st.text_input('City:', placeholder="City")
        state = st.text_input('State:', placeholder="State")
        email = st.text_input('Email:', placeholder="Email")
        phone_number = st.text_input('Phone Number:', placeholder="Your phone number")
        occupation = st.text_input('Occupation:', placeholder="Your occupation")
        education = st.selectbox('Education Level:', ['High School', 'Undergraduate', 'Graduate', 'Postgraduate'])
        relationship = st.selectbox('Relationship Status:', ['Single', 'In a relationship', 'Married', 'Divorced', 'Widowed'])
        parent = st.radio('Are you a parent?', ('Yes', 'No'))
        preferred_location = st.selectbox('Preferred Locations for Matches/Events:', ['Near current location', 'Anywhere in United States', 'Specific city or state'])

        # Hobbies section with two columns
        st.markdown('## Hobbies and Interests')
        col1, col2 = st.columns(2)
        with col1:
            reading = st.checkbox('Reading')
            fitness = st.checkbox('Fitness and Exercise')
            cooking = st.checkbox('Cooking and Baking')
            music = st.checkbox('Music')
            art = st.checkbox('Art and Creativity')
        with col2:
            traveling = st.checkbox('Traveling')
            outdoor = st.checkbox('Outdoor Activities')
            sports = st.checkbox('Sports')
            gaming = st.checkbox('Gaming')
            volunteering = st.checkbox('Volunteering')
        other_hobby = st.text_input('Other hobbies/interests:', placeholder="Specify any other hobbies")

        # Account details
        username = st.text_input('Username:', placeholder="Choose a username")
        password = st.text_input('Password:', placeholder="Create a password", type='password')
        confirm_password = st.text_input('Confirm Password:', placeholder="Confirm your password", type='password')
        
        consent = st.checkbox('I consent to the processing of my personal data.', value=False, key='consent')

        st.markdown('</div>', unsafe_allow_html=True)  # Close the signup-container
        st.markdown('<div class="terms-text">By creating an account you agree to our <a href="#">Terms & Privacy</a>.</div>', unsafe_allow_html=True)

        # Submit button
        submitted = st.form_submit_button('Submit')

    if submitted and password == confirm_password:
        if consent:
            user_data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'city': city,
                'state': state,
                'email': email,
                'phone_number': phone_number,
                'occupation': occupation,
                'education': education,
                'relationship': relationship,
                'parent': parent,
                'preferred_location': preferred_location,
                'hobbies': {
                    'Reading': reading,
                    'Fitness and Exercise': fitness,
                    'Cooking and Baking': cooking,
                    'Music': music,
                    'Art and Creativity': art,
                    'Traveling': traveling,
                    'Outdoor Activities': outdoor,
                    'Sports': sports,
                    'Gaming': gaming,
                    'Volunteering': volunteering,
                    'Other': other_hobby
                },
                'username': username,
                'password': password  # Remember to hash passwords in a real application!
            }
            add_user(user_data)
            st.session_state.page = 'login'  # Redirect to login page
            st.rerun() 
            st.success('Account created successfully!')
        else:
            st.error('You must consent to the processing of your personal data to create an account.')
    elif submitted and password != confirm_password:
        st.error('Passwords do not match.')


elif st.session_state.page == 'manage_friends':
    set_styling_form()
    font_style()
    # st.subheader('Manage Friends')
    if 'user' in st.session_state:
        current_user = st.session_state['user']

        with st.form("add_friend_form"):
            st.subheader('Manage Friends')
            friend_username = st.text_input("Enter your friend's username to add:")
            submit_friend = st.form_submit_button("Add Friend")
            
            if submit_friend:
                if friend_username == current_user:
                    st.error("You cannot add yourself as a friend.")
                elif add_friend(current_user, friend_username):
                    st.success(f'{friend_username} has been added to your friends list.')
                    st.rerun()
                else:
                    st.error('Failed to add friend. Check if the username exists and is not already a friend.')

        # Display current friends in a scrollable container
            friends =get_friends(current_user)
            if friends:
                st.write("Your Friends:")
                friends_container = st.container()
                with friends_container:
                    cols_per_row = 3
                    for i in range(0, len(friends), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for col, friend in zip(cols, friends[i:i+cols_per_row]):
                            col.write(friend)
            else:
                st.write("No friends yet.")


# Page to generate activities with a friend
elif st.session_state.page == 'create_activities':
    set_styling_form()
    with st.form("display_activities"):
        st.subheader('Generate Activities')
        if 'user' in st.session_state:
            current_user = st.session_state['user']
            friends =get_friends(current_user)
            friend_selected = st.selectbox('Select a friend to plan an activity:', friends)
            st.write(f"You selected {friend_selected}.")
            
        # Generate activities button
            if st.form_submit_button('Generate Activities'):
                r1 = fetch_user_by_username(current_user)
                r2 = fetch_user_by_username(friend_selected)
                activities = events(r1, r2)
                if activities:
                    st.write(activities[0])
                    display_events_and_map(activities[2])
                else:
                    st.error("No activities found.")
        else:
            st.error("Please login to use this feature.")