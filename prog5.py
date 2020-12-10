import sys
from math import gcd # Python versions 3.5 and above
#from fractions import gcd # Python versions below 3.5
from functools import reduce # Python version 3.x
import copy

# Find LCM for scheduling time
def lcm(denominators):
    return reduce(lambda a,b: a*b // gcd(a,b), denominators)

def setup(f):
    # Read file
    lines = f.read().splitlines()
    print(lines)
    num_processes, time_run = lines[0].split(' ')
    num_processes = int(num_processes)
    time_run = int(time_run)
    # processes start at 1
    # keep track of number of times it has been run
    periods = []
    processes={}
    priority = []
    for i, line in enumerate(lines):
        if i == 0:
            continue


        period, runtime = line.split(' ')
        period = int(period)
        runtime = int(runtime)

        periods.append(period)
        priority.append({
            "current": 1,
            "deadline": period,
            "remaining": runtime,
            "pid": i,
            "period": period,
            "runtime": runtime
        })



    # Calculate priority using period
    # Smaller period = higher priority
    priority = sorted(priority, key=lambda x: x['period'])
    # print(priority)
    for p in priority:
        pid = p["pid"]
        processes[pid] = {
            "current": 0,
            "deadline": p["period"],
            "remaining": p["runtime"],
            "pid": pid,
            "period": p["period"],
            "runtime": p["runtime"]
        }

    return num_processes, time_run, processes, periods


def get_index(processes, pid):
    for idx, p in enumerate(processes):
        if p["pid"] == pid:
            return idx
    return -1

# Rate monotonic scheduling
def rms(num_processes, processes, t, scheduling_time, w):
    # Based on the priority, loop through all processes
    totalTime = 0


    # Run until stop or failure
    remaining_processes = [] # Store the pid

    # Check if it will work
    # Bonus
    n = num_processes
    threshold = n * ( 2**(1/n) - 1)
    utilization = 0

    # Exec time / Time period
    for p in processes:
        utilization += (processes[p]["runtime"] / processes[p]["period"])

    able_to_schedule = int(utilization < threshold)
    print("Able to schedule: ", type(able_to_schedule))


    arrivals = []
    # print(processes.items())
    # processes = sorted(processes.items(), key=lambda x: x['period'])
    print(processes)

    for p in processes:
        arrivals.append( (processes[p]["pid"], processes[p]["period"]) )

    current_process = list(processes.keys())[0]

    pArrived = False
    pCompleted = False
    pCompletedPID = -1
    pFail = -1

    while totalTime <= t:
        pArrived = False
        pCompleted = False

        # Get all arrivals for this time
        arrived = []
        for pid, period in arrivals:
            if totalTime % period == 0:
                print("Current time: ", totalTime)
                print("Process: ", pid, " period: ", period)
                arrived.append(pid)

        if len(arrived) > 0:
            pArrived = True

        # Check if current process has finished / idle
        if processes[current_process]["remaining"] <= 0:
           print("Remaining: ", remaining_processes)
           if processes[current_process]["remaining"] == 0:
               pCompleted = True
               pCompletedPID = current_process
               print("Process ", current_process, "has finished at time ", totalTime)
               # Current process has FINISHED, only append to completed process if remaining is 0
               # Set remaining to -1
               processes[current_process]["remaining"] = -1

           # Check if there are any other processes remaining
           if len(remaining_processes) > 0:
               print("Getting new current process")
               current_process = remaining_processes.pop(0)

        for pid in arrived:
            # Check for failure
            if processes[pid]["remaining"] > 0 and totalTime != 0:
                print("Remaining: ", processes[pid]["remaining"])
                pFail = pid
                print("Failure")
                # return

            # Reset if no failure
            processes[pid]["deadline"] = totalTime + processes[pid]["period"]
            processes[pid]["current"] += 1
            processes[pid]["remaining"] = processes[pid]["runtime"]

            # Check if process has run for necessary time
            print("Before check for finish")
            print(current_process, ": ", processes[current_process]["remaining"])
            # Check if current process needs to change
            if processes[pid]["period"] < processes[current_process]["period"]:
                print("Process ", pid, " is replacing ", current_process, " as current process")

                # If current process has yet to complete, add to back of remaining
                if processes[current_process]["remaining"] > 0:
                    remaining_processes.append(current_process)
                # If it has already completed, don't do anything
                if processes[current_process]["remaining"] <= 0:
                    print("Process ", current_process, " already finished")


                current_process = pid
            else:
                remaining_processes.append(pid)

            if processes[current_process]["remaining"] == -1 and len(remaining_processes) > 0:
                current_process = remaining_processes.pop(0)

        # Do the actual algorithm

        # Remove current pid from remaining if it exists
        if current_process in remaining_processes:
            remaining_processes.remove(current_process)

        # Write to file if process arrived or finished
        # Write arrivals to file

        # Check for priority
        if pCompleted or pArrived:
            w.write(str(totalTime))
            w.write("\n")
            use = current_process
            if pCompleted:
                # w.write("F: ")
                w.write("F: P"+str(pCompletedPID)+"-"+str(processes[pCompletedPID]["current"]))
                use = pCompletedPID

            if pCompleted and pArrived:
                w.write(" ")

            if pArrived:
            # Check if they have completed their stuff yet
                if len(arrived) > 0:
                    w.write("A:")

                for pid in arrived:
                    if pFail == pid:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]) + " FAIL")
                    else:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]))

            w.write('\n')

            # print(pCompletedPID)
            # Write current process
            if processes[current_process]["remaining"] != -1:
                w.write("P"+str(current_process)+"-"+str(processes[current_process]["current"]) + " (" + str(processes[current_process]["period"]) + ", " +  str(processes[current_process]["remaining"]) + ")")
            w.write("\n")

            # Write all remaining processes
            for idx, p in enumerate(remaining_processes):
                w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]) + " (" + str(processes[p]["period"]) + ", " +  str(processes[p]["remaining"]) + ")")
                if idx + 1 != len(remaining_processes):
                    w.write(" ")
            w.write("\n")

            if pFail != -1:
                return able_to_schedule

        # Increment time and decrement remaining for process
        print("Time: ", totalTime)
        print("Current process: ", current_process)
        print("Process ", current_process, " remaining: ", processes[current_process]["remaining"])
        processes[current_process]["remaining"] -= 1
        totalTime += 1

    return able_to_schedule

