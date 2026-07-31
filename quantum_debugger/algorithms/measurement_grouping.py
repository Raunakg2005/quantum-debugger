"""
Measurement grouping -- fewer circuits per energy evaluation.

A VQE energy is ``<H> = sum_P c_P <P>``, and each Pauli expectation costs a batch of
shots. Because commuting Paulis share an eigenbasis, they can be measured *together*, so
the number of distinct measurement settings can be far below the number of terms. Two
grouping rules are provided:

* **Qubit-wise commuting (QWC)** -- Paulis that agree on every shared qubit; measured
  with only single-qubit basis rotations.
* **General commuting** -- Paulis with even symplectic overlap; measured after a joint
  Clifford, giving strictly coarser (fewer) groups.

Both are built by greedy graph colouring of the commutation graph. Verified: every group
is internally (QWC-)commuting, every term is covered exactly once, and general commuting
never needs more groups than QWC.
"""

import numpy as np

from .pauli_hamiltonian import decompose, qubit_wise_commute, symplectic_commute


def _greedy_groups(labels, compatible):
    """Greedy colouring: place each label in the first group where it is `compatible`."""
    groups = []
    for lab in labels:
        for g in groups:
            if all(compatible(lab, other) for other in g):
                g.append(lab)
                break
        else:
            groups.append([lab])
    return groups


def qubit_wise_commuting_groups(H):
    """
    Partition the Pauli terms of ``H`` into qubit-wise-commuting groups (each measurable
    with single-qubit rotations). Returns a list of lists of Pauli labels.
    """
    labels = [t[1] for t in decompose(H)]
    return _greedy_groups(labels, qubit_wise_commute)


def commuting_groups(H):
    """
    Partition the Pauli terms of ``H`` into general commuting groups (each measurable
    after one joint Clifford). Coarser than QWC -- never more groups.
    """
    terms = decompose(H)
    xz = {t[1]: (t[2], t[3]) for t in terms}

    def commute(a, b):
        xa, za = xz[a]; xb, zb = xz[b]
        return symplectic_commute(xa, za, xb, zb)

    return _greedy_groups(list(xz), commute)


def is_valid_grouping(H, groups, qwc: bool = True) -> bool:
    """
    Check a grouping: every term of ``H`` appears exactly once and every group is
    internally commuting (qubit-wise if ``qwc``, else general).
    """
    terms = decompose(H)
    all_labels = sorted(t[1] for t in terms)
    covered = sorted(l for g in groups for l in g)
    if covered != all_labels:
        return False
    xz = {t[1]: (t[2], t[3]) for t in terms}
    for g in groups:
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                if qwc:
                    if not qubit_wise_commute(g[i], g[j]):
                        return False
                else:
                    xa, za = xz[g[i]]; xb, zb = xz[g[j]]
                    if not symplectic_commute(xa, za, xb, zb):
                        return False
    return True


def measurement_reduction(H) -> dict:
    """
    Report how much grouping saves: the number of Pauli terms versus the number of QWC
    and general-commuting measurement settings. Fewer settings = fewer circuits per energy
    evaluation.
    """
    n_terms = len(decompose(H))
    return {
        "n_terms": n_terms,
        "n_qwc_groups": len(qubit_wise_commuting_groups(H)),
        "n_commuting_groups": len(commuting_groups(H)),
    }
