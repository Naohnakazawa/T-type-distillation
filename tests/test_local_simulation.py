# This test is suggested by chat GPT 20261013

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def test_aer_simulator_executes_a_circuit():
    """Verify that Aer can execute a circuit and return measurements."""
    circuit = QuantumCircuit(1, 1)
    circuit.x(0)
    circuit.measure(0, 0)

    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=100).result()
    counts = result.get_counts()

    assert counts == {"1": 100}
