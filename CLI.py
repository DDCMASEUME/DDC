import os
from pprint import pprint

import click

from SolveOpt import get_solution
from InputOutput import load
from GenerateInstances import ninstances


@click.command()
@click.option('--refined/--no-refined', default=False)
@click.option('--generate', nargs=4, type=int)
@click.option('--solve', type=int)
def main(refined, generate, solve):

    if generate:
        batchnumber, nsets, maxp, n = generate
        dir = "Batch" + str(batchnumber)
        os.mkdir(dir)
        ninstances(n, 1154, 890, nsets, maxp)

    if solve:
        f = open('batchsol.txt', 'w')
        click.echo("✨Solving batch number " + str(solve) + "✨")
        json_instances = [f for f in os.listdir('./Batch'+str(solve))]
        for file in json_instances:
            print("Solving instance " + file)
            pointsets = load("Batch" + str(solve) +"/" + file)
            sol = get_solution(pointsets, refined)
            f.write("SOLUTION TO INSTANCE " + file + "\n")
            f.write("xvalues \n")
            f.write(" ".join(str(e) for e in sol[0]))
            f.write("yvalues \n")
            f.write(" ".join(str(e) for e in sol[1]))
            f.write("rvalues \n")
            f.write(" ".join(str(e) for e in sol[2]))
            f.write("--------------------------------------------------------")
            f.write("                                                        ")

        f.close()

if __name__ == "__main__":
    main()
