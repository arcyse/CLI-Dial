# Import all necessary objects and methods for quantum circuits:
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator
from random import randrange

# Registers for measurement bases and keys:
basesalice, keyalice = [],[]
basesbob, keybob = [],[]
baseseave, keyeave = [],[]

for i in range(64): # Charlie prepares 64 EPR pairs
    qreg = QuantumRegister(2)
    creg = ClassicalRegister(2) 
    mycircuit = QuantumCircuit(qreg, creg)

    # Creating entanglement:
    mycircuit.h(qreg[0])
    mycircuit.cx(qreg[0], qreg[1])

    # Eave intercepts qubits and chooses measurement basis:
    choiceeave=randrange(2)
    if choiceeave==0: # measurement in Z basis
        baseseave.append('Z')
    if choiceeave==1: # measurement in W basis
        mycircuit.s(qreg)
        mycircuit.h(qreg)
        mycircuit.t(qreg)
        mycircuit.h(qreg)
        baseseave.append('W')
    
    mycircuit.measure(qreg,creg) # applying final measurement
    job = AerSimulator().run(mycircuit, shots=1)
    counts = job.result().get_counts(mycircuit)

    # Saving results:
    result=list(counts.keys())[0] # retrieve key from dictionary
    keyeave.append(int(result[0])) # saving first qubit value in eave's key register 

for i in keyeave: # eave preparing fake states
    qregE = QuantumRegister(2)
    cregE = ClassicalRegister(2) 
    mycircuitE = QuantumCircuit(qregE, cregE)
    if keyeave=='1': # if eave obtained result 11 or 00, she will send corresponding states to alice and bob
        mycircuitE.x(qregE[0])
        mycircuitE.x(qregE[1])
    if keyeave=='0':
        pass # preparing state 00
       
    # Alice chooses measurement basis:
    choicealice=randrange(3)
    if choicealice==0: # measurement in Z basis
        basesalice.append('Z')
    if choicealice==1: # measurement in X basis
        mycircuitE.h(qregE[0])
        basesalice.append('X')
    if choicealice==2: # measurement in W basis
        mycircuitE.s(qregE[0])
        mycircuitE.h(qregE[0])
        mycircuitE.t(qregE[0])
        mycircuitE.h(qregE[0])
        basesalice.append('W')

    # Bob chooses measurement basis:
    choicebob=randrange(3)
    if choicebob==0: # measurement in Z basis
        basesbob.append('Z')
    if choicebob==1: # measurement in W basis
        mycircuitE.s(qregE[1])
        mycircuitE.h(qregE[1])
        mycircuitE.t(qregE[1])
        mycircuitE.h(qregE[1])
        basesbob.append('W')
    if choicebob==2: # measurement in V basis
        mycircuitE.s(qregE[1])
        mycircuitE.h(qregE[1])
        mycircuitE.tdg(qregE[1])
        mycircuitE.h(qregE[1])
        basesbob.append('V')

    mycircuitE.measure(qregE,cregE) # applying final measurement
    job = AerSimulator().run(mycircuitE, shots=1)
    countsE = job.result().get_counts(mycircuitE)
        
    # Saving results:
    resultE=list(countsE.keys())[0] # retrieve key from dictionary
    keyalice.append(int(resultE[0])) # saving first qubit value in alice's key register 
    keybob.append(int(resultE[1])) # and second to bob

# Registers:
finalKeyalice, finalKeybob = [],[] # for matching rounds
finalKeyeave=[] # for matching rounds
diffalice, diffbob = [],[] # missmatched rounds
diffBasesA, diffBasesB = [],[] # bases of missmatched rounds
# Users comparing rounds:
for i in range(0, len(basesalice)):
    if basesalice[i] == basesbob[i]: # When users used same bases
        finalKeyalice.append(keyalice[i])
        finalKeybob.append(keybob[i]) 
    else: # When used different
        diffalice.append(keyalice[i])
        diffbob.append(keybob[i])
        diffBasesA.append(basesalice[i])
        diffBasesB.append(basesbob[i])

    if (basesalice[i] == baseseave[i] and basesbob[i] == baseseave[i]):
        finalKeyeave.append(keyeave[i])

key_percent_eave = (len(finalKeyalice) - len(finalKeyeave))/len(finalKeyalice) # eave's knowledge
print(key_percent_eave)

# ZW:
sameZW = 0
diffZW = 0
for i, (bA, bB) in enumerate(zip(diffBasesA, diffBasesB)):
    if (bA == 'Z' and bB == 'W'):
        if diffalice[i]==diffbob[i]:
            sameZW=sameZW+1
        else:
            diffZW=diffZW+1

            
totalZW=sameZW+diffZW
if totalZW!=0:
    ZW=(sameZW-diffZW)/totalZW
else:
    ZW=0
    
# XW:
sameXW = 0
diffXW = 0
for i, (bA, bB) in enumerate(zip(diffBasesA, diffBasesB)):
    if (bA == 'X' and bB == 'W'):
        if diffalice[i]==diffbob[i]:
            sameXW=sameXW+1
        else:
            diffXW=diffXW+1

totalXW=sameXW+diffXW
if totalXW!=0:
    XW=(sameXW-diffXW)/totalXW
else:
    XW=0

# XV:
sameXV = 0
diffXV = 0
for i, (bA, bB) in enumerate(zip(diffBasesA, diffBasesB)):
    if (bA == 'X' and bB == 'V'):
        if diffalice[i]==diffbob[i]:
            sameXV=sameXV+1
        else:
            diffXV=diffXV+1

totalXV=sameXV+diffXV
if totalXV!=0:
    XV=(sameXV-diffXV)/totalXV
else:
    XV=0
    
# ZV:
sameZV = 0
diffZV = 0
for i, (bA, bB) in enumerate(zip(diffBasesA, diffBasesB)):
    if (bA == 'Z' and bB == 'V'):
        if diffalice[i]==diffbob[i]:
            sameZV=sameZV+1
        else:
            diffZV=diffZV+1

totalZV=sameZV+diffZV
if totalZV!=0:
    ZV=(sameZV-diffZV)/totalZV

else:
    ZV=0
    
S=ZW+XW-XV+ZV

print("CHSH inequality value is", S)
if(abs(S) >= 2):
    print('Valid quantum state! Protocol successful!')
else:
    print('Invalid quantum state! Protocol aborted!')
print(finalKeyalice)
print(finalKeybob)