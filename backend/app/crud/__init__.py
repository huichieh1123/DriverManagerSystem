from . import tasks
from . import invitations
from app.db import mongodb
from app.api.v1.schemas.users import RoleType

# Users
class CRUDUserMongoDB:
    async def get_by_username(self, username: str):
        return await mongodb.get_user_by_username_mongodb(username)

    async def create(self, user_data):
        return await mongodb.create_user_mongodb(user_data)

    async def get_by_id(self, user_id: str):
        return await mongodb.get_user_by_id_mongodb(user_id)

    async def update(self, user_id: str, updated_data):
        return await mongodb.update_user_mongodb(user_id, updated_data)

    async def get_dispatchers_by_company_id(self, company_id: str):
        return await mongodb.get_dispatchers_by_company_id_mongodb(company_id)

    async def get_drivers_by_company_id(self, company_id: str):
        return await mongodb.get_drivers_by_company_id_mongodb(company_id)

user = CRUDUserMongoDB()

# Tasks (still placeholder)
class CRUDTaskMongoDB:
    async def get_all(self):
        return await mongodb.get_tasks_mongodb()

    async def create(self, task_data):
        return await mongodb.create_task_mongodb(task_data)

task = CRUDTaskMongoDB()

# Jobs
class CRUDJobMongoDB:
    async def get_all(self, assigned_driver_id=None, created_by_dispatcher_id=None, is_public=None, status=None, company_id=None):
        return await mongodb.get_jobs_mongodb(assigned_driver_id, created_by_dispatcher_id, is_public, status, company_id)

    async def get_by_id(self, job_id: str):
        return await mongodb.get_job_by_id_mongodb(job_id)

    async def create(self, job_data, created_by_dispatcher_id: str, company_id=None, company_name=None):
        return await mongodb.create_job_mongodb(job_data, created_by_dispatcher_id, company_id, company_name)

    async def update(self, job_id: str, updated_data):
        return await mongodb.update_job_mongodb(job_id, updated_data)

    async def delete(self, job_id: str):
        return await mongodb.delete_job_mongodb(job_id)

    async def request_claim(self, job_id: str, driver_id: str, vehicle_id: str):
        return await mongodb.request_claim_job_mongodb(job_id, driver_id, vehicle_id)

    async def approve_claim(self, job_id: str):
        return await mongodb.approve_claim_job_mongodb(job_id)

    async def reject_claim(self, job_id: str):
        return await mongodb.reject_claim_job_mongodb(job_id)

job = CRUDJobMongoDB()

# Invitations
class CRUDInvitationMongoDB:
    async def get_by_id(self, invitation_id: str):
        return await mongodb.get_invitation_by_id_mongodb(invitation_id)

    async def create(self, invitee_username: str, invitee_role: RoleType, invitee_id: str, company_id: str, company_name: str):
        return await mongodb.create_invitation_mongodb(
            invitee_id=invitee_id,
            invitee_username=invitee_username,
            invitee_role=invitee_role,
            company_id=company_id,
            company_name=company_name
        )

    async def update(self, invitation_id: str, updated_data):
        return await mongodb.update_invitation_mongodb(invitation_id, updated_data)

    async def get_for_invitee(self, invitee_id: str, invitee_role: RoleType):
        return await mongodb.get_invitations_for_invitee_mongodb(invitee_id, invitee_role)

invitation = CRUDInvitationMongoDB()