import matplotlib.pyplot as plt
import glob


class VisualizeTutorialData:

    def __init__(self):
        self.runs_to_action_scores = {}  # k = run_id, v = {action, score}
        self.all_scores_per_action = {}  # k = action_count, v = [scores]
        self.min_score_per_action = {}  # k = action count, v = score representing minimum across all runs
        self.max_score_per_action = {}  # k = action count, v = score representing maximum across all runs
        self.average_score_per_action = {}  # k = action count, v = average score
        self.data_dir = '../data/'
        self.max_actions_over_all_runs = -1
        self.SCORE_OFFSET = 1  # this is because of how we recorded the data

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
                        score = int(score) - self.SCORE_OFFSET
                        curr_run_action_score_data[action_count] = score


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
            score_max_action_count_this_run = -1
            for a, s in self.runs_to_action_scores[run_id].items():
                if a > max_action_count_this_run:
                    max_action_count_this_run = a
                    score_max_action_count_this_run = s

                if a not in self.all_scores_per_action.keys():
                    self.all_scores_per_action[a] = [s]
                else:
                    self.all_scores_per_action[a].append(s)

            for i in range(max_action_count_this_run+1, self.max_actions_over_all_runs+1):
                if i in self.runs_to_action_scores[run_id]:
                    raise Exception("Tried to add a value that already exists when filling in values")
                else:
                    self.runs_to_action_scores[run_id][i] = score_max_action_count_this_run+1

                if i not in self.all_scores_per_action.keys():
                    self.all_scores_per_action[i] = [score_max_action_count_this_run+1]
                else:
                    self.all_scores_per_action[i].append(score_max_action_count_this_run+1)

        # now verify data is consistent and average the scores
        num_data_points_per_action = len(self.runs_to_action_scores.keys())
        for a in self.all_scores_per_action.keys():
            if len(self.all_scores_per_action[a]) != num_data_points_per_action:
                raise Exception("action {} has {} data point when it should have {} data points".format(a, len(self.all_scores_per_action[a]), num_data_points_per_action))
            else:
                self.average_score_per_action[a] = sum(self.all_scores_per_action[a]) / num_data_points_per_action

    def get_data_as_ordered_list(self, data_as_dict):
        average_scores = []
        for i in range(self.max_actions_over_all_runs):
            average_scores.append(data_as_dict[i])
        return average_scores

    def get_min_max_scores(self):
        min_scores = []
        max_scores = []
        for i in range(len(self.all_scores_per_action.keys())):
            min_scores.append(min(self.all_scores_per_action[i]))
            max_scores.append(max(self.all_scores_per_action[i]))

        return min_scores, max_scores

    def graph_data(self):
        fig, ax = plt.subplots(1)
        x_data = list(range(self.max_actions_over_all_runs))
        average_scores = self.get_data_as_ordered_list(self.average_score_per_action)
        min_scores, max_scores = self.get_min_max_scores()

        ax.plot(average_scores, lw=2, label="Average Planner Agent Score", color='blue')
        ax.fill_between(range(0, len(max_scores)), max_scores, min_scores, facecolor='blue', alpha=0.1)

        ax.set_title('Planner Agent Performance on Tutorial 1')
        ax.set_ylabel('Goals Achieved (out of 4)')
        ax.set_xlabel('Actions Executed')

        plt.show()

if __name__ == "__main__":
    v = VisualizeTutorialData()
    v.read_in_data()
    v.compute_average_run()
    v.graph_data()
