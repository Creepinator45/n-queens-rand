from random import shuffle, choice
from itertools import chain

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
    for (row_index, col_index) in  enumerate(queen):
        # queens that share a negative diagonal have the same sum
        sum = row_index + col_index
        dn[sum] += 1
        # queens that share a positive diagonal have the same difference
        # offset to give positive indices
        offset_dif = row_index-col_index + size-1
        dp[offset_dif] += 1
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
            pcollisions_indices.append(i-(size-1))

    # check for queens on those diagonals
    attack = []
    for row,col in enumerate(queen):
        if row+col in ncollisions_indices:
            attack.append(row)         
        elif row-col in pcollisions_indices:
            attack.append(row)

    return (len(attack), attack)

def swap_ok(row1: int, row2: int, queen: list[int], dn: list[int], dp: list[int])->bool:
    """
       Check if a candidate swap will reduce collisions 
    """
    
    # Computes the number of collision of each of the four original diagonals, and adds them to the total initital collisions
    # if they include two or more queens
    initial_collisions = 0 
    if dn[row1 + queen[row1]] >= 2:
        initial_collisions += dn[row1 + queen[row1]] -1 # To just count the number of collisions, remove the queen we are considering
    if dp[row1 - queen[row1] + len(queen) - 1] >= 2:
        initial_collisions += dp[row1 - queen[row1] + len(queen) - 1] - 1
    if (dn[row2 + queen[row2]] >= 2 
    and dn[row2 + queen[row2]] != dn[row1 + queen[row1]]): # Ensures we don't double count collisions
        initial_collisions += dn[row2 + queen[row2]] -1
    if (dp[row2 - queen[row2] + len(queen) - 1] >= 2 
    and dp[row2 - queen[row2] + len(queen) - 1] != dp[row1 - queen[row1] + len(queen) - 1]):
        initial_collisions += dp[row2 - queen[row2] + len(queen) - 1] -1
    print(f"Initial collisisons: {initial_collisions}")

    # Computes the number of collisions on the four diagonals formed after swapping the row indices of the two queens
    swap_collisions = 0 
    
    # The swap is performed by moving queen (row1, col1) into (row2, col2) and queen (row2, col2) into (row1, col2)

    # Add the collisions on the diagonals of the first swapped queen
    # We don't subtract one here because dn and dp aren't updated with this hypothetical swap, so we look for the entries being greater than 1
    swap_collisions += dn[row2 + queen[row1]] 
    swap_collisions += dn[row2 - queen[row1] + len(queen) - 1]
    print(f"first additions, swap collisions {swap_collisions}")
    # Now updates this sum based on the pre-swapped queens who are still in dp and dn and the other swapped queen
    # First, removes a collision if it is on the same diagonal as a pre-swapped queen as that piece isn't there any more
    if (row2 + queen[row1] == row1 + queen[row1]
    or row2 - queen[row1] + len(queen) - 1  == row1 - queen[row1] + len(queen) - 1): 
        swap_collisions -= 1
    if (row2 + queen[row1] == row2 + queen[row2]
    or row2 - queen[row1] + len(queen) - 1  == row2 - queen[row2] + len(queen) - 1):
        swap_collisions -= 1
    print(f"first round of removal, swap collisions {swap_collisions}")
    if (row2 + queen[row1] == row1 + queen[row2] 
    or row2 - queen[row1] + len(queen) - 1 == row1 - queen[row2] + len(queen) - 1): # Because these new swapped queens aren't in dn and dp we need to manually check if they form a collision
        swap_collisions += 1
        print(f"checking new queens, swap collisions {swap_collisions}")
    print(f"swap collisions for first queen {swap_collisions}")

    if row1 + queen[row2] != row2 + queen[row1]: # Making sure we don't double count collisions
        swap_collisions += dn[row1 + queen[row2]] 
        print(f"not on same diagonal, add all, swap collisions {swap_collisions}")
        if row1 + queen[row2] == row1 + queen[row1]:
            swap_collisions -= 1
        if row1 + queen[row2] == row2 + queen[row2]:
            swap_collisions -= 1
        print(f"remove, swap collisions {swap_collisions}")
    if row1 - queen[row2] + len(queen) - 1 != row2 - queen[row1] + len(queen) - 1:
        swap_collisions += dn[row1 - queen[row2] + len(queen) - 1] 
        print(f"not on same diagonal, add all, swap collisions {swap_collisions}")
        if row1 - queen[row2] + len(queen) - 1 == row1 - queen[row1] + len(queen) - 1: 
            swap_collisions -= 1
        if row1 - queen[row2] + len(queen) - 1 == row2 - queen[row2] + len(queen) - 1:
            swap_collisions -= 1
        print(f"remove, swap collisions {swap_collisions}")
    print(f"Swap collisions: {swap_collisions}")

    print(f"swap_ok returns: {swap_collisions < initial_collisions}")
    return swap_collisions < initial_collisions

def perform_swap(row1: int, row2:int, queen:list[int], dn: list[int], dp:list[int], collisions: list[int]):
    """
       Perform a swap 
    """
    pass

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
    number_of_attacks, attacks = compute_attacks(queen, dn, dp)
    print(f"attacks:{attacks}")

    rand_queen = choice(queen)
    rand_queen_2 = choice(queen)
    print(f"Consider first attacked queen {attacks[0]} and a random queen {rand_queen}")
    print(f"random queen: {rand_queen}")
    swap_ok(attacks[0],rand_queen,queen,dn, dp)
    print(f"Consider second attacked queen {attacks[1]} and a random queen {rand_queen_2}")
    print(f"another random queen: {rand_queen_2}")
    swap_ok(attacks[1],rand_queen_2,queen,dn, dp)

def main():
    queen = init_queens(8)
    print(queen)
    queen_search2(queen)


if __name__ == "__main__":
    main()
