{ pkgs, lib, config, inputs, ... }:

# Templates
# - https://github.com/myrheimb/devenv-python-uv
# - https://gitlab.com/devenv-templates/python

{
  # https://devenv.sh/basics/
  # Default Configs location where the an
  # OpenStudioLandscapes-OpenRV-Builder
  # subdirectory will be created:
  # - ~/.config/OpenStudioLandscapes
  env = {
    DOCKER_CONFIG_JSON = "${config.devenv.root}/.docker/config.json";
    OPENSTUDIOLANDSCAPES_CONFIGS_ROOT = "${config.devenv.root}/.config/OpenStudioLandscapes";
    # Sensor Status can be one of:
    # - STOPPED
    # - RUNNING
    # OPENSTUDIOLANDSCPES_OPENRV_BUILDER__NTFY_SENSOR_STATUS = "RUNNING";
    # OPENSTUDIOLANDSCPES_OPENRV_BUILDER__CHECK_FOR_NEW_COMMITS_SENSOR_STATUS = "STOPPED";
    # Sensor interval in hours:
    # OPENSTUDIOLANDSCPES_OPENRV_BUILDER__CHECK_FOR_NEW_COMMITS_SENSOR_INTERVAL = "48";
  };

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.docker
    # pkgs.apptainer
    # pkgs.gocryptfs  # This is actually a runtime dependency
    # pkgs.sudo
    # pkgs.polkit  # pkexec
    # pkgs.libpq
  ];

  languages.python = {
    enable = true;
    venv.enable = true;
    uv = {
      # let's start with false
      enable = true;
      sync = {
        enable = true;
        allGroups = true;             # Install all dependency groups
        # groups = [ "dev" ];  # Or pick specific ones
        # extras = [ "plotting" ];    # Specific extras
        allExtras = true;           # All extras
      };
    };
    version = "3.11";
  };

  # https://devenv.sh/languages/
  # languages.rust.enable = true;

  # https://devenv.sh/processes/
  # processes.dev.exec = "${lib.getExe pkgs.watchexec} -n -- ls -la";
  processes = {
    openstudiolandscapes = {
      ports.dagit.allocate = 3000;
      exec = "dagster dev --port ${toString config.processes.openstudiolandscapes.ports.dagit.value} --workspace $DAGSTER_WORKSPACE";
    };
  };

  # Files
  # - https://devenv.sh/creating-files/
  #
  # The copyMode attribute accepts:
  # - symlink (default): symlink to the read-only file in the Nix store. Edits are not possible; devenv keeps the link pointed at the current contents.
  # - seed: copy the file into place once, only if it does not already exist, and make it writable. Existing files are left untouched, so your edits are preserved. This is useful for seeding configuration files from templates that the user can then edit to fit their project.
  # - copy: copy the file into place as a writable file, overwriting it with fresh contents on every shell entry. The file is replaced atomically, by renaming a temporary file in the same directory over it, so tools that walk the project never see it missing. This is useful when a tool must write to the file in place but devenv should remain the source of truth.
  #
  # Docker Config File
  # Todo:
  #  - [ ] This was just a proof of concept
  #  - [ ] Find a better, clearer implementation
  #        the path to the Docker config.json is
  #        set in `.config/OpenStudioLandscapes/OpenStudioLandscapes-OpenRV-Builder/resource_docker_config.yaml`
  files.".docker/config.json" = {
    copyMode = "symlink";
    json = {};
  };

  # dagster.yaml for SQLite
  files.".dagster/dagster.yaml" = {
    copyMode = "seed";
    yaml = {
      auto_materialize = {
        enabled = true;
        use_sensors = true;
      };
      concurrency = {
        default_op_concurrency_limit = 1;
      };
      run_queue = {
        block_op_concurrency_limited_runs = {
          enabled = true;
        };
        max_concurrent_runs = 1;
      };
      telemetry = {
        enabled = false;
      };
    };
  };

  # dagster.yaml for PostgreSQL
  files.".dagster-postgres/dagster.yaml" = {
    copyMode = "seed";
    yaml = {
      auto_materialize = {
        enabled = true;
        use_sensors = true;
      };
      concurrency = {
        default_op_concurrency_limit = 1;
      };
      run_queue = {
        block_op_concurrency_limited_runs = {
          enabled = true;
        };
        max_concurrent_runs = 1;
      };
      telemetry = {
        enabled = false;
      };
      storage = {
        postgres = {
          postgres_db = {
            db_name = "postgres";
            hostname = "localhost";
            password = "mysecretpassword";
            port = "2345";
            username = "postgres";
          };
        };
      };
    };
  };

  # .dagster_home_mysql/workspace.yaml
  files."./workspace.yaml" = {
    copyMode = "seed";
    yaml = {
      load_from = [
        {
          python_module = {
            module_name = "OpenStudioLandscapes.engine.definitions";
            location_name = "OpenStudioLandscapes Engine";
          };
        }
      ];
    };
  };

  # # .dagster_home_mysql/dagster.yaml
  # files.".dagster_home_postgres/dagster.yaml" = {
  #   copyMode = "seed";
  #   yaml = {
  #     auto_materialize = {
  #       enabled = true;
  #       use_sensors = true;
  #     };
  #     concurrency = {
  #       default_op_concurrency_limit = 1;
  #     };
  #     run_queue = {
  #       block_op_concurrency_limited_runs = {
  #         enabled = true;
  #       };
  #       max_concurrent_runs = 1;
  #     };
  #     telemetry = {
  #       enabled = false;
  #     };
  #     storage = {
  #       postgres = {
  #         postgres_db = {
  #           username = "postgres";
  #           password = "mysecretpassword";
  #           hostname = "localhost";
  #           db_name = "postgres";
  #           port = 5432;
  #         };
  #       };
  #     };
  #   };
  # };

  # # .dagster_home_mysql/workspace.yaml
  # files.".dagster_home_postgres/workspace.yaml" = {
  #   copyMode = "seed";
  #   yaml = {
  #     load_from = [
  #       {
  #         python_module = {
  #           module_name = "OpenStudioLandscapes.OpenRV_Builder._definitions_with_upstream_specs";
  #           location_name = "OpenStudioLandscapes-OpenRV-Builder";
  #         };
  #       }
  #     ];
  #   };
  # };

  # https://devenv.sh/services/
  # - https://youtu.be/joIeF6uuMC0?list=PLfdfqqNJDWhcDaR3vzn1PtT2aGrl4UiSk&t=949
  # Test
  # `pg_isready --host localhost --port 5432 --username postgres`
  # `devenv processes up postgres`
  # `devenv processes down postgres`
  # services.postgres = {
  #   enable = false;
  #   package = pkgs.postgresql_17;
  #   createDatabase = false;
  #   initdbArgs = [
