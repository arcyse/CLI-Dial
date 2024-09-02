'''
MAJOR STEPS INVOLVED IN THE BB84 QKD PROTOCOL:
1) DISTRIBUTING QUANTUM STATES
2) SIFTING
3) COMPUTING QBER
4) INFORMATION RECONCILIATION (IF NOISY CHANNEL IS USED)
5) PRIVAACY AMPLIFICATION
'''

#####################################################################################################

'''
STEP 0: DEFINING HELPER FUNCTIONS:
'''
# Import all necessary objects and methods for quantum circuits
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, qasm3
from qiskit_aer import AerSimulator
import random
from random import randrange
import hashlib

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

#####################################################################################################

'''
STEP 1: DISTRIBUTING QUANTUM STATES:
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

bob = QuantumCircuit(qreg, creg, name='bob') # Defining Bob circuit
NoisyChannel(alice, bob, 'alice') # Alice sends noisy states to bob

# Bob:
for i in range(24):
    r=randrange(2) # Bob randomly picks a basis
    if r==0: # if bit is 0, then measures in Z basis
        bob.measure(qreg[i],creg[i])
        bob_basis.append('Z')
    else: # if bit is 1, then measures in X basis
        bob.h(qreg[i])
        bob.measure(qreg[i],creg[i])
        bob_basis.append('X')

# Run the bob circuit:
job = AerSimulator().run(bob, shots=1)
counts = job.result().get_counts(bob)
counts = print_outcomes_in_reverse(counts)
received = list(map(int, counts))

#####################################################################################################

'''
STEP 2: SIFTING:
'''
# Sifting:
alice_key=[] # Alice's register for matching rounds
bob_key=[] # Bob's register for matching rounds
for j in range(0,len(alice_basis)): # Going through list of bases 
    if alice_basis[j] == bob_basis[j]: # Comparing
        alice_key.append(send[j])
        bob_key.append(received[j]) # Keeping key bit if bases matched
    else:
        pass # Discard round if bases mismatched

#####################################################################################################

'''
STEP 3: COMPUTING QBER (QUANTUM BIT ERROR RATE):
'''

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
print("alices secret key =", alice_key)
print("bob secret key =", bob_key)

#####################################################################################################

'''
STEP 4: INFORMATION RECONCILIATION:

