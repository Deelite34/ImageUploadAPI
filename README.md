# ImageUploadAPI
Rest API that allows user to upload images and receive response containing multiple normal or single timed thumbnail adequate to type of his account.  
User can view specific thumbnail he received using link in response.  
Timed thumbnail of specific type(size) is viewable for 300 to 30000 seconds, depending on passed by its creator parameters.  

# Authorization
To use API, one of authorization methods needs to be user. Admin logged in using admin panel can also choose to not add anything to his header, pages will still work.
Typical user however needs a django token or JWT token.  
When using django token, user needs to add `Authorization` key and `Token <replace-this-with-django-token>` as value,  
and with JWT token: `Authorization` key and `Bearer <replace-this-with-jwt-token>` as value.   

## Installation and configuration
Configure `example.env` file with data that will be used for postgres database, and rename it to `.env`  
Run container `docker-compose up`. Requirements.txt will be automatically installed.  
Access container using bash and run commands:  
- Apply migrations `python manage.py migrate`  
- Create admin account `python manage.py createsuperuser`  
Log in as super user in admin panel. Create user account that will use token to access API.  
Create tables:   
- Account type permissions: contains info on permissions for account type, allowed custom thumbnail sizes(custom thumbnails are square)  
- Api user profiles: assigns user to account type created above  

# Tests
To run tests, enter web docker container trough bash and run command `pytest`

# Endpoint documentation
TODO
