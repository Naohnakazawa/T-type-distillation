# T-type-distillation
an example code of T-type-distillation

## Overview

This repository provides an example implementation of T-type
distillation.

## Method

Software

This project is using Qiskit, including Qiskit Aer and Qiskit IBM Runtime.

References

This code implements an example of the T-type distillation protocol
described in:

S. Bravyi and A. Kitaev,
"Universal quantum computation with ideal Clifford gates and noisy ancillas,"
Physical Review A 71, 022316 (2005).

DOI: 10.1103/PhysRevA.71.022316

License

This project is licensed under the Apache License 2.0.


## Requirements

- Python 3.x
- qiskit
- qiskit-aer
- qiskit-ibm-runtime
- numpy

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/T-type-distillation.git
cd T-type-distillation
pip install -r requirements.txt
```

```zsh
git clone https://github.com/YOUR_USERNAME/T-type-distillation.git
cd ~/path/to/T-type-distillation
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

(.venv) myMac:T-type-distillation username$

deactivate
```

## Execution

This repository supports two execution modes.

1. Local simulation

The circuits can be executed locally using Qiskit Aer:

backend = AerSimulator()


This mode does not require an IBM Quantum account or access to quantum hardware.

2. IBM Quantum hardware

The circuits can also be executed on real IBM Quantum hardware using
Qiskit IBM Runtime.

The implementation uses job-mode execution and does not require Runtime
sessions. Therefore, it is intended to be usable with the IBM Quantum
Open Plan, subject to the availability and usage limits of the user's
IBM Quantum account.

Users must provide their own IBM Quantum credentials. No API key or
other credentials are included in this repository.

