import logging
import json
from django.views.generic.base import View
from django.http import HttpResponse, Http404
from django.http.response import HttpResponseBase
from django.utils import six

from dajaxice.exceptions import FunctionNotCallableError
from dajaxice.core import dajaxice_functions

log = logging.getLogger('dajaxice')


def safe_dict(d):
    """
    Recursively clone json structure with UTF-8 dictionary keys
    http://www.gossamer-threads.com/lists/python/bugs/684379
    """
    if isinstance(d, dict):
        return dict([(k.encode('utf-8'), safe_dict(v)) for k, v in d.iteritems()])
    elif isinstance(d, list):
        return [safe_dict(x) for x in d]
    else:
        return d


class DajaxiceRequest(View):
    """ Handle all the dajaxice xhr requests. """

    def dispatch(self, request, name=None):

        if not name:
            raise Http404

        # Check if the function is callable
        if dajaxice_functions.is_callable(name, request.method):

            function = dajaxice_functions.get(name)
            data = getattr(request, function.method).get('argv', '')

            # Clean the argv
            if data != 'undefined':
                try:
                    data = safe_dict(json.loads(data))
                except Exception:
                    data = {}
            else:
                data = {}

            response_data = function.call(request, **data)
            if isinstance(response_data, HttpResponseBase):
                return response_data
            if isinstance(response_data, dict) and not response_data.get('success'):
                log.warning('Dajaxice success=false.\nResponse data: %s', response_data, extra={'request': request})
            if not isinstance(response_data, six.string_types):
                response_data = json.dumps(response_data)
            return HttpResponse(response_data, content_type="application/x-json")
        else:
            raise FunctionNotCallableError(name)
