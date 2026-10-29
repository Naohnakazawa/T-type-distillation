import numpy as np

from qiskit.circuit import QuantumCircuit, Parameter
from typing import List, Optional, Sequence
from collections import defaultdict
from qiskit.providers.backend import Backend
from qiskit_aer import AerSimulator
from qiskit_experiments.framework import BaseExperiment, Options

# TTypeDistillationAnalysis()
import matplotlib.pyplot as plt
from qiskit_experiments.framework import (
    BaseAnalysis,
    ExperimentData,
    AnalysisResultData
)

# module for circuit construction
from five_qubits_code_T_type_distillation import epsilon, \
                                                func_p_out, \
                                                func_error_out, \
                                                initialize_data_qubits, \
                                                t_type_dephasing_operation_5_qubits, \
                                                initialize_state_ancilla_qubits, \
                                                syndrome_4_ancillas_no_reset_decoding, \
                                                calculate_accept_rate_and_error_rate

# parameter values in this module
NUM_CIRC = 243 # == 3 ** 5
SHOTS = 1024

# TTypeDistillationExperiment()
class TTypeDistillationExperiment(BaseExperiment):
    """Custom experiment class template."""

    def __init__(self,
                 physical_qubits: Sequence[int],
                 analysis: Optional = None,
                 backend: Optional[Backend] = None,
                 list_params: Optional[List[float]] = None,
                ):
        """Initialize the experiment."""
        super().__init__(physical_qubits,
                         analysis = analysis or TTypeDistillationAnalysis(),
                         backend = backend,
        )
        self.set_experiment_options(
            list_params=list_params if list_params is not None else []
        )

    @classmethod
    def _default_experiment_options(cls) -> Options:
        """Set default experiment options here."""
        options = super()._default_experiment_options()
        options.list_params = []
        return options
    
    def circuits(self) -> List[QuantumCircuit]:
        """Generate the list of circuits to be run."""
        phi = Parameter("φ")
        circuits_initialized = []
        # Generate circuits and populate metadata here
        for i in range(NUM_CIRC):

            circ = QuantumCircuit(self.num_qubits)

            initialize_state_ancilla_qubits(qc=circ, q_anc=[5, 6, 7, 8])
            initialize_data_qubits(qc=circ, q_data=[0, 1, 2, 3, 4], phi=phi)

            t_type_dephasing_operation_5_qubits(qc=circ, q_data=[0, 1, 2, 3, 4], input_num=i)
            syndrome_4_ancillas_no_reset_decoding(qc=circ, q_data=[0, 1, 2, 3, 4], q_anc=[5, 6, 7, 8], phi=phi)

            circ.measure_all()

            circ.metadata = {"circuit_id": i}
            circuits_initialized.append(circ)

        circuits = []
        for phi_idx, phi_value in enumerate(self.experiment_options.list_params):
            for circuit_initialized in circuits_initialized:
                bound_circuit = circuit_initialized.assign_parameters(
                    {phi: phi_value}
                )
                bound_circuit.metadata = {
                    **(bound_circuit.metadata or {}),
                    "phi_idx": phi_idx,
                    "φ": phi_value,
                }
                circuits.append(bound_circuit)

        return circuits

class TTypeDistillationAnalysis(BaseAnalysis):
    """Custom analysis class template."""

    @classmethod
    def _default_options(cls) -> Options:
        """Set default analysis options. Plotting is on by default."""

        options = super()._default_options()
        options.plot = True
        return options

    def _run_analysis(
        self,
        experiment_data: ExperimentData
    ):

        _phi_dict = { } # 
        _accept_counts = defaultdict(int)
        _accept_counts_check = defaultdict(int)
        _error_counts = defaultdict(int)

        for idx, datum in enumerate(experiment_data.data()): # 3888 = 16 * 243

            circuit_idx = idx % NUM_CIRC
            phi_value_idx = idx // NUM_CIRC

#            assert idx == phi_value_idx * NUM_CIRC + circuit_idx # move the line to pytest

            counts = datum["counts"]
            metadata = datum["metadata"]
            phi_value = metadata["φ"]

