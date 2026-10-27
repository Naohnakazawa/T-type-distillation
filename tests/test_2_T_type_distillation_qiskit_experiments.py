# chat GPT's new test sample 20261026
from T_type_distillation_qiskit_experiments import ( TTypeDistillationExperiment,
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

    # Check every circuit's metadata and parameter grouping.
    for phi_idx, phi_value in enumerate(params):
        group = circuits[
            phi_idx * NUM_CIRC:(phi_idx + 1) * NUM_CIRC
        ]
    
        assert len(group) == NUM_CIRC
    
        for circuit_id, circuit in enumerate(group):
            assert circuit.metadata["circuit_id"] == circuit_id
            assert circuit.metadata["phi_idx"] == phi_idx
            assert circuit.metadata["φ"] == phi_value
    
            # Parameters should be bound before execution.
            assert len(circuit.parameters) == 0

def test_circuits_empty_parameter_list():
    experiment = TTypeDistillationExperiment(
        physical_qubits=tuple(range(9)),
        list_params=[],
    )

    assert experiment.circuits() == []

class FakeExperimentData:
    """Minimal test double for the analysis input."""
    
    def __init__(self, data):
        self._data = data
    
    def data(self):
        return self._data
    def make_experiment_data(params, counts_factory):
        """Build synthetic data in circuit submission order."""
        data = []
        
        for phi_idx, phi_value in enumerate(params):
            for circuit_id in range(NUM_CIRC):
                data.append(
                    {
                        "counts": counts_factory(),
                        "metadata": {
                            "circuit_id": circuit_id,
                            "phi_idx": phi_idx,
                            "φ": phi_value,
                        },
                    }
                )
        
        return FakeExperimentData(data)

    def run_analysis(data):
        analysis = TTypeDistillationAnalysis()
        analysis.set_options(plot=False)
        
        results, figures = analysis._run_analysis(data)
        
        result_dict = {
            result.name: result.value
            for result in results
        }
        
        assert figures == []
        return result_dict

    def test_analysis_all_shots_accepted_without_error():
        params = [0.0, 0.1]
        
        data = make_experiment_data(
            params,
            lambda: {"000000000": SHOTS},
        )
        
        result_dict = run_analysis(data)
        
        expected_accepted = NUM_CIRC * SHOTS
    
        assert result_dict["phi_list"] == params
        assert result_dict["accept_counts"] == [
            expected_accepted,
            expected_accepted,
        ]
        assert result_dict["accept_counts_check"] == [
            expected_accepted,
            expected_accepted,
        ]
        assert result_dict["error_counts"] == [0, 0]
        
    def test_analysis_counts_logical_errors_and_rejected_shots():
        params = [0.0, 0.1]

    def mixed_counts():
        return {
            # Accepted, no logical error.
            "000000000": SHOTS - 3,
            # Accepted, logical error.
            "000000001": 2,
            # Nonzero syndrome: rejected.
            "000100000": 1,
        }
    
        data = make_experiment_data(params, mixed_counts)
        result_dict = run_analysis(data)
        
        expected_accepted = NUM_CIRC * (SHOTS - 1)
        expected_errors = NUM_CIRC * 2
        
        assert result_dict["phi_list"] == params
        assert result_dict["accept_counts"] == [
            expected_accepted,
            expected_accepted,
        ]
        assert result_dict["accept_counts_check"] == [
            expected_accepted,
            expected_accepted,
        ]
        assert result_dict["error_counts"] == [
            expected_errors,
            expected_errors,
        ]

    def test_analysis_rejects_malformed_bitstring():
        data = FakeExperimentData(
            [ { "counts": {"00000000": SHOTS},
                "metadata": { "circuit_id": 0,
                              "phi_idx": 0,
                              "φ": 0.0,
                            }, 
              } 
            ] 
        )
    
    
        analysis = TTypeDistillationAnalysis()
        analysis.set_options(plot=False)
        
        with pytest.raises(ValueError, match="Unexpected key_bitstring"):
            analysis._run_analysis(data)

    def test_analysis_result_lists_match_parameter_count():
        params = [0.0, 0.1, 0.2]
    
    
        data = make_experiment_data(
            params,
            lambda: {"000000000": SHOTS},
        )
        
        result_dict = run_analysis(data)
        
        for name in (
            "phi_list",
            "accept_counts",
            "accept_counts_check",
            "error_counts",
        ):
            assert len(result_dict[name]) == len(params)
