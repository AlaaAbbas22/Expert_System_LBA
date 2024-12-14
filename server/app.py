from datetime import timedelta
from flask import Flask, request, session
from flask_session import Session
from flask_cors import CORS
from collections import defaultdict
from options import options
import random
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign, Atom, Functor, call, Variable
import sys

# **Query Interrupt Exception**
# This exception is raised when a query requires user input.
class QueryInterrupt(Exception):
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

# **Prolog Initialization**
prolog = Prolog()  # Global handle to Prolog interpreter

# **Prolog Predicates**
retractall = Functor("retractall")  # Retract all facts of a given predicate
known = Functor("known", 3)  # Predicate for storing user-provided information
prolog.consult("KB.pl")  # Consult the KB

# **Foreign Predicates for User Interaction**
# Define foreign predicates to handle user input and output.
def write_py(X):
    sys.stdout.flush()
    return True

write_py.arity = 1
registerForeign(write_py)

def read_py(A, V, Y):
    if isinstance(Y, Variable):
        if session["choices"][str(A)] == set():  # If user hasn't answered this question yet
            session["ask"] = str(A)  # Store the question for later retrieval
            raise QueryInterrupt(A, V)  # Raise an exception to pause the query
        else:
            session["ask"] = None  # Clear the question
        if str(V) in session["choices"][str(A)]:  # Check if the user's answer matches the option
            Y.unify(Atom("yes"))  # Unify the variable with 'yes'
        else:
            Y.unify(Atom("no"))  # Unify the variable with 'no'
        return True
    else:
        return False

read_py.arity = 3
registerForeign(read_py)

# **Flask App Initialization**
app = Flask(__name__)

# **Session Configuration**
app.config["SECRET_KEY"] = str(random.random())
app.config["SESSION_TYPE"] = "filesystem"
CORS(app, supports_credentials=True)
Session(app)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="None",
)
app.permanent_session_lifetime = timedelta(days=1000)

# **Prolog Cleanup After Request**
@app.after_request
def after_request_cleanup(response):
    if request.method in ['GET', 'POST']:
        call(retractall(known))  # Clear dynamic predicates
    return response


# Natural language mapping for questions
question_mapping = {
    "wifi": "Would you prefer a cafe with Wi-Fi?",
    "wifi_quality": "What is your preference for Wi-Fi quality?",
    "purchase_required": "Is it important if the cafe requires a purchase to stay?",
    "outlets": "How many power outlets would you like to have available?",
    "distance": "What is your preferred search radius?",
    "english_staff": "Do you require the staff to speak English?",
    "size": "What cafe size do you prefer?",
    "busyness": "How busy do you prefer the cafe to be?",
    "laptops_allowed": "Do you need a cafe that allows laptops?"
}


# Natural language mapping for options
option_mapping = {
    "wifi": {"yes": "Yes Please", "no": "Not necessary"},
    "wifi_quality": {"1": "Poor", "2": "Fair", "3": "Good", "4": "Very Good", "5": "Excellent"},
    "purchase_required": {"yes": "No, I'm fine if they require purchasing", "no": "Yes, I want to stay without purchasing anything"},
    "outlets": {"few": "Few outlets is sufficient", "tons": "I require many outlets"},
    "distance": {
        "less_than_1_km": "Less than 1 km",
        "between_1_2_km": "Between 1-2 km",
        "between_2_5_km": "Between 2-5 km",
        "between_5_10_km": "Between 5-10 km",
        "more_than_10_km": "More than 10 km"
    },
    "english_staff": {"yes": "Yes, Please!", "no": "No, I can manage!"},
    "size": {"small": "Small", "medium": "Medium", "big": "Big"},
    "busyness": {"1": "Very Quiet", "2": "Quiet", "3": "Moderate", "4": "Busy", "5": "Very Busy"},
    "laptops_allowed": {"yes": "Yes, it's important.", "no": "No, not necessary"}
}

result_mapping = {
    "cafe_martinez": "Café Martinez",
    "seul_cafe": "Seoul Café",
    "clorindo": "Clorindo Café",
    "seoul_cafe": "Seoul Café",
    "the_coffee_house": "The Coffee House",
    "cofi_jaus_palermo": "Cofi Jaus Palermo",
    "manifesto": "Manifesto",
    "moksha_studio": "Moksha Café Studio",
    "clorindo_cafe_brunch": "Clorindo Café",
    "las_flores": "Las Flores",
    "No Cafe satisfies your preferences" : "No Cafe satisfies your preferences"
}


# **Start Route**
@app.route("/")
def start():
    session.clear()
    session["choices"] = defaultdict(set)

    try:
        cafe = next(prolog.query("cafe(X).", maxresult=1))  # Get the first askable
    except StopIteration:
        cafe = {"X": "No Cafe satisfies your preferences"}
    except:
        ...

    if session["ask"]:  # If a question is pending
        ask_key = str(session["ask"])
        return {
            "ask": question_mapping[ask_key],  # Use natural language question
            "options": [option_mapping[ask_key][opt] for opt in options[ask_key]]  # Use natural language options
        }
    else:
        return {"result": {"X": result_mapping[cafe["X"]]}}  # Return the Cafe


# **Continuation Route**
@app.route("/ask", methods=["POST"])
def continuation():
    answers = request.json["answers"]

    # Map answers back to Prolog-compatible format
    ask_key = session["ask"]
    prolog_answers = {key for key, value in option_mapping[ask_key].items() if value in answers}
    session["choices"][ask_key] = prolog_answers  # Store the user's answers

    try:
        cafe = next(prolog.query("cafe(X).", maxresult=1))
    except StopIteration:
        cafe = {"X": "No Cafe satisfies your preferences"}
    except:
        ...
    
    if session["ask"]:
        ask_key = str(session["ask"])
        return {
            "ask": question_mapping[ask_key],
            "options": [option_mapping[ask_key][opt] for opt in options[ask_key]]
        }
    else:
        return {"result": {"X": result_mapping[cafe["X"]]}}

# **Dummy Route**
@app.route("/dummy", methods=["GET"])
def dummy():
    return {"result": 1}

# **App Start**
app.run(port=4000)
