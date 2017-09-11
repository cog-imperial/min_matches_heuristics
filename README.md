# Exact and Heuristic Methods for the Minimum Number of Matches Problem in Heat Recovery Network Design

Source code of the methods proposed in Dimitrios Letsios, Georgia Kouyialis, Ruth Misener, "Heuristics with Performance Guarantees for the Minimum
Number of Matches Problem in Heat Recovery Network Design".

This repository contains 1) a collection of benchmark instances of the general heat exchanger network synthesis problem, 2) a source code implementing and evaluating the performance of exact and heuristic methods for the minimum number of matches problem (using Python 2.7.6 and Pyomo 4.4.1), and 3) the obtained results after running the code on an Intel Core i7-4790 CPU 3.60 GHz with 15.6 GB RAM and 64-bit Ubuntu 14.04. Letsios, Kouyialis and Misener (2017) present a technical description of the implemented methods.

Based on the standard sequential method for heat exchanger network design, solving the minimum number of matches problem requires solving the minimum utility cost problem beforehand. In particular, the solution process consists of the following steps:
1. generation of minimum utility cost (i.e. general heat exchanger network design) input files,
2. solving of the minimum utility cost problem using the transportation LP model and generation of the minimum number of matches problem instances,
3. solving of the minimum number of matches problem via exact and heuristic methods.

All input and output data files are located in directory `data`, all required Python modules are located in directory `lib` while the the root file `main.py` performs all steps for obtaining the results. 
