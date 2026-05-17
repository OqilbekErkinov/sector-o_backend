from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from api.models import Conversation, Message

User = get_user_model()

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = Conversation.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-updated_at')
        
        data = []
        for conv in conversations:
            other_user = conv.user2 if conv.user1 == user else conv.user1
            last_msg = conv.messages.last()
            
            # Count unread messages for this user
            unread_count = conv.messages.filter(is_read=False).exclude(sender=user).count()

            data.append({
                'id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'full_name': other_user.full_name,
                    'email': other_user.email,
                    'img': request.build_absolute_uri(other_user.img.url) if other_user.img else None,
                },
                'last_message': last_msg.content if last_msg else '',
                'last_message_time': last_msg.created_at if last_msg else conv.created_at,
                'unread_count': unread_count
            })
        return Response(data)

class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        target_email = request.data.get('email')
        target_id = request.data.get('user_id')

        target_user = None
        if target_id:
            target_user = User.objects.filter(id=target_id).first()
        elif target_email:
            target_user = User.objects.filter(email=target_email.lower().strip()).first()

        if not target_user:
            return Response({'error': 'Foydalanuvchi topilmadi'}, status=404)
        if target_user == user:
            return Response({'error': "O'zingizga yoza olmaysiz"}, status=400)

        # Check if conversation exists
        conv = Conversation.objects.filter(
            (Q(user1=user) & Q(user2=target_user)) | 
            (Q(user1=target_user) & Q(user2=user))
        ).first()

        if not conv:
            conv = Conversation.objects.create(user1=user, user2=target_user)

        return Response({
            'id': conv.id,
            'other_user': {
                'id': target_user.id,
                'full_name': target_user.full_name,
                'email': target_user.email,
                'img': request.build_absolute_uri(target_user.img.url) if target_user.img else None,
            }
        })

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        try:
            conv = Conversation.objects.get(id=pk)
        except Conversation.DoesNotExist:
            return Response({'error': 'Suhbat topilmadi'}, status=404)

        if user not in [conv.user1, conv.user2]:
            return Response({'error': "Ruxsat yo'q"}, status=403)

        # Mark as read
        unread_messages = conv.messages.filter(is_read=False).exclude(sender=user)
        if unread_messages.exists():
            unread_messages.update(is_read=True)
            
            # Notify the sender that their messages were read
            other_user = conv.user2 if conv.user1 == user else conv.user1
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{other_user.id}',
                {
                    'type': 'chat_message',
                    'message': {
                        'action': 'messages_read',
                        'conversation_id': conv.id,
                    }
                }
            )

        messages = conv.messages.all()
        data = [{
            'id': msg.id,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'is_read': msg.is_read,
            'created_at': msg.created_at
        } for msg in messages]

        return Response(data)

    def post(self, request, pk):
        user = request.user
        try:
            conv = Conversation.objects.get(id=pk)
        except Conversation.DoesNotExist:
            return Response({'error': 'Suhbat topilmadi'}, status=404)

        if user not in [conv.user1, conv.user2]:
            return Response({'error': "Ruxsat yo'q"}, status=403)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': "Xabar bo'sh bo'lishi mumkin emas"}, status=400)

        msg = Message.objects.create(
            conversation=conv,
            sender=user,
            content=content
        )
        
        # update conversation updated_at
        conv.updated_at = msg.created_at
        conv.save()
        
        # Broadcast to other user
        other_user = conv.user2 if conv.user1 == user else conv.user1
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{other_user.id}',
            {
                'type': 'chat_message',
                'message': {
                    'action': 'new_message',
                    'conversation_id': conv.id,
                    'msg': {
                        'id': msg.id,
                        'sender_id': msg.sender.id,
                        'content': msg.content,
                        'is_read': msg.is_read,
                        'created_at': msg.created_at.isoformat()
                    }
                }
            }
        )

        return Response({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'is_read': msg.is_read,
            'created_at': msg.created_at
        })
