from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'List all URLs for a specified app'

    def add_arguments(self, parser):
        parser.add_argument('payment', type=str, help='The name of the app to list URLs for')

    def handle(self, *args, **kwargs):
        app_name = kwargs['payment']
        urls = self.list_app_urls(app_name)
        for pattern, name in urls:
            self.stdout.write(f"Pattern: {pattern}, Name: {name}")

    def list_app_urls(self, app_name):
        resolver = get_resolver()
        all_urls = resolver.url_patterns

        def list_urls(url_patterns, namespace=None):
            urls = []
            for entry in url_patterns:
                if hasattr(entry, 'url_patterns'):
                    urls.extend(list_urls(entry.url_patterns, namespace=entry.namespace or namespace))
                else:
                    url_name = entry.name
                    if namespace:
                        url_name = f"{namespace}:{url_name}"
                    urls.append((entry.pattern, url_name))
            return urls

        app_urls = [url for url in list_urls(all_urls) if url[1] and app_name in url[1]]
        return app_urls
