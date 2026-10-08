# references
# S. Bravy and A. Kitaev, PRA71(2005)022316

# Information of the local environment

# python: 3.11.11
# jupyter notebook: 7.4.4
# qiskit: 2.4.0
# qiskit-aer: 0.17.2
# qiskit-experiments: 0.13.0
# qiskit-ibm-experiment: 0.4.8
# qiskit-ibm-runtime: 0.46.1
import qiskit

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit import Parameter
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_histogram, plot_state_city
from qiskit.quantum_info import Statevector, DensityMatrix, SparsePauliOp, Operator
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, QiskitRuntimeService, SamplerV2 as Sampler

# Check that the account has been saved properly
# from qiskit_ibm_runtime import QiskitRuntimeService
# service = QiskitRuntimeService(name="qgss-2025")

# comment on the stabilizers of 5 qubits perfect code

# stabilisers for 5 qubits code
# the index of a strig is equal to the qubit index

S0 = "XZZXI"
S1 = "IXZZX"
S2 = "XIXZZ"
S3 = "ZXIXZ"
iD = "IIIII"

XZ_stab_label_list = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]

X_error_list = ["XIIII", "IXIII", "IIXII", "IIIXI","IIIIX"]
Z_error_list = ["ZIIII", "IZIII", "IIZII", "IIIZI","ZIIIZ"]

# 5 qubits code syndrome examples
# the ordering of this sindrome bit strings are defined by the anciella qubits ordering (q_anc[3], q_anc[2], q_anc[1], q_anc[0])
# ane their classical registers (c[3], c[2], c[1], c[0]).
# this is equivalent to the ordering (H_5_code[3], H_5_code[2], H_5_code[1], H_5_code[0]) = (s3, s2, s1, s0)

_5_qubits_code_decoder_syndrome_map = {
    '1000': 'X0',
    '0001': 'X1',
    '0011': 'X2',
    '0110': 'X3',
    '1100': 'X4',
    '0101': 'Z0',
    '1010': 'Z1',
    '0100': 'Z2',
    '1001': 'Z3',
    '0010': 'Z4',
    '0000': 'I'
}

# test
# _5_qubits_code_syndrome_string_list = list(_5_qubits_code_decoder_syndrome_map.keys())
# print(f"5 Qubits Code Syndrome List is here: {_5_qubits_code_syndrome_string_list}")

# end of the comment

# begin definiton of functions

NUM_PHY_Q = 9
NUM_Q = 5
NUM_ANC = 4

# state preparation
# in this example code, epsilon ( = epsilon_ini) which is a parameter in the initial mixed state to be distilled. is defined by
# epsilon = (1 - np.cos( delta )) / np.sqrt(6), where delta =  PHI - phi
# 0 < delta < PHI (0 < phi < PHI)
# phi = PHI corresponds to delta = 0 ( epsilon = 0 )

# version final
# test (initial state with a parameter) + (dephasing circuit)

# comment "Statevector()" implies that the function is used only for backend=AerSimulator(method="statevector")

# phi = Parameter("phi")
# phi_list = [i * 0.05 for i in range(16)]

THETA = np.arctan(np.sqrt(2))
PHI = np.pi / 4

def epsilon(x):

    return (1 - np.cos( PHI - x )) / np.sqrt(6)

def func_p_out(x):

    return (1 / 6) * (x ** 5 + 5 * x ** 3 * (1-x) ** 2 + 5 * x ** 2 * (1-x) ** 3 + (1-x) ** 5 )

def func_error_out(x):

    return ((x ** 5 + 5 * x ** 2) / (x ** 5 + 5 * x ** 3  + 5 * x ** 2  + 1 ))

def generate_rho_initial_5_qubits(phi): # Statevector()

    qc = QuantumCircuit(NUM_Q)

    qc.rx(- THETA, [0, 1, 2, 3, 4])
    qc.rz(- phi, [0, 1, 2, 3, 4])

    state_in = Statevector(qc)
    rho_in = DensityMatrix(state_in)

    return rho_in

def initialize_data_qubits(qc, q_data, phi):

    # state_ini
    THETA = np.arctan(np.sqrt(2))

    qc.rx(- THETA, q_data)
    qc.rz(- phi, q_data)

