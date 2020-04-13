import unittest

from qbpy_utils.docker import postgres

class TestPostgresPull(unittest.TestCase):

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_pull(self):
        image = postgres.pull_postgres(version="latest")
        assert(image)
        image = postgres.pull_postgres(version="11-alpine")
        assert(image.tags, ['postgres:11-alpine'])

    def test_pull_via_cli(self):
        image = postgres.postgres_main("pull -v 10-alpine".split())
        assert(image.tags, ['postgres:10-alpine'])

    def test_start_via_cli(self):
        container = postgres.postgres_main("start -v 10-alpine -n mypg -p 5006 --mount-volume /docker/volumes/var/lib/postgresql/data:/var/lib/postgresql/data".split())

    def test_restart_existing_via_cli(self):
        container = postgres.postgres_main("start --name pru_cogclaims --restart-if-exists")


# if __name__ == '__main__':
#    unittest.main()