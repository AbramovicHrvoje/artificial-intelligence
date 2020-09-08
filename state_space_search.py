## HRVOJE ABRAMOVIC 0036506160
## UMJETNA INTELIGENCIJA 2019/2020
## PRVA LABORATORIJSKA VJEZBA
import sys
import io
import queue
import time
import statistics
from heapq import heappush, heappop

## Solution class used for representing solutions of searching algorithms
class Solution:
    def __init__(self, states_visited, length, cost, path):
        self.states_visited = states_visited
        self.length = length
        self.cost = cost
        self.path = path

    ## Prints out solution
    def print_sol(self):
        print("States visited = " + str(self.states_visited))
        print("Fount path of length "+str(self.length), end = "")
        if self.cost != "NONE":
            print(" with total cost "+ str(self.cost),end="")
        print(":")
        for state in reversed(self.path[1:]):
            print(state + " =>")
        print(self.path[0])
        return



### LOADING FUNCTIONS ###

## Function for loading of start state, end states and graph with costs
## Input: path to file
## Output (start_state (string), end_states (list), graph (dictionary {node: [list of (neighbours,cost)]}))
def load_problem(path):

    graph = {}
    
    with io.open(path, mode= "r", encoding = "utf-8") as graph_file:
        graph_all_lines = graph_file.readlines()

    got_start = False
    got_end = False
    
    for graph_line in graph_all_lines:
        if graph_line[0] == "#":
            continue

        if not got_start:
            start_state = graph_line.strip()
            got_start = True
            continue

        if not got_end:
            end_states = graph_line.split()
            got_end = True
            continue
        
        succ = []

        graph_line_split = graph_line.split()
        state = graph_line_split[0][:-1]

        for succ_string in graph_line_split[1:]:
            (n_node, cost) = succ_string.split(",")   
            succ.append((n_node, float(cost)))

        graph.update({state: succ})

    
    return (start_state, end_states, graph)

## Function for loading heuristic
## Input: path to heuristic file
## Output heurisitc (dictionary {state : value})
def load_heuristic(path):
    heuristic = {}
    
    with io.open(path, mode= "r", encoding = "utf-8") as h_file:
        h_all_lines = h_file.readlines()

    for h_line in h_all_lines:
        if h_line[0] == "#":
            continue
        
        h_line_split = h_line.split(':')
        heuristic.update({h_line_split[0] : float(h_line_split[1].strip())})
    
    return heuristic

#########################


### SOLVING FUNCTIONS ###

##  Function for BFS
##  Input: start_state, graph, end_states
##  Output: Solution type object if solution was found, None otherwise
def solve_bfs(start_state, graph, end_states):

    print("Running bfs:")
    
    sol = Solution(0,0,"NONE", [])

    visited = {} ## visited oblika (cvor :  parent)
    open_nodes = queue.Queue()

    open_nodes.put((start_state,""))

    while not open_nodes.empty():

        (current, parent) = open_nodes.get()

        if current in visited:
            continue

        visited.update({current:parent})

        sol.states_visited +=1
    
        if current in end_states:
            
            path = [current]
            path_next = visited[current]
            sol.length+=1
            
            while path_next != "":
                path.append(path_next)
                path_next = visited[path_next]
                sol.length+=1
                
            sol.path = path
            return sol

        for succ_node in graph[current]:
            open_nodes.put((succ_node[0], current))
        
    
    return None

##  Function for USC
##  Input: start_state, graph, end_states
##  Output: Solution type object if solution was found, None otherwise
def solve_uniform_cost(start_state, graph, end_states):

    print("Running ucs:")
    
    sol = Solution(0,0,0,[])

    visited = {} ## visited oblika (cvor : parent)
    open_nodes = []
    
    heappush(open_nodes, (0, start_state, ""))

    while open_nodes:

        (cost, current, parent) = heappop(open_nodes)

        if current in visited:
            continue


        visited.update({current:parent})

        sol.states_visited +=1
    
        if current in end_states:

            sol.length+=1
            sol.cost = cost
            
            path = [current]
            path_next = visited[current]

            while path_next != "":
                path.append(path_next)
                path_next = visited[path_next]
                sol.length+=1
                
            sol.path = path
            return sol

        for succ_node in graph[current]:
            heappush(open_nodes,(succ_node[1]+cost, succ_node[0], current))
        
    
    return None


