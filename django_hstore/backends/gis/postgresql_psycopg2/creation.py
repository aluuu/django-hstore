# -*- coding: utf-8 -*-
from django import VERSION
from django.conf import settings
from django.db.backends.util import truncate_name
from django.contrib.gis.db.backends.postgis.base import PostGISCreation


class DatabaseCreation(PostGISCreation):

    def sql_table_creation_suffix(self):
        qn = self.connection.ops.quote_name
        return ' TEMPLATE %s' % qn(getattr(settings, 'POSTGIS_TEMPLATE', 'template_postgis'))

    def sql_indexes_for_field(self, model, f, style):
        kwargs = VERSION[:2] >= (1, 3) and {'connection': self.connection} or {}
        if f.db_type(**kwargs) == 'hstore':
            if not f.db_index:
                return []
            qn = self.connection.ops.quote_name
            tablespace = f.db_tablespace or model._meta.db_tablespace
            tablespace_sql = ''
            if tablespace:
                sql = self.connection.ops.tablespace_sql(tablespace)
                if sql:
                    tablespace_sql = ' ' + sql
            index_name = '%s_%s_gist' % (model._meta.db_table, f.column)
            clauses = [style.SQL_KEYWORD('CREATE INDEX'),
                style.SQL_TABLE(qn(truncate_name(index_name, self.connection.ops.max_name_length()))),
                style.SQL_KEYWORD('ON'),
                style.SQL_TABLE(qn(model._meta.db_table)),
                style.SQL_KEYWORD('USING GIST'),
                '(%s)' % style.SQL_FIELD(qn(f.column))]
            return ['%s%s;' % (' '.join(clauses), tablespace_sql)]
        else:
            return super(DatabaseCreation, self).sql_indexes_for_field(model, f, style)
