# Quantum Optimal Control

## 1. What has been done ?

- [summary.xlsx](./summary.xlsx)

## 2. Algorithms and Implementations

- List of Jupyter Notebooks. Since there are many graphs, some are big, I will just put their links instead of showing them below:
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE/examples.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE/examples-spectrum.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE%20autograd%20jax/examples.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE%20genetic/examples.html

    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT/examples.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20autograd/examples.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20auto/examples.html
    - https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20nelder/examples.html
    - https://github.com/tesla-cat/Quantum-Optimal-Control/blob/main/1%20Implementations/6%20GOAT%20genetic/examples.ipynb

Quantum optimal control is used to optimize some parameters that define the control pulse. 
Naturally, there are two types of parameters:

- Analytical: The control pulses are indirectly described by parameters that define continuous functions, for example, Fourier components. 
- Piecewise constant: The control pulses are directly described by the parameters, i.e., time is divided into discrete steps, the parameters are simply the amplitude of the pulse at each timestep.

In this project, I call these two interchangeably with their representing algorithms: 

- Analytical = GOAT = Gradient Optimization of Analytic Controls (2018)
- Piecewise constant = GRAPE = Gradient Ascent Pulse Engineering (2004)

The algorithms under these two main categories only differ from the optimization method, 
whereas the formulation of the problem and the minimization target does not change.

I have implemented the following:

- Piecewise constant (GRAPE)
    - Gradient based minimization algorithm
        - [Calculate gradient using analytically derived formula](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE/examples.html), [spectrum](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE/examples-spectrum.html)
        - [Calculate gradient using automatic differentiation algorithm](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE%20autograd%20jax/examples.html)
    - Non Gradient
        - [Genetic algorithm](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/1%20GRAPE%20genetic/examples.html)

- Analytical (GOAT)
    - Gradient based minimization algorithm
        - [Calculate gradient using analytically derived formula](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT/examples.html)
        - [Calculate gradient using automatic differentiation algorithm](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20autograd/examples.html) 
        - [Calculate gradient based on finite difference method](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20auto/examples.html) 
    - Non Gradient
        - [Nelder Mead algorithm](https://tesla-cat.github.io/Quantum-Optimal-Control/1%20Implementations/6%20GOAT%20nelder/examples.html)
        - [Genetic algorithm](https://github.com/tesla-cat/Quantum-Optimal-Control/blob/main/1%20Implementations/6%20GOAT%20genetic/examples.ipynb)

The following comparisons have been observed:

- Piecewise constant (GRAPE) vs Analytical (GOAT)
    - It is much easier to optimize Piecewise constant pulse than Analytical pulse. Reflected by the convergence speed.
    - GOAT was not able to solve the cat state transfer problem for a qubit-cavity system, whereas GRAPE found simple pulses. Through Fourier analysis of these pulses, it suggests that there does exist a set of analytical parameters, which I wonder why GOAT wasn't able to find. Possible reasons are:
        - Based on the control landscape theory, although we know that the optimal set of analytical parameters exist, it is surrounded by many traps, thus they are hard to find.
        - In the GRAPE optimization, changing one parameter (pulse amplitude at one time point), doesn't influence other parameters (pulse amplitudes as other time points). Whereas in GOAT optimization, changing one parameter causes amplitude to change at all time points.

- Gradient based minimization algorithm vs Non Gradient
    - Gradient methods converge much faster than non gradient methods. The latter either converges slowly or never converges. This agrees with the computer optimization community.
    - In the Piecewise constant case, Gradient method is able to generate very smooth pulses when the pulse derivative cost is added to the infidelity cost. Whereas a non-gradient method produces very noisy pulses even when the derivative cost is present. This is also expected as the non-gradient algorithms choose the amplitude at each time point independent of those from other time points.

- Analytically derived gradient vs automatic gradient
    - Analytically derived gradients are faster to evaluate than the automatic gradient. This is because automatic gradients are calculated by chain rule according to a computation graph built during forward evaluation of the code. Whereas Analytically derived gradients are derived and simplified by hand on paper before implementing as computer code.
    However, the speed advantage is not very significant since they are both quite fast.
    - Automatic gradient has the advantage of reducing coding / derivation effort by human as suggested by Schuster et al.

