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
        logger = config.Config.config_instance().logger
        logger.info("Attempting to create object class instance "
                    "'{}' with attributes '{}'"
                    .format(str(self.__class__), str(kwargs)))
        self.id = uuid.uuid4().hex
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def save(self):
        c = config.Config.config_instance()
        logger, pool = c.logger, c.connection.pool
        insert = self.INSERT.format(
            self.table_name,
            str(tuple([getattr(self, clmn) for clmn in self.columns]))
        )
        logger.info("Attempting to save object '{}' "
                    "using SQL query: {}".format(self.table_name, insert))
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(insert)
                await conn.commit()
        logger.info("Object saved.")
        return self

    @classmethod
    async def delete(cls, **kwargs):
        c = config.Config.config_instance()
        logger, pool = c.logger, c.connection.pool
        delete = cls.DELETE.format(
            cls.table_name, cls.__define_where(**kwargs))
        logger.info("Attempting to delete object '{}' "
                    "using SQL query: {}".format(cls.table_name, delete))
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(delete)
                await conn.commit()
        logger.info("Object gone.")

    # async def update(self, **kwargs):
    #     async with config.Connection.from_class().acquire() as conn:
    #         async with conn.cursor() as cur:
    #             await cur.execute()

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
        c = config.Config.config_instance()
        logger, pool = c.logger, c.connection.pool
        where = cls.__define_where(**kwargs)
        select = cls.SELECT.format(
            cls.table_name, where)
        logger.info("Attempting to find object(s) '{}' "
                    "using SQL : {}".format(cls.table_name, select))
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(select)
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