#            assert circuit_idx == metadata["circuit_id"] # confirm the structure of experiment_data.data() 
#            assert phi_value_idx == metadata["phi_idx"] # move the line to pytest

            # test _phi_list
            if metadata["circuit_id"] == 0:
                _phi_dict[metadata["phi_idx"]] = phi_value

            else:
                pass
            
            for key_bitstring, value in counts.items():

                if len(key_bitstring) != 9: # assume 9 physical_qubits in 5 qubits perfect code
                    raise ValueError(
                        f"Unexpected key_bitstring: {key_bitstring}"
                    )

                else:
                    
                    pass

                ancilla_bits = key_bitstring[:4]
                data_bits = key_bitstring[4:]

                if ancilla_bits == "0000":

                    _accept_counts[phi_value] += value

                    if data_bits == "00000":

                        _accept_counts_check[phi_value] += value
                        _error_counts[phi_value] += 0

                    elif data_bits == "00001":

                        _accept_counts_check[phi_value] += value
                        _error_counts[phi_value] += value

                    else:
                        
                        pass
                else:
                    
                    pass

            # Confirm that _accept_counts is equal to _accept_counts_check
#            assert _accept_counts[phi_value] == _accept_counts_check[phi_value] # move the line to pytest

        # test  _phi_list
        _phi_list = [_phi_value for _phi_value in _phi_dict.values()]

        # test _accept_counts and error_counts
        _accept_counts_list = [value for value in _accept_counts.values()]
        _accept_counts_check_list = [value for value in _accept_counts_check.values()]
        _error_counts_list = [value for value in _error_counts.values()]

#        assert len(_accept_counts_list) == len(_phi_list) # move the line to pytest
#        assert len(_accept_counts_check_list) == len(_phi_list) # move the line to pytest
#        assert len(_error_counts_list) == len(_phi_list) # move the line to pytest

        analysis_results = [
            AnalysisResultData(name="phi_list", value=_phi_list),
            AnalysisResultData(name="accept_counts", value=_accept_counts_list),
            AnalysisResultData(name="accept_counts_check", value=_accept_counts_check_list),
            AnalysisResultData(name="error_counts", value=_error_counts_list),
        ]

        # visualization
        
        figures = []

        phi_list = _phi_list
        
        accept_rates, error_rates = calculate_accept_rate_and_error_rate(
            shots=SHOTS,
            reps=NUM_CIRC, 
            accept_counts_list=_accept_counts_list, 
            error_counts_list=_error_counts_list,
            )

        if self.options.plot:
            # Theoretical acceptance probabilities
            epsilon_data = [epsilon(phi) for phi in phi_list]
        
            theoretical_accept_rates = [
                func_p_out(eps) for eps in epsilon_data
            ]
        
            fig_accept, ax_accept = plt.subplots()
        
            ax_accept.plot(
                phi_list,
                theoretical_accept_rates,
                "x-",
                label="Theory",
            )
            ax_accept.plot(
                phi_list,
                accept_rates,
                "o",
                label="Simulation",
            )
        
            ax_accept.set_xlabel(r"$\phi_{\mathrm{in}}$")
            ax_accept.set_ylabel(r"$P_{\mathrm{accept}}$")
            ax_accept.set_title("T-type Distillation: Acceptance Rate")
            ax_accept.legend()
            ax_accept.grid(True, alpha=0.3)
        
            figures.append(fig_accept)

            # Theoretical output error rates
            theoretical_error_rates = [
                func_error_out(eps / (1 - eps))
                for eps in epsilon_data
            ]
        
            fig_error, ax_error = plt.subplots()
        
            ax_error.plot(
                phi_list,
                theoretical_error_rates,
                "x-",
                label="Theory",
            )
            ax_error.plot(
                phi_list,
                error_rates,
                "o",
                label="Simulation",
            )
        
            ax_error.set_xlabel(r"$\phi_{\mathrm{in}}$")
            ax_error.set_ylabel(r"$\epsilon_{\mathrm{out}}$")
            ax_error.set_title("T-type Distillation: Output Error Rate")
            ax_error.legend()
            ax_error.grid(True, alpha=0.3)
        
            figures.append(fig_error)
        
        return analysis_results, figures

if __name__ == '__main__':
    #backend_aer = AerSimulator()
    
    aer_backend = AerSimulator(
        max_parallel_threads=4,
        max_parallel_experiments=4,
        max_parallel_shots=1,
        )
    
    experiment = TTypeDistillationExperiment(
        physical_qubits=(0, 1, 2, 3, 4, 5, 6, 7, 8, ),
        backend=aer_backend,
        list_params = [i * 0.05 for i in range(16)],
    )
    
    # display(experiment.circuits()[0].draw(output="mpl", fold=-1))
    
    experiment_data = experiment.run(shots=SHOTS).block_for_results()
    experiment_data.analysis_results(dataframe=True)
