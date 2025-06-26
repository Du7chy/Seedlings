from flask_socketio import emit, join_room as socket_join_room, leave_room as socket_leave_room
from flask_login import current_user
from flask import request
from models.database import db
from models.room import Room
from models.chat_message import ChatMessage

def init_socket_events(socketio):
    @socketio.on('connect')
    def connect():
        """Handle client connection to Socket.IO server"""
        if not current_user.is_authenticated:
            return False
        
        # If user is in a room, join the socket room
        if current_user.room_id:
            socket_join_room(str(current_user.room_id))

    @socketio.on('join')
    def join(data):
        """Handle user joining a room"""
        room_id = str(data.get('room_id'))
        socket_join_room(room_id)
        emit('status', {'message': f'{current_user.username} joined the room.'}, room=room_id)

        # Update member count/list for all users in the room
        room = Room.query.get(room_id)
        if room:
            emit('member_update', {
                'count': room.member_count(),
                'members': [{
                    'id': m.id,
                    'username': m.username,
                    'is_owner': m == room.owner
                } for m in room.members]
            }, room=room_id)
    
    @socketio.on('leave')
    def leave(data):
        """Handle user leaving a room"""
        room_id = str(data.get('room_id'))
        socket_leave_room(room_id)
        emit('status', {'message': f'{current_user.username} left the room.'}, room=room_id)

        # Update member count/list for all users in the room
        room = Room.query.get(room_id)
        if room:
            emit('member_update', {
                'count': room.member_count(),
                'members': [{
                    'id': m.id,
                    'username': m.username,
                    'is_owner': m == room.owner
                } for m in room.members]
            }, room=room_id)

    @socketio.on('chat')
    def chat(data):
        """Handle user chat inputs"""
        room_id = int(data.get('room_id'))
        message_content = data.get('message', '').strip()

        if not message_content:
            return
        
        # Save message to database
        message = ChatMessage(
            message_content=message_content,
            room_id=room_id,
            user_id=current_user.id,
        )
        db.session.add(message)
        db.session.commit()

        # Send message to room
        emit('chat', {
            'id': message.id,
            'message_content': message.message_content,
            'timestamp': message.timestamp.isoformat(),
            'user': current_user.username
        }, room=str(room_id))