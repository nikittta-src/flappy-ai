from typing import List
import nn
import random
import numpy as np

class EVO:
    def __init__(self, population_size, num_parents, mutants_per_generation = 0):
        self.population_size = population_size
        self.num_parents = num_parents
        self.n_mutants = mutants_per_generation

    def crossing_over(self, p1: nn.Agent, p2: nn.Agent):
        if not p1.n_inputs == p2.n_inputs:
            print('Can\'t perform crossing over: number of inputs differs from parent to parent')
            return
        if not p1.n_outputs == p2.n_outputs:
            print('Can\'t perform crossing over: number of outputs differs from parent to parent')
            return
        child = nn.Agent(p1.n_inputs, p1.n_outputs)
        child.activation = p1.activation
        child.dense1.W = self.random_mix(p1.dense1.W, p2.dense1.W)
        child.dense1.b = self.random_mix(p1.dense1.b, p2.dense1.b)
        return child

    def random_mix(self, X, Y):
        choice = np.random.randint(2, size = X.size).reshape(X.shape).astype(bool)
        return np.where(choice, X, Y)

    def randomly_modify(self, arr):
        mask = np.random.randint(0,3, size = arr.shape).astype(np.bool8)
        modifier = np.random.rand(*arr.shape)*np.max(arr)
        arr[mask]+=modifier[mask]
        return arr

    def step(self, parents):
        new_gen = []
        #crossing over
        l = True
        while l:
            for i in range(self.num_parents-1, 0, -1):
                if not l:
                    break
                for j in range(0, self.num_parents):
                    new_gen.append(self.crossing_over(parents[i], parents[j]))
                    #print(len(new_gen))
                    if len(new_gen) >= self.population_size - self.num_parents:
                        l = False
                        break

        #adding the parents to the new population in order to not lose their genes
        new_gen.extend(parents)
        #mutations
        for i in range(self.n_mutants):
            j = np.random.randint(0, self.population_size)
            new_gen[j].dense1.W = self.randomly_modify(new_gen[j].dense1.W)
            new_gen[j].dense1.b = self.randomly_modify(new_gen[j].dense1.b)
            
        return new_gen


if __name__ == '__main__':
    parents = [nn.Agent(3, 1) for i in range(4)]
    new_generation = NEAT(30, 4, 10).step(parents)
    print(new_generation)
    print(len(new_generation))