4.1] CASCADE PROTOCOL
4.2] BICONF STRATEGY
'''

def split(list1, n): 
    out = []
    last = 0.0
    while last < len(list1):
        out.append(list1[int(last):int(last + n)])
        last += n
    return out

def cascade_pass(lA, lB, n): # input key lists A-alice, B-bob and target block size to divide in blocks
    # Shuffle:
    permutation = list(zip(lA, lB)) # map the index of multiple lists
    random.shuffle(permutation) # performing permutation
    shuffledLA, shuffledLB = zip(*permutation) # unpacking values
    # Split:
    splitLA=split(shuffledLA, n)
    splitLB=split(shuffledLB, n)
    # Calculate parity:
    # Creating empty lists, where "correctA/B" will include blocks with no error found
    # And "errorA/B" list with blocks where parities mismatched
    correctA, correctB, errorA, errorB= [], [], [], []
    sumBlocksA = [sum(block) for block in splitLA] # calculating parity by first calculating sums of each block in splitA/B
    sumBlocksB = [sum(block) for block in splitLB]
    parityA = [i %2 for i in sumBlocksA] # then applying mod(2) operator to our calculated sums and saving results
    parityB = [i %2 for i in sumBlocksB] # in parity bit list
    for i,value in enumerate(range(len(parityA))): # comparing parity bits from list1 with list2
        if parityA[i]==parityB[i]: # if parity bits matched - we add corresponding blocks to our list 'correct'
            correctA.append(splitLA[i])
            correctB.append(splitLB[i])
        else:
            errorA.append(splitLA[i]) # if parity bits mismatched - we add corresponding blocks to our list 'errors'
            errorB.append(splitLB[i])
    keyA = [item for i in correctA for item in i] # Converting our correct blocks into a list
    keyB= [item for i in correctB for item in i]
    return keyA, keyB, errorA, errorB # returning key that consist of correct blocks (list) and blocks with errors (tuple)

'''
4.1] CASCADING PROTOCOL:
'''
# Before starting error correction, we check calculated QBER value:
if QBER==0.0:
    print("QBER is 0. Cascade Protocol skipped!")
    print("Final Key alice", alice_key)
    print("Final Key bob", bob_key)
if QBER>=0.25: 
    print("QBER value is", QBER,"\nThreshold value reached! Protocol Aborted!") # If QBER is above threshold value - we abort protocol
if 0<QBER<=0.25: # if 0<QBER<=0.25 we perform Cascade protocol
    blockSize=0.73//QBER
    kFinalA, kFinalB=[], [] # creating registers for final keys
    # Cascade protocol 1st pass:
    corrBlockA, corrBlockB, errBlockA, errBlockB=cascade_pass(alice_key, bob_key, blockSize) # cascade function
    kFinalA.extend(corrBlockA) # adding block which parity bits matched to final key string
    kFinalB.extend(corrBlockB)
    
# Now aproximately know how many errors we have in initial key string,
# because after first pass each block in errorA/B list contains 1 (or other odd number) of errors
# Now can determine the final (corrected) key list length before correcting those errors (when 1 bit is left in each block)
# In other words, key length in penultimate pass of the Cascade protocol is known

    penultimatePassLength=len(alice_key)-len(errBlockA)
    while len(kFinalA)!=penultimatePassLength: # Bisective search at each block until corrected key length is not equal length of initial key minus error blocks number after first pass
        for i, (blockA, blockB) in enumerate(zip(errBlockA, errBlockB)):
            if len(blockA)>1:
                secondPassA=list(blockA) # convert block into a lists
                secondPassB=list(blockB)
                blockSize2=len(blockA)//2 # change block size, now we will divide each block that contains an error in halfs
                corrBlockA2, corrBlockB2,  errBlockA2, errBlockB2=cascade_pass(secondPassA, secondPassB, blockSize2) # and apply cascade
                kFinalA.extend(corrBlockA2) # then add correct bits to key strings
                kFinalB.extend(corrBlockB2)
                errBlockA[i]=errBlockA2[0] # updating error block values
                errBlockB[i]=errBlockB2[0]
            if len(blockA)==1: # Edge case if one block in the round will be shorter than the oner thus will require less passes
                for bit in blockA:
                    if bit==1:
                        bitA=errBlockA[0][0]
                        kFinalA.append(bitA) # alice adds corresponding bit to her key string without change
                        bitB=errBlockB[0][0]+1 # but bob will first correct the error by flipping the bit value 
                        kFinalB.append(bitB)
                    if bit==0:
                        bitA=errBlockA[0][0]
                        kFinalA.append(bitA) # alice adds corresponding bit to her key string without change
                        bitB=errBlockB[0][0]-1 # but bob will first correct the error by flipping the bit value 
                        kFinalB.append(bitB)
                        
        #print("---PERFORMING NEXT PASS---\n", "Final key alice:", kFinalA, "\n", "Final key bob", kFinalB)
        #print(" Blocks with errors alice", errBlockA, "\n", "Blocks with errors bob", errBlockB)
        
    # After previous passes result is a nested lists, to convert them:    
    errorA=[item for elem in errBlockA for item in elem]
    errorB=[item for elem in errBlockB for item in elem]
    
    # Error correction step, when our error blocks contains just 1 bit (error)
    for i, error in enumerate(zip(errorA, errorB)):
#       bitA=int(''.join(map(str, errorA))) # Converting tuple to integer
#       bitB=int(''.join(map(str, errorB)))
        bitA=int(errorA[i])
        bitB=int(errorB[i])
        if bitA==1:
            kFinalA.append(bitA)
            correctedBitB=bitB+1
            kFinalB.append(correctedBitB)
        if bitA==0:
            kFinalA.append(bitA)
            correctedBitB=bitB-1
            kFinalB.append(correctedBitB)
            
    print("Final Key alice", kFinalA)
    print("Final Key bob", kFinalB)

'''
4.2] BICONF STRATEGY:
'''

from numpy import log as ln


kFinalA=alice_key
kFinalB=bob_key

if QBER!=0: # defining size of blocks
    biconfBlockSize=(4*ln(2))//(3*QBER)
if QBER==0:
    biconfBlockSize= min(8,len(kFinalA))
# print(QBER)

rounds = 0 # counting rounds
biconfError=[] # creating register for rounds with an error
error=0 # register for found and corrected error

while rounds!=8: # we will go through rounds and monitor if blocks with errors will be found 
    rounds=rounds+1
    # Creating random subsets:
    kFinalZipped=list(zip(kFinalA, kFinalB)) # mapping indexes of our two lists
    randomBlock=random.sample(list(enumerate(kFinalZipped)), int(biconfBlockSize))
    # at this point there is nested tuple that contains (index of random bit, (bit from alice string, bit from bob string))
    #print(randomBitList) # will print out the nested tuple
    #print(randomBitList[0]) # will print out one block (index, (bitA, bitB))
    #print(randomBitList[0][0]) # will print only first pair index
    #print(randomBitList[0][1][0]) #will print only first pair alices' bit
    
    # To calculate and compare parity bits for both users bits:
    sumBlockA=0
    sumBlockB=0
    for i in range(0,int(biconfBlockSize)):
        sumBlockA=sumBlockA+randomBlock[i][1][0]
        sumBlockB=sumBlockB+randomBlock[i][1][1]
    parityA = sumBlockA%2 # then aplying mod(2) operator to the calculated sums and saving results
    parityB = sumBlockB%2
    
    if parityA!=parityB: # if parities of block dismatch - bisective search to correct error before continue with next round
        print("Error found in round:", rounds)
        print("Applying bisective search and error correction")
        # Applying bisective search to find and correct an error:
        while len(randomBlock)>1: # Take the block with error and run besective search till bit with error is found
            # Split the block:
            if len(randomBlock)%2==1: # If block size is odd
                half=len(randomBlock)//2+1 # Length of our first block should be half+1
            else:
                half=len(randomBlock)//2
            splitBlock=split(randomBlock, half) # spliting the block into two parts
            for i, block in enumerate(splitBlock): # For each part:
                sumA=0
                sumB=0
                for j in range(0,len(block)): # calculating sums 
                    sumA=sumA+splitBlock[i][j][1][0]
                    sumB=sumB+splitBlock[i][j][1][1]
                parA=sumA%2 # then calculate parities
                parB=sumB%2
                if parA==parB:
                    pass
                if parA!=parB: # if parities dismatch- update our block and run while loop again
                    randomBlock=splitBlock[i]
        if len(randomBlock)==1: #once the error to 1 bit is isolated
            error=error+1
            print("Error found in bit:", randomBlock[0][0]) #  Retrieving the index of bit pair
            errorIndex=int(randomBlock[0][0])
            # Apply error correction at bob' initial key string:
        if kFinalB[errorIndex]==0:
            kFinalB[errorIndex]=1
        else:
            kFinalB[errorIndex]=0
        print("Error corrected!\n")
    else: # If parities matched
        pass

print("BICONF strategy completed!\n", error, "errors found!")
print("Final key alice", kFinalA)
print("Final key bob", kFinalB)

#####################################################################################################

'''
STEP 5: PRIVACY AMPLIFICATION: (THROUGH HASHING)
'''

# Privacy amplification:
# Generating seed (salt):
seed=[]
for i in kFinalA:
    a=randrange(2)
    seed.append(a)

# Adding seeds to the keys:
kFinalA.append(seed)
kFinalB.append(seed)

# Converting lists to strings:
strKFinalA = ''.join([str(elem) for elem in kFinalA])
strKFinalB = ''.join([str(elem) for elem in kFinalB])

# Checking first bit to decide hash function to use:
if kFinalA[0]==1:
    resultA=hashlib.sha256(strKFinalA.encode())
    print("alices' final key:", bin(int(resultA.hexdigest(), 16))[2:])
else:
    resultA=hashlib.sha3_256(strKFinalA.encode())
    print("alices' final key:", bin(int(resultA.hexdigest(), 16))[2:])

print()
if kFinalB[0]==1:
    resultB=hashlib.sha256(strKFinalB.encode())
    print("bob' final key:", bin(int(resultB.hexdigest(), 16))[2:])
else:
    resultB=hashlib.sha3_256(strKFinalB.encode())
    print("bob' final key:", bin(int(resultB.hexdigest(), 16))[2:])