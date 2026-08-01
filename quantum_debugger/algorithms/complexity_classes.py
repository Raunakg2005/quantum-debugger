"""
Complexity classes and their containments.

Where does quantum computing sit in the complexity landscape? The relevant classes and their
*proven* containments form a partial order,

    P  subseteq  BPP  subseteq  BQP  subseteq  PP  subseteq  PSPACE,
    P  subseteq  NP   subseteq  PSPACE,

with **BQP** (bounded-error quantum polynomial time) the class of problems a quantum computer
solves efficiently. Factoring and discrete log are in BQP (via Shor) but not known to be in BPP;
whether ``BPP = BQP`` (no quantum advantage) or ``BQP`` contains ``NP`` are famous open problems.
This module encodes the known containment DAG, answers containment queries by transitive closure,
and verifies the order is consistent (reflexive, transitive, acyclic).
"""

_CONTAINMENTS = {
    "P": ["BPP", "NP"],
    "BPP": ["BQP"],
    "BQP": ["PP"],
    "NP": ["PSPACE"],
    "PP": ["PSPACE"],
    "PSPACE": ["EXP"],
    "EXP": [],
}

# Problems and the smallest class they are known to lie in.
_PROBLEM_CLASS = {
    "factoring": "BQP",
    "discrete_log": "BQP",
    "unstructured_search": "BQP",     # quadratic speedup, still in BQP
    "simulation": "BQP",
    "sat": "NP",
    "primality": "P",
    "sorting": "P",
}


def known_containments() -> dict:
    """The proven containment DAG of complexity classes (each class -> the classes proven to
    contain it directly)."""
    return {k: list(v) for k, v in _CONTAINMENTS.items()}


def contains(bigger: str, smaller: str) -> bool:
    """
    True iff ``smaller subseteq bigger`` is a *proven* containment (by transitive closure of the
    known DAG). Reflexive. E.g. ``contains('PSPACE', 'BQP')`` is True; ``contains('BQP', 'NP')`` is
    not known.
    """
    if bigger == smaller:
        return True
    seen, stack = set(), [smaller]
    while stack:
        c = stack.pop()
        for nxt in _CONTAINMENTS.get(c, []):
            if nxt == bigger:
                return True
            if nxt not in seen:
                seen.add(nxt); stack.append(nxt)
    return False


def problem_class(problem: str) -> str:
    """The smallest complexity class a problem is known to lie in -- ``BQP`` for factoring /
    simulation, ``P`` for sorting, etc."""
    return _PROBLEM_CLASS[problem]


def in_bqp(problem: str) -> bool:
    """True iff a problem is (known to be) solvable in bounded-error quantum polynomial time --
    i.e. its class is contained in BQP."""
    return contains("BQP", problem_class(problem))


def is_open_separation(a: str, b: str) -> bool:
    """
    True iff whether ``a subseteq b`` (or its reverse) is an *open* problem -- neither containment
    is proven. E.g. ``BPP`` vs ``BQP`` (does quantum help?) and ``BQP`` vs ``NP`` are open.
    """
    return not contains(a, b) and not contains(b, a)


def hierarchy_is_consistent() -> bool:
    """
    Verify the containment order is a consistent partial order: reflexive, transitive, and acyclic
    (no class strictly contains itself). The sanity check on the encoded knowledge.
    """
    classes = list(_CONTAINMENTS)
    # reflexive
    if not all(contains(c, c) for c in classes):
        return False
    # transitive
    for a in classes:
        for b in classes:
            for c in classes:
                if contains(a, b) and contains(b, c) and not contains(a, c):
                    return False
    # acyclic: no two distinct classes contain each other
    for a in classes:
        for b in classes:
            if a != b and contains(a, b) and contains(b, a):
                return False
    return True
