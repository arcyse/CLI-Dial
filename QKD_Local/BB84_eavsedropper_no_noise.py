# Import all necessary objects and methods for quantum circuits:
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, qasm3
from qiskit_aer import AerSimulator
from random import randrange

def SendState(qc1, qc2, qc1_name):
    ''' This function takes the output of a circuit qc1 (made up only of x and 
        h gates) and initializes another circuit qc2 with the same state
    ''' 
    
    # Quantum state is retrieved from qasm code of qc1:
    qs = qasm3.dumps(qc1).split(sep=';')[4:-1]

    # Process the code to get the instructions:
    for index, instruction in enumerate(qs):
        qs[index] = instruction.lstrip()

    # Parse the instructions and apply to new circuit:
    for instruction in qs:
        if instruction[0] == 'x':
            if instruction[5] == '[':
                old_qr = int(instruction[6:-1])
            else:
                old_qr = int(instruction[5:-1])
            qc2.x(qreg[old_qr])
        elif instruction[0] == 'h':
            if instruction[5] == '[':
                old_qr = int(instruction[6:-1])
            else:
                old_qr = int(instruction[5:-1])
            qc2.h(qreg[old_qr])
        elif instruction[0] == 'm': # exclude measuring
            pass
        else:
            raise Exception('Unable to parse instruction')

def print_outcomes_in_reverse(counts): # takes a dictionary variable
    for outcome in counts: # for each key-value in dictionary
        reverse_outcome = ''
        for i in outcome: # each string can be considered as a list of characters
            reverse_outcome = i + reverse_outcome # each new symbol comes before the old symbol(s)
    return reverse_outcome

def split_list(bit_string, parts=1):
    length = len(bit_string)
    return [ bit_string[i*length // parts: (i+1)*length // parts] 
             for i in range(parts) ]

#############################################################################
qreg = QuantumRegister(24)
creg = ClassicalRegister(24) 
alice = QuantumCircuit(qreg, creg, name='alice')

send=[] # Initial bit string ot send
alice_basis=[]
bob_basis=[] 
eave_basis=[]

# Creating random bit string:
for i in range(24):
    bit = randrange(2)
    send.append(bit)
    
# Alice preparing qubits:
for i, n in enumerate(send):
    if n==1:
        alice.x(qreg[i]) # apply x-gate

#alice encoding
for i in range(24):
    r=randrange(2) 
    if r==0: # if bit is 0, then she encodes in Z basis
        alice_basis.append('Z')
    else: # if bit is 1, then she encodes in X basis
        alice.h(qreg[i])
        alice_basis.append('X')

eave = QuantumCircuit(qreg, creg, name='eave') # Defining eave circuit
SendState(alice, eave, 'alice') # alice sends states to eave

# Eave intercepts and measures qubits:
for i in range(24):
    r=randrange(2) # Randomly pick a basis
    if r==0: # if bit is 0, then measures in Z basis
        eave.measure(qreg[i],creg[i])
        eave_basis.append('Z')
    else: # if bit is 1, then measures in X basis
        eave.h(qreg[i])
        eave.measure(qreg[i],creg[i])
        eave_basis.append('X')

job = AerSimulator().run(eave, shots=1) # eave has only has one shot to measure qubits
counts = job.result().get_counts(eave) # counts is a dictionary object in python
counts = print_outcomes_in_reverse(counts)

eave_received = list(map(int, counts)) # Saving eave received string as a list

# eave preparing fake states
eave_fake = QuantumCircuit(qreg, creg, name='eave_fake')
for i, n in enumerate(eave_received): # if measured bit is 1 - apply X gate
    if n==1:
        eave_fake.x(qreg[i]) # apply x-gate

for i, n in enumerate(eave_basis):
    if i == 'X': # if eave used X basis to measure qubit, she applies H gate for same round
        eave_fake.h(qreg[i])
    else:
        pass

bob = QuantumCircuit(qreg, creg, name='bob') # Defining bob circuit
SendState(eave_fake, bob, 'eave') # eave sends states to bob

# Bob receives qubits:
for i in range(24):
    r=randrange(2) # Randomly pick a basis
    if r==0: # if bit is 0, then measures in Z basis
        bob.measure(qreg[i],creg[i])
        bob_basis.append('Z')
    else: # if bit is 1, then measures in X basis
        bob.h(qreg[i])
        bob.measure(qreg[i],creg[i])
        bob_basis.append('X')

job_b = AerSimulator().run(bob,shots=1) # bob has only has one shot to measure qubits
counts_b = job_b.result().get_counts(bob) # counts is a dictionary object in python
counts_b = print_outcomes_in_reverse(counts_b)

received = list(map(int, counts_b)) # Saving bob received string as a list

########################################################################################

# Sifting:
alice_key=[] # alices register for matching rounds
bob_key=[] # bob register for matching rounds
for j in range(0,len(alice_basis)): # Going through list of bases 
    if alice_basis[j] == bob_basis[j]: # Comparing
        alice_key.append(send[j])
        bob_key.append(received[j]) # Keeping key bit if bases matched
    else:
        pass # Discard round if bases mismatched

########################################################################################

# QBER:
rounds = len(alice_key)//3
errors=0
for i in range(rounds):
    bit_index = randrange(len(alice_key)) 
    tested_bit = alice_key[bit_index]
    if alice_key[bit_index]!=bob_key[bit_index]: # comparing tested rounds
        errors=errors+1 # calculating errors
    del alice_key[bit_index] # removing tested bits from key strings
    del bob_key[bit_index]
QBER=errors/rounds # calculating QBER
QBER=round(QBER,2) # saving the answer to two decimal places

print("QBER value =", QBER)
print("alice's secret key =", alice_key)
print("bob' secret key =", bob_key)

if(QBER>0):
    print('Eavsedropper detected! Protocol aborted!')
else:
    print('Good to go!')

#########################################################################################