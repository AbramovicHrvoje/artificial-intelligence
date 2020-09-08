import sys

## Function for atom negation
## Input: string
## Output: negated atom string
def neg(atom):
    if atom[0] == '~':
        return atom[1:]
    else:
        return '~'+atom

## Function that turns string type clause into set type clause
## Input: string clause
## Output: set clause
def parseClause(clause):
    clauseSet = set()
    clause = clause.lower()
    for c in clause.split(' v '):
        clauseSet.add(c.strip().lower())
    return clauseSet

## Function that turns set type clause into string type clause
## Input: set clause
## Output: string clause
def clauseToStr(clause):
    if clause == "NIL":
        return clause
    
    clauseStr = ""
    for c in clause:
        clauseStr+=(c+" v ")
    return clauseStr[:-3]

## Function for negating a clause written in CNF
## Input: string clause
## Output: array of sets
def parseAndNegate(clause):
    newClauses = []
    for c in clause.split(' v '):
        newClauses.append({neg(c.strip().lower())})
    return newClauses
        
## Check if clause is tautology
## input set clause
## output True/False
def tautology(clause):
    for atom in clause:
        if neg(atom) in clause:
            return True
    return False

## Function that resolves 2 clauses
## Input: 2 set type clauses
## Output: None - clauses cannot be resolved, empty set - result is NIL, set - resolvent clause
def resolve(clause1, clause2):
    
    for atom1 in clause1:
        if neg(atom1) in clause2:
            newClause = clause1.union(clause2)
            newClause.remove(atom1)
            newClause.remove(neg(atom1))
            if not tautology(newClause):
                return newClause
            else:
                break
            
    return None
## Function used for printing proof
## Input: knowledge array of sets, premNum - number of premises, goalNum - number of goalClauses, paths - array of parents for each clause
## Output: nothing
def reconstructAndPrint(knowledge, premNum, goalNum, paths):

    korisni = [False for i in knowledge]

    for i in range(premNum, premNum+goalNum):
        korisni[i] = True

    korisni[-1] = True

    bfs = [paths[-1]]
    
    while bfs:
        now = bfs.pop(0)
        korisni[now[0]] = True
        korisni[now[1]] = True
        if paths[now[0]] != "PREMISE" and paths[now[0]] != "GOAL":
            bfs.append(paths[now[0]])
        if paths[now[1]] != "PREMISE" and paths[now[1]] != "GOAL":
            bfs.append(paths[now[1]])

    skipper = 0
    skipped = []
    for i in  range(len(knowledge)):
        skipped.append(skipper)
        if not korisni[i]:
            skipper+=1

    transition1 = True
    transition2 = True
    I = 0
    
    for i in range(len(knowledge)):
        if not korisni[i]:
            continue

        if paths[i] == "GOAL" and transition1:
            print("============")
            transition1 = False
        elif paths[i] != "GOAL" and paths[i] != "PREMISE" and transition2:
            print("============")
            transition2 = False

        I+=1
        print(str(I)+". " + clauseToStr(knowledge[i]), end = '')
        if paths[i] == "GOAL" or paths[i] == "PREMISE":
            print()
            continue

        print(" ("+ str(paths[i][0]-skipped[paths[i][0]]+1) + "," + str(paths[i][1]-skipped[paths[i][1]]+1)+ ")")
    

    #print(str(I)+". "+"NIL" + " (" +str(paths[-1][0]-skipped[paths[-1][0]]+1)+ "," + str(paths[-1][1]-skipped[paths[-1][1]]+1)+ ")")
    print("============")
    return

