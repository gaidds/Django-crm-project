import uuid

# Django imports
from django.db import models

# Third party imports
from crum import get_current_user

# Module imports
from common.mixins import AuditModel

from django.contrib.auth import get_user_model

class BaseModel(AuditModel):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Extract the user from the token or session
        user = get_current_user()
        uid = kwargs.pop('uidb64', None)
        
        # If the user is updating their info through the link
        if uid:
            try:
                # Get the user object using the UID
                user = get_user_model().objects.get(pk=uid)
            except get_user_model().DoesNotExist:
                user = None

        if user is None or user.is_anonymous:
            self.created_by = None
            self.updated_by = None
        else:
            # If the record is being created for the first time
            if self._state.adding:
                if not self.created_by:
                    # Set created_by only if it is not already set
                    self.created_by = user
                self.updated_by = None
            else:
                # If the record is being updated, set updated_by without modifying created_by
                self.updated_by = user
                
        super(BaseModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)