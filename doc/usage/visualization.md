# Visualization

The visualization is served as static files.
You can use your local harddisk or a webserver.
When using a webserver, please take care of access control,
which can f.i. be done with HTTP basic authentication.

The visualization is build with Angular 5 [major release](http://angularjs.blogspot.co.at/2016/10/versioning-and-releasing-angular.html) 

* [Angular CLI](https://github.com/angular/angular-cli): 1.5.4
* [Node](https://nodejs.org): 8.1.4
* [D3](https://d3js.org/): 4.12.0 

For more details please check the package.json file.

## Prerequisites

In order to run the visualisation, you will need to have the following installed

    npm 

see https://docs.npmjs.com/

## To run the example

1. Clone Repository

        git clone <repository-url>

2. Change directory

        cd plotina/visualization/

3. Install modules
   
        npm install
    
4. Serve development version
    
        ng serve --aot
        
5. Run the visualization by browsing to 

        http://localhost:4200/

## Production

To deploy the visualisation you need to build it with the following command

    ng build --prod

You need to copy the content of the resulting ``dist/`` directory to your document root.

If required, you can use this build flags:

    --env=(demo|prod|dev) 
    --base-href="..." 

### Apache

This is a routed app so every request has to fallback to index.html.
Add a rewrite rule to your .htaccess file or to vhost configuration

    RewriteEngine On
    RewriteCond %{DOCUMENT_ROOT}%{REQUEST_URI} -f [OR]
    RewriteCond %{DOCUMENT_ROOT}%{REQUEST_URI} -d
    RewriteRule ^ - [L]  
    RewriteRule ^ /index.html

[More information on deployment techniques to a remote server](https://angular.io/guide/deployment)

## Data

There are two data files:
* visualization_data.json
* settings.json

### visualization_data.json

This file contains all the data required for the visualization.

After each completed survey you can extract data with the corresponding python script. 
You furthermore need to copy ``python/results/visualization_data.json`` to the `assets/data/`` 
directory in your document root.

### settings.json

This file contains the defaults for all thresholds and weights.

You can also provide a settings file, if you have downloaded one
in a previous run of the visualization. It will allow you to store
the previously chosen weights of individual indicators (used for
calculating the total indicator) as well as the threshold values.  

