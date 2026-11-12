import logging

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import exists, select

from .extensions import db
from .model import Todo
from .utility import TaskPriority

logger = logging.getLogger(__name__)


def _validate_user_task(user_id):
    if user_id != current_user.id:
        flash("Unable to access", "danger")
        return redirect(url_for("home"))
    return True


def todo_route(app):
    
    @app.route('/toggle/<id>', methods=['POST'])
    @login_required
    def toggle_todo(id):
        
        lst = db.session.get(Todo, id)
        
        _validate_user_task(lst.user_id)
        
        lst.completed = not lst.completed
        db.session.commit()
        action = "done" if lst.completed is True else "undone"
        
        flash(f"{lst.title} has being marked {action}", "warning")
        return redirect(url_for('home'))
        
        
    @app.route('/home', methods=['GET','POST'])
    @login_required
    def home():
        logger.info("Accessing the index route")
        if request.method == 'GET':            
            lst = db.session.scalars(
                select(Todo)
                .where(Todo.user_id == current_user.id
                       )).all()
            
            return render_template('todo/home.html', lst=lst, priority=TaskPriority)
        
        title = request.form.get('title', '').lower().strip()
        decrp = request.form.get('description', '').lower().strip()
        priority = request.form.get('priority')
        
        if bool(db.session.scalar(
            select(
                exists()
                .where(Todo.title == title)
                   ))):
            flash("Title already in todo list.", "warning")
            return redirect(url_for("home"))
        
        data = Todo(
            user_id=current_user.id,
            title=title, 
            description=decrp,
            priority=priority
            )
        
        db.session.add(data)
        db.session.commit()
        
        flash(f'Task "{title}" added successfully', 'success')
        logger.info(f"Added new task: {title}")
        return redirect(url_for('home'))
        
    
    @app.route('/view/<id>', methods=['GET'])
    @login_required
    def view(id):
        logger.info(f"Viewing task with ID: {id}")
        lst = db.session.get(Todo, id)
        
        if not lst:
            logger.warning("Id was not found, process was invalid")
            flash('Not found', 'danger')
            return redirect(url_for('home'))
        
        _validate_user_task(lst.user_id)
        
        return render_template('todo/view.html', lst=lst)
    
    
    @app.route('/delete/<id>')
    @login_required
    def delete(id):
        logger.info(f"Deleting task with ID: {id}")
        lst = db.session.get(Todo, id)
        
        if not lst:
            logger.warning("Id was not found, process was invalid")
            flash('Not found', 'danger')
            return redirect(url_for('home'))
        
        _validate_user_task(lst.user_id)
        
        db.session.delete(lst)
        db.session.commit()
        flash('Deleted successfully', 'success')
        return redirect(url_for('home'))
    
    
    @app.route('/search', methods=['POST'])
    @login_required
    def search():
        logger.info("Performing search operation")
        user_search = request.form.get('search', '').lower().strip()
        lst = db.session.scalars(
                select(Todo)
                .where(
                    Todo.title.ilike(f'%{user_search}%'),
                    Todo.user_id == current_user.id
                       )
                ).all()
        
        if not lst:
            logger.warning(f"No results found for search query: {user_search}")
            flash('Not found', 'danger')
            return redirect(url_for('home'))
        
        logger.info(f"Search results for '{user_search}': {len(lst)} items found")
        return render_template('todo/search.html', lst=lst)
            
    
    @app.route('/update/<id>', methods=['GET', 'POST'])
    @login_required
    def update(id):
        logger.info(f"Updating task with ID: {id}")
        lst = db.session.get(Todo, id)
        
        if not lst:
            logger.warning(f"Task with ID {id} not found for update")
            flash('Todo not found', 'danger')
            return redirect(url_for("home"))
        
        _validate_user_task(lst.user_id)
        
        if request.method == 'GET':
            return render_template('todo/update.html', lst=lst, priority=TaskPriority)

        title = request.form.get('title', '').lower().strip()
        decrp = request.form.get('description', '').lower().strip()
        priority = request.form.get('priority', '')

        lst.title = title
        lst.description = decrp
        lst.priority = priority
        
        db.session.commit()
        flash('Updated Successfully', 'success')
        return redirect(url_for('home'))
    


    