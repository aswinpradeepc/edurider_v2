from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Permission to only allow owners or admins to access objects.
    Requires the model to have a field that can be compared with 
    the associated_id in the JWT token.
    """
    # The name of the field to compare with associated_id
    id_field = 'id'  # Default, override in views as needed
    
    def has_permission(self, request, view):
        # Always allow list views for admins only
        if request.method == 'GET' and getattr(view, 'action', None) == 'list':
            return request.user.is_staff
            
        # For other actions, proceed to object permission check
        return True
        
    def has_object_permission(self, request, view, obj):
        # Allow admin access
        if request.user.is_staff:
            return True
            
        # Get the ID field name from the view or use default
        id_field = getattr(view, 'owner_id_field', self.id_field)
        
        # Check if the JWT contains an associated_id
        if hasattr(request, 'auth') and request.auth:
            associated_id = request.auth.payload.get('associated_id')
            # Get the object's ID using the specified field
            obj_id = str(getattr(obj, id_field))
            # Compare with the associated_id
            return obj_id == associated_id
                
        return False

class IsDriverOrAdmin(BasePermission):
    """Permission to only allow drivers or admins"""
    
    def has_permission(self, request, view):
        # Allow admin access
        if request.user.is_staff:
            return True
            
        # Check if user is a driver
        if hasattr(request, 'auth') and request.auth:
            user_type = request.auth.payload.get('user_type')
            return user_type == 'driver'
                
        return False

class IsGuardianOrAdmin(BasePermission):
    """Permission to only allow guardians or admins"""
    
    def has_permission(self, request, view):
        # Allow admin access
        if request.user.is_staff:
            return True
            
        # Check if user is a guardian
        if hasattr(request, 'auth') and request.auth:
            user_type = request.auth.payload.get('user_type')
            return user_type == 'guardian'
                
        return False