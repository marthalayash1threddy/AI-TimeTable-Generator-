import random

# Constants
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS_PER_DAY = 7  # study periods per day
PERIOD_TIMES = ["8:00-8:55", "9:00-9:55", "10:00-10:45", "11:15-12:10",
                "12:10-1:05", "2:00-2:55", "3:00-3:55"]
BREAKS = {2: "Break", 5: "Lunch"}  # slots for morning and lunch break

# Input function
def get_section_input(section_name, include_teacher=True, default_teachers=None):
    print(f"\n[Input for {section_name}]")
    subjects = []
    n_subjects = int(input(f"How many subjects for {section_name}: "))
    for i in range(n_subjects):
        print(f"\nSubject {i+1}:")
        name = input("  Subject name: ")
        if include_teacher:
            teacher = input("  Teacher name: ")
        else:
            teacher = default_teachers[i]
        classes = int(input("  Number of classes per week: "))
        labs = int(input("  Number of labs per week: "))
        subjects.append({"name": name, "teacher": teacher, "classes": classes, "labs": labs})
    return subjects

# Function to calculate total hours
def total_hours(subjects):
    return sum(sub["classes"] + sub["labs"]*2 for sub in subjects)

# Timetable generation
def generate_timetable(subjects, other_timetable=None):
    timetable = {day: [""]*PERIODS_PER_DAY for day in DAYS}
    teacher_slots = {sub["teacher"]: {day: [] for day in DAYS} for sub in subjects}

    # Flatten class and lab allocations
    class_list = []
    lab_list = []
    for sub in subjects:
        class_list += [{"name": sub["name"], "teacher": sub["teacher"]}] * sub["classes"]
        lab_list += [{"name": sub["name"] + " (Lab)", "teacher": sub["teacher"]}] * sub["labs"]

    random.shuffle(class_list)
    random.shuffle(lab_list)

    # Determine which day is full 7-hour day
    full_day = random.choice(DAYS)
    partial_days = [d for d in DAYS if d != full_day]

    # Assign regular classes
    for cls in class_list:
        assigned = False
        days_priority = [full_day] + partial_days
        for day in days_priority:
            subjects_today = [s.replace(" (Lab)","") for s in timetable[day] if s]
            if cls["name"] in subjects_today:
                continue
            for slot in range(PERIODS_PER_DAY):
                if slot in BREAKS:
                    continue
                # Check teacher clash with other section
                if other_timetable:
                    if other_timetable[day][slot] != "":
                        other_teacher = next((sub["teacher"] for sub in subjects if other_timetable[day][slot].startswith(sub["name"])), None)
                        if other_teacher == cls["teacher"]:
                            continue
                if timetable[day][slot] == "" and slot not in teacher_slots[cls["teacher"]][day]:
                    timetable[day][slot] = cls["name"]
                    teacher_slots[cls["teacher"]][day].append(slot)
                    assigned = True
                    break
            if assigned:
                break

    # Assign labs (1 per day, 2 consecutive periods)
    for lab in lab_list:
        assigned = False
        random.shuffle(DAYS)
        for day in DAYS:
            # Skip if lab already scheduled this day
            if any(lab["name"] in s for s in timetable[day]):
                continue
            for slot in range(PERIODS_PER_DAY-1):
                if slot in BREAKS or slot+1 in BREAKS:
                    continue
                if other_timetable:
                    if any(other_timetable[day][s] != "" and 
                           next((sub["teacher"] for sub in subjects if other_timetable[day][s].startswith(sub["name"])), None) == lab["teacher"]
                           for s in [slot, slot+1]):
                        continue
                if timetable[day][slot] == "" and timetable[day][slot+1] == "":
                    timetable[day][slot] = lab["name"]
                    timetable[day][slot+1] = lab["name"]
                    teacher_slots[lab["teacher"]][day].extend([slot, slot+1])
                    assigned = True
                    break
            if assigned:
                break
    return timetable

# Timetable printing
def print_timetable(timetable, subjects, section_name):
    print(f"\nTimetable for {section_name}:\n")
    print(f"{'Time':<12}", end="")
    for p in range(PERIODS_PER_DAY):
        if p in BREAKS:
            print(f"{BREAKS[p]:<15}", end="")
        else:
            print(f"{PERIOD_TIMES[p]:<15}", end="")
    print()
    for day in DAYS:
        print(f"{day:<12}", end="")
        for slot in range(PERIODS_PER_DAY):
            if slot in BREAKS:
                if BREAKS[slot] == "Break":
                    print(f"10:45-11:15   ", end="")
                elif BREAKS[slot] == "Lunch":
                    print(f"1:05-2:00     ", end="")
            else:
                print(f"{timetable[day][slot]:<15}", end="")
        print()
    print("\nTeachers:")
    for sub in subjects:
        print(f"{sub['name']}: {sub['teacher']}")

# Main
def main():
    section_a_subjects = get_section_input("Section-A")
    total_week_hours = total_hours(section_a_subjects)
    if total_week_hours > 35:
        print(f"Warning: Total weekly hours {total_week_hours} exceed 35 hours/week.")

    same_input = int(input("\nInputs are same for Section-B also? (0 for yes, 1 for no): "))
    if same_input == 0:
        section_b_subjects = section_a_subjects
    else:
        default_teachers = [sub["teacher"] for sub in section_a_subjects]
        section_b_subjects = get_section_input("Section-B", include_teacher=False, default_teachers=default_teachers)

    timetable_a = generate_timetable(section_a_subjects)
    timetable_b = generate_timetable(section_b_subjects, other_timetable=timetable_a)

    print_timetable(timetable_a, section_a_subjects, "Section-A")
    print_timetable(timetable_b, section_b_subjects, "Section-B")

if __name__ == "__main__":
    main()
