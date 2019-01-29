# /***********[WAPS.py]
# Copyright (c) 2018 Rahul Gupta, Shubham Sharma, Subhajit Roy, Kuldeep Meel
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********/

import argparse
import os
import pickle
import random
import re
import sys
import time
from fractions import Fraction

import numpy as np
import pydot
from gmpy2 import mpq, mpfr

class Node():
    def __init__(self,label=None,children=[],decision=None):
        self.label = label
        self.children = children
        self.models = 1
        self.decisionat = decision

class Sampler():
    '''Main class which defines parsing, graph drawing, counting and sampling functions'''
    def __init__(self):
        self.totalvariables = None
        self.variables = []
        self.treenodes = []
        self.graph = None
        self.samples = None
        self.drawnnodes = {}
        self.isSamplingSetPresent = False
    
    def drawtree(self,root):
        '''Recursively draws tree for the d-DNNF'''
        rootnode = pydot.Node(str(root.label)+" "+str(root.models))
        self.graph.add_node(rootnode)
        self.drawnnodes[root.label] = rootnode
        for ch in root.children:
            if ch.label not in self.drawnnodes:
                node = self.drawtree(ch)
                self.graph.add_edge(pydot.Edge(rootnode,node))
            else:
                self.graph.add_edge(pydot.Edge(rootnode,self.drawnnodes[ch.label]))
        return rootnode

    def parse(self,inputnnffile):
        '''Parses the d-DNNF tree to a tree like object'''
        with open(inputnnffile) as f:
            treetext = f.readlines()
        nodelen = 0
        for node in treetext:
            node = node.split()
            if node[0] == 'c':
                continue
            elif node[0] == 'nnf':
                self.totalvariables = int(node[3])
            elif node[0] == 'L':
                self.treenodes.append(Node(label=int(node[1])))
                nodelen+=1
            elif node[0] == 'A':
                if node[1] == '0':
                    self.treenodes.append(Node(label='T ' + str(nodelen)))
                else:
                    andnode = Node(label='A '+ str(nodelen))
                    andnode.children = list(map(lambda x: self.treenodes[int(x)],node[2:]))
                    self.treenodes.append(andnode)
                nodelen+=1
            elif node[0] == 'O':
                if node[2] == '0':
                    self.treenodes.append(Node(label='F '+ str(nodelen)))
                else:
                    ornode = Node(label='O '+ str(nodelen),decision = int(node[1]))
                    ornode.children = list(map(lambda x: self.treenodes[int(x)],node[3:]))
                    self.treenodes.append(ornode)
                nodelen+=1

    def annotate(self,root, weights = None):
        '''Computes Model Counts'''
        if(str(root.label)[0] == 'A'):
            root.weight = mpq('1')
            for ch in root.children: #can perform IBCP for conditioning               
                root.weight *= self.annotate(ch, weights=weights)
            return root.weight
        elif(str(root.label)[0] == 'O'):
            root.weight = self.annotate(root.children[0], weights=weights) + self.annotate(root.children[1], weights=weights)
            return root.weight
        else:
            try:
                int(root.label)
                if weights and abs(int(root.label)) in weights:
                    if int(root.label) > 0:
                        root.weight = weights[int(root.label)]
                    else:
                        root.weight = mpq('1')-weights[abs(int(root.label))]
                else:
                    root.weight = mpq('0.5')
            except:
                if (str(root.label)[0] == 'F'):
                    root.weight = 0
                elif (str(root.label)[0] == 'T'):                    
                    root.weight = 1
            return root.weight

    def getsamples(self,root,indices):
        '''Generates Uniform Independent Samples'''
        if(not indices.shape[0]):
            return
        if(str(root.label)[0] == 'O'):
            z0 = root.children[0].weight
            z1 = root.children[1].weight
            p = (mpq('1.0')*z0)/(z0+z1)
            tosses = np.random.binomial(1, p, indices.shape[0])
            self.getsamples(root.children[0],np.array(indices[np.where(tosses==1)[0]]))
            self.getsamples(root.children[1],np.array(indices[np.where(tosses==0)[0]]))
        elif(str(root.label)[0] == 'A'):
            for ch in root.children:       
                self.getsamples(ch,indices)
        else:
            try:
                int(root.label)
                for index in indices:
                    self.samples[index] += str(root.label)+' '
            except:
                pass

