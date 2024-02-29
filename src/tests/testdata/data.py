import asyncio

from pydantic import BaseModel

from tests.testdata.utils import main


class TestData(BaseModel):

    login: str = 'test_user',
    login_error: str = '1234___',
    password: str = 'testpassword',
    current_password: str = 'testpassword',
    new_password: str = 'testpassword',
    password_error: str = '1234___',
    first_name: str = 'test',
    last_name: str = 'user',
    user_id: str = asyncio.run(main())


test_data = TestData()
