from T_type_distillation_qiskit_experiments import (
    TTypeDistillationExperiment,
    TTypeDistillationAnalysis,
    NUM_CIRC,
    SHOTS,
)

def test_circuits_count_and_metadata():
    params = [0.0, 0.1]

    experiment = TTypeDistillationExperiment(
        physical_qubits=tuple(range(9)),
        list_params=params,
    )

    circuits = experiment.circuits()

    assert len(circuits) == NUM_CIRC * len(params)

    # First circuit in the first parameter group
    assert circuits[0].metadata["circuit_id"] == 0
    assert circuits[0].metadata["phi_idx"] == 0
    assert circuits[0].metadata["φ"] == 0.0

    # First circuit in the second parameter group
    assert circuits[NUM_CIRC].metadata["circuit_id"] == 0
    assert circuits[NUM_CIRC].metadata["phi_idx"] == 1
    assert circuits[NUM_CIRC].metadata["φ"] == 0.1

    # Last circuit in the second parameter group
    assert circuits[-1].metadata["circuit_id"] == NUM_CIRC - 1
    assert circuits[-1].metadata["phi_idx"] == 1

class FakeExperimentData:
    """Minimal test double for the analysis input."""

    def __init__(self, data):
        self._data = data

    def data(self):
        return self._data

def test_analysis_counts_and_result_lengths():
    params = [0.0, 0.1]
    data = []

    # Simulate two complete parameter groups.
    # Every shot is accepted and has no logical error.
    for phi_idx, phi_value in enumerate(params):
        for circuit_id in range(NUM_CIRC):
            data.append({
                "counts": {"000000000": SHOTS},
                "metadata": {
                    "circuit_id": circuit_id,
                    "phi_idx": phi_idx,
                    "φ": phi_value,
                },
            })

    analysis = TTypeDistillationAnalysis()
    analysis.set_options(plot=False)

    results, figures = analysis._run_analysis(
        FakeExperimentData(data)
    )

    # Convert analysis results to a dictionary for easy checking.
    result_dict = {
        result.name: result.value
        for result in results
    }

    assert result_dict["phi_list"] == params

    expected_accepted = NUM_CIRC * SHOTS
    assert result_dict["accept_counts"] == [
        expected_accepted,
        expected_accepted,
    ]

    assert result_dict["accept_counts_check"] == [
        expected_accepted,
        expected_accepted,
    ]

    assert result_dict["error_counts"] == [0, 0]

    # All result lists should have one entry per parameter.
    assert len(result_dict["accept_counts"]) == len(params)
    assert len(result_dict["accept_counts_check"]) == len(params)
    assert len(result_dict["error_counts"]) == len(params)

    # Plotting is disabled for this test.
    assert figures == []
