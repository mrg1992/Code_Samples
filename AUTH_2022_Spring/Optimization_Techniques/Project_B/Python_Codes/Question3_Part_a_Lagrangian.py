import numpy as np
from sympy import symbols, zeros, Matrix, pprint, sqrt, Eq, solve
import random
import copy


x1, x2, x3 = symbols('x1 x2 x3')
symbol_list = [x1, x2, x3]
lam = symbols('lambda')
extended_sym_list = [x1, x2, x3, lam]
X = Matrix(3, 1, [x1, x2, x3])

function_selector = 1

f1 = x1**2 + x2**2 + x3**2
g1 = x1 + x2 + x3 - 1

f2 = x1*x2*x3
g2 = x1*x2 + x1*x3 + x2*x3 - 6


if function_selector == 1:
    f = f1
    g = g1
else:
    f = f2
    g = g2



def main():
    print("\nFunction f(X):\n")
    pprint(f)
    print("\nFunction g(X):\n")
    pprint(g)
    
    L = f - lam * g
    print("\nFunction L(X, lambda):\n")
    pprint(L)
    
    
    gradient_f = []
    for element in symbol_list:
        gradient_f.append(f.diff(element))
    print("\nGradient of f:")
    pprint(Matrix(gradient_f))
    
    gradient_g = []
    for element in symbol_list:
        gradient_g.append(g.diff(element))
    print("\nGradient of g:")
    pprint(Matrix(gradient_g))
    
    gradient_L = []
    for element in extended_sym_list:
        gradient_L.append(L.diff(element))
    
    
    
    
    lagrange_expressions = []
    for item in gradient_L:
        lagrange_expressions.append(item)
    print("\nExpressions with Lagrange multiplier:")
    print(lagrange_expressions)
    
    complete_expressions = copy.deepcopy(lagrange_expressions)
    complete_expressions.append(g)
    
    first_order_equations = []
    for expression in complete_expressions:
        first_order_equations.append(Eq(expression, 0))
    
    x_lam_star_set = solve(first_order_equations, extended_sym_list, dict=True)
    
    print("\nList of Points satisfying the necessary condition:")
    print(x_lam_star_set)
    
    
    
    hessian_mat = zeros(len(extended_sym_list), len(extended_sym_list))
    for i in range(len(extended_sym_list)):
        for j  in range(len(extended_sym_list)):
            hessian_mat[i,j] = L.diff(extended_sym_list[i]).diff(extended_sym_list[j])
    print("\nGeneral form of the Hessian Matrix:")
    pprint(hessian_mat)
    
    
    #solution = []
    counter = 0
    for x_lambda in x_lam_star_set:
        counter = counter + 1
        hessian_mat_k = hessian_mat.subs(x_lambda)
        print("\n\n##########################################\n##########################################")
        print("\n&&& (X, Lambda) value number {} that satisfies the first order condition:\n".format(counter))
        print("{}\n".format(x_lambda))
        print("The Hessian matrix at point {}:\n".format(x_lambda))
        pprint(hessian_mat_k)
        
        #calculating Minors
        minors = []
        for i in range(2, len(extended_sym_list)):
            minor_submatrix = hessian_mat_k.extract(list(range(i+1)), list(range(i+1)))
            minors.append(minor_submatrix.det())
        
        print("\n### Minors:\n")
        for i in range(len(minors)):
            print("Delta_{} = {}".format(i+3, minors[i]))
        
        #Analyzing the minors to determine whether the critical points are a local optimizer.
        #If yes, determining whether they are Minimizers or Maximizers.    
        sum_flag = 0
        for i in range(len(minors)):
            if minors[i] < 0:
                sum_flag = sum_flag + 1
            else:
                break
        if sum_flag == len(minors):
            print("\nPoint {} is a LOCAL MINIMIZER and the value of the function at this point is: {}".format([x_lambda[x1], x_lambda[x2], x_lambda[x3]], float(f.subs({'x1':x_lambda[x1], 'x2':x_lambda[x2], 'x3':x_lambda[x3]}))))
        else:
            sum_flag = 0
            for i in range(len(minors)):
                if minors[i]*((-1)**(i+1)) < 0:
                    sum_flag = sum_flag + 1
                else:
                    break
            if sum_flag == len(minors):
                print("\nPoint {} is a LOCAL MAXIMIZER and the value of the function at this point is: {}".format([x_lambda[x1], x_lambda[x2], x_lambda[x3]], float(f.subs({'x1':x_lambda[x1], 'x2':x_lambda[x2], 'x3':x_lambda[x3]}))))
            else:
                print("\nPoint {} is NOT a local optimizer".format([x_lambda[x1], x_lambda[x2], x_lambda[x3]]))
        


main()