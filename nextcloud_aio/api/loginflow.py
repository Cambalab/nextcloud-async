"""Implement the Nextcloud Login Flow v2.

This will allow your application to:

    * Use an app token to log in as a user
    * Check for Remote Wipe status (see api.wipe)

Using an app token for your authorization will allow the user to:

    * Have the ability to disable access for your application
    * Signal your application to wipe all of its data (see api.wipe)

Reference:
    https://docs.nextcloud.com/server/latest/developer_manual/client_apis/LoginFlow/index.html
"""

import asyncio

from importlib.metadata import version

import datetime as dt

from typing import Dict, Optional

from nextcloud_aio.exceptions import NextCloudLoginFlowTimeout

__VERSION__ = version('nextcloud_aio')


class LoginFlowV2(object):
    """Obtain an app password after user web authorization.

    Simply:
        > login_flow = await ncc.login_flow_initiate()
        > print(login_flow('login'))   # Direct user to open the provided URL
        > token = login_flow['poll']['token']
        > results = await ncc.login_flow_wait_confirm(token, timeout=60))
        > print(results['appPassword'])

    You may then use `appPassword` to log in as the user with your application.
    """

    async def login_flow_initiate(self, user_agent: Optional[str] = None) -> Dict:
        """Initiate login flow v2.

        `user_agent` will show up as the name of your application in the
        Nextcloud instance.
        """
        response = await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/login/v2',
            headers={
                'user-agent':
                    f'nextcloud_aio/{__VERSION__}' if user_agent is None else user_agent})
        return response.json()

    async def login_flow_wait_confirm(self, token, timeout: int = 60) -> Dict:
        """Wait for user to confirm login.

        Returns dict including new `appPassword`.
        """
        start_dt = dt.datetime.now()
        running_time = 0

        response = await self.request(
            method='POST',
            url=f'{self.endpoint}/index.php/login/v2/poll',
            data={'token': token})

        while response.status_code == 404 and running_time < timeout:
            response = await self.request(
                method='POST',
                url=f'{self.endpoint}/index.php/login/v2/poll',
                data={'token': token})
            running_time = (dt.datetime.now() - start_dt).seconds
            await asyncio.sleep(1)

        if response.status_code == 404:
            raise NextCloudLoginFlowTimeout(
                'Login flow timed out.  You can try again.')

        return response.json()

    async def destroy_login_token(self):
        """Delete an app password generated by Login Flow v2.

        You must currently be logged in using the login token.
        """
        return await self.ocs_query(
            method='DELETE',
            sub='/ocs/v2.php/core/apppassword')
