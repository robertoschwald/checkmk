#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Service-groups"""
from cmk.gui import watolib
from cmk.gui.http import Response
from cmk.gui.plugins.openapi.endpoints.utils import serve_group, serialize_group
from cmk.gui.plugins.openapi.restful_objects import constructors, endpoint_schema, response_schemas, \
    request_schemas
from cmk.gui.watolib.groups import edit_group, add_group, load_service_group_information


@endpoint_schema('/collections/service_group',
                 'cmk/create',
                 method='post',
                 etag='output',
                 request_body_required=True,
                 request_schema=request_schemas.InputServiceGroup,
                 response_schema=response_schemas.DomainObject)
def create(params):
    """Create a service-group"""
    body = params['body']
    name = body['name']
    alias = body.get('alias')
    add_group(name, 'service', {'alias': alias})
    group = _fetch_service_group(name)
    return serve_group(group, serialize_group('service_group'))


@endpoint_schema('/collections/service_group',
                 '.../collection',
                 method='get',
                 response_schema=response_schemas.DomainObjectCollection)
def list_groups(params):
    """List service-groups"""
    return constructors.serve_json({
        'id': 'folders',
        'value': [
            constructors.collection_item('service_group', 'service_group', group)
            for group in load_service_group_information().values()
        ],
        'links': [constructors.link_rel('self', '/collections/service_group')]
    })


@endpoint_schema('/objects/service_group/{name}',
                 'cmk/show',
                 method='get',
                 response_schema=response_schemas.ServiceGroup,
                 etag='output',
                 parameters=['name'])
def show_group(params):
    """Show a service-group"""
    name = params['name']
    group = _fetch_service_group(name)
    return serve_group(group, serialize_group('service_group'))


@endpoint_schema('/objects/service_group/{name}',
                 '.../delete',
                 method='delete',
                 parameters=['name'],
                 output_empty=True,
                 etag='input')
def delete(params):
    """Delete a service-group"""
    name = params['name']
    group = _fetch_service_group(name)
    constructors.require_etag(constructors.etag_of_dict(group))
    watolib.delete_group(name, 'service')
    return Response(status=204)


@endpoint_schema('/objects/service_group/{name}',
                 '.../update',
                 method='put',
                 parameters=['name'],
                 response_schema=response_schemas.ServiceGroup,
                 etag='both',
                 request_body_required=True,
                 request_schema=request_schemas.InputServiceGroup)
def update(params):
    """Update a service-group"""
    name = params['name']
    group = _fetch_service_group(name)
    constructors.require_etag(constructors.etag_of_dict(group))
    edit_group(name, 'service', params['body'])
    group = _fetch_service_group(name)
    return serve_group(group, serialize_group('service_group'))


def _fetch_service_group(ident):
    groups = load_service_group_information()
    group = groups[ident].copy()
    group['id'] = ident
    return group
