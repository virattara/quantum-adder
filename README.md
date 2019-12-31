    # qubits 0,1,2 represent the first number in this case no. is 2
    a = [0,1,2]
    # qubits 3,4,5 represent the second number in this case no. is 3
    b = [3,4,5]

    p = Program()
    # a = (010) = 2
    p += X(a[1])
    # b = (011) = 3
    p += X(b[1])
    p += X(b[2])    

    p += qft(a)

    # Define a controlled rotation gate where control bit
    # is the second number, rotation is performed on the first number.
    div = Parameter('div')

    CROT = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, quil_cos(2*pi/div) + 1j * quil_sin(2*pi/div)] 
    ])
    CROTdef = DefGate("CROT", CROT, [div])
    CROT = CROTdef.get_constructor()

    p += CROTdef

    # Run a for loop on 2nd number qubits.
    # (both number should have the same number of qubits)
    for j in range(len(a), 0, -1):
        pwi = 1
        for i in range(len(b)-j, len(b)):
            div = np.power(2, pwi)
            pwi += 1

            p += CROT(div)(b[i], a[j-1])

    p += inverse_qft(a)
    print(WavefunctionSimulator().wavefunction(p))

    qc = get_qc('9q-square-qvm')
    result = qc.run_and_measure(p, trials=1)

    print(result)
