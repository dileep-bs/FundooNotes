from elasticsearch_dsl import connections

connections.create_connection(hosts=['localhost'], timeout=20)
from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import analyzer, tokenizer
from .models import Notes

html_strip = analyzer(
    'html_strip',
    tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
    filter=["lowercase", "stop", "snowball"]
)


class Document(Document):
    note = fields.TextField(analyzer=html_strip)
    title = fields.TextField(analyzer=html_strip)
    label = fields.ObjectField(properties={'name': fields.TextField(analyzer=html_strip)})
    reminder = fields.TextField(analyzer=html_strip)
    user = fields.ObjectField(
        properties={'email': fields.TextField(analyzer=html_strip), 'username': fields.TextField()})

    class Index:
        name = 'note'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Notes
