import pandas as pd
import random
import os
import logging

# Set up logging
logging.basicConfig(filename='scheduler.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Define the number of employees and their names
num_employees = 6
employee_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley"]

class Employee:
    def __init__(self, employee_id, name):
        # Initialize employee with ID and name
        self.id = employee_id
        self.name = name
        self.schedule = {}
        self.total_hours = 0
    
    def set_schedule(self, schedule):
        # Set the employee's schedule and calculate total hours
        self.schedule = schedule
        self.total_hours = sum(6 for shift in schedule.values() if shift != "Rest")

class Schedule:
    def __init__(self, employees):
        # Initialize schedule with a list of employees
        self.employees = {emp.id: emp for emp in employees}
        self.shift_hours = 6  # Each shift is 6 hours
        self.shifts = ["11 am - 5 pm", "6 pm - 12 am"]
        self.hourly_wage = 15  # Wage per hour
        self.schedule_df = pd.DataFrame(columns=["ID", "Name", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Total Hours"])

    def create_schedule(self):
        # Create a random schedule for each employee
        for employee in self.employees.values():
            work_days = random.sample(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 5)
            rest_days = [day for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if day not in work_days]
            schedule = {day: "Rest" if day in rest_days else random.choice(self.shifts) for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
            employee.set_schedule(schedule)
            # Add employee's schedule to the DataFrame
            self.schedule_df = pd.concat([self.schedule_df, pd.DataFrame([{
                "ID": employee.id,
                "Name": employee.name,
                **employee.schedule,
                "Total Hours": employee.total_hours
            }])], ignore_index=True)
    
    def export_schedule(self, employee_id=None):
        # Export schedule to an Excel file
        output_directory = "schedules"
        os.makedirs(output_directory, exist_ok=True)
        
        if employee_id:
            # Export individual schedule if employee ID is specified
            employee = self.employees.get(employee_id)
            if not employee:
                return f"Employee with ID {employee_id} not found."
            
            individual_schedule = self.schedule_df[self.schedule_df["ID"] == employee_id]
            file_path = os.path.join(output_directory, f"employee_{employee_id}_schedule.xlsx")
            individual_schedule.to_excel(file_path, index=False)
            logging.info(f"Exported schedule for employee {employee_id} to {file_path}")
            return f"Schedule for employee {employee_id} exported to {file_path}"
        
        # Export full schedule
        file_path = os.path.join(output_directory, "employee_schedule.xlsx")
        self.schedule_df.to_excel(file_path, index=False)
        logging.info("Exported full schedule")
        return f"Full schedule exported to {file_path}"
    
    def calculate_wages(self):
        # Calculate wages for each employee and export to an Excel file
        self.schedule_df["Wages"] = self.schedule_df["Total Hours"] * self.hourly_wage
        file_path = os.path.join("schedules", "employee_wages.xlsx")
        self.schedule_df.to_excel(file_path, index=False)
        logging.info("Exported wage report")
        return f"Wage report exported to {file_path}"
    
    def mark_absence(self, employee_id, day, status):
        # Mark an employee's absence
        employee = self.employees.get(employee_id)
        if not employee:
            return f"Employee with ID {employee_id} not found."
        
        day = day.capitalize()
        if day not in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            return "Invalid day. Use a valid weekday name."
        
        if status not in ["out", "in", "full out"]:
            return "Invalid status. Use 'out', 'in', or 'full out'."
        
        if status == "full out":
            # Mark all days as absent and reduce total hours accordingly
            for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                if employee.schedule[d] != "Rest" and employee.schedule[d] != "Absent":
                    employee.total_hours -= 6
                employee.schedule[d] = "Absent"
        else:
            # Mark specific day as absent or working and adjust total hours
            if status == "out" and employee.schedule[day] != "Rest" and employee.schedule[day] != "Absent":
                employee.schedule[day] = "Absent"
                employee.total_hours -= 6
            elif status == "in" and employee.schedule[day] == "Absent":
                employee.schedule[day] = random.choice(self.shifts)
                employee.total_hours += 6
        
        # Update the schedule DataFrame and recalculate wages
        self.schedule_df.loc[self.schedule_df["ID"] == employee_id, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]] = [employee.schedule[d] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
        self.schedule_df.loc[self.schedule_df["ID"] == employee_id, "Total Hours"] = employee.total_hours
        self.schedule_df.loc[self.schedule_df["ID"] == employee_id, "Wages"] = employee.total_hours * self.hourly_wage

        file_path = os.path.join("schedules", "employee_schedule.xlsx")
        self.schedule_df.to_excel(file_path, index=False)
        logging.info(f"Updated absence status for employee {employee_id} on {day} to {status}")
        return f"Absence status for employee {employee_id} updated. Schedule exported to {file_path}"

class SchedulerSystem:
    def __init__(self, schedule):
        # Initialize the scheduler system with a Schedule object
        self.schedule = schedule
    
    def run(self):
        # Main loop to handle user input
        while True:
            user_input = input("Enter a command (e.g., 'schedule id 1', 'schedule report', 'calculate wages', 'mark absence <id> <day> <status>', or 'exit' to quit): ").strip().lower()
            
            if user_input.startswith("schedule id "):
                try:
                    # Export individual schedule
                    employee_id = int(user_input.split("schedule id ")[1])
                    print(self.schedule.export_schedule(employee_id))
                except (IndexError, ValueError) as e:
                    print(f"Invalid input: {e}")
            
            elif user_input == "schedule report":
                # Export full schedule
                print(self.schedule.export_schedule())
            
            elif user_input == "calculate wages":
                # Calculate and export wages
                print(self.schedule.calculate_wages())
            
            elif user_input.startswith("mark absence "):
                try:
                    # Mark absence for an employee
                    parts = user_input.split(" ")
                    employee_id = int(parts[2])
                    day = parts[3]
                    status = parts[4]
                    print(self.schedule.mark_absence(employee_id, day, status))
                except (ValueError, IndexError) as e:
                    print(f"Invalid input: {e}")
            
            elif user_input == "exit":
                # Exit the program
                print("Exiting the scheduler.")
                logging.info("Scheduler exited by user")
                break
            
            else:
                print("Invalid command. Please try again.")

# Initialize employees
employees = [Employee(i, name) for i, name in zip(range(1, num_employees + 1), employee_names)]

# Initialize and create schedule
schedule = Schedule(employees)
schedule.create_schedule()

# Run the scheduler system
scheduler_system = SchedulerSystem(schedule)
scheduler_system.run()
