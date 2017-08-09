from lib.instance_generation.chen_grossman_miller_generator import generate_chen_grossman_miller_instances
from lib.instance_generation.grossman_random_generator import generate_grossman_random_instances
from lib.instance_generation.min_utility_cost_solver import solve_min_utility_cost
from lib.exact_methods.exact_solver import solve_exactly
from lib.heuristic_methods.heuristic_solver import solve_heuristically
from lib.io_modules.bigM_comparator import bigM_compare
from lib.io_modules.bigM_comparator import write_bigM_comparison_spreadsheet
from lib.io_modules.results_visualization import generate_problem_sizes_table
from lib.io_modules.results_visualization import generate_exact_methods_table
from lib.io_modules.results_visualization import generate_heuristic_methods_table
from lib.io_modules.results_visualization import generate_comparison_table
from lib.io_modules.results_visualization import generate_upper_bounds_box_plot
from lib.io_modules.results_visualization import generate_elapsed_times_box_plot
from lib.io_modules.results_visualization import generate_line_chart
from lib.io_modules.results_visualization import generate_bigM_comparison_table


# INSTANCE GENERATION

#print('--Generation of chen_grossman_miller instances')
#generate_chen_grossman_miller_instances()

#print('--Generation of grossman_random instances')
#generate_grossman_random_instances()

#print('--Minimum utility cost solving')
#solve_min_utility_cost()

# EXACT METHODS

#print('--Minimum number of matches solving via exact methods')
#solve_exactly()

# HEURISTIC METHODS

#print('--Minimum number of matches solving via heuristic methods')
#solve_heuristically()

# BIG-M COMPARISONS

#print('--BigM comparisons')
#bigM_compare()
#write_bigM_comparison_spreadsheet()

# PLOTTING

#print('--Generating box-and-whisker plots')
#generate_upper_bounds_box_plot()
#generate_elapsed_times_box_plot()

#print('--Generating line chart')
#generate_line_chart()


# RESULTS PRINTING

#print('--Printing mip results')
#print_mip_results()

#print('--Printing heuristic results')
#print_heuristic_results()




# RSULTS TABLE GENERATION (IN THE PAPER)

#print('--Generating problem sizes table')
#generate_problem_sizes_table()

#print('--Generating exact methods table')
#generate_exact_methods_table()

#print('--Generating heuristic methods tables')
#generate_heuristic_methods_table()

#print('--Generating comparison table')
#generate_comparison_table()

#print('--Generating bigM comparison table')
#generate_bigM_comparison_table()



# RESULTS TABLE GENERATION (IN THE PRESENTATION)

#print('--Generating all heuristic results tables')
#generate_all_exact_results_tables()

#print('--Generating comparison table: relaxation rounding')
#generate_relaxation_rounding_comparison_table()

#print('--Generating comparison table: water filling')
#generate_water_filling_comparison_table()

#print('--Generating all heuristic results tables')
#generate_all_heuristic_results_tables()