def random_assignment(solution, samplingset = [], weights=None):
    '''Takes total number of variables and a partial assignment
    to return a complete assignment'''
    literals = set()
    solutionstr = ""
    vartolit = {}
    for x in solution.split():
        literals.add(abs(int(x)))
        vartolit[abs(int(x))] = int(x)
    for i in samplingset:
        if i not in literals:
            if weights and i in weights:
                litchoice = np.random.choice([1, -1], p=[weights[i], 1-weights[i]])
                solutionstr += str(litchoice*i)+" "
            else:
                solutionstr += str(((random.randint(0,1)*2)-1)*i)+" "
        else:
            solutionstr += str(vartolit[i]) + " "
    return solutionstr
       

def fetchWeights(weightFile):
    '''either specify all positive literal weights between 0 and 1 or
    specify weights for both positive and negative literals.'''
    data = open(weightFile).read()
    lines = data.strip().split("\n")
    weights = {}
    for line in lines:
        if int(line.split(',')[0])*(-1) in weights:
            if int(line.split(',')[0]) > 0:
                weights[int(line.split(',')[0])] = mpq(Fraction(line.split(',')[1]))/(weights.pop(int(line.split(',')[0])*(-1), None)+mpq(Fraction(line.split(',')[1])))
            else:
                weights[int(line.split(',')[0])*(-1)] = weights[int(line.split(',')[0])*(-1)]/(weights[int(line.split(',')[0])*(-1)]+mpq(Fraction(line.split(',')[1])))
        else:
            weights[int(line.split(',')[0])] = mpq(Fraction(line.split(',')[1]))
    print(weights)
    return weights

