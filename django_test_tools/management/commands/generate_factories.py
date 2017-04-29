from django.core.management import BaseCommand
from django.apps.registry import apps


PRINT_IMPORTS = """
from pytz import timezone

from factory import Iterator
from factory import LazyAttribute
from factory import SubFactory
from factory import lazy_attribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyInteger
from faker import Factory as FakerFactory

faker = FakerFactory.create()

"""
PRINT_FACTORY_CLASS= """
class {0}Factory(DjangoModelFactory):
    class Meta:
        model = {0}
"""

PRINT_CHARFIELD ="""    {} = LazyAttribute(lambda x: FuzzyText(length={}, chars=string.digits).fuzz()){}"""
PRINT_CHARFIELD_CHOICES ="""    {} = Iterator({}.{}, getter=lambda x: x[0])"""
PRINT_DATETIMEFIELD ="""    {} = LazyAttribute(lambda x: faker.date_time_between(start_date="-1y", end_date="now",
                                                           tzinfo=timezone(settings.TIME_ZONE))){}"""
PRINT_FOREIGNKEY ="""    {} = SubFactory({}Factory){}"""
PRINT_BOOLEANFIELD ="""    {} = Iterator([True, False])"""
PRINT_INTEGERFIELD ="""    {} = LazyAttribute(lambda o: randint(1, 100))"""
PRINT_TEXTFIELD ="""    {} = LazyAttribute(lambda x: faker.sentence(nb_words=6, variable_nb_words=True))"""
PRINT_TEXTFIELD ="""    {} = LazyAttribute(lambda x: faker.sentence(nb_words=6, variable_nb_words=True))"""



class ModelFactoryGenerator(object):

    def __init__(self, model):
        self.model = model

    def _generate(self):
        factory_class_content = list()
        factory_class_content.append(PRINT_FACTORY_CLASS.format(self.model.__name__))
        for field in self.model._meta.fields:
            if type(field).__name__ in ['AutoField', 'AutoCreatedField', 'AutoLastModifiedField']:
                pass
            elif type(field).__name__ in ['DateTimeField', 'DateField']:
                factory_class_content.append(PRINT_DATETIMEFIELD.format(field.name, ''))
            elif type(field).__name__ == 'CharField':
                if len(field.choices) > 0:
                    factory_class_content.append(PRINT_CHARFIELD_CHOICES.format(field.name, self.model.__name__, 'CHOICES'))
                else:
                    factory_class_content.append(PRINT_CHARFIELD.format(field.name, field.max_length,''))
            elif type(field).__name__ == 'ForeignKey':
                related_model = field.rel.to.__name__
                factory_class_content.append(PRINT_FOREIGNKEY.format(field.name, related_model, ''))
            elif type(field).__name__ == 'BooleanField':
                factory_class_content.append(PRINT_BOOLEANFIELD.format(field.name))
            elif type(field).__name__ == 'TextField':
                factory_class_content.append(PRINT_TEXTFIELD.format(field.name))
            elif type(field).__name__ == 'IntegerField':
                factory_class_content.append(PRINT_INTEGERFIELD.format(field.name))
            else:
                factory_class_content.append('     **** {} = {} ******'.format(field.name, type(field).__name__))

        return factory_class_content

    def __str__(self):
        return '\n'.join(self._generate())


class Command(BaseCommand):
    """

        $ python manage.py
    """

    def add_arguments(self, parser):
        pass
        parser.add_argument('app_name')
        # parser.add_argument("-l", "--list",
        #                     action='store_true',
        #                     dest="list",
        #                     help="List employees",
        #                     )
        # parser.add_argument("-a", "--assign",
        #                     action='store_true',
        #                     dest="assign",
        #                     help="Create unit assignments",
        #                     )
        #
        #
        # parser.add_argument("--office",
        #                     dest="office",
        #                     help="Organizational unit short name",
        #                     default=None,
        #                     )
        # parser.add_argument("--start-date",
        #                     dest="start_date",
        #                     help="Start date for the assignment",
        #                     default=None,
        #                     )
        # parser.add_argument("--fiscal-year",
        #                     dest="fiscal_year",
        #                     help="Fiscal year for assignments",
        #                     default=None,
        #                     )
        # parser.add_argument("-u", "--username",
        #                 dest="usernames",
        #                 help="LDAP usernames for employees",
        #                 nargs='+',
        #                 )
    def handle(self, *args, **options):
        app = options.get('app_name')
        installed_apps = dict(self.get_apps())
        app = installed_apps.get(app)
        for model in app.get_models():
            model_fact = ModelFactoryGenerator(model)
            self.stdout.write(str(model_fact))




    def get_apps(self):
        for app_config in apps.get_app_configs():
            yield app_config.name, app_config
