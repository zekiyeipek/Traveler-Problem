class Query:
    def __init__(self, query_type, source, destination, transport_types=None, n=None):
        self.type = query_type
        self.source = source
        self.destination = destination
        self.transport_types = transport_types if transport_types is not None else []
        self.n = n