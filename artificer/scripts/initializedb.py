import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from artificer.models.meta import Base
from artificer.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from artificer.lib.artifacts import get_artifact, init_labels, init_sources, init_supported_os
from artificer.models import User

from artifacts import reader as fa_readers

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        db_session = get_tm_session(session_factory, transaction.manager)
        init_labels(db_session)
        init_supported_os(db_session)
        init_sources(db_session)
        init_admin(db_session)
        init_artifacts(db_session)


def init_admin(db_session):
    password = ''
    # TODO prompt for password
    admin = User(name='admin', fullname='admin', password=password)
    db_session.add(admin)


def init_artifacts(db_session, artifact_path=None):
    # TODO handle alternate artifact_path options
    if not artifact_path:
        artifact_path = os.path.join(sys.prefix, 'share/artifacts')

    artifact_reader = fa_readers.YamlArtifactsReader()

    for forensic_artifact in artifact_reader.ReadDirectory(artifact_path, extension='yaml'):
        artifact = get_artifact(db_session, forensic_artifact, author='admin', replace=True)
        db_session.add(artifact)


if __name__ == "__main__":
    main()