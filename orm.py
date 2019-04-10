from mysql import connector


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
                raise ValueError('Required field is not defined')
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
        col_name = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        query = f'insert into {table_name}({col_name}) values({values})'
        args = tuple(kwargs.values())
        self.execute(query, args)

    def select(self, **kwargs):
        table_name = self.model_cls.Meta.table_name

        if kwargs == {}:
            query = f'select * from {table_name}'
            args = None

        else:
            condition = '=%s and '.join(kwargs.keys()) + '=%s'
            query = f'select * from {table_name} where {condition}'
            args = tuple(kwargs.values())

        ans = self.execute(query, args)
        instances = []
        for d in ans:
            instances.append(self.model_cls(**d))

        return instances

    def delete(self, obj=None, **kwargs):
        table_name = self.model_cls.Meta.table_name
        args = None

        if obj is not None:
            query = f'delete from {table_name} where id={obj.id}'

        elif kwargs == {}:
            query = f'delete from {table_name}'

        else:
            condition = '=%s and'.join(kwargs.keys()) + '=%s'
            query = f'delete from {table_name} where {condition}'
            args = tuple(kwargs.values())

        self.execute(query, args)

    def update(self, obj=None):
        table_name = self.model_cls.Meta.table_name

        if obj is None:
            raise ValueError('object is None, select object to save')

        assign = '=%s, '.join(obj.__dict__.keys()) + '=%s'
        query = f'update {table_name} set {assign} where id={obj.id}'
        args = tuple(obj.__dict__.values())

        self.execute(query, args)

    @staticmethod
    def execute(query, args):
        answer = None
        try:
            conn = connector.connect(host='localhost',
                                     database='persons',
                                     user='some_admin',
                                     password='')
            cursor = conn.cursor()
            cursor.execute(query, args)
            if query[0] == 's':
                rows = cursor.fetchall()
                columns = cursor.column_names
                answer = []
                for i in range(len(rows)):
                    d = dict()
                    for j in range(len(columns)):
                        d[columns[j]] = rows[i][j]
                    answer.append(d)
            conn.commit()

        finally:
            cursor.close()
            conn.close()

        return answer


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
        type(self).objects.update(self)


class User(Model):
    id = IntField()
    name = StringField()

    class Meta:
        table_name = 'users'


# User.objects.delete(id=2, name='Sasha')
# user = User(id='3', name='Katya')
# user.delete()
# users = User.objects.select(id=5)
# print(users)
# user1 = users[0]
# user1.id = 8
# user1.save()

user = User.objects.select(name='Vika')[0]
user.name = 'Vanya'
user.save()
user = User.objects.select(id=3)[0]
print(user.name)
