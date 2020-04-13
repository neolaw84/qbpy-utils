import sys
import os
import argparse
from typing import Dict, List

import docker


def pull_postgres(version: str, verbose:bool = False):
    repo_version = "postgres:{}".format(version)
    client = docker.from_env()
    
    image = client.images.list(repo_version)
    if image and len(image) > 0:
        if verbose: print("{} already exists.".format(repo_version))
        image = image[0]
    else:
        if verbose: print("pulling: {}".format(repo_version))
        image = client.images.pull("postgres", tag=version)
    
    print("pulling complete : {}".format(repo_version))
    if verbose: print("id : {}".format(image.id))
    if verbose: print("tag : {}".format(image.tags))
    return image


def start_postgres(version: str = "latest", name: str = None, 
    postgres_password: str = None, postgres_user: str = None, postgres_db: str = None, 
    postgres_initdb_args: str = None, postgres_initdb_waldir: str = None, 
    postgres_host_auth_method: str = "password", pgdata: str = "/var/lib/postgresql/data", 
    mount_volume: Dict = {}, port: str="5432", verbose:bool = False, 
    restart_if_exists:bool = False
    ):

    for k, _ in mount_volume.items():
        try:
            if verbose: print ("creating directory: {}".format(k))
            os.makedirs(k)
        except FileExistsError:
            if verbose: print ("directory {} already exists".format(k))
            pass

    client = docker.from_env()
    print("starting postgres version: {} and name: {}".format(version, name))
    if name:
        containers = client.containers.list(all=True, filters={"name": name})
        if containers:
            print ("container with name: {} exists.".format(name))
            if restart_if_exists:
                print ("restarting container: {}".format(name))
                containers[0].restart(timeout=120) 
            else:
                print("will do nothing. exiting.")
            return containers[0]

    volumes = {}
    if mount_volume: volumes = {k: {"bind": v, "mode": "rw"} for k, v in mount_volume.items()}

    environment={
        "POSTGRES_PASSWORD": postgres_password, 
        "POSTGRES_USER": postgres_user, 
        "POSTGRES_DB": postgres_db,
        "POSTGRES_INITDB_ARGS": postgres_initdb_args,
        "POSTGRES_INITDB_WALDIR": postgres_initdb_waldir, 
        "POSTGRES_HOST_AUTH_METHOD": postgres_host_auth_method, 
        "PGDATA": pgdata
    }

    print("ensuring postgres:{} exists.".format(version))
    pull_postgres(version, verbose)

    container = client.containers.run("postgres:{}".format(version), detach=True, 
        name=name, ports={"5432/tcp":int(port)}, stdin_open=True, tty=True, 
        volumes=volumes, environment=environment
    )
    print("successfully started container: {}".format(container.name))
    
    return container


def get_parser():
    parser = argparse.ArgumentParser(description="Utilities to set up postgres in docker containers.")
    
    choices = ["help", "pull", "start", "stop"]
    parser.add_argument(action="store", default="help", type=str, 
        choices=choices, help="action: one of {}".format(", ".join(choices)), dest="action")
    
    parser.add_argument("--version", "-vs", action="store", default="latest", type=str,
        help="Postgresql docker version. E.g. 10-alpine.", dest="version")

    parser.add_argument("--name", "-n", action="store", default=None, type=str, 
        help="Name of the container. Default is assigned by docker engine.",dest="name")

    parser.add_argument("--postgres_password", "-pwd", action="store", default="bad_password", type=str,
        help="Password. Default is 'bad_password'.", dest="password")

    parser.add_argument("--postgres_user", "-usr", action="store", default="postgres", type=str,
        help="Username. Default is 'postgres'.", dest="user")

    parser.add_argument("--postgres_db", "-db", action="store", default="postgres", type=str,
        help="Db. Default is 'postgres'.", dest="db")

    parser.add_argument("--port", "-p", action="store", default="5432", help="Port to forward. Default is 5432.", dest="port")

    parser.add_argument("--mount-volume", "-mv", nargs = "*", dest="volumes")

    parser.add_argument("--verbose", "-v", action="store_true", default=False, dest="verbose")

    parser.add_argument("--restart-if-exists", "-rs", action="store_true", default=False, dest="restart_if_exists")

    return parser

def postgres_main(argv: List[str] = ["help"]):
    
    parser = get_parser()
    args = parser.parse_args(argv)        

    def print_help():
        parser.print_help()

    def pull():
        return pull_postgres(version=args.version)

    def start():

        postgres_host_auth_method: str = "password"
        pgdata: str = "/var/lib/postgresql/data/pgdata"
        if args.volumes: mount_volume: Dict = {x.split(":")[0]: x.split(":")[1] for x in args.volumes if ":" in x}
        else:
            mount_volume={}
        
        return start_postgres(version=args.version,
            name=args.name, 
            postgres_password=args.password, 
            postgres_user=args.user, 
            postgres_db=args.db, 
            postgres_initdb_args=None, 
            postgres_initdb_waldir=None, 
            postgres_host_auth_method="password", 
            pgdata=pgdata, 
            mount_volume=mount_volume, 
            port=args.port,
            restart_if_exists=args.restart_if_exists,
            verbose=args.verbose)

    def stop():
        pass

    action_to_function = {
        "help" : print_help,
        "pull" : pull,
        "start" : start,
        "stop" : stop
    }

    function = action_to_function.get(args.action, "help")
    return function()


if __name__ == "__main__":
    postgres_main(sys.argv[1:])
    