## Function for deduction. Chekcs if toProve clause is true or unknown given premises
## Input: premises - array of sets, toProve - goal clause, verbose - True/False
## Output: nothing
def evaluate(premises, toProve, verbose):
    
    knowledge = premises.copy()
    startClauses = len(knowledge)
    paths = ["PREMISE" for i in knowledge]

    toProve = toProve.strip().lower()
    goalNegated = parseAndNegate(toProve)
    goalNum = len(goalNegated)
    
    knowledge+=goalNegated

    for g in goalNegated:
        paths.append("GOAL")
    
    i = startClauses
    
    ignore = [False for i in knowledge]
    

    while i < len(knowledge):
        j = -1
        
        while j < i:
            j+=1

            if ignore[j]:
                continue
            
            resolvent = resolve(knowledge[i], knowledge[j])

            ## nema novih znanja
            if resolvent is None:
                continue

            ## nasao NIL - super
            if not resolvent:
                if verbose:
                    knowledge.append("NIL")
                    paths.append((j,i))
                    reconstructAndPrint(knowledge, startClauses, goalNum, paths)
                print(toProve + " is true")
                if verbose:
                    print()
                return

            ## ako je tautologija - odbaci
            if tautology(resolvent):
                continue

            ## provjera podskupova
            add = True
            nextOne = False
            
            for k in range(len(knowledge)):
                if knowledge[k].issubset(resolvent):
                    add = False
                    break

                elif resolvent.issubset(knowledge[k]):
                    ignore[k] = True
                    if k == i:
                        nextOne = True

            ## ako je on nadskup nekog od prije nemoj dodat        
            if not add:
                continue

            ## dodaj novog u bazu znanja
            knowledge.append(resolvent)
            paths.append((j, i))
            ignore.append(False)

            ## ako si pobrisao onog s kojim upravo gledas, idi na sljedeceg
            if nextOne:
                break
            
        i+=1
    print(toProve + " is unknown")
    return

## Function for normal resolution
def normalResolution(premisesPath, verbose):
    # otvori file
    # napravi sve normalno
    # verbose je T ili F
    knowledge = []
    
    with open(premisesPath, 'r', encoding = 'utf-8') as premisesFile:
        premises = premisesFile.readlines()

    for clause in premises:
        if clause[0] == '#':
            continue
        clause = clause.strip()
        knowledge.append(parseClause(clause))
    
    knowledge = knowledge[:-1]

    i = len(premises)-1
    while( premises[i][0] == '#'):
        i-=1
        
    evaluate(knowledge, premises[i].strip(), verbose)
    #print(knowledge)
    
    return

## Function for query test
def queryTest(premisesPath, queryPath, verbose):

    knowledge = []

    with open(premisesPath, 'r', encoding = 'utf-8') as premisesFile:
        premises = premisesFile.readlines()

    for clause in premises:
        if clause[0] == '#':
            continue
        clause = clause.strip()
        knowledge.append(parseClause(clause))

    with open(queryPath, 'r', encoding = 'utf-8') as queryFile:
        insLines = queryFile.readlines()

    for ins in insLines:
        if ins[0] == '#':
            continue

        ins = ins.strip()

        if ins[-1] == '?':
            toProve = ins[:-2].strip()
            evaluate(knowledge, toProve, verbose)

        elif ins[-1] == '-':
            knowledge.remove(parseClause(ins[:-2].strip()))
            
        elif ins[-1] == '+':
            knowledge.append(parseClause(ins[:-2].strip()))
    
        #print(knowledge)
    return


## Function for interactive query type program
def queryInt(premisesPath, verbose):
    knowledge = []

    with open(premisesPath, 'r', encoding = 'utf-8') as premisesFile:
        premises = premisesFile.readlines()

    if verbose:
        print("Knowledge system constructed with: ")

    for clause in premises:
        if clause[0] == '#':
            continue
        clause = clause.strip()
        knowledge.append(parseClause(clause))
        if verbose:
            print(clauseToStr(knowledge[-1]))

    if verbose:
        print("\nEnter your query:")

    query = input(">>> ")
    while query != 'exit':
        
        if query[-1] == '?':
            toProve = query[:-2].strip()
            evaluate(knowledge, toProve, verbose)

        elif query[-1] == '-':
            knowledge.remove(parseClause(query[:-2].strip()))
            if verbose:
                print(query[:-2] + " removed")
            
        elif query[-1] == '+':
            knowledge.append(parseClause(query[:-2].strip()))
            if verbose:
                print(query[:-2] + " added")
                
        query = input(">>> ")
    
    return

def smartResTest():
    

## Main function
def main():
    parameters = sys.argv
    mode = parameters[1]
    premisesPath = parameters[2]
    verbose = False
    
    if parameters[-1] == 'verbose':
        verbose = True
        
    if mode == 'resolution':
        normalResolution(premisesPath, verbose)
    elif mode == 'cooking_test':
        queryPath = parameters[3]
        queryTest(premisesPath, queryPath, verbose)
    elif mode == 'cooking_interactive':
        queryInt(premisesPath, verbose)
    
    return

main()
