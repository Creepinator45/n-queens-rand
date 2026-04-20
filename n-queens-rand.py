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
       Returns whether the swap reduces collisions, and the difference between the intitial and swapped collisions
    """
    size = len(queen)
    # counts the number of collisions that will be removed if the chosen queens are moved
    removed_collisions = 0 
    if dn[dn_indexer(row1, queen[row1], size)] >= 2:
        removed_collisions += 1 # on a problematic diagonal, removing 1 queen will remove 1 collisions
    if dp[dp_indexer(row1, queen[row1], size)] >= 2:
        removed_collisions += 1
    if dn[dn_indexer(row2, queen[row2], size)] >= 2:
        removed_collisions += 1 
    if dp[dp_indexer(row2, queen[row2], size)] >= 2:
        removed_collisions += 1
    if dn_indexer(row1, queen[row1], size) == dn_indexer(row2, queen[row2], size) and dn[dn_indexer(row1, queen[row1], size)] == 2:
        removed_collisions -= 1 # if both queens are on the same diagonal, and are the only queens on that diagonal, the collisions are reduced by 1 not 2
    if dp_indexer(row1, queen[row1], size) == dp_indexer(row2, queen[row2], size) and dp[dp_indexer(row1, queen[row1], size)] == 2:
        removed_collisions -= 1 
    print(removed_collisions)

    # counts the number of collisions that will be added after the chosen queens are moved
    added_collisions = 0 
    # The swap is performed by moving queen (row1, col1) into (row2, col1) and queen (row2, col2) into (row1, col2)
    if dn[dn_indexer(row2, queen[row1], size)] >= 1:
        added_collisions += 1 # adding a queen to a diagonal will always add a collisions if there's already a queen on that diagonal
    if dp[dp_indexer(row2, queen[row1], size)] >= 1:
        added_collisions += 1
    if dn[dn_indexer(row1, queen[row2], size)] >= 1:
        added_collisions += 1 
    if dp[dp_indexer(row1, queen[row2], size)] >= 1:
        added_collisions += 1
    if dn_indexer(row1, queen[row2], size) == dn_indexer(row2, queen[row1], size) and dn[dn_indexer(row1, queen[row2], size)] == 0:
        added_collisions += 1 # if both queens are on the same diagonal, and that diagonal is empty, then adding them adds 1 collisions not 0
    if dp_indexer(row1, queen[row2], size) == dp_indexer(row2, queen[row1], size) and dp[dp_indexer(row1, queen[row2], size)] == 0:
        added_collisions += 1 
    print(added_collisions)
    return (added_collisions < removed_collisions, added_collisions-removed_collisions)

def perform_swap(row1: int, row2:int, queen:list[int], dn: list[int], dp:list[int], collisions: int) -> int:
    """
       Perform a swap 
       returns the new number of collisions
    """
    size = len(queen)
    (swap_ok_bool, swap_collisions) = swap_ok(row1, row2, queen, dn, dp)
    if swap_ok_bool:
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
    
        # Swaps the positions in the array queen
        queen[row1], queen[row2] = queen[row2], queen[row1]

    return collisions + swap_collisions

def queen_search2(size = int, C1 = 0.45, C2 = 32) -> list[int]:
    """
        Search for a valid arrangement of queens.
        Algorithm based on https://doi.org/10.1109/21.135698.
        Takes a random starting arrangment of queens, returns valid solution to the n-queens problem.
    """
    def fallible() -> None|list[int]:
        # initialization
        queen = init_queens(size)
        print(f"Initial positions (queen): {queen}")
        collisions, dn, dp = compute_collisions(queen)
        print(f"dn: {dn}")
        print(f"dp: {dp}")
        print(f"collisions: {collisions}")
        limit = C1*collisions
        number_of_attacks, attack = compute_attacks(queen, dn, dp)
        print(f"attack: {attack}")
        loopcount = 0
        atk_index = 0

        for _ in range(C2*size):
            if collisions <= 0:
                return queen
            attacked_queen = attack[atk_index]
            atk_index += 1
            rand_queen = randrange(size-2)
            if rand_queen >= attacked_queen:
                rand_queen += 1

            print(f"attacked: {attacked_queen}")
            print(f"rand: {rand_queen}")
            if dbg("swap_ok", swap_ok(attacked_queen, rand_queen, queen, dn, dp))[0]:
                collisions = perform_swap(attacked_queen, rand_queen, queen, dn, dp, collisions)
                if collisions < limit:
                    limit = C1 * collisions
                    number_of_attacks, attack = compute_attacks(queen, dn, dp)
                    atk_index = 0
            print(queen)
            print(f"collisions: {collisions}")
        return None
    while True:
        out = fallible()
        if out is not None:
            return out
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
    print(f"Ending positions: {queen_search2(8)}")


if __name__ == "__main__":
    main()
