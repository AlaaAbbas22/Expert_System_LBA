% Knowledge base for cafe recommendations dynamically assessing user inputs

% Cafe facts with attributes
cafe(cafe_martinez, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(less_than_1_km), english_staff(no), size(medium), busyness(2), laptops_allowed(yes)]).
cafe(clorindo, [wifi(yes), wifi_quality(5), purchase_required(yes), outlets(few), distance(between_1_2_km), english_staff(yes), size(big), busyness(3), laptops_allowed(yes)]).
cafe(cofi_jaus_palermo, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(between_5_10_km), english_staff(yes), size(big), busyness(3), laptops_allowed(yes)]).
cafe(manifesto, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(less_than_1_km), english_staff(yes), size(small), busyness(3), laptops_allowed(yes)]).
cafe(moksha_studio, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(between_5_10_km), english_staff(yes), size(small), busyness(3), laptops_allowed(yes)]).
cafe(toki, [wifi(yes), wifi_quality(3), purchase_required(yes), outlets(few), distance(less_than_1_km), english_staff(yes), size(small), busyness(3), laptops_allowed(yes)]).
cafe(clorindo_cafe_brunch, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(between_1_2_km), english_staff(yes), size(big), busyness(4), laptops_allowed(yes)]).
cafe(las_flores, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(few), distance(between_5_10_km), english_staff(no), size(big), busyness(4), laptops_allowed(yes)]).
cafe(seul_cafe, [wifi(yes), wifi_quality(3), purchase_required(yes), outlets(few), distance(less_than_1_km), english_staff(yes), size(small), busyness(3), laptops_allowed(yes)]).
cafe(seoul_cafe, [wifi(yes), wifi_quality(4), purchase_required(yes), outlets(tons), distance(less_than_1_km), english_staff(no), size(small), busyness(3), laptops_allowed(yes)]).

% Rule to dynamically determine a recommendation based on user preferences
problem(Cafe) :- cafe(Cafe, Attributes), satisfies_preferences(Attributes).

% Dynamically satisfies preferences based on known facts
satisfies_preferences(Attributes) :-
    findall(Attribute(Value), known(yes, Attribute, Value), KnownPreferences),
    forall(member(Attribute(Value), KnownPreferences), member(Attribute(Value), Attributes)).

% Dynamic predicates for storing known facts
:- dynamic known/3, multivalued/1.

% Adding askables dynamically
wifi(X) :- ask(wifi, X).
wifi_quality(X) :- ask(wifi_quality, X).
purchase_required(X) :- ask(purchase_required, X).
outlets(X) :- ask(outlets, X).
distance(X) :- ask(distance, X).
english_staff(X) :- ask(english_staff, X).
size(X) :- ask(size, X).
busyness(X) :- ask(busyness, X).
laptops_allowed(X) :- ask(laptops_allowed, X).

% Asking clauses
ask(A, V) :-
    known(yes, A, V),
    !.

ask(A, V) :-
    known(_, A, V),
    !, fail.

ask(A, V) :-
    \+multivalued(A),
    known(yes, A, V2),
    V \== V2,
    !, fail.

ask(A, V) :-
    read_py(A, V, Y),
    assertz(known(Y, A, V)),
    Y == yes.