def conditionWeights(lits, weights):
    '''Modifies the weight of positive literal as per condition given by list lits'''    
    for lit in lits:
        weights[int(lit)] = 1
        weights[-1*int(lit)] = 0

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outputfile", type=str, default="samples.txt", help="output file for samples", dest='outputfile')
    parser.add_argument("--drawtree", type=int, default = 0, help="draw nnf tree", dest='draw')
    parser.add_argument("--samples", type=int, default = 10, help="number of samples", dest='samples')
    parser.add_argument("--randAssign", type=int, default = 1, help="randomly assign unassigned variables in a model with partial assignments", dest="randAssign")
    parser.add_argument("--savePickle", type=str, default=None, help="specify name to save Pickle of count annotated dDNNF for incremental sampling", dest="savePickle")
    parser.add_argument("--weights", type=str, default=None, help="specify a csv file which contains weights for literals", dest="weightFile")
    parser.add_argument("--conditionVars",type=str, default="", help="specify the literals on which you want to condition", dest="conditionVars")
    parser.add_argument("--conditionFile", type=str, default="", help="specify the file containing the literals on which you want to condition", dest="conditionFile")
    parser.add_argument('--dDNNF', type=str, help="specify dDNNF file", dest="dDNNF")
    parser.add_argument('--countPickle', type=str, help="specify Pickle of count annotated dDNNF", dest="countPickle")
    parser.add_argument('DIMACSCNF', nargs='?', type=str, default="", help='input cnf file')
    args = parser.parse_args()
    if not (args.dDNNF or args.countPickle or args.DIMACSCNF):
        parser.error("Please give at least one argument out of dDNNF, countPickle and DIMACSCNF")
    draw = args.draw
    totalsamples = args.samples
    randAssignInt = args.randAssign
    dDNNF = False
    countPickle = False
    inputFile = False
    if args.countPickle:
        countPickle = args.countPickle
    else:
        if args.dDNNF:
            dDNNF = args.dDNNF        
        if args.DIMACSCNF:
            inputFile = args.DIMACSCNF
    savePickle = args.savePickle
    randAssign = False
    if (randAssignInt == 1):
        randAssign = True
    if (args.weightFile):
        weights = fetchWeights(args.weightFile)
    else:
        weights = {}
    sampler = Sampler()
    if inputFile:
        print("Seperating weights from Input cnf")
        weighttext = ''
        with open(inputFile, "r") as f:
            text = f.read()
            f.close()
        print("Extracting the Sampling Set")
        with open("/tmp/" + inputFile.split("/")[-1]+".pvars","w") as f:
            samplingvars = "v "
            for ind in re.findall(r"c ind.*", text):
                sampler.isSamplingSetPresent = True
                samplingvars += " ".join(ind.split(" ")[2:-1])
                samplingvars += " "
            samplingvars += "0"
            if (sampler.isSamplingSetPresent):
                for variable in samplingvars.split()[1:-1]:
                    sampler.variables.append(int(variable))
            f.write(samplingvars)
            f.close()
        with open("/tmp/" + inputFile.split("/")[-1]+".tmp", "w") as f:
            f.write(text.replace('w','c w'))
            f.close()
            weighttext = re.findall(r'^w[^\S\n]+.*', text, re.MULTILINE)
        for line in weighttext:
            if int(line.split()[1])*(-1) in weights:
                if int(line.split()[1]) > 0:
                    weights[int(line.split()[1])] = mpq(Fraction(line.split()[2]))/(weights.pop(int(line.split()[1])*(-1), None)+mpq(Fraction(line.split()[2])))
                else:
                    weights[int(line.split()[1])*(-1)] = weights[int(line.split()[1])*(-1)]/(weights[int(line.split()[1])*(-1)]+mpq(Fraction(line.split()[2])))
            else:
                weights[int(line.split()[1])] = mpq(Fraction(line.split()[2]))
        if not args.dDNNF:
            dDNNF = inputFile.split("/")[-1] + ".nnf"
            cmd = "/usr/bin/time --verbose ./d4 /tmp/" + inputFile.split("/")[-1] + ".tmp " + " -out=" + dDNNF
            if(sampler.isSamplingSetPresent):
                cmd = "/usr/bin/time --verbose ./Dsharp_PCompile -cs 2000 -pvarsfile "+ "/tmp/" + inputFile.split("/")[-1]+".pvars" +" -Fnnf " + dDNNF + " /tmp/" + inputFile.split("/")[-1]+".tmp" 

            start = time.time()
            os.system(cmd)
            print("The time taken by D4/Dsharp_PCompile is ", time.time() - start)
    if dDNNF:
        start = time.time()
        sampler.parse(dDNNF)
        if sampler.variables == []:
            for i in range(1,sampler.totalvariables+1):
                sampler.variables.append(i)
        print("The time taken to parse the nnf text:", time.time() - start)
        # can easily adjust code in conditionWeights to give cmd/file priority
        # right now, it simply takes union of the conditioned literals
        if (args.conditionFile):
            lits = open(args.conditionFile).read().strip().split()
            conditionWeights(lits, weights)
        if (args.conditionVars):
            lits = args.conditionVars.split()
            conditionWeights(lits, weights)
        start = time.time()
        modelcount = sampler.annotate(sampler.treenodes[-1], weights=weights)
        sampler.treenodes[-1].models = modelcount
        print("The time taken for Model Counting:", time.time()-start)
        timepickle = time.time()
        if savePickle:
            fp = open(savePickle, "wb")
            pickle.dump((sampler.variables,sampler.totalvariables,sampler.treenodes), fp)
            fp.close()
            print("Time taken to save the count annotated dDNNF pickle:", time.time() - timepickle)
    else:
        timepickle = time.time()
        fp = open(countPickle, "rb")
        (sampler.variables,sampler.totalvariables,sampler.treenodes) = pickle.load(fp)
        fp.close()
        print("The time taken to read the pickle:", time.time() - timepickle)
        if savePickle:
            fp = open(savePickle, "wb")
            pickle.dump((sampler.variables,sampler.totalvariables,sampler.treenodes), fp)
            fp.close()
            print("Time taken to save the count annotated dDNNF pickle:", time.time() - timepickle)
    if weights:
        print("Weighted Model Count as per normalised weights limited to var in dDNNF:",mpfr(sampler.treenodes[-1].weight))
    else:   
        print("Model Count limited to var in dDNNF:",mpfr(sampler.treenodes[-1].models))
    if draw:
        sampler.graph = pydot.Dot(graph_type='digraph')
        sampler.drawtree(sampler.treenodes[-1])
        sampler.graph.write_png('d-DNNFgraph.png')
    sampler.samples = []
    for i in range(totalsamples):
        sampler.samples.append('')
    start = time.time()
    if (sampler.treenodes[-1].weight == 0):
        print("The current conditional assignment has no satisfying sample")
        exit()
    sampler.getsamples(sampler.treenodes[-1],np.arange(0,totalsamples))
    print("The time taken by sampling:", time.time()-start)
    if randAssign:
        sampler.samples = list(map(lambda x: random_assignment(x, samplingset = sampler.variables, weights=weights), sampler.samples))
    f = open(args.outputfile,"w+")
    for i in range(totalsamples):
        f.write(str(i+1) + ", " + sampler.samples[i] + "\n")
    f.close()
    print("Samples saved to", args.outputfile)

if __name__== "__main__":
    main()