from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.room import Room
import random
import string

rooms = Blueprint('rooms', __name__)

@rooms.route('/rooms')
@login_required
def room_list():
    """List all available rooms"""
    return render_template('rooms/list.html')

@rooms.route('/rooms/create', methods=['GET', 'POST'])
@login_required
def create_room():
    """Create and add a new room to the session"""
    if request.method == 'POST':
        name = request.form.get('name')
        is_private = request.form.get('is_private') == 'true'
        max_members = int(request.form.get('max_members', 10))

        if not name:
            flash('Room name is required!', 'error')
            return render_template('rooms/create.html')
        
        if len(name) < 3:
            flash('Room name must be at least 3 characters!', 'error')
            return render_template('rooms/create.html')
        
        if max_members < 1 or max_members > 10:
            flash('Maximum members must be between 1 and 10!', 'error')
            return render_template('rooms/create.html')
        
        # Generate a unique random code for joining the room
        while True:
            # Generate a 4-character code using letters and numbers
            join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            # Check if code is unique
            if not Room.query.filter_by(join_code=join_code).first():
                break

        # Create room
        room = Room(name, is_private, max_members, join_code)
        room.owner = current_user # Set the creator as the owner
        room.members.append(current_user) # Add creator to member list

        db.session.add(room)
        db.session.commit()

        flash('Room created successfully!', 'success')
        return redirect(url_for('rooms.view_room', room_id=room.id))
    
    return render_template('rooms/create.html')

@rooms.route('/rooms/join', methods=['POST'])
@login_required
def join_room():
    """Join a room via ID or join code"""
    room_id = request.form.get('room_id')
    join_code = request.form.get('join_code')

    if bool(room_id) == bool(join_code): # If both or neither are provided
        return jsonify({
            'success': False,
            'message': "Please either click 'Join Room' for public rooms or enter a join code for private rooms."
        })
    
    # Find room by ID or join code
    if join_code:
        room = Room.query.filter_by(join_code=join_code).first()
    elif room_id:
        room = Room.query.get(room_id)
        # Prevent joining private rooms via ID
        if room and room.is_private:
            flash("Private rooms can only be joined using a join code!", 'error')
            return redirect(url_for('rooms.room_list'))
        
    if not room:
        flash("Room not found.", 'error')
        return redirect(url_for('rooms.room_list'))
    
    # Check if user is already in a room
    if current_user.room_id:
        flash("You can only be in one room at a time! Please leave your current room and try again!", 'error')
        # Redirect the user to the room they are already in
        return redirect(url_for('rooms.load_room', room_id=current_user.room_id))
    
    # Check if room is full
    member_count = room.member_count()
    if member_count >= room.max_members:
        flash("Room is full!", 'error')
        return redirect(url_for('rooms.room_list'))
    
    # Incase user is still in a room, remove them
    current_user.leave_room()

    # Add user to new room
    room.members.append(current_user)
    current_user.room_id = room.id
    db.session.commit()

    flash(f"Successfully joined {room.name}!", 'success')
    return redirect(url_for('rooms.load_room', room_id=room.id))

@rooms.route('/rooms/<int:room_id>')
@login_required
def load_room(room_id):
    """Load a specific room"""
    room = Room.query.get_or_404(room_id)

    # Repeat checks from join_room route for security (prevents URL crafting)
    
    if current_user.room_id != room_id:
        flash("You can only be in one room at a time! Please leave your current room and try again!", 'error')
        return redirect(url_for('rooms.load_room', room_id=current_user.room_id))
    
    # Check if they are a member of the room
    if current_user not in room.members:
        # Not a member - redirect to list
        flash("Please join this room first!", 'error')
        return redirect(url_for('rooms.room_list'))
    
    member_count = room.member_count()
    return render_template('rooms/room.html', room=room, member_count=member_count, members=room.members)

@rooms.route('/api/rooms/search')
@login_required
def search_rooms():
    """API endpoint for searching specific rooms"""
    query = request.args.get('q', '')

    # Base query: no filter - all rooms
    base_query = Room.query

    # Apply search filter if used
    if query:
        base_query = base_query.filter(Room.name.ilike(f'%{query}'))

    # Get results
    rooms = base_query.all()
    return jsonify([room.format_dict() for room in rooms])

@rooms.route('/api/rooms/<int:room_id>/leave', methods=['POST'])
@login_required
def leave_room(room_id):
    """Remove user from their current room"""
    room = Room.query.get_or_404(room_id)

    if current_user not in room.members:
        return jsonify({
            'success': False,
            'message': 'You are not a member of this room!'
        })
    
    room.members.remove(current_user)

    # If user is the owner of the room, close the room
    if room.is_owner(current_user.id):
        db.session.delete(room)
    # If room is empty after user leaves, close the room
    elif not room.members:
        db.session.delete(room)

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Left the room successfully'
    })

@rooms.route('/api/rooms/join', methods=['POST'])
@login_required
def join_room_api():
    """API endpoint to join a room"""
    data = request.get_json()
    room_id = data.get('room_id')
    join_code = data.get('join_code')

    if bool(room_id) == bool(join_code): # If both or neither are provided
        return jsonify({
            'success': False,
            'message': "Please either click 'Join Room' for public rooms or enter a join code for private rooms."
        })
    
    # Find room by ID or join code
    if join_code:
        room = Room.query.filter_by(join_code=join_code).first()
    elif room_id:
        room = Room.query.get(room_id)
        # Prevent joining private rooms via ID
        if room and room.is_private:
            return jsonify({
                'success': False,
                'message': "Private rooms can only be joined using a join code!"
            })
        
    if not room:
        return jsonify({
            'success': False,
            'message': "Room not found!"
        })
    
    # Check if user is already in a room
    if current_user.room_id:
        return jsonify({
            'success': False,
            'message': "You can only be in one room at a time! Please leave your current room and try again!",
            'redirect': url_for('rooms.load_room', room_id=current_user.room_id)
        })
    
    # Check if room is full
    member_count = room.member_count()
    if member_count >= room.max_members:
        return jsonify({
            'success': False,
            'message': "Room is full!"
        })
    
    # Incase user is still in a room, remove them
    current_user.leave_room()

    # Add user to new room
    current_user.room_id = room.id
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Successfully joined {room.name}!",
        'redirect': url_for('rooms.load_room', room_id=room.id)
    })