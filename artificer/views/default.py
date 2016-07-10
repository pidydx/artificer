from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError


@view_config(route_name='index', renderer='../templates/index.jinja2')
def index_view(request):
    return {'version': 0.1, 'project': 'artificer'}
