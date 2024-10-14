import os
import csv
from collections import defaultdict
from pathlib import Path

class CompleteGraph:
    def __init__(self, pairs):
        self.pairs = pairs

    def construct(self):
        graph = defaultdict(set)
        for pair1 in self.pairs:
            for pair2 in self.pairs:
                if pair1 != pair2:
                    graph[f"{pair1[0]} {pair1[1]}"].add(f"{pair2[0]} {pair2[1]}")
        return graph

class GraphProcessor:
    def __init__(self):
        self.graph_data = defaultdict(set)
        self.color_map = {}
        self.color_node_map = defaultdict(set)
        self.color_usage = defaultdict(int)
        self.total_colors = 0

    def merge_graphs(self, graph_data):
        for kv in graph_data.items():
            complete_graph = CompleteGraph(kv[1])
            graph = complete_graph.construct()
            self.merge(graph)
        self.color_graph()

    def merge(self, new_graph):
        for node, neighbors in new_graph.items():
            self.graph_data[node].update(neighbors)

    def color_graph(self):
        degrees = [(node, len(neighbors)) for node, neighbors in self.graph_data.items()]
        degrees.sort(key=lambda x: x[1], reverse=True)

        used_colors = set()

        for node, _ in degrees:
            color = 1
            for neighbor in self.graph_data[node]:
                if neighbor in self.color_map:
                    used_colors.add(self.color_map[neighbor])

            while color in used_colors:
                color += 1

            self.color_map[node] = color
            self.color_node_map[color].add(node)
            self.color_usage[color] += 1
            used_colors.clear()

    def print_color_map(self):
        print("Color Node Map:")
        for color, nodes in self.color_node_map.items():
            print(f"Color {color}: ", ' '.join(nodes))

        print("\nColor Usage:")
        for color, usage in self.color_usage.items():
            print(f"Color {color} used {usage} times")

class TeacherSubjects:
    def __init__(self, filename):
        self.filename = filename
        self.sections = []
        self.teacher_subjects = defaultdict(list)

    def process_file(self):
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            self.sections = next(reader)[1:]  # Skip first entry for sections
            for row in reader:
                teacher_id = int(row[0])
                subjects = row[1:]
                for sec, sub in zip(self.sections, subjects):
                    if sub:
                        self.teacher_subjects[teacher_id].append((sec, sub))

    def get_teacher_subjects_map(self):
        return self.teacher_subjects

    def print_results(self):
        for teacher, subjects in self.teacher_subjects.items():
            print(f"Teacher {teacher} teaches subjects: ", ' '.join(f"{sec}-{sub}" for sec, sub in subjects))

class TimeTableGenerator:
    def __init__(self):
        self.tot_slots = 15
        self.slots = defaultdict(list)

    def populate_slots_manually(self, sections):
        subjects = ["Math", "English", "History", "Chemistry", "Physics"]
        for sec in sections:
            for i in range(1, self.tot_slots + 1):
                subject = subjects[(i - 1) % len(subjects)]
                self.slots[sec].append((i, subject))

    def write_timetable_to_csv(self, sections):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        slots_per_day = self.tot_slots // len(days)

        os.makedirs("timetables", exist_ok=True)

        for sec in sections:
            section_slots = self.slots[sec]
            filename = f"timetables/{sec}_timetable.csv"
            with open(filename, 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["Day"] + [f"Slot {i}" for i in range(1, slots_per_day + 1)])

                used_slots = 0
                for day in days:
                    row = [day]
                    for _ in range(slots_per_day):
                        if used_slots < len(section_slots):
                            row.append(section_slots[used_slots][1])
                            used_slots += 1
                        else:
                            row.append("Free")
                    writer.writerow(row)

                print(f"Timetable for section {sec} written to {filename}")

    def print_table(self, sections):
        for sec in sections:
            print(f"Section {sec}: ", ' '.join(f"{slot[0]}-{slot[1]}" for slot in self.slots[sec]))

    def generate_timetable(self, graph_processor, sections):
        color_node_map = graph_processor.color_node_map

        # Initialize slots
        for sec in sections:
            self.slots[sec] = [(i, "free") for i in range(1, self.tot_slots + 1)]

        current_slot = 0

        for color, nodes in color_node_map.items():
            for node in nodes:
                section, subject = node.split(" ", 1)
                while self.slots[section][current_slot][1] != "free":
                    current_slot = (current_slot + 1) % self.tot_slots

                self.slots[section][current_slot] = (current_slot + 1, subject)
                current_slot = (current_slot + 1) % self.tot_slots

        self.print_table(sections)

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def authenticate(self, entered_username, entered_password):
        return (entered_username == self.username) and (entered_password == self.password)

class Auth:
    is_logged_in = False

    def __init__(self):
        self.current_user = None
        self.users = self.read_user_data_from_csv("user.csv")

    def read_user_data_from_csv(self, filename):
        users = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                users.append(User(row[0], row[1], row[2]))
        return users

    def display_auth(self):
        if self.is_logged_in:
            print("User already logged in. Logout first.")
            return

        print("===== Login Page =====")
        entered_username = input("Enter username: ")
        entered_password = input("Enter password: ")

        for user in self.users:
            if user.authenticate(entered_username, entered_password):
                print(f"Login successful! Role: {user.role}")
                self.current_user = user
                self.is_logged_in = True
                return

        print("Login failed. Invalid username or password.")

    def logout(self):
        if self.is_logged_in:
            self.current_user = None
            self.is_logged_in = False
            print("Logout successful!")
        else:
            print("No user is currently logged in.")

def main():
    auth = Auth()
    graph_processor = GraphProcessor()
    teacher_subjects = TeacherSubjects("teacher_data.csv")
    time_table_generator = TimeTableGenerator()

    # Process the teacher subjects file
    teacher_subjects.process_file()
    sections = list(teacher_subjects.teacher_subjects.values())[0]  # Just to get sections

    # Display login page
    auth.display_auth()

    if auth.is_logged_in:
        role = auth.current_user.role

        while True:
            print("========== TimeTable Generator Menu ==========")
            if role == "hod":
                print("1. View Timetable\n2. Approve Timetable\n3. View Report\n4. Logout")
            elif role == "admin":
                print("1. Generate Timetable\n2. Update Timetable\n3. View Report\n4. Logout")
            else:
                print("1. View Timetable\n2. Logout")

            choice = int(input("Enter your choice (1-4): "))

            if choice == 1:
                if role in ["hod", "teacher"]:
                    time_table_generator.print_table(sections)
                elif role == "admin":
                    graph_processor.merge_graphs(teacher_subjects.get_teacher_subjects_map())
                    time_table_generator.generate_timetable(graph_processor, sections)
                    time_table_generator.write_timetable_to_csv(sections)

            elif choice == 2:
                if role == "hod":
                    # Implement approval logic here
                    print("Approval logic not implemented.")
                elif role == "admin":
                    # Implement update logic here
                    print("Update logic not implemented.")

            elif choice == 3:
                graph_processor.print_color_map()

            elif choice == 4:
                auth.logout()
                print("Exiting TimeTable Generator. Goodbye!")
                return

            else:
                print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
