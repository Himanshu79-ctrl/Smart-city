# accounts/utils.py (naya file banao)

from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def get_all_active_sessions():
    """Saari active sessions ki list"""
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    session_list = []
    
    for session in sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id')
        try:
            user = User.objects.get(id=user_id) if user_id else None
        except User.DoesNotExist:
            user = None
            
        session_list.append({
            'session_key': session.session_key,
            'user': user,
            'expire_date': session.expire_date,
            'ip': data.get('ip_address', 'Unknown'),
            'user_agent': data.get('user_agent', 'Unknown'),
        })
    
    return session_list

def delete_user_sessions(user):
    """Kisi specific user ki saari sessions delete karo"""
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    deleted_count = 0
    
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            session.delete()
            deleted_count += 1
    
    return deleted_count

def cleanup_expired_sessions():
    """Expired sessions ko delete karo"""
    expired = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired.count()
    expired.delete()
    return count