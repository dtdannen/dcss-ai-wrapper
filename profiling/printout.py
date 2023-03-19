import pstats

p = pstats.Stats('profiles/profile_1')

p.strip_dirs().sort_stats('cumulative').print_stats()