# #      "--show"
  #     #    98 │ VERSION=17.11
  #     #    99 │ PGDATA=/home/michael/git/backup_copy/repos/OpenStudioLandscapes-OpenRV-Builder/.devenv/state/postgres
  #     #   100 │ share_path=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/share/postgresql
  #     #   101 │ PGPATH=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/bin
  #     #   102 │ POSTGRES_SUPERUSERNAME=michael
  #     #   103 │ POSTGRES_BKI=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/share/postgresql/postgres.bki
  #     #   104 │ POSTGRESQL_CONF_SAMPLE=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/share/postgresql/postgresql.conf.sample
  #     #   105 │ PG_HBA_SAMPLE=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/share/postgresql/pg_hba.conf.sample
  #     #   106 │ PG_IDENT_SAMPLE=/nix/store/0m6z1g5zrgngyysmgj7qsvcz0xz8l8a9-postgresql-17.11/share/postgresql/pg_ident.conf.sample
  #     #   107 │ cp: cannot create regular file '/home/michael/git/backup_copy/repos/OpenStudioLandscapes-OpenRV-Builder/.devenv/state/postgres/postgresql.conf':
  #     #       │  No such file or directory
  #     "--debug"
  #     "--username=postgres"
  #   ];
  #   listen_addresses = "localhost,127.0.0.1";
  #   #listen_addresses = "localhost";
  #   # listen_addresses = "*";
  #   initialDatabases = [
  #     {
  #       "name" = "postgres";
  #       "user" = "postgres";
  #       "pass" = "mysecretpassword";
  #       # psycopg.errors.InsufficientPrivilege: permission denied for schema public
  #       # sqlalchemy.exc.ProgrammingError: (psycopg.errors.InsufficientPrivilege) permission denied for schema public
