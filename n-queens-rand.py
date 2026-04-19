from random import shuffle, choice, randrange
from itertools import chain

def dbg(name, val):
    print(f"{name}: {val}")
    return val

def dn_indexer(row: int, col: int, size: int) -> int:
    # queens that share a negative diagonal have the same sum
    return row + col
def dp_indexer(row: int, col: int, size: int) -> int:
    # queens that share a positive diagonal have the same difference
    # offset to give positive indices
    return row - col + size - 1

def init_queens(size: int) -> list[int]:
    """
        Initialize a random arrangement of n-queens.
    """
    queen = list(range(size))
    shuffle(queen)
    return queen

def compute_collisions(queen: list[int])-> tuple[int, list[int], list[int]]:
    """
        Initialize dn and dp, and return number of collisions.
        queen should be a list with len=size.
        returns (number of collisions, dn, dp).
    """
    size = len(queen)
    dn = [0]*(2*size-1)
    dp = [0]*(2*size-1)
    # count queens on positive diagonals 
    # using zip(range) instead of enumerate to maintain symmetry with negative diagonals
    for (row, col) in  enumerate(queen):
        dn[dn_indexer(row, col, size)] += 1
        dp[dp_indexer(row, col, size)] += 1
    # count total collisions
    collisions = 0
    for diagonal in dn + dp:
        if diagonal >= 2:
            collisions += diagonal-1
    return (collisions, dn, dp)

def compute_attacks(queen: list[int], dn: list[int], dp: list[int]) -> tuple[int, list[int]]:
    """
        Initialize attack, and return number of queens under attack.
    """
    size = len(queen)

    # get problematic negative diagonals
    ncollisions_indices = []
    for i,n in enumerate(dn):
        if n>=2:
            ncollisions_indices.append(i)
            
    # get problematic positive diagonals
    pcollisions_indices = []
    for i,n in enumerate(dp):
        if n>=2:
            pcollisions_indices.append(i)

    # check for queens on those diagonals
    attack = []
    for row,col in enumerate(queen):
        if dn_indexer(row, col, size) in ncollisions_indices:
            attack.append(row)         
        elif dp_indexer(row, col, size) in pcollisions_indices:
            attack.append(row)

    return (len(attack), attack)

def swap_ok(row1: int, row2: int, queen: list[int], dn: list[int], dp: list[int])->(bool,int):
    """
       Check if a candidate swap will reduce collisions 
    """
    #I think the way we're checking collisions here might be bugged. 
    size = len(queen)
    # Computes the number of collision of each of the four original diagonals, and adds them to the total initital collisions
    # if they include two or more queens
    initial_collisions = 0 
    if dn[dn_indexer(row1, queen[row1], size)] >= 2:
        initial_collisions += dn[dn_indexer(row1, queen[row1], size)] -1 # To just count the number of collisions, remove the queen we are considering
    if dp[dp_indexer(row1, queen[row1], size)] >= 2:
        initial_collisions += dp[dp_indexer(row1, queen[row1], size)] -1
    if (dn[dn_indexer(row2, queen[row2], size)] >= 2 
    and dn_indexer(row2, queen[row2], size) != dn_indexer(row1, queen[row1], size)): # Ensures we don't double count collisions
        initial_collisions += dn[dn_indexer(row2, queen[row2], size)] -1
    if (dp[dp_indexer(row2, queen[row2], size)] >= 2 
    and dp_indexer(row2, queen[row2], size) != dp_indexer(row1, queen[row1], size)):
        initial_collisions += dp[dp_indexer(row2, queen[row2], size)] -1

    # Computes the number of collisions on the four diagonals formed after swapping the row indices of the two queens
    swap_collisions = 0 
    # The swap is performed by moving queen (row1, col1) into (row2, col1) and queen (row2, col2) into (row1, col2)

    # Add the collisions on the diagonals of the first swapped queen
    # We don't subtract one here because dn and dp aren't updated with this hypothetical swap, so we look for the entries being greater than 1
    swap_collisions += dn[dn_indexer(row2, queen[row1], size)] 
    swap_collisions += dp[dp_indexer(row2, queen[row1], size)]
    
    if (dn_indexer(row2, queen[row1], size) == dn_indexer(row1, queen[row2], size)
    or dp_indexer(row2, queen[row1], size) == dp_indexer(row1, queen[row2], size)):
        swap_collisions += 1
    
    if dn_indexer(row1, queen[row2], size) != dn_indexer(row2, queen[row1], size): # Making sure we don't double count collisions
        swap_collisions += dn[dn_indexer(row1, queen[row2], size)]
    if dp_indexer(row1, queen[row2], size) != dp_indexer(row2, queen[row1], size): # Making sure we don't double count collisions
        swap_collisions += dp[dp_indexer(row1, queen[row2], size)]

    return (swap_collisions < initial_collisions, swap_collisions)

