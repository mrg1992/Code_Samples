import numpy as np
from sympy import symbols, zeros, Matrix, pprint, sqrt, Eq, solve
import random
import copy


x1, x2 = symbols('x1 x2')
symbol_list = [x1, x2]
lam1 = symbols('lambda1')
lam2 = symbols('lambda2')
extended_sym_list = [x1, x2, lam1, lam2]
X = Matrix(2, 1, [x1, x2])



f = (x1 - 1)**2 + 2*(x2 - 1)**2 
g1 = 3 - x1 - 4*x2
g2 = x1 - x2






def main():
    print("\nFunction f(X):\n")
    pprint(f)
    print("\nFunction g1(X):\n")
    pprint(g1)
    print("\nFunction g2(X):\n")
    pprint(g2)
    
    g = [g1, g2]
    
    L = f - lam1 * g1 - lam2 * g2
    print("\nFunction L(X, lambda):\n")
    pprint(L)
    
    
    gradient_f = []
    for element in symbol_list:
        gradient_f.append(f.diff(element))
    print("\nGradient of f:")
    pprint(Matrix(gradient_f))
    
    
    gradient_L = []
    for element in symbol_list:
        gradient_L.append(L.diff(element))
    print("\nGradient of L with respect to x1 and x2:")
    pprint(Matrix(gradient_L))
    
    lagrange_expressions = []
    for item in gradient_L:
        lagrange_expressions.append(item)
    print("\nExpressions with Lagrange multiplier:")
    pprint(Matrix(lagrange_expressions))
    
    complete_expressions = copy.deepcopy(lagrange_expressions)
    complete_expressions.append(lam1 * g1)
    complete_expressions.append(lam2 * g2)
    
    equations = []
    for expression in complete_expressions:
        equations.append(Eq(expression, 0))
    
    x_lam_star_set = solve(equations, extended_sym_list, dict=True)
    
    print("\nList of (X, Lambda) satisfying the equations condition:")
    print(x_lam_star_set)
    
    
    counter = 0
    for x_lambda in x_lam_star_set:
        
        
        #checking inequalities:
        flag = 1
        for gi in g:
            if gi.subs(x_lambda) < 0:
                flag = 0
                break
        if flag == 1:
            if x_lambda[lam1] < 0:
                flag = 0
            if x_lambda[lam2] < 0:
                flag = 0
        
        if flag == 1:
            print("\n\n##########################################\n##########################################")
            print("\n&&& (X, Lambda) value number {} that satisfies all of the conditions:\n".format(counter+1))
            print("{}\n".format(x_lambda))
            print("\nPoint {} is a LOCAL MINIMIZER and the value of the function at this point is: {}".format([x_lambda[x1], x_lambda[x2]], float(f.subs({'x1':x_lambda[x1], 'x2':x_lambda[x2]}))))
        
        

        
main()    