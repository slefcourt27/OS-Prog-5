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
            "runtime": p["runtime"],
            "failure": 0
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
    failureRemaining = -1

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
        # Set arrival flag
        if len(arrived) > 0:
            pArrived = True

        # Check if current process has finished / idle
        if processes[current_process]["remaining"] <= 0:
           print("Remaining: ", remaining_processes)
           # Process has just finished
           if processes[current_process]["remaining"] == 0:
               pCompleted = True
               pCompletedPID = current_process
               print("Process ", current_process, "has finished at time ", totalTime)
               # Set remaining to -1
               processes[current_process]["remaining"] = -1

           # Check if there are any other processes remaining
           # If so, set new current process
           if len(remaining_processes) > 0:
               print("Getting new current process")
               current_process = remaining_processes.pop(0)
        # For each process that has arrived
        for pid in arrived:
            # Check for failure
            if processes[pid]["remaining"] > 0 and totalTime != 0:
                print("Remaining: ", processes[pid]["remaining"])
                # Set failure PID
                pFail = pid
                # Set failure remaining
                failureRemaining = processes[pid]["remaining"]
                print("Failure")

            # Reset if no failure
            else:
                processes[pid]["deadline"] = totalTime + processes[pid]["period"]
                processes[pid]["current"] += 1
                processes[pid]["remaining"] = processes[pid]["runtime"]

            # Check if current process needs to change
            if processes[pid]["period"] < processes[current_process]["period"]:
                print("Process ", pid, " is replacing ", current_process, " as current process")

                # If current process has yet to complete, add to back of remaining
                if processes[current_process]["remaining"] > 0:
                    remaining_processes.append(current_process)

                # If it has already completed, don't do anything
                # if processes[current_process]["remaining"] <= 0:
                #     print("Process ", current_process, " already finished")


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
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]+1) + " FAIL")
                    else:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]))

            w.write('\n')

            # print(pCompletedPID)
            # Write current process
            if processes[current_process]["remaining"] != -1:
                w.write("P"+str(current_process)+"-"+str(processes[current_process]["current"]) + " (" + str(processes[current_process]["period"]) + ", " +  str(processes[current_process]["remaining"]) + ")")
            w.write("\n")

            # Write all remaining processes
            iter = 0
            for idx, p in enumerate(remaining_processes):
                if pFail == p and iter == 0:
                    # Write the previous
                    w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]) + " (" + str(processes[p]["period"]) + ", " +  str(failureRemaining) + ")")
                    iter += 1
                elif pFail == p and iter == 1:
                    # Write the previous
                    w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]+1) + " (" + str(processes[p]["period"]) + ", " +  str(processes[p]["runtime"]) + ")")
                    iter += 1
                else:
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

# Sort according to earliest deadline
def edfs_sort(pid, processes):
    if processes[pid]["failure"] == 1:
        print("Failure PID ", pid)
        print("Runtime: ", processes[pid]["runtime"])
        deadline = processes[pid]["deadline"] + processes[pid]["runtime"]
        print("Deadline for failure: ", deadline)
        return deadline
    else:
        return processes[pid]["deadline"]

def edfs(processes, t, scheduling_time, w):
    # Calculate the priority based on distance to deadline is less
    # Based on the priority, loop through all processes
    totalTime = 0
    remaining_processes = [] # Store the pid
    print("EDFS")

    arrivals = []
    for p in processes:
        arrivals.append( (processes[p]["pid"], processes[p]["period"]) )

    current_process = list(processes.keys())[0]

    while totalTime <= t:
        print(totalTime)
        print(current_process)
        print(remaining_processes)
        pArrived = False
        pCompleted = False

        pFail = -1
        failureRemaining = -1
        failureDeadline = -1
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
            # FAILURE
            if processes[pid]["remaining"] > 0 and totalTime != 0:
                processes[pid]["failure"] = 1

                failureDeadline = processes[pid]["deadline"]
                failureRemaining = processes[pid]["remaining"]
                pFail = pid

                # Problem is that when we sort, it will have the same deadline as previous one..
                new_deadline = totalTime + processes[pid]["runtime"]
                new_remaining = processes[pid]["runtime"]
                remaining_processes.append(pid)

            else:
                # Reset before appending to remaining
                processes[pid]["deadline"] = totalTime + processes[pid]["period"]
                processes[pid]["current"] += 1
                processes[pid]["remaining"] = processes[pid]["runtime"]

                if pid is not current_process:
                    remaining_processes.append(pid)

        # If new processes arrived, need to sort by closest deadline
        if len(arrived) > 0:
            # Create custom sort class to handle when fail case
            remaining_processes.sort(key=lambda pid: edfs_sort(pid, processes))

        if pFail != -1:
            print("Remaining after sort: ", remaining_processes)

        # Check sorting cond later
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
                remaining_processes.sort(key=lambda pid: processes[pid]["deadline"])

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
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]+1) + " FAIL")
                    else:
                        w.write(' P' + str(pid) + '-' + str(processes[pid]["current"]))

            w.write('\n')

            # print(pCompletedPID)
            # Write current process
            if processes[current_process]["remaining"] != -1:
                w.write("P"+str(current_process)+"-"+str(processes[current_process]["current"]) + " (" + str(processes[current_process]["deadline"]) + ", " +  str(processes[current_process]["remaining"]) + ")")
            w.write("\n")

            # Write all remaining processes
            iter = 0

            # Check if the failure is in the remaining processes twice
            # If it is only there once, then only need to do one check
            # Check # times process failure is in remaining
            occurences = remaining_processes.count(pFail)

            print("About to print: ", remaining_processes)
            for idx, p in enumerate(remaining_processes):
                if occurences == 2 and pFail == p:
                    if iter == 0:
                        # Write the current
                        # Check which current should be here
                        w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]) + " (" + str(processes[p]["deadline"]) + ", " +  str(failureRemaining) + ")")
                        iter += 1
                    if iter == 1:
                        # Write the fail
                        w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]+1) + " (" + str(processes[p]["deadline"] + processes[p]["deadline"]) + ", " +  str(processes[p]["runtime"]) + ")")
                        iter += 1
                if occurences == 1 and pFail == p:
                    w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]+1) + " (" + str(processes[p]["deadline"] + processes[p]["deadline"]) + ", " +   str(processes[p]["runtime"]) + ")")
                    iter += 1
                else:
                    w.write("P"+str(processes[p]["pid"])+"-"+str(processes[p]["current"]) + " (" + str(processes[p]["deadline"]) + ", " +  str(processes[p]["deadline"]) + ")")


                if idx + 1 != len(remaining_processes):
                    w.write(" ")

            w.write("\n")

        if pFail != -1:
            return

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
