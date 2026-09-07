def fib(n):
    """
    Generate the first n Fibonacci numbers.
    
    The Fibonacci sequence starts with 0 and 1, and each subsequent number
    is the sum of the two preceding ones: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...
    
    Args:
        n (int): The number of Fibonacci numbers to generate. Must be non-negative.
    
    Returns:
        list: A list containing the first n Fibonacci numbers.
              Returns an empty list if n is 0.
    
    Raises:
        ValueError: If n is negative.
        TypeError: If n is not an integer.
    
    Examples:
        >>> fib(0)
        []
        >>> fib(1)
        [0]
        >>> fib(5)
        [0, 1, 1, 2, 3]
        >>> fib(8)
        [0, 1, 1, 2, 3, 5, 8, 13]
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n == 0:
        return []
    elif n == 1:
        return [0]
    
    # Initialize with first two Fibonacci numbers
    result = [0, 1]
    
    # Generate remaining numbers
    for i in range(2, n):
        result.append(result[i-1] + result[i-2])
    
    return result


# Example assertions to demonstrate usage
assert fib(0) == []
assert fib(1) == [0]
assert fib(8) == [0, 1, 1, 2, 3, 5, 8, 13]