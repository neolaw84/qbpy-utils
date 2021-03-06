import os
import unittest

from qbpy_utils.docker import postgres

class TestPostgres(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.container = None
        cls.mypg_dir = "/docker/volumes/mypg/var/lib/postgresql/data"

    @classmethod
    def tearDownClass(cls):
        if cls.container:
            postgres.stop_postgres(name=cls.container.name, mount_volume={cls.mypg_dir : True}, verbose=True, remove=True, remove_data=True)
        try:
            os.removedirs(cls.mypg_dir)
        except:
            pass

    def test_pull(self):
        image = postgres.pull_postgres(version="latest")
        assert(image)
        image = postgres.pull_postgres(version="11-alpine")
        assert("postgres:11-alpine" in list(image.tags))

    def test_pull_via_cli(self):
        image = postgres.postgres_main("pull -vs 10-alpine".split())
        assert("postgres:10-alpine" in list(image.tags))

    def test_start_via_cli(self):
        container = postgres.postgres_main("start -vs 10-alpine -n mypg -p 5006 --mount-volume {}:/var/lib/postgresql/data".format(TestPostgres.mypg_dir).split())
        TestPostgres.container = container

    def test_restart_existing_via_cli(self):
        container = postgres.postgres_main("start --name mypg --restart-if-exists".split())
