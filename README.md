# ImageUploadAPI
Rest API that allows user to upload images and receive response containing multiple normal or single timed thumbnail adequate to type of his account.  
User can view specific thumbnail he received using link in response.  
Timed thumbnail of specific type(size) is viewable for 300 to 30000 seconds, depending on passed by its creator parameters.  

## Features
- Uses django rest API, django, docker, nginx server with gunicorn
- Upload image to have server generate various-sized thumbnails, or a single time-limited thumbnail, viewable under unique urls
- Media and static files served by nginx
- Tests with pytest
- Authorization through django token or JWT token

## Authorization
To use API, one of authorization methods needs to be used, django token or JWT token.  
To get one of token types, send login and password to `api/auth/token/login` or `api/auth/jwt/create/` endpoint.
To be able to send authorized requests, add to your request headers `Authorization` key and value:
- `Token addtokenhere` when using django token
- `Bearer addjwttokenhere` when using jwt token 


## Installation and configuration
Configure `example.env` file with data that will be used for postgres database - replace words starting with "replace",  
and rename it to `.env`.  
Run container `docker-compose up`. Requirements.txt will be automatically installed, pip updated, static files collected, and nginx/gunicorn ran.  
Access container using `docker ps` to find out id of web container, and `docker exec -it INPUTIDOFCONTAINERHERE bash` to enter container, and run commands:  
`python manage.py migrate` Apply migrations  
`python manage.py createsuperuser` Create admin account  
Log in as super user in admin panel.  
Create user account, or use newly created admin account, that will use a token to access API.  
Create tables:   
a) Account type permissions: contains info on permissions for account type, allowed custom thumbnail sizes(all thumbnails are square shaped, therefore size is a single number, like 500).    
b) Api user profiles: assigns user to created account type.    
Get auth token, details in Authorization section above.
You can start sending requests to endpoints specified in api documentation.  
Website can be found under url `http://localhost:8000/`  

## Tests
To run tests, enter web docker container through bash and run command `pytest`

## Endpoint documentation
Documentation can be found after application installation under /api/schema/swagger-ui/ address.
Alternatively, schema can be generated and viewed without downloading project:
1. Download schema.yml file from repository
2. Go to https://editor.swagger.io/ 
3. File->Import-> select schema.yml file and send it
4. Same documentation as in the project will be generated.
