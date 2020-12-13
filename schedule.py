import sys
import copy


# Rate monotonic scheduling
def rms(num_processes, processes, t, w):
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
        utilization += p["runtime"] / p["period"]

    able_to_schedule = int(utilization < threshold)
    # print("Able to schedule: ", type(able_to_schedule))


    arrivals = []
    # print(processes.items())
    # processes = sorted(processes.items(), key=lambda x: x['period'])

    for p in processes:
        arrivals.append( (p["pid"], p["period"]) )

    current_process = copy.deepcopy(processes[0])

    pArrived = False
    pCompleted = False
    completed_processes = []
    processes_arrived = []
    pFail = False
    idle = False

    while totalTime <= t:
        arrived = []
        completed_processes = []
        processes_arrived = []
        pArrived = False
        pCompleted = False
        pFail = False

        # Get all arrivals for this time
        for pid, period in arrivals:
            # Process arrived
            if totalTime % period == 0:
                arrived.append(pid)

        # Set arrival flag
        if len(arrived) > 0:
            pArrived = True

        # Check if current process has finished / idle
        if current_process["remaining"] == 0:
            pCompleted = True
            print("Current process completed")
            completed_processes.append( copy.deepcopy(current_process) )
            print("Processes completed: ", completed_processes)
            current_process["remaining"] = -1
            idle = True

        if current_process["remaining"] == -1 and len(remaining_processes) > 0:
           # Check if there are any other processes remaining
           # If so, set new current process
           current_process = remaining_processes.pop(0)
           idle = False

        # For each process that has arrived
        for pid in arrived:
            # Get first item with this pid in remaining processes
            res = next((item for item in remaining_processes if item["pid"] == pid), False)

            if res != False:
                # A previous object with this pid still exists and has not finished
                # Failure
                print("Fail at time ", totalTime)

                print("Process: ", res)
                pFail = True

            elif current_process["pid"] == pid and idle == False and totalTime is not 0:
                # Current process is not idle so it is a failure
                print("Curr process fails at time ", totalTime)
                print("Process: ", res)
                pFail = True

            # Add to remaining
            obj = next((item for item in processes if item["pid"] == pid))
            new_obj = { "current": obj["current"], "deadline": totalTime + obj["period"], "pid": pid, "period": obj["period"],"runtime": obj["runtime"],"remaining": obj["runtime"]}
            processes_arrived.append(copy.deepcopy(new_obj))
            obj["current"] += 1

            # Don't add the current PID on time 0
            if totalTime == 0 and pid == current_process["pid"]:
                continue

            # Check if current process is idle
            if idle == True:
                current_process = copy.deepcopy(new_obj)
                idle = False
            # Check if incoming period is < current process period
            elif obj["period"] < current_process["period"]:
                # Swap
                print("Swapping time ", totalTime)
                remaining_processes.append(copy.deepcopy(current_process))
                print("Remaining: ", remaining_processes)
                current_process = copy.deepcopy(new_obj)
            else:
                remaining_processes.append(copy.deepcopy(new_obj))


        # Sort by smallest period
        remaining_processes.sort(key=lambda p: p["period"])


        # Write arrivals to file
        if pCompleted or pArrived:
            # Time
            print("Time: ", totalTime)
            print("Completed: ", pCompleted)
            print("Processes completed: ", completed_processes)
            print("Arrived: ", pArrived)
            print("Remaining: ", remaining_processes)
            w.write(str(totalTime))
            w.write("\n")

            # Completed processes
            for i,p in enumerate(completed_processes):
                w.write("F: P"+ str(p["pid"])+"-"+str(p["current"]))
                if i+1 != len(completed_processes):
                    w.write(" ")

            # Separating space for completed processes and arrivals
            if pCompleted and pArrived:
                w.write(" ")

            # Write all arrivals
            if pArrived:
                w.write("A:")

                for p in processes_arrived:
                    w.write(' P' + str(p["pid"]) + '-' + str(p["current"]))

                if pFail == True:
                    w.write(" FAIL")

            w.write('\n')

            # Write current process
            if current_process["remaining"] != -1:
                w.write("P"+str(current_process["pid"])+"-"+str(current_process["current"]) + " (" + str(current_process["period"]) + ", " +  str(current_process["remaining"]) + ")")

            w.write("\n")

            # Write all remaining processes
            iter = 0
            for idx, p in enumerate(remaining_processes):
                w.write("P"+str(p["pid"])+"-"+str(p["current"]) + " (" + str(p["period"]) + ", " +  str(p["remaining"]) + ")")

                if idx + 1 != len(remaining_processes):
                    w.write(" ")

            w.write("\n")

            if pFail == True:
                return 1


        # Increment time and decrement remaining for process
        current_process["remaining"] -= 1
        totalTime += 1

    return able_to_schedule





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
    processes=[]
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
        processes.append({
            "current": 1,
            "deadline": p["period"],
            "remaining": p["runtime"],
            "pid": pid,
            "period": p["period"],
            "runtime": p["runtime"],
            "failure": 0
        })

    return num_processes, time_run, processes


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
    num_processes, time_run, processes = setup(f)

    p1 = copy.deepcopy(processes)
    p2 = copy.deepcopy(processes)

    able_to_schedule = rms(num_processes, p1, time_run, w)

    w.write("\n")

    # print("Able to schedule MAIN: ", able_to_schedule)
    # w.write( str(able_to_schedule) )
    #
    # w.write("\n")

    # edfs(p2, time_run, w)



    # Create file for writing output
    # output = open("output.txt", "a")


main()
