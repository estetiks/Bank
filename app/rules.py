from flask import flash

def validate_string(str, allowed_chars):
    pattern = list(str)
    for i in pattern:
        if i not in allowed_chars:
            return True
    return False


def send_msg_rule(form):
    min_len_name = 5
    max_len_name = 20
    max_len_msg = 150
    allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

    if ( len(form['name']) < min_len_name or len(form['name']) > max_len_name): 
        flash('ERROR: The name length must be from 5 to 20 characters', category='error')
        return False
    
    if validate_string(form['name'], allowed): 
        flash('ERROR: Unsupported characters in the name', category='error')
        return False 

    if  len(form['email']) < 5: 
        flash('ERROR: Incorrect email', category='error')
        return False

    if len(form['message']) > max_len_msg:
        flash('ERROR: Message length cannot exceed 150 characters', category='error')
        return False

    flash('Thank you for your message!', category='success')
    return True
    
def login_creds(form):
    min_len_name = 5
    max_len_name = 20
    min_len_password = 10
    allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    
    if ( len(form['username']) < min_len_name or len(form['username']) > max_len_name): 
        flash('ERROR: The name length must be from 5 to 20 characters', category='error')
        return False
    
    if validate_string(form['username'], allowed): 
        flash('ERROR: Unsupported characters in the name', category='error')
        return False 
    
    if ( len(form['password']) < min_len_password): 
        flash('ERROR: The password must contain at least 10 characters', category='error')
        return False
    
    return True


