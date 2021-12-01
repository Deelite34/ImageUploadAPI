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
Configure `example.env` file with data that will be used for postgres database - replace words starting with "replace", and rename it to `.env`  
Run container `docker-compose up`. Requirements.txt will be automatically installed.  
Access container using bash and run commands:  
- Apply migrations `python manage.py migrate`  
- Create admin account `python manage.py createsuperuser`  
Log in as super user in admin panel.  
Create user account that will use token to access API.  
Create tables:   
a) Account type permissions: contains info on permissions for account type, allowed custom thumbnail sizes(custom thumbnails are square)  
b) Api user profiles: assigns user to account type created above  
You can start sending requests to endpoints specified in docs. First you should upload image to /api/all/ or /api/timed/  

# Tests
To run tests, enter web docker container trough bash and run command `pytest`

# Endpoint documentation
Documentation can be found after application installation under /api/schema/swagger-ui/ address.
Alternatively, schema can be generated and viewed without downloading project:
1. Download schema.yml file from repository
2. Go to https://editor.swagger.io/ 
3. File->Import-> select schema.yml file and send it
4. Same documentation as in the project will be generated.
