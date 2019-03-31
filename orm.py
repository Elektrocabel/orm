class Field:
    def __init__(self, f_type, required=True, default=None):
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None:
            if not self.required:
                return None
            else:
                raise ValueError('Required item is not defined')
        return self.f_type(value)


class IntField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(int, required, default)


class StringField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(str, required, default)


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')

        # todo mro

        fields = {k: v for k, v in namespace.items()
                  if isinstance(v, Field)}
        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        return super().__new__(mcs, name, bases, namespace)


class Manage:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        self.model_cls = owner
        return self

    def create(self, **kwargs):
        table_name = self.model_cls.Meta.table_name
        col_name = tuple(kwargs.keys())
        values = tuple(kwargs.values())
        req = f'insert into {table_name} {col_name} values {values}'
        self.send(req)

    def select(self, **kwargs):
        table_name = self.model_cls.Meta.table_name
        condition = ''
        for k, v in kwargs.items():
            condition += f'{k}={v}, '
        condition = condition[:-2]
        req = f'select * from {table_name} where {condition}'
        ans = self.send(req)
        instance = self.model_cls()
        for k, v in ans.items():
            setattr(instance, k, v)

    def delete(self, obj=None, **kwargs):
        table_name = self.model_cls.Meta.table_name
        if obj is not None:
            key, val = list(obj.__dict__.items())[0]
            req = f'delete from {table_name} where {key}={val}'
        elif kwargs == {}:
            req = f'delete from {table_name}'
        else:
            condition = ''
            for k, v in kwargs.items():
                condition += f'{k}={v}, '
            condition = condition[:-2]
            req = f'delete from {table_name} where {condition}'
        self.send(req)

    def update(self, **kwargs):
        pass

    @staticmethod
    def send(request):
        print(request)
        return {'id': 5, 'name': 'Kolya'}


class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects = Manage()
    # todo DoesNotExist

    def __init__(self, *_, **kwargs):
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

    def delete(self):
        type(self).objects.delete(self)

    def save(self):
        pass


class User(Model):
    id = IntField()
    name = StringField()

    class Meta:
        table_name = 'Users'


User.objects.create(id=2, name='Vasya')
User.objects.delete(id=2)
user = User(id='3', name='Katya')
user.delete()
# User.objects.select(id=5)