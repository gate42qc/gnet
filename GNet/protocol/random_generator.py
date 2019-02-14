import numpy as np
import random
import secrets

class NumpyRandomGenerator:
    @classmethod
    def get_randomly_choosen_from(cls, choices, length):
        return np.random.choice(choices, length)
    
    @classmethod
    def get_random_sample(cls, array, sample_size):
        return random.sample(array, sample_size)
    
    @classmethod
    def get_random_integer(cls, low, high):
        return np.random.randint(low, high)
    
    @classmethod
    def get_random_bits(cls, length):
        return np.random.randint(2, size=length)


class SecureRandomGenerator:
    @classmethod
    def get_randomly_choosen_from(cls, choices, length):
        return [secrets.choice(choices) for i in range(length)]
    
    @classmethod
    def get_random_sample(cls, population, sample_size):
        randbelow = secrets.randbelow
        n = len(population)
        k = sample_size
        
        if not 0 <= k <= n:
            raise ValueError("Sample larger than population or is negative")
        
        result = [None] * k
        selected = set()
        selected_add = selected.add
        for i in range(k):
            j = randbelow(n)
            while j in selected:
                j = randbelow(n)
            selected_add(j)
            result[i] = population[j]
        
        return result
    
    @classmethod
    def get_random_integer(cls, low, high):
        return low + secrets.randbelow(high-low)
    
    @classmethod
    def get_random_bits(cls, length):
        return [secrets.randbits(1) for i in range(length)]