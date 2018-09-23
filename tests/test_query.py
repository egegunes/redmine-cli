from redmine.query import Query


def test_query_str():
    query = Query(id=1, name="Query")

    assert str(query) == "1   Query"
