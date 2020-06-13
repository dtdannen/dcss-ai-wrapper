"""

Setup crawl server for RL agents

"""
import shlex, subprocess
import sys, traceback

def main():
	try:
		#TODO these should really be from the command line
		num_instances=1
		num_episodes=100
		num_games = num_instances*num_episodes

		#create an array of commands for each train/test playthrough, should really get them from command line
		command = "./crawl -name midca -seed {0} -rc .rcs/midca.rc -macro ./rcs/midca.macro -morgue ./rcs/midca -webtiles-socket ./rcs/midca:test.sock -await-connection"
		commands = [command.format("01")] * (num_episodes)
		commands.append(command.format("03"))
		commands.append(command.format("03"))
		p = None
#		TODO we may want to train many instances of the same agent, this is placeholder for that idea
#		instances = commands*num_instances
#		for commands in instances:
		episode_counter = 1
		for command in commands:
			working_directory = "./crawl/crawl-ref/source/"

			#fancy command line arg splitting to make subprocess easy
			args = shlex.split(command)

			print("Starting episode: " + str(episode_counter))
			print(command)
			
			#start the server and wait until it is finished, clean it up when done, otherwise you end up with zombies
			p = subprocess.Popen(args, cwd=working_directory)
			p.wait()
			p.kill()
			
			episode_counter += 1
	#catch the exceptiosn so we can exit gracefully without zombies
	except KeyboardInterrupt:
		print("Shutdown requested...exiting")
		p.kill()
	except Exception:
		p.kill()
		traceback.print_exc(file=sys.stdout)
	sys.exit(0)

if __name__ == "__main__":
	#TODO should pass command line args and print usage
    main()