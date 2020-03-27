from faker import Faker
fake = Faker()


def generate_movies(movie_count):
    movies_payload = []

    for counter in range(movie_count):
        movie = {
            "title": f"{fake.first_name()} Loves {fake.first_name()}",
            "year": 2999,
            "director": fake.name(),
            "actor": fake.name()
        }

        movies_payload.append(movie)
    return movies_payload
