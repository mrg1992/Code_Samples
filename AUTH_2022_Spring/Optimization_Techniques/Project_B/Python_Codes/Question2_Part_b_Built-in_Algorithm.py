import time
import random
from scipy.optimize import minimize

random_initialization = 1
formula = 1   #Which function to select

def function(x):
    if formula == 1:
        return (x[0] + 2*x[1] - 7)**2 + (2*x[0] + x[1] -5)**2    #Booth Function
    elif formula == 2:
        return 0.26*(x[0]**2 + x[1]**2) - 0.48*x[0]*x[1]         #Matyas Function
    elif formula == 3:
        return 2*(x[0]**2) - 1.05*(x[0]**4) + (x[0]**6)/6 + x[0]*x[1] + x[1]**2   #Three-hump Camel Function
        

if formula == 3:
    boundary = [-4.5, 4.5]
    func_name = "Booth Function"
elif formula == 2:
    boundary = [-10, 10]
    func_name = "Matyas Function"
else:
    boundary = [-5, 5]
    func_name = "Three-hump Camel Function"

if random_initialization == 1:
    x1 = random.uniform(boundary[0], boundary[1])
    x2 = random.uniform(boundary[0], boundary[1])
else:
    x1 = -1
    x2 = -1

print("\nFunction:   {}".format(func_name))
print("\nDimention:    2")
print("\nRandomly Initialized?    {}".format(bool(random_initialization)))
print("\nInitial X:   {}".format([x1, x2]))
print("\n\n###############  Solution  ###############\n")
    
def main():
    OptimizeResult = minimize(function, [x1, x2])
    print("\nWas Optimization successful?    {}".format(OptimizeResult.success))
    print("\nSolution - Point:    {}".format(OptimizeResult.x))
    print("\nValue of the objective function:    {}".format(OptimizeResult.fun))
    

start_time = time.time()

main()

end_time = time.time()

runtime_sec = end_time - start_time

print("\nThe algorithm took {} minutes and {} seconds to run.".format(int(runtime_sec/60), runtime_sec % 60))