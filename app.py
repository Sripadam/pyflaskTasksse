from flask import * 
import datetime 
import time  # Simulate some work 
import threading
import queue
app = Flask(__name__) 


tasks = [ 
    {'id': 1, 'title': 'Grocery Shopping', 'completed': False, 
    'due_date': '2024-03-15'}, 
    {'id': 2, 'title': 'Pay Bills', 'completed': False, 
    'due_date': '2024-03-20'}, 
] 
subscribers = []

next_task_id = 3 # For assigning new task IDs

# Send notification for  subscriber 
def send_notification(task_id, message):
    """ Notify all active SSE subscribers about task updates. """
    try:
        for subscriber in subscribers:
            subscriber.put(f"data: Task {task_id} update - {message}\n\n")

        time.sleep(3)  # Simulating delay
        print(f"Notification sent to user: {message}")
    except Exception as e:
        return jsonify({'error': "Error sending notification: {e}"}),404

# get the all tasks
@app.route('/api/get-tasks', methods=['GET']) 
def get_tasks():
    try: 
        return jsonify({ "message": f"Tasks retrieved successfully.",
                         "tasks": tasks
                        }), 201            
    except Exception as e:
        return jsonify({'error': 'Error retrieving tasks: {e}'}), 404 

# Create new task
@app.route('/api/tasks-create', methods=['POST']) 
def create_task():
    global next_task_id 
    try:
        data = request.get_json()  
        next_task_id+=1
        new_task = { 
            'id': next_task_id, 
            'title': data['title'], 
            'completed': False,
            'due_date': data.get('due_date') or 
            datetime.date.today().strftime("%Y-%m-%d") 
        }  
        tasks.append(new_task) 
        return jsonify({ "message": f"New task with id {next_task_id} is created successfully.",
                         "task": new_task }), 201
    except Exception as e:
        return jsonify({'error': 'Error create tasks: {e}'}), 404 

# Update new task
@app.route('/api/tasks-update/<int:task_id>', methods=['PUT']) 
def update_task(task_id):
    try: 
        data = request.get_json() 
        for task in tasks: 
            if task['id'] == task_id: 
                task.update(data)  # Update task attributes 
                # Simulate sending a notification ( Asynchronous) 
                notification_thread = threading.Thread(
                target=send_notification, args=(task_id, f"Your task {task_id} is now Updated")
                )
                notification_thread.start()

                time.sleep(2)  # Simulate some work (e.g., sending email) 
                print(f"Notification sent for task {task_id}") 
                return jsonify({
                            "message": f"Task {task_id} updated successfully, and notification has been sent.",
                            "task": task
                        }), 200

        return jsonify({'error': 'Task not found'}), 404 
    except Exception as e:
       return jsonify({'error': 'Error update task: {e}'}), 404  

# Delete the task
@app.route('/api/tasks-delete/<int:task_id>', methods=['DELETE']) 
def delete_task(task_id): 
    try:
        for i, task in enumerate(tasks): 
            if task['id'] == task_id: 
                del tasks[i] 
                return jsonify({'message': 'Task deleted successfully'}), 200
        return jsonify({'error': 'Task not found'}), 404 
    except Exception as e:
        return jsonify({'error': 'Error delete a task: {e}'}), 404
 
 # Server sent Events endpoint
@app.route('/events')
def events():
    """Server-Sent Events endpoint for real-time updates."""
    try:
        def event_stream():
            q = queue.Queue()
            subscribers.append(q)
            try:
                while True:
                    message = q.get()  # Wait for a new message
                    yield message
            except GeneratorExit:
                subscribers.remove(q)  # Remove subscriber when they disconnect
        return Response(event_stream(), mimetype="text/event-stream"), 200
    except Exception as e:
        print(f" Error in SSE route: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__': 
    app.run(debug=True)