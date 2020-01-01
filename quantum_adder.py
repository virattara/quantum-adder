from pyquil.quil import Program
from pyquil import api, get_qc
from pyquil.gates import *
from grove.qft.fourier import *

qc = get_qc('9q-square-qvm')

def classical_adder():
    """
    SUM GATE
    c(i)       ---x----------
                  |
    a(i)       -------x------
                  |   |
    b(i)       ---o---o------

    CARRY GATE
    c(i)       ----------x---
                         |
    a(i)       --x---x-------
                 |   |   |
    b(i)       --x---o---x---
                 |       |
    c(i+1)     --o-------o---
    """
    # qubits 0,1 represent the first number 
    a = [0,1]
    # qubits 2,3 represent the second number
    b = [2,3]
    # qubits 4,5,6 are carry qubits
    c = [4,5,6]

    p = Program()
    # a = (10) = 2
    p += X(a[1])
    # b = (11) = 3
    p += X(b[1])
    p += X(b[0])    

    for i in range(len(a)):
        ## CARRY BIT ##
        # carry bit
        # toggle carry next if both a[i] and b[i] are 1
        p += CCNOT(a[i], b[i], c[i+1])

        # add
        # toggle b[i] if a[i] is 1
        p += CNOT(a[i], b[i])

        # carry again
        # toggle carry next if c[i] and b[i] are 1
        p += CCNOT(c[i], b[i], c[i+1])

        ## SUM GATE ##
        # Get the original value of b
        p += CNOT(a[i], b[i])

        p += CNOT(c[i], b[i])

        p += CNOT(a[i], b[i])

    result = qc.run_and_measure(p, trials=1)

    print('classical adder RESULT (2+3):',result[6],result[3],result[2])


def qft_adder():
    """
    |b1>    --*----------------------------
              |
    |b2>    ---------*-----------*----------
              |      |           |
    |b3>    --------------*------------*------*
              |      |    |      |     |      |
    Q(a3)   -[R1]---[R2]---[R3]------------------
                                 |     |      |
    Q(a2)   --------------------[R1]----[R2]---
                                              |
    Q(a1)   ---------------------------------[R1]
    """
    # qubits 0,1,2 represent the first number
    a = [0,1,2]
    # qubits 3,4,5 represent the second number
    b = [3,4,5]

    p = Program()
    # a = (010) = 2
    p += X(a[1])
    # b = (011) = 3
    p += X(b[1])
    p += X(b[2])    

    p += qft(a)

    # Define a controlled rotation gate where control bit
    # is the second number (b), rotation is performed on 
    # the first number.

    # Keeping the divisor variable, thus passing it as
    # a parameter to the gate
    div = Parameter('div')

    # CROT(i) = exp(2j*pi/2**i)
    # 2**i is passed as the parameter
    CROT = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, quil_cos(2*pi/div) + 1j * quil_sin(2*pi/div)] 
    ])
    CROTdef = DefGate("CROT", CROT, [div])
    CROT = CROTdef.get_constructor()

    p += CROTdef

    # Run a for loop on both the number's qubits
    for j in range(len(a), 0, -1):
        pw = 1
        for i in range(len(b)-j, len(b)):
            div = np.power(2, pw)
            pw += 1

            p += CROT(div)(b[i], a[j-1])

    p += inverse_qft(a)
    # print(WavefunctionSimulator().wavefunction(p))

    result = qc.run_and_measure(p, trials=1)

    print('qft adder RESULT (2+3):',result[0],result[1],result[2])

if __name__ == '__main__':
    classical_adder()
    qft_adder()
