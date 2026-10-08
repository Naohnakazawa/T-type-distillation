# tests/test_five_qubits_code_T_type_distillation.py

import numpy as np
import pytest

from qiskit import QuantumCircuit, QuantumRegister

from five_qubits_code_T_type_distillation import (
    NUM_Q,
    PHI,
    epsilon,
    func_p_out,
    func_error_out,
    decimal_to_base_3_number,
    initialize_data_qubits,
    initialize_state_ancilla_qubits,
    t_type_dephasing_operation_5_qubits,
    generate_state_t0_t1,
    generate_rho_initial_5_qubits,
    calculate_accept_rate_and_error_rate,
)


# ============================================================
# Mathematical functions
# ============================================================

def test_epsilon_at_phi():
    assert epsilon(PHI) == pytest.approx(0.0)


@pytest.mark.parametrize(
    "x",
    [0.0, 0.1, 0.25, 0.5, 0.75, 1.0],
)
def test_func_p_out_is_finite(x):
    assert np.isfinite(func_p_out(x))


@pytest.mark.parametrize(
    "x",
    [0.0, 0.1, 0.25, 0.5, 0.75, 1.0],
)
def test_func_error_out_is_finite(x):
    assert np.isfinite(func_error_out(x))


# ============================================================
# Base-3 conversion
# ============================================================

@pytest.mark.parametrize(
    "input_n, expected",
    [
        (0, "00000"),
        (1, "00001"),
        (2, "00002"),
        (3, "00010"),
        (4, "00011"),
        (5, "00012"),
        (8, "00022"),
        (9, "00100"),
    ],
)
def test_decimal_to_base_3_number(input_n, expected):
    assert decimal_to_base_3_number(input_n) == expected


@pytest.mark.parametrize("input_n", range(3**NUM_Q))
def test_decimal_to_base_3_number_properties(input_n):

    result = decimal_to_base_3_number(input_n)

    assert len(result) == NUM_Q
    assert all(c in "012" for c in result)


# ============================================================
# Quantum circuit construction
# ============================================================

def test_initialize_data_qubits():

    q_data = QuantumRegister(NUM_Q, "data")
    qc = QuantumCircuit(q_data)

    initialize_data_qubits(
        qc,
        q_data,
        phi=0.3,
    )

    assert qc.count_ops()["rx"] == NUM_Q
    assert qc.count_ops()["rz"] == NUM_Q


def test_initialize_state_ancilla_qubits():

    q_anc = QuantumRegister(4, "anc")
    qc = QuantumCircuit(q_anc)

    initialize_state_ancilla_qubits(
        qc,
        q_anc,
    )

    assert qc.count_ops()["reset"] == 4


@pytest.mark.parametrize("input_num", range(3**NUM_Q))
def test_dephasing_gate_counts(input_num):

    q_data = QuantumRegister(NUM_Q, "data")
    qc = QuantumCircuit(q_data)

    t_type_dephasing_operation_5_qubits(
        qc,
        q_data,
        input_num,
    )

    ternary = decimal_to_base_3_number(input_num)

    n_nonzero = sum(
        digit != "0"
        for digit in ternary
    )

    assert qc.count_ops().get("h", 0) == n_nonzero

    assert (
        qc.count_ops().get("s", 0)
        + qc.count_ops().get("sdg", 0)
    ) == n_nonzero


# ============================================================
# Quantum states
# ============================================================

def test_generate_state_t0_t1_are_normalized():

    state_t0, state_t1 = generate_state_t0_t1()

    norm_t0_squared = np.vdot(
        state_t0.data,
        state_t0.data,
    )

    norm_t1_squared = np.vdot(
        state_t1.data,
        state_t1.data,
    )

    assert norm_t0_squared == pytest.approx(1.0)
    assert norm_t1_squared == pytest.approx(1.0)


def test_generate_state_t0_t1_are_orthogonal():

    state_t0, state_t1 = generate_state_t0_t1()

    overlap = np.vdot(
        state_t0.data,
        state_t1.data,
    )

    assert overlap == pytest.approx(0.0)


def test_generate_rho_initial_5_qubits():

    rho = generate_rho_initial_5_qubits(0.2)

    assert rho.dims(qargs = [0, 1, 2, 3, 4]) == (2, 2, 2, 2, 2)
    assert np.trace(rho.data) == pytest.approx(1.0)

    assert np.allclose(
        rho.data,
        rho.data.conj().T,
    )


# ============================================================
# Rate calculation
# ============================================================

def test_calculate_accept_rate_and_error_rate():

    shots = 100
    reps = 2

    accept_counts = [100, 50]
    error_counts = [10, 5]

    accept_rates, error_rates = (
        calculate_accept_rate_and_error_rate(
            shots,
            reps,
            accept_counts,
            error_counts,
        )
    )

    assert accept_rates == pytest.approx(
        [0.5, 0.25]
    )

    assert error_rates == pytest.approx(
        [0.1, 0.1]
    )
