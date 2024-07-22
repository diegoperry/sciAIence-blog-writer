import streamlit as st
import stripe
from crewai import Crew
from app_agents import AppAgents, StreamToExpander
from app_tasks import AppTasks
import datetime
import sys
import sqlite3
from database import get_db_connection, create_tables, register_user, authenticate_user, user_exists, get_all_users
from streamlit_cookies_manager import EncryptedCookieManager

# Ensure this is the first Streamlit command
st.set_page_config(page_icon="✈️", layout="wide")

# Access Stripe API key from secrets
stripe.api_key = st.secrets["STRIPE_API_KEY"]

# Ensure tables are created
create_tables()

# Initialize the cookies manager with a password
cookies = EncryptedCookieManager(prefix="my_app_", password="your_secure_password_here")

if not cookies.ready():
    st.stop()

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

def check_subscription(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user and user['subscription_active']

def create_checkout_session(username):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1Pf9RrLkwsTSMeq4dibgOiZ6',  # Replace with your price ID
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'http://localhost:8501/?session_id={{CHECKOUT_SESSION_ID}}&username={username}',
        cancel_url='http://localhost:8501/cancel',
    )
    return session

class MyCrew:
    def __init__(self, topic, complexity, interests):
        self.topic = topic
        self.complexity = complexity
        self.interests = interests
        self.output_placeholder = st.empty()

    def save_blog(self, output):
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO blogs (topic, complexity, interests, output)
            VALUES (?, ?, ?, ?)
        ''', (self.topic, self.complexity, self.interests, output))
        conn.commit()
        conn.close()

    def run(self):
        agents = AppAgents()  # Instantiate agents
        tasks = AppTasks()  # Instantiate tasks

        # Define the agents
        researcher_agent = agents.researcher_agent()
        writer_agent = agents.writer_agent()
        quality_agent = agents.quality_agent()

        # Define the tasks
        research_task = tasks.research_task(
            researcher_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        write_task = tasks.write_task(
            writer_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        check_task = tasks.check_task(
            quality_agent,
            self.topic,
            self.interests,
            self.complexity,
        )

        rewrite_task = tasks.rewrite_task(
            writer_agent,  # Use writer_agent for rewriting
            self.topic,
            self.interests,
            self.complexity,
        )

        # Define the crew with the agents and tasks
        crew = Crew(
            agents=[researcher_agent, writer_agent, quality_agent],
            tasks=[research_task, write_task, check_task, rewrite_task],
            verbose=True
        )

        # Kick off the crew process and get the result
        result = crew.kickoff()

        # Debugging: Print the result to inspect its structure
        print("DEBUG: Result Structure:", result)

        # Attempt to parse the result based on its structure
        try:
            # If result is a dictionary with 'tasks', access the output of the last task
            if isinstance(result, dict) and 'tasks' in result:
                final_output = result['tasks'][-1]['output']
            # If result is a list, access the output of the last element
            elif isinstance(result, list):
                final_output = result[-1]['output']
            # If result is a string, use it directly
            elif isinstance(result, str):
                final_output = result
            else:
                final_output = "Unexpected result format"
        except Exception as e:
            print("DEBUG: Error accessing final output:", e)
            final_output = "Error processing the result"

        # Save the final output to the database
        self.save_blog(final_output)

        # Display the final output
        self.output_placeholder.markdown(final_output)
        return final_output

def check_payment_success():
    query_params = st.query_params
    if "session_id" in query_params and "username" in query_params:
        session_id = query_params["session_id"]
        username = query_params["username"]
        if st.session_state.username == username:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                subscription = stripe.Subscription.retrieve(session.subscription)
                if subscription.status == 'active':
                    st.session_state.subscription_active = True
                    cookies["subscription_active"] = "true"
                    cookies.save()
                    st.success("Subscription activated successfully!")
            except Exception as e:
                st.error(f"Error verifying subscription: {e}")

def main():
    st.header("⚛️ SciAIence Blog Writer")

    st.subheader("🤖 Let a team of specialized AI agents research and write your scientific blog!",
                 divider="rainbow", anchor=False)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "subscription_active" not in st.session_state:
        st.session_state.subscription_active = False

    if cookies.get("logged_in") == "true":
        st.session_state.logged_in = True
        st.session_state.username = cookies.get("username")
        st.session_state.subscription_active = cookies.get("subscription_active") == "true"

    def login():
        with st.sidebar:
            st.header("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    cookies["logged_in"] = "true"
                    cookies["username"] = username
                    cookies["subscription_active"] = str(check_subscription(username))
                    cookies.save()
                    st.experimental_rerun()  # Rerun to update the sidebar content
                else:
                    st.sidebar.error("Invalid username or password")

    def logout():
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.subscription_active = False
        cookies["logged_in"] = "false"
        cookies["username"] = ""
        cookies["subscription_active"] = "false"
        cookies.save()
        st.experimental_rerun()  # Rerun to update the sidebar content

    def register():
        with st.sidebar:
            st.header("Register")
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            if st.button("Register"):
                if user_exists(username):
                    st.sidebar.error("Username already exists")
                else:
                    register_user(username, email, password)
                    st.sidebar.success("User registered successfully")

    def manage_subscription():
        st.sidebar.write(f"[Manage your subscription](https://billing.stripe.com/p/login/test/{st.session_state.username})")

    if st.session_state.logged_in:
        st.sidebar.button("Logout", on_click=logout)
        st.sidebar.write(f"Logged in as {st.session_state.username}")

        check_payment_success()

        if not st.session_state.subscription_active:
            st.write("You must have an active subscription to access the inputs.")
            if st.button("Subscribe Now"):
                session = create_checkout_session(st.session_state.username)
                st.write(f"[Proceed to Payment]({session.url})")

        if st.session_state.subscription_active:
            manage_subscription()
            with st.sidebar:
                st.header("👇 Enter your blog details")
                with st.form("my_form"):
                    topic = st.text_area(
                        "What is the topic of your scientific blog?", placeholder="How String Theory Proposes Multiple Dimensions Beyond Our Perception.", key="blog_topic")
                    complexity = st.text_input(
                        "What level of complexity do you want your blog post to be?", placeholder="Simple, easy to understand", key="blog_complexity")

                    interests = st.text_area("What discoveries, scientists or experiments do you want to highlight?",
                                            placeholder="The role of the Large Hadron Collider in providing evidence for string theory's predictions.", key="blog_interests")

                    submitted = st.form_submit_button("Submit")

                st.divider()

                st.sidebar.info("Built with CrewAI and Streamlit by Diego Perry", icon="🔭")

            if submitted:
                with st.spinner("🤖 **Agents at work...**"):
                    with st.container():
                        sys.stdout = StreamToExpander(st)
                        my_crew = MyCrew(topic, complexity, interests)
                        result = my_crew.run()

                st.subheader("Here is your blog", anchor=False, divider="rainbow")
                st.markdown(result)

    else:
        login()
        register()

if __name__ == "__main__":
    main()
