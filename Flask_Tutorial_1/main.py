from website import create_app

app = create_app()

# Only run the web server if main is run:
if __name__ == '__main__':
    # Run the web server
    # (Debug = True means that the server will rerun when python code is changed)
    #TODO: Set Debug = False after finishing code
    app.run(debug=True)




#################################
#NOTE: Dependencies to install: #
#                               #
#pip install flask              #
#pip install flask-login        #
#pip install flask-sqlalchemy   #
#################################