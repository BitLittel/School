# -*- coding: utf-8 -*-

import hashlib
from school import school


@school.template_filter('md5')
def md5_string(value):
    h = hashlib.new('md5')
    h.update(value.encode('utf-8'))
    return h.hexdigest()
