# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime
import uuid

from laos.common import config


class BaseDatabaseModel(object):

    INSERT = "INSERT INTO {} VALUES {}"
    SELECT = "SELECT * FROM {} {}"
    WHERE = "WHERE {}"
    AND = " AND "
    DELETE = "DELETE FROM {} {}"

    def __init__(self, **kwargs):
        self.id = uuid.uuid4().hex
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def save(self):
        insert = self.INSERT.format(
            self.table_name,
            str(tuple([getattr(self, clmn) for clmn in self.columns]))
        )
        print(insert)
        async with config.Connection.from_class().acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(insert)
                await conn.commit()
        return self

    @classmethod
    async def delete(cls, **kwargs):
        delete = cls.DELETE.format(
            cls.table_name, cls.__define_where(**kwargs))
        async with config.Connection.from_class().acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(delete)
                await conn.commit()

    async def update(self, **kwargs):
        async with config.Connection.from_class().acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute()

    @classmethod
    async def exists(cls, name, project_id):
        return True if len(await cls.find_by(
            name=name,
            project_id=project_id)) else False

    @classmethod
    def __define_where(cls, **kwargs):
        search_field_parts = []
        final = []
        for k, v in kwargs.items():
            search_field_parts.append("{}='{}'".format(k, v))

        for i in range(len(search_field_parts)):
            final.extend([search_field_parts[i],
                          cls.AND if i != len(
                              search_field_parts) - 1 else ""])

        return cls.WHERE.format("".join(final))

    @classmethod
    async def find_by(cls, **kwargs):
        where = cls.__define_where(**kwargs)

        async with config.Connection.from_class().acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(cls.SELECT.format(
                    cls.table_name, where))
                results = await cur.fetchall()
                return [cls.from_tuple(instance)
                        for instance in results] if results else []

    @classmethod
    def from_tuple(cls, tpl):
        items = []
        for i in range(len(tpl)):
            items.append((cls.columns[i], tpl[i]))
        return cls(**dict(items))

    def to_dict(self):
        return self.__dict__
