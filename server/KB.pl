%  Tell prolog that known/3 and multivalued/1 will be added later
:- dynamic known/3, multivalued/1.

% Enter your KB below this line:
%%%% Add in your rules here %%%
problem(battery) :- \+engine(turning_over), battery(bad).
problem(engine_oil_low) :- \+engine(turning_over), warning_light(oil).
battery(bad) :- light(weak).
battery(bad) :- radio(weak).
problem(engine_flooded) :- engine(turning_over), smell(gas).
problem(out_of_gas) :- engine(turning_over), gas_gauge(empty).


% The code below implements the prompting to ask the user:
%%%% Add in your askables here %%%%
light(X) :- ask(light, X).
radio(X) :- ask(radio, X).
engine(X) :- ask(engine, X).
smell(X) :- ask(smell, X).
gas_gauge(X) :- ask(gas_gauge, X).
warning_light(X) :- ask(warning_light, X).


% Asking clauses

ask(A, V):-
known(yes, A, V), % succeed if true
!.	% stop looking

ask(A, V):-
known(_, A, V), % fail if false
!, fail.

% If not multivalued, and already known to be something else, don't ask again for a different value.
ask(A, V):-
\+multivalued(A),
known(yes, A, V2),
V \== V2,
!, fail.

ask(A, V):-
read_py(A,V,Y), % get the answer
assertz(known(Y, A, V)), % remember it
Y == yes.	% succeed or fail