def perform_swap(row1: int, row2:int, queen:list[int], dn: list[int], dp:list[int], collisions: int):
    """
       Perform a swap 
    """
    size = len(queen)
    (swap_ok_bool, swap_collisions) = swap_ok(row1, row2, queen, dn, dp)
    if swap_ok_bool:
        # Swaps the positions in the array queen
        queen[row1], queen[row2] = queen[row2], queen[row1]

        # Updates collisions from the value returned from swap_ok
        collisions = swap_collisions

        # Updates dn and dp by adding one to the number of queens on the new diagonals
        # and removing one from the old diagonals
        dn[dn_indexer(row2, queen[row1], size)] += 1
        dp[dp_indexer(row2, queen[row1], size)] += 1
        dn[dn_indexer(row1, queen[row2], size)] += 1
        dp[dp_indexer(row1, queen[row2], size)] += 1
        dn[dn_indexer(row1, queen[row1], size)] -= 1
        dp[dp_indexer(row1, queen[row1], size)] -= 1
        dn[dn_indexer(row2, queen[row2], size)] -= 1
        dp[dp_indexer(row2, queen[row2], size)] -= 1

def queen_search2(queen: list[int], C1 = 0.45, C2 = 32) -> list[int]:
    """
        Search for a valid arrangement of queens.
        Algorithm based on https://doi.org/10.1109/21.135698.
        Takes a random starting arrangment of queens, returns valid solution to the n-queens problem.
    """
    size = len(queen)
    # initialization
    collisions, dn, dp = compute_collisions(queen)
    print(f"dn: {dn}")
    print(f"dp: {dp}")
    print(f"collisions: {collisions}")
    limit = C1*collisions
    number_of_attacks, attack = compute_attacks(queen, dn, dp)
    print(f"attack: {attack}")
    loopcount = 0

    for _ in range(20):
        attacked_queen = attack[1]
        
        rand_queen = randrange(size-2)
        if rand_queen >= attacked_queen:
            rand_queen += 1

        print(f"attacked: {attacked_queen}")
        print(f"rand: {rand_queen}")
        if dbg("swap_ok", swap_ok(attacked_queen, rand_queen, queen, dn, dp))[0]:
            perform_swap(attacked_queen, rand_queen, queen, dn, dp, collisions)
        print(queen)
        print(f"collisions: {collisions}")
    # Search
    #while collisions != 0:
        ##while loopcount <= C2 * size:
            #for k in range(number_of_attacks):
                ## Chooses an attacked queen and another random queen
                #attacked_queen = attack[k]
                #edited_queen = queen.copy()
                #edited_queen.pop(attacked_queen)
                #rand_queen = choice(edited_queen)
                #if swap_ok(attacked_queen, rand_queen, queen, dn, dp):
                    #perform_swap(attacked_queen, rand_queen, queen, dn, dp, collisions)
                    #if collisions == 0:
                        #return queen
                    #if collisions < limit:
                        #limit = C1 * collisions
                        #number_of_attacks, attack = compute_attacks(queen, dn, dp) # ??? Should this just reset num of attacks or the list attacks as well?
            #loopcount += number_of_attacks
    #return queen


def main():
    queen = init_queens(8)
    print(f"Initial positions (queen): {queen}")
    print(f"Ending positions: {queen_search2(queen)}")


if __name__ == "__main__":
    main()
