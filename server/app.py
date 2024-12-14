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

# **Start Route**
@app.route("/")
def start():
    session.clear()
    session["choices"] = defaultdict(set)

    try:
        cafe = next(prolog.query("cafe(X).", maxresult=1))  # Get the first askable
    except StopIteration:
        cafe = {"X": "No Cafe"}
    except:
        ...

    if session["ask"]:  # If a question is pending
        return {"ask": str(session["ask"]), "options": list(options[str(session["ask"])])}
    else:
        return {"result": cafe}  # Return the Cafe

# **Continuation Route**
@app.route("/ask", methods=["POST"])
def continuation():
    answers = request.json["answers"]
    session["choices"][session["ask"]] = set(answers)  # Store the user's answers
    try:
        cafe = next(prolog.query("cafe(X).", maxresult=1))
    except StopIteration:
        cafe = {"X": "No Cafe"}
    except:
        ...
    
    if session["ask"]:
        return {"ask": str(session["ask"]), "options": list(options[str(session["ask"])])}
    else:
        return {"result": cafe}

# **Dummy Route**
@app.route("/dummy", methods=["GET"])
def dummy():
    return {"result": 1}

# **App Start**
app.run(port=4000)