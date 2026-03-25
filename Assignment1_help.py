import threading
import time
import random

from printDoc import printDoc
from printList import printList

class Assignment1:
    # Simulation Initialisation parameters
    NUM_MACHINES = 50        # Number of machines that issue print requests
    NUM_PRINTERS = 5         # Number of printers in the system
    SIMULATION_TIME = 30     # Total simulation time in seconds
    MAX_PRINTER_SLEEP = 3    # Maximum sleep time for printers
    MAX_MACHINE_SLEEP = 5    # Maximum sleep time for machines

    # Initialise simulation variables
    def __init__(self):
        self.sim_active = True
        self.print_list = printList()  # Create an empty list of print requests
        self.mThreads = []             # list for machine threads
        self.pThreads = []             # list for printer threads
        
        # Create semaphores
        self.semaphore = threading.Semaphore(self.NUM_PRINTERS)  # counting semaphore
        self.binary = threading.Semaphore(1)#diffrerence

        self.queue_full=threading.Semaphore(self.NUM_PRINTERS)#num of printers= max capacity of queue
        self.queue_empty=threading.Semaphore(0)               #wgen printer is waiting ,the queue is null
        #

    def startSimulation(self):
        # Create Machine and Printer threads
        # Write code here
        for i in range(self.NUM_MACHINES):
            t=self.machineThread(i,self)
            self.mThreads.append(t)

        for i in range(self.NUM_PRINTERS):
            t = self.printerThread(i, self)
            self.pThreads.append(t)
        # Start all the threads
        # Write code here
        for t in  self.mThreads:
            t.start()
        for t in  self.pThreads:
            t.start()

        # Let the simulation run for some time
        time.sleep(self.SIMULATION_TIME)

        # Finish simulation
        self.sim_active = False

        # Wait until all printer threads finish by joining them
        # Write code here
        for t in self.pThreads:
            t.join()
        print("Simulation finished.")
        # We won't join machine threads as they may be in busy waiting.
        # Flush output and exit.

    # Printer class
    class printerThread(threading.Thread):
        def __init__(self, printerID, outer):
            threading.Thread.__init__(self)
            self.printerID = printerID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                # Simulate printer taking some time to print the document
                self.printerSleep()#task1
                # Grab the request at the head of the queue and print it
                # Write code here
                self.outer.queue_empty.acquire()
                self.printDox(self.printerID)#task1 print
                self.outer.queue_full.release()


                

        def printerSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_PRINTER_SLEEP)
            time.sleep(sleepSeconds)

        def printDox(self, printerID):
            print(f"Printer ID: {printerID} : now available")#add lock
            #Write code here for Binary and counting Semaphore
            # Acquire the binary semaphore to ensure mutual exclusion
            self.outer.binary.acquire()

            # Print from the queue
            self.outer.print_list.queuePrint(printerID)
            # Release the binary semaphore
            self.outer.binary.release()
            # Increment the semaphore count so that machines can send requests




    # Machine class
    class machineThread(threading.Thread):
        def __init__(self, machineID, outer):
            threading.Thread.__init__(self)
            self.machineID = machineID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                # Machine sleeps for a random amount of time
                self.machineSleep()
                # Machine wakes up and sends a print request
                # Write code here
                
                # Check if it is safe to send a request by acquiring semaphores
                self.isRequestSafe(self.machineID)
                # Both semaphores have been acquired, now send a print request
                self.printRequest(self.machineID)
                # Release the binary semaphore after inserting the print request
                self.postRequest(self.machineID)#task1 request directly there check send release

        def machineSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_MACHINE_SLEEP)
            time.sleep(sleepSeconds)
        
        # Write code here for Acquiring the Counting Semaphore
        def isRequestSafe(self, id):
            print(f"Machine {id} Checking availability")
            self.outer.queue_full.acquire()#defend cover
            # Acquire counting semaphore (wait for an available printer)
            self.outer.semaphore.acquire()
            # Acquire binary semaphore for mutual exclusion of the print queue
            self.outer.binary.acquire()
            # Both semaphores acquired
            print(f"Machine {id} will proceed")
        
        def printRequest(self, id):
            print(f"Machine {id} Sent a print request")
            # Build a print document
            doc = printDoc(f"My name is machine {id}", id)
            # Insert it in the print queue
            self.outer.print_list.queueInsert(doc)

        # Write code here for postRequest, i.e., after inserting the print request
        def postRequest(self, id):#release queue lock
            print(f"Machine {id} Releasing binary semaphore")
            # Release the binary semaphore
            self.outer.binary.release()

            self.outer.queue_empty.release()