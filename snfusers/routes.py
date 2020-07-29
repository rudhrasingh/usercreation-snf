from flask import Flask, render_template, url_for, flash, redirect,session,request
from snfusers import app
from snfusers.forms import UserCreation
import snowflake.connector
import csv
import codecs



def execute_query(conn,sql):
    rc = False
    try:
        cs = conn.cursor()
        cs.execute(sql)
        rc=True
    except:
        rc=False
    finally:
        return rc

@app.route("/")
def home():
    return redirect (url_for('createuser'))


@app.route("/snf/createusers/bulk", methods=['GET', 'POST'])
def createuser():
    form = UserCreation()
    #if request.method=="POST":
    if form.validate_on_submit():
        usr=form.username.data
        regn=form.region.data 
        role=form.rolename.data
        pwd=form.password.data 
        users_file = form.usersfile.data
        reader=list(csv.reader(codecs.iterdecode(users_file, 'utf-8')))
        try:
            users_file.seek(0)
            
            ctx = snowflake.connector.connect(
            user=usr,
            password=pwd,
            account=regn
            )
            cs = ctx.cursor()
            cs.execute("SELECT current_version()")
            one_row = cs.fetchone()
            if one_row!=None:
                sql_role="USE ROLE "+  role # assume role
                sql_db="USE DATABASE USERDB"
                sql_dw="USE WAREHOUSE COMPUTE_WH"
                if execute_query(ctx,sql_role) and execute_query(ctx,sql_db) and execute_query(ctx,sql_dw):
                    print('logged in and pre-requisites completed')
                    reader=list(csv.reader(codecs.iterdecode(users_file, 'utf-8')))
                    usr_cnt=0
                    for line in reader[1:]:
                        sql_usr_id="select NEW_USER_SEQ.nextval"
                        cs.execute(sql_usr_id)
                        uid = cs.fetchone()
                        username= line[0]+line[1]+str(uid[0])
                        pwd='Test123'
                        loginame =username
                        displayname=line[0]+line[1]
                        fname=line[0]
                        lname=line[1]
                        df_role='SYSADMIN'
                        dw='COMPUTE_WH'
                        sql_usr = f'''CREATE 
                        USER  {username} 
                        PASSWORD = "{pwd}"  
                        COMMENT = "new user"  
                        LOGIN_NAME = "{loginame}"  
                        DISPLAY_NAME = "{displayname}" 
                        FIRST_NAME = "{fname}" 
                        LAST_NAME = "{lname}" 
                        DEFAULT_ROLE = "{df_role}"  
                        DEFAULT_WAREHOUSE = "{dw}" 
                        MUST_CHANGE_PASSWORD = TRUE ;
                        '''  
                        print ('sql_usr: ' + sql_usr )
                        #cs.execute(sql_usr)


                        sql_usr_grant= f'''GRANT ROLE "{df_role}" TO USER {username};'''             
                        print ('sql_usr_grant: ' + sql_usr_grant )
                        #cs.execute(sql_usr_grant)
                        usr_cnt = usr_cnt+1

                    fmsg=str(usr_cnt) + ' Users created successfully!'
                
                    flash(fmsg, 'success')
                    return redirect(url_for('createuser'))
                else:
                    flash('You do not have required priviledges!', 'danger')
                    return redirect(url_for('createuser'))


            else:
                flash('Authentication Failed!', 'danger')
                return redirect(url_for('createuser'))
        except Exception as e:
            flash('Authentication Failed!', 'danger')
            return redirect(url_for('createuser'))
                
    return render_template('login.html', title='Home', form=form)