##  Function for A*
##  Input: start_state, graph, end_states, heuristic
##  Output: Solution type object if solution was found, None otherwise
def solve_a_star(start_state, graph, end_states, heuristic):

    print("Running a*:")

    sol = Solution(0,0,0,[])

    visited = {} ## visited oblika (cvor : (g, parent))
    open_nodes = [] ## priority queue oblika (f, node, parent)
    
    heappush(open_nodes, (heuristic[start_state], start_state, ""))

    while open_nodes:

        (f, current, parent) = heappop(open_nodes)

        if current in visited:
            continue

        h = heuristic[current]
        g = f - h
        visited.update({current:(g, parent)})

        sol.states_visited +=1
    
        if current in end_states:

            sol.length+=1
            sol.cost = g
            
            path = [current]
            path_next = visited[current][1]

            while path_next != "":
                path.append(path_next)
                path_next = visited[path_next][1]
                sol.length+=1
                
            sol.path = path
            return sol

        for succ_node in graph[current]:
            succ_state = succ_node[0]
            succ_node_g = g + succ_node[1]

##      DIO S PONOVNIM PROVJERAVANJEM CLOSED CVOROVA   
##            for open_test in open_nodes:
##                if open_test[1] != succ_state:
##                    continue
##                h_test = heuristic[open_test[1]]
##                g_test = open_test[0] - h_test
##                if g_test <= succ_node_g:
##                    continue
##                else:
##                    open_nodes.remove(open_test)
##                    break
##           
##            if succ_state in visited:
##                (g_test, parent_test) = visited[succ_state]
##                if g_test <= succ_node_g:
##                    continue
##                else:
##                    del visited[succ_state]

            succ_node_f = succ_node_g + heuristic[succ_state]  
            heappush(open_nodes,(succ_node_f, succ_state, current))
        
    
    return None

#########################


### HEURISTIC CHECK FUNCTIONS ###

##  Function for graph transposing (inverts edges)
##  Input: graph
##  Output: transposed graph dictionary {node : [list of (neighbours,cost)]}
def invert_edges(graph):
    graph_transpose = {}


    for state in graph:
        graph_transpose.update({state:[]})

    for state in graph:
        for neighbour in graph[state]:
            graph_transpose[neighbour[0]].append((state,neighbour[1]))



    return graph_transpose

##  Function for getting oracle heuristic
##  Input: already transposed graph, end states
##  Output: oracle heuristic dictionary {state : value}
def get_oracle_heuristic(graph_t, end_states):
    
    oracle = {} ## distances {node:dist}
    opened = [] ### priority queue onih koji se trebaju jos obraditi (dist, node)

    for end_s in end_states:
        oracle.update({end_s:0})
        heappush(opened,(0,end_s))

    while opened:

        (minDist, curr_node) = heappop(opened)

        for neighbour in graph_t[curr_node]:
            (n_node, cost) = neighbour
            if n_node not in oracle or oracle[n_node] > oracle[curr_node] + cost:
                oracle.update({n_node: oracle[curr_node]+cost})
                heappush(opened, (oracle[curr_node]+cost,n_node))
            
    return oracle

## Function for checking if heruistic is optimistic
## Input: heuristic that we want to check, oracle heuristic
## Output: True/False
def check_optimistic(heuristic, oracle_heuristic):
    print("Checking if heuristic is optimistic:")
    errors = 0
    for h in oracle_heuristic:
        if heuristic[h] > oracle_heuristic[h]:
            print("  [ERR] h({0}) > h*: {1} > {2}".format(h, heuristic[h], oracle_heuristic[h]))
            errors += 1


    if (errors == 0):
        print("Heuristic is optimistic")
    else:
        print("Heuristic is not optimistic, there are {0} errors". format(errors))
    
    return (errors == 0)

## Function for checking if heruistic is consistent
## Input: graph, heuristic that we want to check
## Output: True/False
def check_consistency(graph, heuristic):

    print("Checking if heuristic is consistent:")
    errors = 0
    
    for node in  graph:
        curr_h = heuristic[node]
        for succ in graph[node]:
            (succ_node,cost) = succ
            succ_h = heuristic[succ_node]

            if curr_h > succ_h + cost:
                errors += 1
                print("  [ERR] h({0}) > h({1}) + cost: {2} > {3} + {4}".format(node, succ_node, curr_h, succ_h, cost))

    if (errors == 0):
        print("Heuristic is consistent")
    else:
        print("Heuristic is not consistent, there are {0} errors".format(errors))
    
    return (errors == 0)

