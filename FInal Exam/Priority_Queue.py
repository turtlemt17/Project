import queue

# priority queue object
my_priority_queue = queue.PriorityQueue()

# element 
my_priority_queue.put((2, "Second element"))

# Pop
first_element = my_priority_queue.get()

# Print 
print(first_element)
