from xml.parsers.expat import model

from ortools.sat.python import cp_model
from .models import Teacher, SubjectAllocation


def generate_timetable():

    model = cp_model.CpModel()

    allocations = SubjectAllocation.objects.select_related(
        "teacher", "subject", "class_ref"
    )

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    hours = range(1, 9)

    timeslots = [(d, h) for d in days for h in hours]

    assignments = {}

    # Create decision variables
    for a in allocations:
        for (d, h) in timeslots:
            assignments[(a.id, d, h)] = model.NewBoolVar(
                f"a{a.id}{d}{h}"
            )

    # =====================================
    # 1️⃣ Weekly Hours Constraint
    # =====================================
    for a in allocations:

        if a.mode == 'REG':

            model.Add(

            sum(assignments[(a.id, d, h)] for (d, h) in timeslots) == a.subject.weekly_hours
            )
        else:


            model.Add(
                sum(assignments[(a.id, d, h)] for (d, h) in timeslots)
                ==0
            )
    # =====================================
    # 2️⃣ One Subject Per Class Per Slot
    # =====================================
    class_ids = set(a.class_ref_id for a in allocations)

    for c in class_ids:
        for (d, h) in timeslots:
            model.Add(
                sum(
                    assignments[(a.id, d, h)]
                    for a in allocations
                    if a.class_ref_id == c
                ) == 1
            )

    # =====================================
    # 3️⃣ Teacher Clash Constraint
    # =====================================
    teacher_ids = set(a.teacher_id for a in allocations)

    for t in teacher_ids:
        for (d, h) in timeslots:
            model.Add(
                sum(
                    assignments[(a.id, d, h)]
                    for a in allocations
                    if a.teacher_id == t
                ) <= 1
            )


    # Teacher gap only for REG subjects (not labs)
    for t in teacher_ids:
        for d in days:
            for h in range(1, 8):

                model.Add(
                    sum(
                    assignments[(a.id, d, h)]
                    for a in allocations
                    if a.teacher_id == t
                    and "LAB" not in a.subject.subject_name.upper()
                )
                +
                    sum(
                    assignments[(a.id, d, h+1)]
                    for a in allocations
                    if a.teacher_id == t
                    and "LAB" not in a.subject.subject_name.upper()
                )
                <= 1
            )

 # 4️⃣ LAB MODELLING (STRICT 3-HOUR BLOCK)
# =====================================

    lab_blocks = {}  # store block variables per (allocation, day)

    for a in allocations:
        if "LAB" in a.subject.subject_name.upper():

            weekly_block_vars = []

            for d in days:

                valid_starts = [1, 2, 5, 6]  # no lunch crossing
                start_vars = []

                for start in valid_starts:
                    start_var = model.NewBoolVar(f"lab_{a.id}{d}{start}")
                    start_vars.append(start_var)
                    weekly_block_vars.append(start_var)

                # If block chosen → force 3 consecutive hours
                    model.Add(assignments[(a.id, d, start)] == 1).OnlyEnforceIf(start_var)
                    model.Add(assignments[(a.id, d, start+1)] == 1).OnlyEnforceIf(start_var)
                    model.Add(assignments[(a.id, d, start+2)] == 1).OnlyEnforceIf(start_var)

                lab_blocks[(a.id, d)] = start_vars

        # Exactly ONE block in entire week
            model.Add(sum(weekly_block_vars) == 1)

    # 5️⃣ Only ONE lab per class per day
# =====================================

    for c in class_ids:
        for d in days:

            blocks_today = []

            for a in allocations:
                if (
                    a.class_ref_id == c and
                "LAB" in a.subject.subject_name.upper()
            ):
                    blocks_today.extend(lab_blocks[(a.id, d)])

            model.Add(sum(blocks_today) <= 1)
            



# 7️⃣ Lab days must not be consecutive
# =====================================

    day_index = {days[i]: i for i in range(len(days))}

    for c in class_ids:

        # store lab_day bools for this class
        lab_day_vars = {}

        for d in days:

            blocks_today = []

            for a in allocations:
                if (
                a.class_ref_id == c and
                "LAB" in a.subject.subject_name.upper()
            ):
                 blocks_today.extend(lab_blocks[(a.id, d)])

            lab_day = model.NewBoolVar(f"lab_day_consecutive_{c}_{d}")
            lab_day_vars[d] = lab_day

            model.Add(sum(blocks_today) >= 1).OnlyEnforceIf(lab_day)
            model.Add(sum(blocks_today) == 0).OnlyEnforceIf(lab_day.Not())

    # Now forbid consecutive days
        for i in range(len(days) - 1):
            d1 = days[i]
            d2 = days[i + 1]

            model.Add(lab_day_vars[d1] + lab_day_vars[d2] <= 1)






    # 6️⃣ If lab exists on day → no placement/SIG
# =====================================

    for c in class_ids:
        for d in days:

            blocks_today = []

            for a in allocations:
                if (
                a.class_ref_id == c and
                "LAB" in a.subject.subject_name.upper()
            ):
                    blocks_today.extend(lab_blocks[(a.id, d)])

            lab_day = model.NewBoolVar(f"lab_day_{c}_{d}")

            model.Add(sum(blocks_today) >= 1).OnlyEnforceIf(lab_day)
            model.Add(sum(blocks_today) == 0).OnlyEnforceIf(lab_day.Not())

            for a in allocations:
                if (
                a.class_ref_id == c and
                (
                    "PLACEMENT" in a.subject.subject_name.upper()
                    or "SIG" in a.subject.subject_name.upper()
                    or "ACTIVITY" in a.subject.subject_name.upper()
                )
            ):
                    for h in hours:
                        model.Add(assignments[(a.id, d, h)] == 0).OnlyEnforceIf(lab_day)



# 8️⃣ Max 2 hours per subject per day
# =====================================

    for a in allocations:
        if (
        "LAB" not in a.subject.subject_name.upper()
        and a.subject.subject_code != "PBCST404"
    ):
            for d in days:
                model.Add(
                    sum(assignments[(a.id, d, h)] for h in hours)
                <= 2
            )


# 9️⃣ Library / Placement / SIG only in afternoon
# =====================================

    # 10️⃣ Library / Placement / SIG only in 7th & 8th hour
# =====================================
    for a in allocations:
        if (
        "LIBRARY" in a.subject.subject_name.upper()
        or "PLACEMENT" in a.subject.subject_name.upper()
        or "SIG" in a.subject.subject_name.upper()
    ):
            for d in days:
                for h in range(1, 7):  # Block hours 1–6
                    model.Add(assignments[(a.id, d, h)] == 0)

    

    solver = cp_model.CpSolver()
    status = solver.Solve(model)


    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:

        structured = {d: {h: "" for h in hours} for d in days}

        for a in allocations:
          for (d, h) in timeslots:
            if solver.Value(assignments[(a.id, d, h)]) == 1:
                structured[d][h] = f"{a.subject.subject_name} ({a.teacher.teacher_name})"

        return structured

    else:
        return None