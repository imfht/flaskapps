# cfe.sh/github -> 30 Day of Python -> Day 27
import time

iteration_times = [1, 3, 2, 4]

def sleeper(seconds, i=-1):
    start_time = time.time()
    if i != -1:
        print(f"{i}\t{seconds}s")
    time.sleep(seconds)
    return time.time() - start_time

run_time = 0
def main():
    global run_time
    for i, second in enumerate(iteration_times):
        run_time += sleeper(second, i=i)
main()
print(f"Ran for {run_time} seconds")