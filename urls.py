# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('eqnsolver.views',
	url(r'^$', 'list', name='list'),
	url(r'^remove$', 'remove', name='remove'),
	url(r'^image$', 'image', name='image'),
	url(r'^imagenorm$', 'image_norm', name='imagenorm'),
)