def decimal_to_base_3_number(input_n):
    # input_n is transformed to base-3 number

    if input_n == 0:
        return "00000"

    n = input_n
    base_3_str = ""

    while n > 0:
        base_3_str = str(n % 3) + base_3_str
        m = n // 3
        n = m

    while len(base_3_str) < NUM_Q:

        base_3_str = "0" + base_3_str

    return base_3_str

def t_type_dephasing_operation_5_qubits(qc, q_data, input_num):
    # idx is the qubit index
    # return 3 circuits for the dephasing operation

    depahsing_str = decimal_to_base_3_number(input_n=input_num)

    for idx, base_3 in enumerate(depahsing_str):

        if base_3 == "0":

            pass

        elif base_3 == "1":

            # T operation, phase factor does not affect to the density matirix
            qc.h(q_data[idx])
            qc.s(q_data[idx])

        else:
            assert base_3 == "2"

            # T^dagger operation, phase factor does not affect to the density matirix
            qc.sdg(q_data[idx])
            qc.h(q_data[idx])

    qc.barrier()

def initialize_state_ancilla_qubits(qc, q_anc):

    qc.reset(q_anc)

def syndrome_4_ancillas_no_reset_decoding(qc, q_data, q_anc, phi): # This function can be used only for SamplerV2 experiments

    # No error correction, syndrome is used to calculate rate of acceptance only

    # 5 qubits code only
    # generate a class 'qiskit.quantum_info.states.statevector.Statevector' object
    # state.data.shape = (num_q, )
    # state = np.zeros((num_q,), dtype=complex)

    # construct a circuit for syndrome measurement for 5 qubits code
    for i in range(NUM_ANC):

        qc.cx(q_data[np.mod(i+1, 5)], q_anc[i+0])
        qc.cx(q_data[np.mod(i+2, 5)], q_anc[i+0])

        qc.h(q_anc[i+0])
        qc.cx(q_anc[i+0], q_data[np.mod(i+3, 5)])
        qc.cx(q_anc[i+0], q_data[i+0])
        qc.h(q_anc[i+0])

        qc.barrier()

    # an error correction code for single-qubit error, a bit flip and also a phase flip, with if_test (Dynamic Circuit)
    # operate one of x(), y() and z () to the qubit with error

    # decoding without any conditions

    qc.cz(0, 1)
    qc.cz(1, 2)
    qc.cz(2, 3)
    qc.cz(3, 4)
    qc.cz(4, 0)

    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.h(3)
    qc.h(4)
    qc.barrier()

    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(0, 3)
    qc.cx(0, 4)
    qc.h(0)
    qc.z(0)
    qc.barrier()

    # swap |t0> and |t1>
    qc.h(0)
    qc.y(0)
    qc.barrier()

    # This is the state rotation to get the fidelity of the sate in SamplerV2
    # This rotation is dfined by hermite conjugation of "initialize_data_qubits(qc, q_data, phi)"
    # After this rotation, "0" means "|t0>" while "1" means "|t1>".

    qc.rz(+ phi, q_data[0])
    qc.rx(+ THETA, q_data[0])

def generate_state_t0_t1(): # Statevector()

    # Generate state |t0>, |t1> without error
    # definition of a logical state with no error

    state_0 = Statevector.from_label("0")
    state_1 = Statevector.from_label("1")

    a0 = np.sqrt((np.sqrt(3)+1) / (2 * np.sqrt(3)))
    b0 = np.sqrt((np.sqrt(3)-1) / (2 * np.sqrt(3)))

    state_t0 = a0 * state_0 + np.exp(np.pi * 1j / 4) * b0 * state_1
    state_t1 = np.exp(- np.pi * 1j / 4) * b0 * state_0 - a0 * state_1

    return state_t0, state_t1

def calculate_accept_rate_and_error_rate(shots, reps, accept_counts_list, error_counts_list):

    accept_rates = [0. for i in range(len(accept_counts_list))]
    error_rates = [0. for i in range(len(error_counts_list))]

    for idx, value in enumerate(accept_counts_list):
        rate = value / (shots * reps)
        accept_rates[idx] = rate

    for kdx, value_ in enumerate(error_counts_list):
        rate_ = value_ / accept_counts_list[kdx]
        error_rates[kdx] = rate_

    return accept_rates, error_rates

# end definition of functions
