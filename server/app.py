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
class QueryInterrupt(Exception):
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

# **Prolog Initialization**
prolog = Prolog()

# **Prolog Predicates**
retractall = Functor("retractall")
known = Functor("known", 3)
try:
    prolog.consult("KB.pl")
except Exception as e:
    print(f"Error loading Prolog KB: {e}")
    sys.exit(1)

# **Foreign Predicates for User Interaction**
def write_py(X):
    sys.stdout.flush()
    return True

write_py.arity = 1
registerForeign(write_py)

def read_py(A, V, Y):
    print(f"read_py called with: A={A}, V={V}, session['ask']={session.get('ask')}")
    if isinstance(Y, Variable):
        if not session.get("choices", {}).get(str(A)):
            session["ask"] = str(A)
            print(f"QueryInterrupt raised for attribute: {A}")
            raise QueryInterrupt(A, V)
        session["ask"] = None
        if str(V) in session["choices"].get(str(A), set()):
            Y.unify(Atom("yes"))
        else:
            Y.unify(Atom("no"))
        return True
    else:
        return False


read_py.arity = 3
registerForeign(read_py)

# **Flask App Initialization**
app = Flask(__name__)
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
        try:
            call(retractall(known))
        except Exception as e:
            print(f"Error during Prolog cleanup: {e}")
    return response

# **Start Route**
@app.route("/")
def start():
    session.clear()
    session["choices"] = defaultdict(set)
    session["ask"] = None

    try:
        print("Querying Prolog for problem...")
        problem = next(prolog.query("problem(X).", maxresult=1))
        print(f"Prolog returned: {problem}")
    except QueryInterrupt as e:
        print(f"QueryInterrupt: {e.attribute}")
        session["ask"] = e.attribute
        return {"ask": natural_language_question(session["ask"]), "options": list(options.get(session["ask"], []))}
    except StopIteration:
        problem = None
    except Exception as e:
        return {"error": f"Prolog query failed: {e}"}, 500

    if session["ask"]:
        return {"ask": natural_language_question(session["ask"]), "options": list(options.get(session["ask"], []))}
    else:
        return {"result": format_recommendation(problem)}


# **Continuation Route**
@app.route("/ask", methods=["POST"])
def continuation():
    answers = request.json.get("answers", [])
    if not session.get("ask"):
        return {"error": "No question pending"}, 400

    session["choices"][session["ask"]] = set(answers)
    try:
        problem = next(prolog.query("problem(X).", maxresult=1))
    except StopIteration:
        problem = None
    except Exception as e:
        return {"error": f"Prolog query failed: {e}"}, 500

    if session["ask"]:
        return {"ask": natural_language_question(session["ask"]), "options": list(options.get(session["ask"], []))}
    else:
        return {"result": format_recommendation(problem)}

# **Dummy Route**
@app.route("/dummy", methods=["GET"])
def dummy():
    return {"result": 1}

# **Natural Language Question Formatter**
def natural_language_question(attribute):
    questions = {
        "wifi": "Does the cafe have Wi-Fi?",
        "wifi_quality": "How would you rate the Wi-Fi quality?",
        "purchase_required": "Do you need to make a purchase to stay at the cafe?",
        "outlets": "Are there enough power outlets available?",
        "distance": "How far is the cafe from your location?",
        "english_staff": "Does the staff speak English?",
        "size": "What size of cafe are you looking for (small, medium, or big)?",
        "busyness": "How busy is the cafe usually?",
        "laptops_allowed": "Are laptops allowed in the cafe?",
    }
    return questions.get(attribute, f"Can you provide information about {attribute}?")

# **Recommendation Formatter**
def format_recommendation(problem):
    if not problem:
        return "No matching cafe was found. Please refine your preferences."
    return f"Based on your preferences, we recommend: {problem['X']}"

# **App Start**
if __name__ == "__main__":
    app.run(port=4000)