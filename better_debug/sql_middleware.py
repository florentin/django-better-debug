import logging
from django.db import connections
from django.template import Template, Context
from django.conf import settings

#
# Log all SQL statements direct to the console (when running in DEBUG)
# Intended for use with the django development server.
#
class SqlMiddlewareBase(object):
    def get_query_stats(self):
        sql_data = {}
        for connection_name in connections:
            connection = connections[connection_name]
            if connection.queries:
                time = sum([float(q['time']) for q in connection.queries])        
                header_t = Template("{{name}}: {{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds")
                stats = header_t.render(Context({
                  'name': connection_name, 
                  'sqllog':connection.queries,
                  'count':len(connection.queries),
                  'time':time
                }))
                t = Template("\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
                queries = t.render(Context({'sqllog':connection.queries}))
                queries = queries
                sql_data[connection_name] = {'stats': stats, 'queries': queries}
        return sql_data

                    
class SqlConsoleMiddleware(SqlMiddlewareBase):
    def process_response(self, request, response): 
        for conn_name, sql_data in self.get_query_stats().items():
            print "\033[31;1m"
            print conn_name
            print sql_data['stats']
            print "\033[0;30;1m"
            print sql_data['queries']
        return response


class SqlLoggerMiddleware(SqlMiddlewareBase):
    def process_response(self, request, response): 
        logger = logging.getLogger('queries')
        for conn_name, sql_data in self.get_query_stats().items():
            logger.debug(sql_data['stats'])
            logger.debug(sql_data['queries'])
        return response


class SqlDumpMiddleware(SqlMiddlewareBase):
    def process_response(self, request, response):
        content = ''
        for conn_name, sql_data in self.get_query_stats().items():
            content += sql_data['stats'] + sql_data['queries']
            
        if settings.DEBUG and 'debugsql' in request.GET:
            response.content = content
            response['Content-Type'] = 'text/plain'
        return response
