import streamlit as st
from datetime import date
from listings import events
#from data_gen import events_gen
import psycopg2
from psycopg2 import sql
import pg8000
import json
#from dotenv import load_dotenv
import os
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, select, update,text
from sqlalchemy.orm import sessionmaker

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
            body, label, .stTextInput, .css-10trblm, .css-1s44ra {
                color: #ffffff !important; /* White font color */
                font-family: 'Garamond', serif; /* Example font family */
            }

            /* Change font color of main content */
            .main .block-container {
                color: #ffffff !important;
            }

            # /* Change font color for all text globally */
            # body, .st-bd, .st-be, .st-bh, .st-bj, .st-bq, .st-de, .st-ei, .st-el, .st-er, .st-es, .st-ex, .st-fj, .st-fp, .st-ft, .st-fv, .st-gb, .st-gm {
            #     color: #ffffff !important;
            # }

            /* Change placeholder color */
            .stTextInput ::placeholder {
                color: rgba(255, 255, 255, 0.7) !important;
            }

            /* Change the color of text in buttons */
            .stButton > button {
                color: #ffffff !important;
            }

            /* If you have links, change their color as well */
            a {
                color: #ffffff !important;
            }
            
            /* Adjust the color of text in the expander */
            # .st-cx, .st-db, .st-dd, .st-dp, .st-dq {
            #     color: #ffffff !important;
            # }

            .myDiv {
                # border: 5px outset red;
                background-color: #ffffff;
                # text-align: center;
                }
            
            </style>
            """, unsafe_allow_html=True)


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




def init_unix_connection_engine(db_config):
    # Setup the SQLAlchemy engine with the proper URL and configuration.
    engine = create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=os.environ.get('DATABASE_USER'),
            password=os.environ.get('DATABASE_PASSWORD'),
            host=os.environ['DATABASE_HOST'],
            # port=os.environ['DATABASE_PORT'],
            database=os.environ.get('DATABASE_NAME'),
            query={
                "unix_sock":"/cloudsql/herav3:us-west1:herapsql/.s.PGSQL.5432".format(
                    os.environ.get('DATABASE_HOST')
                )
            }
        ),
        **db_config
    )
    return engine

def init_db_connection():
    db_config = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    return init_unix_connection_engine(db_config)

# Initialize database connection
engine = init_db_connection()


def add_user(user_data):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Check if user already exists
            existing_user = conn.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {'username': user_data['username']}
            ).fetchone()

            if existing_user:
                return False

            # Handle hobbies data
            true_hobbies = [hobby for hobby, is_interested in user_data['hobbies'].items() if is_interested]
            if user_data['hobbies'].get('Other'):
                true_hobbies.append(user_data['hobbies']['Other'])

            # Insert new user data into the database
            conn.execute(
                text("""
                    INSERT INTO users (
                        name, dob, gender, address, city, state, email, phone_number, occupation, education,
                        relationship, parent, preferred_location, hobbies, friends, username, password
                    ) VALUES (
                        :name, :dob, :gender, :address, :city, :state, :email, :phone_number, :occupation, :education,
                        :relationship, :parent, :preferred_location, :hobbies, :friends, :username, :password
                    )
                """),
                {
                    'name': user_data['name'], 'dob': user_data['dob'], 'gender': user_data['gender'],
                    'address': user_data['address'], 'city': user_data['city'], 'state': user_data['state'],
                    'email': user_data['email'], 'phone_number': user_data['phone_number'],
                    'occupation': user_data['occupation'], 'education': user_data['education'],
                    'relationship': user_data['relationship'], 'parent': user_data['parent'],
                    'preferred_location': user_data['preferred_location'], 'hobbies': true_hobbies,
                    'friends': [], 'username': user_data['username'], 'password': user_data['password']
                }
            )
            trans.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            trans.rollback()
            return False

def add_friend(current_user, friend_username):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            result = conn.execute(
                text("SELECT friends FROM users WHERE username = :username"),
                {'username': current_user}
            ).fetchone()
            current_friends = result[0] if result else []

            if friend_username in current_friends:
                return False

            current_friends.append(friend_username)

            conn.execute(
                text("UPDATE users SET friends = :friends WHERE username = :username"),
                {'friends': current_friends, 'username': current_user}
            )
            trans.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            trans.rollback()
            return False

def get_friends(current_user):
    """
    Fetch the current user's friends list from the table.
    """
    with engine.connect() as conn:
        # Execute a SELECT query to fetch the current user's friends list from the database
        result = conn.execute(
            text("SELECT friends FROM users WHERE username = :username"),
            {'username': current_user}
        ).fetchone()
        
        # If result is not None, parse the friends list from the database and return it
        friends_list = result[0] if result else []
        return friends_list

def fetch_user_by_username(username):
    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()
        return user

def user_login(username, password):
    with engine.connect() as conn:
        # Query the user based on username
        user = conn.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()

        # Check if the user exists and if the password matches
        if user and user['password'] == password:
            return True
        else:
            return False

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
   #st.subheader('Home Page')
    if 'user' in st.session_state:
        # st.subheader(f"Welcome {st.session_state['user']}!")
        if 'user' in st.session_state:
            st.markdown(
            f'''
            <h1 style="color: #5c2d60; font-size: 26px; font-family: Arial, sans-serif;">
            Welcome {st.session_state['user']}!
            </h1>
            ''',
            unsafe_allow_html=True
        )
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
        st.markdown('<h1 class="hera-title" style="color:white;">Signup</h1>', unsafe_allow_html=True)

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
        st.markdown('<h1 class="hera-title" style="color:white;">Hobbies and Interests</h1>', unsafe_allow_html=True)
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
    # font_style()
    # st.subheader('Manage Friends')
    if 'user' in st.session_state:
        font_style()
        current_user = st.session_state['user']
        with st.form("add_friend_form"):
            st.markdown('<h1 style="color:white;">Manage Friends</h1>', unsafe_allow_html=True)
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
        # st.subheader('Generate Activities')
        st.markdown('<h1 style="color:white;">Generate Activities</h1>', unsafe_allow_html=True)
        if 'user' in st.session_state:
            font_style()
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