##########################

## OLD (SLOW) ORACLE HEURISTIC FUNCTION
def get_oracle_old(graph_t, end_states):
    
    oracle = {} ## distances {node:dist}
    visited = {} #### {node: True}
    for end_s in end_states:
        oracle.update({end_s:0})

    while True:
        minDist = 10000000
        curr_node = None
        for node in oracle:
            if node in visited:
                continue

            if oracle[node] < minDist:
                minDist = oracle[node]
                curr_node = node
        
        if curr_node == None:
            break

        visited.update({curr_node : True})
        for neighbour in graph_t[curr_node]:
            (n_node, cost) = neighbour
            if n_node not in oracle or oracle[n_node] > oracle[curr_node] + cost:
                oracle.update({n_node: oracle[curr_node]+cost})
            
    return oracle

##


## TIME CHECK FOR BONUS POINTS ##

## Checks wall clock time for checking if heuristic is optimistic and/or consistent
def check_time(graph, heuristic, end_states):

    N = 10
    times_opt = []
    times_cons = []

    for i in range(N):
        t_start = time.time()
        graph_transpose = invert_edges(graph)
        oracle_heuristic = get_oracle_heuristic(graph_transpose, end_states)
        check_optimistic(heuristic, oracle_heuristic)
        times_opt.append(time.time()-t_start)

    opt_avg = sum(times_opt)/N
    opt_std_dev = statistics.stdev(times_opt)
    print("Is heuristic optimistic check runs in: {0} +/- {1} seconds average on {2} measures.".format(opt_avg, opt_std_dev,N))

    for i in range(N):
        t_start = time.time()
        check_consistency(graph, heuristic)
        times_cons.append(time.time()-t_start)

    cons_avg = sum(times_cons)/N
    cons_std_dev = statistics.stdev(times_cons)
    
    print("Consistency check runs in: {0} +/- {1} seconds average on {2} measures.".format(cons_avg, cons_std_dev,N))
    
    return


### MAIN FUNCTION ###

def main():

    locations = sys.stdin.readlines()
    ## 2 lines expected - 1st line: path to graph text file, 2nd line path to heuristic text file

    (start_state, end_states, graph) = load_problem(locations[0].strip())
    heuristic = load_heuristic(locations[1].strip())

    print("Start state: "+start_state)
    print("End state(s): "+str(end_states))
    print("State space size: "+str(len(graph)))
    print("")

    bfs_sol = solve_bfs(start_state, graph, end_states)
    if bfs_sol is None:
        print("BFS failed")
    else:
        bfs_sol.print_sol()
    print("")

    ucs_sol = solve_uniform_cost(start_state, graph, end_states)
    if ucs_sol is None:
        print("Uniform-cost failed")
    else:
        ucs_sol.print_sol()
    print("")

    a_star_sol = solve_a_star(start_state, graph, end_states, heuristic)
    if a_star_sol is None:
        print("A* failed")
    else:
        a_star_sol.print_sol()
    print("")


    
    graph_transpose = invert_edges(graph)

    
    print("Getting oracle heuristic")
    ## old (slow) solution:
    #oracle_heuristic = get_oracle_old(graph_transpose, end_states)
    oracle_heuristic = get_oracle_heuristic(graph_transpose, end_states)

    check_optimistic(heuristic, oracle_heuristic)

    check_consistency(graph, heuristic)

    #check_time(graph, heuristic, end_states)
        
    return

main()

## SLOZENOST PROVJERE OPTIMISTICNOSTI : O(E+V*log(V)+V) gdje je V broj cvorova grafa, a E broj bridova grafa
## SLOZENOST PROVJERE KONZISTENTNOSTI: O(E) gdje je E broj bridova grafa

## provjere vezane uz heuristiku 3x3 slagalice se izvode odmah
## tijek optimiziranja  je opisan u dodatni_2.pdf fileu
## stara impplementacija - get_oracle_old
## brza implementacija - get_oracle_heuristic
