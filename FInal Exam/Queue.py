import queue

# queue object
my_queue = queue.Queue()

# element 
my_queue.put("First element")

# Pop 
first_element = my_queue.get()

# Print
print(first_element)
