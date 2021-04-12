import matplotlib.pyplot as plt
import glob


class VisualizeTutorialData:

    def __init__(self):
        self.runs_to_action_scores = {}  # k = run_id, v = {action, score}
        self.all_scores_per_action = {}  # k = action_count, v = [scores]
        self.min_score_per_action = {}  # k = action count, v = score representing minimum across all runs
        self.max_score_per_action = {}  # k = action count, v = score representing maximum across all runs
        self.data_dir = '../data/'
        self.max_actions_over_all_runs = -1

    def read_in_data(self):
        data_files = glob.glob(self.data_dir+"*.csv")
        run_id = 0
        for filename in data_files:
            with open(filename, 'r') as f:
                curr_run_action_score_data = {}
                header_line = True
                for line in f.readlines():
                    if header_line:
                        header_line = False
                        continue
                    else:
                        action_count, score = line.strip().split(",")
                        action_count = int(action_count)
                        score = int(score)
                        curr_run_action_score_data[action_count] = score

                        if action_count not in self.all_scores_per_action.keys():
                            self.all_scores_per_action[action_count] = [score]
                        else:
                            self.all_scores_per_action[action_count].append(score)

                        if action_count > self.max_actions_over_all_runs:
                            self.max_actions_over_all_runs = action_count

                        if action_count not in self.min_score_per_action.keys():
                            self.min_score_per_action[action_count] = score
                        elif score < self.min_score_per_action[action_count]:
                            self.min_score_per_action[action_count] = score

                        if action_count not in self.max_score_per_action.keys():
                            self.max_score_per_action[action_count] = score
                        elif score > self.max_score_per_action[action_count]:
                            self.max_score_per_action[action_count] = score

            self.runs_to_action_scores[run_id] = curr_run_action_score_data
            run_id += 1

    def compute_average_run(self):
        # first fill in values on shorter runs
        for run_id in self.runs_to_action_scores.keys():
            max_action_count_this_run = 0
            for a, s in self.runs_to_action_scores[run_id].items():
                if a > max_action_count_this_run:
                    max_action_count_this_run = a

            for range()


    def graph_data(self):
        fig, ax = plt.subplots(1)




if __name__ == "__main__":
    v = VisualizeTutorialData()
    v.read_in_data()
    v.graph_data()
