from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from qa_service import query_document

app = Flask(__name__)
socketio = SocketIO(app)

# Store user and admin rooms
user_room = "user_room"
admin_room = "admin_room"

# Initialize bot_enabled flag
bot_enabled = False

# Dictionary to store user messages
user_messages = {}

@app.route("/user_interface")
def user_interface():
    return render_template("user_interface.html")

@app.route("/admin_interface")
def admin_interface():
    return render_template("admin_interface.html", users=list(user_messages.keys()))

@app.route("/admin_interface/<username>")
def admin_with_user(username):
    if username not in user_messages:
        user_messages[username] = []
    return render_template("admin_interface_with_user.html", username=username, messages=user_messages[username])

@socketio.on("join_room")
def join_user_room():
    join_room(user_room)

@socketio.on("message")
def handle_message(data):
    if bot_enabled:
        query = data["message"]
        bot_response = query_document(query)  # Assuming query_document function is available
        emit("message", {"user": "Admin", "message": bot_response}, room=user_room)
    else:
        emit("message", data, room=user_room, broadcast=True)

@socketio.on("user_send_message")
def handle_user_message(data):
    username = data["user"]
    message = data["message"]
    if username not in user_messages:
        user_messages[username] = []
    user_messages[username].append({"user": username, "message": message})
    emit("message", data, room=user_room)

@socketio.on("admin_join_room")
def join_admin_room():
    join_room(admin_room)

@socketio.on("admin_send_message")
def handle_admin_send_message(data):
    emit("message", data, room=user_room)

@socketio.on("toggle_bot")
def toggle_bot_reply():
    global bot_enabled
    bot_enabled = not bot_enabled

if __name__ == "__main__":
    socketio.run(app, debug=True)
