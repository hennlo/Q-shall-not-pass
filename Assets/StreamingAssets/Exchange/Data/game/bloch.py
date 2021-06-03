# Importing standard Qiskit libraries and configuring account
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.visualization import *
from qiskit import *

# Set up tools for visualizing the Bloch sphere
from math import pi
def get_bloch(qc):
    
    # create a circuit that measures the qubit in the z basis
    m_z = QuantumCircuit(1,1)
    m_z.measure(0,0)

    # create a circuit that measures the qubit in the x basis
    m_x = QuantumCircuit(1,1)
    m_x.h(0)
    m_x.measure(0,0)

    # create a circuit that measures the qubit in the y basis
    m_y = QuantumCircuit(1,1)
    m_y.rx(pi/2,0)
    m_y.measure(0,0)

    shots = 2**14 # number of samples used for statistics

    bloch_vector = []
    # look at each possible measurement
    for measure_circuit in [m_x, m_y, m_z]:

        # run the circuit with a the selected measurement and get the number of samples that output each bit value
        counts = execute(qc+measure_circuit,Aer.get_backend('qasm_simulator'),shots=shots).result().get_counts()

        # calculate the probabilities for each bit value
        probs = {}
        for output in ['0','1']:
            if output in counts:
                probs[output] = counts[output]/shots
            else:
                probs[output] = 0

        # the bloch vector needs the different between these values
        bloch_vector.append( probs['0'] -  probs['1'] )
        
    return bloch_vector