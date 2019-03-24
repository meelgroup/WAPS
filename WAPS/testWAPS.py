from WAPS import sampler

DIMACScnf = open("toy.cnf").read()
sampler = sampler(cnfFile="toy.cnf")
sampler.compile()
sampler.parse()
sampler.start_annotation()
print(sampler.weights)
# sampler.save_annotation_tree("bench.pkl")
# sampler.load_annotation_tree("bench.pkl")
# print(list(sampler.samplingSet))
samples = sampler.sample(randAssign=1, totalSamples=2)
print(list(samples))
# sampler.draw("toy.png")



