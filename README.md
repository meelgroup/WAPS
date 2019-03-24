# WAPS-Sampler
WAPS, Weighted And Projected Sampler, generates samples on a sampling set conforming to a weight distribution defined by a literal-weighted weight function. It operates by using a compiled deterministic decomposable negation normal form (d-DNNF) of a CNF. It expects CNF in the DIMACS format and d-DNNF in the same format as that produced by the [C2D compiler](http://reasoning.cs.ucla.edu/c2d/). Is is based on our paper titled "WAPS:Weighted and Projected Sampling" as published in TACAS-2019 conference.

## Installation
```bash
sudo apt-get install graphviz
sudo apt-get install libgmp-dev
sudo apt-get install libmpfr-dev
sudo apt-get install libmpc-dev
pip install -r requirements.txt
wget -P bin/ http://www.cril.univ-artois.fr/KC/ressources/d4
chmod u+x bin/d4
```

For now, [D4 compiler](http://www.cril.univ-artois.fr/KC/d4.html) and [Dsharp_PCompile](https://bitbucket.org/haz/dsharp) (modified for our use case, see the "PCompile" procedure) are included as default for compiling CNF to d-DNNF. Any other compiler can be easily used with slight modifications.

## Running WAPS
You can run WAPS by using 'WAPS.py' Python script present in WAPS directory. A simple invocation looks as follows:
```bash
python3 WAPS.py <cnffile>
```
The usage instructions and default values to arguments can be found by running
```bash
python3 WAPS.py -h
```
## Weight Format
WAPS support providing weights in CNF itself apart from being provided separately in a file. A type variable weight is in [0,inf], specified by line starting with 'w' ,literal, and weight separated by space. Later, WAPS normalizes it such that weight(l)+weight(-l)=1 where l is a literal. By default, every variable weight is set to 0.5, if its value is not given in CNF or the weightfile.

## Specifying sampling set
WAPS support providing sampling set in CNF itself. It is specified by lines starting with 'c ind' ,var indexes separated by space, and ended by 0. If sampling set is not provided, by default, every variable specified in formula is assumed to be a part of sampling set.

## Output Format
The output samples are stored in samples.txt by default. Each line of the output consists of a serial number of the sample followed by a satisfying assignment projected on sampling set. The satisfying assignment consists of literals seperated by space. Note that turning random assignment (--randAssign) to 0 can lead to partial assignments in each line. In such cases, the unassigned sampling variables can be chosen to be True or False.

Also, WAPS can output a graphical representation of d-DNNF for the input NNF. In this d-DNNF, the leaves consists of literals and internal nodes can be OR ('O') or AND ('A') nodes as expected for an NNF. However, internal nodes also contain 2 numbers seperated by space in our representation. This second one gives the annotation. The first one, only serves the purpose of distinguishing between individual OR and AND nodes and has no other meaning.

## Benchmarks
Benchmarks can be found [here](https://drive.google.com/open?id=1AQnpPwqJ-3ouwqKGw_VIjqWEHfQCnzBM).

## Python Usage
WAPS is also available as a library on PyPI, installable via pip. 
```bash
sudo apt-get install graphviz
sudo apt-get install libgmp-dev
sudo apt-get install libmpfr-dev
sudo apt-get install libmpc-dev
wget https://github.com/meelgroup/WAPS/master/bin/Dsharp_PCompile
wget http://www.cril.univ-artois.fr/kc/ressources/d4
chmod u+x Dsharp_PCompile
chmod u+x d4
sudo mv Dsharp_PCompile /usr/local/bin/
sudo mv d4 /usr/local/bin/
pip install WAPS
```
Please reload your shell so that binaries are accessible via PATH.

A typical usage is as follows:
```python
from WAPS import sampler

sampler = sampler(cnfFile="toy.cnf")
sampler.compile()
sampler.parse()
sampler.annotate()
samples = sampler.sample()
print(list(samples))
```

You can find more information on usage by:
```python
from WAPS import sampler
help(sampler)
```


## Issues, questions, bugs, etc.
Please click on "issues" at the top and [create a new issue](https://github.com/meelgroup/WAPS/issues). All issues are responded to promptly.

## How to Cite
```
@inproceedings{GSRM19,
author={Gupta, Rahul and  Sharma, Shubham and  Roy, Subhajit and  Meel, Kuldeep S.},
title={WAPS: Weighted and Projected Sampling},
booktitle={Proceedings of Tools and Algorithms for the Construction and Analysis of Systems (TACAS)},
month={4},
year={2019},
code={https://github.com/meelgroup/WAPS},
abstract={Previous work on applying Knowledge compilation has focused on uniform sampling over all the variables. Since the constraints are written in high level languages such as Verilog, the popular CNF encoding schemes as Tseitin encoding introduces additional auxiliary variables. The resulting CNF formulas are not equivalent but equisatisfiable. In particular, for a formula $G$ specified in high level language we obtain a CNF formula F such that $G (X) = \exists Y F(X,Y)$. This makes one wonder if it is possible to extend Knowledge compilation based techniques to sample over a subset of variables. Furthermore, languages such as Verilog allow specification of weights to user-defined constraints, so there is a need to sample according to the posterior distribution. In this paper, we provide affirmative question to the above two questions: We propose KUS that samples over user defined subset of variables from posterior distribution for a given prior distribution defined over product spaces.},
}
```

## Contributors
  * Rahul Gupta (grahul@iitk.ac.in)
  * Shubham Sharma (smsharma@iitk.ac.in)
  * Subhajit Roy (subhajit@iitk.ac.in)
  * Kuldeep Meel (meel@comp.nus.edu.sg)