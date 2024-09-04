
#TODO: Add Eavesdroper simulation in another code
#TODO: Add functionality whereby connection is re-attempted if failure (due to noise or eavesdropper)
'''
IMPORTS
'''
import socket
import pickle
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, qasm3
from qiskit_aer import AerSimulator
import random
from random import randrange
import hashlib

#########################################################################################################
'''
HELPER FUNCTIONS:
'''
# Code modified to introduce noise in communication channel:
def NoisyChannel(qc1, qc2, qc1_name):
    ''' This function takes the output of a circuit qc1 (made up only of x and 
        h gates), simulate noisy quantum channel, where Pauli errors (X - bit flip; Z - phase flip
        will occur in qc2) and then initializes another circuit qc2 with introduce noise.
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
        elif instruction[0] == 'm': # exclude measuring:
            pass
        else:
            raise Exception('Unable to parse instruction')
    
    ### Introducing noise
    for instruction in qs:
        if randrange(7)<1:
            if instruction[5] == '[':
                old_qr = int(instruction[6:-1])
            else:
                old_qr = int(instruction[5:-1])
            qc2.x(qreg[old_qr]) #apply bit-flip error
        if randrange(7)<1:
            if instruction[5] == '[':
                old_qr = int(instruction[6:-1])
            else:
                old_qr = int(instruction[5:-1])
            qc2.z(qreg[old_qr]) #apply phase-flip error

def print_outcomes_in_reverse(counts): # takes a dictionary variable
    for outcome in counts: # for each key-value in dictionary
        reverse_outcome = ''
        for i in outcome: # each string can be considered as a list of characters
            reverse_outcome = i + reverse_outcome # each new symbol comes before the old symbol(s)
    return reverse_outcome

#########################################################################################################



# Client connection establishment with server:
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999)) # Or public IP address of server if connected to internet
print('Connection established!')

# After connection, client actions:
try:
    '''
    STEP 1: DISTRIBUTING QUANTUM STATES
    '''
    qreg = QuantumRegister(24) # Quantum register with 24 qubits
    creg = ClassicalRegister(24) # Classical register with 24 bits

    send=[] # Initial bit string to send
    alice_basis=[] # Register to save information about encoding basis
    bob_basis=[] # Register to save information about decoding basis

    # Alice:
    alice = QuantumCircuit(qreg, creg, name='alice')

    for i in range(24):
        bit = randrange(2)
        send.append(bit)
    for i, n in enumerate(send):
        if n==1: alice.x(qreg[i]) # apply x-gate
    for i in range(24):
        r=randrange(2) # alice randomly picks a basis
        if r==0: # if bit is 0, then she encodes in Z basis
            alice_basis.append('Z')
        else: # if bit is 1, then she encodes in X basis
            alice.h(qreg[i])
            alice_basis.append('X')
    
    print('Alice circuit created! Sending to Bob!')
    #* Send alice circuit + basis + sent key with pickle:
    serialized = pickle.dumps(alice)
    #print('Serialized circuit:', serialized)
    client.sendall(serialized)
    print('Sent to Bob!')
    client.recv(1024) #Wait for acknowledgement
    print('Acknowledgement Received from Bob!')
    serialized = pickle.dumps(alice_basis)
    client.sendall(serialized)
    print('Sent Basis to Bob!')
    client.recv(1024) #Wait for acknowledgement
    print('Acknowledgement Received from Bob!')

    #* Receive bob basis with pickle:
    # Get chunks of data until there is no data:
    bob_basis_data = b''
    while True:
        chunk = client.recv(4096) # Receive 4096-byte chunks
        if len(chunk) < 4096:
            bob_basis_data += chunk
            break # Break when reading done
        bob_basis_data += chunk # Else, append chunk to our data (byte stream)
    bob_basis = pickle.loads(bob_basis_data)
    
    print('Alice and Bob basis:', alice_basis, bob_basis)
    print('Key:', send)

    '''
    STEP 2: SIFTING:
    '''
    # Sifting:
    alice_key=[] # Alice's register for matching rounds
    for j in range(0,len(alice_basis)): # Going through list of bases 
        if alice_basis[j] == bob_basis[j]: # Comparing
            alice_key.append(send[j])
        else:
            pass # Discard round if bases mismatched

    '''
    STEP 3: COMPUTING QBER (QUANTUM BIT ERROR RATE):
    '''

    # QBER:
    rounds = len(alice_key)//3
    errors=0
    # For each and every round:
    for i in range(rounds):
        # Select random bit index at Alice end:
        bit_index = randrange(len(alice_key))
        # Send bit index with bit value to Bob:
        data_tuple = (bit_index, alice_key[bit_index])
        serialized = pickle.dumps(data_tuple)
        client.sendall(serialized)
        # Receive response from Bob with his corresponding bit value:
        response = client.recv(4096)
        bob_bit = int(response.decode('utf-8'))

        if alice_key[bit_index]!=bob_bit: # comparing tested rounds
            errors=errors+1 # calculating errors
        del alice_key[bit_index] # removing tested bits from key strings
    
    QBER=errors/rounds # calculating QBER
    QBER=round(QBER,2) # saving the answer to two decimal places

    print("QBER value =", QBER)
    print("alices secret key =", alice_key)

    '''
    STEP 4: INFORMATION RECONCILIATION:
    '''
    #NOTE: IN REAL LIFE YOU WOULD DO THIS THROUGH SOME OTHER SECURE CHANNEL:
    # Send key to Bob for reconciliation:
    serialized = pickle.dumps(alice_key)
    client.sendall(serialized)

    # Receive status of connection:
    response = client.recv(4096)
    response = response.decode('utf-8')
    #TODO: Add a simulated eavesdropper:
    if(response=='ABORT'):
        print('Eavesdropper detected! Aborting!')
        exit()
    else:
        # Receive final key form Bob:
        kFinalA = client.recv(4096)
        kFinalA = pickle.loads(kFinalA)
    print('Final key of Alice:', kFinalA)
    
    '''
    STEP 5: PRIVACY AMPLIFICATION: (THROUGH HASHING)
    '''

    # Privacy amplification:
    # Generating seed (salt):
    seed=[]
    for i in kFinalA:
        a=randrange(2)
        seed.append(a)

    # Send seed to Bob:
    serialized = pickle.dumps(seed)
    client.sendall(serialized)

    # Adding seeds to the keys:
    kFinalA.append(seed)

    # Converting lists to strings:
    strKFinalA = ''.join([str(elem) for elem in kFinalA])

    # Checking first bit to decide hash function to use:
    if kFinalA[0]==1:
        resultA=hashlib.sha256(strKFinalA.encode())
        print("alices' final key:", bin(int(resultA.hexdigest(), 16))[2:])
    else:
        resultA=hashlib.sha3_256(strKFinalA.encode())
        print("alices' final key:", bin(int(resultA.hexdigest(), 16))[2:])

finally:
    client.close()