# #        initialSQL = ''
# #          CREATE SCHEMA public;
# #          GRANT USAGE ON SCHEMA public TO postgres;
# #          GRANT CREATE ON SCHEMA public TO postgres;
# #          GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
# #        '';
  #     }
  #   ];
  #   port = 5432;
# #    initialScript = ''
# #      CREATE ROLE postgres WITH LOGIN PASSWORD 'mysecretpassword' CREATEDB;
# #    '';
  #     # ALTER ROLE postgres WITH LOGIN;
  #     # CREATE SCHEMA public;
  #     # GRANT USAGE ON SCHEMA public TO postgres;
  #     # GRANT CREATE ON SCHEMA public TO postgres;
  #     # GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
# #    '';
  # };
  # Todo:
  #  - [ ] Enable PostgreSQL as backend for Dagster
  #  - [ ] Is Docker as a service needed?
  #        - pkgs.docker
  #        - How would we add $USER to the `docker` group?

  # # https://devenv.sh/scripts/
  # scripts.openstudiolandscapes-openrv-builder-mysql = {
  #   exec = ''
  #     dagster dev --workspace $DAGSTER_WORKSPACE_MYSQL
  #   '';
  # };
  # scripts.openstudiolandscapes-openrv-builder-postgresql = {
  #   exec = ''
  #     dagster dev --workspace $DAGSTER_WORKSPACE_POSTGRESQL
  #   '';
  #   # env = {};
  # };
  # scripts.openstudiolandscapes-openrv-builder = {
# #    exec = config.scripts.openstudiolandscapes-openrv-builder-mysql.exec;
  #   exec = ''
  #     export DAGSTER_HOME=/home/michael/git/backup_copy/repos/OpenStudioLandscapes-OpenRV-Builder/.dagster_home_postgres
  #     dagster dev --workspace /home/michael/git/backup_copy/repos/OpenStudioLandscapes-OpenRV-Builder/.dagster_home_postgres/workspace.yaml
  #   '';
  # };

  scripts.create_openstudiolandscapes_configs_root.exec = ''
    mkdir -p $OPENSTUDIOLANDSCAPES_CONFIGS_ROOT
  '';

  # https://devenv.sh/basics/
  enterShell = ''
    create_openstudiolandscapes_configs_root
  '';

  # See full reference at https://devenv.sh/reference/options/

  profiles = {
    # `devenv --profile mysql up openstudiolandscapes-openrv-builder`
    mysql.module = {
      env = {
        DAGSTER_HOME = "${config.devenv.root}/.dagster_home_mysql";
        DAGSTER_WORKSPACE = "${config.devenv.root}/.dagster_home_mysql/workspace.yaml";
      };

    };
    # Todo
    #  - [ ] PostgreSQL does not work yet
#     # `devenv --profile postgresql up openstudiolandscapes-openrv-builder`
#     # `devenv --profile postgresql processes down`
#     postgresql.module = { config, pkgs, ... }: {
#       packages = [ pkgs.libpq ];
#       # is this referring to the services dict defined in this file?
#       services.postgres = {
#         enable = true;
# #        package = pkgs.postgresql_17;
# #        createDatabase = true;
# ##        # TBD: hbaConf = builtins.readFile ./my-custom/directory/to/pg_hba.conf;
# ##        initdbArgs = [
# ##          "--locale=C"
# ##          "--encoding=UTF8"
# ##        ];
# ##        # PGHOST
# ##        listen_addresses = "localhost";
# ##        port = 5432;
# #        initialDatabases = [
# #          {
# #            "name" = "postgres";
# #            "user" = "postgres";
# #            "pass" = "mysecretpassword";
# #          }
# #        ];
#       };
#       env = {
#         DAGSTER_HOME = "${config.devenv.root}/.dagster_home_postgres";
#         DAGSTER_WORKSPACE = "${config.devenv.root}/.dagster_home_postgres/workspace.yaml";
#         # DB_HOST = config.env.PGHOST;
#       };
#     };
  };
}
