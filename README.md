# Exact and Heuristic Methods for the Minimum Number of Matches Problem in Heat Recovery Network Design

Source code of the methods proposed in Dimitrios Letsios, Georgia Kouyialis, Ruth Misener, "Heuristics with Performance Guarantees for the Minimum
Number of Matches Problem in Heat Recovery Network Design".

This repository contains 1) a collection of benchmark instances of the general heat exchanger network synthesis problem, 2) a source code implementing and evaluating the performance of exact and heuristic methods for the minimum number of matches problem (using Python 2.7.6 and Pyomo 4.4.1), and 3) the obtained results after running the code on an Intel Core i7-4790 CPU 3.60 GHz with 15.6 GB RAM and 64-bit Ubuntu 14.04. Letsios, Kouyialis and Misener (2017) present a technical description of the implemented methods.

Based on the standard sequential method for heat exchanger network design, solving the minimum number of matches problem requires solving the minimum utility cost problem beforehand. In particular, the solution process consists of the following steps:
1. generation of minimum utility cost (i.e. general heat exchanger network design) input files,
2. solving of the minimum utility cost problem using the transportation LP model and generation of the minimum number of matches problem instances,
3. solving of the minimum number of matches problem via exact and heuristic methods.

All input and output data files are located in directory `data`, all required Python modules are located in directory `lib` while the the root file `main.py` performs all steps for obtaining the results. 

## Benchmark Instances

This repository contains a collection of 48 general heat exchanger network design problem instances. These instances are classified into three test sets: 
1. Furman (2000) test set,
2. Chen et al. (2015a, 2015b) test set, and
3. Grossman (2017) test set.

The Furman (2000) instances are manually digitized from the engineering literature, the Chen et al. (2015a, 2015b) are existing instances in the literature, and the Grossman (2017) instances are generated randomly with fixed seeds. Obtaining the Chen et al. (2015a, 2015b) and Grossman (2017) instances requires parsing existing `.gms` files and random selections in the latter case. All minimum utility cost instances as well as the corresponding `.gms` files are stored in the directory `data/original_instances`.

## Minimum Utility Cost Problem Instances

An instance of the minimum utility cost problem (class `Min_Utility_Instance` in `lib/problem_classes/min_utility_instance.py`) consists of
- a set of hot streams HS,
- a set of cold streams CS,
- a set of hot utilities HU,
- a set of cold utilities CU, and
- a minimum approach temperature ΔTmin.

A hot / cold stream (class `Stream` in `lib/problem_classes/stream.py`) is specified by
- an inlet temperature Tin,
- an outlet temperature Tout, and
- a flow rate heat capacity FCp.

A hot / cold utility (class `Utility` in `lib/problem_classes/utility.py`) is associated with
- an inlet temperature Tin,
- an outlet temperature Tout, and
- a cost κ.

A minimum utility cost problem is instance is stored in `.dat` file under the following format:
---
DTmin 10 
HS1 320 200 16.67 
HS2 480 280 20 
CS1 140 320 14.45 
CS2 240 500 11.53 
HU1 540 539 0.001 
CU1 100 180 0.00005
---

The first line specifies the minimum approach temperature. Every subsequent line and specifies the parameters of either a hot stream (`HS`), cold stream (`CS`), hot utility (`HU`), or cold utility (`CU`) and consists of four elements separated by one or more white spaces. The first element is an identifier indicating whether the line corresponds to a hot stream, cold stream, hot utility or cold utility. The second and third elements correspond to the inlet temperature Tin and outlet temperature Tout, respectively. The fourth element indicates the flow rate heat capacity or the cost depending on whether the line corresponds to a stream or utility, respectively.