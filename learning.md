// a route is not registered unless it is opened and read 
// thats why using api router is important because when you include routes in the app instance
// because when you do  from .http.main import router 
// fastapi is forced to open the .http.main file and read it and register that route
// if a route is not registered the app returns a 403 forbidden error 