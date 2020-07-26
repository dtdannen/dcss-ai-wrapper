import pandas as pd
import seaborn as sns

def main():
	data_file_prefix = "./data/"
	dcss_df = pd.DataFrame()
	agents = ["fast-downward_agent_seed_", "random_agent_seed_", "q-learning_new_agent_seed_"]
	num_seeds = 3
	time_str = time.strftime("%Y%m%d_%H%M%S_")

	for seed in range(1,num_seeds+1):
		for agent in agents:
			filepath= data_file_prefix + agent + str(seed) +".csv"
			print("reading: " + filepath)
			cur_df = pd.read_csv(filepath, header=0, names=["Actions Executed", "Tiles Visited"], usecols=[0,1])
			cur_df["Agent Type"] = agent.split("_")[0].capitalize()
			cur_df["seed"] = seed
			dcss_df = pd.concat([dcss_df, cur_df])

	sns.set(style="darkgrid")
	plot = sns.lineplot(x="Actions Executed", y="Tiles Visited", hue="Agent Type", data=dcss_df)
	fig = plot.get_figure()
	fig.savefig(time_str + 'three_agents_three_seeds.png')

if __name__ == "__main__":
    #TODO should pass command line args and print usage
    main()