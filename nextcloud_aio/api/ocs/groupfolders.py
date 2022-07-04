"""Implement Nextcloud Group Folders Interaction.

https://github.com/nextcloud/groupfolders#api
"""

from enum import IntFlag


class Permissions(IntFlag):
    read = 1
    update = 2
    create = 4
    delete = 8
    share = 16


class GroupFolderManager(object):

    async def get_all_group_folders(self):
        """Get list of all group folders."""
        return await self.ocs_query(
            method='GET',
            sub='/apps/groupfolders/folders')

    async def create_group_folder(self, path: str):
        """Create new group folder."""
        return await self.ocs_query(
            method='POST',
            sub='/apps/groupfolders/folders',
            data={'mountpoint': path})

    async def get_group_folder(self, folder_id: int):
        """Get group folder with id `folder_id`."""
        return await self.ocs_query(
            method='GET',
            sub=f'/apps/groupfolders/folders/{folder_id}')

    async def remove_group_folder(self, folder_id: int):
        """Delete group folder with id `folder_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/apps/groupfolders/folders/{folder_id}')

    async def add_group_to_group_folder(self, group_id: str, folder_id: int):
        """Give `group_id` access to `folder_id`."""
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/groups',
            data={'group': group_id})

    async def remove_group_from_group_folder(self, group_id: str, folder_id: int):
        """Remove `group_id` access from `folder_id`."""
        return await self.ocs_query(
            method='DELETE',
            sub=f'/apps/groupfolders/folders/{folder_id}/groups/{group_id}')

    async def enable_group_folder_advanced_permissions(self, folder_id: int):
        """Enable advanced permissions on `folder_id`."""
        return await self.__advanced_permissions(folder_id, True)

    async def disable_group_folder_advanced_permissions(self, folder_id: int):
        """Disable advanced permissions on `folder_id`."""
        return await self.__advanced_permissions(folder_id, False)

    async def __advanced_permissions(self, folder_id: int, enable: bool):
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/acl',
            data={'acl': 1 if enable else 0})

    async def add_group_folder_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str):
        """Enable `object_id` as manager of advanced permissions.

        `object_type` is either `user` or `group`
        """
        return await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type,
            manage_acl=True)

    async def remove_group_folder_advanced_permissions(
            self,
            folder_id: int,
            object_id: str,
            object_type: str):
        """Disable `object_id` as manager of advanced permissions."""
        return await self.__advanced_permissions_admin(
            folder_id,
            object_id=object_id,
            object_type=object_type,
            manage_acl=False)

    async def __advanced_permissions_admin(
            self,
            folder_id: int,
            object_id: str,
            object_type: str,
            manage_acl: bool):
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/manageACL',
            data={
                'mappingId': object_id,
                'mappingType': object_type,
                'manageAcl': manage_acl})

    async def set_group_folder_permissions(
            self,
            folder_id: int,
            group_id: str,
            permissions: Permissions):
        """Set permissions a group has in a folder."""
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/groups/{group_id}',
            data={'permissions': permissions.value})

    async def set_group_folder_quota(self, folder_id: int, quota: int):
        """Set quota for group folder.

        `quota` is in bytes.  -3 for unlimited.
        """
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/quota',
            data={'quota': quota})

    async def rename_group_folder(self, folder_id: int, mountpoint: str):
        """Rename a group folder."""
        return await self.ocs_query(
            method='POST',
            sub=f'/apps/groupfolders/folders/{folder_id}/mountpoint',
            data={'mountpoint': mountpoint})
