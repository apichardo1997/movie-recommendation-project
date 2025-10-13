import logging
import sys
from typing import List

sys.path.append(".")


from server.backend.postgres import PostgresSessionManager
from server.models.user import UserModel

session_manager = PostgresSessionManager()


logger = logging.getLogger("sqlalchemy.engine")


with session_manager.open_session() as session:
    # raw sql query
    # result = session.execute(text("select * from public.users"))
    # print(result.fetchall())

    # sqlalchemy
    result: List[UserModel] = session.query(UserModel).all()
    print(result)
