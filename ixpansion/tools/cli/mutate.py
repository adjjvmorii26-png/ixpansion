from expansion.models.mutation import Mutation


def build(field="energy", value=3):
    return Mutation("origin", field, "add", value)
