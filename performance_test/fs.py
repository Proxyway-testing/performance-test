def file_to_list(filename: str) -> list:
    with open(filename) as f:
        return [line.strip() for line in f.readlines()]
