from redmine.project import Project


def test_project_str():
    project = Project(id=1, name="Project")

    assert str(project) == "1   Project"