def edfs(processes, t, scheduling_time, w):
    # Calculate the priority based on distance to deadline is less
    # Based on the priority, loop through all processes
    totalTime = 0
    remaining_processes = [] # Store the pid

    arrivals = []
    for p in processes:
        arrivals.append( (processes[p]["pid"], processes[p]["period"]) )

    current_process = list(processes.keys())[0]

    while totalTime <= t:
        pArrived = False
        pCompleted = False

        pFail = -1
        pCompletedPID = -1

        arrived = []
        for pid, period in arrivals:
            if totalTime % period == 0:
                arrived.append(pid)

        if len(arrived) > 0:
            pArrived = True

        # Check if process has run for necessary time
        if processes[current_process]["remaining"] <= 0:
            # print("Remaining: ", remaining_processes)
            if processes[current_process]["remaining"] == 0:
                print("Process ", current_process, "has finished at time ", totalTime)
                pCompleted = True
                pCompletedPID = current_process
                # Current process has FINISHED, only append to completed process if remaining is 0
                # Set remaining to -1
                processes[current_process]["remaining"] = -1

            # Check if there are any other processes remaining
            if len(remaining_processes) > 0:
                # print("Getting new current process")
                current_process = remaining_processes.pop(0)

        # Check if they have completed their stuff yet
        for pid in arrived:
            print("Process ", pid, " arrived at time ", totalTime)
            if processes[pid]["remaining"] > 0 and totalTime != 0:
                pFail = pid

            else:
                # Reset before appending to remaining
                processes[pid]["deadline"] = totalTime + processes[pid]["period"]
                processes[pid]["current"] += 1
                processes[pid]["remaining"] = processes[pid]["runtime"]
                remaining_processes.append(pid)

        # If new processes arrived, need to sort by closest deadline
        if len(arrived) > 0:
            remaining_processes.sort(key=lambda pid: processes[pid]["deadline"])

        for pid in remaining_processes:
            if processes[pid]["deadline"] < processes[current_process]["deadline"] or processes[current_process]["remaining"] == -1:
                print("Process ", pid, " is replacing ", current_process, " as current process")

                if processes[current_process]["remaining"] > 0:
                    remaining_processes.append(current_process)


                if processes[current_process]["remaining"] <= 0:
                    print("Process ", current_process, " already finished")

                print(remaining_processes)
                current_process = pid
                remaining_processes.remove(current_process)

        if current_process in remaining_processes:
            remaining_processes.remove(current_process)
        if pArrived or pCompleted:
            # Current time
            w.write( str(totalTime) + "\n" )

            # Arrivals
            use = current_process

            if pCompleted:
                # w.write("F: ")
                w.write("F: P"+str(pCompletedPID)+"-"+str(processes[pCompletedPID]["current"]))
                use = pCompletedPID

            if pCompleted and pArrived:
                w.write(" ")

            if pArrived:
            # Check if they have completed their stuff yet
                if len(arrived) > 0:
                    w.write("A:")

                for pid in arrived:
                    if pFail == pid:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]) + " FAIL")
                    else:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]))

            w.write('\n')

            # print(pCompletedPID)
            # Write current process
            if processes[current_process]["remaining"] != -1:
                w.write("P"+str(current_process)+"-"+str(processes[current_process]["current"]) + " (" + str(processes[current_process]["deadline"]) + ", " +  str(processes[current_process]["remaining"]) + ")")
            w.write("\n")

            # Write all remaining processes
            for idx, p in enumerate(remaining_processes):
                w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]) + " (" + str(processes[p]["deadline"]) + ", " +  str(processes[p]["remaining"]) + ")")
                if idx + 1 != len(remaining_processes):
                    w.write(" ")
            w.write("\n")

        # Run this process once
        processes[current_process]["remaining"] = processes[current_process]["remaining"]-1
        totalTime += 1

def main():
    filename = sys.argv[1]


    try:
        # Open file for reading
        f = open('./'+filename, 'r')
    except:
        # File does not exist
        print("No file named ", filename, " in current directory")

    w = open("output.txt", "w")

    # Read in file
    num_processes, time_run, priority, periods = setup(f)

    p1 = copy.deepcopy(priority)
    p2 = copy.deepcopy(priority)

    scheduling_time = lcm(periods)
    able_to_schedule = rms(num_processes, p1, time_run,scheduling_time, w)

    w.write("\n")

    # print("Able to schedule MAIN: ", able_to_schedule)
    # w.write( str(able_to_schedule) )
    #
    # w.write("\n")

    edfs(p2, time_run,scheduling_time, w)



    # Create file for writing output
    # output = open("output.txt", "a")


main()
