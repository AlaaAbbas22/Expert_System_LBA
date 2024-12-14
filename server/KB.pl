%  Tell prolog that known/3 and multivalued/1 will be added later
:- dynamic known/3, multivalued/1.

% Declare which attributes are multivalued
multivalued(wifi_quality).
multivalued(distance).
multivalued(size).
multivalued(busyness).
multivalued(outlets).

% Enter your KB below this line:
%%%% Add in your rules here %%%
cafe(cafe_martinez) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(less_than_1_km),
    english_staff(no),
    size(medium),
    busyness(2),
    laptops_allowed(yes).

cafe(clorindo) :-
    wifi(yes),
    wifi_quality(5),
    purchase_required(yes),
    outlets(few),
    distance(between_1_2_km),
    english_staff(yes),
    size(big),
    busyness(3),
    laptops_allowed(yes).

cafe(cofi_jaus_palermo) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(between_5_10_km),
    english_staff(yes),
    size(big),
    busyness(3),
    laptops_allowed(yes).

cafe(manifesto) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(less_than_1_km),
    english_staff(yes),
    size(small),
    busyness(3),
    laptops_allowed(yes).

cafe(moksha_studio) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(between_5_10_km),
    english_staff(yes),
    size(small),
    busyness(3),
    laptops_allowed(yes).

cafe(toki) :-
    wifi(yes),
    wifi_quality(3),
    purchase_required(yes),
    outlets(few),
    distance(less_than_1_km),
    english_staff(yes),
    size(small),
    busyness(3),
    laptops_allowed(yes).

cafe(clorindo_cafe_brunch) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(between_1_2_km),
    english_staff(yes),
    size(big),
    busyness(4),
    laptops_allowed(yes).

cafe(las_flores) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(few),
    distance(between_5_10_km),
    english_staff(no),
    size(big),
    busyness(4),
    laptops_allowed(yes).

cafe(seul_cafe) :-
    wifi(yes),
    wifi_quality(3),
    purchase_required(yes),
    outlets(few),
    distance(less_than_1_km),
    english_staff(yes),
    size(small),
    busyness(3),
    laptops_allowed(yes).

cafe(seoul_cafe) :-
    wifi(yes),
    wifi_quality(4),
    purchase_required(yes),
    outlets(tons),
    distance(less_than_1_km),
    english_staff(no),
    size(small),
    busyness(3),
    laptops_allowed(yes).


% The code below implements the prompting to ask the user:
%%%% Add in your askables here %%%%
wifi(X) :- ask(wifi, X).
purchase_required(X) :- ask(purchase_required, X).
english_staff(X) :- ask(english_staff, X).
laptops_allowed(X) :- ask(laptops_allowed, X).

wifi_quality(X) :- ask(wifi_quality, X).
distance(X) :- ask(distance, X).
size(X) :- ask(size, X).
busyness(X) :- ask(busyness, X).
outlets(X) :- ask(outlets, X).

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