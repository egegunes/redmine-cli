from datetime import datetime
from textwrap import wrap


class Journal:
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("user")
        self.created_on = kwargs.get("created_on")
        self.notes = kwargs.get("notes")
        self.details = kwargs.get("details")
        self.prefixes = {
            "assigned_to_id": "Assignee",
            "status_id": "Status",
            "start_date": "Start date",
            "due_date": "Due date",
            "parent_id": "Parent task",
            "blocks": "Blocks",
            "blocked": "Blocked by",
            "priority_id": "Priority",
            "tracker_id": "Tracker",
            "fixed_version_id": "Version",
            "done_ratio": "Done",
            "project_id": "Project",
            "description": "Description",
            "subject": "Subject",
            "relates": "Relates",
        }
        self.statuses = {str(s["id"]): s["name"] for s in kwargs.get("statuses", {})}
        self.priorities = {
            str(p["id"]): p["name"] for p in kwargs.get("priorities", {})
        }
        self.users = kwargs.get("users")

    def __repr__(self):
        return f"Journal({self.user['name']}, {self.created_on})"

    def __str__(self):
        return self.get_header() + self.get_notes() + self.get_details()

    def get_header(self):
        created_on = datetime.strptime(self.created_on, "%Y-%m-%dT%H:%M:%SZ")
        created_on = created_on.strftime("%Y-%m-%d %H:%M")

        return f"\n• {created_on} {self.user['name']}\n\n"

    def get_notes(self):
        notes = ""

        if not self.notes:
            return notes

        for note in self.notes.splitlines():
            for n in wrap(note, width=79):
                notes += f"\t{n}\n"

        return notes

    def get_details(self):
        update_detail = ""

        for detail in self.details:
            try:
                prefix = self.prefixes[detail["name"]]
            except KeyError as e:
                if detail["property"] == "attachment":
                    prefix = "Attachment"
                elif detail["property"] == "cf":
                    continue
                else:
                    raise KeyError(e)

            if detail.get("old_value") and detail.get("new_value"):
                if prefix == "Status" and self.statuses:
                    detail["old_value"] = self.statuses[detail["old_value"]]
                    detail["new_value"] = self.statuses[detail["new_value"]]
                elif prefix == "Priority" and self.priorities:
                    detail["old_value"] = self.priorities[detail["old_value"]]
                    detail["new_value"] = self.priorities[detail["new_value"]]
                elif prefix == "Assignee" and self.users:
                    detail["old_value"] = self.users[detail["old_value"]]
                    detail["new_value"] = self.users[detail["new_value"]]

                update_detail += (
                    f"\t‣ {prefix} changed from "
                    f"{detail['old_value']} to "
                    f"{detail['new_value']}\n"
                )
            elif detail.get("new_value"):
                update_detail += f"\t‣ {prefix} set to {detail['new_value']}\n"
            else:
                update_detail += f"\t‣ {prefix} deleted" f" {detail['old_value']}\n"

        return update_detail
